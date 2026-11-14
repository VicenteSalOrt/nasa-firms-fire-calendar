import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración general de la página
st.set_page_config(page_title="FIRMS Fire Calendar", page_icon="🔥", layout="wide")
st.title("🔥 Harmonized Wildfire Activity Calendar (MODIS + VIIRS)")
st.markdown("26 years of cross-calibrated NASA satellite thermal anomalies (`Out-of-sample R² = 0.887`) for early warning and fire management.")
# 1. Cargar los datos armonizados (en caché para máxima velocidad)
@st.cache_data
def load_data():
    return pd.read_csv("harmonized_chile.csv")

df = load_data()

# 2. Barra Lateral: Filtros de Coordenadas (Requisito oficial del reto)
st.sidebar.header("📍 Area of Interest (AOI)")
preset = st.sidebar.selectbox(
    "Quick Presets (Chile):", 
    ["Biobío & Ñuble", "Valparaíso", "La Araucanía", "All Chile", "Custom Coordinates"]
)

if preset == "Biobío & Ñuble":
    lat_min, lat_max, lon_min, lon_max = -38.5, -36.0, -73.8, -71.0
elif preset == "Valparaíso":
    lat_min, lat_max, lon_min, lon_max = -33.6, -32.2, -71.8, -70.5
elif preset == "La Araucanía":
    lat_min, lat_max, lon_min, lon_max = -39.6, -37.5, -73.6, -71.0
elif preset == "All Chile":
    lat_min, lat_max, lon_min, lon_max = -56.0, -17.0, -76.0, -66.0
else:
    lat_min = st.sidebar.number_input("Min Latitude", value=-38.5, format="%.2f")
    lat_max = st.sidebar.number_input("Max Latitude", value=-36.0, format="%.2f")
    lon_min = st.sidebar.number_input("Min Longitude", value=-73.8, format="%.2f")
    lon_max = st.sidebar.number_input("Max Longitude", value=-71.0, format="%.2f")

st.sidebar.markdown("---")
metric_choice = st.sidebar.radio(
    "Select Metric to Analyze:",
    ["Calibrated Hotspots (Count)", "Fire Radiative Power (FRP - MW)"]
)
value_col = "harmonized_hotspots" if "Hotspots" in metric_choice else "harmonized_frp"

# Filtrar dataset por coordenadas
df_filtered = df[
    (df['lat_bin'].between(lat_min, lat_max)) & 
    (df['lon_bin'].between(lon_min, lon_max))
]

if df_filtered.empty:
    st.warning("⚠️ No fire hotspots detected in the selected coordinates. Try expanding the bounding box.")
    st.stop()

# 3. Detector de Anomalías Históricas (KPIs)
st.subheader("📊 Historical Anomaly Detector")
years_available = sorted(df_filtered['year'].unique())
default_year = 2023 if 2023 in years_available else years_available[-1]
selected_year = st.slider("Select Year to Compare Against Historical Median:", int(min(years_available)), int(max(years_available)), int(default_year))

monthly_totals = df_filtered.groupby(['year', 'month'])[value_col].sum().reset_index()
historical_median = monthly_totals.groupby('month')[value_col].median().reset_index()
current_year_data = monthly_totals[monthly_totals['year'] == selected_year]

total_selected = current_year_data[value_col].sum()
median_annual = historical_median[value_col].sum()
anomaly_pct = ((total_selected - median_annual) / median_annual * 100) if median_annual > 0 else 0

col1, col2, col3 = st.columns(3)
unit_label = "Hotspots" if value_col == "harmonized_hotspots" else "MW"
col1.metric(f"Total Activity ({selected_year})", f"{total_selected:,.0f} {unit_label}")
col2.metric("26-Year Historical Median", f"{median_annual:,.0f} {unit_label}")
col3.metric("Anomaly vs. Median", f"{anomaly_pct:+.1f}%", delta_color="inverse")

# 4. Calendario de Actividad de Incendios (Heatmap Accesible)
st.subheader("🗓️ Burning Activity Calendar (2000 – Present)")
calendar_pivot = monthly_totals.pivot(index='year', columns='month', values=value_col).fillna(0)

# Asegurar que estén los 12 meses en orden
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
calendar_pivot = calendar_pivot.reindex(columns=range(1, 13), fill_value=0)

fig_cal = px.imshow(
    calendar_pivot,
    labels=dict(x="Month", y="Year", color=unit_label),
    x=month_names,
    y=calendar_pivot.index.astype(str),
    color_continuous_scale="Cividis", # Paleta accesible para daltonismo (requisito del reto)
    aspect="auto"
)
fig_cal.update_layout(height=550)
st.plotly_chart(fig_cal, width='stretch')

# 5. Mapa Espacial y Descarga de CSV
col_map, col_dl = st.columns([2, 1])

with col_map:
    st.subheader(f"🗺️ Spatial Distribution ({selected_year})")
    map_data = df_filtered[df_filtered['year'] == selected_year][['lat_bin', 'lon_bin']].drop_duplicates()
    map_data = map_data.rename(columns={'lat_bin': 'lat', 'lon_bin': 'lon'})
    st.map(map_data)

with col_dl:
    st.subheader("📥 Export Calibrated Data")
    st.write("Download the harmonized MODIS + VIIRS dataset for the selected coordinates and date range.")
    csv_export = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download Harmonized CSV",
        data=csv_export,
        file_name=f"harmonized_fires_{preset.replace(' ', '_').lower()}.csv",
        mime="text/csv",
    )
    st.info("💡 **Calibration Note:** Pre-2012 MODIS records are cross-calibrated to VIIRS 375m scale using Gradient Boosting with optical pixel geometry (`scan × track`) and Duan's smearing correction (`Out-of-sample R² = 0.887` across 8,497 overlapping 0.25° cells).")