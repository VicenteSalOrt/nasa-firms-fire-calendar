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

# 3. Cargar dataset calibrado (contiene todo Chile: 16 regiones)
@st.cache_data
def load_data():
    return pd.read_csv("harmonized_chile.csv")

df = load_data()

# 4. Límites y Polígonos Exactos de las 16 Regiones de Chile (evita que Concepción entre en Ñuble)
REGIONS_BOUNDS = {
    "All Chile": (-56.0, -17.0, -76.0, -66.0),
    "Arica y Parinacota": (-19.25, -17.50, -70.50, -68.75),
    "Tarapacá": (-21.65, -18.90, -70.50, -68.25),
    "Antofagasta": (-26.10, -20.90, -70.80, -66.80),
    "Atacama": (-29.60, -25.25, -71.80, -68.25),
    "Coquimbo": (-32.30, -29.00, -71.80, -69.75),
    "Valparaíso": (-33.90, -32.02, -71.95, -70.00),
    "Región Metropolitana": (-34.28, -32.92, -71.45, -69.78),
    "O'Higgins": (-35.02, -33.85, -72.15, -70.02),
    "Maule": (-36.55, -34.70, -72.85, -70.25),
    "Ñuble": (-37.22, -36.00, -72.85, -71.00),
    "Biobío": (-38.45, -36.52, -73.75, -71.05),
    "La Araucanía": (-39.65, -37.55, -73.60, -70.80),
    "Los Ríos": (-40.70, -39.25, -73.80, -71.50),
    "Los Lagos": (-44.10, -40.25, -74.90, -71.50),
    "Aysén": (-49.30, -43.60, -75.80, -71.00),
    "Magallanes": (-56.00, -48.50, -75.80, -66.20),
}

# Polígonos precisos en la zona central para separar fronteras diagonales (Ñuble vs Biobío, RM vs Valparaíso, etc.)
REGION_POLYGONS = {
    "Valparaíso": [
        (-71.95, -32.02), (-70.00, -32.02), (-70.00, -33.15), (-70.65, -33.05),
        (-71.15, -33.25), (-71.40, -33.55), (-71.85, -33.90), (-71.95, -32.02)
    ],
    "Región Metropolitana": [
        (-71.40, -32.92), (-69.78, -32.92), (-69.78, -34.28), (-71.45, -34.20),
        (-71.40, -33.55), (-71.15, -33.25), (-70.65, -33.05), (-71.40, -32.92)
    ],
    "O'Higgins": [
        (-72.15, -33.85), (-71.45, -33.85), (-71.45, -34.20), (-70.02, -34.15),
        (-70.25, -35.02), (-72.15, -34.95), (-72.15, -33.85)
    ],
    "Maule": [
        (-72.85, -34.70), (-70.25, -34.70), (-70.35, -36.55), (-71.00, -36.00),
        (-72.85, -36.00), (-72.85, -34.70)
    ],
    "Ñuble": [
        (-72.85, -36.00), (-71.00, -36.00), (-71.15, -37.22), (-72.25, -37.22),
        (-72.32, -36.88), (-72.58, -36.82), (-72.62, -36.68), (-72.83, -36.52),
        (-72.85, -36.00)
    ],
    "Biobío": [
        (-73.75, -36.52), (-72.83, -36.52), (-72.62, -36.68), (-72.58, -36.82),
        (-72.32, -36.88), (-72.25, -37.22), (-71.15, -37.22), (-71.05, -38.45),
        (-73.75, -38.45), (-73.75, -36.52)
    ],
}

