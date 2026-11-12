# Violencia intrafamiliar en Bogotá — narrativa visual interactiva con Plotly

**Curso:** Visualización de Datos · Maestría en Ciencia de Datos · Universidad Santo Tomás
**Actividad:** Gráficos interactivos y storytelling con Plotly (20 %) — Sección 2
**Integrantes:** Adrian Felipe Grateron, Jhonatan Smith Doncel y Jorge Emmanuel Marin
**Fuente:** microdato *Seguimiento a delitos de alto impacto* de la Secretaría Distrital de Seguridad, Convivencia y Justicia
de Bogotá (SDSCJ), publicado en su Observatorio → <https://oaiee.scj.gov.co/DatosDescarga/SIEDCO.csv>
(el servidor publica el archivo con el nombre técnico `SIEDCO.csv`; en el proyecto se guarda como `data/raw/delitos_alto_impacto_SDSCJ.csv`).

> **Gran Idea:** *La violencia intrafamiliar está 61 % por encima de su promedio histórico mientras el hurto retrocede:
> la seguridad de Bogotá también se juega dentro de la casa.*

**Ver la visualización interactiva:** <https://adrianfelipe812.github.io/violencia-intrafamiliar-bogota-plotly/>

---

## 1. Estructura del proyecto

```
Proyecto_Plotly_SDSCJ/
├── README.md                    ← este paso a paso
├── requirements.txt             ← dependencias
├── main.py                      ← ejecuta todo de punta a punta (alternativa a los cuadernos)
├── src/                         ← código reutilizable, documentado
│   ├── config.py                ← rutas, URL, ventana, paleta, integrantes (una sola fuente de verdad)
│   ├── descarga.py              ← Paso 1: descarga con trazabilidad (SHA-256, fecha, Last-Modified)
│   ├── normalizacion.py         ← Paso 2: limpieza, tipos, etiquetas, 7 validaciones, diccionario
│   ├── analisis.py              ← Paso 3: ventana comparable, índice, KPIs (todas las cifras)
│   ├── visual.py                ← Paso 4: las tres perlas y la figura de síntesis (Plotly Graph Objects)
│   ├── artefacto.py             ← Paso 5: HTML autónomo: tres actos + síntesis (Bing-Bang-Bongo)
│   └── empaquetar.py            ← Paso 8: .zip de entrega
├── notebooks/
│   ├── 01_descarga_y_normalizacion.ipynb
│   ├── 02_exploracion_plotly_express.ipynb   ← «abrir ostras» con Plotly Express
│   └── 03_artefacto_final.ipynb              ← perlas, exportación, control de calidad, PDF y ZIP
├── data/
│   ├── raw/                     ← delitos_alto_impacto_SDSCJ.csv tal como se descarga (contenido sin modificar) + metadatos
│   └── processed/               ← delitos_alto_impacto_normalizado.csv.gz + reporte_calidad.json
├── salidas/                     ← Violencia_intrafamiliar_Bogota_SDSCJ.html + kpis.json
├── docs/                        ← PDF de justificación (APA 7), generador, diccionario, bitácora
└── entrega/                     ← Proyecto_Plotly_SDSCJ_entrega.zip
```

## 2. Paso a paso en Visual Studio Code

### 2.1 Preparar el entorno (una sola vez)
> **Versión de Python:** el proyecto se generó con **Python 3.14.3** y las versiones exactas de `requirements.txt`.
> Use esa versión de Python para obtener resultados idénticos.

