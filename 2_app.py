import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import urllib.request
import json
from urllib.parse import quote

# 1. Configuración general de la página
st.set_page_config(page_title="FIRMS Fire Calendar", layout="wide")

# 2. Cargar dataset calibrado (contiene todo Chile: 16 regiones)
@st.cache_data
def load_data():
    df_loaded = pd.read_csv("harmonized_chile.csv")
    if "lat_exact" not in df_loaded.columns:
        df_loaded["lat_exact"] = df_loaded["lat_bin"]
    if "lon_exact" not in df_loaded.columns:
        df_loaded["lon_exact"] = df_loaded["lon_bin"]
    return df_loaded

df = load_data()

# 3. Geocodificación Inversa Exacta (Comuna, Sector, Parque o Camino) vía OpenStreetMap
@st.cache_data(show_spinner=False)
def reverse_geocode_exact(lat_round, lon_round, is_es_flag=True):
    url = (
        f"https://nominatim.openstreetmap.org/reverse?format=jsonv2"
        f"&lat={lat_round}&lon={lon_round}&zoom=13&addressdetails=1"
    )
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "ChileWildfireCalendar-NASA-App/1.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            addr = data.get("address", {})
            sector = (
                addr.get("hamlet")
                or addr.get("village")
                or addr.get("suburb")
                or addr.get("neighbourhood")
                or addr.get("locality")
                or addr.get("nature_reserve")
                or addr.get("park")
                or addr.get("road")
                or ""
            )
            comuna = (
                addr.get("town")
                or addr.get("city")
                or addr.get("municipality")
                or addr.get("county")
                or ""
            )
            region = addr.get("state", "")
            parts = []
            if sector and sector.lower() != comuna.lower():
                parts.append(f"Sector {sector}" if is_es_flag else f"{sector} area")
            if comuna:
                parts.append(f"Comuna de {comuna}" if is_es_flag else f"{comuna} Commune")
            if not parts and region:
                parts.append(region)
            if parts:
                return ", ".join(parts), comuna
    except Exception:
        pass
    return None, ""

# 4. Límites y Polígonos Exactos de las 16 Regiones de Chile
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
    lons = df_in['lon_exact'].to_numpy()
    lats = df_in['lat_exact'].to_numpy()
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

def make_circle_coords(lat_c, lon_c, radius_km, num_pts=48):
    angles = np.linspace(0, 2 * np.pi, num_pts)
    dlat = (radius_km / 111.0) * np.cos(angles)
    dlon = (radius_km / (111.0 * max(np.cos(np.radians(lat_c)), 0.1))) * np.sin(angles)
    return list(lat_c + dlat), list(lon_c + dlon)

# 5. Cabecera Accesible (Idioma + Daltonismo + Baja Visión / Texto Grande)
head_title, head_lang, head_color, head_vision = st.columns([2.1, 0.9, 1.3, 1.1])

with head_lang:
    lang = st.radio("Idioma / Language", ["English", "Español"], horizontal=True)
is_es = (lang == "Español")

with head_color:
    palette_mode = st.radio(
        "Escala de color" if is_es else "Color scale",
        ["standard", "colorblind"],
        format_func=lambda k: (
            ("Estándar" if is_es else "Standard")
            if k == "standard" else
            ("Daltonismo" if is_es else "Colorblind-safe")
        ),
        horizontal=True
    )

with head_vision:
    large_text_mode = st.radio(
        "Lectura / Visión" if is_es else "Text size",
        ["normal", "large"],
        format_func=lambda k: (
            ("Normal" if is_es else "Normal")
            if k == "normal" else
            ("Texto Grande" if is_es else "Large Text")
        ),
        horizontal=True
    )

is_large = (large_text_mode == "large")
chart_font_size = 16 if is_large else 12