def filter_by_polygon(df_in, poly):
    lons = df_in['lon_bin'].to_numpy()
    lats = df_in['lat_bin'].to_numpy()
    inside = np.zeros(len(df_in), dtype=bool)
    n = len(poly)
    p1x, p1y = poly[0]
    for i in range(1, n + 1):
        p2x, p2y = poly[i % n]
        cond1 = (lats > min(p1y, p2y)) & (lats <= max(p1y, p2y)) & (lons <= max(p1x, p2x))
        if np.any(cond1):
            if p1y != p2y:
                xinters = (lats[cond1] - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                toggle = (p1x == p2x) | (lons[cond1] <= xinters)
            else:
                toggle = np.ones(np.sum(cond1), dtype=bool)
            idx = np.where(cond1)[0][toggle]
            inside[idx] = ~inside[idx]
        p1x, p1y = p2x, p2y
    return df_in[inside]

preset_keys = list(REGIONS_BOUNDS.keys()) + ["Custom Coordinates"]
preset_labels = {
    "All Chile": "🇨🇱 Todo Chile (País Completo)" if is_es else "🇨🇱 All Chile (Full Country)",
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
    "Custom Coordinates": "🧭 Coordenadas Personalizadas" if is_es else "🧭 Custom Coordinates",
}

st.sidebar.header("📍 Territorio / Región" if is_es else "📍 Territory / Region")
preset = st.sidebar.selectbox(
    "Selecciona País o Región:" if is_es else "Select Country or Region:",
    preset_keys,
    index=preset_keys.index("Biobío"),
    format_func=lambda k: preset_labels[k]
)

if preset in REGIONS_BOUNDS:
    lat_min, lat_max, lon_min, lon_max = REGIONS_BOUNDS[preset]
else:
    lat_min = st.sidebar.number_input("Latitud Mínima" if is_es else "Min Latitude", value=-38.5, format="%.2f")
    lat_max = st.sidebar.number_input("Latitud Máxima" if is_es else "Max Latitude", value=-36.0, format="%.2f")
    lon_min = st.sidebar.number_input("Longitud Mínima" if is_es else "Min Longitude", value=-73.8, format="%.2f")
    lon_max = st.sidebar.number_input("Longitud Máxima" if is_es else "Max Longitude", value=-71.0, format="%.2f")

# 5. Encabezado Principal + Selector de Público Objetivo
st.title(
    "🔥 Calendario Satelital de Incendios en Chile (2000–2026)"
    if is_es else
    "🔥 Harmonized Wildfire Activity Calendar (2000–2026)"
)

st.markdown(
    "**👤 Elige tu perfil para adaptar las explicaciones y herramientas de esta página:**"
    if is_es else
    "**👤 Select your profile to tailor explanations and tools to your needs:**"
)

audience = st.radio(
    "Audience Profile",
    ["citizen", "municipal", "scientist"],
    format_func=lambda k: {
        "citizen": "🏡 Ciudadanía y Comunidades (Lenguaje Simple)" if is_es else "🏡 Citizens & Communities (Plain Language)",
        "municipal": "🏛️ Municipios y Gestión de Emergencias" if is_es else "🏛️ Municipalities & Emergency Managers",
        "scientist": "🔬 Investigadores y Analistas de Datos" if is_es else "🔬 Researchers & Data Analysts",
    }[k],
    horizontal=True,
    label_visibility="collapsed"
)

if audience == "citizen":
    value_col = "harmonized_hotspots"
    unit_label = "Focos de calor" if is_es else "Fire hotspots"
else:
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Métrica de Análisis" if is_es else "⚙️ Analysis Metric")
    metric_key = st.sidebar.radio(
        "Variable a visualizar:" if is_es else "Variable to visualize:",
        ["hotspots", "frp"],
        format_func=lambda k: (
            ("Focos Calibrados (Conteo)" if is_es else "Calibrated Hotspots (Count)")
            if k == "hotspots" else
            ("Potencia Radiativa del Fuego (FRP - MW)" if is_es else "Fire Radiative Power (FRP - MW)")
        )
    )
    value_col = "harmonized_hotspots" if metric_key == "hotspots" else "harmonized_frp"
    unit_label = ("Focos" if is_es else "Hotspots") if metric_key == "hotspots" else "MW"

st.markdown("---")

# 6. Banner Introductorio Específico por Público
if audience == "citizen":
    if is_es:
        st.info(
            "👋 **Bienvenido/a a la Vista Ciudadana:** Aquí no necesitas saber de ciencia ni satélites. "
            "Esta página usa datos de la NASA para mostrarte **en qué meses hay mayor peligro de incendios en tu región**, "
            "si este año está más tranquilo o más crítico que lo normal, y qué zonas han sido más afectadas."
        )
    else:
        st.info(
            "👋 **Welcome to the Citizen View:** No scientific background needed. "
            "This page translates NASA satellite observations to show **which months carry the highest wildfire danger in your region**, "
            "whether a year is calmer or worse than usual, and where fires have concentrated."
        )
elif audience == "municipal":
    if is_es:
        st.info(
            "🏛️ **Vista de Gestión Territorial y Emergencias:** Diseñada para municipios, encargados comunales de emergencia y equipos preventivos. "
            "Permite identificar la ventana crítica anual para **planificar cortafuegos, limpieza de maleza y despliegue preventivo de brigadas**, "
            "comparando cada temporada contra el rango histórico normal de 26 años."
        )
    else:
        st.info(
            "🏛️ **Municipal & Emergency Management View:** Built for local governments, civil protection, and prevention teams. "
            "Identifies peak seasonal windows to **schedule firebreaks, brush clearance, and brigade pre-positioning**, "
            "benchmarking each season against the 26-year normal operating corridor."
        )
else:
    if is_es:
        st.info(
            "🔬 **Vista Científica y Analítica:** Serie temporal armonizada de **detecciones NASA FIRMS (2000–2026)**. "
            "Combina registros MODIS (1 km, calibrados mediante Gradient Boosting con geometría `scan × track` y corrección de Duan; "
            "`R² fuera de muestra = 0.887`, sesgo en hindcast temporal ciego `+4.88%`) con observaciones VIIRS (375 m) desduplicadas orbitalmente."
        )
    else:
        st.info(
            "🔬 **Scientific & Analytical View:** Cross-calibrated time series of **NASA FIRMS detections (2000–2026)**. "
            "Aligns pre-2012 MODIS (1 km, calibrated via Gradient Boosting with `scan × track` optical geometry and Duan's smearing; "
            "`Out-of-sample R² = 0.887`, blind temporal hindcast bias `+4.88%`) with orbitally de-duplicated VIIRS (375 m) observations."
        )

# 7. Filtrado Espacial (Caja + Polígono Regional Exacto)
df_filtered = df[
    (df['lat_bin'].between(lat_min, lat_max)) &
    (df['lon_bin'].between(lon_min, lon_max))
]
if preset in REGION_POLYGONS:
    df_filtered = filter_by_polygon(df_filtered, REGION_POLYGONS[preset])

if df_filtered.empty:
    st.warning(
        "⚠️ No se detectaron focos de calor en la zona seleccionada durante los 26 años analizados."
        if is_es else
        "⚠️ No fire hotspots detected in the selected area across the 26-year record."
    )
    st.stop()

month_names = (
    ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    if is_es else
    ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
)

years_available = sorted(df_filtered['year'].unique())
default_year = 2023 if 2023 in years_available else years_available[-1]

all_years = range(int(min(years_available)), int(max(years_available)) + 1)
full_grid = pd.MultiIndex.from_product([all_years, range(1, 13)], names=['year', 'month']).to_frame().reset_index(drop=True)
monthly_raw = df_filtered.groupby(['year', 'month'])[value_col].sum().reset_index()
monthly_totals = pd.merge(full_grid, monthly_raw, on=['year', 'month'], how='left').fillna(0)
monthly_totals.loc[(monthly_totals['year'] == 2026) & (monthly_totals['month'] > 11), value_col] = np.nan

# Ventana crítica histórica (Top 3 meses en 2000–2025)
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

# Controles de Año y Mes
col_ctrl1, col_ctrl2 = st.columns([3, 1])
with col_ctrl1:
    selected_year = st.slider(
        "📅 Elige el año que quieres revisar:" if (is_es and audience == "citizen") else ("📅 Selecciona Año a Evaluar:" if is_es else "📅 Select Year to Inspect:"),
        int(min(years_available)),
        int(max(years_available)),
        int(default_year)
    )
with col_ctrl2:
    month_idx_choice = st.selectbox(
        "🗓️ Filtrar por mes:" if is_es else "🗓️ Filter by month:",
        options=list(range(0, 13)),
        format_func=lambda m: ("Todo el Año" if is_es else "Full Year") if m == 0 else month_names[m - 1]
    )

if month_idx_choice == 0:
    total_selected = annual_totals.loc[selected_year]
    median_baseline = annual_median_baseline
    period_title = (
        f"{selected_year} ({'hasta Nov' if is_es else 'YTD Nov'})"
        if selected_year == 2026 else
        f"{selected_year}"
    )
    median_label = (
        ("Lo normal en un año" if is_es else "Typical Year (Normal)")
        if audience == "citizen" else
        ("Mediana Anual (2000–2025)" if is_es else "2000–2025 Annual Median")
    )
    df_map_source = df_filtered[df_filtered['year'] == selected_year]
else:
    month_series = monthly_totals[monthly_totals['month'] == month_idx_choice].set_index('year')[value_col].dropna()
    total_selected = month_series.loc[selected_year] if selected_year in month_series.index else 0.0
    median_baseline = month_series.median()
    period_title = f"{month_names[month_idx_choice - 1]} {selected_year}"
    median_label = (
        (f"Lo normal en {month_names[month_idx_choice - 1]}" if is_es else f"Typical {month_names[month_idx_choice - 1]}")
        if audience == "citizen" else
        (f"Mediana Histórica ({month_names[month_idx_choice - 1]})" if is_es else f"Historical Median ({month_names[month_idx_choice - 1]})")
    )
    df_map_source = df_filtered[(df_filtered['year'] == selected_year) & (df_filtered['month'] == month_idx_choice)]

region_display = preset_labels[preset]

# 8. Semáforo de Alerta Adaptado al Público
if median_baseline > 0:
    ratio = total_selected / median_baseline
    pct_diff = (ratio - 1.0) * 100
    anomaly_str = f"{ratio:.1f}x {'lo normal' if is_es else 'normal'}" if audience == "citizen" else f"{pct_diff:+.1f}%"

    if ratio >= 2.0:
        if audience == "citizen":
            st.error(
                f"🔴 **PELIGRO EXTREMO en {region_display} ({period_title}):** "
                f"Hubo **{ratio:.1f} veces más fuego** que en un año normal.\n\n"
                f"🛡️ **Consejo preventivo:** En esta zona, los meses más peligrosos son **{top3_names}** (concentran el **{top3_share:.0f}%** de los incendios). "
                f"Es clave limpiar pasto seco y evitar cualquier uso de fuego antes de esa fecha."
                if is_es else
                f"🔴 **EXTREME FIRE DANGER in {region_display} ({period_title}):** "
                f"Fire activity was **{ratio:.1f}x higher** than a typical year.\n\n"
                f"🛡️ **Prevention tip:** Peak fire months here are **{top3_names}** (**{top3_share:.0f}%** of annual fires). "
                f"Clear dry brush and avoid outdoor burning ahead of these months."
            )
        elif audience == "municipal":
            st.error(
                f"🔴 **EMERGENCIA / ANOMALÍA EXTREMA en {region_display} ({period_title}):** "
                f"Actividad **{pct_diff:+.1f}%** sobre la mediana histórica (**{ratio:.1f}x** lo habitual).\n\n"
                f"📋 **Priorización Operativa:** El **{top3_share:.0f}%** de la carga anual de fuego ocurre en **{top3_names}**. "
                f"Se recomienda activar alerta temprana comunal y reforzar cortafuegos en los cuadrantes amarillos del mapa inferior."
                if is_es else
                f"🔴 **EMERGENCY / EXTREME ANOMALY in {region_display} ({period_title}):** "
                f"Activity is **{pct_diff:+.1f}%** above historical median (**{ratio:.1f}x** baseline).\n\n"
                f"📋 **Operational Priority:** **{top3_share:.0f}%** of annual fire load concentrates in **{top3_names}**. "
                f"Prioritize preventive fuel management and brigade readiness in the highlighted map cells below."
            )
        else:
            st.error(
                f"🔴 **ANOMALÍA TÉRMICA EXTREMA en {region_display} ({period_title}):** "
                f"`{pct_diff:+.1f}%` respecto a la mediana 2000–2025 (`{ratio:.2f}x` línea base). "
                f"Ventana estacional dominante: **{top3_names}** (`{top3_share:.1f}%` de la mediana acumulada)."
                if is_es else
                f"🔴 **EXTREME THERMAL ANOMALY in {region_display} ({period_title}):** "
                f"`{pct_diff:+.1f}%` vs. 2000–2025 median (`{ratio:.2f}x` baseline). "
                f"Dominant seasonal window: **{top3_names}** (`{top3_share:.1f}%` of cumulative median)."
            )
    elif ratio >= 1.25:
        st.warning(
            f"🟠 **ACTIVIDAD SOBRE LO NORMAL en {region_display} ({period_title}):** "
            f"**{pct_diff:+.1f}%** ({ratio:.1f}x lo habitual). Ventana crítica local: **{top3_names}** (**{top3_share:.0f}%**)."
            if is_es else
            f"🟠 **ABOVE-NORMAL ACTIVITY in {region_display} ({period_title}):** "
            f"**{pct_diff:+.1f}%** ({ratio:.1f}x normal). Local critical window: **{top3_names}** (**{top3_share:.0f}%**)."
        )
    elif ratio >= 0.75:
        st.success(
            f"🟢 **NIVEL NORMAL en {region_display} ({period_title}):** "
            f"Actividad dentro del rango histórico esperado ({pct_diff:+.1f}%). Meses de mayor cuidado en la zona: **{top3_names}**."
            if is_es else
            f"🟢 **NORMAL LEVEL in {region_display} ({period_title}):** "
            f"Activity within expected historical range ({pct_diff:+.1f}%). Local peak danger months: **{top3_names}**."
        )
    else:
        st.info(
            f"🔵 **ACTIVIDAD BAJO LO NORMAL en {region_display} ({period_title}):** "
            f"**{abs(pct_diff):.1f}% menos** actividad que lo habitual. Recuerda que la temporada crítica aquí es **{top3_names}**."
            if is_es else
            f"🔵 **BELOW-NORMAL ACTIVITY in {region_display} ({period_title}):** "
            f"**{abs(pct_diff):.1f}% lower** than usual. Peak danger season here remains **{top3_names}**."
        )
else:
    if total_selected > 0:
        anomaly_str = "Inusual" if is_es else "Off-season"
        st.warning(
            f"🟠 **FUEGO FUERA DE TEMPORADA en {region_display} ({period_title}):** "
            f"Se detectaron {total_selected:,.0f} {unit_label.lower()} en un mes donde normalmente no hay incendios."
            if is_es else
            f"🟠 **OFF-SEASON FIRE DETECTED in {region_display} ({period_title}):** "
            f"{total_selected:,.0f} {unit_label.lower()} recorded in a month with zero typical activity."
        )
    else:
        anomaly_str = "Normal (0)"
        st.success(
            f"🟢 **SIN INCENDIOS DETECTADOS en {region_display} ({period_title}):** Comportamiento normal."
            if is_es else
            f"🟢 **NO FIRES DETECTED in {region_display} ({period_title}):** Normal behavior."
        )

# 9. Tarjetas KPI adaptadas
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric(
    f"{'Focos en' if (is_es and audience == 'citizen') else ('Actividad en' if is_es else 'Activity in')} {period_title}",
    f"{total_selected:,.0f} {unit_label}"
)
kpi2.metric(median_label, f"{median_baseline:,.0f} {unit_label}")
kpi3.metric(
    ("Comparación con año normal" if is_es else "Compared to normal")
    if audience == "citizen" else
    ("Anomalía vs. Mediana" if is_es else "Anomaly vs. Median"),
    anomaly_str
)

if selected_year == 2026 and month_idx_choice == 0:
    st.caption(
        "ℹ️ *Nota: 2026 incluye datos hasta noviembre (aún no termina el año).*"
        if is_es else
        "ℹ️ *Note: 2026 includes observations through November (year in progress).*"
    )

st.markdown("---")

# 10. Visualizaciones Principales según el Público
calendar_pivot = monthly_totals.pivot(index='year', columns='month', values=value_col).reindex(columns=range(1, 13))
max_monthly_all_time = max(float(monthly_totals[value_col].max()), 1.0)

if audience == "citizen":
    st.subheader("🗓️ ¿En qué meses ocurren los incendios? (Calendario 2000–2026)" if is_es else "🗓️ When Do Wildfires Happen? (2000–2026 Calendar)")
    st.caption(
        "Cada fila es un año y cada columna es un mes. **Azul oscuro** = mes tranquilo | **Amarillo brillante** = emergencia grave (colores aptos para daltonismo)."
        if is_es else
        "Each row is a year and each column is a month. **Dark blue** = calm month | **Bright yellow** = severe emergency (colorblind-safe palette)."
    )
    fig_cal = px.imshow(
        calendar_pivot,
        labels=dict(x="Mes" if is_es else "Month", y="Año" if is_es else "Year", color=unit_label),
        x=month_names,
        y=calendar_pivot.index.astype(str),
        color_continuous_scale="Cividis",
        aspect="auto"
    )
    fig_cal.update_layout(height=460, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_cal, width='stretch')

    st.markdown("---")
    st.subheader(f"🗺️ ¿Qué zonas fueron afectadas por el fuego? — {period_title}" if is_es else f"🗺️ Which Areas Were Affected by Fire? — {period_title}")
    st.caption(
        "Los **cuadrantes amarillos** muestran toda la extensión territorial donde se concentraron los incendios."
        if is_es else
        "**Bright yellow zones** show the full geographic footprint where wildfires concentrated."
    )

else:
    col_cal, col_curve = st.columns([1.4, 1])

    with col_cal:
        st.subheader("🗓️ Calendario de Actividad (26 Años)" if is_es else "🗓️ 26-Year Burning Activity Calendar")
        fig_cal = px.imshow(
            calendar_pivot,
            labels=dict(x="Mes" if is_es else "Month", y="Año" if is_es else "Year", color=unit_label),
            x=month_names,
            y=calendar_pivot.index.astype(str),
            color_continuous_scale="Cividis",
            aspect="auto"
        )
        fig_cal.update_layout(height=460, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_cal, width='stretch')

    with col_curve:
        st.subheader(
            f"{'📈 Curva Estacional' if is_es else '📈 Seasonal Profile'} ({selected_year} {'vs. Normal' if is_es else 'vs. Baseline'})"
        )
        stats_monthly = monthly_totals.groupby('month')[value_col].agg(
            median='median',
            p25=lambda x: x.quantile(0.25),
            p75=lambda x: x.quantile(0.75)
        ).reset_index()
        year_curve = monthly_totals[monthly_totals['year'] == selected_year].sort_values('month')

        fig_curve = go.Figure()
        fig_curve.add_trace(go.Scatter(
            x=month_names + month_names[::-1],
            y=list(stats_monthly['p75']) + list(stats_monthly['p25'])[::-1],
            fill='toself',
            fillcolor='rgba(100, 149, 237, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name="Rango Normal (25%–75%)" if is_es else "Normal Range (25th–75th pct)"
        ))
        fig_curve.add_trace(go.Scatter(
            x=month_names,
            y=stats_monthly['median'],
            mode='lines',
            line=dict(color='#6495ED', dash='dash', width=2),
            name="Mediana 26 Años" if is_es else "26-Year Median"
        ))
        fig_curve.add_trace(go.Scatter(
            x=month_names,
            y=year_curve[value_col],
            mode='lines+markers',
            line=dict(color='#FDE725', width=3),
            marker=dict(size=7),
            name=f"{'Año' if is_es else 'Year'} {selected_year}"
        ))
        fig_curve.update_layout(
            height=460,
            margin=dict(l=10, r=10, t=20, b=10),
            yaxis=dict(title=unit_label, range=[0, max_monthly_all_time * 1.05]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_curve, width='stretch')

    if audience == "scientist":
        st.markdown("---")
        st.subheader(
            "📉 Continuidad Instrumental 2000–2026 (MODIS Calibrado vs. VIIRS Directo)"
            if is_es else
            "📉 2000–2026 Instrumental Continuity (MODIS Calibrated vs. VIIRS Direct)"
        )
        annual_df = annual_totals.reset_index()
        modis_lbl = "MODIS (Calibrado)" if is_es else "MODIS (Calibrated)"
        viirs_lbl = "VIIRS (Directo)" if is_es else "VIIRS (Direct)"
        annual_df['Sensor'] = np.where(annual_df['year'] < 2012, modis_lbl, viirs_lbl)

        fig_trend = px.bar(
            annual_df,
            x='year',
            y=value_col,
            color='Sensor',
            color_discrete_map={modis_lbl: '#3B528B', viirs_lbl: '#FDE725'},
            labels={'year': "Año" if is_es else "Year", value_col: unit_label}
        )
        fig_trend.add_hline(
            y=annual_median_baseline,
            line_dash="dash",
            line_color="white",
            annotation_text="Mediana 2000–2025" if is_es else "2000–2025 Median",
            annotation_position="top left"
        )
        fig_trend.add_vline(
            x=2011.5,
            line_dash="dot",
            line_color="#FF6B6B",
            annotation_text="Transición VIIRS 2012" if is_es else "2012 VIIRS Transition",
            annotation_position="top right"
        )
        fig_trend.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=30, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_trend, width='stretch')

    st.markdown("---")
    st.subheader(f"🗺️ Mapa Espacial de Intensidad — {period_title}" if is_es else f"🗺️ Spatial Fire Intensity Map — {period_title}")

# 11. Mapa Espacial de Extensión Real (Normalizado por Región / País)
col_map, col_side = st.columns([2.2, 1])

with col_map:
    if df_map_source.empty:
        st.info(
            "No se registraron focos de calor en este período para la zona elegida."
            if is_es else
            "No fire hotspots recorded in this period for the selected area."
        )
    else:
        map_agg = df_map_source.groupby(['lat_bin', 'lon_bin']).agg(
            harmonized_hotspots=('harmonized_hotspots', 'sum'),
            harmonized_frp=('harmonized_frp', 'sum')
        ).reset_index()
        map_agg["cell_id"] = map_agg.index.astype(str)

        # Auto-detectar resolución de malla (ej. 0.025° ~2.7 km o 0.25° ~27 km)
        unique_lats = np.sort(df['lat_bin'].unique())
        diffs = np.diff(unique_lats)
        diffs = diffs[diffs > 1e-5]
        grid_res = float(np.min(diffs)) if len(diffs) > 0 else 0.25
        half = grid_res / 2.0

        features = []
        for _, row in map_agg.iterrows():
            lat_c, lon_c = float(row["lat_bin"]), float(row["lon_bin"])
            poly = [[
                [lon_c - half, lat_c - half],
                [lon_c + half, lat_c - half],
                [lon_c + half, lat_c + half],
                [lon_c - half, lat_c + half],
                [lon_c - half, lat_c - half],
            ]]
            features.append({
                "type": "Feature",
                "id": row["cell_id"],
                "geometry": {"type": "Polygon", "coordinates": poly},
                "properties": {"cell_id": row["cell_id"]}
            })
        geojson_grid = {"type": "FeatureCollection", "features": features}

        # Escala de color normalizada al máximo histórico de 26 años del territorio seleccionado
        # (Cada región se compara contra su propio máximo 2000-2026; Todo Chile contra el máximo nacional)
        if month_idx_choice == 0:
            hist_cell_max = float(df_filtered.groupby(['year', 'lat_bin', 'lon_bin'])[value_col].sum().max())
        else:
            hist_cell_max = float(df_filtered[value_col].max())
        hist_cell_max = max(hist_cell_max, 1.0)

        # Centrado exacto en los datos de la región seleccionada
        if preset != "All Chile" and preset != "Custom Coordinates":
            center_lat = float((df_filtered['lat_bin'].min() + df_filtered['lat_bin'].max()) / 2.0)
            center_lon = float((df_filtered['lon_bin'].min() + df_filtered['lon_bin'].max()) / 2.0)
            span = max(
                float(df_filtered['lat_bin'].max() - df_filtered['lat_bin'].min()) + grid_res,
                float(df_filtered['lon_bin'].max() - df_filtered['lon_bin'].min()) + grid_res
            )
        else:
            center_lat = (lat_min + lat_max) / 2.0
            center_lon = (lon_min + lon_max) / 2.0
            span = max(abs(lat_max - lat_min), abs(lon_max - lon_min))

        zoom_lvl = float(np.clip(8.3 - np.log2(max(span, 0.4)), 3.2, 8.2))

        choro_func = px.choropleth_map if hasattr(px, "choropleth_map") else px.choropleth_mapbox
        style_kwarg = {"map_style": "carto-darkmatter"} if hasattr(px, "choropleth_map") else {"mapbox_style": "carto-darkmatter"}

        hover_cols = {"cell_id": False, "lat_bin": ":.3f", "lon_bin": ":.3f", "harmonized_hotspots": ":,.0f"}
        if audience != "citizen":
            hover_cols["harmonized_frp"] = ":,.1f"

        fig_map = choro_func(
            map_agg,
            geojson=geojson_grid,
            locations="cell_id",
            featureidkey="id",
            color=value_col,
            color_continuous_scale="Cividis",
            range_color=[0, hist_cell_max],
            opacity=0.68,
            zoom=zoom_lvl,
            center={"lat": center_lat, "lon": center_lon},
            hover_data=hover_cols,
            labels={
                "lat_bin": "Latitud" if is_es else "Latitude",
                "lon_bin": "Longitud" if is_es else "Longitude",
                "harmonized_hotspots": "Focos de calor" if is_es else "Calibrated Hotspots",
                "harmonized_frp": "FRP (MW)"
            },
            **style_kwarg
        )
        fig_map.update_traces(marker_line_width=0.5, marker_line_color="rgba(255,255,255,0.22)")
        fig_map.update_layout(height=480, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_map, width='stretch')

with col_side:
    if audience == "citizen":
        st.subheader("📖 ¿Qué significa cada cosa?" if is_es else "📖 What Does Everything Mean?")
        if is_es:
            st.markdown(
                "- **🔥 Foco de calor:** Un punto del terreno donde el satélite de la NASA detectó temperatura anormalmente alta (incendio forestal o quema).\n"
                "- **📏 Lo normal (Mediana):** El nivel habitual de fuego en tu región durante los últimos 26 años. Sirve para saber si un año estuvo tranquilo o fuera de control.\n"
                "- **🛰️ ¿Por qué es confiable?** Unimos satélites antiguos (2000–2011) con los modernos (2012–2026) corrigiendo sus diferencias de cámara para que la comparación sea justa."
            )
            st.success(
                "💡 **¿Cómo ayudar en tu comunidad?**\n"
                f"En **{region_display}**, prepara cortafuegos y limpia pastizales secos antes de **{top3_names}**."
            )
        else:
            st.markdown(
                "- **🔥 Fire hotspot:** A patch of land where NASA satellites detected abnormally high heat (wildfire or burn).\n"
                "- **📏 Typical Year (Normal):** The usual fire level in your region over the past 26 years, used as a yardstick.\n"
                "- **🛰️ Why trust it?** We aligned older satellites (2000–2011) with modern ones (2012–2026) so historical comparisons are fair."
            )
            st.success(
                "💡 **Community action tip:**\n"
                f"In **{region_display}**, clear dry brush and maintain firebreaks ahead of **{top3_names}**."
            )
    elif audience == "municipal":
        st.subheader("📥 Reporte Territorial (GIS / Excel)" if is_es else "📥 Territorial Data (GIS / Excel)")
        st.write(
            f"Descarga la base histórica calibrada de **{region_display}** ({len(df_filtered):,} registros) para cruzarla con mapas comunales en QGIS o Excel."
            if is_es else
            f"Download the calibrated historical dataset for **{region_display}** ({len(df_filtered):,} records) for municipal mapping in QGIS or Excel."
        )
        csv_export = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Descargar Datos Regionales (CSV)" if is_es else "⬇️ Download Regional Data (CSV)",
            data=csv_export,
            file_name=f"incendios_calibrados_{preset.replace(' ', '_').lower()}.csv",
            mime="text/csv",
        )
        st.info(
            "🏛️ **Uso Municipal:** Las coordenadas (`lat_bin`, `lon_bin`) permiten identificar qué sectores rurales concentran recurrencia histórica de fuego."
            if is_es else
            "🏛️ **Municipal Use:** Grid coordinates (`lat_bin`, `lon_bin`) pinpoint which rural sectors suffer recurring fire activity."
        )
    else:
        st.subheader("📥 Exportar Dataset Calibrado" if is_es else "📥 Export Calibrated Dataset")
        st.write(
            f"Serie armonizada MODIS + VIIRS para **{region_display}** ({len(df_filtered):,} registros celda-mes)."
            if is_es else
            f"Harmonized MODIS + VIIRS time series for **{region_display}** ({len(df_filtered):,} grid-month records)."
        )
        csv_export = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Descargar CSV Armonizado" if is_es else "⬇️ Download Harmonized CSV",
            data=csv_export,
            file_name=f"harmonized_fires_{preset.replace(' ', '_').lower()}.csv",
            mime="text/csv",
        )
        st.info(
            "🔬 **Nota Técnica:** Calibración cruzada MODIS→VIIRS mediante Gradient Boosting con área óptica de píxel (`scan × track`) y factor de Duan (`R² = 0.887`; sesgo temporal ciego `+4.88%`)."
            if is_es else
            "🔬 **Technical Note:** Cross-calibrated MODIS→VIIRS via Gradient Boosting using optical pixel geometry (`scan × track`) and Duan's smearing (`R² = 0.887`; blind temporal hindcast bias `+4.88%`)."
        )