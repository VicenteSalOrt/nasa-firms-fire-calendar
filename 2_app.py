import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuración general de la página
st.set_page_config(page_title="FIRMS Fire Calendar", page_icon="🔥", layout="wide")

st.title("🔥 Harmonized Wildfire Activity Calendar (MODIS + VIIRS)")
st.markdown(
    "26 years of cross-calibrated NASA satellite thermal anomalies "
    "(`Out-of-sample R² = 0.887` | Blind Hindcast Bias `< 5%`) for early warning and fire management."
)

# 2. Cargar dataset calibrado
@st.cache_data
def load_data():
    return pd.read_csv("harmonized_chile.csv")

df = load_data()

# 3. Barra Lateral: Filtros de Ubicación, Tiempo y Métrica
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
st.sidebar.header("⚙️ Metric & Resolution")
metric_choice = st.sidebar.radio(
    "Select Metric to Analyze:",
    ["Calibrated Hotspots (Count)", "Fire Radiative Power (FRP - MW)"]
)
value_col = "harmonized_hotspots" if "Hotspots" in metric_choice else "harmonized_frp"
unit_label = "Hotspots" if value_col == "harmonized_hotspots" else "MW"

st.sidebar.markdown("---")
st.sidebar.caption(
    "**Calibration Summary:**\n"
    "- Grid: `0.25° × 0.25°`\n"
    "- Swath Geometry: `scan × track`\n"
    "- Orbital De-duplication: Active\n"
    "- Fixed 26-year `Cividis` scale"
)

# Filtrar por coordenadas
df_filtered = df[
    (df['lat_bin'].between(lat_min, lat_max)) &
    (df['lon_bin'].between(lon_min, lon_max))
]

if df_filtered.empty:
    st.warning("⚠️ No fire hotspots detected in the selected coordinates. Try expanding the bounding box.")
    st.stop()

# 4. Controles Temporales (Año y Mes)
st.subheader("📊 Historical Anomaly Detector")
years_available = sorted(df_filtered['year'].unique())
default_year = 2023 if 2023 in years_available else years_available[-1]

month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
month_options = ["All Year (Annual)"] + month_names

col_ctrl1, col_ctrl2 = st.columns([3, 1])
with col_ctrl1:
    selected_year = st.slider(
        "Select Year to Benchmark:",
        int(min(years_available)),
        int(max(years_available)),
        int(default_year)
    )
with col_ctrl2:
    selected_month_label = st.selectbox("Filter Map & KPIs by Month:", month_options, index=0)

# Cálculo de series mensuales completas (26 años), enmascarando meses futuros (Dic 2026)
all_years = range(int(min(years_available)), int(max(years_available)) + 1)
full_grid = pd.MultiIndex.from_product([all_years, range(1, 13)], names=['year', 'month']).to_frame().reset_index(drop=True)
monthly_raw = df_filtered.groupby(['year', 'month'])[value_col].sum().reset_index()
monthly_totals = pd.merge(full_grid, monthly_raw, on=['year', 'month'], how='left').fillna(0)
monthly_totals.loc[(monthly_totals['year'] == 2026) & (monthly_totals['month'] > 11), value_col] = np.nan

# KPIs dinámicos y referencia máxima histórica fija
if selected_month_label == "All Year (Annual)":
    annual_totals = monthly_totals.groupby('year')[value_col].sum()
    total_selected = annual_totals.loc[selected_year]
    median_baseline = annual_totals.median()
    period_title = f"{selected_year} (Full Year)"
    df_map_source = df_filtered[df_filtered['year'] == selected_year]
    ref_cell_max = float(df_filtered.groupby(['year', 'lat_bin', 'lon_bin'])[value_col].sum().max())
else:
    month_idx = month_names.index(selected_month_label) + 1
    month_series = monthly_totals[monthly_totals['month'] == month_idx].set_index('year')[value_col].dropna()
    total_selected = month_series.loc[selected_year] if selected_year in month_series.index else 0.0
    median_baseline = month_series.median()
    period_title = f"{selected_month_label} {selected_year}"
    df_map_source = df_filtered[(df_filtered['year'] == selected_year) & (df_filtered['month'] == month_idx)]
    ref_cell_max = float(df_filtered[value_col].max())

ref_cell_max = max(ref_cell_max, 1.0)

if median_baseline > 0:
    anomaly_str = f"{((total_selected - median_baseline) / median_baseline * 100):+.1f}%"
elif total_selected > 0:
    anomaly_str = "Above 0 baseline"
else:
    anomaly_str = "0.0% (Normal)"

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric(f"Activity in {period_title}", f"{total_selected:,.0f} {unit_label}")
kpi2.metric(f"26-Year Median ({selected_month_label.split()[0]})", f"{median_baseline:,.0f} {unit_label}")
kpi3.metric("Anomaly vs. Median", anomaly_str)

st.markdown("---")

# 5. Calendario de 26 Años + Curva Estacional Comparativa
col_cal, col_curve = st.columns([1.4, 1])

