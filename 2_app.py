import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuración general de la página
st.set_page_config(page_title="FIRMS Fire Calendar", page_icon="🔥", layout="wide")

# 2. Selector de Idioma en la Barra Lateral (English por defecto para entrega oficial NASA)
lang = st.sidebar.radio("🌐 Language / Idioma", ["English", "Español"], horizontal=True)
is_es = (lang == "Español")

st.sidebar.markdown("---")

# Diccionario bilingüe completo
T = {
    "title": "🔥 Calendario Armonizado de Actividad de Incendios (MODIS + VIIRS)" if is_es else "🔥 Harmonized Wildfire Activity Calendar (MODIS + VIIRS)",
    "subtitle": (
        "26 años de anomalías térmicas satelitales de la NASA calibradas cruzadamente "
        "(`R² fuera de muestra = 0.887` | Sesgo Hindcast Ciego `< 5%`) para alerta temprana y gestión territorial."
        if is_es else
        "26 years of cross-calibrated NASA satellite thermal anomalies "
        "(`Out-of-sample R² = 0.887` | Blind Hindcast Bias `< 5%`) for early warning and fire management."
    ),
    "aoi_header": "📍 Área de Interés (AOI)" if is_es else "📍 Area of Interest (AOI)",
    "preset_label": "Zonas Rápidas (Chile):" if is_es else "Quick Presets (Chile):",
    "all_chile": "Todo Chile" if is_es else "All Chile",
    "custom_coords": "Coordenadas Personalizadas" if is_es else "Custom Coordinates",
    "min_lat": "Latitud Mínima" if is_es else "Min Latitude",
    "max_lat": "Latitud Máxima" if is_es else "Max Latitude",
    "min_lon": "Longitud Mínima" if is_es else "Min Longitude",
    "max_lon": "Longitud Máxima" if is_es else "Max Longitude",
    "metric_header": "⚙️ Métrica y Resolución" if is_es else "⚙️ Metric & Resolution",
    "metric_label": "Selecciona Métrica a Analizar:" if is_es else "Select Metric to Analyze:",
    "opt_hotspots": "Focos Calibrados (Conteo)" if is_es else "Calibrated Hotspots (Count)",
    "opt_frp": "Potencia Radiativa del Fuego (FRP - MW)" if is_es else "Fire Radiative Power (FRP - MW)",
    "unit_hotspots": "Focos" if is_es else "Hotspots",
    "sidebar_summary": (
        "**Resumen de Calibración:**\n"
        "- Malla espacial: `0.25° × 0.25°`\n"
        "- Geometría de barrido: `scan × track`\n"
        "- Desduplicación orbital: Activa\n"
        "- Mediana base: `2000–2025` completos\n"
        "- Paleta `Cividis` apta para daltonismo"
        if is_es else
        "**Calibration Summary:**\n"
        "- Grid: `0.25° × 0.25°`\n"
        "- Swath Geometry: `scan × track`\n"
        "- Orbital De-duplication: Active\n"
        "- Baseline Median: `2000–2025` complete years\n"
        "- Fixed `Cividis` colorblind-safe scale"
    ),
    "no_data_coords": (
        "⚠️ No se detectaron focos de calor en las coordenadas seleccionadas. Intenta ampliar el área."
        if is_es else
        "⚠️ No fire hotspots detected in the selected coordinates. Try expanding the bounding box."
    ),
    "detector_header": "📊 Detector de Anomalías Históricas" if is_es else "📊 Historical Anomaly Detector",
    "year_slider": "Selecciona Año a Evaluar:" if is_es else "Select Year to Benchmark:",
    "month_select": "Filtrar Mapa y KPIs por Mes:" if is_es else "Filter Map & KPIs by Month:",
    "all_year": "Todo el Año (Anual)" if is_es else "All Year (Annual)",
    "ytd_note": (
        "ℹ️ *Nota: 2026 refleja datos acumulados hasta noviembre y se excluye de la mediana anual histórica (2000–2025).*"
        if is_es else
        "ℹ️ *Note: 2026 reflects Year-to-Date observations through November and is excluded from the 2000–2025 annual median baseline.*"
    ),
    "cal_header": "🗓️ Calendario de Actividad (26 Años)" if is_es else "🗓️ 26-Year Burning Activity Calendar",
    "month_axis": "Mes" if is_es else "Month",
    "year_axis": "Año" if is_es else "Year",
    "curve_header": "📈 Perfil Estacional" if is_es else "📈 Seasonal Profile",
    "vs_baseline": "vs. Línea Base" if is_es else "vs. Baseline",
    "norm_range": "Rango Normal (Percentil 25–75)" if is_es else "Normal Range (25th–75th pct)",
    "med_26": "Mediana 26 Años" if is_es else "26-Year Median",
    "year_prefix": "Año" if is_es else "Year",
    "cont_header": "📉 Verificación de Continuidad Instrumental (MODIS Calibrado vs. VIIRS Directo)" if is_es else "📉 26-Year Continuity Check (MODIS Calibrated vs. VIIRS Direct)",
    "modis_cal": "MODIS (Calibrado)" if is_es else "MODIS (Calibrated)",
    "viirs_dir": "VIIRS (Directo)" if is_es else "VIIRS (Direct)",
    "med_annot": "Mediana 2000–2025" if is_es else "2000–2025 Median",
    "trans_annot": "Transición VIIRS 2012" if is_es else "2012 VIIRS Transition",
    "map_header": "🗺️ Mapa Espacial de Intensidad de Fuego" if is_es else "🗺️ Spatial Fire Intensity Map",
    "no_data_period": (
        "No se registraron anomalías térmicas en este período para la zona elegida."
        if is_es else
        "No thermal anomalies detected in this period for this region."
    ),
    "lat_lbl": "Latitud" if is_es else "Latitude",
    "lon_lbl": "Longitud" if is_es else "Longitude",
    "dl_header": "📥 Exportar Datos Calibrados" if is_es else "📥 Export Calibrated Data",
    "dl_btn": "⬇️ Descargar CSV Armonizado" if is_es else "⬇️ Download Harmonized CSV",
    "meth_note": (
        "💡 **Metodología:** Los registros MODIS previos a 2012 fueron calibrados a la escala VIIRS de 375 m "
        "mediante Gradient Boosting con geometría óptica de píxel (`scan × track`) y corrección de Duan "
        "(`R² fuera de muestra = 0.887` en 8,497 celdas de 0.25°; sesgo temporal ciego `+4.88%`)."
        if is_es else
        "💡 **Methodology:** Pre-2012 MODIS records are cross-calibrated to VIIRS 375m scale "
        "using Gradient Boosting with optical pixel geometry (`scan × track`) and Duan's smearing "
        "correction (`Out-of-sample R² = 0.887` across 8,497 overlapping 0.25° cells; blind temporal "
        "hindcast bias `+4.88%`)."
    ),
}

