import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuración general de la página
st.set_page_config(page_title="FIRMS Fire Calendar", page_icon="🔥", layout="wide")

# 2. Cargar dataset calibrado (contiene todo Chile: 16 regiones)
@st.cache_data
def load_data():
    return pd.read_csv("harmonized_chile.csv")

df = load_data()

# 3. Límites y Polígonos Exactos de las 16 Regiones de Chile
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

# 4. Barra superior visible (Idioma + Título) para no esconder nada en celular
top_col1, top_col2 = st.columns([3.2, 1])
with top_col2:
    lang = st.radio("🌐 Language / Idioma", ["English", "Español"], horizontal=True)
is_es = (lang == "Español")

with top_col1:
    st.title(
        "🔥 Calendario Satelital de Incendios en Chile"
        if is_es else
        "🔥 Harmonized Wildfire Activity Calendar (2000–2026)"
    )

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

# 5. Paso 1 y Paso 2 visibles directamente en pantalla (ideal para celular y ciudadanía)
ctrl_a, ctrl_b = st.columns([1.3, 1.7])

with ctrl_a:
    preset = st.selectbox(
        "📍 Paso 1 · Elige tu Región o Territorio:" if is_es else "📍 Step 1 · Choose Region or Territory:",
        preset_keys,
        index=preset_keys.index("Biobío"),
        format_func=lambda k: preset_labels[k]
    )

