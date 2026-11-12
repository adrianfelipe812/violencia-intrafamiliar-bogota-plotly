"""
main.py — Ejecuta TODO el flujo de punta a punta sin abrir los cuadernos.

    python main.py            # usa el CSV si ya está descargado
    python main.py --forzar   # vuelve a descargar desde el Observatorio

Pasos: descarga → normalización y validación → KPIs → HTML autónomo → PDF → ZIP.
"""
import argparse
import subprocess
import sys

from src import analisis, artefacto, config, descarga, normalizacion
from src.empaquetar import empaquetar


def main(forzar: bool = False) -> None:
    descarga.descargar(forzar=forzar)
    df, reporte = normalizacion.ejecutar()
    kpis = analisis.construir_kpis(df, reporte)
    artefacto.guardar_kpis(kpis)
    artefacto.construir_html(df, kpis)
    subprocess.run([sys.executable, str(config.RAIZ / "docs" / "generar_justificacion.py")], check=True)
    empaquetar()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--forzar", action="store_true")
    main(p.parse_args().forzar)