if is_large:
    st.markdown(
        """
        <style>
        html, body, [class*="css"] {
            font-size: 19px !important;
        }
        p, li, label, .stMarkdown, .stRadio label, .stSelectbox label {
            font-size: 1.12rem !important;
            line-height: 1.55 !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 2.2rem !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 1.1rem !important;
        }
        .stButton button {
            font-size: 1.08rem !important;
            padding: 0.6rem 1rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

color_scale = "YlOrRd" if palette_mode == "standard" else "Cividis"
accent_line_color = "#D7301F" if palette_mode == "standard" else "#FDE725"

if palette_mode == "standard":
    color_guide_text = (
        "Amarillo claro = calma o pocos focos  |  Naranja = actividad moderada  |  Rojo oscuro = concentración crítica."
        if is_es else
        "Light yellow = calm / low activity  |  Orange = moderate  |  Dark red = critical concentration."
    )
else:
    color_guide_text = (
        "Azul oscuro = calma o pocos focos  |  Gris = actividad moderada  |  Amarillo brillante = concentración crítica (paleta Cividis)."
        if is_es else
        "Dark blue = calm / low activity  |  Grey = moderate  |  Bright yellow = critical concentration (Cividis palette)."
    )

with head_title:
    st.title(
        "Calendario Satelital de Incendios en Chile"
        if is_es else
        "Harmonized Wildfire Activity Calendar"
    )

if is_es:
    st.info(
        "**¿Qué hace esta aplicación?** Unifica 26 años de observaciones satelitales de la NASA (2000–2026) corrigiendo las diferencias entre satélites antiguos y modernos para mostrar un historial confiable de focos de calor y **potencia térmica (FRP)** en todo Chile.\n\n"
        "**¿En qué ayuda?** Permite a vecinos, municipios e investigadores identificar **qué meses del año son más peligrosos**, **qué porcentaje de incendios ocurre en cada temporada** y **qué comunas o sectores concentran mayor recurrencia de fuego**."
    )
else:
    st.info(
        "**What does this app do?** It unifies 26 years of NASA satellite fire observations (2000–2026), calibrating older and newer sensors into a single consistent record across Chile.\n\n"
        "**How does it help?** It helps residents, municipalities, and researchers identify **which months carry the highest fire risk**, **what percentage of annual fires falls in each season**, and **which communes experience recurring fires**."
    )

# 6. Tutorial / Guía Visual Grande y Destacada al Inicio
st.markdown(
    f"### {'¿Cómo usar esta página en 5 pasos?' if is_es else 'How to use this page in 5 simple steps'}"
)
tut_cols = st.columns(5)
tutorial_steps = (
    [
        ("1. Elige tu Región", "Selecciona todo Chile, una región específica o ingresa coordenadas exactas."),
        ("2. Nivel de Detalle", "Elige *Ciudadanía* (simple y con audio), *Municipios* (QGIS) o *Investigadores*."),
        ("3. Año y Rango de Meses", "Usa el desplegable o flechas de año y elige un trimestre, semestre o rango de meses."),
        ("4. Revisa el Calendario", "Mira qué meses y años tuvieron mayor actividad y compara con lo normal."),
        ("5. Mapa Satelital y Ayuda", "Explora el mapa en vista satélite o calles, revisa los sectores críticos y contacta a CONAF.")
    ]
    if is_es else
    [
        ("1. Choose Region", "Pick All Chile, a specific region, or enter custom coordinates."),
        ("2. Detail Level", "Select *Citizens* (plain language + audio), *Municipalities*, or *Researchers*."),
        ("3. Year & Month Range", "Use the year selector or arrows and pick a quarter, semester, or custom months."),
        ("4. Read Calendar", "Spot which months and years peaked and compare against historical baselines."),
        ("5. Satellite Map & Help", "Explore satellite/street layers, inspect affected sectors, and send preventive alerts.")
    ]
)
for col_t, (t_head, t_body) in zip(tut_cols, tutorial_steps):
    with col_t:
        st.markdown(
            f"""
            <div style="border: 1px solid rgba(150,150,150,0.35); border-radius: 10px; padding: 14px; height: 100%; background-color: rgba(120,140,180,0.08);">
                <div style="font-size: {'1.22rem' if is_large else '1.08rem'}; font-weight: 700; margin-bottom: 6px;">{t_head}</div>
                <div style="font-size: {'1.08rem' if is_large else '0.95rem'}; line-height: 1.4;">{t_body}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("---")

# 7. Paso 1 y Paso 2: Territorio y Nivel de Detalle
preset_keys = list(REGIONS_BOUNDS.keys()) + ["Custom Coordinates"]
preset_labels = {
    "All Chile": "Todo Chile (País Completo)" if is_es else "All Chile (Full Country)",
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
    "Custom Coordinates": "Coordenadas Personalizadas" if is_es else "Custom Coordinates",
}

step1_col, step2_col = st.columns([1.3, 1.7])

with step1_col:
    preset = st.selectbox(
        "Paso 1 · Selecciona territorio o región:" if is_es else "Step 1 · Select territory or region:",
        preset_keys,
        index=preset_keys.index("Biobío"),
        format_func=lambda k: preset_labels[k]
    )

with step2_col:
    audience = st.radio(
        "Paso 2 · Elige el nivel de detalle:" if is_es else "Step 2 · Choose level of detail:",
        ["citizen", "municipal", "scientist"],
        format_func=lambda k: {
            "citizen": "Ciudadanía (Simple)" if is_es else "Citizens (Plain Language)",
            "municipal": "Municipios y Emergencias" if is_es else "Municipalities & Emergency",
            "scientist": "Investigadores y Datos" if is_es else "Researchers & Data",
        }[k],
        horizontal=True
    )

if preset in REGIONS_BOUNDS:
    lat_min, lat_max, lon_min, lon_max = REGIONS_BOUNDS[preset]
else:
    c_lat1, c_lat2, c_lon1, c_lon2 = st.columns(4)
    lat_min = c_lat1.number_input("Latitud Mínima" if is_es else "Min Latitude", value=-38.5, format="%.2f")
    lat_max = c_lat2.number_input("Latitud Máxima" if is_es else "Max Latitude", value=-36.0, format="%.2f")
    lon_min = c_lon1.number_input("Longitud Mínima" if is_es else "Min Longitude", value=-73.8, format="%.2f")
    lon_max = c_lon2.number_input("Longitud Máxima" if is_es else "Max Longitude", value=-71.0, format="%.2f")

opt_col1, opt_col2 = st.columns([1.6, 1.4])
with opt_col1:
    metric_key = st.radio(
        "Métrica principal:" if is_es else "Primary metric:",
        ["hotspots", "frp"],
        format_func=lambda k: (
            ("Cantidad de Focos Calibrados" if is_es else "Calibrated Hotspot Count")
            if k == "hotspots" else
            ("Intensidad / Potencia Térmica (FRP - MW)" if is_es else "Fire Intensity / Radiative Power (FRP - MW)")
        ),
        horizontal=True
    )
    value_col = "harmonized_hotspots" if metric_key == "hotspots" else "harmonized_frp"
    unit_label = ("Focos" if is_es else "Hotspots") if metric_key == "hotspots" else "MW"

with opt_col2:
    exclude_industrial = st.checkbox(
        "Ocultar fuentes industriales fijas del norte (fundiciones y plantas solares)"
        if is_es else
        "Hide persistent northern industrial heat sources (smelters & solar plants)",
        value=(audience != "scientist")
    )

# 8. Filtrado Espacial (Caja + Polígono Regional Exacto + Filtro Industrial Opcional)
df_filtered = df[
    (df['lat_exact'].between(lat_min, lat_max)) &
    (df['lon_exact'].between(lon_min, lon_max))
]
if preset in REGION_POLYGONS:
    df_filtered = filter_by_polygon(df_filtered, REGION_POLYGONS[preset])

if exclude_industrial and not df_filtered.empty:
    north_mask = df_filtered['lat_exact'] > -29.0
    if north_mask.any():
        df_north = df_filtered[north_mask]
        active_months_per_cell = df_north.groupby(['lat_bin', 'lon_bin', 'year'])['month'].nunique().groupby(['lat_bin', 'lon_bin']).mean()
        persistent_cells = active_months_per_cell[active_months_per_cell >= 8.5].index
        if len(persistent_cells) > 0:
            cell_tuples = list(zip(df_filtered['lat_bin'], df_filtered['lon_bin']))
            keep_mask = ~pd.Series(cell_tuples, index=df_filtered.index).isin(persistent_cells)
            df_filtered = df_filtered[keep_mask]

if df_filtered.empty:
    st.warning(
        "No se registraron focos de calor en la zona seleccionada durante los 26 años analizados."
        if is_es else
        "No fire hotspots detected in the selected area across the 26-year record."
    )
    st.stop()

month_names = (
    ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    if is_es else
    ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
)
month_full_names = (
    ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    if is_es else
    ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
)

years_available = sorted([int(y) for y in df_filtered['year'].unique()])
years_desc = list(reversed(years_available))

all_years = range(int(min(years_available)), int(max(years_available)) + 1)
full_grid = pd.MultiIndex.from_product([all_years, range(1, 13)], names=['year', 'month']).to_frame().reset_index(drop=True)
monthly_raw = df_filtered.groupby(['year', 'month'])[value_col].sum().reset_index()
monthly_totals = pd.merge(full_grid, monthly_raw, on=['year', 'month'], how='left').fillna(0)
monthly_totals.loc[(monthly_totals['year'] == 2026) & (monthly_totals['month'] > 11), value_col] = np.nan

# Ventana crítica histórica por carga total (Top 3 meses en 2000–2025)
hist_complete = monthly_totals[monthly_totals['year'] < 2026]
month_totals_hist = hist_complete.groupby('month')[value_col].sum()
top3_months = month_totals_hist.nlargest(3)
top3_indices = sorted(top3_months.index.tolist())
top3_names = " – ".join([month_names[i - 1] for i in top3_indices])
top3_share = (top3_months.sum() / month_totals_hist.sum() * 100) if month_totals_hist.sum() > 0 else 0.0

annual_totals = monthly_totals.groupby('year')[value_col].sum()
complete_years = annual_totals[annual_totals.index < 2026]
annual_median_baseline = complete_years.median() if not complete_years.empty else annual_totals.median()
worst_yr = int(annual_totals.idxmax())

# Si el usuario cambia de región, seleccionar automáticamente su peor año histórico (ej. 2024 en Valparaíso, 2023 en Biobío)
if st.session_state.get("last_preset_tracker") != preset:
    st.session_state["last_preset_tracker"] = preset
    st.session_state["selected_year_state"] = worst_yr

if "selected_year_state" not in st.session_state or st.session_state["selected_year_state"] not in years_available:
    st.session_state["selected_year_state"] = worst_yr

# Callbacks seguros para botones (evita StreamlitWidgetAlreadyInstantiatedError)
def set_year_cb(new_yr):
    st.session_state["selected_year_state"] = int(new_yr)

def step_year_cb(delta):
    cur = st.session_state.get("selected_year_state", worst_yr)
    if cur in years_available:
        idx = years_available.index(cur)
        new_idx = int(np.clip(idx + delta, 0, len(years_available) - 1))
        st.session_state["selected_year_state"] = years_available[new_idx]

# 9. Paso 3: Selección Cómoda de Año (Desplegable + Flechas) y Rango de Meses
st.subheader("Paso 3 · Selecciona Año y Rango de Meses" if is_es else "Step 3 · Select Year & Month Range")

q1, q2, q3 = st.columns(3)
q1.button(
    "Atajo: Año actual (2026)" if is_es else "Shortcut: Current year (2026)",
    on_click=set_year_cb,
    args=(int(max(years_available)),),
    width='stretch'
)
q2.button(
    f"Atajo: Peor año en esta región ({worst_yr})" if is_es else f"Shortcut: Worst year in region ({worst_yr})",
    on_click=set_year_cb,
    args=(worst_yr,),
    width='stretch'
)
calm_yr = 2016 if 2016 in years_available else int(min(years_available))
q3.button(
    f"Atajo: Año tranquilo ({calm_yr})" if is_es else f"Shortcut: Calm year ({calm_yr})",
    on_click=set_year_cb,
    args=(calm_yr,),
    width='stretch'
)

yr_col1, yr_col2, yr_col3, period_mode_col = st.columns([0.7, 1.4, 0.7, 2.2])

cur_yr_idx = years_available.index(st.session_state["selected_year_state"])
with yr_col1:
    st.write("")
    st.button(
        "◀ Anterior" if is_es else "◀ Prev",
        disabled=(cur_yr_idx == 0),
        on_click=step_year_cb,
        args=(-1,),
        width='stretch'
    )

with yr_col2:
    selected_year = st.selectbox(
        "Año a revisar:" if is_es else "Year to inspect:",
        options=years_desc,
        key="selected_year_state"
    )

with yr_col3:
    st.write("")
    st.button(
        "Siguiente ▶" if is_es else "Next ▶",
        disabled=(cur_yr_idx == len(years_available) - 1),
        on_click=step_year_cb,
        args=(1,),
        width='stretch'
    )

with period_mode_col:
    period_preset = st.selectbox(
        "Período dentro del año (Trimestre, Semestre o Rango):" if is_es else "Period within year (Quarter, Semester, or Range):",
        options=["full_year", "q1_summer", "q2_autumn", "q3_winter", "q4_spring", "s1", "s2", "single_month", "custom_range"],
        format_func=lambda k: {
            "full_year": "Todo el Año (Ene – Dic)" if is_es else "Full Year (Jan – Dec)",
            "q1_summer": "1er Trimestre · Verano Crítico (Ene – Mar)" if is_es else "Q1 · Peak Summer (Jan – Mar)",
            "q2_autumn": "2do Trimestre · Otoño (Abr – Jun)" if is_es else "Q2 · Autumn (Apr – Jun)",
            "q3_winter": "3er Trimestre · Invierno (Jul – Sep)" if is_es else "Q3 · Winter (Jul – Sep)",
            "q4_spring": "4to Trimestre · Primavera (Oct – Dic)" if is_es else "Q4 · Spring (Oct – Dec)",
            "s1": "1er Semestre (Ene – Jun)" if is_es else "1st Semester (Jan – Jun)",
            "s2": "2do Semestre (Jul – Dic)" if is_es else "2nd Semester (Jul – Dic)",
            "single_month": "Un mes específico" if is_es else "Single specific month",
            "custom_range": "Rango personalizado de meses (Desde – Hasta)" if is_es else "Custom month range (From – To)",
        }[k]
    )

if period_preset == "full_year":
    m_start, m_end = 1, 12
elif period_preset == "q1_summer":
    m_start, m_end = 1, 3
elif period_preset == "q2_autumn":
    m_start, m_end = 4, 6
elif period_preset == "q3_winter":
    m_start, m_end = 7, 9
elif period_preset == "q4_spring":
    m_start, m_end = 10, 12
elif period_preset == "s1":
    m_start, m_end = 1, 6
elif period_preset == "s2":
    m_start, m_end = 7, 12
elif period_preset == "single_month":
    m_single = st.selectbox(
        "Elige el mes:" if is_es else "Choose month:",
        options=list(range(1, 13)),
        index=1 if (preset == "Valparaíso" and selected_year == 2024) else 0,
        format_func=lambda m: month_full_names[m - 1]
    )
    m_start, m_end = m_single, m_single
else:
    rc1, rc2 = st.columns(2)
    with rc1:
        m_start = st.selectbox(
            "Desde el mes:" if is_es else "From month:",
            options=list(range(1, 13)),
            index=0,
            format_func=lambda m: month_full_names[m - 1]
        )
    with rc2:
        m_end = st.selectbox(
            "Hasta el mes:" if is_es else "To month:",
            options=list(range(1, 13)),
            index=2,
            format_func=lambda m: month_full_names[m - 1]
        )
    if m_end < m_start:
        st.warning(
            f"Ajustando rango automáticamente de {month_names[m_end - 1]} a {month_names[m_start - 1]}."
            if is_es else
            f"Automatically ordering range from {month_names[m_end - 1]} to {month_names[m_start - 1]}."
        )
        m_start, m_end = m_end, m_start

selected_months = list(range(m_start, m_end + 1))
is_full_year = (m_start == 1 and m_end == 12)

if is_full_year:
    effective_months = list(range(1, 12)) if selected_year == 2026 else list(range(1, 13))
    period_title = f"{selected_year} (Ene–Nov)" if (selected_year == 2026 and is_es) else (f"{selected_year} (Jan–Nov YTD)" if selected_year == 2026 else f"{selected_year}")
    median_label = (
        ("Lo normal Ene–Nov" if is_es else "Typical Jan–Nov") if selected_year == 2026 else ("Lo normal en un año" if is_es else "Typical Year (Normal)")
    ) if audience == "citizen" else (
        ("Mediana Ene–Nov (2000–2025)" if is_es else "2000–2025 Jan–Nov Median") if selected_year == 2026 else ("Mediana Anual (2000–2025)" if is_es else "2000–2025 Annual Median")
    )
else:
    effective_months = [m for m in selected_months if not (selected_year == 2026 and m > 11)]
    if not effective_months:
        effective_months = selected_months
    range_label = month_names[m_start - 1] if m_start == m_end else f"{month_names[m_start - 1]} – {month_names[m_end - 1]}"
    period_title = f"{range_label} {selected_year}"
    median_label = (
        (f"Lo normal en {range_label}" if is_es else f"Typical {range_label}")
        if audience == "citizen" else
        (f"Mediana Histórica ({range_label})" if is_es else f"Historical Median ({range_label})")
    )

# Calcular totales del rango elegido y porcentaje respecto al total del año
range_by_year = (
    monthly_totals[monthly_totals['month'].isin(effective_months)]
    .groupby('year')[value_col]
    .sum()
)
total_selected = float(range_by_year.loc[selected_year]) if selected_year in range_by_year.index else 0.0
complete_range_years = range_by_year[range_by_year.index < 2026]
median_baseline = float(complete_range_years.median()) if not complete_range_years.empty else float(range_by_year.median())

year_total_selected = float(annual_totals.loc[selected_year]) if selected_year in annual_totals.index else 0.0
share_of_year_pct = (total_selected / year_total_selected * 100.0) if year_total_selected > 0 else 0.0
hist_share_pct = (
    float(hist_complete[hist_complete['month'].isin(selected_months)][value_col].sum()) /
    float(hist_complete[value_col].sum()) * 100.0
) if float(hist_complete[value_col].sum()) > 0 else 0.0

df_map_source = df_filtered[
    (df_filtered['year'] == selected_year) &
    (df_filtered['month'].isin(selected_months))
]

region_display = preset_labels[preset]

# 10. Diagnóstico Comparativo + Contexto de Incendios Rápidos Urbano-Forestales
if median_baseline > 0:
    ratio = total_selected / median_baseline
    pct_diff = (ratio - 1.0) * 100
    anomaly_str = f"{ratio:.1f}x {'lo normal' if is_es else 'normal'}" if audience == "citizen" else f"{pct_diff:+.1f}%"

    if ratio >= 2.0:
        diag_plain = (
            f"Nivel crítico extremo en {region_display} durante {period_title}. "
            f"Se registraron {total_selected:,.0f} {unit_label.lower()}, es decir {ratio:.1f} veces más que lo normal. "
            f"En esta zona, el {top3_share:.0f} por ciento de los incendios ocurre entre {top3_names}."
            if is_es else
            f"Extreme critical level in {region_display} during {period_title}. "
            f"{total_selected:,.0f} {unit_label.lower()} recorded, {ratio:.1f} times higher than normal."
        )
        if audience == "citizen":
            st.error(
                f"**NIVEL CRÍTICO EXTREMO en {region_display} ({period_title}):** "
                f"Se registraron **{ratio:.1f} veces más {unit_label.lower()}** que en un período normal.\n\n"
                f"En esta región, el **{top3_share:.0f}%** de la actividad ocurre entre **{top3_names}**. "
                f"Es fundamental mantener cortafuegos limpios y evitar cualquier uso de fuego o chispas antes de esos meses."
                if is_es else
                f"**EXTREME CRITICAL LEVEL in {region_display} ({period_title}):** "
                f"Activity was **{ratio:.1f}x higher** than normal. Peak fire months here are **{top3_names}** (**{top3_share:.0f}%**)."
            )
        elif audience == "municipal":
            st.error(
                f"**ANOMALÍA EXTREMA en {region_display} ({period_title}):** "
                f"**{pct_diff:+.1f}%** sobre la mediana histórica (**{ratio:.1f}x** lo habitual). "
                f"El **{top3_share:.0f}%** de la carga anual ocurre en **{top3_names}**; priorizar cortafuegos en las comunas destacadas del mapa."
                if is_es else
                f"**EXTREME ANOMALY in {region_display} ({period_title}):** "
                f"**{pct_diff:+.1f}%** above historical median (**{ratio:.1f}x** baseline). **{top3_share:.0f}%** concentrates in **{top3_names}**."
            )
        else:
            st.error(
                f"**ANOMALÍA TÉRMICA EXTREMA en {region_display} ({period_title}):** "
                f"`{pct_diff:+.1f}%` vs. mediana 2000–2025 (`{ratio:.2f}x` línea base). Ventana dominante: **{top3_names}** (`{top3_share:.1f}%`)."
                if is_es else
                f"**EXTREME THERMAL ANOMALY in {region_display} ({period_title}):** "
                f"`{pct_diff:+.1f}%` vs. 2000–2025 median (`{ratio:.2f}x` baseline). Dominant window: **{top3_names}** (`{top3_share:.1f}%`)."
            )
    elif ratio >= 1.25:
        diag_plain = (
            f"Actividad sobre lo normal en {region_display} durante {period_title}, con {total_selected:,.0f} {unit_label.lower()}, "
            f"un {pct_diff:.0f} por ciento sobre la mediana histórica."
            if is_es else
            f"Above-normal activity in {region_display} during {period_title}, {pct_diff:.0f} percent above baseline."
        )
        st.warning(
            f"**ACTIVIDAD SOBRE LO NORMAL en {region_display} ({period_title}):** "
            f"**{pct_diff:+.1f}%** ({ratio:.1f}x lo habitual). Ventana crítica local: **{top3_names}** (**{top3_share:.0f}%**)."
            if is_es else
            f"**ABOVE-NORMAL ACTIVITY in {region_display} ({period_title}):** "
            f"**{pct_diff:+.1f}%** ({ratio:.1f}x normal). Local critical window: **{top3_names}**."
        )
    elif ratio >= 0.75:
        diag_plain = (
            f"Nivel normal en {region_display} durante {period_title}, con {total_selected:,.0f} {unit_label.lower()}."
            if is_es else
            f"Normal activity level in {region_display} during {period_title}."
        )
        st.success(
            f"**NIVEL NORMAL en {region_display} ({period_title}):** "
            f"Actividad dentro del rango habitual ({pct_diff:+.1f}%). Meses de mayor riesgo en la zona: **{top3_names}**."
            if is_es else
            f"**NORMAL LEVEL in {region_display} ({period_title}):** "
            f"Activity within expected historical range ({pct_diff:+.1f}%)."
        )
    else:
        diag_plain = (
            f"Actividad bajo lo normal en {region_display} durante {period_title}, un {abs(pct_diff):.0f} por ciento menos que lo habitual."
            if is_es else
            f"Below-normal activity in {region_display} during {period_title}."
        )
        st.info(
            f"**ACTIVIDAD BAJO LO NORMAL en {region_display} ({period_title}):** "
            f"**{abs(pct_diff):.1f}% menos** actividad que lo habitual. La temporada crítica sigue siendo **{top3_names}**."
            if is_es else
            f"**BELOW-NORMAL ACTIVITY in {region_display} ({period_title}):** "
            f"**{abs(pct_diff):.1f}% lower** than usual. Peak season remains **{top3_names}**."
        )
else:
    if total_selected > 0:
        anomaly_str = "Inusual" if is_es else "Off-season"
        diag_plain = f"Fuego fuera de temporada en {region_display} durante {period_title}: {total_selected:,.0f} {unit_label.lower()}."
        st.warning(
            f"**FUEGO FUERA DE TEMPORADA en {region_display} ({period_title}):** "
            f"Se detectaron {total_selected:,.0f} {unit_label.lower()} en un período sin actividad habitual."
            if is_es else
            f"**OFF-SEASON FIRE DETECTED in {region_display} ({period_title}):** "
            f"{total_selected:,.0f} {unit_label.lower()} recorded in a period with zero typical activity."
        )
    else:
        anomaly_str = "Normal (0)"
        diag_plain = f"Sin incendios detectados en {region_display} durante {period_title}."
        st.success(
            f"**SIN INCENDIOS DETECTADOS en {region_display} ({period_title}):** Comportamiento normal."
            if is_es else
            f"**NO FIRES DETECTED in {region_display} ({period_title}):** Normal behavior."
        )

# Nota aclaratoria clave para megaincendios ultra-rápidos de interfaz urbano-forestal (ej. Valparaíso Feb 2024)
if preset == "Valparaíso" and selected_year == 2024 and is_es:
    st.caption(
        "**Nota sobre el Megaincendio de Valparaíso (2–3 Feb 2024):** Este evento avanzó a velocidad extrema en menos de 48 horas sobre zonas urbanas densas (Viña del Mar, Quilpué y Villa Alemana). "
        "Como los satélites pasan 2–4 veces al día y el área quemada (~10.000 ha) fue geográficamente más compacta que los megaincendios forestales rurales de Biobío/Maule (que arden durante semanas en >400.000 ha), "
        "el número total de pasadas satelitales es menor, pero su **potencia radiativa (FRP)** y concentración urbana marcaron el máximo histórico regional de 26 años."
    )

# Botón accesible de lectura en voz alta (Web Speech API)
safe_speech_text = json.dumps(diag_plain)
speech_lang = "es-CL" if is_es else "en-US"
btn_speak_label = "Escuchar resumen en voz alta" if is_es else "Listen to summary aloud"
btn_stop_label = "Detener" if is_es else "Stop"
components.html(
    f"""
    <div style="display:flex; gap:10px; align-items:center; font-family: sans-serif;">
        <button onclick='
            window.speechSynthesis.cancel();
            const u = new SpeechSynthesisUtterance({safe_speech_text});
            u.lang = "{speech_lang}";
            u.rate = 0.96;
            window.speechSynthesis.speak(u);
        ' style="background:#1f6feb; color:white; border:none; border-radius:8px; padding:8px 16px; font-size:15px; font-weight:600; cursor:pointer;">
            🔊 {btn_speak_label}
        </button>
        <button onclick='window.speechSynthesis.cancel();'
            style="background:#444; color:white; border:none; border-radius:8px; padding:8px 12px; font-size:14px; cursor:pointer;">
            ⏹ {btn_stop_label}
        </button>
    </div>
    """,
    height=46
)

# 11. Indicadores Numéricos (KPIs con Porcentaje del Rango y Potencia FRP)
frp_selected = float(
    df_filtered[(df_filtered['year'] == selected_year) & (df_filtered['month'].isin(effective_months))]['harmonized_frp'].sum()
)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric(
    f"{'Focos en' if (is_es and metric_key == 'hotspots') else ('Potencia en' if is_es else 'Activity in')} {period_title}",
    f"{total_selected:,.0f} {unit_label}",
    delta=(f"Potencia térmica: {frp_selected:,.0f} MW" if (metric_key == "hotspots" and is_es) else None),
    delta_color="off"
)
kpi2.metric(median_label, f"{median_baseline:,.0f} {unit_label}")
kpi3.metric(
    ("Comparación con lo normal" if is_es else "Compared to normal")
    if audience == "citizen" else
    ("Anomalía vs. Mediana" if is_es else "Anomaly vs. Median"),
    anomaly_str
)
if is_full_year:
    kpi4.metric(
        "Concentración ventana crítica" if is_es else "Peak window share",
        f"{top3_share:.1f}% ({top3_names})"
    )
else:
    kpi4.metric(
        f"% {'del año' if is_es else 'of year'} {selected_year}",
        f"{share_of_year_pct:.1f}%",
        delta=(f"Histórico: {hist_share_pct:.1f}%" if is_es else f"Hist avg: {hist_share_pct:.1f}%"),
        delta_color="off"
    )

st.markdown("---")

# 12. Calendario Histórico
calendar_pivot = monthly_totals.pivot(index='year', columns='month', values=value_col).reindex(columns=range(1, 13))
max_monthly_all_time = max(float(monthly_totals[value_col].max()), 1.0)

if audience == "citizen":
    st.subheader("Paso 4 · Calendario Histórico por Mes y Año (2000–2026)" if is_es else "Step 4 · Historical Calendar by Month & Year (2000–2026)")
    st.markdown(
        (
            "**Cómo leer este cuadro:** Cada **fila horizontal** es un año y cada **columna vertical** es un mes. "
            "Cada **cuadrícula (rectángulo)** representa la actividad total detectada en esa región durante **ese mes y año exacto**.\n\n"
            f"**Guía de colores:** {color_guide_text}"
        )
        if is_es else
        (
            "**How to read this grid:** Each **row** is a year and each **column** is a month. "
            "Each **cell (rectangle)** represents the total fire activity detected in this region during **that exact month and year**.\n\n"
            f"**Color guide:** {color_guide_text}"
        )
    )
    fig_cal = px.imshow(
        calendar_pivot,
        labels=dict(x="Mes" if is_es else "Month", y="Año" if is_es else "Year", color=unit_label),
        x=month_names,
        y=calendar_pivot.index.astype(str),
        color_continuous_scale=color_scale,
        aspect="auto"
    )
    fig_cal.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10), font=dict(size=chart_font_size))
    st.plotly_chart(fig_cal, width='stretch')

