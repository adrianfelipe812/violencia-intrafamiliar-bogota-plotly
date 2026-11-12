"""
empaquetar.py — Paso 8: arma el .zip de entrega que pide la guía.

Contenido: código fuente (.ipynb y .py), visualización final (.html), documento
de justificación (.pdf) y LOS DATOS (CSV crudo + tabla normalizada).

Se incluyen los datos porque el Observatorio actualiza el archivo cada mes: si
el código lo volviera a descargar, otro computador obtendría cifras distintas.
Con el CSV incluido (y su huella SHA-256 verificada en descarga.py), cualquiera
reproduce exactamente las mismas cifras, sin internet.
"""
from __future__ import annotations

import zipfile

from src import config as C

INCLUIR = [
    "README.md", "requirements.txt", "main.py",
    "src/__init__.py", "src/config.py", "src/descarga.py", "src/normalizacion.py",
    "src/analisis.py", "src/visual.py", "src/artefacto.py", "src/empaquetar.py",
    "notebooks/01_descarga_y_normalizacion.ipynb",
    "notebooks/02_exploracion_plotly_express.ipynb",
    "notebooks/03_artefacto_final.ipynb",
    "docs/generar_justificacion.py", "docs/diccionario_datos.md", "docs/bitacora_decisiones.md",
    "data/raw/delitos_alto_impacto_SDSCJ.csv", "data/raw/metadatos_descarga.json",
    "data/processed/delitos_alto_impacto_normalizado.csv.gz", "data/processed/reporte_calidad.json",
    "salidas/kpis.json",
]


def empaquetar(nombre: str = "Proyecto_Plotly_SDSCJ_entrega.zip"):
    destino = C.ENTREGA / nombre
    obligatorios = [C.ARCHIVO_HTML, C.ARCHIVO_PDF, C.ARCHIVO_RAW, C.ARCHIVO_NORMALIZADO]
    faltan = [p.name for p in obligatorios if not p.exists()]
    if faltan:
        raise FileNotFoundError(f"Falta generar: {faltan}. Ejecute primero el cuaderno 03.")
    with zipfile.ZipFile(destino, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for rel in INCLUIR:
            p = C.RAIZ / rel
            if p.exists():
                z.write(p, f"Proyecto_Plotly_SDSCJ/{rel}")
        for p in obligatorios:
            rel = p.relative_to(C.RAIZ).as_posix()
            if rel not in INCLUIR:  # HTML y PDF (los datos ya se escribieron arriba)
                z.write(p, f"Proyecto_Plotly_SDSCJ/{rel}")
    print(f"✔ ZIP de entrega: {destino} ({destino.stat().st_size / 1e6:.1f} MB)")
    return destino


if __name__ == "__main__":
    empaquetar()