with ctrl_b:
    audience = st.radio(
        "👤 Paso 2 · ¿Cómo quieres ver la información?" if is_es else "👤 Step 2 · Choose your profile:",
        ["citizen", "municipal", "scientist"],
        format_func=lambda k: {
            "citizen": "🏡 Ciudadanía (Simple)" if is_es else "🏡 Citizens (Plain Language)",
            "municipal": "🏛️ Municipios y Emergencias" if is_es else "🏛️ Municipalities & Emergency",
            "scientist": "🔬 Investigadores / Datos" if is_es else "🔬 Researchers / Data",
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

# Métrica técnica solo visible en perfil Municipal o Científico
if audience == "citizen":
    value_col = "harmonized_hotspots"
    unit_label = "Focos de calor" if is_es else "Fire hotspots"
else:
    metric_key = st.radio(
        "⚙️ Métrica a analizar:" if is_es else "⚙️ Analysis metric:",
        ["hotspots", "frp"],
        format_func=lambda k: (
            ("Focos Calibrados (Conteo de detecciones)" if is_es else "Calibrated Hotspots (Count)")
            if k == "hotspots" else
            ("Potencia Radiativa del Fuego (FRP - MW)" if is_es else "Fire Radiative Power (FRP - MW)")
        ),
        horizontal=True
    )
    value_col = "harmonized_hotspots" if metric_key == "hotspots" else "harmonized_frp"
    unit_label = ("Focos" if is_es else "Hotspots") if metric_key == "hotspots" else "MW"

st.markdown("---")

# 6. Filtrado Espacial (Caja + Polígono Regional Exacto)
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

# Botones rápidos interactivos (1 clic para explorar escenarios clave)
if "selected_year_state" not in st.session_state:
    st.session_state["selected_year_state"] = int(default_year)

if audience == "citizen":
    st.markdown("**⚡ Exploración rápida con 1 clic:**" if is_es else "**⚡ 1-Click Quick Exploration:**")
    q1, q2, q3 = st.columns(3)
    if q1.button("📅 Ver este año (2026)" if is_es else "📅 Current Year (2026)", use_container_width=True):
        st.session_state["selected_year_state"] = int(max(years_available))
    worst_yr = int(annual_totals.idxmax())
    if q2.button(f"🔥 Ver peor año ({worst_yr})" if is_es else f"🔥 Worst Year ({worst_yr})", use_container_width=True):
        st.session_state["selected_year_state"] = worst_yr
    if q3.button("🌱 Ver año tranquilo (2016)" if is_es else "🌱 Calm Year (2016)", use_container_width=True):
        st.session_state["selected_year_state"] = 2016 if 2016 in years_available else int(min(years_available))

# Controles de Año y Mes
col_ctrl1, col_ctrl2 = st.columns([3, 1])
with col_ctrl1:
    selected_year = st.slider(
        "📅 Paso 3 · Elige el año que quieres revisar:" if (is_es and audience == "citizen") else ("📅 Selecciona Año a Evaluar:" if is_es else "📅 Select Year to Inspect:"),
        int(min(years_available)),
        int(max(years_available)),
        key="selected_year_state"
    )
with col_ctrl2:
    month_idx_choice = st.selectbox(
        "🗓️ Mes:" if is_es else "🗓️ Month:",
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

# 7. Semáforo de Alerta Adaptado al Público
if median_baseline > 0:
    ratio = total_selected / median_baseline
    pct_diff = (ratio - 1.0) * 100
    anomaly_str = f"{ratio:.1f}x {'lo normal' if is_es else 'normal'}" if audience == "citizen" else f"{pct_diff:+.1f}%"

    if ratio >= 2.0:
        if audience == "citizen":
            st.error(
                f"🔴 **PELIGRO EXTREMO en {region_display} ({period_title}):** "
                f"Hubo **{ratio:.1f} veces más fuego** que en un año normal.\n\n"
                f"🛡️ **Qué significa para tu familia:** En esta región, el **{top3_share:.0f}%** de los incendios ocurre entre **{top3_names}**. "
                f"Es urgente mantener cortafuegos limpios y evitar quemas o chispas cerca de pastizales."
                if is_es else
                f"🔴 **EXTREME FIRE DANGER in {region_display} ({period_title}):** "
                f"Fire activity was **{ratio:.1f}x higher** than a typical year.\n\n"
                f"🛡️ **What this means:** Peak fire months here are **{top3_names}** (**{top3_share:.0f}%** of annual fires)."
            )
        elif audience == "municipal":
            st.error(
                f"🔴 **EMERGENCIA / ANOMALÍA EXTREMA en {region_display} ({period_title}):** "
                f"Actividad **{pct_diff:+.1f}%** sobre la mediana histórica (**{ratio:.1f}x** lo habitual).\n\n"
                f"📋 **Priorización Operativa:** El **{top3_share:.0f}%** de la carga anual ocurre en **{top3_names}**. "
                f"Activar alerta temprana comunal y priorizar cortafuegos en los cuadrantes amarillos del mapa."
                if is_es else
                f"🔴 **EMERGENCY / EXTREME ANOMALY in {region_display} ({period_title}):** "
                f"Activity is **{pct_diff:+.1f}%** above historical median (**{ratio:.1f}x** baseline)."
            )
        else:
            st.error(
                f"🔴 **ANOMALÍA TÉRMICA EXTREMA en {region_display} ({period_title}):** "
                f"`{pct_diff:+.1f}%` vs. mediana 2000–2025 (`{ratio:.2f}x` línea base). "
                f"Ventana estacional dominante: **{top3_names}** (`{top3_share:.1f}%`)."
                if is_es else
                f"🔴 **EXTREME THERMAL ANOMALY in {region_display} ({period_title}):** "
                f"`{pct_diff:+.1f}%` vs. 2000–2025 median (`{ratio:.2f}x` baseline)."
            )
    elif ratio >= 1.25:
        st.warning(
            f"🟠 **ACTIVIDAD SOBRE LO NORMAL en {region_display} ({period_title}):** "
            f"**{pct_diff:+.1f}%** ({ratio:.1f}x lo habitual). Meses críticos locales: **{top3_names}** (**{top3_share:.0f}%**)."
            if is_es else
            f"🟠 **ABOVE-NORMAL ACTIVITY in {region_display} ({period_title}):** "
            f"**{pct_diff:+.1f}%** ({ratio:.1f}x normal). Local critical window: **{top3_names}**."
        )
    elif ratio >= 0.75:
        st.success(
            f"🟢 **NIVEL NORMAL en {region_display} ({period_title}):** "
            f"Actividad dentro de lo habitual ({pct_diff:+.1f}%). Recuerda cuidarte en **{top3_names}**."
            if is_es else
            f"🟢 **NORMAL LEVEL in {region_display} ({period_title}):** "
            f"Activity within expected historical range ({pct_diff:+.1f}%)."
        )
    else:
        st.info(
            f"🔵 **AÑO TRANQUILO / BAJO LO NORMAL en {region_display} ({period_title}):** "
            f"**{abs(pct_diff):.1f}% menos** fuego que lo habitual. La temporada de mayor cuidado sigue siendo **{top3_names}**."
            if is_es else
            f"🔵 **BELOW-NORMAL ACTIVITY in {region_display} ({period_title}):** "
            f"**{abs(pct_diff):.1f}% lower** than usual."
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

# 8. Tarjetas KPI adaptadas
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric(
    f"{'Focos detectados en' if (is_es and audience == 'citizen') else ('Actividad en' if is_es else 'Activity in')} {period_title}",
    f"{total_selected:,.0f} {unit_label}"
)
kpi2.metric(median_label, f"{median_baseline:,.0f} {unit_label}")
kpi3.metric(
    ("Comparación con año normal" if is_es else "Compared to normal")
    if audience == "citizen" else
    ("Anomalía vs. Mediana" if is_es else "Anomaly vs. Median"),
    anomaly_str
)

st.markdown("---")

# 9. Visualizaciones Principales según el Público
calendar_pivot = monthly_totals.pivot(index='year', columns='month', values=value_col).reindex(columns=range(1, 13))
max_monthly_all_time = max(float(monthly_totals[value_col].max()), 1.0)

if audience == "citizen":
    st.subheader("🗓️ ¿En qué meses hay más peligro? (Calendario 2000–2026)" if is_es else "🗓️ When Is Fire Danger Highest? (2000–2026 Calendar)")
    st.caption(
        "Cada fila es un año y cada columna es un mes. **Azul** = tranquilo | **Amarillo** = emergencia grave."
        if is_es else
        "Each row is a year and each column is a month. **Blue** = calm | **Yellow** = severe emergency."
    )
    fig_cal = px.imshow(
        calendar_pivot,
        labels=dict(x="Mes" if is_es else "Month", y="Año" if is_es else "Year", color=unit_label),
        x=month_names,
        y=calendar_pivot.index.astype(str),
        color_continuous_scale="Cividis",
        aspect="auto"
    )
    fig_cal.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_cal, use_container_width=True)

    st.markdown("---")
    st.subheader(f"🗺️ Mapa: ¿Dónde ocurrió el fuego en {period_title}?" if is_es else f"🗺️ Map: Where Did Fires Happen in {period_title}?")
    st.caption(
        "Elige una localidad de la lista o haz clic en un cuadrante del mapa para acercarte y verlo en Google Maps."
        if is_es else
        "Pick a locality from the dropdown or click any zone on the map to zoom in and open Google Maps."
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
        fig_cal.update_layout(height=450, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_cal, use_container_width=True)

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
            height=450,
            margin=dict(l=10, r=10, t=20, b=10),
            yaxis=dict(title=unit_label, range=[0, max_monthly_all_time * 1.05]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_curve, use_container_width=True)

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
        st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("---")
    st.subheader(f"🗺️ Mapa Espacial de Intensidad — {period_title}" if is_es else f"🗺️ Spatial Fire Intensity Map — {period_title}")

# 10. Mapa Espacial Interactivo con Inspector de Localidades y Google Maps
CHILE_LOCALITIES = [
    ("Arica", -18.48, -70.31, "urban"),
    ("Iquique", -20.21, -70.15, "urban"),
    ("Calama / Chuquicamata", -22.46, -68.93, "industrial_desert"),
    ("San Pedro de Atacama", -22.91, -68.20, "desert"),
    ("Antofagasta", -23.65, -70.40, "industrial_desert"),
    ("Copiapó / Tierra Amarilla", -27.37, -70.33, "industrial_desert"),
    ("Vallenar", -28.58, -70.76, "semi_arid"),
    ("La Serena / Coquimbo", -29.90, -71.25, "semi_arid"),
    ("Ovalle", -30.60, -71.20, "semi_arid"),
    ("Illapel", -31.63, -71.17, "semi_arid"),
    ("La Ligua / Petorca", -32.45, -71.23, "forest_agri"),
    ("Quillota / Limache", -32.88, -71.25, "forest_agri"),
    ("Valparaíso / Viña del Mar", -33.05, -71.62, "forest_agri"),
    ("San Antonio", -33.59, -71.61, "forest_agri"),
    ("Santiago (RM)", -33.45, -70.67, "forest_agri"),
    ("Melipilla", -33.69, -71.21, "forest_agri"),
    ("Rancagua / Machalí", -34.17, -70.74, "forest_agri"),
    ("San Fernando", -34.58, -70.99, "forest_agri"),
    ("Pichilemu", -34.39, -72.00, "forest_agri"),
    ("Curicó", -34.98, -71.24, "forest_agri"),
    ("Talca", -35.43, -71.66, "forest_agri"),
    ("Constitución", -35.33, -72.41, "forest_agri"),
    ("Linares", -35.85, -71.59, "forest_agri"),
    ("Cauquenes", -35.97, -72.32, "forest_agri"),
    ("Parral", -36.14, -71.83, "forest_agri"),
    ("San Carlos", -36.42, -71.96, "forest_agri"),
    ("Coelemu / Quirihue", -36.49, -72.70, "forest_agri"),
    ("Chillán / Coihueco", -36.61, -72.10, "forest_agri"),
    ("Quillón / Bulnes", -36.74, -72.47, "forest_agri"),
    ("Yungay / Pemuco", -37.12, -72.01, "forest_agri"),
    ("Penco / Tomé / Concepción", -36.74, -72.99, "forest_agri"),
    ("Coronel / Lota / Santa Juana", -37.03, -73.14, "forest_agri"),
    ("Cabrero / Yumbel", -37.04, -72.40, "forest_agri"),
    ("Los Ángeles / Nacimiento", -37.47, -72.35, "forest_agri"),
    ("Lebu / Cañete (Arauco)", -37.60, -73.65, "forest_agri"),
    ("Angol / Collipulli", -37.80, -72.71, "forest_agri"),
    ("Victoria / Traiguén", -38.23, -72.33, "forest_agri"),
    ("Temuco / Padre Las Casas", -38.74, -72.59, "forest_agri"),
    ("Villarrica / Pucón", -39.28, -72.23, "forest_agri"),
    ("Valdivia / Mariquina", -39.81, -73.25, "forest_agri"),
    ("La Unión / Río Bueno", -40.29, -73.08, "forest_agri"),
    ("Osorno", -40.57, -73.13, "forest_agri"),
    ("Puerto Montt / Puerto Varas", -41.47, -72.94, "forest_agri"),
    ("Castro / Ancud (Chiloé)", -42.48, -73.76, "forest_agri"),
    ("Chaitén / Futaleufú", -42.92, -72.71, "forest_agri"),
    ("Coyhaique / Puerto Aysén", -45.57, -72.07, "forest_agri"),
    ("Cochrane", -47.25, -72.57, "forest_agri"),
    ("Puerto Natales", -51.73, -72.50, "forest_agri"),
    ("Punta Arenas", -53.16, -70.91, "forest_agri"),
]

def describe_location(lat, lon, is_es_flag=True):
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
    if best_dist < 14.0:
        loc_str = f"Sector {best_name}" if is_es_flag else f"{best_name} area"
    else:
        ns = "N" if best_dlat >= 0 else "S"
        ew = ("E" if best_dlon >= 0 else ("O" if is_es_flag else "W"))
        loc_str = (
            f"~{best_dist:.0f} km al {ns}{ew} de {best_name}"
            if is_es_flag else
            f"~{best_dist:.0f} km {ns}{ew} of {best_name}"
        )
    return loc_str, best_type

col_map, col_side = st.columns([2.2, 1])

with col_map:
    if df_map_source.empty:
        st.info(
            "No se registraron focos de calor en este período para la zona elegida."
            if is_es else
            "No fire hotspots recorded in this period for the selected area."
        )
    else:
        map_style_choice = st.radio(
            "🗺️ Vista del mapa:" if is_es else "🗺️ Map view:",
            ["osm", "dark"],
            format_func=lambda k: (
                ("📍 Con Ciudades, Pueblos y Caminos" if is_es else "📍 Cities, Towns & Roads")
                if k == "osm" else
                ("🌑 Fondo Oscuro (Alto Contraste)" if is_es else "🌑 Dark Background")
            ),
            horizontal=True
        )
        chosen_style = "open-street-map" if map_style_choice == "osm" else "carto-darkmatter"

        map_agg = (
            df_map_source.groupby(['lat_bin', 'lon_bin'])
            .agg(
                harmonized_hotspots=('harmonized_hotspots', 'sum'),
                harmonized_frp=('harmonized_frp', 'sum')
            )
            .reset_index()
            .sort_values(by=value_col, ascending=False)
            .reset_index(drop=True)
        )
        map_agg["cell_id"] = map_agg.index.astype(str)
        loc_info = [describe_location(float(r["lat_bin"]), float(r["lon_bin"]), is_es) for _, r in map_agg.iterrows()]
        map_agg["localidad"] = [x[0] for x in loc_info]
        map_agg["zone_type"] = [x[1] for x in loc_info]

        top_n = min(len(map_agg), 30)
        inspect_options = [-1] + list(range(top_n))
        selected_idx = st.selectbox(
            "🔍 Elige un sector afectado para acercar el mapa y abrirlo en Google Maps:"
            if is_es else
            "🔍 Pick an affected sector to zoom in and open in Google Maps:",
            options=inspect_options,
            format_func=lambda idx: (
                ("— Ver toda la región completa —" if is_es else "— Full region overview —")
                if idx == -1 else
                f"#{idx + 1} · {map_agg.loc[idx, 'localidad']} ({map_agg.loc[idx, value_col]:,.0f} {unit_label})"
            )
        )

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

        if month_idx_choice == 0:
            hist_cell_max = float(df_filtered.groupby(['year', 'lat_bin', 'lon_bin'])[value_col].sum().max())
        else:
            hist_cell_max = float(df_filtered[value_col].max())
        hist_cell_max = max(hist_cell_max, 1.0)

        zoom_to_selected = False
        if selected_idx != -1:
            zoom_to_selected = st.checkbox(
                f"🔎 Acercar mapa a {map_agg.loc[selected_idx, 'localidad']}"
                if is_es else
                f"🔎 Zoom map into {map_agg.loc[selected_idx, 'localidad']}",
                value=True
            )

        if selected_idx != -1 and zoom_to_selected:
            center_lat = float(map_agg.loc[selected_idx, "lat_bin"])
            center_lon = float(map_agg.loc[selected_idx, "lon_bin"])
            zoom_lvl = 9.2
        elif preset != "All Chile" and preset != "Custom Coordinates":
            center_lat = float((df_filtered['lat_bin'].min() + df_filtered['lat_bin'].max()) / 2.0)
            center_lon = float((df_filtered['lon_bin'].min() + df_filtered['lon_bin'].max()) / 2.0)
            span = max(
                float(df_filtered['lat_bin'].max() - df_filtered['lat_bin'].min()) + grid_res,
                float(df_filtered['lon_bin'].max() - df_filtered['lon_bin'].min()) + grid_res
            )
            zoom_lvl = float(np.clip(8.3 - np.log2(max(span, 0.4)), 3.2, 8.2))
        else:
            center_lat = (lat_min + lat_max) / 2.0
            center_lon = (lon_min + lon_max) / 2.0
            span = max(abs(lat_max - lat_min), abs(lon_max - lon_min))
            zoom_lvl = float(np.clip(8.3 - np.log2(max(span, 0.4)), 3.2, 8.2))

        choro_func = px.choropleth_map if hasattr(px, "choropleth_map") else px.choropleth_mapbox
        style_kwarg = {"map_style": chosen_style} if hasattr(px, "choropleth_map") else {"mapbox_style": chosen_style}

        hover_cols = {
            "cell_id": False,
            "localidad": True,
            "lat_bin": ":.3f",
            "lon_bin": ":.3f",
            "harmonized_hotspots": ":,.0f"
        }
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
            opacity=0.65,
            zoom=zoom_lvl,
            center={"lat": center_lat, "lon": center_lon},
            hover_data=hover_cols,
            labels={
                "localidad": "Localidad cercana" if is_es else "Nearest locality",
                "lat_bin": "Latitud" if is_es else "Latitude",
                "lon_bin": "Longitud" if is_es else "Longitude",
                "harmonized_hotspots": "Focos de calor" if is_es else "Calibrated Hotspots",
                "harmonized_frp": "FRP (MW)"
            },
            **style_kwarg
        )
        fig_map.update_traces(marker_line_width=0.6, marker_line_color="rgba(255,255,255,0.35)")
        fig_map.update_layout(height=460, margin=dict(l=0, r=0, t=10, b=0))

        try:
            chart_event = st.plotly_chart(fig_map, use_container_width=True, on_select="rerun", selection_mode="points", key="fire_map_chart")
            if chart_event and getattr(chart_event, "selection", None) and chart_event.selection.get("points"):
                pt = chart_event.selection["points"][0]
                clicked_idx = pt.get("point_index", pt.get("pointIndex", None))
                if clicked_idx is not None and 0 <= int(clicked_idx) < len(map_agg):
                    selected_idx = int(clicked_idx)
        except TypeError:
            st.plotly_chart(fig_map, use_container_width=True)

        if selected_idx != -1:
            sel_row = map_agg.loc[selected_idx]
            s_lat, s_lon = float(sel_row["lat_bin"]), float(sel_row["lon_bin"])
            gmaps_url = f"https://www.google.com/maps/search/?api=1&query={s_lat:.4f},{s_lon:.4f}"
            firms_url = f"https://firms.modaps.eosdis.nasa.gov/map/#d:24hrs;@{s_lon:.3f},{s_lat:.3f},11z"

            if sel_row["zone_type"] == "industrial_desert":
                origin_note = (
                    "🏭 **¿Por qué hay calor aquí?** En el norte minero (Calama / Antofagasta), el satélite suele detectar **fundiciones de cobre o plantas solares**, no bosques quemándose."
                    if is_es else
                    "🏭 **Why is heat detected here?** In northern mining areas, satellites often detect **copper smelters or solar plants** rather than forest wildfires."
                )
            else:
                origin_note = (
                    "🌲 **¿Por qué hay calor aquí?** En esta zona centro-sur, las alertas corresponden principalmente a **incendios forestales, de pastizales o quemas agrícolas**."
                    if is_es else
                    "🌲 **Why is heat detected here?** In central-southern Chile, alerts mainly reflect **forest/brush wildfires or agricultural burns**."
                )

            st.info(
                f"📍 **Zona seleccionada:** **{sel_row['localidad']}** (`{s_lat:.3f}°, {s_lon:.3f}°`) — "
                f"**{sel_row['harmonized_hotspots']:,.0f}** {'focos calibrados' if is_es else 'calibrated hotspots'}\n\n"
                f"{origin_note}\n\n"
                f"🔗 [**Ver terreno real en Google Maps**]({gmaps_url})  |  "
                f"[**Ver alerta en vivo en NASA FIRMS**]({firms_url})"
            )

with col_side:
    if audience == "citizen":
        st.subheader("🏛️ Consulta a tu Municipio y Ayuda" if is_es else "🏛️ Contact Municipality & Help")
        if is_es:
            st.error("🚨 **¿Ves humo o fuego ahora mismo?**\nLlama gratis al **130 (CONAF)**, **132 (Bomberos)** o **133 (Carabineros)**.")
            st.markdown(
                f"**📋 Solicita prevención en tu comuna ({region_display}):**\n"
                f"Si vives cerca de pastizales o bosques, copia este mensaje y envíalo a la oficina de emergencias de tu municipalidad antes de **{top3_names}**:"
            )
            sample_sector = map_agg.loc[0, "localidad"] if not df_map_source.empty else region_display
            msg_muni = (
                f"Estimado equipo de Emergencias y Gestión de Riesgos de la Municipalidad:\n"
                f"Según los registros satelitales calibrados de NASA FIRMS (2000–2026), nuestra zona ({region_display} - {sample_sector}) "
                f"concentra el {top3_share:.0f}% de los incendios entre {top3_names}. "
                f"Solicitamos informar el calendario preventivo de limpieza de maleza y mantención de cortafuegos para nuestro sector."
            )
            st.text_area("Mensaje listo para copiar y enviar a tu municipio:", value=msg_muni, height=155)
        else:
            st.error("🚨 **See active smoke or fire?**\nCall **130 (CONAF)** or **132 (Firefighters)** immediately.")
            st.info(f"In **{region_display}**, **{top3_names}** concentrate **{top3_share:.0f}%** of annual fire activity. Ask your local municipality about preventive firebreaks ahead of this window.")

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
            "🏛️ **Uso Municipal:** Las coordenadas (`lat_bin`, `lon_bin`) permiten priorizar cortafuegos y patrullajes preventivos."
            if is_es else
            "🏛️ **Municipal Use:** Grid coordinates (`lat_bin`, `lon_bin`) help prioritize firebreaks and preventive patrols."
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
            "🔬 **Validación:** Calibración MODIS→VIIRS mediante Gradient Boosting (`scan × track` + factor de Duan). "
            "`R² lineal = 0.887` (`0.689` log); hindcast temporal ciego 2012–2015 con `R² = 0.784` y sesgo `+4.88%`."
            if is_es else
            "🔬 **Validation:** MODIS→VIIRS Gradient Boosting (`scan × track` + Duan's smearing). "
            "`Linear R² = 0.887` (`0.689` log); blind 2012–2015 temporal hindcast `R² = 0.784` (`+4.88%` bias)."
        )

st.markdown("---")

# 11. Sección Educativa e Interactiva: Satélites, Qué se hizo y Preguntas Clave
st.subheader("ℹ️ Ayuda, Satélites y ¿Qué se hizo en este proyecto?" if is_es else "ℹ️ Help, Satellites & How This Was Built")

tab_sat, tab_how, tab_faq = st.tabs(
    [
        "🛰️ ¿Qué satélites usamos?",
        "🛠️ ¿Qué se hizo en este proyecto?",
        "❓ Preguntas Clave (Ayuda)"
    ]
    if is_es else
    [
        "🛰️ Which Satellites Are Used?",
        "🛠️ How Was This Built?",
        "❓ Key Questions (FAQ)"
    ]
)

with tab_sat:
    if is_es:
        c_s1, c_s2 = st.columns(2)
        with c_s1:
            st.markdown(
                "### 📡 1. Satélites MODIS (2000–2011)\n"
                "* **Naves de la NASA:** **Terra** y **Aqua**.\n"
                "* **Cómo miran:** Tienen una cámara térmica de **1 kilómetro por píxel**.\n"
                "* **Su valor:** Guardan la memoria histórica más antigua (desde el año 2000), pero al tener píxeles grandes no alcanzan a ver focos pequeños."
            )
        with c_s2:
            st.markdown(
                "### 🛰️ 2. Satélites VIIRS (2012–2026)\n"
                "* **Naves NASA / NOAA:** **Suomi-NPP**, **NOAA-20** y **NOAA-21**.\n"
                "* **Cómo miran:** Tienen una cámara de alta definición de **375 metros por píxel** (casi 7 veces más detalle).\n"
                "* **El problema:** Como ven mucho más detalle, si comparas 2005 con 2023 sin corregirlos, parece que los incendios crecieron artificialmente."
            )
    else:
        st.markdown(
            "- **MODIS (Terra & Aqua, 2000–2011):** 1 km thermal resolution; provides the deep 26-year historical baseline.\n"
            "- **VIIRS (Suomi-NPP, NOAA-20/21, 2012–2026):** 375 m high-resolution thermal sensors; detects smaller and lower-intensity fires.\n"
            "- **Why harmonize?** Combining raw counts creates a false jump in 2012; our calibration translates MODIS into VIIRS-equivalent units."
        )

with tab_how:
    if is_es:
        st.markdown(
            "Para que cualquier persona pueda comparar el pasado con el presente sin engaños, construimos un sistema en **4 pasos**:\n"
            "1. **Limpieza de duplicados orbitales:** Cuando dos satélites pasan por el mismo lugar con minutos de diferencia, eliminamos las detecciones repetidas para no contar el mismo incendio dos veces.\n"
            "2. **Corrección del ángulo de cámara (`scan × track`):** Cuando el satélite mira de lado hacia el horizonte, el píxel se estira hasta 9.6 veces; calculamos el área real observada.\n"
            "3. **Inteligencia Artificial traductora:** Aprovechamos los **14 años en que ambos satélites volaron juntos (2012–2026)** para entrenar un modelo (*Gradient Boosting*) que aprendió a traducir los datos antiguos al estándar moderno (`R² = 0.887`, error acumulado menor al `5%`).\n"
            "4. **Calendario ciudadano:** Transformamos millones de datos científicos de la NASA en este semáforo y mapa interactivo para comunidades y municipios."
        )
    else:
        st.markdown(
            "1. **Orbital de-duplication:** Removes redundant detections from overlapping satellite passes.\n"
            "2. **Optical pixel geometry (`scan × track`):** Accounts for off-nadir pixel stretching up to 9.6 km².\n"
            "3. **Cross-sensor Machine Learning:** Trains Gradient Boosting with Duan's smearing on the 2012–2026 overlap (`R² = 0.887`, `< 5%` blind hindcast bias).\n"
            "4. **Multi-profile calendar:** Delivers tailored views for citizens, municipalities, and researchers."
        )

with tab_faq:
    if is_es:
        with st.expander("❓ ¿Por qué aparecen puntos amarillos en el desierto (ej. Calama o Antofagasta)?"):
            st.write(
                "Los satélites de la NASA detectan **calor intenso en la superficie**, sin distinguir si viene de un árbol o de una máquina. "
                "En el norte de Chile, esas señales fijas corresponden a **fundiciones de cobre (como Chuquicamata), faenas mineras o plantas termosolares**, no a incendios forestales."
            )
        with st.expander("❓ ¿Cómo se leen los colores del calendario y del mapa?"):
            st.write(
                "Usamos una paleta llamada **Cividis** (apta para personas con daltonismo): el **azul oscuro** indica calma o actividad baja, "
                "el **gris/verdoso** indica actividad moderada y el **amarillo brillante** señala concentración crítica o emergencia grave."
            )
        with st.expander("❓ ¿Qué significa 'Lo normal (Mediana de 26 años)'?"):
            st.write(
                "Es el valor típico de un año o mes en tu región entre 2000 y 2025. Usar la mediana evita que megaincendios extremos (como 2017 o 2023) distorsionen lo que consideramos un año normal."
            )
        with st.expander("❓ ¿Esta página sirve para avisar de un incendio que está empezando ahora mismo?"):
            st.write(
                "Esta herramienta está diseñada para **prevención, educación y planificación** usando registros históricos y mensuales. "
                "Si ves humo o fuego activo hoy, llama de inmediato al **130 (CONAF)** o **132 (Bomberos)**."
            )
    else:
        with st.expander("❓ Why do hotspots appear in the northern desert (e.g., Calama)?"):
            st.write("NASA FIRMS detects thermal anomalies including copper smelters, mining operations, and solar thermal plants.")
        with st.expander("❓ How do I read the blue-to-yellow colors?"):
            st.write("Dark blue means low/calm activity, grey-green means moderate, and bright yellow marks severe hotspot concentration (colorblind-safe Cividis scale).")