else:
    col_cal, col_curve = st.columns([1.4, 1])

    with col_cal:
        st.subheader("Calendario de Actividad (26 Años)" if is_es else "26-Year Burning Activity Calendar")
        st.caption(
            f"Cada cuadrícula representa 1 mes de 1 año en {region_display}. {color_guide_text}"
            if is_es else
            f"Each cell represents 1 month of 1 year in {region_display}. {color_guide_text}"
        )
        fig_cal = px.imshow(
            calendar_pivot,
            labels=dict(x="Mes" if is_es else "Month", y="Año" if is_es else "Year", color=unit_label),
            x=month_names,
            y=calendar_pivot.index.astype(str),
            color_continuous_scale=color_scale,
            aspect="auto"
        )
        fig_cal.update_layout(height=450, margin=dict(l=10, r=10, t=10, b=10), font=dict(size=chart_font_size))
        st.plotly_chart(fig_cal, width='stretch')

    with col_curve:
        st.subheader(
            f"{'Curva Estacional' if is_es else 'Seasonal Profile'} ({selected_year} {'vs. Normal' if is_es else 'vs. Baseline'})"
        )
        st.caption(
            "La banda sombreada muestra el rango habitual (percentiles 25–75) y la línea sólida muestra el año elegido."
            if is_es else
            "Shaded band shows the normal corridor (25th–75th percentiles); solid line shows the selected year."
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
            line=dict(color=accent_line_color, width=3),
            marker=dict(size=7),
            name=f"{'Año' if is_es else 'Year'} {selected_year}"
        ))
        fig_curve.update_layout(
            height=450,
            margin=dict(l=10, r=10, t=10, b=10),
            font=dict(size=chart_font_size),
            yaxis=dict(title=unit_label, range=[0, max_monthly_all_time * 1.05]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_curve, width='stretch')

    if audience == "scientist":
        st.markdown("---")
        st.subheader(
            "Continuidad Instrumental 2000–2026 (MODIS Calibrado vs. VIIRS Directo)"
            if is_es else
            "2000–2026 Instrumental Continuity (MODIS Calibrated vs. VIIRS Direct)"
        )
        annual_df = annual_totals.reset_index()
        modis_lbl = "MODIS (Calibrado)" if is_es else "MODIS (Calibrated)"
        viirs_lbl = "VIIRS (Directo)" if is_es else "VIIRS (Direct)"
        annual_df['Sensor'] = np.where(annual_df['year'] < 2012, modis_lbl, viirs_lbl)

        bar_colors = (
            {modis_lbl: '#FE9929', viirs_lbl: '#B10026'}
            if palette_mode == "standard" else
            {modis_lbl: '#3B528B', viirs_lbl: '#FDE725'}
        )

        fig_trend = px.bar(
            annual_df,
            x='year',
            y=value_col,
            color='Sensor',
            color_discrete_map=bar_colors,
            labels={'year': "Año" if is_es else "Year", value_col: unit_label}
        )
        fig_trend.add_hline(
            y=annual_median_baseline,
            line_dash="dash",
            line_color="gray",
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
            font=dict(size=chart_font_size),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_trend, width='stretch')

# Tabla accesible para lectores de pantalla (personas ciegas / baja visión)
with st.expander(
    "Ver datos mensuales en tabla accesible (Lectores de pantalla)"
    if is_es else
    "View monthly data in accessible table (Screen readers)"
):
    acc_df = pd.DataFrame({
        "Mes / Month": month_full_names,
        f"{selected_year} ({unit_label})": [
            round(float(monthly_totals[(monthly_totals['year'] == selected_year) & (monthly_totals['month'] == m)][value_col].sum()), 1)
            for m in range(1, 13)
        ],
        f"{'Mediana 2000–2025' if is_es else '2000–2025 Median'} ({unit_label})": [
            round(float(hist_complete[hist_complete['month'] == m][value_col].median()), 1)
            for m in range(1, 13)
        ],
        "% Historico / Share": [
            round(float(month_totals_hist.loc[m] / month_totals_hist.sum() * 100), 1) if month_totals_hist.sum() > 0 else 0.0
            for m in range(1, 13)
        ]
    })
    st.dataframe(acc_df, hide_index=True, width='stretch')

st.markdown("---")

# 13. Catálogo Denso de Comunas, Localidades y Parques de Chile
CHILE_LOCALITIES = [
    ("Arica", -18.48, -70.31, "urban"),
    ("Putre", -18.20, -69.56, "semi_arid"),
    ("Iquique / Alto Hospicio", -20.24, -70.12, "urban"),
    ("Pozo Almonte / Pica", -20.26, -69.78, "desert"),
    ("Calama / Chuquicamata", -22.46, -68.93, "industrial_desert"),
    ("San Pedro de Atacama", -22.91, -68.20, "desert"),
    ("Antofagasta", -23.65, -70.40, "industrial_desert"),
    ("Taltal", -25.41, -70.48, "industrial_desert"),
    ("Chañaral / Diego de Almagro", -26.35, -70.62, "industrial_desert"),
    ("Copiapó / Tierra Amarilla", -27.37, -70.33, "industrial_desert"),
    ("Vallenar / Alto del Carmen", -28.58, -70.76, "semi_arid"),
    ("La Serena / Coquimbo", -29.90, -71.25, "semi_arid"),
    ("Vicuña / Paihuano", -30.03, -70.71, "semi_arid"),
    ("Ovalle / Monte Patria", -30.60, -71.20, "semi_arid"),
    ("Illapel / Salamanca", -31.63, -71.17, "semi_arid"),
    ("La Ligua / Petorca / Cabildo", -32.45, -71.23, "forest_agri"),
    ("San Felipe / Los Andes", -32.75, -70.72, "forest_agri"),
    ("Quillota / La Calera / Limache", -32.88, -71.25, "forest_agri"),
    ("Viña del Mar / Quilpué / Villa Alemana / Valparaíso", -33.04, -71.48, "forest_agri"),
    ("Casablanca", -33.32, -71.41, "forest_agri"),
    ("San Antonio / Cartagena / Algarrobo", -33.59, -71.61, "forest_agri"),
    ("Colina / Lampa / Tiltil", -33.20, -70.68, "forest_agri"),
    ("Santiago / Puente Alto / Maipú", -33.48, -70.65, "forest_agri"),
    ("San José de Maipo", -33.64, -70.35, "forest_agri"),
    ("Melipilla / Curacaví / María Pinto", -33.69, -71.21, "forest_agri"),
    ("Talagante / Peñaflor / Paine", -33.66, -70.93, "forest_agri"),
    ("Rancagua / Machalí / Graneros", -34.17, -70.74, "forest_agri"),
    ("Rengo / San Vicente / Peumo", -34.41, -70.86, "forest_agri"),
    ("San Fernando / Chimbarongo", -34.58, -70.99, "forest_agri"),
    ("Santa Cruz / Peralillo / Marchigüe", -34.64, -71.36, "forest_agri"),
    ("Pichilemu / Litueche / Navidad", -34.39, -72.00, "forest_agri"),
    ("Curicó / Teno / Romeral / Molina", -34.98, -71.24, "forest_agri"),
    ("Hualañé / Licantén / Vichuquén", -34.98, -71.81, "forest_agri"),
    ("Talca / San Clemente / Maule", -35.43, -71.66, "forest_agri"),
    ("Constitución / Empedrado / Curepto", -35.33, -72.41, "forest_agri"),
    ("San Javier / Villa Alegre", -35.59, -71.74, "forest_agri"),
    ("Linares / Colbún / Yerbas Buenas", -35.85, -71.59, "forest_agri"),
    ("Longaví / Retiro / Parral", -36.14, -71.83, "forest_agri"),
    ("Cauquenes / Chanco / Pelluhue", -35.97, -72.32, "forest_agri"),
    ("San Carlos / Ñiquén / San Fabián", -36.42, -71.96, "forest_agri"),
    ("Coelemu / Quirihue / Ninhue / Trehuaco", -36.49, -72.70, "forest_agri"),
    ("Portezuelo / Ránquil / Nicolás", -36.53, -72.43, "forest_agri"),
    ("Chillán / Chillán Viejo / Coihueco", -36.61, -72.10, "forest_agri"),
    ("Pinto / San Ignacio / El Carmen", -36.70, -71.89, "forest_agri"),
    ("Quillón / Bulnes", -36.74, -72.47, "forest_agri"),
    ("Yungay / Pemuco / Tucapel", -37.12, -72.01, "forest_agri"),
    ("Tomé / Penco / Concepción / Talcahuano", -36.74, -72.99, "forest_agri"),
    ("Florida / Hualqui", -36.82, -72.66, "forest_agri"),
    ("Coronel / Lota / Santa Juana", -37.03, -73.14, "forest_agri"),
    ("Cabrero / Yumbel / Laja / San Rosendo", -37.04, -72.40, "forest_agri"),
    ("Los Ángeles / Nacimiento / Negrete", -37.47, -72.35, "forest_agri"),
    ("Quilleco / Antuco", -37.47, -71.96, "forest_agri"),
    ("Mulchén / Quilaco", -37.72, -72.24, "forest_agri"),
    ("Santa Bárbara / Alto Biobío", -37.67, -71.82, "forest_agri"),
    ("Arauco / Curanilahue / Los Álamos", -37.47, -73.35, "forest_agri"),
    ("Lebu / Cañete / Contulmo / Tirúa", -37.80, -73.40, "forest_agri"),
    ("Angol / Renaico / Collipulli", -37.80, -72.71, "forest_agri"),
    ("Los Sauces / Purén / Lumaco", -37.98, -72.83, "forest_agri"),
    ("Victoria / Traiguén / Ercilla", -38.23, -72.33, "forest_agri"),
    ("Curacautín / Lonquimay", -38.44, -71.89, "forest_agri"),
    ("Galvarino / Perquenco / Lautaro", -38.41, -72.78, "forest_agri"),
    ("Nueva Imperial / Carahue / Cholchol", -38.74, -72.95, "forest_agri"),
    ("Temuco / Padre Las Casas / Vilcún", -38.74, -72.59, "forest_agri"),
    ("Freire / Pitrufquén / Gorbea", -38.95, -72.63, "forest_agri"),
    ("Cunco / Melipeuco", -38.93, -72.03, "forest_agri"),
    ("Villarrica / Pucón / Curarrehue", -39.28, -72.23, "forest_agri"),
    ("Loncoche / Lanco / Panguipulli", -39.46, -72.63, "forest_agri"),
    ("Valdivia / Mariquina / Máfil / Corral", -39.81, -73.25, "forest_agri"),
    ("Los Lagos / Paillaco / Futrono", -39.86, -72.82, "forest_agri"),
    ("La Unión / Río Bueno / Lago Ranco", -40.29, -73.08, "forest_agri"),
    ("Osorno / San Pablo / Río Negro", -40.57, -73.13, "forest_agri"),
    ("Purranque / Puerto Octay / Puyehue", -40.91, -73.16, "forest_agri"),
    ("Frutillar / Llanquihue / Puerto Varas", -41.25, -73.01, "forest_agri"),
    ("Puerto Montt / Calbuco / Maullín", -41.47, -72.94, "forest_agri"),
    ("Cochamó / Hualaihué", -41.50, -72.30, "forest_agri"),
    ("Ancud / Quemchi / Dalcahue (Chiloé)", -41.87, -73.83, "forest_agri"),
    ("Castro / Chonchi / Quellón (Chiloé)", -42.48, -73.76, "forest_agri"),
    ("Chaitén / Futaleufú / Palena", -42.92, -72.71, "forest_agri"),
    ("Cisnes / Lago Verde", -44.75, -72.70, "forest_agri"),
    ("Coyhaique / Puerto Aysén", -45.57, -72.07, "forest_agri"),
    ("Río Ibáñez / Chile Chico", -46.54, -71.72, "forest_agri"),
    ("Cochrane / Tortel / O'Higgins", -47.25, -72.57, "forest_agri"),
    ("Puerto Natales / Torres del Paine", -51.73, -72.50, "forest_agri"),
    ("Punta Arenas / Laguna Blanca", -53.16, -70.91, "forest_agri"),
    ("Porvenir / Primavera (Tierra del Fuego)", -53.30, -70.37, "forest_agri"),
]

def describe_location_local(lat, lon, is_es_flag=True):
    best_name, best_dist, best_type = "", 1e9, "forest_agri"
    best_dlat, best_dlon = 0.0, 0.0
    for name, l_lat, l_lon, l_type in CHILE_LOCALITIES:
        dlat = (lat - l_lat) * 111.0
        dlon = (lon - l_lon) * 111.0 * np.cos(np.radians(lat))
        dist = float(np.hypot(dlat, dlon))
        if dist < best_dist:
            best_dist = dist
            best_name = name
            best_type = l_type
            best_dlat, best_dlon = dlat, dlon
    if best_dist < 10.0:
        loc_str = f"Comuna / Sector {best_name}" if is_es_flag else f"{best_name} commune/area"
    else:
        ns = "N" if best_dlat >= 0 else "S"
        ew = ("E" if best_dlon >= 0 else ("O" if is_es_flag else "W"))
        loc_str = (
            f"~{best_dist:.0f} km al {ns}{ew} de {best_name}"
            if is_es_flag else
            f"~{best_dist:.0f} km {ns}{ew} of {best_name}"
        )
    return loc_str, best_type, best_name

unique_lats = np.sort(df['lat_bin'].unique())
diffs = np.diff(unique_lats)
diffs = diffs[diffs > 1e-5]
native_res = float(np.min(diffs)) if len(diffs) > 0 else 0.05

st.subheader(
    f"Paso 5 · Mapa Interactivo (Satélite / Calles) y Sectores Afectados — {period_title}"
    if is_es else
    f"Step 5 · Interactive Map (Satellite / Streets) & Affected Sectors — {period_title}"
)

col_map, col_side = st.columns([2.2, 1])

with col_map:
    # Controles interactivos superiores del mapa
    m_ctrl1, m_ctrl2, m_ctrl3, m_ctrl4 = st.columns([1.15, 1.15, 1.15, 1.15])
    with m_ctrl1:
        map_scope_mode = st.radio(
            "Datos en mapa:" if is_es else "Map scope:",
            ["selected", "all_26y"],
            format_func=lambda k: (
                ("Período elegido" if is_es else "Selected period")
                if k == "selected" else
                ("Acumulado 26 años" if is_es else "26-Yr Cumulative")
            ),
            horizontal=True
        )
    with m_ctrl2:
        viz_mode = st.radio(
            "Estilo visual:" if is_es else "Visual layer:",
            ["bubbles", "heatmap", "grid"],
            format_func=lambda k: {
                "bubbles": "Círculos" if is_es else "Circles",
                "heatmap": "Nube calor" if is_es else "Heat cloud",
                "grid": "Cuadrícula" if is_es else "Grid",
            }[k],
            horizontal=True
        )
    with m_ctrl3:
        res_mode = st.radio(
            "Detalle espacial:" if is_es else "Spatial grid:",
            ["fine", "commune", "macro"],
            format_func=lambda k: {
                "fine": f"Máx (~{native_res * 111:.1f} km)" if is_es else f"Max (~{native_res * 111:.1f} km)",
                "commune": "Comunal (~11 km)" if is_es else "Commune (~11 km)",
                "macro": "Regional (~22 km)" if is_es else "Regional (~22 km)",
            }[k],
            horizontal=True
        )
    with m_ctrl4:
        map_style_choice = st.radio(
            "Mapa base:" if is_es else "Basemap:",
            ["satellite", "osm", "dark"],
            format_func=lambda k: {
                "satellite": "Satélite" if is_es else "Satellite",
                "osm": "Calles" if is_es else "Streets",
                "dark": "Oscuro" if is_es else "Dark",
            }[k],
            horizontal=True
        )

    df_active_map_df = df_map_source if map_scope_mode == "selected" else df_filtered
    map_scope_label = period_title if map_scope_mode == "selected" else ("2000–2026 (Acumulado)" if is_es else "2000–2026 (Cumulative)")

    if df_active_map_df.empty:
        st.info(
            "No se registraron focos de calor en este período para la zona elegida. Cambia 'Datos en mapa' a 'Acumulado 26 años' para ver el historial completo."
            if is_es else
            "No fire hotspots recorded in this period. Switch 'Map scope' to '26-Yr Cumulative' to inspect full history."
        )
        map_agg = pd.DataFrame()
        selected_idx = -1
        exact_zone_display = ""
        exact_comuna_name = ""
    else:
        res_step_map = {
            "fine": native_res,
            "commune": max(native_res, 0.10),
            "macro": max(native_res, 0.20),
        }
        active_grid_res = res_step_map[res_mode]

        df_map_work = df_active_map_df.copy()
        w = df_map_work[value_col].clip(lower=1e-6)
        df_map_work["_w_lat"] = df_map_work["lat_exact"] * w
        df_map_work["_w_lon"] = df_map_work["lon_exact"] * w
        df_map_work["_w"] = w

        if res_mode == "fine":
            df_map_work["_g_lat"] = df_map_work["lat_bin"]
            df_map_work["_g_lon"] = df_map_work["lon_bin"]
        else:
            df_map_work["_g_lat"] = (np.floor(df_map_work["lat_exact"] / active_grid_res) + 0.5) * active_grid_res
            df_map_work["_g_lon"] = (np.floor(df_map_work["lon_exact"] / active_grid_res) + 0.5) * active_grid_res

        map_agg = (
            df_map_work.groupby(['_g_lat', '_g_lon'])
            .agg(
                harmonized_hotspots=('harmonized_hotspots', 'sum'),
                harmonized_frp=('harmonized_frp', 'sum'),
                _w_lat=('_w_lat', 'sum'),
                _w_lon=('_w_lon', 'sum'),
                _w=('_w', 'sum'),
            )
            .reset_index()
            .rename(columns={'_g_lat': 'lat_bin', '_g_lon': 'lon_bin'})
        )
        map_agg["lat_plot"] = map_agg["_w_lat"] / map_agg["_w"]
        map_agg["lon_plot"] = map_agg["_w_lon"] / map_agg["_w"]
        map_agg = map_agg[map_agg[value_col] > 0].sort_values(by=value_col, ascending=False).reset_index(drop=True)
        map_agg["cell_id"] = map_agg.index.astype(str)

        total_map_val = max(float(map_agg[value_col].sum()), 1e-6)
        map_agg["pct_share"] = (map_agg[value_col] / total_map_val) * 100.0

        loc_info = [describe_location_local(float(r["lat_plot"]), float(r["lon_plot"]), is_es) for _, r in map_agg.iterrows()]
        map_agg["localidad"] = [x[0] for x in loc_info]
        map_agg["zone_type"] = [x[1] for x in loc_info]
        map_agg["comuna_ref"] = [x[2] for x in loc_info]

        top_n = min(len(map_agg), 35)
        inspect_options = [-1] + list(range(top_n))
        selected_idx = st.selectbox(
            f"Enfocar comuna / sector en el mapa ({map_scope_label}) — o haz clic directo en cualquier punto:"
            if is_es else
            f"Focus commune / sector on map ({map_scope_label}) — or click any point directly:",
            options=inspect_options,
            format_func=lambda idx: (
                ("— Vista general de toda la región —" if is_es else "— Full region overview —")
                if idx == -1 else
                f"#{idx + 1} · {map_agg.loc[idx, 'localidad']} ({map_agg.loc[idx, value_col]:,.0f} {unit_label} · {map_agg.loc[idx, 'pct_share']:.1f}%)"
            )
        )

        # Escala de color calibrada al percentil 95 para que los focos críticos resalten con contraste real
        color_max_val = float(np.percentile(map_agg[value_col], 95)) if len(map_agg) > 3 else float(map_agg[value_col].max())
        color_max_val = max(color_max_val, 1.0)

        zoom_to_selected = False
        show_buffer_rings = False
        if selected_idx != -1:
            z_c1, z_c2 = st.columns(2)
            with z_c1:
                zoom_to_selected = st.checkbox(
                    f"Acercar vista detallada en {map_agg.loc[selected_idx, 'localidad']}"
                    if is_es else
                    f"Zoom in on {map_agg.loc[selected_idx, 'localidad']}",
                    value=True
                )
            with z_c2:
                show_buffer_rings = st.checkbox(
                    "Mostrar anillos preventivos (5 km y 10 km)"
                    if is_es else
                    "Show preventive radius rings (5 km & 10 km)",
                    value=True
                )

        if selected_idx != -1 and zoom_to_selected:
            center_lat = float(map_agg.loc[selected_idx, "lat_plot"])
            center_lon = float(map_agg.loc[selected_idx, "lon_plot"])
            zoom_lvl = 11.8
        elif preset != "All Chile" and preset != "Custom Coordinates":
            center_lat = float((df_filtered['lat_exact'].min() + df_filtered['lat_exact'].max()) / 2.0)
            center_lon = float((df_filtered['lon_exact'].min() + df_filtered['lon_exact'].max()) / 2.0)
            span = max(
                float(df_filtered['lat_exact'].max() - df_filtered['lat_exact'].min()) + active_grid_res,
                float(df_filtered['lon_exact'].max() - df_filtered['lon_exact'].min()) + active_grid_res
            )
            zoom_lvl = float(np.clip(8.3 - np.log2(max(span, 0.4)), 3.2, 8.2))
        else:
            center_lat = (lat_min + lat_max) / 2.0
            center_lon = (lon_min + lon_max) / 2.0
            span = max(abs(lat_max - lat_min), abs(lon_max - lon_min))
            zoom_lvl = float(np.clip(8.3 - np.log2(max(span, 0.4)), 3.2, 8.2))

        hover_cols = {
            "localidad": True,
            "lat_plot": ":.4f",
            "lon_plot": ":.4f",
            "harmonized_hotspots": ":,.0f",
            "harmonized_frp": ":,.1f",
            "pct_share": ":.1f"
        }

        labels_map = {
            "localidad": "Zona / Comuna" if is_es else "Zone / Commune",
            "lat_plot": "Latitud" if is_es else "Latitude",
            "lon_plot": "Longitud" if is_es else "Longitude",
            "harmonized_hotspots": "Focos de calor" if is_es else "Calibrated Hotspots",
            "harmonized_frp": "Potencia FRP (MW)" if is_es else "FRP Power (MW)",
            "pct_share": "% del período" if is_es else "% of period"
        }

        base_style_name = "carto-darkmatter" if map_style_choice == "dark" else "open-street-map"

        if viz_mode == "bubbles":
            scatter_func = px.scatter_map if hasattr(px, "scatter_map") else px.scatter_mapbox
            style_kwarg = {"map_style": base_style_name} if hasattr(px, "scatter_map") else {"mapbox_style": base_style_name}
            fig_map = scatter_func(
                map_agg,
                lat="lat_plot",
                lon="lon_plot",
                size=value_col,
                color=value_col,
                size_max=30,
                color_continuous_scale=color_scale,
                range_color=[0, color_max_val],
                opacity=0.88,
                zoom=zoom_lvl,
                center={"lat": center_lat, "lon": center_lon},
                hover_name="localidad",
                hover_data=hover_cols,
                labels=labels_map,
                **style_kwarg
            )
        elif viz_mode == "heatmap":
            density_func = px.density_map if hasattr(px, "density_map") else px.density_mapbox
            style_kwarg = {"map_style": base_style_name} if hasattr(px, "density_map") else {"mapbox_style": base_style_name}
            fig_map = density_func(
                map_agg,
                lat="lat_plot",
                lon="lon_plot",
                z=value_col,
                radius=28,
                color_continuous_scale=color_scale,
                range_color=[0, color_max_val],
                opacity=0.80,
                zoom=zoom_lvl,
                center={"lat": center_lat, "lon": center_lon},
                hover_name="localidad",
                hover_data=hover_cols,
                labels=labels_map,
                **style_kwarg
            )
        else:
            half = active_grid_res / 2.0
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
            choro_func = px.choropleth_map if hasattr(px, "choropleth_map") else px.choropleth_mapbox
            style_kwarg = {"map_style": base_style_name} if hasattr(px, "choropleth_map") else {"mapbox_style": base_style_name}
            hover_grid = dict(hover_cols)
            hover_grid["cell_id"] = False
            fig_map = choro_func(
                map_agg,
                geojson=geojson_grid,
                locations="cell_id",
                featureidkey="id",
                color=value_col,
                color_continuous_scale=color_scale,
                range_color=[0, color_max_val],
                opacity=0.68,
                zoom=zoom_lvl,
                center={"lat": center_lat, "lon": center_lon},
                hover_data=hover_grid,
                labels=labels_map,
                **style_kwarg
            )
            fig_map.update_traces(marker_line_width=0.7, marker_line_color="rgba(255,255,255,0.45)")

        # Capa Satelital Real (Esri World Imagery + etiquetas de caminos/ciudades)
        if map_style_choice == "satellite":
            sat_layers = [
                {
                    "below": "traces",
                    "sourcetype": "raster",
                    "sourceattribution": "Esri World Imagery",
                    "source": [
                        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                    ],
                },
                {
                    "below": "traces",
                    "sourcetype": "raster",
                    "source": [
                        "https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"
                    ],
                },
            ]
            if hasattr(px, "scatter_map"):
                fig_map.update_layout(map_layers=sat_layers)
            else:
                fig_map.update_layout(mapbox_layers=sat_layers)

        # Anillos de radio preventivo (5 km y 10 km) alrededor del sector seleccionado
        if selected_idx != -1 and show_buffer_rings:
            s_lat_ring = float(map_agg.loc[selected_idx, "lat_plot"])
            s_lon_ring = float(map_agg.loc[selected_idx, "lon_plot"])
            lat_5, lon_5 = make_circle_coords(s_lat_ring, s_lon_ring, 5.0)
            lat_10, lon_10 = make_circle_coords(s_lat_ring, s_lon_ring, 10.0)
            trace_cls = go.Scattermap if hasattr(go, "Scattermap") else go.Scattermapbox
            fig_map.add_trace(trace_cls(
                lat=lat_5,
                lon=lon_5,
                mode="lines",
                line=dict(width=2.5, color="#00E5FF"),
                name="Radio 5 km" if is_es else "5 km Radius",
                hoverinfo="skip"
            ))
            fig_map.add_trace(trace_cls(
                lat=lat_10,
                lon=lon_10,
                mode="lines",
                line=dict(width=1.8, color="#FFD600"),
                name="Radio 10 km" if is_es else "10 km Radius",
                hoverinfo="skip"
            ))

        fig_map.update_layout(
            height=520,
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=0.01, xanchor="left", x=0.01, bgcolor="rgba(20,20,20,0.65)", font=dict(color="white"))
        )

        try:
            chart_event = st.plotly_chart(fig_map, width='stretch', on_select="rerun", selection_mode="points", key="fire_map_chart")
            if chart_event and getattr(chart_event, "selection", None) and chart_event.selection.get("points"):
                pt = chart_event.selection["points"][0]
                if pt.get("curve_number", 0) == 0:
                    clicked_idx = pt.get("point_index", pt.get("pointIndex", None))
                    if clicked_idx is not None and 0 <= int(clicked_idx) < len(map_agg):
                        selected_idx = int(clicked_idx)
        except TypeError:
            st.plotly_chart(fig_map, width='stretch')

        exact_zone_display = ""
        exact_comuna_name = ""

        if selected_idx != -1 and not map_agg.empty:
            sel_row = map_agg.loc[selected_idx]
            s_lat, s_lon = float(sel_row["lat_plot"]), float(sel_row["lon_plot"])
            osm_exact, osm_comuna = reverse_geocode_exact(round(s_lat, 4), round(s_lon, 4), is_es)
            exact_zone_display = osm_exact if osm_exact else sel_row["localidad"]
            exact_comuna_name = osm_comuna if osm_comuna else sel_row["comuna_ref"]

            gmaps_url = f"https://www.google.com/maps/search/?api=1&query={s_lat:.5f},{s_lon:.5f}"
            firms_url = f"https://firms.modaps.eosdis.nasa.gov/map/#d:24hrs;@{s_lon:.4f},{s_lat:.4f},13z"

            if sel_row["zone_type"] == "industrial_desert":
                origin_note = (
                    "**Origen probable:** En el norte minero (Calama / Antofagasta), los focos fijos corresponden generalmente a **fundiciones de cobre o plantas solares**, no a incendios forestales."
                    if is_es else
                    "**Probable source:** In northern mining areas, persistent detections generally correspond to **copper smelters or solar thermal plants**, not forest wildfires."
                )
            else:
                origin_note = (
                    "**Origen probable:** En esta zona centro-sur, las detecciones reflejan principalmente **incendios forestales, de pastizales, interfaz urbano-forestal o quemas agrícolas**."
                    if is_es else
                    "**Probable source:** In central-southern Chile, detections primarily reflect **forest/brush wildfires, urban-wildland interface fires, or agricultural burns**."
                )

            st.info(
                f"**Ubicación exacta:** **{exact_zone_display}** (`{s_lat:.4f}°, {s_lon:.4f}°`) — "
                f"**{sel_row['harmonized_hotspots']:,.0f}** {'focos calibrados' if is_es else 'calibrated hotspots'} "
                f"(**{sel_row['harmonized_frp']:,.0f} MW** {'potencia radiativa' if is_es else 'radiative power'})\n\n"
                f"{origin_note}\n\n"
                f"[Abrir en Google Maps]({gmaps_url})  |  "
                f"[Focos activos 24h NASA FIRMS]({firms_url})"
            )

        # Ranking Top 10 Sectores / Comunas más afectados en el período
        if not map_agg.empty:
            top_rank_df = (
                map_agg.groupby("localidad", as_index=False)[value_col]
                .sum()
                .sort_values(by=value_col, ascending=False)
                .head(10)
                .sort_values(by=value_col, ascending=True)
            )
            if not top_rank_df.empty:
                st.markdown(
                    f"**Top {len(top_rank_df)} {'sectores más afectados en' if is_es else 'most affected sectors in'} {map_scope_label}:**"
                )
                fig_rank = px.bar(
                    top_rank_df,
                    x=value_col,
                    y="localidad",
                    orientation="h",
                    color=value_col,
                    color_continuous_scale=color_scale,
                    labels={"localidad": "", value_col: unit_label}
                )
                fig_rank.update_layout(
                    height=max(220, len(top_rank_df) * 32),
                    margin=dict(l=10, r=10, t=5, b=10),
                    font=dict(size=chart_font_size),
                    coloraxis_showscale=False,
                    yaxis=dict(title=""),
                    xaxis=dict(title=unit_label)
                )
                st.plotly_chart(fig_rank, width='stretch')