month_names = (
    ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    if is_es else
    ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
)

st.title(T["title"])
st.markdown(T["subtitle"])

# 3. Cargar dataset calibrado
@st.cache_data
def load_data():
    return pd.read_csv("harmonized_chile.csv")

df = load_data()

# 4. Barra Lateral: Filtros de Ubicación y Métrica
st.sidebar.header(T["aoi_header"])
preset_keys = ["Biobío & Ñuble", "Valparaíso", "La Araucanía", "All Chile", "Custom Coordinates"]
preset_labels = {
    "Biobío & Ñuble": "Biobío & Ñuble",
    "Valparaíso": "Valparaíso",
    "La Araucanía": "La Araucanía",
    "All Chile": T["all_chile"],
    "Custom Coordinates": T["custom_coords"],
}
preset = st.sidebar.selectbox(
    T["preset_label"],
    preset_keys,
    format_func=lambda k: preset_labels[k]
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
    lat_min = st.sidebar.number_input(T["min_lat"], value=-38.5, format="%.2f")
    lat_max = st.sidebar.number_input(T["max_lat"], value=-36.0, format="%.2f")
    lon_min = st.sidebar.number_input(T["min_lon"], value=-73.8, format="%.2f")
    lon_max = st.sidebar.number_input(T["max_lon"], value=-71.0, format="%.2f")

st.sidebar.markdown("---")
st.sidebar.header(T["metric_header"])
metric_key = st.sidebar.radio(
    T["metric_label"],
    ["hotspots", "frp"],
    format_func=lambda k: T["opt_hotspots"] if k == "hotspots" else T["opt_frp"]
)
value_col = "harmonized_hotspots" if metric_key == "hotspots" else "harmonized_frp"
unit_label = T["unit_hotspots"] if metric_key == "hotspots" else "MW"

st.sidebar.markdown("---")
st.sidebar.caption(T["sidebar_summary"])

# Filtrar por coordenadas
df_filtered = df[
    (df['lat_bin'].between(lat_min, lat_max)) &
    (df['lon_bin'].between(lon_min, lon_max))
]

if df_filtered.empty:
    st.warning(T["no_data_coords"])
    st.stop()

# 5. Controles Temporales y Cálculos Históricos
years_available = sorted(df_filtered['year'].unique())
default_year = 2023 if 2023 in years_available else years_available[-1]

all_years = range(int(min(years_available)), int(max(years_available)) + 1)
full_grid = pd.MultiIndex.from_product([all_years, range(1, 13)], names=['year', 'month']).to_frame().reset_index(drop=True)
monthly_raw = df_filtered.groupby(['year', 'month'])[value_col].sum().reset_index()
monthly_totals = pd.merge(full_grid, monthly_raw, on=['year', 'month'], how='left').fillna(0)
monthly_totals.loc[(monthly_totals['year'] == 2026) & (monthly_totals['month'] > 11), value_col] = np.nan

# Temporada crítica histórica (Top 3 meses con mayor mediana en 2000–2025)
hist_complete = monthly_totals[monthly_totals['year'] < 2026]
month_medians = hist_complete.groupby('month')[value_col].median()
top3_months = month_medians.nlargest(3)
top3_indices = sorted(top3_months.index.tolist())
top3_names = " – ".join([month_names[i - 1] for i in top3_indices])
top3_share = (top3_months.sum() / month_medians.sum() * 100) if month_medians.sum() > 0 else 0.0

# Totales anuales y mediana de años completos (2000–2025)
annual_totals = monthly_totals.groupby('year')[value_col].sum()
complete_years = annual_totals[annual_totals.index < 2026]
annual_median_baseline = complete_years.median() if not complete_years.empty else annual_totals.median()

st.subheader(T["detector_header"])
col_ctrl1, col_ctrl2 = st.columns([3, 1])
with col_ctrl1:
    selected_year = st.slider(
        T["year_slider"],
        int(min(years_available)),
        int(max(years_available)),
        int(default_year)
    )
with col_ctrl2:
    month_idx_choice = st.selectbox(
        T["month_select"],
        options=list(range(0, 13)),
        format_func=lambda m: T["all_year"] if m == 0 else month_names[m - 1]
    )

if month_idx_choice == 0:
    total_selected = annual_totals.loc[selected_year]
    median_baseline = annual_median_baseline
    period_title = (
        f"{selected_year} ({'Acum. Nov' if is_es else 'YTD Nov'})"
        if selected_year == 2026 else
        f"{selected_year} ({'Año Completo' if is_es else 'Full Year'})"
    )
    median_label = "Mediana Anual (2000–2025)" if is_es else "2000–2025 Median (Annual)"
    df_map_source = df_filtered[df_filtered['year'] == selected_year]
    ref_cell_max = float(df_filtered.groupby(['year', 'lat_bin', 'lon_bin'])[value_col].sum().max())
else:
    month_series = monthly_totals[monthly_totals['month'] == month_idx_choice].set_index('year')[value_col].dropna()
    total_selected = month_series.loc[selected_year] if selected_year in month_series.index else 0.0
    median_baseline = month_series.median()
    period_title = f"{month_names[month_idx_choice - 1]} {selected_year}"
    median_label = f"Mediana Histórica ({month_names[month_idx_choice - 1]})" if is_es else f"Historical Median ({month_names[month_idx_choice - 1]})"
    df_map_source = df_filtered[(df_filtered['year'] == selected_year) & (df_filtered['month'] == month_idx_choice)]
    ref_cell_max = float(df_filtered[value_col].max())

ref_cell_max = max(ref_cell_max, 1.0)
region_display = preset_labels[preset]

# 6. Semáforo de Riesgo Ciudadano (Diagnóstico inmediato en 5 segundos)
if median_baseline > 0:
    ratio = total_selected / median_baseline
    pct_diff = (ratio - 1.0) * 100
    anomaly_str = f"{pct_diff:+.1f}%"

    if ratio >= 2.0:
        if is_es:
            st.error(
                f"🔴 **ALERTA EXTREMA en {region_display} ({period_title}):** "
                f"La actividad térmica es **{ratio:.1f} veces mayor** ({pct_diff:+.1f}%) que lo normal en los últimos 26 años.\n\n"
                f"📅 **Ventana Crítica Local:** Históricamente, el **{top3_share:.0f}%** de la actividad de fuego en esta zona se concentra entre **{top3_names}**."
            )
        else:
            st.error(
                f"🔴 **EXTREME FIRE ACTIVITY in {region_display} ({period_title}):** "
                f"Thermal activity is **{ratio:.1f}x higher** ({pct_diff:+.1f}%) than the 26-year historical baseline.\n\n"
                f"📅 **Local Critical Window:** Historically, **{top3_share:.0f}%** of fire activity in this area occurs during **{top3_names}**."
            )
    elif ratio >= 1.25:
        if is_es:
            st.warning(
                f"🟠 **ACTIVIDAD ELEVADA en {region_display} ({period_title}):** "
                f"Se registra un **{pct_diff:+.1f}%** por encima de la mediana histórica ({ratio:.1f}x lo habitual).\n\n"
                f"📅 **Ventana Crítica Local:** El **{top3_share:.0f}%** de la actividad anual se concentra en **{top3_names}**."
            )
        else:
            st.warning(
                f"🟠 **ELEVATED FIRE ACTIVITY in {region_display} ({period_title}):** "
                f"Activity is **{pct_diff:+.1f}%** above the historical median ({ratio:.1f}x normal levels).\n\n"
                f"📅 **Local Critical Window:** **{top3_share:.0f}%** of annual fire activity concentrates in **{top3_names}**."
            )
    elif ratio >= 0.75:
        if is_es:
            st.success(
                f"🟢 **NIVEL ESTACIONAL NORMAL en {region_display} ({period_title}):** "
                f"La actividad ({pct_diff:+.1f}%) se mantiene dentro del rango histórico esperado.\n\n"
                f"📅 **Ventana Crítica Local:** Recuerda que el **{top3_share:.0f}%** de los incendios de esta zona ocurren entre **{top3_names}**."
            )
        else:
            st.success(
                f"🟢 **NORMAL SEASONAL LEVEL in {region_display} ({period_title}):** "
                f"Activity ({pct_diff:+.1f}%) remains within the expected 26-year historical range.\n\n"
                f"📅 **Local Critical Window:** **{top3_share:.0f}%** of fires in this zone historically occur during **{top3_names}**."
            )
    else:
        if is_es:
            st.info(
                f"🔵 **ACTIVIDAD BAJO LO NORMAL en {region_display} ({period_title}):** "
                f"Se observa un **{abs(pct_diff):.1f}% menos** actividad que la mediana de 26 años.\n\n"
                f"📅 **Ventana Crítica Local:** La temporada de mayor riesgo en esta zona es **{top3_names}** (**{top3_share:.0f}%** del total)."
            )
        else:
            st.info(
                f"🔵 **BELOW-AVERAGE ACTIVITY in {region_display} ({period_title}):** "
                f"Activity is **{abs(pct_diff):.1f}% lower** than the 26-year median.\n\n"
                f"📅 **Local Critical Window:** Peak fire danger in this zone occurs during **{top3_names}** (**{top3_share:.0f}%** of annual total)."
            )
else:
    if total_selected > 0:
        anomaly_str = "Sobre base 0" if is_es else "Above 0 baseline"
        st.warning(
            f"🟠 **ACTIVIDAD INUSUAL FUERA DE TEMPORADA en {region_display} ({period_title}):** "
            f"Se detectaron {total_selected:,.0f} {unit_label.lower()} en un mes que normalmente registra 0."
            if is_es else
            f"🟠 **UNUSUAL OFF-SEASON ACTIVITY in {region_display} ({period_title}):** "
            f"Detected {total_selected:,.0f} {unit_label.lower()} in a month with a historical median of 0."
        )
    else:
        anomaly_str = "0.0% (Normal)"
        st.success(
            f"🟢 **SIN ACTIVIDAD DE INCENDIOS en {region_display} ({period_title}):** Comportamiento normal para este período."
            if is_es else
            f"🟢 **NO FIRE ACTIVITY in {region_display} ({period_title}):** Normal baseline behavior for this period."
        )

# 7. Tarjetas KPI
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric(
    f"{'Actividad en' if is_es else 'Activity in'} {period_title}",
    f"{total_selected:,.0f} {unit_label}"
)
kpi2.metric(median_label, f"{median_baseline:,.0f} {unit_label}")
kpi3.metric("Anomalía vs. Mediana" if is_es else "Anomaly vs. Median", anomaly_str)

if selected_year == 2026 and month_idx_choice == 0:
    st.caption(T["ytd_note"])

st.markdown("---")

# 8. Calendario de 26 Años + Curva Estacional Comparativa
col_cal, col_curve = st.columns([1.4, 1])

with col_cal:
    st.subheader(T["cal_header"])
    calendar_pivot = monthly_totals.pivot(index='year', columns='month', values=value_col)
    calendar_pivot = calendar_pivot.reindex(columns=range(1, 13))

    fig_cal = px.imshow(
        calendar_pivot,
        labels=dict(x=T["month_axis"], y=T["year_axis"], color=unit_label),
        x=month_names,
        y=calendar_pivot.index.astype(str),
        color_continuous_scale="Cividis",
        aspect="auto"
    )
    fig_cal.update_layout(height=480, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig_cal, width='stretch')

with col_curve:
    st.subheader(f"{T['curve_header']} ({selected_year} {T['vs_baseline']})")
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
        name=T["norm_range"]
    ))
    fig_curve.add_trace(go.Scatter(
        x=month_names,
        y=stats_monthly['median'],
        mode='lines',
        line=dict(color='#6495ED', dash='dash', width=2),
        name=T["med_26"]
    ))
    fig_curve.add_trace(go.Scatter(
        x=month_names,
        y=year_curve[value_col],
        mode='lines+markers',
        line=dict(color='#FDE725', width=3),
        marker=dict(size=7),
        name=f"{T['year_prefix']} {selected_year}"
    ))
    fig_curve.update_layout(
        height=480,
        margin=dict(l=10, r=10, t=20, b=10),
        yaxis=dict(title=unit_label, range=[0, max_monthly_all_time * 1.05]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_curve, width='stretch')

st.markdown("---")

# 9. Prueba Visual de Continuidad Instrumental (2000–2026)
st.subheader(T["cont_header"])
annual_df = annual_totals.reset_index()
annual_df['Sensor Regime'] = np.where(annual_df['year'] < 2012, T["modis_cal"], T["viirs_dir"])

fig_trend = px.bar(
    annual_df,
    x='year',
    y=value_col,
    color='Sensor Regime',
    color_discrete_map={T["modis_cal"]: '#3B528B', T["viirs_dir"]: '#FDE725'},
    labels={'year': T["year_axis"], value_col: unit_label, 'Sensor Regime': 'Sensor'}
)
fig_trend.add_hline(
    y=annual_median_baseline,
    line_dash="dash",
    line_color="white",
    annotation_text=T["med_annot"],
    annotation_position="top left"
)
fig_trend.add_vline(
    x=2011.5,
    line_dash="dot",
    line_color="#FF6B6B",
    annotation_text=T["trans_annot"],
    annotation_position="top right"
)
fig_trend.update_layout(
    height=320,
    margin=dict(l=10, r=10, t=30, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig_trend, width='stretch')

st.markdown("---")

# 10. Mapa Espacial Normalizado con Zoom Dinámico y Descarga CSV
col_map, col_dl = st.columns([2.2, 1])

with col_map:
    st.subheader(f"{T['map_header']} — {period_title}")
    if df_map_source.empty:
        st.info(T["no_data_period"])
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
                "lat_bin": T["lat_lbl"],
                "lon_bin": T["lon_lbl"],
                "harmonized_hotspots": T["opt_hotspots"],
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
    st.subheader(T["dl_header"])
    if is_es:
        st.write(f"Descarga la serie armonizada MODIS + VIIRS para **{region_display}** ({len(df_filtered):,} registros celda-mes).")
    else:
        st.write(f"Download the harmonized MODIS + VIIRS dataset for **{region_display}** ({len(df_filtered):,} grid-month records).")

    csv_export = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=T["dl_btn"],
        data=csv_export,
        file_name=f"harmonized_fires_{preset.replace(' ', '_').lower()}.csv",
        mime="text/csv",
    )
    st.info(T["meth_note"])