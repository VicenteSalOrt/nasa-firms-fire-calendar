import glob
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

print("🚀 Iniciando pipeline de armonización MODIS + VIIRS...")

# 1. Buscar recursivamente los CSV dentro de las subcarpetas de 'data/'
modis_files = glob.glob("data/**/*M-C61*.csv", recursive=True)
viirs_files = glob.glob("data/**/*SV-C2*.csv", recursive=True) + glob.glob("data/**/*J1V-C2*.csv", recursive=True)

if not modis_files or not viirs_files:
    raise FileNotFoundError("⚠️ No se encontraron los CSV dentro de 'data/'. Verifica que los archivos estén descomprimidos.")

print(f"📂 Archivos encontrados -> MODIS: {len(modis_files)} | VIIRS: {len(viirs_files)}")

df_modis = pd.concat([pd.read_csv(f, low_memory=False) for f in modis_files], ignore_index=True)
df_viirs = pd.concat([pd.read_csv(f, low_memory=False) for f in viirs_files], ignore_index=True)

print(f"📊 Registros crudos cargados -> MODIS: {len(df_modis):,} | VIIRS: {len(df_viirs):,}")

# 2. Filtrar por nivel de confianza para eliminar falsos positivos
df_modis = df_modis[df_modis['confidence'] >= 70].copy()
df_viirs = df_viirs[df_viirs['confidence'].isin(['n', 'h'])].copy()

# 3. Extraer Año, Mes y crear Malla Espacial Común (Binning de ~11x11 km)
for df in [df_modis, df_viirs]:
    df['acq_date'] = pd.to_datetime(df['acq_date'])
    df['year'] = df['acq_date'].dt.year
    df['month'] = df['acq_date'].dt.month
    df['lat_bin'] = df['latitude'].round(1)
    df['lon_bin'] = df['longitude'].round(1)

# 4. Agrupar por celda espacio-temporal (Año, Mes, Latitud, Longitud)
modis_agg = df_modis.groupby(['year', 'month', 'lat_bin', 'lon_bin']).agg(
    modis_count=('frp', 'count'),
    modis_frp=('frp', 'sum')
).reset_index()

df_viirs_clean = df_viirs.drop_duplicates(subset=['acq_date', 'acq_time', 'lat_bin', 'lon_bin'])

viirs_agg = df_viirs_clean.groupby(['year', 'month', 'lat_bin', 'lon_bin']).agg(
    viirs_count=('frp', 'count'),
    viirs_frp=('frp', 'sum')
).reset_index()

# 5. Calibración Instrumental: Cruzar el periodo de solapamiento (2012 - presente)
overlap = pd.merge(modis_agg, viirs_agg, on=['year', 'month', 'lat_bin', 'lon_bin'], how='inner')
print(f"🔬 Celdas espacio-temporales coincidentes para calibración: {len(overlap):,}")

# Validación científica fuera de muestra (80% entrenamiento / 20% prueba)
X = overlap[['modis_count', 'modis_frp', 'month', 'lat_bin']]
y_count = overlap['viirs_count']
y_frp = overlap['viirs_frp']

X_train, X_test, y_train_c, y_test_c, y_train_f, y_test_f = train_test_split(
    X, y_count, y_frp, test_size=0.2, random_state=42
)

model_count = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
model_count.fit(X_train, y_train_c)

model_frp = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
model_frp.fit(X_train, y_train_f)

r2_test = r2_score(y_test_c, model_count.predict(X_test))
print(f"✅ Modelo validado fuera de muestra. R² (Test Set 20%): {r2_test:.3f}")

# Re-entrenar con el 100% de los datos de solapamiento antes de predecir el pasado
model_count.fit(X, y_count)
model_frp.fit(X, y_frp)

# 6. Reconstruir la serie histórica completa (2000 - 2026)
pre_viirs = modis_agg[modis_agg['year'] < 2012].copy()
X_pre = pre_viirs[['modis_count', 'modis_frp', 'month', 'lat_bin']]

pre_viirs['harmonized_hotspots'] = np.round(model_count.predict(X_pre)).astype(int)
pre_viirs['harmonized_frp'] = model_frp.predict(X_pre)
pre_viirs['source'] = 'MODIS (Calibrated)'

post_viirs = viirs_agg.rename(columns={
    'viirs_count': 'harmonized_hotspots',
    'viirs_frp': 'harmonized_frp'
}).copy()
post_viirs['source'] = 'VIIRS (Direct)'

# 7. Unificar y exportar el dataset final liviano para la App Web
cols = ['year', 'month', 'lat_bin', 'lon_bin', 'harmonized_hotspots', 'harmonized_frp', 'source']
final_df = pd.concat([pre_viirs[cols], post_viirs[cols]], ignore_index=True)

final_df.to_csv("harmonized_chile.csv", index=False)
print(f"🎉 ¡Listo! Archivo 'harmonized_chile.csv' generado con {len(final_df):,} registros armonizados.")