with col_side:
    if audience == "citizen":
        st.subheader("Consulta a tu Municipio y Ayuda" if is_es else "Contact Municipality & Help")
        if is_es:
            st.error("**Emergencias activas:** Si ves humo o fuego ahora mismo, llama gratis al **130 (CONAF)** o **132 (Bomberos)**.")

            if not map_agg.empty:
                if selected_idx != -1 and exact_zone_display:
                    active_sector = exact_zone_display
                    muni_target = f"de la Municipalidad de {exact_comuna_name}" if exact_comuna_name else "de la Municipalidad"
                    p_lat = float(map_agg.loc[selected_idx, "lat_plot"])
                    p_lon = float(map_agg.loc[selected_idx, "lon_plot"])
                else:
                    p_lat = float(map_agg.loc[0, "lat_plot"])
                    p_lon = float(map_agg.loc[0, "lon_plot"])
                    osm_top, osm_top_comuna = reverse_geocode_exact(round(p_lat, 4), round(p_lon, 4), True)
                    active_sector = osm_top if osm_top else map_agg.loc[0, "localidad"]
                    comuna_clean = osm_top_comuna if osm_top_comuna else map_agg.loc[0, "comuna_ref"]
                    muni_target = f"de la Municipalidad de {comuna_clean}" if comuna_clean else "de la Municipalidad"

                df_scope = df_filtered[
                    (df_filtered["lat_exact"].between(p_lat - 0.15, p_lat + 0.15)) &
                    (df_filtered["lon_exact"].between(p_lon - 0.15, p_lon + 0.15))
                ]
                if df_scope.empty:
                    df_scope = df_filtered
                scope_label = f"{region_display} — {active_sector}"
            else:
                df_scope = df_filtered
                scope_label = region_display
                muni_target = "de la Municipalidad"

            hist_scope = df_scope[df_scope["year"] < 2026]
            if hist_scope.empty:
                hist_scope = df_scope

            month_sums = hist_scope.groupby("month")[value_col].sum().reindex(range(1, 13), fill_value=0)
            if month_sums.sum() > 0:
                local_top3 = month_sums.nlargest(3)
                local_top3_idx = sorted(local_top3.index.tolist())
                mail_months = " – ".join([month_names[i - 1] for i in local_top3_idx])
                mail_share = local_top3.sum() / month_sums.sum() * 100
            else:
                mail_months = top3_names
                mail_share = top3_share

            st.markdown(
                f"**Solicitud preventiva para tu comuna ({scope_label}):**\n"
                f"Copia este texto y envíalo antes de **{mail_months}** a tu municipalidad o a las instituciones de prevención:"
            )
            msg_muni = (
                f"Estimado equipo de Emergencias {muni_target}:\n"
                f"De acuerdo con los registros satelitales calibrados de NASA FIRMS (2000–2026), nuestra zona ({scope_label}) "
                f"concentra el {mail_share:.0f}% de la actividad histórica de incendios entre {mail_months}. "
                f"Solicitamos informar el calendario de limpieza de maleza y mantención de cortafuegos preventivos para nuestro sector."
            )
            st.text_area("Mensaje listo para copiar:", value=msg_muni, height=160)

            mailto_subject = quote(f"Solicitud preventiva de cortafuegos - {scope_label}")
            mailto_body = quote(msg_muni)
            mailto_link = f"mailto:consulta.oirs@conaf.cl,oirs@senapred.gob.cl?subject={mailto_subject}&body={mailto_body}"

            st.markdown(f"[Abrir correo listo para enviar (CONAF / SENAPRED)]({mailto_link})")

            st.markdown(
                "**Correos de instituciones de ayuda y prevención:**\n"
                "* **CONAF (Prevención de Incendios - OIRS):** `consulta.oirs@conaf.cl` (Fono: `130`)\n"
                "* **SENAPRED (Gestión de Riesgos y Emergencias):** `oirs@senapred.gob.cl`\n"
                "* **Red de Prevención Comunitaria (Interfaz Urbano-Forestal):** `contacto@reddeprevencioncomunitaria.cl`\n"
                "* **Tu Municipalidad:** Busca la ventanilla **OIRS** o **Emergencias** en el sitio web de tu comuna y pega este mismo mensaje."
            )
        else:
            st.error("**Active emergencies:** If you see smoke or fire right now, call **130 (CONAF)** or **132 (Firefighters)**.")
            st.info(
                f"In **{region_display}**, **{top3_names}** concentrate **{top3_share:.0f}%** of annual fire activity.\n\n"
                "**Institutional contacts:**\n"
                "- **CONAF (National Forestry Corp.):** `consulta.oirs@conaf.cl` (Phone: `130`)\n"
                "- **SENAPRED (National Disaster Prevention):** `oirs@senapred.gob.cl`\n"
                "- **Local Municipality:** Contact your local Emergency / OIRS desk ahead of this critical window."
            )

    elif audience == "municipal":
        st.subheader("Exportar Reporte Territorial" if is_es else "Export Territorial Report")
        st.write(
            f"Descarga la serie histórica calibrada de **{region_display}** ({len(df_filtered):,} registros) para usar en QGIS o Excel."
            if is_es else
            f"Download the calibrated historical dataset for **{region_display}** ({len(df_filtered):,} records) for QGIS or Excel."
        )
        csv_export = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar Datos Regionales (CSV)" if is_es else "Download Regional Data (CSV)",
            data=csv_export,
            file_name=f"incendios_calibrados_{preset.replace(' ', '_').lower()}.csv",
            mime="text/csv",
        )
        st.info(
            "Las coordenadas exactas (`lat_exact`, `lon_exact`) permiten cruzar cada foco con predios, caminos y cortafuegos en QGIS."
            if is_es else
            "Exact coordinates (`lat_exact`, `lon_exact`) let municipal teams overlay hotspots with roads and firebreaks in QGIS."
        )
    else:
        st.subheader("Exportar Dataset Calibrado" if is_es else "Export Calibrated Dataset")
        st.write(
            f"Serie armonizada MODIS + VIIRS para **{region_display}** ({len(df_filtered):,} registros celda-mes)."
            if is_es else
            f"Harmonized MODIS + VIIRS time series for **{region_display}** ({len(df_filtered):,} grid-month records)."
        )
        csv_export = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar CSV Armonizado" if is_es else "Download Harmonized CSV",
            data=csv_export,
            file_name=f"harmonized_fires_{preset.replace(' ', '_').lower()}.csv",
            mime="text/csv",
        )
        st.info(
            "Validación: Calibración MODIS→VIIRS mediante Gradient Boosting (`scan × track` + factor de Duan). "
            "`R² lineal = 0.887` (`0.689` log); hindcast temporal ciego 2012–2015 con `R² = 0.784` y sesgo `+4.88%`."
            if is_es else
            "Validation: MODIS→VIIRS Gradient Boosting (`scan × track` + Duan's smearing). "
            "`Linear R² = 0.887` (`0.689` log); blind 2012–2015 temporal hindcast `R² = 0.784` (`+4.88%` bias)."
        )