with col_cal:
    st.subheader("🗓️ 26-Year Burning Activity Calendar")
    calendar_pivot = monthly_totals.pivot(index='year', columns='month', values=value_col)
    calendar_pivot = calendar_pivot.reindex(columns=range(1, 13))

    fig_cal = px.imshow(
        calendar_pivot,
        labels=dict(x="Month", y="Year", color=unit_label),
        x=month_names,
        y=calendar_pivot.index.astype(str),
        color_continuous_scale="Cividis",
        aspect="auto"
    )
    fig_cal.update_layout(height=480, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig_cal, width='stretch')

with col_curve:
    st.subheader(f"📈 Seasonal Profile ({selected_year} vs. Baseline)")
    stats_monthly = monthly_totals.groupby('month')[value_col].agg(
        median='median',
        p25=lambda x: x.quantile(0.25),
        p75=lambda x: x.quantile(0.75)
    ).reset_index()
    year_curve = monthly_totals[monthly_totals['year'] == selected_year].sort_values('month')
    max_monthly_all_time = max(float(monthly_totals[value_col].max()), 1.0)

    fig_curve = go.Figure()
    fig_curve.add_trace(go.Scatter(
        x=month_names + month_names[::-1],
        y=list(stats_monthly['p75']) + list(stats_monthly['p25'])[::-1],
        fill='toself',
        fillcolor='rgba(100, 149, 237, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Normal Range (25th–75th pct)'
    ))
    fig_curve.add_trace(go.Scatter(
        x=month_names,
        y=stats_monthly['median'],
        mode='lines',
        line=dict(color='#6495ED', dash='dash', width=2),
        name='26-Year Median'
    ))
    fig_curve.add_trace(go.Scatter(
        x=month_names,
        y=year_curve[value_col],
        mode='lines+markers',
        line=dict(color='#FDE725', width=3),
        marker=dict(size=7),
        name=f'Year {selected_year}'
    ))
    fig_curve.update_layout(
        height=480,
        margin=dict(l=10, r=10, t=20, b=10),
        yaxis=dict(title=unit_label, range=[0, max_monthly_all_time * 1.05]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_curve, width='stretch')

st.markdown("---")

# 6. Mapa Espacial Normalizado con Zoom Dinámico y Visibilidad Mínima
col_map, col_dl = st.columns([2.2, 1])

with col_map:
    st.subheader(f"🗺️ Spatial Fire Intensity Map — {period_title}")
    if df_map_source.empty:
        st.info(f"No thermal anomalies detected in {period_title} for this region.")
    else:
        map_agg = df_map_source.groupby(['lat_bin', 'lon_bin']).agg(
            harmonized_hotspots=('harmonized_hotspots', 'sum'),
            harmonized_frp=('harmonized_frp', 'sum')
        ).reset_index()

        center_lat = (lat_min + lat_max) / 2.0
        center_lon = (lon_min + lon_max) / 2.0
        span = max(abs(lat_max - lat_min), abs(lon_max - lon_min))
        if span > 20:
            zoom_lvl = 3.2
        elif span > 8:
            zoom_lvl = 4.8
        elif span > 3:
            zoom_lvl = 5.8
        else:
            zoom_lvl = 6.8

        max_bubble_px = 30.0
        map_func = px.scatter_map if hasattr(px, "scatter_map") else px.scatter_mapbox
        style_kwarg = {"map_style": "carto-darkmatter"} if hasattr(px, "scatter_map") else {"mapbox_style": "carto-darkmatter"}

        fig_map = map_func(
            map_agg,
            lat="lat_bin",
            lon="lon_bin",
            size=value_col,
            color=value_col,
            color_continuous_scale="Cividis",
            range_color=[0, ref_cell_max],
            size_max=int(max_bubble_px),
            zoom=zoom_lvl,
            center={"lat": center_lat, "lon": center_lon},
            hover_data={
                "lat_bin": ":.2f",
                "lon_bin": ":.2f",
                "harmonized_hotspots": ":,.0f",
                "harmonized_frp": ":,.1f"
            },
            labels={
                "lat_bin": "Latitude",
                "lon_bin": "Longitude",
                "harmonized_hotspots": "Calibrated Hotspots",
                "harmonized_frp": "FRP (MW)"
            },
            **style_kwarg
        )
        fig_map.update_traces(
            marker=dict(
                sizeref=2.0 * ref_cell_max / (max_bubble_px ** 2),
                sizemode='area',
                sizemin=4
            )
        )
        fig_map.update_layout(height=500, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_map, width='stretch')

with col_dl:
    st.subheader("📥 Export Calibrated Data")
    st.write(f"Download the harmonized MODIS + VIIRS dataset for **{preset}** ({len(df_filtered):,} grid-month records).")
    csv_export = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download Harmonized CSV",
        data=csv_export,
        file_name=f"harmonized_fires_{preset.replace(' ', '_').lower()}.csv",
        mime="text/csv",
    )
    st.info(
        "💡 **Methodology:** Pre-2012 MODIS records are cross-calibrated to VIIRS 375m scale "
        "using Gradient Boosting with optical pixel geometry (`scan × track`) and Duan's smearing "
        "correction (`Out-of-sample R² = 0.887` across 8,497 overlapping 0.25° cells)."
    )