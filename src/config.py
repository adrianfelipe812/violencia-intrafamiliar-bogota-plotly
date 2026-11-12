"""
config.py — Parámetros únicos del proyecto (una sola fuente de verdad).

Todo lo que otro módulo necesita saber (rutas, URL de la fuente, ventana de
comparación, paleta de color, integrantes) vive aquí. Si algo cambia, se cambia
en un solo lugar y el resto del proyecto se ajusta solo.
"""
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Rutas (relativas a la raíz del proyecto, funcionan en Windows y Linux)
# ---------------------------------------------------------------------------
RAIZ = Path(__file__).resolve().parents[1]
DATA_RAW = RAIZ / "data" / "raw"
DATA_PROCESSED = RAIZ / "data" / "processed"
SALIDAS = RAIZ / "salidas"
DOCS = RAIZ / "docs"
ENTREGA = RAIZ / "entrega"

for _carpeta in (DATA_RAW, DATA_PROCESSED, SALIDAS, DOCS, ENTREGA):
    _carpeta.mkdir(parents=True, exist_ok=True)

# El Observatorio publica el archivo con el nombre técnico «SIEDCO.csv»; localmente se guarda
# con un nombre que identifica a la entidad responsable de la publicación (la SDSCJ).
ARCHIVO_RAW = DATA_RAW / "delitos_alto_impacto_SDSCJ.csv"
ARCHIVO_METADATOS_DESCARGA = DATA_RAW / "metadatos_descarga.json"
ARCHIVO_NORMALIZADO = DATA_PROCESSED / "delitos_alto_impacto_normalizado.csv.gz"
ARCHIVO_CALIDAD = DATA_PROCESSED / "reporte_calidad.json"
ARCHIVO_DICCIONARIO = DOCS / "diccionario_datos.md"
ARCHIVO_KPIS = SALIDAS / "kpis.json"
ARCHIVO_HTML = SALIDAS / "Violencia_intrafamiliar_Bogota_SDSCJ.html"
ARCHIVO_PDF = DOCS / "Documento_justificacion_APA7.pdf"

# ---------------------------------------------------------------------------
# 2. Fuente de datos
# ---------------------------------------------------------------------------
URL_DATOS = "https://oaiee.scj.gov.co/DatosDescarga/SIEDCO.csv"
URL_TABLERO = "https://oaiee.scj.gov.co/ObservatorioSCJ/?page=Page-Tematicos"
FUENTE_TEXTO = (
    "Fuente: Secretaría Distrital de Seguridad, Convivencia y Justicia de Bogotá (SDSCJ), Observatorio de "
    "Seguridad, Convivencia y Justicia. Microdato «Seguimiento a delitos de alto impacto» (denuncias)."
)

# ---------------------------------------------------------------------------
# 3. Decisiones analíticas (documentadas en docs/bitacora_decisiones.md)
# ---------------------------------------------------------------------------
# Línea base: promedio 2018–2022. NO se usa 2023 como base porque es el año
# mínimo de la serie y coincide con un cambio en el registro (muchos "no
# reportado"): tomarlo como punto de partida inflaría el crecimiento
# (cherry-picking, Cairo, 2019).
ANIOS_BASE = [2018, 2019, 2020, 2021, 2022]

# Delitos con menos de 100 casos anuales generan índices inestables (pasar de
# 5 a 10 casos = +100 %). Se excluyen del gráfico de índice por honestidad.
UMBRAL_CASOS_INDICE = 100

DELITO_FOCO = "Violencia intrafamiliar"
DELITO_CONTRASTE = "Hurto a personas"

# ---------------------------------------------------------------------------
# 4. Sistema visual (gris para el contexto + un color para la historia)
# ---------------------------------------------------------------------------
COLOR_FOCO = "#D55E00"        # coral/bermellón Okabe–Ito: apto para daltonismo
COLOR_FOCO_SUAVE = "#F6D5C0"  # mismo matiz, baja saturación (barras no foco del ranking)
COLOR_CONTRASTE = "#475569"   # gris pizarra: el "otro" protagonista, sin competir
COLOR_CONTEXTO = "#CBD2DB"    # gris claro: el resto de delitos
COLOR_TEXTO = "#1F2937"
COLOR_TEXTO_SUAVE = "#6B7280"
COLOR_EJE = "#94A3B8"
COLOR_GRILLA = "#F1F5F9"
FUENTE_TIPOGRAFICA = "Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"

# ---------------------------------------------------------------------------
# 5. Datos del documento de entrega
# ---------------------------------------------------------------------------
INTEGRANTES = [
    "Adrian Felipe Grateron",
    "Jhonatan Smith Doncel",
    "Jorge Emmanuel Marin",
]
# ---------------------------------------------------------------------------
# 6. Contexto institucional (fuente externa, citada en el HTML y en el PDF)
# ---------------------------------------------------------------------------
# Horario habitual de las comisarías de familia de Bogotá según la Alcaldía Mayor
# (publicación del 21/12/2025). Sustenta la afirmación sobre la oferta nocturna.
COMISARIAS = {
    "permanentes": 2,          # atienden 24 horas: Engativá y la sede del CAPIV (Paloquemao)
    "semipermanentes": 5,      # cierran a las 11:00 p. m.
    "diurnas": 23,             # cierran a las 4:00 p. m.
    "moviles": 2,
    "cierre_diurnas": "4:00 p. m.",
    "cierre_semipermanentes": "11:00 p. m.",
    "cita": "Grandas Medina, 2025",
    "url": "https://bogota.gov.co/mi-ciudad/integracion-social/horarios-comisarias-de-familia-en-bogota-diciembre-2025-y-enero-2026",
}

# "A, B y C": forma legible para el HTML y el PDF
INTEGRANTES_TEXTO = ", ".join(INTEGRANTES[:-1]) + " y " + INTEGRANTES[-1]
CURSO = "Visualización de Datos – Maestría en Ciencia de Datos"
UNIVERSIDAD = "Universidad Santo Tomás"
DOCENTE = "Diana Pulido"