st.markdown("---")

# 14. Guía Informativa: Prevención de Incendios, Satélites y Preguntas Clave
st.subheader(
    "Guía Informativa: Prevención, Satélites y Preguntas Frecuentes"
    if is_es else
    "Information Guide: Wildfire Prevention, Satellites & FAQ"
)

tab_faq, tab_sat, tab_how = st.tabs(
    [
        "Prevención y preguntas frecuentes",
        "Satélites utilizados",
        "Qué se hizo en el proyecto"
    ]
    if is_es else
    [
        "Prevention & FAQ",
        "Satellites used",
        "How it was built"
    ]
)

with tab_faq:
    if is_es:
        with st.expander("¿Cómo prevenir incendios forestales en el hogar, parcelas y barrios? (Guía práctica)", expanded=True):
            st.markdown(
                "En Chile, más del **99% de los incendios forestales se originan por acción humana** (por descuido, negligencia o intencionalidad), y el riesgo aumenta fuertemente en zonas de **interfaz urbano-forestal** (donde las casas colindan con cerros, bosques o pastizales).\n\n"
                "**1. Prepara una zona de autoprotección alrededor de tu vivienda (antes de noviembre):**\n"
                "* **Despeja los primeros 10 a 30 metros:** Elimina pasto seco, hojas acumuladas, ramas bajas de árboles y matorrales densos alrededor de casas, bodegas y cercos.\n"
                "* **Limpia techos y canaletas:** Las pavesas (brasas transportadas por el aire) suelen iniciar incendios al caer sobre hojas secas acumuladas en techumbres y canaletas.\n"
                "* **Ordena materiales inflamables:** Mantén leña, cilindros de gas, combustibles y pinturas lejos de la vivienda y protegidos bajo techo o en casetas cerradas.\n\n"
                "**2. Evita chispas y fuentes de ignición en actividades cotidianas:**\n"
                "* **Herramientas eléctricas y agrícolas:** No uses esmeriles angulares (galleteras), soldadoras ni desmalezadoras de cuchilla metálica cerca de vegetación seca en tardes calurosas; ten siempre agua o un extintor a mano.\n"
                "* **Cero quemas de basura o rastrojos:** Nunca quemes desechos domésticos ni restos vegetales fuera del calendario legal autorizado y supervisado por **CONAF**.\n"
                "* **Fogatas, cigarrillos y vidrios:** Enciende fuego solo en lugares habilitados, apágalo completamente con abundante agua y tierra hasta que no quede humo, y nunca arrojes colillas ni botellas de vidrio (pueden generar efecto lupa).\n\n"
                "**3. Organización comunitaria y gestión municipal:**\n"
                "* **Identifica vías de evacuación y puntos de agua:** Coordina con tus vecinos rutas de salida despejadas para vehículos de emergencia y ubica grifos, piscinas o estanques comunitarios.\n"
                "* **Exige mantención preventiva:** Usa el mensaje automático del panel superior para solicitar a tu municipalidad limpieza de sitios eriazos, podas bajo tendidos eléctricos y cortafuegos antes de los meses críticos de tu comuna."
            )

        with st.expander("¿Qué hacer si ves humo, un foco de fuego o recibes alerta de evacuación?"):
            st.markdown(
                "**1. Avisa de inmediato a los equipos de emergencia (cada minuto cuenta):**\n"
                "* **CONAF:** Llama gratis al **130**.\n"
                "* **Bomberos:** Llama gratis al **132**.\n"
                "* **Carabineros / PDI:** **133** o **134** (especialmente si observas conductas sospechosas o inicio intencional).\n"
                "* Entrega referencias claras: comuna, nombre del camino o kilómetro de ruta, punto de referencia cercano y color/dirección de la columna de humo.\n\n"
                "**2. Si recibes una alerta SAE de evacuación en tu celular:**\n"
                "* **Evacúa de inmediato:** No esperes a ver las llamas cerca ni regreses a buscar objetos materiales; el fuego en quebradas y pendientes puede avanzar a gran velocidad.\n"
                "* **Kit básico de salida rápida:** Ten preparada una mochila con agua, mascarillas (idealmente **N95 o KN95**), medicamentos esenciales, documentos de identidad, linterna, cargador portátil y correa/jaula para mascotas.\n\n"
                "**3. Cómo proteger tu salud ante humo denso:**\n"
                "* Cierra puertas y ventanas, y coloca paños húmedos en rendijas para reducir la entrada de humo al interior.\n"
                "* Evita hacer deporte o esfuerzos físicos al aire libre mientras haya humo visible.\n"
                "* Si debes salir, usa mascarilla **N95 o KN95** (las mascarillas quirúrgicas o de tela no filtran las partículas finas `PM2.5` del humo). Presta especial atención a niños, embarazadas, personas mayores y pacientes con asma o enfermedades cardíacas."
            )

        with st.expander("¿Cómo interpretar los focos de calor, la Potencia Radiativa (FRP) y los colores del mapa?"):
            st.markdown(
                "Este visor entrega dos indicadores complementarios observados desde el espacio:\n"
                "* **Cantidad de Focos Calibrados:** Cuenta cuántas detecciones térmicas activas registraron los satélites en un mes o período. Refleja **extensión y persistencia** en el tiempo.\n"
                "* **Potencia Radiativa del Fuego (FRP, en megawatts - MW):** Mide la **intensidad energética** del incendio (cuánta radiación infrarroja libera el fuego en el momento en que pasa el satélite). Un incendio muy intenso y rápido genera valores altísimos de FRP.\n"
                "* **Escala de colores del mapa:** Los tonos más claros indican actividad baja o aislada, mientras que los tonos oscuros (rojo intenso en modo estándar o amarillo brillante en modo daltonismo) señalan los sectores con **mayor concentración histórica o potencia acumulada**.\n"
                "* **Anillos de 5 km y 10 km:** Al hacer clic en cualquier punto del mapa, puedes activar anillos de distancia para evaluar qué tan cerca ocurrieron esos focos respecto a viviendas, escuelas o infraestructura crítica."
            )

        with st.expander("¿Por qué el megaincendio de Valparaíso (Febrero 2024) tiene menos focos totales que Biobío 2023?"):
            st.markdown(
                "Los satélites polares de la NASA/NOAA orbitan la Tierra pasando sobre cada punto de Chile entre **2 y 4 veces al día**.\n"
                "* El megaincendio de **Viña del Mar, Quilpué y Villa Alemana (2–3 de febrero de 2024)** fue un evento de interfaz urbano-forestal extraordinariamente rápido y violento: avanzó en menos de **48 horas** sobre unas **10.000 hectáreas** densamente pobladas.\n"
                "* En cambio, los megaincendios rurales de **Biobío, Ñuble y Maule (2017 y 2023)** ardieron durante **varias semanas** cubriendo más de **400.000 hectáreas** de plantaciones forestales y bosques.\n"
                "* Por esa diferencia de duración y superficie, un incendio que arde durante 3 semanas acumula muchas más pasadas satelitales que uno de 36 horas. Sin embargo, al revisar **Febrero 2024 en Valparaíso** o cambiar la métrica a **Potencia Térmica (FRP)**, se observa claramente que marcó el máximo histórico de 26 años para esa región."
            )

        with st.expander("¿Por qué aparecen focos en el desierto del norte (ej. Calama o Antofagasta) y qué límites tiene el satélite?"):
            st.markdown(
                "**1. Fuentes industriales estacionarias en el norte:**\n"
                "* Los sensores satelitales NASA FIRMS detectan cualquier punto de la superficie terrestre con temperatura anormalmente alta, sin distinguir si proviene de vegetación o de una instalación industrial.\n"
                "* En regiones como **Antofagasta o Atacama**, los puntos que se repiten casi todos los meses en el mismo lugar corresponden a **fundiciones de cobre (como Chuquicamata), plantas termosolares de concentración o faenas mineras**. Por eso la aplicación incluye la casilla superior para ocultarlos automáticamente.\n\n"
                "**2. Alcances y limitaciones del monitoreo satelital:**\n"
                "* **Para qué sirve:** Es una herramienta de **planificación preventiva y análisis histórico (2000–2026)** que permite saber qué meses son más peligrosos en cada comuna y priorizar cortafuegos.\n"
                "* **Qué no reemplaza:** Como los satélites pasan cada varias horas y las nubes muy densas pueden bloquear la visión infrarroja, un incendio recién iniciado puede tardar en aparecer en el satélite. Ante humo o fuego visible, **nunca esperes confirmación satelital: llama de inmediato al 130 (CONAF) o 132 (Bomberos)**."
            )
    else:
        with st.expander("How to prevent wildfires around homes, rural properties, and neighborhoods (Practical Guide)", expanded=True):
            st.markdown(
                "In Chile, over **99% of wildfires are caused by human activity**, with the highest danger occurring in the **wildland-urban interface** where homes border hills, forests, or dry grassland.\n\n"
                "**1. Build a defensible space around your home (before November):**\n"
                "* **Clear a 10 to 30 meter buffer:** Remove dry grass, fallen leaves, low-hanging tree branches, and dense brush around homes and fences.\n"
                "* **Clean roofs and gutters:** Wind-blown embers frequently ignite dry leaves accumulated on rooftops and rain gutters.\n"
                "* **Store flammables safely:** Keep firewood, gas cylinders, and fuels away from house walls.\n\n"
                "**2. Eliminate sparks and ignition sources:**\n"
                "* Avoid operating angle grinders, welders, or metal-blade brush cutters near dry vegetation during hot afternoons; keep water or a fire extinguisher nearby.\n"
                "* Never burn trash or agricultural waste outside legal **CONAF** burn windows, extinguish campfires completely with water and soil, and never discard cigarette butts or glass bottles outdoors.\n\n"
                "**3. Community coordination:**\n"
                "* Map clear evacuation routes and local water sources with neighbors, and use the side panel's pre-filled message to request municipal firebreak maintenance ahead of your commune's peak months."
            )

        with st.expander("What to do if you see smoke, fire, or receive an SAE evacuation alert?"):
            st.markdown(
                "* **Report immediately:** Call **130 (CONAF)**, **132 (Firefighters)**, or **133 (Carabineros)** with clear road/kilometer references.\n"
                "* **Evacuate immediately on SAE alerts:** Leave right away toward official SENAPRED safe zones without returning for belongings; keep an emergency kit ready (water, **N95/KN95** masks, medications, IDs, flashlight, pet carriers).\n"
                "* **Protect against smoke:** Close doors and windows with damp cloths along gaps, avoid outdoor exertion, and use **N95/KN95** masks to filter fine `PM2.5` smoke particles."
            )

        with st.expander("How to interpret Calibrated Hotspots, Fire Radiative Power (FRP), and map colors?"):
            st.markdown(
                "* **Calibrated Hotspots:** Counts active thermal detections across satellite overpasses, reflecting **spatial extent and duration**.\n"
                "* **Fire Radiative Power (FRP, in MW):** Measures instantaneous **radiative heat output**, capturing burning intensity.\n"
                "* **5 km & 10 km rings:** Select any hotspot on the map to display distance rings and evaluate proximity to populated areas."
            )

        with st.expander("Why does Valparaíso Feb 2024 have fewer total hotspot detections than Biobío 2023?"):
            st.markdown(
                "Polar-orbiting satellites pass 2–4 times per day. The Feb 2–3, 2024 Valparaíso megafire burned ~10,000 ha of dense urban-wildland interface in under 48 hours, whereas rural forestry megafires in Biobío/Maule burned >400,000 ha over several weeks. Switching to **Fire Intensity (FRP)** or inspecting **February 2024** shows it set Valparaíso's 26-year record."
            )

        with st.expander("Why do hotspots appear in the northern desert (e.g., Calama) and what are satellite limits?"):
            st.markdown(
                "NASA FIRMS detects all high-temperature surface anomalies, including copper smelters (such as Chuquicamata) and solar thermal plants in northern Chile. Because polar satellites pass every few hours and dense clouds can obscure thermal views, satellite data supports **prevention and historical planning**—always call **130** or **132** immediately if you spot smoke or fire."
            )

