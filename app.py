import os
os.environ['MPLBACKEND'] = 'Agg'

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Valio | HyRAM+ Hydrogen Safety Tool",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(226, 232, 240, 0.15);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 1.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
col_header_a, col_header_b = st.columns([3, 1])
with col_header_a:
    st.markdown('<div class="main-title">⚡ HyRAM+ Consequence & Risk Assessment Tool</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Modelado cuantitativo de consecuencias y distancias de seguridad para Hidrógeno y Combustibles Alternativos | Desarrollado por Sandia National Laboratories</div>', unsafe_allow_html=True)
with col_header_b:
    st.info("🏢 **Valio Recursos**\n\nHerramienta Técnica en Línea")

# Computation engine with caching
@st.cache_data(show_spinner="Calculando dinámica de fluidos y radiación con HyRAM+...")
def compute_hyram_jet_flame(fuel_name, pres_pa, temp_k, orif_diam_m, cd, amb_pres_pa, amb_temp_k, rel_humidity):
    from hyram.phys._comps import Fluid, Orifice, NozzleFlow
    from hyram.phys._flame import Flame

    # Create fluids
    fuel = Fluid(fuel_name, P=pres_pa, T=temp_k)
    orifice = Orifice(orif_diam_m, Cd=cd)
    ambient = Fluid('air', P=amb_pres_pa, T=amb_temp_k)
    
    # Flow calculation
    nozzle = NozzleFlow(fuel, orifice, amb_pres_pa)
    mass_flow = nozzle.mdot  # kg/s
    choked = nozzle.choked

    # Flame calculation
    flame = Flame(fuel, orifice, ambient)
    flame_length = flame.get_visible_length()
    s_rad = flame.get_srad()  # Watts
    
    # Distance to heat flux thresholds (W/m2)
    thresholds = [1600, 4700, 9800, 25000]
    distances = {}
    for q in thresholds:
        try:
            d = flame.calc_distance_to_heatflux(q, direction='x', RH=rel_humidity)
            distances[q] = float(d)
        except Exception:
            distances[q] = None

    # Calculate axial heat flux profile
    max_d = max([d for d in distances.values() if d is not None] + [flame_length * 2.5])
    x_points = np.linspace(0.1, max(max_d * 1.3, 5.0), 60)
    fluxes = []
    for x in x_points:
        try:
            # WaistLoc ~ 0.75 along flame
            f_val = flame.calc_distance_to_heatflux(q=None, direction='x')
        except Exception:
            pass

    return {
        "mass_flow": mass_flow,
        "choked": choked,
        "flame_length": flame_length,
        "s_rad": s_rad,
        "distances": distances,
        "fuel_density": fuel.rho,
        "max_d": max_d
    }

# Sidebar inputs
st.sidebar.header("⚙️ Parámetros de Operación")

fuel_option = st.sidebar.selectbox(
    "Fluido Combustible",
    ["Hidrógeno (H₂)", "Metano (CH₄)", "Propano (C₃H₈)"],
    index=0
)
fuel_key_map = {
    "Hidrógeno (H₂)": "H2",
    "Metano (CH₄)": "CH4",
    "Propano (C₃H₈)": "propane"
}
selected_fuel = fuel_key_map[fuel_option]

# Pressure input
st.sidebar.subheader("Presión del Sistema")
pres_unit = st.sidebar.radio("Unidad de Presión", ["bar", "MPa", "psi"], horizontal=True)
if pres_unit == "bar":
    pres_val = st.sidebar.number_input("Presión de Almacenamiento (bar)", min_value=1.5, max_value=1000.0, value=200.0, step=10.0)
    pres_pa = pres_val * 1e5
elif pres_unit == "MPa":
    pres_val = st.sidebar.number_input("Presión de Almacenamiento (MPa)", min_value=0.15, max_value=100.0, value=20.0, step=1.0)
    pres_pa = pres_val * 1e6
else:
    pres_val = st.sidebar.number_input("Presión de Almacenamiento (psi)", min_value=20.0, max_value=14500.0, value=2900.0, step=100.0)
    pres_pa = pres_val * 6894.76

# Temperature input
st.sidebar.subheader("Temperatura del Gas")
temp_c = st.sidebar.slider("Temperatura (°C)", min_value=-50, max_value=80, value=20, step=1)
temp_k = temp_c + 273.15

# Orifice input
st.sidebar.subheader("Geometría de la Fuga")
orif_unit = st.sidebar.radio("Unidad Diámetro", ["mm", "pulgadas (in)"], horizontal=True)
if orif_unit == "mm":
    orif_diam_val = st.sidebar.slider("Diámetro del Orificio (mm)", min_value=0.5, max_value=25.0, value=2.0, step=0.5)
    orif_diam_m = orif_diam_val * 1e-3
else:
    orif_diam_val = st.sidebar.slider("Diámetro del Orificio (in)", min_value=0.02, max_value=1.0, value=0.08, step=0.01)
    orif_diam_m = orif_diam_val * 0.0254

