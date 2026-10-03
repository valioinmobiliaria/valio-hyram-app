# ⚡ HyRAM+ Web Application - Valio Industrial Safety

Aplicación web interactiva basada en **Streamlit** y los modelos físicos de **HyRAM+ (Sandia National Laboratories)** para el cálculo cuantitativo de consecuencias, chorros de fuego (*jet fires*), radiación térmica y distancias de seguridad según normas **NFPA 2**, **API 521** e **ISO 19880-1**.

## Características
* Modelado para **Hidrógeno ($H_2$)**, **Metano ($CH_4$)** y **Propano ($C_3H_8$)**.
* Cálculo en tiempo real de tasa de fuga másica, régimen de escape (sónico / choked), longitud de llama y potencia radiativa total.
* Determinación automática de distancias de seguridad:
  * **1.6 kW/m²** (Límite de permanencia continua / público general)
  * **4.7 kW/m²** (Límite de escape seguro sin quemaduras de 2do grado)
  * **9.8 kW/m²** (Límite de daño a equipos e instrumentación)
  * **25.0 kW/m²** (Radiación crítica destructiva)
* Visualización interactiva 2D con isocontornos de zonas de riesgo (Plotly).
* Exportación de reportes de cumplimiento normativo en CSV.

## Despliegue en Streamlit Community Cloud
1. Conectar este repositorio a [share.streamlit.io](https://share.streamlit.io).
2. Indicar la ruta del archivo principal: `apps/hyram-web/app.py`.
3. ¡Listo! La app se compila y queda en línea con URL pública permanente.