with tab_sat:
    if is_es:
        c_s1, c_s2 = st.columns(2)
        with c_s1:
            st.markdown(
                "**1. Satélites MODIS (2000–2011)**\n"
                "* **Instrumentos NASA:** Sensores a bordo de los satélites **Terra** y **Aqua**.\n"
                "* **Resolución:** Píxeles de **1 kilómetro**.\n"
                "* **Aporte:** Entregan la memoria histórica más extensa desde el año 2000, aunque por el tamaño de su píxel no detectan focos pequeños."
            )
        with c_s2:
            st.markdown(
                "**2. Satélites VIIRS (2012–2026)**\n"
                "* **Instrumentos NASA / NOAA:** Sensores a bordo de **Suomi-NPP**, **NOAA-20** y **NOAA-21**.\n"
                "* **Resolución:** Píxeles de **375 metros** (casi 7 veces mayor detalle espacial).\n"
                "* **Desafío:** Al tener mayor sensibilidad, comparar datos crudos de 2005 contra 2023 genera un salto artificial que este proyecto corrige."
            )
    else:
        st.markdown(
            "- **MODIS (Terra & Aqua, 2000–2011):** 1 km thermal resolution; provides the deep 26-year historical baseline.\n"
            "- **VIIRS (Suomi-NPP, NOAA-20/21, 2012–2026):** 375 m high-resolution thermal sensors; detects smaller fires.\n"
            "- **Why harmonize?** Combining raw counts creates an artificial jump in 2012; our calibration translates MODIS into VIIRS-equivalent units."
        )