cd_coeff = st.sidebar.slider("Coeficiente de Descarga (Cd)", min_value=0.5, max_value=1.0, value=0.85, step=0.05)

# Ambient parameters
with st.sidebar.expander("🌐 Condiciones Ambientales"):
    amb_temp_c = st.slider("Temperatura Ambiente (°C)", min_value=-20, max_value=50, value=25)
    amb_temp_k = amb_temp_c + 273.15
    amb_pres_kpa = st.number_input("Presión Atmosférica (kPa)", value=101.325)
    amb_pres_pa = amb_pres_kpa * 1000
    rel_humidity = st.slider("Humedad Relativa (%)", min_value=10, max_value=100, value=80) / 100.0

# Run calculations
try:
    results = compute_hyram_jet_flame(
        selected_fuel, pres_pa, temp_k, orif_diam_m, cd_coeff,
        amb_pres_pa, amb_temp_k, rel_humidity
    )
    calc_success = True
except Exception as e:
    st.error(f"Error al ejecutar cálculo de HyRAM: {str(e)}")
    calc_success = False

if calc_success:
    # Key KPI Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(
            label="Tasa de Fuga Masiva",
            value=f"{results['mass_flow'] * 1000:.2f} g/s",
            delta=f"{results['mass_flow'] * 3600:.2f} kg/h"
        )
    with m2:
        st.metric(
            label="Longitud de Llama Visible",
            value=f"{results['flame_length']:.2f} m",
            delta="Chorro turbulento"
        )
    with m3:
        st.metric(
            label="Potencia Radiativa Total",
            value=f"{results['s_rad'] / 1000:.1f} kW",
            delta=f"{results['s_rad'] / 1e6:.3f} MW"
        )
    with m4:
        regime = "Sónico (Choked)" if results['choked'] else "Subsónico"
        st.metric(
            label="Régimen de Escape",
            value=regime,
            delta="Flujo crítico" if results['choked'] else "Normal"
        )

    st.markdown("---")

    # Main Tabs
    tab_rad, tab_zones, tab_standards, tab_info = st.tabs([
        "🔥 Distancias de Seguridad y Radiación",
        "🎯 Mapa 2D de Zonas de Peligro",
        "📋 Criterios Normativos (NFPA 2 / API)",
        "ℹ️ Acerca de HyRAM+"
    ])

    with tab_rad:
        st.subheader("Distancias de Separación por Nivel de Flujo Térmico")
        st.write("Distancia axial desde el punto de fuga hasta los límites de radiación térmica especificados por estándares internacionales:")

        c_dist_1, c_dist_2 = st.columns([1, 1])
        
        d_16 = results['distances'].get(1600)
        d_47 = results['distances'].get(4700)
        d_98 = results['distances'].get(9800)
        d_25 = results['distances'].get(25000)

        with c_dist_1:
            st.markdown(f"""
            * **🟢 1.6 kW/m² (Exposición Continua Segura):**  
              **`{d_16:.2f} m`** — Seguro para permanencia continua del público sin equipo de protección.
            * **🟡 4.7 kW/m² (Límite de Escape Rápido):**  
              **`{d_47:.2f} m`** — Dolor en ~15-20 s; permite evacuación rápida sin quemaduras de 2do grado.
            * **🟠 9.8 kW/m² (Límite de Daño a Equipos):**  
              **`{d_98:.2f} m`** — Quemaduras en <5 s; daño a instrumentación y tuberías no protegidas.
            * **🔴 25.0 kW/m² (Radiación Destructiva):**  
              **`{d_25:.2f} m`** — Ignición de madera y materiales plásticos; daño estructural rápido.
            """)

        with c_dist_2:
            # Bar chart of safety distances
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
                title="Distancias de Seguridad Requeridas (m)"
            )
            fig_bar.update_layout(showlegend=False, height=280, margin=dict(l=10, r=10, t=35, b=10))
            st.plotly_chart(fig_bar, use_container_width=True)

    with tab_zones:
        st.subheader("Huella Espacial 2D de Zonas de Riesgo Térmico (Plan View)")
        st.write("Vista superior interactiva de los perímetros de seguridad concéntricos alrededor del punto de fuga (0,0):")

        # Create 2D footprint diagram
        fig_2d = go.Figure()

        # Generate ellipses / zones for each threshold
        def make_ellipse_points(a, b, n=100):
            theta = np.linspace(0, 2*np.pi, n)
            return a * np.cos(theta) + a*0.4, b * np.sin(theta)

        if d_16:
            x_16, y_16 = make_ellipse_points(d_16, d_16*0.65)
            fig_2d.add_trace(go.Scatter(
                x=x_16, y=y_16, fill="toself", fillcolor="rgba(16, 185, 129, 0.15)",
                line=dict(color="#10b981", width=2), name="Zona Segura (1.6 kW/m²)"
            ))

        if d_47:
            x_47, y_47 = make_ellipse_points(d_47, d_47*0.65)
            fig_2d.add_trace(go.Scatter(
                x=x_47, y=y_47, fill="toself", fillcolor="rgba(245, 158, 11, 0.25)",
                line=dict(color="#f59e0b", width=2), name="Zona de Escape (4.7 kW/m²)"
            ))

        if d_98:
            x_98, y_98 = make_ellipse_points(d_98, d_98*0.65)
            fig_2d.add_trace(go.Scatter(
                x=x_98, y=y_98, fill="toself", fillcolor="rgba(249, 115, 22, 0.35)",
                line=dict(color="#f97316", width=2), name="Zona de Daño a Equipos (9.8 kW/m²)"
            ))

        if d_25:
            x_25, y_25 = make_ellipse_points(d_25, d_25*0.65)
            fig_2d.add_trace(go.Scatter(
                x=x_25, y=y_25, fill="toself", fillcolor="rgba(239, 68, 68, 0.5)",
                line=dict(color="#ef4444", width=2), name="Zona Crítica / Llama (25 kW/m²)"
            ))

        # Origin leak point
        fig_2d.add_trace(go.Scatter(
            x=[0], y=[0], mode="markers+text", marker=dict(color="blue", size=12, symbol="cross"),
            text=["Punto de Fuga (0,0)"], textposition="top left", name="Origen Fuga"
        ))

        # Flame vector line
        fig_2d.add_trace(go.Scatter(
            x=[0, results['flame_length']], y=[0, 0], mode="lines+markers",
            line=dict(color="#38bdf8", width=4, dash="dot"),
            name=f"Llama Visible ({results['flame_length']:.2f} m)"
        ))

        fig_2d.update_layout(
            title="Isocontornos de Radiación Térmica (m)",
            xaxis_title="Distancia Axial X (m)",
            yaxis_title="Distancia Transversal Y (m)",
            yaxis=dict(scaleanchor="x", scaleratio=1),
            height=500,
            template="plotly_dark",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_2d, use_container_width=True)

    with tab_standards:
        st.subheader("Tabla de Cumplimiento Normativo (NFPA 2 / API 521 / ISO 19880-1)")
        df_summary = pd.DataFrame([
            {"Norma": "NFPA 2 / API 521", "Umbral Térmico": "1.6 kW/m²", "Criterio de Aceptabilidad": "Exposición prolongada continua de personas", "Distancia Requerida": f"{d_16:.2f} m" if d_16 else "N/A"},
            {"Norma": "NFPA 2 / API 521", "Umbral Térmico": "4.7 kW/m²", "Criterio de Aceptabilidad": "Tiempo de escape de personal calificado (hasta 30 s)", "Distancia Requerida": f"{d_47:.2f} m" if d_47 else "N/A"},
            {"Norma": "API 521 / NFPA 59A", "Umbral Térmico": "9.8 kW/m²", "Criterio de Aceptabilidad": "Protección de equipos sin revestimiento resistente al fuego", "Distancia Requerida": f"{d_98:.2f} m" if d_98 else "N/A"},
            {"Norma": "API 521", "Umbral Térmico": "25.0 kW/m²", "Criterio de Aceptabilidad": "Peligro estructural inminente y combustión de materiales", "Distancia Requerida": f"{d_25:.2f} m" if d_25 else "N/A"}
        ])
        st.dataframe(df_summary, use_container_width=True, hide_index=True)

        # Download report
        csv_data = df_summary.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Reporte de Distancias (CSV)",
            data=csv_data,
            file_name=f"reporte_seguridad_hyram_{selected_fuel}_{pres_val}{pres_unit}.csv",
            mime="text/csv"
        )

    with tab_info:
        st.subheader("Metodología y Base Científica")
        st.markdown("""
        **HyRAM+ (Hydrogen Plus Other Alternative Fuels Risk Assessment Models)** es un software científico desarrollado por **Sandia National Laboratories** para el Departamento de Energía de los EE. UU. (DOE).

        * **Modelo de Chorro Térmico:** Implementa las formulaciones de conservación de masa, momento y energía desarrolladas por *Ekoto et al.* (International Journal of Hydrogen Energy, 2014) y los modelos de tobera nocional de *Yüceil & Ötügen*.
        * **Fracción Radiativa:** Modela la radiación térmica emitida por la combustión de chorros turbulentos de hidrógeno y gas natural considerando absorción atmosférica por vapor de agua y dióxido de carbono.
        * **Validación Experimental:** Validado mediante ensayos a gran escala en las instalaciones de combustión de Sandia National Laboratories.
        
        🔗 Enlaces oficiales:
        * [Portal Oficial de HyRAM en Sandia Labs](https://hyram.sandia.gov/)
        * [Repositorio Open Source en GitHub](https://github.com/sandialabs/hyram)
        """)

st.markdown("---")
st.caption("Valio Inmobiliaria & Industrial Safety © 2026 | Desarrollado con base en Sandia National Laboratories HyRAM+ v6.1")
