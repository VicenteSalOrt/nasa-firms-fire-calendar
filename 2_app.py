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

# Estilos globales responsivos (Desktop + Móvil) y tarjetas por pasos
st.markdown(
    """
    <style>
    .step-badge {
        display: inline-block;
        background: linear-gradient(90deg, #D7301F 0%, #FC8D59 100%);
        color: #FFFFFF !important;
        font-weight: 800;
        font-size: 0.80rem;
        letter-spacing: 0.06em;
        padding: 4px 12px;
        border-radius: 999px;
        margin-bottom: 6px;
        text-transform: uppercase;
    }
    .step-badge-blue {
        display: inline-block;
        background: linear-gradient(90deg, #1f6feb 0%, #388bfd 100%);
        color: #FFFFFF !important;
        font-weight: 800;
        font-size: 0.80rem;
        letter-spacing: 0.06em;
        padding: 4px 12px;
        border-radius: 999px;
        margin-bottom: 6px;
        text-transform: uppercase;
    }
    .step-title {
        font-size: 1.28rem;
        font-weight: 700;
        margin: 2px 0 8px 0;
        line-height: 1.25;
    }

    /* Bloque de Bienvenida y Propuesta de Valor (Función + 3 Audiencias) */
    .hero-purpose-box {
        border-radius: 14px;
        padding: 14px 16px;
        background: linear-gradient(135deg, rgba(215,48,31,0.10) 0%, rgba(31,111,235,0.10) 100%);
        border: 1.5px solid rgba(255,107,53,0.40);
        margin: 4px 0 10px 0;
    }
    .hero-purpose-title {
        font-size: 1.02rem;
        font-weight: 800;
        margin-bottom: 4px;
    }
    .hero-purpose-desc {
        font-size: 0.91rem;
        line-height: 1.42;
        opacity: 0.94;
        margin-bottom: 10px;
    }
    .audience-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
    }
    .audience-card {
        border-radius: 11px;
        padding: 11px 12px;
        background: rgba(128, 140, 165, 0.10);
        border: 1px solid rgba(128, 140, 165, 0.28);
    }
    .audience-card-title {
        font-weight: 800;
        font-size: 0.93rem;
        margin-bottom: 4px;
    }
    .audience-card-text {
        font-size: 0.84rem;
        line-height: 1.36;
        opacity: 0.90;
    }

    /* Barra de flujo de 5 pasos responsiva (Desktop: 5 cols, Móvil: 2 cols) */
    .stepper-grid {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 8px;
        margin: 6px 0 12px 0;
    }
    .stepper-card {
        border-radius: 12px;
        padding: 10px 10px;
        background: linear-gradient(135deg, rgba(215,48,31,0.12) 0%, rgba(31,111,235,0.10) 100%);
        border: 1px solid rgba(255,107,53,0.45);
        display: flex;
        align-items: center;
        gap: 9px;
    }
    .stepper-num {
        min-width: 26px;
        height: 26px;
        border-radius: 50%;
        color: #FFFFFF;
        font-weight: 800;
        font-size: 0.85rem;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    .stepper-text-title {
        font-weight: 700;
        font-size: 0.88rem;
        line-height: 1.15;
    }
    .stepper-text-sub {
        font-size: 0.76rem;
        opacity: 0.82;
        line-height: 1.15;
        margin-top: 2px;
    }

    /* Leyenda visual responsiva del calendario */
    .cal-legend-bar {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 10px 16px;
        padding: 8px 12px;
        border-radius: 10px;
        background: rgba(130, 145, 175, 0.12);
        font-size: 0.86rem;
        margin: 4px 0 8px 0;
    }
    .cal-legend-item {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-weight: 500;
    }
    .cal-swatch {
        width: 14px;
        height: 14px;
        border-radius: 3px;
        border: 1px solid rgba(128,128,128,0.5);
        display: inline-block;
    }
    .cal-frame-swatch {
        width: 18px;
        height: 13px;
        border-radius: 3px;
        border: 2.5px solid #00B4D8;
        display: inline-block;
    }

    /* Tarjeta destacada de Correo */
    .mail-highlight-box {
        border: 2.5px solid #FF6B35;
        border-radius: 14px;
        padding: 14px;
        background: linear-gradient(180deg, rgba(255,107,53,0.15) 0%, rgba(255,107,53,0.04) 100%);
        margin-bottom: 10px;
        box-shadow: 0 4px 16px rgba(255,107,53,0.14);
    }
    .mail-sector-pill {
        display: inline-block;
        background: rgba(255, 107, 53, 0.20);
        border: 1px solid rgba(255, 107, 53, 0.55);
        border-radius: 8px;
        padding: 4px 9px;
        font-size: 0.83rem;
        font-weight: 700;
        margin: 6px 0 6px 0;
        word-break: break-word;
    }
    .mail-cta-btn {
        display: block;
        width: 100%;
        text-align: center;
        background: linear-gradient(90deg, #D7301F 0%, #FF6B35 100%);
        color: #FFFFFF !important;
        font-weight: 800;
        font-size: 0.98rem;
        padding: 12px 14px;
        border-radius: 10px;
        text-decoration: none !important;
        margin: 10px 0 4px 0;
        box-shadow: 0 4px 12px rgba(215,48,31,0.30);
    }
    .mail-cta-btn:hover {
        opacity: 0.93;
    }

    /* Grid responsivo de 4 tarjetas visuales de prevención */
    .prev-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 10px;
        margin: 6px 0 14px 0;
    }
    .prev-card {
        border-radius: 12px;
        padding: 12px;
        display: flex;
        flex-direction: column;
        gap: 6px;
    }
    .prev-card-head {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 700;
        font-size: 0.94rem;
        line-height: 1.2;
    }
    .prev-card-body {
        font-size: 0.85rem;
        opacity: 0.9;
        line-height: 1.35;
    }

    /* Ajustes específicos para pantallas de celular (<= 768px) */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.65rem !important;
            padding-right: 0.65rem !important;
            padding-top: 1.2rem !important;
        }
        h1 {
            font-size: 1.48rem !important;
            line-height: 1.2 !important;
        }
        .step-title {
            font-size: 1.12rem !important;
        }
        .audience-grid {
            grid-template-columns: repeat(1, minmax(0, 1fr));
            gap: 8px;
        }
        .stepper-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 6px;
        }
        .stepper-card {
            padding: 8px;
        }
        .prev-grid {
            grid-template-columns: repeat(1, minmax(0, 1fr));
            gap: 8px;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.35rem !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.82rem !important;
        }
        .stRadio > div {
            gap: 0.35rem !important;
            flex-wrap: wrap !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

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

# 5. Cabecera Compacta y Accesible (Optimizada para Desktop y Celular)
head_title, head_opts = st.columns([2.1, 1.9])

with head_opts:
    opt_c1, opt_c2, opt_c3 = st.columns([1.05, 1.25, 1.05])
    with opt_c1:
        lang = st.radio(
            "Idioma / Lang",
            ["English", "Español"],
            format_func=lambda k: "EN" if k == "English" else "ES",
            horizontal=True
        )
    is_es = (lang == "Español")

    with opt_c2:
        palette_mode = st.radio(
            "Colores" if is_es else "Colors",
            ["standard", "colorblind"],
            format_func=lambda k: (
                ("Normal" if is_es else "Standard")
                if k == "standard" else
                ("Daltonismo" if is_es else "Colorblind")
            ),
            horizontal=True
        )

    with opt_c3:
        large_text_mode = st.radio(
            "Letra" if is_es else "Text",
            ["normal", "large"],
            format_func=lambda k: (
                ("Normal" if is_es else "Normal")
                if k == "normal" else
                ("Grande" if is_es else "Large")
            ),
            horizontal=True
        )

is_large = (large_text_mode == "large")
chart_font_size = 14 if is_large else 11

if is_large:
    st.markdown(
        """
        <style>
        html, body, [class*="css"] { font-size: 18.5px !important; }
        p, li, label, .stMarkdown, .stRadio label, .stSelectbox label { font-size: 1.10rem !important; line-height: 1.48 !important; }
        [data-testid="stMetricValue"] { font-size: 1.95rem !important; }
        </style>
        """,
        unsafe_allow_html=True
    )

color_scale = "YlOrRd" if palette_mode == "standard" else "Cividis"
accent_line_color = "#D7301F" if palette_mode == "standard" else "#FDE725"

with head_title:
    st.title(
        "Calendario Satelital de Incendios en Chile"
        if is_es else
        "Harmonized Wildfire Activity Calendar"
    )
    st.caption(
        "26 años de datos satelitales NASA calibrados (2000–2026) · Inteligencia abierta para prevenir incendios en las 16 regiones de Chile."
        if is_es else
        "26 years of calibrated NASA satellite data (2000–2026) · Open wildfire intelligence across all 16 regions of Chile."
    )

# 6. Propósito de la Plataforma y Cómo Ayuda a Personas, Municipalidades y Científicos
if is_es:
    st.markdown(
        """
        <div class="hero-purpose-box">
            <div class="hero-purpose-title">🛰️ ¿Cuál es la función de esta plataforma?</div>
            <div class="hero-purpose-desc">
                Unifica y calibra mediante Machine Learning <b>26 años de detecciones térmicas de satélites NASA (MODIS + VIIRS, 2000–2026)</b>
                en todo Chile, eliminando el salto artificial entre sensores para identificar exactamente <b>cuándo y dónde</b> se concentran los incendios y transformar esa evidencia en prevención territorial.
            </div>
            <div class="audience-grid">
                <div class="audience-card">
                    <div class="audience-card-title">👥 Para Personas y Comunidades</div>
                    <div class="audience-card-text">
                        Muestra los <b>3 meses más críticos</b> de tu sector, ofrece diagnóstico con <b>audio y lectura accesible</b>, y redacta en <b>1 clic un correo oficial</b> para exigir cortafuegos a CONAF, SENAPRED y tu municipio.
                    </div>
                </div>
                <div class="audience-card">
                    <div class="audience-card-title">🏛️ Para Municipalidades y Emergencias</div>
                    <div class="audience-card-text">
                        Ubica los puntos de mayor recurrencia histórica con <b>anillos de proximidad de 5 y 10 km</b> y permite descargar <b>tablas georreferenciadas (CSV)</b> listas para planificar cortafuegos en <b>QGIS</b>.
                    </div>
                </div>
                <div class="audience-card">
                    <div class="audience-card-title">🔬 Para Científicos e Investigadores</div>
                    <div class="audience-card-text">
                        Entrega series temporales armonizadas sin sesgo instrumental (<b>R² = 0.887</b>), <b>bandas de normalidad (P25–P75)</b>, potencia radiativa (<b>FRP en MW</b>) y descarga directa de celdas calibradas.
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <div class="hero-purpose-box">
            <div class="hero-purpose-title">🛰️ What does this platform do?</div>
            <div class="hero-purpose-desc">
                It harmonizes <b>26 years of NASA thermal satellite detections (MODIS + VIIRS, 2000–2026)</b> across all 16 regions of Chile
                using Machine Learning—removing artificial sensor jumps to pinpoint <b>when and where</b> wildfires concentrate and turning satellite data into preventive action.
            </div>
            <div class="audience-grid">
                <div class="audience-card">
                    <div class="audience-card-title">👥 For Citizens & Communities</div>
                    <div class="audience-card-text">
                        Reveals your neighborhood's <b>top 3 peak fire months</b>, provides <b>audio & accessible summaries</b>, and drafts a <b>1-click email</b> to request firebreaks from CONAF, SENAPRED, and local municipalities.
                    </div>
                </div>
                <div class="audience-card">
                    <div class="audience-card-title">🏛️ For Municipalities & Planners</div>
                    <div class="audience-card-text">
                        Pinpoints recurring wildfire hotspots with <b>5 km & 10 km proximity rings</b> and exports <b>georeferenced CSV datasets</b> ready for firebreak planning in <b>QGIS</b>.
                    </div>
                </div>
                <div class="audience-card">
                    <div class="audience-card-title">🔬 For Scientists & Researchers</div>
                    <div class="audience-card-text">
                        Provides bias-corrected multi-sensor time series (<b>R² = 0.887</b>), <b>26-year confidence bands (P25–P75)</b>, Fire Radiative Power (<b>FRP in MW</b>), and downloadable calibrated cells.
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# 7. Mapa Visual de Avance HTML/CSS Responsivo (Desktop 5-col / Celular 2-col)
s_items = (
    [
        ("1", "#D7301F", "Región y Perfil", "Zona y nivel"),
        ("2", "#E6550D", "Año y Meses", "Período a ver"),
        ("3", "#D95F0E", "Calendario", "Meses críticos"),
        ("4", "#FF6B35", "Mapa y Correo", "Sectores y aviso"),
        ("5", "#1f6feb", "Prevención", "Guía rápida"),
    ]
    if is_es else
    [
        ("1", "#D7301F", "Region & View", "Area & detail"),
        ("2", "#E6550D", "Year & Months", "Timeframe"),
        ("3", "#D95F0E", "Calendar", "Peak months"),
        ("4", "#FF6B35", "Map & Email", "Sectors & alert"),
        ("5", "#1f6feb", "Prevention", "Quick guide"),
    ]
)

stepper_html = '<div class="stepper-grid">' + "".join([
    f'<div class="stepper-card">'
    f'<div class="stepper-num" style="background:{bg};">{num}</div>'
    f'<div><div class="stepper-text-title">{title}</div><div class="stepper-text-sub">{sub}</div></div>'
    f'</div>'
    for num, bg, title, sub in s_items
]) + '</div>'
st.markdown(stepper_html, unsafe_allow_html=True)

# ==============================================================================
# PASO 1: TERRITORIO Y PERFIL DE LECTURA
# ==============================================================================
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

with st.container(border=True):
    st.markdown(
        f'<span class="step-badge">{"Paso 1 de 5" if is_es else "Step 1 of 5"}</span>'
        f'<div class="step-title">{"Configura tu Territorio y Nivel de Detalle" if is_es else "Configure Territory & Detail Level"}</div>',
        unsafe_allow_html=True
    )

    step1_col, step2_col = st.columns([1.2, 1.8])
    with step1_col:
        preset = st.selectbox(
            "Territorio o región:" if is_es else "Territory or region:",
            preset_keys,
            index=preset_keys.index("Biobío"),
            format_func=lambda k: preset_labels[k]
        )

    with step2_col:
        audience = st.radio(
            "Perfil de lectura:" if is_es else "View profile:",
            ["citizen", "municipal", "scientist"],
            format_func=lambda k: {
                "citizen": "Ciudadanía (Simple)" if is_es else "Citizens (Simple)",
                "municipal": "Municipios (QGIS)" if is_es else "Municipalities (QGIS)",
                "scientist": "Investigadores (Datos)" if is_es else "Researchers (Data)",
            }[k],
            horizontal=True
        )

    if preset not in REGIONS_BOUNDS:
        c_lat1, c_lat2, c_lon1, c_lon2 = st.columns(4)
        lat_min = c_lat1.number_input("Latitud Mínima" if is_es else "Min Latitude", value=-38.5, format="%.2f")
        lat_max = c_lat2.number_input("Latitud Máxima" if is_es else "Max Latitude", value=-36.0, format="%.2f")
        lon_min = c_lon1.number_input("Longitud Mínima" if is_es else "Min Longitude", value=-73.8, format="%.2f")
        lon_max = c_lon2.number_input("Longitud Máxima" if is_es else "Max Longitude", value=-71.0, format="%.2f")
    else:
        lat_min, lat_max, lon_min, lon_max = REGIONS_BOUNDS[preset]

    opt_col1, opt_col2 = st.columns([1.5, 1.5])
    with opt_col1:
        metric_key = st.radio(
            "¿Qué medir?" if is_es else "Metric:",
            ["hotspots", "frp"],
            format_func=lambda k: (
                ("Focos Calibrados" if is_es else "Calibrated Hotspots")
                if k == "hotspots" else
                ("Potencia Térmica (FRP - MW)" if is_es else "Radiative Power (FRP - MW)")
            ),
            horizontal=True
        )
        value_col = "harmonized_hotspots" if metric_key == "hotspots" else "harmonized_frp"
        unit_label = ("Focos" if is_es else "Hotspots") if metric_key == "hotspots" else "MW"

    with opt_col2:
        exclude_industrial = st.checkbox(
            "Ocultar fundiciones y plantas solares fijas del norte"
            if is_es else
            "Hide persistent northern smelters & solar plants",
            value=(audience != "scientist")
        )

# Filtrado Espacial
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
        "No se registraron focos de calor en la zona seleccionada."
        if is_es else
        "No fire hotspots detected in the selected area."
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

if st.session_state.get("last_preset_tracker") != preset:
    st.session_state["last_preset_tracker"] = preset
    st.session_state["selected_year_state"] = worst_yr

if "selected_year_state" not in st.session_state or st.session_state["selected_year_state"] not in years_available:
    st.session_state["selected_year_state"] = worst_yr

def set_year_cb(new_yr):
    st.session_state["selected_year_state"] = int(new_yr)

# ==============================================================================
# PASO 2: AÑO Y RANGO DE MESES
# ==============================================================================
with st.container(border=True):
    st.markdown(
        f'<span class="step-badge">{"Paso 2 de 5" if is_es else "Step 2 of 5"}</span>'
        f'<div class="step-title">{"Elige el Año y los Meses a Revisar" if is_es else "Select Year & Months to Inspect"}</div>',
        unsafe_allow_html=True
    )

    q1, q2, q3 = st.columns(3)
    q1.button(
        "Año actual (2026)" if is_es else "Current year (2026)",
        on_click=set_year_cb,
        args=(int(max(years_available)),),
        width='stretch'
    )
    q2.button(
        f"Peor año ({worst_yr})" if is_es else f"Worst year ({worst_yr})",
        on_click=set_year_cb,
        args=(worst_yr,),
        width='stretch'
    )
    calm_yr = 2016 if 2016 in years_available else int(min(years_available))
    q3.button(
        f"Año tranquilo ({calm_yr})" if is_es else f"Calm year ({calm_yr})",
        on_click=set_year_cb,
        args=(calm_yr,),
        width='stretch'
    )

    yr_col, period_mode_col = st.columns([1.2, 1.8])
    with yr_col:
        selected_year = st.selectbox("Año:" if is_es else "Year:", options=years_desc, key="selected_year_state")

    with period_mode_col:
        period_preset = st.selectbox(
            "Período dentro del año:" if is_es else "Period within year:",
            options=["full_year", "q1_summer", "q2_autumn", "q3_winter", "q4_spring", "s1", "s2", "single_month", "custom_range"],
            format_func=lambda k: {
                "full_year": "Todo el Año (Ene – Dic)" if is_es else "Full Year (Jan – Dec)",
                "q1_summer": "1er Trimestre · Verano (Ene – Mar)" if is_es else "Q1 · Summer (Jan – Mar)",
                "q2_autumn": "2do Trimestre · Otoño (Abr – Jun)" if is_es else "Q2 · Autumn (Apr – Jun)",
                "q3_winter": "3er Trimestre · Invierno (Jul – Sep)" if is_es else "Q3 · Winter (Jul – Sep)",
                "q4_spring": "4to Trimestre · Primavera (Oct – Dic)" if is_es else "Q4 · Spring (Oct – Dec)",
                "s1": "1er Semestre (Ene – Jun)" if is_es else "1st Semester (Jan – Jun)",
                "s2": "2do Semestre (Jul – Dic)" if is_es else "2nd Semester (Jul – Dic)",
                "single_month": "Un mes específico" if is_es else "Single specific month",
                "custom_range": "Rango de meses (Desde – Hasta)" if is_es else "Custom month range (From – To)",
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
            "Mes:" if is_es else "Month:",
            options=list(range(1, 13)),
            index=1 if (preset == "Valparaíso" and selected_year == 2024) else 0,
            format_func=lambda m: month_full_names[m - 1]
        )
        m_start, m_end = m_single, m_single
    else:
        rc1, rc2 = st.columns(2)
        with rc1:
            m_start = st.selectbox("Desde:" if is_es else "From:", options=list(range(1, 13)), index=0, format_func=lambda m: month_full_names[m - 1])
        with rc2:
            m_end = st.selectbox("Hasta:" if is_es else "To:", options=list(range(1, 13)), index=2, format_func=lambda m: month_full_names[m - 1])
        if m_end < m_start:
            m_start, m_end = m_end, m_start

selected_months = list(range(m_start, m_end + 1))
is_full_year = (m_start == 1 and m_end == 12)

if is_full_year:
    effective_months = list(range(1, 12)) if selected_year == 2026 else list(range(1, 13))
    period_title = f"{selected_year} (Ene–Nov)" if (selected_year == 2026 and is_es) else (f"{selected_year} (Jan–Nov YTD)" if selected_year == 2026 else f"{selected_year}")
    median_label = (
        ("Lo normal Ene–Nov" if is_es else "Typical Jan–Nov") if selected_year == 2026 else ("Lo normal en un año" if is_es else "Typical Year")
    ) if audience == "citizen" else (
        ("Mediana Ene–Nov" if is_es else "Jan–Nov Median") if selected_year == 2026 else ("Mediana Anual" if is_es else "Annual Median")
    )
else:
    effective_months = [m for m in selected_months if not (selected_year == 2026 and m > 11)]
    if not effective_months:
        effective_months = selected_months
    range_label = month_names[m_start - 1] if m_start == m_end else f"{month_names[m_start - 1]} – {month_names[m_end - 1]}"
    period_title = f"{range_label} {selected_year}"
    median_label = (
        (f"Lo normal ({range_label})" if is_es else f"Typical ({range_label})")
        if audience == "citizen" else
        (f"Mediana ({range_label})" if is_es else f"Median ({range_label})")
    )

range_by_year = monthly_totals[monthly_totals['month'].isin(effective_months)].groupby('year')[value_col].sum()
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

# ==============================================================================
# PASO 3: RESULTADOS, DIAGNÓSTICO Y CALENDARIO HISTÓRICO (2026 ARRIBA -> 2000 ABAJO)
# ==============================================================================
with st.container(border=True):
    st.markdown(
        f'<span class="step-badge">{"Paso 3 de 5" if is_es else "Step 3 of 5"}</span>'
        f'<div class="step-title">{"Diagnóstico y Calendario Histórico" if is_es else "Diagnosis & Historical Calendar"} — {region_display} ({period_title})</div>',
        unsafe_allow_html=True
    )

    if median_baseline > 0:
        ratio = total_selected / median_baseline
        pct_diff = (ratio - 1.0) * 100
        anomaly_str = f"{ratio:.1f}x {'lo normal' if is_es else 'normal'}" if audience == "citizen" else f"{pct_diff:+.1f}%"

        if ratio >= 2.0:
            diag_plain = (
                f"Nivel crítico extremo en {region_display} durante {period_title}. "
                f"{total_selected:,.0f} {unit_label.lower()}, {ratio:.1f} veces lo normal. "
                f"El {top3_share:.0f} por ciento ocurre entre {top3_names}."
                if is_es else
                f"Extreme critical level in {region_display} during {period_title}: {ratio:.1f}x normal."
            )
            st.error(
                f"**NIVEL CRÍTICO EXTREMO ({ratio:.1f}x lo normal):** "
                f"En **{region_display}**, el **{top3_share:.0f}%** de los incendios ocurre entre **{top3_names}**."
                if is_es else
                f"**EXTREME CRITICAL LEVEL ({ratio:.1f}x normal):** "
                f"In **{region_display}**, **{top3_share:.0f}%** of fire activity concentrates in **{top3_names}**."
            )
        elif ratio >= 1.25:
            diag_plain = f"Actividad sobre lo normal en {region_display} ({period_title}): {pct_diff:+.0f}%."
            st.warning(
                f"**SOBRE LO NORMAL ({pct_diff:+.1f}%):** Meses críticos en la zona: **{top3_names}** (**{top3_share:.0f}%**)."
                if is_es else
                f"**ABOVE NORMAL ({pct_diff:+.1f}%):** Peak months here: **{top3_names}** (**{top3_share:.0f}%**)."
            )
        elif ratio >= 0.75:
            diag_plain = f"Nivel normal en {region_display} ({period_title})."
            st.success(
                f"**NIVEL NORMAL ({pct_diff:+.1f}%):** Temporada crítica habitual: **{top3_names}**."
                if is_es else
                f"**NORMAL LEVEL ({pct_diff:+.1f}%):** Usual peak season: **{top3_names}**."
            )
        else:
            diag_plain = f"Actividad bajo lo normal en {region_display} ({period_title})."
            st.info(
                f"**BAJO LO NORMAL ({abs(pct_diff):.1f}% menos):** Temporada crítica habitual: **{top3_names}**."
                if is_es else
                f"**BELOW NORMAL ({abs(pct_diff):.1f}% lower):** Usual peak season: **{top3_names}**."
            )
    else:
        if total_selected > 0:
            anomaly_str = "Inusual" if is_es else "Off-season"
            diag_plain = f"Fuego fuera de temporada en {region_display}: {total_selected:,.0f} {unit_label.lower()}."
            st.warning(f"**FUEGO FUERA DE TEMPORADA:** {total_selected:,.0f} {unit_label.lower()} detectados." if is_es else f"**OFF-SEASON FIRE:** {total_selected:,.0f} {unit_label.lower()} detected.")
        else:
            anomaly_str = "Normal (0)"
            diag_plain = f"Sin incendios detectados en {region_display} durante {period_title}."
            st.success("**SIN INCENDIOS DETECTADOS** en este período." if is_es else "**NO FIRES DETECTED** in this period.")

    if preset == "Valparaíso" and selected_year == 2024 and is_es:
        st.caption(
            "Nota Valparaíso Feb 2024: Megaincendio urbano-forestal ultra-rápido (<48 h, ~10.000 ha); marca el récord histórico regional de 26 años."
        )

    safe_speech_text = json.dumps(diag_plain)
    speech_lang = "es-CL" if is_es else "en-US"
    components.html(
        f"""
        <div style="display:flex; gap:8px; align-items:center; font-family: sans-serif;">
            <button onclick='
                window.speechSynthesis.cancel();
                const u = new SpeechSynthesisUtterance({safe_speech_text});
                u.lang = "{speech_lang}";
                u.rate = 0.96;
                window.speechSynthesis.speak(u);
            ' style="background:#1f6feb; color:white; border:none; border-radius:8px; padding:6px 14px; font-size:14px; font-weight:600; cursor:pointer;">
                🔊 {"Escuchar resumen" if is_es else "Listen summary"}
            </button>
            <button onclick='window.speechSynthesis.cancel();'
                style="background:#444; color:white; border:none; border-radius:8px; padding:6px 10px; font-size:13px; cursor:pointer;">
                ⏹ {"Detener" if is_es else "Stop"}
            </button>
        </div>
        """,
        height=40
    )

    frp_selected = float(
        df_filtered[(df_filtered['year'] == selected_year) & (df_filtered['month'].isin(effective_months))]['harmonized_frp'].sum()
    )

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric(
        f"{'Total en' if is_es else 'Total in'} {period_title}",
        f"{total_selected:,.0f} {unit_label}",
        delta=(f"Potencia: {frp_selected:,.0f} MW" if (metric_key == "hotspots" and is_es) else None),
        delta_color="off"
    )
    kpi2.metric(median_label, f"{median_baseline:,.0f} {unit_label}")
    kpi3.metric("Comparación" if is_es else "Comparison", anomaly_str)
    if is_full_year:
        kpi4.metric("Meses críticos" if is_es else "Peak window", f"{top3_share:.0f}% ({top3_names})")
    else:
        kpi4.metric(
            f"% {'del año' if is_es else 'of'} {selected_year}",
            f"{share_of_year_pct:.1f}%",
            delta=(f"Histórico: {hist_share_pct:.1f}%" if is_es else f"Hist avg: {hist_share_pct:.1f}%"),
            delta_color="off"
        )

    # Leyenda visual responsiva HTML/CSS
    swatch_colors = ("#FFFFCC", "#FD8D3C", "#B10026") if palette_mode == "standard" else ("#00224E", "#7C7B78", "#FEE838")
    g_txt = (
        ("↔ Fila = Año", "↕ Columna = Mes", "Calma", "Moderado", "Crítico", f"Marco celeste = {selected_year}")
        if is_es else
        ("↔ Row = Year", "↕ Column = Month", "Calm", "Moderate", "Critical", f"Blue frame = {selected_year}")
    )
    st.markdown(
        f"""
        <div class="cal-legend-bar">
            <span class="cal-legend-item"><b>{g_txt[0]}</b></span>
            <span class="cal-legend-item"><b>{g_txt[1]}</b></span>
            <span class="cal-legend-item"><span class="cal-swatch" style="background:{swatch_colors[0]};"></span>{g_txt[2]}</span>
            <span class="cal-legend-item"><span class="cal-swatch" style="background:{swatch_colors[1]};"></span>{g_txt[3]}</span>
            <span class="cal-legend-item"><span class="cal-swatch" style="background:{swatch_colors[2]};"></span>{g_txt[4]}</span>
            <span class="cal-legend-item"><span class="cal-frame-swatch"></span><b>{g_txt[5]}</b></span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Matriz ordenada: 2026 arriba -> 2000 abajo (índices discretos para evitar rangos 0..2026)
    calendar_pivot = (
        monthly_totals.pivot(index='year', columns='month', values=value_col)
        .reindex(columns=range(1, 13))
        .sort_index(ascending=False)
    )
    max_monthly_all_time = max(float(monthly_totals[value_col].max()), 1.0)
    plotly_mobile_cfg = {"displayModeBar": False, "responsive": True}

    def build_enhanced_calendar(height_px):
        years_list = [int(y) for y in calendar_pivot.index]
        y_idx = list(range(len(years_list)))
        y_lbl = [str(y) for y in years_list]
        z_vals = calendar_pivot.to_numpy()
        custom_yr = np.array([[lbl] * 12 for lbl in y_lbl])

        fig_c = go.Figure(
            data=go.Heatmap(
                z=z_vals,
                x=month_names,
                y=y_idx,
                customdata=custom_yr,
                colorscale=color_scale,
                xgap=2,
                ygap=2,
                colorbar=dict(thickness=12, len=0.88, title=unit_label),
                hovertemplate=(
                    f"<b>%{{customdata}} · %{{x}}</b><br>{unit_label}: <b>%{{z:,.1f}}</b><extra></extra>"
                )
            )
        )

        if selected_year in years_list:
            yr_pos = years_list.index(selected_year)
            fig_c.add_shape(
                type="rect",
                x0=-0.5,
                x1=11.5,
                y0=yr_pos - 0.5,
                y1=yr_pos + 0.5,
                line=dict(color="#00B4D8", width=2.8),
                fillcolor="rgba(0,0,0,0)"
            )

        fig_c.update_layout(
            height=height_px,
            margin=dict(l=4, r=4, t=28, b=4),
            font=dict(size=chart_font_size),
            xaxis=dict(side="top", showgrid=False, zeroline=False),
            yaxis=dict(
                title="Año" if is_es else "Year",
                tickmode="array",
                tickvals=y_idx,
                ticktext=y_lbl,
                range=[len(y_idx) - 0.5, -0.5],
                showgrid=False,
                zeroline=False
            )
        )
        return fig_c

    if audience == "citizen":
        st.plotly_chart(build_enhanced_calendar(500), width='stretch', config=plotly_mobile_cfg)
    else:
        col_cal, col_curve = st.columns([1.35, 1])
        with col_cal:
            st.plotly_chart(build_enhanced_calendar(500), width='stretch', config=plotly_mobile_cfg)

        with col_curve:
            stats_monthly = monthly_totals.groupby('month')[value_col].agg(
                median='median',
                p25=lambda x: x.quantile(0.25),
                p75=lambda x: x.quantile(0.75)
            ).reset_index()
            year_curve = monthly_totals[monthly_totals['year'] == selected_year].sort_values('month').reset_index(drop=True)

            fig_curve = go.Figure()
            fig_curve.add_trace(go.Scatter(
                x=month_names + month_names[::-1],
                y=list(stats_monthly['p75']) + list(stats_monthly['p25'])[::-1],
                fill='toself',
                fillcolor='rgba(100, 149, 237, 0.22)',
                line=dict(color='rgba(255,255,255,0)'),
                name="Normal (P25–P75)",
                hoverinfo="skip"
            ))
            fig_curve.add_trace(go.Scatter(
                x=month_names,
                y=stats_monthly['median'],
                mode='lines',
                line=dict(color='#6495ED', dash='dash', width=2.2),
                name="Mediana 26a" if is_es else "26-Yr Median"
            ))
            fig_curve.add_trace(go.Scatter(
                x=month_names,
                y=year_curve[value_col],
                mode='lines+markers',
                line=dict(color=accent_line_color, width=3.2),
                marker=dict(size=7, line=dict(width=1.5, color="#FFFFFF")),
                name=f"{selected_year}"
            ))

            valid_curve = year_curve.dropna(subset=[value_col])
            if not valid_curve.empty and valid_curve[value_col].max() > 0:
                peak_row = valid_curve.loc[valid_curve[value_col].idxmax()]
                peak_m_idx = int(peak_row['month']) - 1
                fig_curve.add_annotation(
                    x=month_names[peak_m_idx],
                    y=float(peak_row[value_col]),
                    text=f"<b>{peak_row[value_col]:,.0f}</b>",
                    showarrow=True,
                    arrowhead=2,
                    ay=-24,
                    font=dict(size=12, color=accent_line_color)
                )

            fig_curve.update_layout(
                height=500,
                margin=dict(l=4, r=4, t=36, b=4),
                font=dict(size=chart_font_size),
                hovermode="x unified",
                yaxis=dict(title=unit_label, range=[0, max_monthly_all_time * 1.12], gridcolor="rgba(150,150,150,0.18)"),
                xaxis=dict(gridcolor="rgba(150,150,150,0.12)"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_curve, width='stretch', config=plotly_mobile_cfg)

        if audience == "scientist":
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
                annotation_text="VIIRS 2012",
                annotation_position="top right"
            )
            fig_trend.update_layout(
                height=265,
                margin=dict(l=4, r=4, t=25, b=4),
                font=dict(size=chart_font_size),
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_trend, width='stretch', config=plotly_mobile_cfg)

    with st.expander("Tabla accesible (Lectores de pantalla)" if is_es else "Accessible table (Screen readers)"):
        acc_df = pd.DataFrame({
            "Mes / Month": month_full_names,
            f"{selected_year} ({unit_label})": [
                round(float(monthly_totals[(monthly_totals['year'] == selected_year) & (monthly_totals['month'] == m)][value_col].sum()), 1)
                for m in range(1, 13)
            ],
            f"{'Mediana' if is_es else 'Median'} ({unit_label})": [
                round(float(hist_complete[hist_complete['month'] == m][value_col].median()), 1)
                for m in range(1, 13)
            ],
            "% Histórico": [
                round(float(month_totals_hist.loc[m] / month_totals_hist.sum() * 100), 1) if month_totals_hist.sum() > 0 else 0.0
                for m in range(1, 13)
            ]
        })
        st.dataframe(acc_df, hide_index=True, width='stretch')

# ==============================================================================
# PASO 4: MAPA SATELITAL Y ACCIÓN / CORREO DESTACADO (Bilingüe Completo)
# ==============================================================================
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

with st.container(border=True):
    st.markdown(
        f'<span class="step-badge">{"Paso 4 de 5" if is_es else "Step 4 of 5"}</span>'
        f'<div class="step-title">{"Mapa Satelital, Sectores Críticos y Envío de Correo" if is_es else "Satellite Map, Affected Sectors & Email Alert"} — {period_title}</div>',
        unsafe_allow_html=True
    )

    col_map, col_side = st.columns([2.05, 1.15])

    with col_map:
        m_ctrl1, m_ctrl2 = st.columns(2)
        with m_ctrl1:
            map_scope_mode = st.radio(
                "Datos del mapa:" if is_es else "Map scope:",
                ["selected", "all_26y"],
                format_func=lambda k: ("Período elegido" if is_es else "Selected period") if k == "selected" else ("26 Años (2000–26)" if is_es else "26 Years (2000–26)"),
                horizontal=True
            )
            res_mode = st.radio(
                "Escala espacial:" if is_es else "Spatial scale:",
                ["fine", "commune", "macro"],
                format_func=lambda k: {"fine": "Detalle" if is_es else "Fine", "commune": "Comunal" if is_es else "Commune", "macro": "Regional" if is_es else "Regional"}[k],
                horizontal=True
            )
        with m_ctrl2:
            viz_mode = st.radio(
                "Visualización:" if is_es else "Layer:",
                ["bubbles", "heatmap", "grid"],
                format_func=lambda k: {"bubbles": "Círculos" if is_es else "Circles", "heatmap": "Calor" if is_es else "Heat", "grid": "Celdas" if is_es else "Grid"}[k],
                horizontal=True
            )
            map_style_choice = st.radio(
                "Mapa base:" if is_es else "Base map:",
                ["satellite", "osm", "dark"],
                format_func=lambda k: {"satellite": "Satélite" if is_es else "Satellite", "osm": "Calles" if is_es else "Streets", "dark": "Oscuro" if is_es else "Dark"}[k],
                horizontal=True
            )

        df_active_map_df = df_map_source if map_scope_mode == "selected" else df_filtered
        map_scope_label = period_title if map_scope_mode == "selected" else "2000–2026"

        if df_active_map_df.empty:
            st.info(
                "Sin focos en este período. Cambia 'Datos del mapa' a '26 Años' para ver el acumulado histórico."
                if is_es else
                "No hotspots in this period. Switch 'Map scope' to '26 Years' for cumulative history."
            )
            map_agg = pd.DataFrame()
            selected_idx = -1
            exact_zone_display = ""
            exact_comuna_name = ""
        else:
            res_step_map = {"fine": native_res, "commune": max(native_res, 0.10), "macro": max(native_res, 0.20)}
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
                f"Enfocar sector ({map_scope_label}) o toca un punto en el mapa:"
                if is_es else
                f"Focus sector ({map_scope_label}) or tap a point on the map:",
                options=inspect_options,
                format_func=lambda idx: (
                    ("— Vista general de toda la región —" if is_es else "— Full region overview —")
                    if idx == -1 else
                    f"#{idx + 1} · {map_agg.loc[idx, 'localidad']} ({map_agg.loc[idx, value_col]:,.0f} {unit_label} · {map_agg.loc[idx, 'pct_share']:.1f}%)"
                )
            )

            color_max_val = float(np.percentile(map_agg[value_col], 95)) if len(map_agg) > 3 else float(map_agg[value_col].max())
            color_max_val = max(color_max_val, 1.0)

            zoom_to_selected = False
            show_buffer_rings = False
            if selected_idx != -1:
                z_c1, z_c2 = st.columns(2)
                with z_c1:
                    zoom_to_selected = st.checkbox("Acercar vista detallada" if is_es else "Zoom in", value=True)
                with z_c2:
                    show_buffer_rings = st.checkbox("Anillos 5 km y 10 km" if is_es else "5 km & 10 km rings", value=True)

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
                "harmonized_hotspots": "Focos" if is_es else "Hotspots",
                "harmonized_frp": "FRP (MW)" if is_es else "FRP (MW)",
                "pct_share": "%"
            }
            base_style_name = "carto-darkmatter" if map_style_choice == "dark" else "open-street-map"

            if viz_mode == "bubbles":
                scatter_func = px.scatter_map if hasattr(px, "scatter_map") else px.scatter_mapbox
                style_kwarg = {"map_style": base_style_name} if hasattr(px, "scatter_map") else {"mapbox_style": base_style_name}
                fig_map = scatter_func(
                    map_agg, lat="lat_plot", lon="lon_plot", size=value_col, color=value_col,
                    size_max=30, color_continuous_scale=color_scale, range_color=[0, color_max_val],
                    opacity=0.88, zoom=zoom_lvl, center={"lat": center_lat, "lon": center_lon},
                    hover_name="localidad", hover_data=hover_cols, labels=labels_map, **style_kwarg
                )
            elif viz_mode == "heatmap":
                density_func = px.density_map if hasattr(px, "density_map") else px.density_mapbox
                style_kwarg = {"map_style": base_style_name} if hasattr(px, "density_map") else {"mapbox_style": base_style_name}
                fig_map = density_func(
                    map_agg, lat="lat_plot", lon="lon_plot", z=value_col, radius=28,
                    color_continuous_scale=color_scale, range_color=[0, color_max_val],
                    opacity=0.80, zoom=zoom_lvl, center={"lat": center_lat, "lon": center_lon},
                    hover_name="localidad", hover_data=hover_cols, labels=labels_map, **style_kwarg
                )
            else:
                half = active_grid_res / 2.0
                features = []
                for _, row in map_agg.iterrows():
                    lat_c, lon_c = float(row["lat_bin"]), float(row["lon_bin"])
                    poly = [[
                        [lon_c - half, lat_c - half], [lon_c + half, lat_c - half],
                        [lon_c + half, lat_c + half], [lon_c - half, lat_c + half],
                        [lon_c - half, lat_c - half],
                    ]]
                    features.append({"type": "Feature", "id": row["cell_id"], "geometry": {"type": "Polygon", "coordinates": poly}, "properties": {"cell_id": row["cell_id"]}})
                geojson_grid = {"type": "FeatureCollection", "features": features}
                choro_func = px.choropleth_map if hasattr(px, "choropleth_map") else px.choropleth_mapbox
                style_kwarg = {"map_style": base_style_name} if hasattr(px, "choropleth_map") else {"mapbox_style": base_style_name}
                hover_grid = dict(hover_cols)
                hover_grid["cell_id"] = False
                fig_map = choro_func(
                    map_agg, geojson=geojson_grid, locations="cell_id", featureidkey="id",
                    color=value_col, color_continuous_scale=color_scale, range_color=[0, color_max_val],
                    opacity=0.68, zoom=zoom_lvl, center={"lat": center_lat, "lon": center_lon},
                    hover_data=hover_grid, labels=labels_map, **style_kwarg
                )
                fig_map.update_traces(marker_line_width=0.7, marker_line_color="rgba(255,255,255,0.45)")

            if map_style_choice == "satellite":
                sat_layers = [
                    {"below": "traces", "sourcetype": "raster", "sourceattribution": "Esri World Imagery", "source": ["https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"]},
                    {"below": "traces", "sourcetype": "raster", "sourceattribution": "Esri Reference", "source": ["https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"]},
                ]
                if hasattr(px, "scatter_map"):
                    fig_map.update_layout(map_layers=sat_layers)
                else:
                    fig_map.update_layout(mapbox_layers=sat_layers)

            if selected_idx != -1 and show_buffer_rings:
                s_lat_ring = float(map_agg.loc[selected_idx, "lat_plot"])
                s_lon_ring = float(map_agg.loc[selected_idx, "lon_plot"])
                lat_5, lon_5 = make_circle_coords(s_lat_ring, s_lon_ring, 5.0)
                lat_10, lon_10 = make_circle_coords(s_lat_ring, s_lon_ring, 10.0)
                trace_cls = go.Scattermap if hasattr(go, "Scattermap") else go.Scattermapbox
                fig_map.add_trace(trace_cls(lat=lat_5, lon=lon_5, mode="lines", line=dict(width=2.5, color="#00E5FF"), name="5 km", hoverinfo="skip"))
                fig_map.add_trace(trace_cls(lat=lat_10, lon=lon_10, mode="lines", line=dict(width=1.8, color="#FFD600"), name="10 km", hoverinfo="skip"))

            fig_map.update_layout(
                height=440,
                margin=dict(l=0, r=0, t=4, b=0),
                coloraxis_colorbar=dict(thickness=12, len=0.85, title=unit_label),
                legend=dict(orientation="h", yanchor="bottom", y=0.01, xanchor="left", x=0.01, bgcolor="rgba(20,20,20,0.65)", font=dict(color="white"))
            )

            try:
                chart_event = st.plotly_chart(fig_map, width='stretch', on_select="rerun", selection_mode="points", key="fire_map_chart", config=plotly_mobile_cfg)
                if chart_event and getattr(chart_event, "selection", None) and chart_event.selection.get("points"):
                    pt = chart_event.selection["points"][0]
                    if pt.get("curve_number", 0) == 0:
                        clicked_idx = pt.get("point_index", pt.get("pointIndex", None))
                        if clicked_idx is not None and 0 <= int(clicked_idx) < len(map_agg):
                            selected_idx = int(clicked_idx)
            except TypeError:
                st.plotly_chart(fig_map, width='stretch', config=plotly_mobile_cfg)

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

                st.info(
                    f"**{exact_zone_display}** (`{s_lat:.4f}°, {s_lon:.4f}°`) · "
                    f"**{sel_row['harmonized_hotspots']:,.0f}** {'focos' if is_es else 'hotspots'} · "
                    f"**{sel_row['harmonized_frp']:,.0f} MW**  |  "
                    f"[Google Maps]({gmaps_url}) · [NASA 24h]({firms_url})"
                )

            if not map_agg.empty:
                top_rank_df = (
                    map_agg.groupby("localidad", as_index=False)[value_col]
                    .sum()
                    .sort_values(by=value_col, ascending=False)
                    .head(8)
                    .sort_values(by=value_col, ascending=True)
                )
                if not top_rank_df.empty:
                    st.markdown(f"**Top {len(top_rank_df)} {'sectores críticos' if is_es else 'critical sectors'} ({map_scope_label}):**")
                    fig_rank = px.bar(
                        top_rank_df,
                        x=value_col,
                        y="localidad",
                        orientation="h",
                        color=value_col,
                        text=value_col,
                        color_continuous_scale=color_scale,
                        labels={"localidad": "", value_col: unit_label}
                    )
                    fig_rank.update_traces(
                        texttemplate="%{x:,.0f}",
                        textposition="outside",
                        cliponaxis=False
                    )
                    fig_rank.update_layout(
                        height=max(200, len(top_rank_df) * 32),
                        margin=dict(l=4, r=42, t=4, b=4),
                        font=dict(size=chart_font_size),
                        coloraxis_showscale=False,
                        yaxis=dict(title=""),
                        xaxis=dict(title=unit_label, gridcolor="rgba(150,150,150,0.18)")
                    )
                    st.plotly_chart(fig_rank, width='stretch', config=plotly_mobile_cfg)

    with col_side:
        if audience == "citizen":
            if not map_agg.empty:
                if selected_idx != -1 and exact_zone_display:
                    active_sector = exact_zone_display
                    comuna_clean = exact_comuna_name
                    p_lat = float(map_agg.loc[selected_idx, "lat_plot"])
                    p_lon = float(map_agg.loc[selected_idx, "lon_plot"])
                else:
                    p_lat = float(map_agg.loc[0, "lat_plot"])
                    p_lon = float(map_agg.loc[0, "lon_plot"])
                    osm_top, osm_top_comuna = reverse_geocode_exact(round(p_lat, 4), round(p_lon, 4), is_es)
                    active_sector = osm_top if osm_top else map_agg.loc[0, "localidad"]
                    comuna_clean = osm_top_comuna if osm_top_comuna else map_agg.loc[0, "comuna_ref"]

                df_scope = df_filtered[
                    (df_filtered["lat_exact"].between(p_lat - 0.15, p_lat + 0.15)) &
                    (df_filtered["lon_exact"].between(p_lon - 0.15, p_lon + 0.15))
                ]
                if df_scope.empty:
                    df_scope = df_filtered
                scope_label = f"{region_display} — {active_sector}"
            else:
                df_scope = df_filtered
                active_sector = region_display
                comuna_clean = ""
                scope_label = region_display

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

            if is_es:
                st.error("🚨 **EMERGENCIA ACTIVA:** Llama gratis al **130 (CONAF)** o **132 (Bomberos)**")
                muni_target = f"de la Municipalidad de {comuna_clean}" if comuna_clean else "de la Municipalidad"
                msg_mail = (
                    f"Estimado equipo de Emergencias {muni_target}:\n\n"
                    f"Según datos satelitales NASA FIRMS (2000–2026), nuestra zona\n"
                    f"({scope_label}) concentra el {mail_share:.0f}% de los incendios\n"
                    f"históricos entre {mail_months}.\n\n"
                    f"Solicitamos informar el calendario de limpieza de maleza y\n"
                    f"mantención de cortafuegos preventivos para nuestro sector."
                )
                mailto_subject = quote(f"Solicitud preventiva de cortafuegos - {scope_label}")
                mailto_body = quote(msg_mail.replace("\n", " "))
                mailto_link = f"mailto:consulta.oirs@conaf.cl,oirs@senapred.gob.cl?subject={mailto_subject}&body={mailto_body}"

                st.markdown(
                    f"""
                    <div class="mail-highlight-box">
                        <div style="font-size:0.78rem; font-weight:800; color:#FF6B35; letter-spacing:0.05em; text-transform:uppercase;">
                            ✉️ Acción Ciudadana Destacada
                        </div>
                        <div style="font-size:1.12rem; font-weight:800; margin:3px 0 4px 0;">
                            Exige Cortafuegos Antes de {mail_months}
                        </div>
                        <div class="mail-sector-pill">
                            📍 Sector activo: {active_sector}
                        </div>
                        <div style="font-size:0.88rem; opacity:0.9;">
                            Envía este aviso con datos reales a CONAF, SENAPRED o la OIRS de tu comuna:
                        </div>
                        <a class="mail-cta-btn" href="{mailto_link}">
                            📨 Abrir Correo Listo para Enviar
                        </a>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.caption("O copia el mensaje en 1 clic (ícono superior derecho) para pegarlo en la OIRS municipal:")
                st.code(msg_mail, language=None)
                st.markdown(
                    "**Correos directos:**\n"
                    "* **CONAF:** `consulta.oirs@conaf.cl`\n"
                    "* **SENAPRED:** `oirs@senapred.gob.cl`\n"
                    "* **Red Prevención:** `contacto@reddeprevencioncomunitaria.cl`"
                )
            else:
                st.error("🚨 **ACTIVE EMERGENCY:** Call **130 (CONAF)** or **132 (Firefighters)**")
                muni_target_en = f"of the Municipality of {comuna_clean}" if comuna_clean else "of the Municipality"
                msg_mail_en = (
                    f"Dear Emergency & Prevention Team {muni_target_en}:\n\n"
                    f"According to calibrated NASA FIRMS satellite records (2000–2026),\n"
                    f"our area ({scope_label}) concentrates {mail_share:.0f}% of historical\n"
                    f"wildfire activity during {mail_months}.\n\n"
                    f"We kindly request the preventive firebreak maintenance and\n"
                    f"brush-clearing schedule for our neighborhood ahead of peak season."
                )
                mailto_subject_en = quote(f"Preventive Firebreak Request - {scope_label}")
                mailto_body_en = quote(msg_mail_en.replace("\n", " "))
                mailto_link_en = f"mailto:consulta.oirs@conaf.cl,oirs@senapred.gob.cl?subject={mailto_subject_en}&body={mailto_body_en}"

                st.markdown(
                    f"""
                    <div class="mail-highlight-box">
                        <div style="font-size:0.78rem; font-weight:800; color:#FF6B35; letter-spacing:0.05em; text-transform:uppercase;">
                            ✉️ Featured Citizen Action
                        </div>
                        <div style="font-size:1.12rem; font-weight:800; margin:3px 0 4px 0;">
                            Request Firebreaks Before {mail_months}
                        </div>
                        <div class="mail-sector-pill">
                            📍 Active sector: {active_sector}
                        </div>
                        <div style="font-size:0.88rem; opacity:0.9;">
                            Send this pre-filled notice with local data to CONAF, SENAPRED, or your municipal OIRS:
                        </div>
                        <a class="mail-cta-btn" href="{mailto_link_en}">
                            📨 Open Pre-filled Email Now
                        </a>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.caption("Or copy the message in 1 click (top-right icon) to paste into your municipal portal:")
                st.code(msg_mail_en, language=None)
                st.markdown(
                    "**Direct agency emails:**\n"
                    "* **CONAF:** `consulta.oirs@conaf.cl`\n"
                    "* **SENAPRED:** `oirs@senapred.gob.cl`\n"
                    "* **Community Prevention:** `contacto@reddeprevencioncomunitaria.cl`"
                )

        elif audience == "municipal":
            st.subheader("Exportar Datos QGIS" if is_es else "Export QGIS Data")
            st.write(f"**{region_display}** · {len(df_filtered):,} registros calibrados.")
            csv_export = df_filtered.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar CSV Regional" if is_es else "Download Regional CSV",
                data=csv_export,
                file_name=f"incendios_calibrados_{preset.replace(' ', '_').lower()}.csv",
                mime="text/csv",
                width='stretch'
            )
            st.info("Incluye `lat_exact` y `lon_exact` para cruce con predios y cortafuegos." if is_es else "Includes `lat_exact` and `lon_exact` for QGIS overlays.")
        else:
            st.subheader("Dataset Armonizado" if is_es else "Harmonized Dataset")
            st.write(f"**{region_display}** · {len(df_filtered):,} celdas-mes.")
            csv_export = df_filtered.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar CSV Científico" if is_es else "Download Scientific CSV",
                data=csv_export,
                file_name=f"harmonized_fires_{preset.replace(' ', '_').lower()}.csv",
                mime="text/csv",
                width='stretch'
            )
            st.info("Gradient Boosting (`scan × track` + Duan). `R² lineal = 0.887`, hindcast ciego 2012–2015 `R² = 0.784` (`+4.88%` sesgo).")

# ==============================================================================
# PASO 5: GUÍA VISUAL DE PREVENCIÓN Y PREGUNTAS FRECUENTES
# ==============================================================================
with st.container(border=True):
    st.markdown(
        f'<span class="step-badge-blue">{"Paso 5 de 5" if is_es else "Step 5 of 5"}</span>'
        f'<div class="step-title">{"Prevención Visual y Preguntas Clave" if is_es else "Visual Prevention Guide & Key FAQ"}</div>',
        unsafe_allow_html=True
    )

    p_cards = (
        [
            ("rgba(46,160,67,0.12)", "#2ea043", "🏡 1. Zona Segura (10–30 m)", "Despeja pasto seco y ramas bajas alrededor de tu vivienda."),
            ("rgba(31,111,235,0.12)", "#1f6feb", "🏠 2. Techos y Canaletas", "Retira hojas secas donde caen brasas aéreas (pavesas)."),
            ("rgba(255,107,53,0.12)", "#FF6B35", "🚫 3. Cero Chispas", "No uses galleteras, soldadoras ni quemes basura en días calurosos."),
            ("rgba(215,48,31,0.13)", "#D7301F", "📞 4. Llama al 130 / 132", "Avisa humo al instante y evacúa apenas suene la alerta SAE."),
        ]
        if is_es else
        [
            ("rgba(46,160,67,0.12)", "#2ea043", "🏡 1. Safe Buffer (10–30 m)", "Clear dry grass and low tree branches around your home."),
            ("rgba(31,111,235,0.12)", "#1f6feb", "🏠 2. Roofs & Gutters", "Remove dry leaves where wind-blown embers can ignite."),
            ("rgba(255,107,53,0.12)", "#FF6B35", "🚫 3. Zero Sparks", "Avoid grinders, welders, and trash burns on hot windy days."),
            ("rgba(215,48,31,0.13)", "#D7301F", "📞 4. Call 130 / 132", "Report smoke immediately and evacuate upon SAE alerts."),
        ]
    )

    prev_html = '<div class="prev-grid">' + "".join([
        f'<div class="prev-card" style="background:{bg}; border:1.5px solid {brd};">'
        f'<div class="prev-card-head">{head}</div>'
        f'<div class="prev-card-body">{body}</div>'
        f'</div>'
        for bg, brd, head, body in p_cards
    ]) + '</div>'
    st.markdown(prev_html, unsafe_allow_html=True)

    tab_faq, tab_sat, tab_how = st.tabs(
        ["Preguntas frecuentes", "Satélites NASA", "Cómo se construyó"]
        if is_es else
        ["FAQ", "NASA Satellites", "Methodology"]
    )

    with tab_faq:
        if is_es:
            with st.expander("¿Qué hacer ante humo denso o alerta SAE de evacuación?"):
                st.markdown(
                    "* **Evacúa de inmediato** al recibir alerta SAE; no regreses por objetos.\n"
                    "* **Protección respiratoria:** Usa mascarilla **N95 o KN95** (filtra partículas finas `PM2.5`) y sella rendijas con paños húmedos.\n"
                    "* **Teléfonos gratuitos:** **130** (CONAF), **132** (Bomberos), **133** (Carabineros)."
                )
            with st.expander("¿Cuál es la diferencia entre Focos Calibrados y Potencia Térmica (FRP)?"):
                st.markdown(
                    "* **Focos Calibrados:** Cantidad de detecciones térmicas registradas (mide **extensión y duración**).\n"
                    "* **Potencia Radiativa (FRP en MW):** Energía liberada por el fuego al pasar el satélite (mide **intensidad**).\n"
                    "* **Ejemplo (Valparaíso Feb 2024):** Duró menos de 48 horas (menos pasadas orbitales que incendios rurales de semanas), pero marcó el récord histórico regional de intensidad."
                )
            with st.expander("¿Por qué aparecen puntos fijos en el desierto del norte y qué límites tiene el satélite?"):
                st.markdown(
                    "* **Minería y plantas solares:** En Antofagasta/Atacama, los puntos repetitivos todo el año son fundiciones de cobre o plantas termosolares (puedes ocultarlos en el Paso 1).\n"
                    "* **Uso preventivo:** Los satélites pasan 2–4 veces al día; sirven para planificar cortafuegos, pero ante humo visible **llama siempre al 130 o 132 sin esperar al satélite**."
                )
        else:
            with st.expander("What to do during heavy smoke or an SAE evacuation alert?"):
                st.markdown(
                    "* **Evacuate immediately** upon SAE alerts without returning for belongings.\n"
                    "* **Smoke protection:** Wear **N95/KN95** masks (filters `PM2.5`) and seal window gaps with damp cloths.\n"
                    "* **Emergency numbers:** **130** (CONAF), **132** (Firefighters), **133** (Police)."
                )
            with st.expander("Difference between Calibrated Hotspots and Fire Radiative Power (FRP)?"):
                st.markdown(
                    "* **Calibrated Hotspots:** Number of thermal detections (measures **duration & extent**).\n"
                    "* **FRP (MW):** Instantaneous radiative heat output (measures **burning intensity**)."
                )
            with st.expander("Why do fixed points appear in northern Chile and what are satellite limits?"):
                st.markdown(
                    "* **Industrial sources:** Copper smelters and solar thermal plants appear year-round in northern deserts (toggle off in Step 1).\n"
                    "* **Satellite cadence:** Polar satellites pass 2–4 times daily; always call **130/132** immediately if you see smoke."
                )

    with tab_sat:
        if is_es:
            c_s1, c_s2 = st.columns(2)
            with c_s1:
                st.markdown("**MODIS (2000–2011 · Terra y Aqua)**\nPíxeles de **1 km**. Aporta la memoria histórica desde el año 2000.")
            with c_s2:
                st.markdown("**VIIRS (2012–2026 · Suomi-NPP, NOAA-20/21)**\nPíxeles de **375 m** (7x más detalle). Calibramos MODIS a esta escala para evitar saltos artificiales.")
        else:
            st.markdown("- **MODIS (2000–2011):** 1 km pixels.\n- **VIIRS (2012–2026):** 375 m pixels; MODIS is calibrated to VIIRS scale.")

    with tab_how:
        if is_es:
            st.markdown(
                "1. **Desduplicación orbital** de pasadas simultáneas.\n"
                "2. **Corrección óptica (`scan × track`)** por estiramiento del píxel en los bordes.\n"
                "3. **Calibración ML (Gradient Boosting + Duan):** Entrenada en 14 años de solapamiento (`R² lineal = 0.887`, sesgo `< 5%`)."
            )
        else:
            st.markdown(
                "1. **Orbital de-duplication** of overlapping passes.\n"
                "2. **Optical pixel geometry (`scan × track`)** correction.\n"
                "3. **ML Calibration (Gradient Boosting + Duan):** Trained on 14-year overlap (`Linear R² = 0.887`, `< 5%` bias)."
            )