with tab_how:
    if is_es:
        st.markdown(
            "El procesamiento de datos se realizó en **4 etapas**:\n"
            "1. **Desduplicación orbital:** Se filtraron las pasadas redundantes cuando dos satélites observan el mismo incendio con minutos de diferencia.\n"
            "2. **Geometría óptica del píxel (`scan × track`):** Se calculó el área real observada en tierra cuando el sensor mira hacia los bordes del barrido (donde el píxel se estira hasta 9.6 veces).\n"
            "3. **Calibración mediante aprendizaje automático:** Usando los **14 años de operación simultánea (2012–2026)**, se entrenó un modelo *Gradient Boosting* con corrección de Duan para traducir MODIS a escala VIIRS (`R² lineal = 0.887`, sesgo acumulado `< 5%` en validación ciega).\n"
            "4. **Geocodificación y accesibilidad:** Se integró el dataset calibrado con identificación territorial exacta por comuna/sector y accesibilidad visual y auditiva."
        )
    else:
        st.markdown(
            "1. **Orbital de-duplication:** Removes redundant detections from overlapping satellite passes.\n"
            "2. **Optical pixel geometry (`scan × track`):** Accounts for off-nadir pixel stretching up to 9.6 km².\n"
            "3. **Cross-sensor Machine Learning:** Trains Gradient Boosting with Duan's smearing on the 2012–2026 overlap (`Linear R² = 0.887`, `< 5%` blind hindcast bias).\n"
            "4. **Geocoding & accessibility:** Integrates exact local identification by commune/sector and visual/screen-reader accessibility."
        )