1. Instale las extensiones **Python** y **Jupyter** de Microsoft en VS Code.
2. `Archivo → Abrir carpeta…` y elija `Proyecto_Plotly_SDSCJ`.
3. Abra la terminal (`Ctrl + ñ` o `Terminal → Nueva terminal`) y cree un entorno virtual:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1        # en Windows (PowerShell)
   pip install -r requirements.txt
   ```
   > Si PowerShell bloquea la activación: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
4. Al abrir un cuaderno, en la esquina superior derecha pulse **Seleccionar kernel** → *Python Environments* → `.venv`.

### 2.2 Ejecutar los cuadernos en orden (`Ejecutar todo` en cada uno)

| # | Cuaderno | Qué produce | Paso de la guía |
|---|---|---|---|
| 1 | `01_descarga_y_normalizacion.ipynb` | `data/raw/delitos_alto_impacto_SDSCJ.csv`, tabla normalizada, reporte de calidad, diccionario | 2 (datos) |
| 2 | `02_exploracion_plotly_express.ipynb` | 9 gráficos exploratorios y la definición del contexto (audiencia, conflicto, Gran Idea) | 3 y 4 |
| 3 | `03_artefacto_final.ipynb` | HTML final, verificación de afirmaciones, control de calidad, PDF y ZIP | 5, 6, 7 y 8 |

**Alternativa en una línea:** `python main.py` (agregue `--forzar` para volver a descargar los datos).

### 2.3 Productos generados
| Producto | Archivo | Cómo se abre |
|---|---|---|
| Visualización interactiva (HTML autónomo) | `salidas/Violencia_intrafamiliar_Bogota_SDSCJ.html` | Doble clic; funciona sin Python y sin internet |
| Documento de justificación (APA 7, 2 páginas) | `docs/Documento_justificacion_APA7.pdf` | Cualquier lector de PDF |
| Paquete de entrega | `entrega/Proyecto_Plotly_SDSCJ_entrega.zip` | Contiene código, cuadernos, datos, HTML y PDF |

Los tres productos se regeneran juntos con `03_artefacto_final.ipynb` o con `python main.py`, de modo que las cifras siempre coinciden entre sí.

## 3. Cómo se cumple cada paso de la guía

| Paso de la guía | Dónde se cumple |
|---|---|
| 1. Grupo de tres | `config.INTEGRANTES` (aparece en el HTML y en el PDF) |
| 2. Base real y pública con complejidad | Delitos de alto impacto de la SDSCJ: 12 delitos × 20 localidades × 2018–2026 × sexo × ciclo vital × franja × arma (≈376.000 filas, ≈1,9 millones de casos) |
| 3. Contexto antes de programar | Síntesis al final del cuaderno 02 (audiencia, qué saber/hacer, conflicto, Gran Idea en una oración) |
| 4. Exploratorio vs. aclaratorio | Cuaderno 02 (9 ostras con Plotly Express) → 3 perlas + 1 figura de síntesis en el cuaderno 03 |
| 5. Diseño con controles que aportan | Menú *Comparar con…* (Acto 1), botones de métrica (Acto 2), solo hover (Acto 3 y síntesis); < 300 puntos por figura |
| 6. Eliminar el caos y enfocar | Sin fondo, bordes ni leyendas; gris + coral; etiquetado directo; capa de anotación en cada perla |
| 7. HTML autónomo + justificación | `salidas/*.html` con plotly.js incrustado; `docs/Documento_justificacion_APA7.pdf` |
| 8. ZIP con código, HTML y PDF | `entrega/Proyecto_Plotly_SDSCJ_entrega.zip` (incluye también los datos, para reproducir las cifras) |

La correspondencia detallada con la rúbrica (nivel **Estratégico**) está en `docs/bitacora_decisiones.md`.

## 4. Reproducibilidad
**En una frase:** el ZIP trae los mismos datos, el mismo código y las mismas versiones de librerías, así que cualquier computador obtiene exactamente las mismas cifras, sin internet.

* **Datos incluidos:** `data/raw/delitos_alto_impacto_SDSCJ.csv` (archivo original, datos hasta el 30/09/2026) y `data/processed/delitos_alto_impacto_normalizado.csv.gz`. Se incluyen porque el Observatorio actualiza el archivo cada mes: volver a descargarlo daría otras cifras.
* **Huella verificada:** al ejecutar, `descarga.py` compara el SHA-256 del CSV con el registrado en `data/raw/metadatos_descarga.json` y avisa si el archivo no es el mismo.
* **Versiones fijas:** `requirements.txt` usa versiones exactas (`==`).
* **Actualizar con datos nuevos (opcional):** `python main.py --forzar` descarga la versión vigente. Las cifras cambiarán y, si un título deja de ser cierto, las pruebas del cuaderno 03 lo detendrán.

## 5. Decisiones de rigor (resumen)
* **Ventana comparable:** 2026 llega a septiembre, así que todos los años suman solo enero–septiembre.
* **Línea base 2018–2022**, no 2023 (mínimo de la serie y año con cambios de registro): evita inflar el crecimiento. El titular tampoco depende de 2023: frente a 2022 el aumento es de +67 %.
* **Fuente externa citada:** el horario de las comisarías de familia (Portal Bogotá, 2025) sustenta la afirmación sobre la atención nocturna; está en `src/config.py` (`COMISARIAS`).
* **Último mes preliminar** detectado automáticamente y marcado con punto hueco.
* **Denuncias ≠ ocurrencia**, **conteos ≠ tasas**: limitaciones declaradas en el HTML y en el PDF.
* **Cifras sin escribir a mano:** HTML y PDF leen el mismo `salidas/kpis.json`; pruebas automáticas verifican que los títulos sigan siendo ciertos si los datos se actualizan.

## 6. Problemas frecuentes
| Síntoma | Solución |
|---|---|
| Error SSL al descargar (solo con `--forzar`) | `pip install truststore` (ya está en requirements). Si persiste, descargue el CSV desde el botón gris del tablero y guárdelo como `data/raw/delitos_alto_impacto_SDSCJ.csv`. |
| Los gráficos no se ven en el cuaderno | Instale `nbformat` y reinicie el kernel. |
| `ModuleNotFoundError: src` | Ejecute los cuadernos desde la carpeta `notebooks/` del proyecto (la primera celda ajusta la ruta). |
| El PDF supera 3 páginas | Se verifica automáticamente si está instalado `pypdf`. |
