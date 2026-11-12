"""
descarga.py — Paso 1: descargar el microdato de delitos de alto impacto de la
Secretaría Distrital de Seguridad, Convivencia y Justicia (SDSCJ) desde su Observatorio.

Qué hace
--------
1. Descarga https://oaiee.scj.gov.co/DatosDescarga/SIEDCO.csv (el botón gris
   «Descarga microdato de seguimiento a delitos de alto impacto»).
   El servidor publica el archivo con el nombre técnico «SIEDCO.csv».
2. Lo guarda en data/raw/delitos_alto_impacto_SDSCJ.csv SIN modificar su contenido (el dato crudo es sagrado:
   cualquier transformación ocurre después, en normalizacion.py).
3. Registra trazabilidad en data/raw/metadatos_descarga.json: fecha y hora de
   descarga, tamaño, huella SHA-256 y la fecha «Last-Modified» del servidor.
   Con eso cualquier evaluador puede verificar que trabajamos con el mismo archivo.

Uso
---
    python -m src.descarga            # descarga (o reutiliza si ya existe)
    python -m src.descarga --forzar   # vuelve a descargar aunque exista
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import datetime

import requests

try:  # En Windows, usa el almacén de certificados del sistema (evita errores SSL
    import truststore  # con algunos sitios .gov.co cuya cadena no está en certifi).

    truststore.inject_into_ssl()
except Exception:  # pragma: no cover - opcional
    pass

from src import config


def _sha256(ruta) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def descargar(forzar: bool = False, reintentos: int = 3, timeout: int = 120) -> dict:
    """Descarga el CSV y devuelve sus metadatos. Reutiliza el archivo si ya existe."""
    destino = config.ARCHIVO_RAW
    if destino.exists() and not forzar:
        print(f"✔ Ya existe {destino.name} ({destino.stat().st_size/1e6:.1f} MB). "
              "Usa forzar=True para volver a descargar.")
        huella = _sha256(destino)
        if config.ARCHIVO_METADATOS_DESCARGA.exists():
            meta = json.loads(config.ARCHIVO_METADATOS_DESCARGA.read_text(encoding="utf-8"))
            if meta.get("sha256") == huella:
                print(f"✔ Huella SHA-256 verificada ({huella[:12]}…): es el mismo archivo del análisis.")
            else:
                print("⚠ La huella SHA-256 NO coincide con metadatos_descarga.json: el CSV es distinto al "
                      "usado en el análisis y las cifras pueden cambiar.")
            return meta
        return {"archivo": destino.relative_to(config.RAIZ).as_posix(), "sha256": huella}

    ultimo_error = None
    for intento in range(1, reintentos + 1):
        try:
            print(f"⬇ Descargando {config.URL_DATOS} (intento {intento}/{reintentos})…")
            with requests.get(config.URL_DATOS, stream=True, timeout=timeout,
                              headers={"User-Agent": "Proyecto-academico-USTA/1.0"}) as r:
                r.raise_for_status()
                temporal = destino.with_suffix(".part")
                with open(temporal, "wb") as f:
                    for bloque in r.iter_content(chunk_size=1 << 20):
                        f.write(bloque)
                temporal.replace(destino)
                cabeceras = dict(r.headers)
            break
        except requests.RequestException as e:
            ultimo_error = e
            print(f"  ⚠ Falló: {e}")
            time.sleep(3 * intento)
    else:
        raise RuntimeError(
            "No se pudo descargar el archivo. Descárguelo manualmente desde el botón gris "
            f"del tablero ({config.URL_TABLERO}) y guárdelo como {destino}"
        ) from ultimo_error

    meta = {
        "url": config.URL_DATOS,
        "archivo": destino.relative_to(config.RAIZ).as_posix(),
        "fecha_descarga": datetime.now().isoformat(timespec="seconds"),
        "bytes": destino.stat().st_size,
        "sha256": _sha256(destino),
        "last_modified_servidor": cabeceras.get("Last-Modified"),
    }
    config.ARCHIVO_METADATOS_DESCARGA.write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✔ Guardado en {destino} ({meta['bytes']/1e6:.1f} MB) · SHA-256 {meta['sha256'][:12]}…")
    return meta


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Descarga el microdato de delitos de alto impacto (SDSCJ).")
    p.add_argument("--forzar", action="store_true", help="Volver a descargar aunque exista.")
    descargar(forzar=p.parse_args().forzar)
