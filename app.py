import os
import sys

# Asegurar que el directorio actual esté en sys.path para importaciones locales en Streamlit Cloud
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

os.environ['MPLBACKEND'] = 'Agg'

import io
from datetime import datetime
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Módulos especializados de Grupo VALIO
import forensics
import pdf_generator

# Configuración de página
st.set_page_config(
    page_title="Valio | HyRAM+ Hydrogen Safety Tool",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados compactos y ejecutivos
st.markdown("""
<style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    .main-title {
        font-size: 1.85rem;
        font-weight: 800;
        background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
    }
    .sub-title {
        font-size: 0.88rem;
        color: #64748b;
        margin-bottom: 0.8rem;
        line-height: 1.3;
    }
    .valio-header-card {
        background: rgba(14, 165, 233, 0.06);
        border: 1px solid rgba(14, 165, 233, 0.25);
        border-radius: 8px;
        padding: 0.4rem 0.8rem;
        text-align: right;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(226, 232, 240, 0.15);
        border-radius: 10px;
        padding: 0.8rem 1rem;
    }
    .dist-badge {
        padding: 0.35rem 0.6rem;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.4rem;
        display: flex;
        justify-content: space-between;
    }
    .dist-16 { background: rgba(16, 185, 129, 0.15); border-left: 3px solid #10b981; color: #10b981; }
    .dist-47 { background: rgba(245, 158, 11, 0.15); border-left: 3px solid #f59e0b; color: #f59e0b; }
    .dist-98 { background: rgba(249, 115, 22, 0.15); border-left: 3px solid #f97316; color: #f97316; }
    .dist-25 { background: rgba(239, 68, 68, 0.15); border-left: 3px solid #ef4444; color: #ef4444; }

    /* ======================================================== */
    /* LEY DE FITTS: TAMAÑOS TÁCTILES ERGONÓMICOS (>= 44 PX)   */
    /* ======================================================== */
    .stDownloadButton button, 
    .stButton button,
    div[data-testid="stDownloadButton"] button,
    div[data-testid="stButton"] button {
        min-height: 44px !important;
        padding: 0.6rem 1rem !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        transition: all 0.2s ease-in-out !important;
    }
    .stDownloadButton button:hover,
    .stButton button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.25) !important;
    }

    /* Sliders táctiles con manipulador ampliado (24x24 px) para móviles */
    div[data-testid="stSlider"] div[role="slider"] {
        width: 24px !important;
        height: 24px !important;
        background-color: #0ea5e9 !important;
        border: 2px solid #ffffff !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25) !important;
        cursor: grab !important;
        transition: transform 0.15s ease !important;
    }
    div[data-testid="stSlider"] div[role="slider"]:active {
        transform: scale(1.15) !important;
        cursor: grabbing !important;
    }
    div[data-testid="stSlider"] > div {
        padding-top: 0.8rem !important;
        padding-bottom: 0.8rem !important;
    }

    /* Controles de selección y radio con altura táctil ergonómica */
    div[data-testid="stSelectbox"] > div > div {
        min-height: 44px !important;
        border-radius: 8px !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        min-height: 40px !important;
        display: inline-flex !important;
        align-items: center !important;
        padding: 0.25rem 0.6rem !important;
        border-radius: 6px !important;
    }

    /* Botón de apertura de barra lateral en mobile (min 44x44 px) */
    button[data-testid="stSidebarCollapseButton"],
    button[data-testid="baseButton-headerNoPadding"],
    div[data-testid="stSidebarCollapseButton"] button {
        min-width: 44px !important;
        min-height: 44px !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# ENCABEZADO COMPACTO
# ---------------------------------------------------------
col_hdr_1, col_hdr_2 = st.columns([3.2, 1.2])
with col_hdr_1:
    st.markdown('<div class="main-title">⚡ HyRAM+ Consequence & Risk Assessment Tool</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Modelado cuantitativo de consecuencias y distancias de seguridad para Hidrógeno y Combustibles Alternativos | Normas NFPA 2 & API 521</div>',
        unsafe_allow_html=True
    )
with col_hdr_2:
    st.markdown("""
    <div class="valio-header-card">
        <div style="font-weight: 700; color: #0284c7; font-size: 0.88rem;">🛡️ Grupo VALIO S.A.S.</div>
        <div style="font-size: 0.74rem; color: #64748b;">Seguridad de Procesos & PPAM</div>
        <div style="font-size: 0.70rem; margin-top: 0.15rem;"><a href="https://www.grupovalio.com" target="_blank" style="color: #0ea5e9; text-decoration: none;">www.grupovalio.com</a></div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# MOTOR DE CÁLCULO
# ---------------------------------------------------------
@st.cache_data(show_spinner="Calculando dinámica de fluidos y radiación con HyRAM+...")
def compute_hyram_jet_flame(fuel_name, pres_pa, temp_k, orif_diam_m, cd, amb_pres_pa, amb_temp_k, rel_humidity):
    from hyram.phys._comps import Fluid, Orifice, NozzleFlow
    from hyram.phys._flame import Flame

    fuel = Fluid(fuel_name, P=pres_pa, T=temp_k)
    orifice = Orifice(orif_diam_m, Cd=cd)
    ambient = Fluid('air', P=amb_pres_pa, T=amb_temp_k)
    
    nozzle = NozzleFlow(fuel, orifice, amb_pres_pa)
    mass_flow = nozzle.mdot
    choked = nozzle.choked

    flame = Flame(fuel, orifice, ambient)
    flame_length = flame.get_visible_length()
    s_rad = flame.get_srad()
    
    thresholds = [1600, 4700, 9800, 25000]
    distances = {}
    for q in thresholds:
        try:
            d = flame.calc_distance_to_heatflux(q, direction='x', RH=rel_humidity)
            distances[q] = float(d)
        except Exception:
            distances[q] = None

    return {
        "mass_flow": mass_flow,
        "choked": choked,
        "flame_length": flame_length,
        "s_rad": s_rad,
        "distances": distances,
        "fuel_density": fuel.rho
    }

# ---------------------------------------------------------
# PRESETS DE ESCENARIOS TÍPICOS (LEY DE HICK)
# ---------------------------------------------------------
PRESET_SCENARIOS = {
    "Personalizado (Ajuste Manual)": None,
    "Fuga Menor en Racor / Fitting (1 mm @ 700 bar H₂)": {
        "fuel": "Hidrógeno (H₂)", "pres_unit": "bar", "pres_val": 700.0,
        "orif_unit": "mm", "orif_val": 1.0, "temp_c": 20, "cd": 0.85
    },
    "Rotura de Manguera en Dispensador (4 mm @ 350 bar H₂)": {
        "fuel": "Hidrógeno (H₂)", "pres_unit": "bar", "pres_val": 350.0,
        "orif_unit": "mm", "orif_val": 4.0, "temp_c": 20, "cd": 0.85
    },
    "Fuga en Tubing de Rack de Almacenamiento (6 mm @ 200 bar H₂)": {
        "fuel": "Hidrógeno (H₂)", "pres_unit": "bar", "pres_val": 200.0,
        "orif_unit": "mm", "orif_val": 6.0, "temp_c": 20, "cd": 0.85
    },
    "Falla Mayor en Tubería de Gas Natural (12 mm @ 50 bar CH₄)": {
        "fuel": "Metano (CH₄)", "pres_unit": "bar", "pres_val": 50.0,
        "orif_unit": "mm", "orif_val": 12.0, "temp_c": 20, "cd": 0.85
    }
}

# Inicialización de estado para widgets reactivos
if "widget_fuel" not in st.session_state:
    st.session_state.widget_fuel = "Hidrógeno (H₂)"
if "widget_pres_unit" not in st.session_state:
    st.session_state.widget_pres_unit = "bar"
if "widget_pres_bar" not in st.session_state:
    st.session_state.widget_pres_bar = 200.0
if "widget_pres_mpa" not in st.session_state:
    st.session_state.widget_pres_mpa = 20.0
if "widget_pres_psi" not in st.session_state:
    st.session_state.widget_pres_psi = 2900.0
if "widget_orif_unit" not in st.session_state:
    st.session_state.widget_orif_unit = "mm"
if "widget_orif_mm" not in st.session_state:
    st.session_state.widget_orif_mm = 2.0
if "widget_orif_in" not in st.session_state:
    st.session_state.widget_orif_in = 0.08
if "widget_temp_c" not in st.session_state:
    st.session_state.widget_temp_c = 20
if "widget_cd" not in st.session_state:
    st.session_state.widget_cd = 0.85

def apply_preset():
    choice = st.session_state.preset_selector
    if choice in PRESET_SCENARIOS and PRESET_SCENARIOS[choice] is not None:
        p = PRESET_SCENARIOS[choice]
        st.session_state.widget_fuel = p["fuel"]
        st.session_state.widget_pres_unit = p["pres_unit"]
        st.session_state.widget_pres_bar = p["pres_val"]
        st.session_state.widget_pres_mpa = round(p["pres_val"] * 0.1, 2)
        st.session_state.widget_pres_psi = round(p["pres_val"] * 14.5038, 1)
        st.session_state.widget_orif_unit = p["orif_unit"]
        st.session_state.widget_orif_mm = p["orif_val"]
        st.session_state.widget_orif_in = round(p["orif_val"] / 25.4, 2)
        st.session_state.widget_temp_c = p["temp_c"]
        st.session_state.widget_cd = p["cd"]

# ---------------------------------------------------------
# BARRA LATERAL: PARÁMETROS DE OPERACIÓN
# ---------------------------------------------------------
st.sidebar.header("🎯 Escenarios de Referencia (Ley de Hick)")
st.sidebar.selectbox(
    "Cargar Preset Típico",
    list(PRESET_SCENARIOS.keys()),
    key="preset_selector",
    on_change=apply_preset,
    help="Configura automáticamente parámetros de referencia de la industria reduciendo la sobrecarga de decisión."
)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Parámetros de Operación")

fuel_option = st.sidebar.selectbox(
    "Fluido Combustible",
    ["Hidrógeno (H₂)", "Metano (CH₄)", "Propano (C₃H₈)"],
    key="widget_fuel",
    help="Gas combustible a evaluar según modelos de termodinámica de fluidos reales."
)
fuel_key_map = {
    "Hidrógeno (H₂)": "H2",
    "Metano (CH₄)": "CH4",
    "Propano (C₃H₈)": "propane"
}
selected_fuel = fuel_key_map[fuel_option]

st.sidebar.subheader("Presión del Sistema")
pres_unit = st.sidebar.radio("Unidad de Presión", ["bar", "MPa", "psi"], key="widget_pres_unit", horizontal=True)

if pres_unit == "bar":
    pres_val = st.sidebar.number_input("Presión de Almacenamiento (bar)", min_value=1.5, max_value=1000.0, key="widget_pres_bar", step=10.0, help="Presión en bar manométrico/absoluto.")
    pres_pa = pres_val * 1e5
elif pres_unit == "MPa":
    pres_val = st.sidebar.number_input("Presión de Almacenamiento (MPa)", min_value=0.15, max_value=100.0, key="widget_pres_mpa", step=1.0, help="Presión en megapascales.")
    pres_pa = pres_val * 1e6
else:
    pres_val = st.sidebar.number_input("Presión de Almacenamiento (psi)", min_value=20.0, max_value=14500.0, key="widget_pres_psi", step=100.0, help="Presión en psi.")
    pres_pa = pres_val * 6894.76

st.sidebar.subheader("Temperatura del Gas")
temp_c = st.sidebar.slider("Temperatura (°C)", min_value=-50, max_value=80, key="widget_temp_c", step=1, help="Temperatura de almacenamiento del fluido.")
temp_k = temp_c + 273.15

st.sidebar.subheader("Geometría de la Fuga")
orif_unit = st.sidebar.radio("Unidad Diámetro", ["mm", "pulgadas (in)"], key="widget_orif_unit", horizontal=True)

if orif_unit == "mm":
    orif_diam_val = st.sidebar.slider("Diámetro del Orificio (mm)", min_value=0.5, max_value=25.0, key="widget_orif_mm", step=0.5, help="Diámetro equivalente de la rotura.")
    orif_diam_m = orif_diam_val * 1e-3
else:
    orif_diam_val = st.sidebar.slider("Diámetro del Orificio (in)", min_value=0.02, max_value=1.0, key="widget_orif_in", step=0.01, help="Diámetro de fuga en pulgadas.")
    orif_diam_m = orif_diam_val * 0.0254

cd_coeff = st.sidebar.slider("Coeficiente de Descarga (Cd)", min_value=0.5, max_value=1.0, key="widget_cd", step=0.05, help="Coeficiente de descarga según geometría del orificio.")

with st.sidebar.expander("🌐 Condiciones Ambientales", expanded=False):
    amb_temp_c = st.slider("Temperatura Ambiente (°C)", min_value=-20, max_value=50, value=25)
    amb_temp_k = amb_temp_c + 273.15
    amb_pres_kpa = st.number_input("Presión Atmosférica (kPa)", value=101.325)
    amb_pres_pa = amb_pres_kpa * 1000
    rel_humidity = st.slider("Humedad Relativa (%)", min_value=10, max_value=100, value=80) / 100.0

# ---------------------------------------------------------
# EJECUCIÓN DEL CÁLCULO
# ---------------------------------------------------------
try:
    results = compute_hyram_jet_flame(
        selected_fuel, pres_pa, temp_k, orif_diam_m, cd_coeff,
        amb_pres_pa, amb_temp_k, rel_humidity
    )
    calc_success = True
except Exception as e:
    st.error(f"Error al ejecutar cálculo de HyRAM+: {str(e)}")
    calc_success = False

if calc_success:
    input_params = {
        "fluid_name": fuel_option,
        "pressure_val": pres_val,
        "pressure_unit": pres_unit,
        "pressure_pa": pres_pa,
        "temp_c": temp_c,
        "temp_k": temp_k,
        "orif_val": orif_diam_val,
        "orif_unit": orif_unit,
        "orif_m": orif_diam_m,
        "cd": cd_coeff,
        "amb_temp_c": amb_temp_c,
        "amb_temp_k": amb_temp_k,
        "amb_pres_kpa": amb_pres_kpa,
        "rh": rel_humidity * 100
    }
    
    # Generar sello interno de certificación para el PDF
    seal_data = forensics.generate_tamper_seal(input_params, {
        "mass_flow": results['mass_flow'],
        "flame_length": results['flame_length'],
        "s_rad": results['s_rad']
    })

    d_16 = results['distances'].get(1600)
    d_47 = results['distances'].get(4700)
    d_98 = results['distances'].get(9800)
    d_25 = results['distances'].get(25000)

    # Indicador de Criticidad del Escenario (Ley de Hick / Feedback rápido)
    d_crit = d_16 or 0
    if d_crit < 5.0:
        crit_badge = '<span style="background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid #10b981; padding: 0.2rem 0.6rem; border-radius: 6px; font-weight: 700; font-size: 0.78rem;">🟢 Impacto Térmico Bajo (< 5 m)</span>'
    elif d_crit < 15.0:
        crit_badge = '<span style="background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid #f59e0b; padding: 0.2rem 0.6rem; border-radius: 6px; font-weight: 700; font-size: 0.78rem;">🟡 Impacto Térmico Moderado (5 - 15 m)</span>'
    else:
        crit_badge = '<span style="background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid #ef4444; padding: 0.2rem 0.6rem; border-radius: 6px; font-weight: 700; font-size: 0.78rem;">🔴 Impacto Térmico Mayor / Crítico (> 15 m)</span>'

    st.markdown(f'<div style="margin-bottom: 0.6rem; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;"><span style="font-size: 0.82rem; color: #64748b; font-weight: 600;">Simulación de Consecuencias Termodinámicas en Tiempo Real</span>{crit_badge}</div>', unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 1. BLOQUE DE KPIS (PARTE SUPERIOR)
    # ---------------------------------------------------------
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(
            label="Tasa de Fuga Másica",
            value=f"{results['mass_flow'] * 1000:.2f} g/s",
            delta=f"{results['mass_flow'] * 3600:.2f} kg/h",
            help="Caudal másico descargado a través del orificio."
        )
    with m2:
        st.metric(
            label="Longitud de Llama Visible",
            value=f"{results['flame_length']:.2f} m",
            delta="Chorro turbulento",
            help="Longitud axial de llama visible (Ekoto et al. 2014)."
        )
    with m3:
        st.metric(
            label="Potencia Radiativa Total",
            value=f"{results['s_rad'] / 1000:.1f} kW",
            delta=f"{results['s_rad'] / 1e6:.3f} MW",
            help="Potencia de radiación emitida por la combustión."
        )
    with m4:
        regime = "Sónico (Choked)" if results['choked'] else "Subsónico"
        st.metric(
            label="Régimen de Escape",
            value=regime,
            delta="Flujo crítico" if results['choked'] else "Normal",
            help="Estado del flujo en la sección del orificio."
        )

    st.markdown("<hr style='margin-top: 0.5rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 2. VISTA PRINCIPAL: DISTANCIAS + MAPA 2D EN PARALELO
    # ---------------------------------------------------------
    col_dist, col_map = st.columns([1, 1.25], gap="medium")

    with col_dist:
        st.subheader("🔥 Distancias de Separación")
        
        # Resumen en tarjetas compactas
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="dist-badge dist-16">
                <span>1.6 kW/m² (Público)</span>
                <span><b>{d_16:.2f} m</b></span>
            </div>
            <div class="dist-badge dist-47">
                <span>4.7 kW/m² (Escape)</span>
                <span><b>{d_47:.2f} m</b></span>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="dist-badge dist-98">
                <span>9.8 kW/m² (Equipos)</span>
                <span><b>{d_98:.2f} m</b></span>
            </div>
            <div class="dist-badge dist-25">
                <span>25 kW/m² (Crítico)</span>
                <span><b>{d_25:.2f} m</b></span>
            </div>
            """, unsafe_allow_html=True)

        # Gráfico horizontal de distancias
        df_dist = pd.DataFrame({
            "Nivel de Radiación": ["1.6 kW/m² (Público)", "4.7 kW/m² (Escape)", "9.8 kW/m² (Equipos)", "25 kW/m² (Crítico)"],
            "Distancia (m)": [d_16 or 0, d_47 or 0, d_98 or 0, d_25 or 0],
            "Color": ["#10b981", "#f59e0b", "#f97316", "#ef4444"]
        })
        fig_bar = px.bar(
            df_dist, x="Distancia (m)", y="Nivel de Radiación",
            orientation='h',
            color="Nivel de Radiación",
            color_discrete_sequence=["#10b981", "#f59e0b", "#f97316", "#ef4444"],
        )
        fig_bar.update_layout(
            showlegend=False,
            height=260,
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_map:
        st.subheader("🎯 Mapa 2D de Zonas de Peligro")
        
        # Gráfico de isocontornos
        fig_2d = go.Figure()

        def make_ellipse_points(a, b, n=100):
            theta = np.linspace(0, 2*np.pi, n)
            return a * np.cos(theta) + a*0.4, b * np.sin(theta)

        if d_16:
            x_16, y_16 = make_ellipse_points(d_16, d_16*0.65)
            fig_2d.add_trace(go.Scatter(
                x=x_16, y=y_16, fill="toself", fillcolor="rgba(16, 185, 129, 0.15)",
                line=dict(color="#10b981", width=2), name="1.6 kW/m² (Segura)"
            ))

        if d_47:
            x_47, y_47 = make_ellipse_points(d_47, d_47*0.65)
            fig_2d.add_trace(go.Scatter(
                x=x_47, y=y_47, fill="toself", fillcolor="rgba(245, 158, 11, 0.25)",
                line=dict(color="#f59e0b", width=2), name="4.7 kW/m² (Escape)"
            ))

        if d_98:
            x_98, y_98 = make_ellipse_points(d_98, d_98*0.65)
            fig_2d.add_trace(go.Scatter(
                x=x_98, y=y_98, fill="toself", fillcolor="rgba(249, 115, 22, 0.35)",
                line=dict(color="#f97316", width=2), name="9.8 kW/m² (Equipos)"
            ))

        if d_25:
            x_25, y_25 = make_ellipse_points(d_25, d_25*0.65)
            fig_2d.add_trace(go.Scatter(
                x=x_25, y=y_25, fill="toself", fillcolor="rgba(239, 68, 68, 0.5)",
                line=dict(color="#ef4444", width=2), name="25 kW/m² (Llama)"
            ))

        fig_2d.add_trace(go.Scatter(
            x=[0], y=[0], mode="markers+text", marker=dict(color="cyan", size=10, symbol="cross"),
            text=["Origen (0,0)"], textposition="top left", name="Punto de Fuga"
        ))

        fig_2d.add_trace(go.Scatter(
            x=[0, results['flame_length']], y=[0, 0], mode="lines+markers",
            line=dict(color="#38bdf8", width=3, dash="dot"),
            name=f"Llama ({results['flame_length']:.2f} m)"
        ))

        fig_2d.update_layout(
            xaxis_title="Distancia Axial X (m)",
            yaxis_title="Distancia Transversal Y (m)",
            yaxis=dict(scaleanchor="x", scaleratio=1),
            height=340,
            template="plotly_dark",
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_2d, use_container_width=True)

    # ---------------------------------------------------------
    # 3. MATRIZ NORMATIVA Y DESCARGAS
    # ---------------------------------------------------------
    st.markdown("---")
    col_table, col_dl = st.columns([1.5, 1], gap="large")

    with col_table:
        st.markdown("##### 📋 Criterios Normativos (NFPA 2 / API 521 / ISO 19880-1)")
        df_summary = pd.DataFrame([
            {"Norma": "NFPA 2 / API 521", "Umbral": "1.6 kW/m²", "Criterio": "Permanencia continua de personas sin EPP", "Distancia": f"{d_16:.2f} m" if d_16 else "N/A"},
            {"Norma": "NFPA 2 / API 521", "Umbral": "4.7 kW/m²", "Criterio": "Escape rápido de personal (hasta 30 s)", "Distancia": f"{d_47:.2f} m" if d_47 else "N/A"},
            {"Norma": "API 521 / NFPA 59A", "Umbral": "9.8 kW/m²", "Criterio": "Protección de equipos sin aislamiento ignífugo", "Distancia": f"{d_98:.2f} m" if d_98 else "N/A"},
            {"Norma": "API 521", "Umbral": "25.0 kW/m²", "Criterio": "Peligro estructural inminente y combustión", "Distancia": f"{d_25:.2f} m" if d_25 else "N/A"}
        ])
        st.dataframe(df_summary, use_container_width=True, hide_index=True)

    with col_dl:
        st.markdown("##### 📥 Exportar Resultados")
        try:
            pdf_bytes = pdf_generator.build_hyram_pdf_report(input_params, results, seal_data)
            st.download_button(
                label="📄 Descargar Informe Técnico Oficial (PDF)",
                data=pdf_bytes,
                file_name=f"Informe_HyRAM_{selected_fuel}_{pres_val}{pres_unit}_{seal_data['certificate_id']}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as pdf_err:
            st.error(f"Error generando PDF: {str(pdf_err)}")

        csv_data = df_summary.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📊 Descargar Matriz de Datos (CSV)",
            data=csv_data,
            file_name=f"reporte_hyram_{selected_fuel}_{pres_val}{pres_unit}.csv",
            mime="text/csv",
            use_container_width=True
        )

        with st.popover("🔬 Ver Ecuaciones de Cálculo"):
            st.markdown("**1. Caudal Másico en Régimen Sónico (Choked):**")
            st.latex(r"\dot{m} = C_d A P_0 \sqrt{\frac{\gamma M}{R T_0}} \left(\frac{2}{\gamma + 1}\right)^{\frac{\gamma+1}{2(\gamma-1)}}")
            st.markdown("**2. Condición de Flujo Crítico:**")
            st.latex(r"\frac{P_{crit}}{P_0} = \left(\frac{2}{\gamma + 1}\right)^{\frac{\gamma}{\gamma - 1}}")
            st.markdown("**3. Flujo Térmico Radiante:**")
            st.latex(r"q'' = \frac{\tau_{atm} \cdot \eta_{rad} \cdot \dot{m} \cdot \Delta H_c}{4 \pi R^2}")

# ---------------------------------------------------------
# 4. FOOTER: METODOLOGÍA & MARCO LEGAL (EXPANDERS)
# ---------------------------------------------------------
st.markdown("---")

with st.expander("📚 Metodología Científica y Formulación (HyRAM+ v6.1)"):
    st.markdown(r"""
    **HyRAM+ (Hydrogen Plus Other Alternative Fuels Risk Assessment Models)** es un software científico de referencia global desarrollado por **Sandia National Laboratories** para el Departamento de Energía de los EE. UU. (DOE).

    * **Modelo de Chorro Térmico (Jet Fire):** Implementa las formulaciones de conservación de masa, momento y energía desarrolladas por *Ekoto et al.* (International Journal of Hydrogen Energy, 2014) y los modelos de tobera nocional de *Yüceil & Ötügen*.
    * **Fracción Radiativa:** Modela la radiación térmica emitida por la combustión de chorros turbulentos de hidrógeno y gas natural considerando absorción atmosférica por vapor de agua y dióxido de carbono.
    * **Validación Experimental:** Validado mediante ensayos a gran escala en las instalaciones de combustión de Sandia National Laboratories en Livermore, California.
    
    *Referencias:*
    * [Portal Oficial de HyRAM en Sandia Labs](https://hyram.sandia.gov/)
    * [Repositorio Open Source en GitHub (Sandia Labs)](https://github.com/sandialabs/hyram)
    """)

with st.expander("⚖️ Marco Legal, Exención de Responsabilidad y Licencia GNU GPL-3.0"):
    st.markdown("""
    **Cláusula de Exclusión ("AS IS"):**  
    Esta herramienta web ha sido desarrollada por **Grupo VALIO S.A.S.** con fines **exclusivamente pedagógicos, académicos y de evaluación técnica preliminar**.  
    Los resultados generados no reemplazan estudios formales de Análisis Cuantitativo de Riesgo (QRA), Planes de Prevención de Accidentes Mayores (PPAM), ni memorias de cálculo periciales suscritas por ingenieros debidamente matriculados.  
    Ni Grupo VALIO S.A.S. ni sus colaboradores asumen responsabilidad alguna por pérdidas, daños o decisiones operativas derivadas del uso de esta herramienta.

    **Régimen de Licencia Abierta:**  
    El motor de cálculo utiliza **HyRAM+ v6.1**, licenciado bajo **GNU General Public License v3.0 (GPL-3.0)** por Sandia National Laboratories / NTESS / US DOE.  
    La interfaz y herramientas de visualización de Grupo VALIO respetan los términos de dicha licencia de código abierto sin implicar respaldo de agencias gubernamentales.
    """)

st.caption("Grupo VALIO S.A.S. · Seguridad de Procesos & Prevención de Accidentes Mayores (PPAM) · [www.grupovalio.com](https://www.grupovalio.com) © 2026")
