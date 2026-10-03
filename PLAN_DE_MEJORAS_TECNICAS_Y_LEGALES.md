# ⚡ Plan de Mejoras Técnicas & Legales — HyRAM+ Web (Grupo VALIO)

Documento oficial de especificaciones técnicas, arquitectura legal y estado de implementación para la plataforma web [valio-hyram.streamlit.app](https://valio-hyram.streamlit.app) / `apps/hyram-web`.

Desarrollado y parametrizado por **Grupo VALIO S.A.S.** ([www.grupovalio.com](https://www.grupovalio.com))  
*División de Consultoría en Seguridad de Procesos & Prevención de Accidentes Mayores (PPAM)*

---

## 📌 Estado de Implementación General

| Pilar de Mejora | Componente Principal | Archivo Fuente | Estado |
| :--- | :--- | :--- | :---: |
| **1. 🛡️ Blindaje Legal & Licencias** | Cláusula "AS IS", exoneración total, régimen GNU GPL-3.0 | [`app.py`](app.py), [`pdf_generator.py`](pdf_generator.py) | **100% Implementado** |
| **2. 🔐 Protección Anti-Plagio** | Esteganografía Unicode Zero-Width + Sello Criptográfico SHA-256 | [`forensics.py`](forensics.py), [`pdf_generator.py`](pdf_generator.py) | **100% Implementado** |
| **3. 📄 Reportes Ejecutivos en PDF** | ReportLab Full Color, gráficos 2D en alta resolución y KPIs | [`pdf_generator.py`](pdf_generator.py), [`app.py`](app.py) | **100% Implementado** |
| **4. 💡 Micro-Ventanas Teóricas** | Tooltips nativos, Popovers LaTeX y Diálogos Modales limpios | [`app.py`](app.py) | **100% Implementado** |

---

## 1. 🛡️ Blindaje Legal y Régimen de Licencias
* **Propósito:** Proteger a **VALIO S.A.S.** de responsabilidades técnicas, legales, civiles o comerciales derivadas del uso o mala interpretación de los cálculos por terceros.
* **Componentes implementados:**
  * **Cláusula de Exclusión ("AS IS"):** Declaración explícita de que la herramienta tiene fines **exclusivamente pedagógicos, académicos y de investigación preliminar**. No reemplaza la ingeniería de detalle, auditorías de riesgo presenciales (QRA / PPAM) ni dictámenes periciales firmados por profesionales colegiados.
  * **Inmunidad ante daños:** Exoneración total de responsabilidad por daños directos, indirectos, daño emergente, lucro cesante o pérdidas operacionales.
  * **Régimen de Licencia Abierta GNU GPL-3.0:** Cumplimiento de la licencia **GNU General Public License v3.0** de HyRAM+ (Sandia National Laboratories / NTESS / US DOE), atribuyendo la autoría del motor de cálculo y aclarando que la interfaz web desarrollada por **Grupo VALIO** respeta dicha licencia sin vinculación oficial con agencias gubernamentales de EE.UU.
* **Ubicación en el código:**
  * Modal interactivo `@st.dialog("⚖️ Marco Legal, Exención de Responsabilidad & Licencia GPL-3.0")` en [`app.py`](app.py).
  * Pestaña `⚖️ Marco Legal & Licencia GPL-3.0` en la interfaz principal.
  * Cláusula legal vinculante en el pie de página de cada informe PDF generado en [`pdf_generator.py`](pdf_generator.py).

---

## 2. 🔐 Protección de Código y Marcas Forenses Invisibles (Anti-Plagio)
* **Propósito:** Proteger el esfuerzo de ingeniería, parametrización normativa y desarrollo de VALIO frente a copias no autorizadas o scraping no atribuido.
* **Mecanismos implementados en [`forensics.py`](forensics.py):**
  * **Marcas Esteganográficas Unicode (Zero-Width Characters):** Inserción de secuencias invisibles de caracteres (`\u200B`, `\u200C`, `\u200D`, `\uFEFF`) en comentarios, estructuras de datos devueltas por el motor y cadenas de texto del PDF. Visualmente indetectables para el usuario final, pero extraíbles y verificables como prueba forense en caso de litigio o plagio.
  * **Firma Criptográfica de Autoría (Hash SHA-256):** Algoritmo que genera un identificador único por simulación (`VAL-HYR-YYYYMMDD-XXXXXXXX`) derivado de las condiciones del escenario y una sal secreta corporativa de Grupo VALIO.
  * **Metadatos Ocultos en Artefactos (PDF/Gráficos):** Inyección de identificadores XMP en los PDFs generados (*Author: Grupo VALIO S.A.S. - División de Seguridad de Procesos*, *Subject: HyRAM+ Consequence Assessment*, *Copyright: Grupo VALIO © 2026*).

---

## 3. 📄 Generador de Reportes Técnicos en PDF (Full Color & Diseño Ejecutivo)
* **Propósito:** Permitir a clientes y usuarios descargar un informe formal con diseño ejecutivo corporativo de VALIO listo para presentación.
* **Tecnología:** [`pdf_generator.py`](pdf_generator.py) construido sobre **ReportLab** y **Matplotlib**.
* **Estructura del PDF (1-2 páginas):**
  1. **Encabezado Corporativo:** Membrete de **Grupo VALIO S.A.S.**, título de la simulación, número de certificado oficial y fecha/hora UTC.
  2. **Condiciones de Entrada:** Tabla formateada con presión, temperatura, fluido combustible, diámetro de fuga, $C_d$ y meteorología.
  3. **Indicadores Clave (KPIs):** Tarjetas estilizadas con flujo másico ($g/s$ y $kg/h$), longitud de llama visible ($m$), potencia radiativa ($kW$) y régimen sónico/choked.
  4. **Gráfico de Isocontornos Integrado:** Imagen 2D de alta resolución (220 DPI) generada directamente en memoria e incrustada en el PDF.
  5. **Matriz Normativa:** Tabla comparativa formal con los umbrales NFPA 2 / API 521 / ISO 19880-1 ($1.6$, $4.7$, $9.8$ y $25.0\ kW/m^2$) con colores semafóricos.
  6. **Pie de Página Legal & Foliado:** Cláusula de exoneración completa, atribución Sandia Labs GPL-3.0 y numeración dinámica `Página X de Y` (`NumberedCanvas`).

---

## 4. 💡 Micro-Ventanas Teóricas e Interactividad Sutil
* **Propósito:** Divulgar la ciencia detrás de los cálculos sin saturar la pantalla ni complicar la experiencia de usuario.
* **Soluciones de diseño en [`app.py`](app.py):**
  * **Tooltips Nativos (`help`):** Ícono `(?)` flotante en cada control de la barra lateral que explica el significado físico (presión estancada, $C_d$, orificio nocional, absorción por humedad atmosférica).
  * **Popovers Flotantes (`st.popover`):**
    * `🔬 Ver Ecuaciones Físicas`: Fórmulas matemáticas en LaTeX para gasto crítico bloqueado, correlación de Ekoto et al. (2014) y ley de radiación térmica atenuada.
    * `📖 Guía de Umbrales NFPA 2 / API 521`: Explicación de los niveles fisiológicos de dolor, quemaduras y fallo estructural.
    * `🔐 Certificado de Autenticidad`: Desglose del código de certificación y hash SHA-256.
  * **Diálogos Modales Limpios (`st.dialog`):** Ventana emergente con el desglose metodológico completo y el marco legal sin recargar la página.

---

## 🚀 Instrucciones de Ejecución Local

Para verificar la aplicación localmente en el navegador:

```powershell
# 1. Navegar al directorio de la app
cd c:\Users\USUARIO_DE_PRUEBA\Documents\GitHub\v0-valio-landing-page\apps\hyram-web

# 2. Instalar dependencias requeridas
pip install -r requirements.txt

# 3. Iniciar el servidor local de Streamlit
streamlit run app.py
```

La aplicación abrirá automáticamente en su navegador en `http://localhost:8501`.

---
*Documento preparado y certificado por Grupo VALIO S.A.S. — [www.grupovalio.com](https://www.grupovalio.com)*
