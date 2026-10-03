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

# Estilos personalizados y diseño ejecutivo
st.markdown("""
<style>
    .main-title {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 0.98rem;
        color: #64748b;
        margin-bottom: 1rem;
        line-height: 1.4;
    }
    .valio-badge {
        display: inline-block;
        background: rgba(14, 165, 233, 0.1);
        border: 1px solid rgba(14, 165, 233, 0.3);
        border-radius: 6px;
        padding: 0.2rem 0.6rem;
        font-size: 0.78rem;
        font-weight: 600;
        color: #0284c7;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(226, 232, 240, 0.15);
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
    }
    .legal-card {
        background: rgba(15, 23, 42, 0.04);
        border: 1px solid #cbd5e1;
        border-left: 4px solid #0284c7;
        border-radius: 6px;
        padding: 0.85rem 1.1rem;
        font-size: 0.82rem;
        line-height: 1.45;
        color: #475569;
    }
    .seal-pill {
        font-family: monospace;
        font-size: 0.75rem;
        background: #0f172a;
        color: #38bdf8;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        border: 1px solid #1e293b;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 1.2rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# DIÁLOGOS MODALES (MICRO-VENTANAS TEÓRICAS Y LEGALES)
# ---------------------------------------------------------

@st.dialog("⚖️ Marco Legal, Exención de Responsabilidad & Licencia GPL-3.0")
def modal_legal_shield():
    st.markdown("""
    ### 🛡️ Declaración Jurídica y Cláusula de Exclusión ("AS IS")
    Esta herramienta web ha sido desarrollada por **Grupo VALIO S.A.S.** con fines **exclusivamente pedagógicos, académicos y de evaluación técnica preliminar**.
    
    * **No sustituye ingeniería formal:** Los resultados generados no reemplazan estudios formales de Análisis Cuantitativo de Riesgo (QRA), memorias de cálculo periciales, ni ingenierías de detalle suscritas por profesionales legalmente matriculados.
    * **Inmunidad ante daños:** Ni Grupo VALIO S.A.S., ni sus directores, colaboradores o programadores asumen responsabilidad alguna por perjuicios directos, indirectos, lucro cesante o pérdidas operacionales que surjan de la adopción o uso de las estimaciones arrojadas por la aplicación.
    
    ---
    ### 📜 Régimen de Licencia Abierta GNU GPL-3.0
    * **Motor de Cálculo:** El núcleo termodinámico y de combustión utiliza **HyRAM+ v6.1**, desarrollado por **Sandia National Laboratories** (operado por *National Technology and Engineering Solutions of Sandia, LLC - NTESS* para el Departamento de Energía de EE. UU. / DOE).
    * **Licenciamiento:** HyRAM+ se distribuye bajo la licencia **GNU General Public License v3.0 (GPL-3.0)**. 
    * **Atribución:** Grupo VALIO reconoce y respeta íntegramente la autoría de Sandia Labs y las libertades del software libre. Esta adaptación web no implica vínculo, endoso ni patrocinio oficial por parte de agencias gubernamentales de los Estados Unidos.
    
    ---
    ### 🔐 Trazabilidad Forense y Sello Digital
    Cada simulación incorpora un sello criptográfico SHA-256 y marcas de agua invisibles esteganográficas para certificar la procedencia de los algoritmos y proteger el desarrollo frente a plagios o manipulaciones no autorizadas.
    """)
    if st.button("Entendido y Acepto las Condiciones", key="close_legal_modal"):
        st.rerun()

@st.dialog("📚 Metodología Detallada & Fundamento Científico (HyRAM+ v6.1)")
def modal_methodology():
    st.markdown(r"""
    ### 🔬 Fundamentos Termofísicos del Modelo
    HyRAM+ integra formulaciones rigurosas para la caracterización de fugas y chorros turbulentos inflamables (*jet fires*):
    
    1. **Ecuación de Estado Real (EoS):**  
       Para Hidrógeno y otros gases a alta presión, utiliza formulaciones de gas real de alta fidelidad basadas en CoolProp / NIST Refprop, calculando compresibilidad ($Z$), entalpía y entropía sin asumir comportamiento de gas ideal.
    
    2. **Modelo de Tobera Nocional (Yüceil & Ötügen, 2002):**  
       En escapes sobreeexpandidos sónicos/choked ($P_0 / P_{amb} > 1.89$), el gas se expande supersónicamente. El modelo proyecta un área nocional efectiva ($A^*$) y velocidad sónica equivalente en el punto donde la presión se equilibra con la atmósfera.
    
    3. **Longitud de Llama Visible (Ekoto et al., 2014):**  
       La longitud de llama $L_f$ se correlaciona a partir del número de Froude de llama ($Fr_f$) y el balance de momento turbulento:
       $$\frac{L_f}{d^*} = f(Fr_f, \Delta T_{ad}, Y_{st})$$
    
    4. **Radiación Térmica y Transmisividad Atmosférica:**  
       El flujo radiativo en un punto receptor $R$ se determina integrando la fracción radiativa del combustible ($\eta_{rad}$) y la atenuación por vapor de agua y $CO_2$ atmosférico:
       $$q'' = \frac{\tau_{atm}(RH, T_{amb}, R) \cdot \eta_{rad} \cdot \dot{m} \cdot \Delta H_c}{4 \pi R^2}$$
    """)

@st.dialog("📋 Plan de Mejoras Técnicas & Legales — HyRAM+ Web (Grupo VALIO)")
def modal_plan_mejoras():
    st.markdown("""
    ### ⚡ Plan de Mejoras Técnicas & Legales — HyRAM+ Web
    **Grupo VALIO S.A.S.** — Estado de Implementación Integral:
    
    1. **🛡️ Blindaje Legal y Régimen de Licencias (100% Implementado):**
       * Cláusula explícita de exclusión *"AS IS"* para fines exclusivamente pedagógicos y conceptuales.
       * Exoneración total de responsabilidad técnica, civil, penal o comercial.
       * Cumplimiento estricto de la licencia **GNU General Public License v3.0 (GPL-3.0)** de Sandia National Laboratories / NTESS / US DOE.
       * Incluido en cabecera, pestaña jurídica y pie de página de cada reporte PDF emitido.
    
    2. **🔐 Protección de Código y Marcas Forenses Invisibles (100% Implementado):**
       * Esteganografía Unicode Zero-Width (`\\u200B`, `\\u200C`, `\\u200D`, `\\uFEFF`) inyectada en datos y documentos exportados para trazabilidad forense anti-plagio.
       * Sello criptográfico SHA-256 (`VAL-HYR-YYYYMMDD-XXXXXXXX`) emitido con sal corporativa privada de Grupo VALIO.
       * Metadatos XMP forenses embebidos en los archivos PDF generados.
    
    3. **📄 Generador de Reportes Técnicos en PDF (100% Implementado):**
       * Motor ejecutivo con **ReportLab** y **Matplotlib** en alta resolución (220 DPI).
       * Membrete institucional, cuadrícula de parámetros, KPIs ejecutivos, huella 2D de isocontornos térmicos y matriz normativa NFPA 2 / API 521.
    
    4. **💡 Micro-Ventanas Teóricas e Interactividad Sutil (100% Implementado):**
       * Tooltips contextuales en todos los controles operacionales de la barra lateral.
       * Popovers flotantes con fórmulas matemáticas en LaTeX (régimen crítico, Ekoto et al. 2014, atenuación $\\tau_{atm}$).
       * Modales interactivos para marco legal y metodología sin recargar la página.
    """)
    if st.button("Cerrar Resumen del Plan", key="close_plan_modal"):
        st.rerun()

# ---------------------------------------------------------
# ENCABEZADO PRINCIPAL DE LA APLICACIÓN
# ---------------------------------------------------------
col_hdr_1, col_hdr_2 = st.columns([3, 1.2])
with col_hdr_1:
    st.markdown('<div class="main-title">⚡ HyRAM+ Consequence & Risk Assessment Tool</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Modelado cuantitativo de consecuencias y distancias de seguridad para Hidrógeno y Combustibles Alternativos | Basado en Sandia National Laboratories (DOE) & Normas NFPA 2 / API 521</div>',
        unsafe_allow_html=True
    )
with col_hdr_2:
    st.markdown("""
    <div style="background: rgba(14, 165, 233, 0.06); border: 1px solid rgba(14, 165, 233, 0.25); border-radius: 8px; padding: 0.6rem 0.8rem; text-align: right;">
        <div style="font-weight: 700; color: #0284c7; font-size: 0.9rem;">🛡️ Grupo VALIO S.A.S.</div>
        <div style="font-size: 0.76rem; color: #64748b;">Seguridad de Procesos & PPAM</div>
        <div style="font-size: 0.72rem; margin-top: 0.25rem;"><a href="https://www.grupovalio.com" target="_blank" style="color: #0ea5e9; text-decoration: none;">www.grupovalio.com</a></div>
    </div>
    """, unsafe_allow_html=True)

# Barra de herramientas superior con botones de micro-ventanas
col_btn_a, col_btn_b, col_btn_c, col_btn_d = st.columns([1.4, 1.2, 1.2, 1.8])
with col_btn_a:
    if st.button("📋 Plan de Mejoras (VALIO)", use_container_width=True):
        modal_plan_mejoras()
with col_btn_b:
    if st.button("⚖️ Marco Legal & GPL", use_container_width=True):
        modal_legal_shield()
with col_btn_c:
    if st.button("📚 Metodología", use_container_width=True):
        modal_methodology()
with col_btn_d:
    st.caption("🔒 *Trazabilidad SHA-256 y marcas forenses activas.*")

st.markdown("---")

# ---------------------------------------------------------
# MOTOR DE CÁLCULO CON CACHÉ Y MARCA FORENSE
# ---------------------------------------------------------
@st.cache_data(show_spinner="Calculando dinámica de fluidos y radiación con HyRAM+...")
def compute_hyram_jet_flame(fuel_name, pres_pa, temp_k, orif_diam_m, cd, amb_pres_pa, amb_temp_k, rel_humidity):
    from hyram.phys._comps import Fluid, Orifice, NozzleFlow
    from hyram.phys._flame import Flame

    # Creación de fluidos en condiciones de almacenamiento y ambiente
    fuel = Fluid(fuel_name, P=pres_pa, T=temp_k)
    orifice = Orifice(orif_diam_m, Cd=cd)
    ambient = Fluid('air', P=amb_pres_pa, T=amb_temp_k)
    
    # Cálculo de dinámica de escape en tobera
    nozzle = NozzleFlow(fuel, orifice, amb_pres_pa)
    mass_flow = nozzle.mdot  # kg/s
    choked = nozzle.choked

    # Cálculo de combustión y radiación del chorro
    flame = Flame(fuel, orifice, ambient)
    flame_length = flame.get_visible_length()
    s_rad = flame.get_srad()  # Watts
    
    # Umbrales normativos de radiación térmica (W/m2) según NFPA 2 y API 521
    thresholds = [1600, 4700, 9800, 25000]
    distances = {}
    for q in thresholds:
        try:
            d = flame.calc_distance_to_heatflux(q, direction='x', RH=rel_humidity)
            distances[q] = float(d)
        except Exception:
            distances[q] = None

    # Inyección de marca forense invisible de Grupo VALIO en la estructura de datos
    zw_token = forensics.get_forensic_watermark_token()

    return {
        "mass_flow": mass_flow,
        "choked": choked,
        "flame_length": flame_length,
        "s_rad": s_rad,
        "distances": distances,
        "fuel_density": fuel.rho,
        "_forensic_signature": zw_token
    }

# ---------------------------------------------------------
# PARÁMETROS DE OPERACIÓN (BARRA LATERAL CON TOOLTIPS)
# ---------------------------------------------------------
st.sidebar.header("⚙️ Parámetros de Operación")

fuel_option = st.sidebar.selectbox(
    "Fluido Combustible",
    ["Hidrógeno (H₂)", "Metano (CH₄)", "Propano (C₃H₈)"],
    index=0,
    help="Seleccione el gas inflamable. HyRAM+ emplea ecuaciones de estado reales (CoolProp) para evaluar propiedades termodinámicas y cinética de combustión."
)
fuel_key_map = {
    "Hidrógeno (H₂)": "H2",
    "Metano (CH₄)": "CH4",
    "Propano (C₃H₈)": "propane"
}
selected_fuel = fuel_key_map[fuel_option]

# Presión de almacenamiento
st.sidebar.subheader("Presión del Sistema")
pres_unit = st.sidebar.radio(
    "Unidad de Presión",
    ["bar", "MPa", "psi"],
    horizontal=True,
    help="Unidad para la presión estancada en el recipiente o tubería antes de la fuga."
)

if pres_unit == "bar":
    pres_val = st.sidebar.number_input(
        "Presión de Almacenamiento (bar)",
        min_value=1.5, max_value=1000.0, value=200.0, step=10.0,
        help="Presión absoluta interna. El hidrógeno suele almacenarse a 200, 350 o 700 bar en cilindros tipo III/IV."
    )
    pres_pa = pres_val * 1e5
elif pres_unit == "MPa":
    pres_val = st.sidebar.number_input(
        "Presión de Almacenamiento (MPa)",
        min_value=0.15, max_value=100.0, value=20.0, step=1.0,
        help="Presión manométrica/absoluta en megapascales (1 MPa = 10 bar)."
    )
    pres_pa = pres_val * 1e6
else:
    pres_val = st.sidebar.number_input(
        "Presión de Almacenamiento (psi)",
        min_value=20.0, max_value=14500.0, value=2900.0, step=100.0,
        help="Presión en libras por pulgada cuadrada (psi)."
    )
    pres_pa = pres_val * 6894.76

# Temperatura del gas
st.sidebar.subheader("Temperatura del Gas")
temp_c = st.sidebar.slider(
    "Temperatura (°C)",
    min_value=-50, max_value=80, value=20, step=1,
    help="Temperatura inicial del combustible en el recipiente. Afecta directamente la densidad y la velocidad sónica del gas."
)
temp_k = temp_c + 273.15

# Geometría de la fuga
st.sidebar.subheader("Geometría de la Fuga")
orif_unit = st.sidebar.radio(
    "Unidad Diámetro",
    ["mm", "pulgadas (in)"],
    horizontal=True,
    help="Seleccione la unidad geométrica del orificio de fuga."
)

if orif_unit == "mm":
    orif_diam_val = st.sidebar.slider(
        "Diámetro del Orificio (mm)",
        min_value=0.5, max_value=25.0, value=2.0, step=0.5,
        help="Diámetro circular equivalente de la rotura o fisura (ej. 1-3 mm para fittings, 10-25 mm para rupturas de manguera)."
    )
    orif_diam_m = orif_diam_val * 1e-3
else:
    orif_diam_val = st.sidebar.slider(
        "Diámetro del Orificio (in)",
        min_value=0.02, max_value=1.0, value=0.08, step=0.01,
        help="Diámetro de fuga en pulgadas."
    )
    orif_diam_m = orif_diam_val * 0.0254

cd_coeff = st.sidebar.slider(
    "Coeficiente de Descarga (Cd)",
    min_value=0.5, max_value=1.0, value=0.85, step=0.05,
    help="Relación entre el flujo másico real y el teórico ideal. Valores típicos: 0.62 para orificios de borde afilado; 0.85 para válvulas y accesorios; 0.98 para toberas convergentes redondeadas."
)

# Parámetros meteorológicos / ambientales
with st.sidebar.expander("🌐 Condiciones Ambientales", expanded=False):
    amb_temp_c = st.slider(
        "Temperatura Ambiente (°C)",
        min_value=-20, max_value=50, value=25,
        help="Temperatura atmosférica externa. Influye en la flotabilidad del chorro y en la atenuación radiativa."
    )
    amb_temp_k = amb_temp_c + 273.15
    amb_pres_kpa = st.number_input(
        "Presión Atmosférica (kPa)",
        value=101.325,
        help="Presión barométrica local (101.3 kPa a nivel del mar; ~74 kPa en Bogotá D.C. a 2600 msnm)."
    )
    amb_pres_pa = amb_pres_kpa * 1000
    rel_humidity = st.slider(
        "Humedad Relativa (%)",
        min_value=10, max_value=100, value=80,
        help="Porcentaje de humedad relativa. El vapor de agua atmosférico absorbe significativamente la radiación térmica infrarroja emitida por la llama."
    ) / 100.0

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
    # Parámetros compilados para reportes y sellado
    input_params = {
        "fuel_option": fuel_option,
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
    
    # Generar sello criptográfico SHA-256 y certificado oficial
    seal_data = forensics.generate_tamper_seal(input_params, {
        "mass_flow": results['mass_flow'],
        "flame_length": results['flame_length'],
        "s_rad": results['s_rad']
    })

    # ---------------------------------------------------------
    # INDICADORES CLAVE (KPIS)
    # ---------------------------------------------------------
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(
            label="Tasa de Fuga Masiva",
            value=f"{results['mass_flow'] * 1000:.2f} g/s",
            delta=f"{results['mass_flow'] * 3600:.2f} kg/h",
            help="Caudal másico descargado a través del orificio bajo la presión estancada especificada."
        )
    with m2:
        st.metric(
            label="Longitud de Llama Visible",
            value=f"{results['flame_length']:.2f} m",
            delta="Chorro turbulento",
            help="Longitud axial de la llama visible basada en la correlación de Ekoto et al. (Sandia National Labs, 2014)."
        )
    with m3:
        st.metric(
            label="Potencia Radiativa Total",
            value=f"{results['s_rad'] / 1000:.1f} kW",
            delta=f"{results['s_rad'] / 1e6:.3f} MW",
            help="Energía térmica total emitida en forma de radiación electromagnética (fracción radiativa del calor de combustión)."
        )
    with m4:
        regime = "Sónico (Choked)" if results['choked'] else "Subsónico"
        st.metric(
            label="Régimen de Escape",
            value=regime,
            delta="Flujo crítico" if results['choked'] else "Normal",
            help="Indica si la velocidad del gas en la garganta del orificio alcanza la velocidad local del sonido (flujo bloqueado/crítico)."
        )

    # ---------------------------------------------------------
    # MICRO-VENTANAS TEÓRICAS Y POPOVERS INTERACTIVOS
    # ---------------------------------------------------------
    c_pop1, c_pop2, c_pop3 = st.columns([1, 1, 1.2])
    with c_pop1:
        with st.popover("🔬 Ver Ecuaciones Físicas"):
            st.markdown("#### Formulación Matemática del Modelo")
            st.markdown("**1. Caudal Másico en Régimen Sónico (Choked):**")
            st.latex(r"\dot{m} = C_d A P_0 \sqrt{\frac{\gamma M}{R T_0}} \left(\frac{2}{\gamma + 1}\right)^{\frac{\gamma+1}{2(\gamma-1)}}")
            st.markdown("**2. Condición Crítica de Bloqueo:**")
            st.latex(r"\frac{P_{crit}}{P_0} = \left(\frac{2}{\gamma + 1}\right)^{\frac{\gamma}{\gamma - 1}} \approx 0.528 \text{ (para H}_2\text{)}")
            st.markdown("**3. Flujo Térmico Radiante (Receptor a distancia R):**")
            st.latex(r"q'' = \frac{\tau_{atm}(RH) \cdot \eta_{rad} \cdot \dot{m} \cdot \Delta H_c}{4 \pi R^2}")
            st.caption("*Referencia: Ekoto et al. (Int. J. Hydrogen Energy, 2014).*")
            
    with c_pop2:
        with st.popover("📖 Guía de Umbrales NFPA 2 / API 521"):
            st.markdown("#### Niveles de Exposición Térmica")
            st.markdown("""
            * **🟢 1.6 kW/m²:** Seguro para permanencia continua prolongada del público general sin ropa especial.
            * **🟡 4.7 kW/m²:** Límite para escape de personal entrenado. Dolor tolerable hasta 15-20 s; no causa ampollas ni quemaduras de 2° grado.
            * **🟠 9.8 kW/m²:** Límite de daño para equipos, tuberías y sistemas de instrumentación no aislados. Dolor en <5 s.
            * **🔴 25.0 kW/m²:** Radiación crítica destructiva. Ignición espontánea de madera, deformación plástica y colapso de soportes de acero no ignifugados.
            """)

    with c_pop3:
        with st.popover("🔐 Certificado de Autenticidad"):
            st.markdown("#### Trazabilidad y Sello Criptográfico")
            st.markdown(f"**Certificado:** `{seal_data['certificate_id']}`")
            st.markdown(f"**Hash SHA-256:**  \n`{seal_data['sha256']}`")
            st.markdown(f"**Emisión UTC:** {seal_data['timestamp_utc']}")
            st.markdown(f"**Emisor:** {seal_data['issuer']}")
            st.caption("Verificación forense de autoría Grupo VALIO activa.")

    st.markdown("---")

    # ---------------------------------------------------------
    # PESTAÑAS PRINCIPALES DE VISUALIZACIÓN Y REPORTES
    # ---------------------------------------------------------
    tab_rad, tab_zones, tab_standards, tab_info, tab_legal = st.tabs([
        "🔥 Distancias de Seguridad y Radiación",
        "🎯 Mapa 2D de Zonas de Peligro",
        "📋 Cumplimiento Normativo & Reportes",
        "🔬 Base Científica & Metodología",
        "⚖️ Marco Legal & Licencia GPL-3.0"
    ])

    d_16 = results['distances'].get(1600)
    d_47 = results['distances'].get(4700)
    d_98 = results['distances'].get(9800)
    d_25 = results['distances'].get(25000)

    # PESTAÑA 1: DISTANCIAS DE RADIACIÓN
    with tab_rad:
        st.subheader("Distancias de Separación por Nivel de Flujo Térmico")
        st.write("Distancia axial desde el punto de fuga hasta los límites de radiación térmica especificados por estándares internacionales:")

        c_dist_1, c_dist_2 = st.columns([1, 1])
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

    # PESTAÑA 2: MAPA 2D INTERACTIVO
    with tab_zones:
        st.subheader("Huella Espacial 2D de Zonas de Riesgo Térmico (Plan View)")
        st.write("Vista superior interactiva de los perímetros de seguridad concéntricos alrededor del punto de fuga (0,0):")

        fig_2d = go.Figure()

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

        fig_2d.add_trace(go.Scatter(
            x=[0], y=[0], mode="markers+text", marker=dict(color="blue", size=12, symbol="cross"),
            text=["Punto de Fuga (0,0)"], textposition="top left", name="Origen Fuga"
        ))

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

    # PESTAÑA 3: CUMPLIMIENTO NORMATIVO Y DESCARGAS (CSV + PDF OFICIAL)
    with tab_standards:
        st.subheader("Tabla de Cumplimiento Normativo (NFPA 2 / API 521 / ISO 19880-1)")
        df_summary = pd.DataFrame([
            {"Norma": "NFPA 2 / API 521", "Umbral Térmico": "1.6 kW/m²", "Criterio de Aceptabilidad": "Exposición prolongada continua de personas sin EPP", "Distancia Requerida": f"{d_16:.2f} m" if d_16 else "N/A"},
            {"Norma": "NFPA 2 / API 521", "Umbral Térmico": "4.7 kW/m²", "Criterio de Aceptabilidad": "Tiempo de escape de personal calificado (hasta 30 s)", "Distancia Requerida": f"{d_47:.2f} m" if d_47 else "N/A"},
            {"Norma": "API 521 / NFPA 59A", "Umbral Térmico": "9.8 kW/m²", "Criterio de Aceptabilidad": "Protección de equipos sin revestimiento ignífugo", "Distancia Requerida": f"{d_98:.2f} m" if d_98 else "N/A"},
            {"Norma": "API 521", "Umbral Térmico": "25.0 kW/m²", "Criterio de Aceptabilidad": "Peligro estructural inminente y combustión de materiales", "Distancia Requerida": f"{d_25:.2f} m" if d_25 else "N/A"}
        ])
        st.dataframe(df_summary, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("📥 Exportación de Informes Técnicos")

        col_rep_a, col_rep_b = st.columns([1.2, 1])

        # Generación del PDF con ReportLab
        try:
            pdf_bytes = pdf_generator.build_hyram_pdf_report(input_params, results, seal_data)
            pdf_ready = True
        except Exception as pdf_err:
            st.error(f"Error generando reporte PDF: {str(pdf_err)}")
            pdf_ready = False

        with col_rep_a:
            st.markdown("""
            **📄 Informe Técnico Ejecutivo en PDF (Full Color):**  
            Incluye membrete de Grupo VALIO, tabla de parámetros operacionales, tarjetas de KPIs, mapa 2D de isocontornos integrado, matriz de distancias normativas, firma forense criptográfica SHA-256 y cláusula legal de exención vinculante.
            """)
            if pdf_ready:
                st.download_button(
                    label="📄 Descargar Informe Técnico Oficial (PDF)",
                    data=pdf_bytes,
                    file_name=f"VALIO_Informe_HyRAM_{selected_fuel}_{pres_val}{pres_unit}_{seal_data['certificate_id']}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

        with col_rep_b:
            st.markdown("""
            **📊 Tabla de Datos en Formato CSV:**  
            Permite importar los resultados tabulados de distancias y umbrales directamente en hojas de cálculo o software de ingeniería.
            """)
            csv_data = df_summary.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📊 Descargar Matriz de Datos (CSV)",
                data=csv_data,
                file_name=f"reporte_seguridad_hyram_{selected_fuel}_{pres_val}{pres_unit}.csv",
                mime="text/csv",
                use_container_width=True
            )

    # PESTAÑA 4: BASE CIENTÍFICA & METODOLOGÍA
    with tab_info:
        st.subheader("Metodología Científica y Formulación HyRAM+")
        st.markdown("""
        **HyRAM+ (Hydrogen Plus Other Alternative Fuels Risk Assessment Models)** es un software científico de referencia global desarrollado por **Sandia National Laboratories** para el Departamento de Energía de los EE. UU. (DOE).

        * **Modelo de Chorro Térmico (Jet Fire):** Implementa las formulaciones de conservación de masa, momento y energía desarrolladas por *Ekoto et al.* (International Journal of Hydrogen Energy, 2014) y los modelos de tobera nocional de *Yüceil & Ötügen*.
        * **Fracción Radiativa:** Modela la radiación térmica emitida por la combustión de chorros turbulentos de hidrógeno y gas natural considerando absorción atmosférica por vapor de agua y dióxido de carbono.
        * **Validación Experimental:** Validado mediante extensos ensayos a gran escala en las instalaciones de combustión de Sandia National Laboratories en Livermore, California.
        
        🔗 Enlaces de consulta oficial:
        * [Portal Oficial de HyRAM en Sandia Labs](https://hyram.sandia.gov/)
        * [Repositorio Open Source en GitHub (Sandia Labs)](https://github.com/sandialabs/hyram)
        """)

    # PESTAÑA 5: BLINDAJE LEGAL Y RÉGIMEN DE LICENCIAS
    with tab_legal:
        st.subheader("⚖️ Régimen Jurídico, Blindaje Legal y Licencia GPL-3.0")
        
        st.markdown("""
        <div class="legal-card">
            <h4 style="margin-top:0; color:#0f172a;">1. Cláusula de Exclusión Total de Responsabilidad ("AS IS")</h4>
            <p>La presente plataforma web <strong>HyRAM+ Web</strong>, provista por <strong>Grupo VALIO S.A.S.</strong>, se pone a disposición pública bajo fines estrictamente pedagógicos, académicos y de evaluación conceptual preliminar.</p>
            <p><strong>Bajo ningún concepto los resultados de esta herramienta sustituyen:</strong></p>
            <ul>
                <li>Un Estudio de Análisis Cuantitativo de Riesgos (QRA) formal.</li>
                <li>Un Plan de Prevención de Accidentes Mayores (PPAM / Decreto 1347 de Colombia o normas análogas).</li>
                <li>Memorias de cálculo técnicas, periciales o de ingeniería de detalle firmadas y avaladas por ingenieros legalmente colegiados y matriculados.</li>
            </ul>
            <p><strong>Inmunidad ante daños:</strong> Grupo VALIO S.A.S., sus accionistas, representantes legales, empleados, aliados y desarrolladores quedan plenamente exonerados de cualquier responsabilidad civil, comercial, penal, contractual o extracontractual por perjuicios directos, indirectos, daño emergente, lucro cesante o siniestros derivados del uso, interpretación o aplicación de los resultados obtenidos.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br/>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="legal-card" style="border-left-color: #10b981;">
            <h4 style="margin-top:0; color:#0f172a;">2. Cumplimiento de la Licencia Open Source GNU General Public License v3.0 (GPL-3.0)</h4>
            <p>El motor analítico subyacente empleado en los cálculos físicos es <strong>HyRAM+ v6.1</strong>, una obra de autoría científica de <strong>Sandia National Laboratories</strong> (gestionado por <em>National Technology and Engineering Solutions of Sandia, LLC - NTESS</em> para el U.S. Department of Energy - DOE).</p>
            <p>En conformidad estricta con los términos de la licencia <strong>GNU GPL-3.0</strong>:</p>
            <ul>
                <li>Se reconoce y preserva de forma explícita la autoría original de Sandia National Laboratories.</li>
                <li>La integración web, interfaces interactivas y capas de generación documental desarrolladas por Grupo VALIO respetan el carácter abierto y no comercializan el código fuente base de HyRAM+.</li>
                <li>El uso del motor HyRAM+ no constituye, bajo ninguna circunstancia, asociación, patrocinio, certificación ni endoso por parte de Sandia National Laboratories, NTESS ni del gobierno de los Estados Unidos de América.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br/>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="legal-card" style="border-left-color: #6366f1;">
            <h4 style="margin-top:0; color:#0f172a;">3. Protección de Código y Marcas Forenses Invisibles</h4>
            <p>Para resguardar los desarrollos metodológicos y la parametrización de visualización desarrollada por Grupo VALIO frente a plagios o extracciones no autorizadas, esta versión incorpora:</p>
            <ul>
                <li><strong>Esteganografía Unicode de Ancho Cero:</strong> Marcado de autoría invisible en las estructuras de datos y reportes generados.</li>
                <li><strong>Certificado Criptográfico SHA-256:</strong> Cada corrida genera un código único de verificación: <span class="seal-pill">{seal_data['certificate_id']}</span></li>
                <li><strong>Metadatos Inyectados en PDF:</strong> Trazabilidad pericial vinculada a Grupo VALIO S.A.S.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# PIE DE PÁGINA CORPORATIVO CON ADVERTENCIA LEGAL PERMANENTE
# ---------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="font-size: 0.78rem; color: #64748b; line-height: 1.5; text-align: center;">
    <strong>Grupo VALIO S.A.S.</strong> · Consultoría en Seguridad de Procesos & Prevención de Accidentes Mayores (PPAM) · 
    <a href="https://www.grupovalio.com" target="_blank" style="color: #0284c7; text-decoration: none;">www.grupovalio.com</a> © 2026<br/>
    <em>Aviso Legal: Herramienta de uso pedagógico y preliminar. No sustituye estudios de ingeniería formal ni dictámenes periciales certificados. Desarrollado con base en Sandia National Laboratories HyRAM+ v6.1 (Licencia GNU GPL-3.0).</em>
</div>
""", unsafe_allow_html=True)
