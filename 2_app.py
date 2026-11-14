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
    "tab_dash": "🔥 Tablero Interactivo" if is_es else "🔥 Interactive Dashboard",
    "tab_guide": "📖 Guía Ciudadana: ¿Qué significa cada cosa?" if is_es else "📖 Citizen Guide: What Everything Means",
    "quick_intro_expander": "👋 ¿Primera vez aquí? Lee esta guía rápida en lenguaje simple (30 segundos)" if is_es else "👋 First time here? Read this 30-second plain-language guide",
    "quick_intro_body": """Esta herramienta traduce **26 años de observaciones satelitales de la NASA (2000–2026)** en un semáforo claro para que cualquier persona entienda el riesgo de incendios en su territorio:
- **¿Qué mide?** **Focos de calor** (puntos donde el satélite detecta fuego activo) y **FRP** (la fuerza o potencia térmica del incendio medida en megawatts).
- **¿Por qué dice 'Armonizado'?** En 2012 la NASA lanzó satélites con cámaras mucho más nítidas. Si se mezclan los datos sin corregir, parece que los incendios se multiplicaron de golpe; aquí igualamos ambos sensores para mostrar la realidad.
- **¿Cómo usarlo?** Elige **Todo Chile**, cualquiera de las **16 regiones** o **Coordenadas Personalizadas** en el menú izquierdo, mueve el año arriba y revisa el **Semáforo de Alerta** y los **cuadros amarillos del calendario**. Para ver ejemplos detallados, abre la pestaña **📖 Guía Ciudadana** arriba.""" if is_es else """This tool translates **26 years of NASA satellite observations (2000–2026)** into a clear traffic-light dashboard so anyone can understand local wildfire danger:
- **What does it measure?** **Hotspots** (locations where satellites detect active fire) and **FRP** (fire heat intensity measured in megawatts).
- **Why 'Harmonized'?** In 2012 NASA launched satellites with sharper cameras. Merging raw data without calibration creates a fake jump; we aligned both sensors to reveal true fire trends.
- **How to use it?** Pick **All Chile**, any of the **16 administrative regions**, or **Custom Coordinates** on the left menu, slide the year above, and check the **Alert Banner** and **bright yellow calendar cells**. Open the **📖 Citizen Guide** tab above for a full plain-language walkthrough.""",
    "aoi_header": "📍 Territorio / Área de Interés" if is_es else "📍 Territory / Area of Interest",
    "preset_label": "Selecciona País o Región (16 Regiones):" if is_es else "Select Country or Region (16 Regions):",
    "all_chile": "🇨🇱 Todo Chile (País Completo)" if is_es else "🇨🇱 All Chile (Full Country)",
    "custom_coords": "🧭 Coordenadas Personalizadas" if is_es else "🧭 Custom Coordinates",
    "min_lat": "Latitud Mínima" if is_es else "Min Latitude",
    "max_lat": "Latitud Máxima" if is_es else "Max Latitude",
    "min_lon": "Longitud Mínima" if is_es else "Min Longitude",
    "max_lon": "Longitud Máxima" if is_es else "Max Longitude",
    "metric_header": "⚙️ Métrica y Resolución" if is_es else "⚙️ Metric & Resolution",
    "metric_label": "Selecciona Métrica a Analizar:" if is_es else "Select Metric to Analyze:",
    "opt_hotspots": "Focos Calibrados (Conteo)" if is_es else "Calibrated Hotspots (Count)",
    "opt_frp": "Potencia Radiativa del Fuego (FRP - MW)" if is_es else "Fire Radiative Power (FRP - MW)",
    "unit_hotspots": "Focos" if is_es else "Hotspots",
    "sidebar_summary": """**Resumen de Calibración:**
- Cobertura: `Todo Chile (16 regiones)`
- Malla espacial: `0.25° × 0.25°`
- Geometría de barrido: `scan × track`
- Desduplicación orbital: Activa
- Mediana base: `2000–2025` completos
- Paleta `Cividis` apta para daltonismo""" if is_es else """**Calibration Summary:**
- Coverage: `All Chile (16 regions)`
- Grid: `0.25° × 0.25°`
- Swath Geometry: `scan × track`
- Orbital De-duplication: Active
- Baseline Median: `2000–2025` complete years
- Fixed `Cividis` colorblind-safe scale""",
    "no_data_coords": (
        "⚠️ No se detectaron focos de calor en la zona seleccionada durante los 26 años analizados."
        if is_es else
        "⚠️ No fire hotspots detected in the selected area across the 26-year record."
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

# 3. Cargar dataset calibrado (contiene Chile completo de Arica a Magallanes)
@st.cache_data
def load_data():
    return pd.read_csv("harmonized_chile.csv")

df = load_data()

# 4. Barra Lateral: País completo, las 16 Regiones de Chile (Norte a Sur) y Coordenadas Libres
REGIONS_BOUNDS = {
    "All Chile": (-56.0, -17.0, -76.0, -66.0),
    "Arica y Parinacota": (-19.25, -17.50, -70.50, -68.75),
    "Tarapacá": (-21.65, -18.90, -70.50, -68.25),
    "Antofagasta": (-26.10, -20.90, -70.80, -66.80),
    "Atacama": (-29.60, -25.25, -71.80, -68.25),
    "Coquimbo": (-32.30, -29.00, -71.80, -69.75),
    "Valparaíso": (-33.90, -32.00, -72.00, -69.90),
    "Región Metropolitana": (-34.30, -32.90, -71.80, -69.75),
    "O'Higgins": (-35.05, -33.85, -72.20, -70.00),
    "Maule": (-36.55, -34.70, -72.85, -70.25),
    "Ñuble": (-37.25, -36.00, -73.00, -71.00),
    "Biobío": (-38.50, -36.40, -73.80, -71.00),
    "La Araucanía": (-39.65, -37.55, -73.60, -70.80),
    "Los Ríos": (-40.70, -39.25, -73.80, -71.50),
    "Los Lagos": (-44.10, -40.25, -74.90, -71.50),
    "Aysén": (-49.30, -43.60, -75.80, -71.00),
    "Magallanes": (-56.00, -48.50, -75.80, -66.20),
}

preset_keys = list(REGIONS_BOUNDS.keys()) + ["Custom Coordinates"]
preset_labels = {
    "All Chile": T["all_chile"],
    "Arica y Parinacota": "XV · Arica y Parinacota",
    "Tarapacá": "I · Tarapacá",
    "Antofagasta": "II · Antofagasta",
    "Atacama": "III · Atacama",
    "Coquimbo": "IV · Coquimbo",
    "Valparaíso": "V · Valparaíso",
    "Región Metropolitana": "RM · Metropolitana",
    "O'Higgins": "VI · O'Higgins",
    "Maule": "VII · Maule",
    "Ñuble": "XVI · Ñuble",
    "Biobío": "VIII · Biobío",
    "La Araucanía": "IX · La Araucanía",
    "Los Ríos": "XIV · Los Ríos",
    "Los Lagos": "X · Los Lagos",
    "Aysén": "XI · Aysén",
    "Magallanes": "XII · Magallanes",
    "Custom Coordinates": T["custom_coords"],
}

st.sidebar.header(T["aoi_header"])
preset = st.sidebar.selectbox(
    T["preset_label"],
    preset_keys,
    index=preset_keys.index("Biobío"),
    format_func=lambda k: preset_labels[k]
)

if preset in REGIONS_BOUNDS:
    lat_min, lat_max, lon_min, lon_max = REGIONS_BOUNDS[preset]
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

# Pestañas principales: Tablero en vivo + Guía Ciudadana explicativa
tab_dashboard, tab_citizen_guide = st.tabs([T["tab_dash"], T["tab_guide"]])

# ==============================================================================
# PESTAÑA 1: TABLERO INTERACTIVO EN VIVO
# ==============================================================================
with tab_dashboard:
    with st.expander(T["quick_intro_expander"], expanded=False):
        st.markdown(T["quick_intro_body"])

    # Filtrar por coordenadas
    df_filtered = df[
        (df['lat_bin'].between(lat_min, lat_max)) &
        (df['lon_bin'].between(lon_min, lon_max))
    ]

    if df_filtered.empty:
        st.warning(T["no_data_coords"])
        st.stop()

    # Controles Temporales y Cálculos Históricos
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

    # Semáforo de Riesgo Ciudadano (Diagnóstico inmediato en 5 segundos)
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

    # Tarjetas KPI
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

    # Calendario de 26 Años + Curva Estacional Comparativa
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

    # Prueba Visual de Continuidad Instrumental (2000–2026)
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

    # Mapa Espacial Normalizado con Zoom Dinámico Logarítmico y Descarga CSV
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
            zoom_lvl = float(np.clip(8.2 - np.log2(max(span, 0.5)), 3.2, 7.5))

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

# ==============================================================================
# PESTAÑA 2: GUÍA CIUDADANA EN LENGUAJE SIMPLE
# ==============================================================================
with tab_citizen_guide:
    if is_es:
        st.header("📖 Guía Ciudadana: Entendiendo el Riesgo de Incendios desde el Espacio")
        st.markdown(
            "No necesitas ser científico ni saber programar para usar esta herramienta. "
            "Aquí te explicamos **con palabras simples** qué significan los números, los colores y por qué este mapa ayuda a proteger comunidades."
        )

        st.subheader("1. ¿Por qué existe esta plataforma? (El problema de las 'dos cámaras')")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.info(
                "**🛰️ Satélites Antiguos (MODIS, desde el año 2000)**\n\n"
                "Imagina tomar una foto desde muy lejos donde cada cuadro mide **1 km × 1 km**. "
                "Solo alcanza a ver incendios grandes; las quemas pequeñas pasan desapercibidas."
            )
        with col_g2:
            st.success(
                "**🛰️ Satélites Modernos (VIIRS, desde 2012)**\n\n"
                "Tienen una cámara mucho más nítida donde cada cuadro mide **375 m × 375 m**. "
                "Detectan hasta fogatas grandes o quemas agrícolas pequeñas."
            )
        st.markdown(
            "> **¿Cuál era el problema?** Si juntas los archivos de ambos satélites sin corregirlos, parece que en 2012 los incendios en Chile se multiplicaron mágicamente. "
            "Eso es una **ilusión óptica**: no hubo más fuego, simplemente pusieron una cámara mejor. "
            "Nuestro sistema **traduce** los datos antiguos a la escala moderna (con menos de un 5% de margen de error) para que puedas comparar 26 años en igualdad de condiciones."
        )

        st.markdown("---")
        st.subheader("2. Diccionario sin tecnicismos: ¿Qué significa cada palabra?")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                "#### 🔥 Foco de Calor (*Calibrated Hotspot*)\n"
                "No significa necesariamente una casa quemándose. Es un **cuadrante de terreno donde el satélite detectó una temperatura anormalmente alta** "
                "(un incendio forestal, un frente de avance del fuego o una quema agrícola). Mientras más focos hay en un mes, más extenso es el problema."
            )
            st.markdown(
                "#### 📏 Mediana Histórica (26 años)\n"
                "Es lo que consideramos **'normal' o habitual** para un año o un mes en tu zona entre 2000 y 2025. "
                "Sirve como regla de comparación para saber si una temporada estuvo tranquila o fuera de control."
            )
        with c2:
            st.markdown(
                "#### ⚡ Potencia Radiativa del Fuego (*FRP - MW*)\n"
                "Mide **con cuánta fuerza o violencia arde el fuego** (en megawatts). "
                "Un incendio puede tener pocos focos, pero si tiene un FRP muy alto, significa que libera muchísimo calor y es muy peligroso para los brigadistas."
            )
            st.markdown(
                "#### 🚨 Anomalía vs. Mediana (%)\n"
                "Indica cuánto subió o bajó el fuego respecto a un año normal. Por ejemplo, en **Biobío en 2023**, la anomalía fue de cientos por ciento sobre lo normal: "
                "eso significa varias veces la cantidad de fuego habitual."
            )

        st.markdown("---")
        st.subheader("3. ¿Cómo leer cada gráfico de la página principal?")
        st.markdown(
            "1. **🚦 El Semáforo Superior (Rojo, Naranjo, Verde o Azul):** Te da el diagnóstico en 5 segundos sin hacer cálculos y te avisa cuáles son los **3 meses más peligrosos** de tu región (por ejemplo, *Ene – Feb – Mar* en el centro-sur).\n"
            "2. **🗓️ El Calendario de Colores (2000–2026):** Cada fila es un año y cada columna es un mes. Los cuadros **azul oscuro** son meses tranquilos; los cuadros **amarillo brillante** son emergencias graves (como enero de 2017 o febrero de 2023). Usamos colores diseñados para que personas con **daltonismo** puedan distinguirlos sin dificultad.\n"
            "3. **📈 La Curva Estacional:** La línea amarilla muestra el año que elegiste; la zona sombreada azul muestra lo que es normal. Cuando la línea amarilla se sale muy por arriba de la sombra azul, estás frente a una temporada crítica.\n"
            "4. **🗺️ El Mapa de Burbujas:** Muestra *dónde* ocurrió el fuego. Los círculos grandes y amarillos indican zonas con alta concentración de incendios; los puntos pequeños y azules muestran actividad baja."
        )

        st.markdown("---")
        st.subheader("4. ¿A quién le sirve esta herramienta?")
        st.markdown(
            "- **Vecinos, agricultores y juntas de vecinos:** Para saber en qué meses exactos deben limpiar maleza, hacer cortafuegos preventivos y extremar cuidados.\n"
            "- **Municipios y encargados de emergencia:** Para respaldar con evidencia histórica dónde concentrar recursos de prevención antes de que empiece el verano.\n"
            "- **Investigadores y analistas (CONAF, SENAPRED, universidades):** Pueden descargar los datos ya calibrados en formato **CSV** con un clic y abrirlos directamente en QGIS, Excel o Python."
        )
    else:
        st.header("📖 Citizen Guide: Understanding Wildfire Risk from Space")
        st.markdown(
            "You do not need to be a scientist or programmer to use this tool. "
            "Here is a **plain-language guide** explaining what every number and color means, and how communities can use it."
        )

        st.subheader("1. Why does this platform exist? (The 'Two Cameras' Problem)")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.info(
                "**🛰️ Older Satellites (MODIS, since 2000)**\n\n"
                "Imagine taking a photo from very far away where every pixel covers **1 km × 1 km**. "
                "It detects large wildfires clearly, while smaller burns go unnoticed."
            )
        with col_g2:
            st.success(
                "**🛰️ Modern Satellites (VIIRS, since 2012)**\n\n"
                "They carry a sharper sensor where each pixel covers **375 m × 375 m**, "
                "detecting much smaller fires and agricultural burns."
            )
        st.markdown(
            "> **What was the catch?** If you merge raw files from both satellites without calibration, it looks like wildfires suddenly exploded worldwide in 2012. "
            "That is an **optical illusion**: fire didn't suddenly multiply—NASA simply upgraded its camera. "
            "Our system **translates** older MODIS records onto the modern VIIRS scale (with under 5% cumulative bias) so all 26 years can be compared fairly."
        )

        st.markdown("---")
        st.subheader("2. Plain-Language Glossary: What Does Every Term Mean?")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                "#### 🔥 Calibrated Hotspot\n"
                "A hotspot is a **patch of land where the satellite detected abnormally high heat** "
                "(an active wildfire front or agricultural burn). More hotspots in a given month mean wider fire spread."
            )
            st.markdown(
                "#### 📏 26-Year Historical Median\n"
                "This is the **'normal' or typical level** of fire activity for a region between 2000 and 2025. "
                "It acts as our yardstick to tell whether a season was calm or unusually severe."
            )
        with c2:
            st.markdown(
                "#### ⚡ Fire Radiative Power (*FRP - MW*)\n"
                "Measures **how intensely a fire is burning** (in megawatts). "
                "A fire with fewer hotspots but high FRP is releasing extreme heat energy and is much harder for firefighters to contain."
            )
            st.markdown(
                "#### 🚨 Anomaly vs. Median (%)\n"
                "Shows how much fire activity increased or decreased compared to a normal year. For example, **Biobío in 2023** spiked several hundred percent above its historical median."
            )

        st.markdown("---")
        st.subheader("3. How to Read Each Chart on the Main Dashboard")
        st.markdown(
            "1. **🚦 The Top Alert Banner (Red, Orange, Green, or Blue):** Gives you a 5-second diagnosis and highlights the **top 3 peak fire months** in your chosen area.\n"
            "2. **🗓️ The 26-Year Burning Calendar:** Each row is a year and each column is a month. **Dark blue** cells mean calm months; **bright yellow** cells mark severe emergencies (such as Jan 2017 or Feb 2023). The `Cividis` palette is fully accessible for **colorblind users**.\n"
            "3. **📈 The Seasonal Profile Curve:** The yellow line shows your selected year against the blue shaded normal range. Whenever the yellow line spikes above the blue band, the region is experiencing an abnormal fire season.\n"
            "4. **🗺️ The Spatial Bubble Map:** Shows *where* fires concentrated. Large yellow circles mark intense fire corridors; small dark-blue dots indicate low activity."
        )

        st.markdown("---")
        st.subheader("4. Who Can Use This Tool?")
        st.markdown(
            "- **Residents, farmers & neighborhood councils:** Identify exact peak danger months to clear dry brush, maintain firebreaks, and plan community prevention.\n"
            "- **Municipalities & emergency managers:** Back resource allocation and early-warning campaigns with 26 years of unbiased local evidence.\n"
            "- **Researchers & GIS analysts:** Download clean, cross-calibrated **CSV** time series in one click for QGIS, ArcGIS, Excel, or Python."
        )