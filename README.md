# ⚡ HyRAM+ Web Application — Grupo VALIO

Aplicación web interactiva de ingeniería basada en **Streamlit** y los modelos físicos de **HyRAM+ v6.1 (Sandia National Laboratories)** para el cálculo cuantitativo de consecuencias, chorros de fuego (*jet fires*), radiación térmica y distancias de seguridad según normas **NFPA 2**, **API 521** e **ISO 19880-1**.

Desarrollada y parametrizada por **Grupo VALIO S.A.S.** ([www.grupovalio.com](https://www.grupovalio.com)).

---

## 🚀 Arquitectura y Mejoras Implementadas

### 1. 🛡️ Blindaje Legal y Régimen de Licencias
* **Cláusula de Exclusión ("AS IS"):** Exoneración explícita de responsabilidad patrimonial y comercial; la herramienta tiene fines exclusivamente pedagógicos, académicos y de evaluación conceptual preliminar. No sustituye estudios de ingeniería formal ni dictámenes periciales certificados.
* **Cumplimiento GPL-3.0:** Reconocimiento de autoría del motor de cálculo a **Sandia National Laboratories / NTESS / US DOE**, respetando plenamente los términos de la **GNU General Public License v3.0**.

### 2. 🔐 Protección de Código y Marcas Forenses Invisibles (Anti-Plagio)
* **Esteganografía Unicode de Ancho Cero (`\u200B`, `\u200C`, `\u200D`):** Inyección de firmas de autoría invisibles en las estructuras de datos y artefactos exportados.
* **Sello Criptográfico SHA-256:** Generación de identificador único de verificación (`VAL-HYR-YYYYMMDD-XXXXXXXX`) para validar autenticidad e integridad de cada cálculo.
* **Metadatos Forenses:** Inyección de autoría institucional en cabeceras XMP de los documentos generados.

### 3. 📄 Generador de Reportes Técnicos en PDF (Full Color & Diseño Ejecutivo)
* Motor de renderizado con **ReportLab** y **Matplotlib**.
* Formato ejecutivo corporativo con membrete oficial de Grupo VALIO.
* Cuadrícula de parámetros operacionales, tarjetas de KPIs y tabla comparativa de umbrales normativos.
* Gráfico 2D en alta resolución (300 DPI) con isocontornos de radiación y vector de llama visible.
* Numeración automática `Página X de Y` y cláusula legal vinculante en el pie de página.

### 4. 💡 Micro-Ventanas Teóricas e Interactividad Sutil
* **Tooltips Nativos (`help`):** Explicación física contextualizada en cada control de la barra lateral (presión estancada, $C_d$, orificio nocional, humedad relativa).
* **Popovers Flotantes (`st.popover`):** Formulación física y ecuaciones en LaTeX (gasto másico sónico/choked, correlación de Ekoto et al. 2014, atenuación atmosférica $\tau(RH)$) y guía de criterios de daño fisiológico.
* **Diálogos Modales (`st.dialog`):** Ventanas emergentes para consulta metodológica profunda y términos legales sin recargar la página.

---

## 📦 Requisitos e Instalación

```bash
cd apps/hyram-web
pip install -r requirements.txt
streamlit run app.py
```

## 🌐 Despliegue en Streamlit Community Cloud
1. Conectar este repositorio a [share.streamlit.io](https://share.streamlit.io).
2. Indicar la ruta del archivo principal: `apps/hyram-web/app.py`.
3. Desplegar en modo continuo con Python 3.11+.
