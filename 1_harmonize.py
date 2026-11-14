import glob
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

print("🚀 Iniciando calibración física instrument-aware (MODIS -> VIIRS)...")

# 1. Cargar MODIS y separar VIIRS S-NPP vs NOAA-20 para evitar doble conteo orbital
modis_files = glob.glob("data/**/*M-C61*.csv", recursive=True)
snpp_files = glob.glob("data/**/*SV-C2*.csv", recursive=True)
noaa20_files = glob.glob("data/**/*J1V-C2*.csv", recursive=True)

df_modis = pd.concat([pd.read_csv(f, low_memory=False) for f in modis_files], ignore_index=True)
df_snpp = pd.concat([pd.read_csv(f, low_memory=False) for f in snpp_files], ignore_index=True)

# S-NPP cubre hasta 2026-11-02; usamos NOAA-20 solo para los días posteriores (sin solapamiento doble)
if noaa20_files:
    df_noaa20 = pd.concat([pd.read_csv(f, low_memory=False) for f in noaa20_files], ignore_index=True)
    df_noaa20_post = df_noaa20[df_noaa20['acq_date'] > '2026-11-02'].copy()
    df_viirs = pd.concat([df_snpp, df_noaa20_post], ignore_index=True)
else:
    df_viirs = df_snpp.copy()

# 2. Filtrar detecciones de alta confianza
df_modis['confidence'] = pd.to_numeric(df_modis['confidence'], errors='coerce')
df_modis = df_modis[df_modis['confidence'] >= 70].copy()
df_viirs = df_viirs[df_viirs['confidence'].isin(['n', 'h'])].copy()

# 3. Física del sensor MODIS: área real de píxel (km²) y detección diurna/nocturna
if 'scan' in df_modis.columns and 'track' in df_modis.columns:
    df_modis['pixel_area_km2'] = df_modis['scan'] * df_modis['track']
else:
    df_modis['pixel_area_km2'] = 1.0

df_modis['is_day'] = (df_modis['daynight'] == 'D').astype(int) if 'daynight' in df_modis.columns else 0

# 4. Malla espacial estándar de 0.25° (~25 km, elimina errores de borde de barrido)
GRID_RES = 0.25
for df in [df_modis, df_viirs]:
    df['acq_date'] = pd.to_datetime(df['acq_date'])
    df['year'] = df['acq_date'].dt.year
    df['month'] = df['acq_date'].dt.month
    df['lat_bin'] = ((df['latitude'] / GRID_RES).round() * GRID_RES).round(2)
    df['lon_bin'] = ((df['longitude'] / GRID_RES).round() * GRID_RES).round(2)

# 5. Agregar por celda espacio-temporal
modis_agg = df_modis.groupby(['year', 'month', 'lat_bin', 'lon_bin']).agg(
    modis_count=('frp', 'count'),
    modis_frp=('frp', 'sum'),
    modis_max_frp=('frp', 'max'),
    modis_area=('pixel_area_km2', 'sum'),
    modis_day_count=('is_day', 'sum')
).reset_index()

viirs_agg = df_viirs.groupby(['year', 'month', 'lat_bin', 'lon_bin']).agg(
    viirs_count=('frp', 'count'),
    viirs_frp=('frp', 'sum')
).reset_index()

# 6. Cruce en periodo de solapamiento (2012 - 2026)
overlap = pd.merge(modis_agg, viirs_agg, on=['year', 'month', 'lat_bin', 'lon_bin'], how='inner')
print(f"🔬 Celdas coincidentes sin doble conteo: {len(overlap):,}")

def build_features(df_in):
    X_out = pd.DataFrame()
    X_out['log_count'] = np.log1p(df_in['modis_count'])
    X_out['log_frp'] = np.log1p(df_in['modis_frp'])
    X_out['log_max_frp'] = np.log1p(df_in['modis_max_frp'])
    X_out['log_area'] = np.log1p(df_in['modis_area'])
    X_out['day_ratio'] = df_in['modis_day_count'] / df_in['modis_count']
    X_out['month'] = df_in['month']
    X_out['lat_bin'] = df_in['lat_bin']
    return X_out

X = build_features(overlap)
yc_log = np.log1p(overlap['viirs_count'])
yf_log = np.log1p(overlap['viirs_frp'])

# Validación estricta 80/20 fuera de muestra
X_train, X_test, yc_train, yc_test, yf_train, yf_test = train_test_split(
    X, yc_log, yf_log, test_size=0.2, random_state=42
)

model_count = GradientBoostingRegressor(n_estimators=250, max_depth=4, learning_rate=0.05, subsample=0.8, random_state=42)
model_count.fit(X_train, yc_train)

model_frp = GradientBoostingRegressor(n_estimators=250, max_depth=4, learning_rate=0.05, subsample=0.8, random_state=42)
model_frp.fit(X_train, yf_train)

# Evaluación fuera de muestra (escala logarítmica y escala lineal con corrección de Duan)
pred_yc_test = model_count.predict(X_test)
r2_log = r2_score(yc_test, pred_yc_test)

smear_c_val = np.mean(np.exp(yc_train - model_count.predict(X_train)))
pred_linear_test = np.maximum(1, smear_c_val * np.exp(pred_yc_test) - 1)
r2_linear = r2_score(np.expm1(yc_test), pred_linear_test)

print(f"✅ R² fuera de muestra (escala log / ley de potencia): {r2_log:.3f}")
print(f"✅ R² fuera de muestra (conteo lineal sin sesgo):    {r2_linear:.3f}")

# 7. Reentrenar con el 100% de solapamiento y calcular factores de Duan
model_count.fit(X, yc_log)
model_frp.fit(X, yf_log)

smear_c = np.mean(np.exp(yc_log - model_count.predict(X)))
smear_f = np.mean(np.exp(yf_log - model_frp.predict(X)))

# 8. Reconstruir serie histórica (2000 - 2011)
pre_viirs = modis_agg[modis_agg['year'] < 2012].copy()
X_pre = build_features(pre_viirs)

pre_viirs['harmonized_hotspots'] = np.maximum(1, np.round(smear_c * np.exp(model_count.predict(X_pre)) - 1)).astype(int)
pre_viirs['harmonized_frp'] = np.maximum(0.1, smear_f * np.exp(model_frp.predict(X_pre)) - 1)
pre_viirs['source'] = 'MODIS (Calibrated)'

# 9. Serie directa VIIRS (2012 - 2026)
post_viirs = viirs_agg.rename(columns={
    'viirs_count': 'harmonized_hotspots',
    'viirs_frp': 'harmonized_frp'
}).copy()
post_viirs['source'] = 'VIIRS (Direct)'

# 10. Exportar dataset final
cols = ['year', 'month', 'lat_bin', 'lon_bin', 'harmonized_hotspots', 'harmonized_frp', 'source']
final_df = pd.concat([pre_viirs[cols], post_viirs[cols]], ignore_index=True)
final_df.to_csv("harmonized_chile.csv", index=False)
print(f"🎉 ¡Listo! 'harmonized_chile.csv' generado con {len(final_df):,} celdas calibradas.")