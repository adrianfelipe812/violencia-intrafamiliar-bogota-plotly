"""
normalizacion.py — Paso 2: de CSV crudo a tabla tidy, tipada y validada.

Por qué normalizar
------------------
El CSV publicado trae: separador «;», BOM UTF-8, etiquetas en MAYÚSCULAS,
dos columnas de metadatos que solo vienen llenas en la primera fila
(«Fecha de consulta» y «Datos actualizados hasta») y 43 categorías de arma.
Para graficar con rigor necesitamos una tabla donde:

* cada fila = una combinación única (año, mes, delito, localidad, sexo, arma,
  ciclo vital, franja del día) y su número de casos (formato *tidy*);
* los tipos sean correctos (enteros, fechas) y las etiquetas sean legibles
  para una audiencia no técnica (con tildes y mayúscula inicial);
* la suma total de casos se conserve exactamente (validación de integridad).

Salidas
-------
* data/processed/delitos_alto_impacto_normalizado.csv.gz — tabla limpia
* data/processed/reporte_calidad.json        — validaciones y alertas
* docs/diccionario_datos.md                  — diccionario de datos
"""
from __future__ import annotations

import json
import unicodedata

import pandas as pd

from src import config

# ---------------------------------------------------------------------------
# Diccionarios de normalización
# ---------------------------------------------------------------------------
RENOMBRAR = {
    "SEXO": "sexo",
    "ANIO": "anio",
    "MES": "mes",
    "HECHO": "delito",
    "LOCALIDAD": "localidad",
    "COD_LOCALIDAD": "cod_localidad",
    "ARMA_EMPLEADA": "arma_empleada",
    "RANGO_VITAL": "ciclo_vital",
    "RANGO_DEL_DIA": "franja_dia",
    "CANTIDAD": "casos",
}
COLUMNAS_METADATO = ["Fecha de consulta", "Datos actualizados hasta"]

ETIQUETAS_DELITO = {
    "DELITOS SEXUALES": "Delitos sexuales",
    "EXTORSION": "Extorsión",
    "HOMICIDIOS": "Homicidios",
    "HURTO A COMERCIO": "Hurto a comercio",
    "HURTO A ENTIDADES FINANCIERAS": "Hurto a entidades financieras",
    "HURTO A PERSONAS": "Hurto a personas",
    "HURTO A RESIDENCIAS": "Hurto a residencias",
    "HURTO AUTOMOTORES": "Hurto de automotores",
    "HURTO MOTOCICLETAS": "Hurto de motocicletas",
    "LESIONES PERSONALES": "Lesiones personales",
    "SECUESTRO": "Secuestro",
    "VIOLENCIA INTRAFAMILIAR": "Violencia intrafamiliar",
}
ETIQUETAS_SEXO = {"FEMENINO": "Mujer", "MASCULINO": "Hombre", "NO REPORTADO": "No reportado"}
ETIQUETAS_CICLO = {
    "INFANCIA": "Infancia", "ADOLESCENCIA": "Adolescencia", "ADULTEZ": "Adultez",
    "VEJEZ": "Vejez", "NO REPORTADO": "No reportado",
}
ORDEN_CICLO = ["Infancia", "Adolescencia", "Adultez", "Vejez", "No reportado"]
ETIQUETAS_FRANJA = {"MADRUGADA": "Madrugada", "MAÑANA": "Mañana", "TARDE": "Tarde", "NOCHE": "Noche"}
ORDEN_FRANJA = ["Madrugada", "Mañana", "Tarde", "Noche"]  # orden cronológico del día
EXCEPCIONES_LOCALIDAD = {"SIN LOCALIZACION": "Sin localización"}

# 43 categorías de arma -> 9 grupos interpretables (las originales se conservan)
GRUPOS_ARMA = {
    "SIN EMPLEO DE ARMAS": "Sin empleo de armas",
    "ARMA BLANCA / CORTOPUNZANTE": "Arma blanca / cortopunzante",
    "ARMA DE FUEGO": "Arma de fuego",
    "ARMA TRAUMATICA": "Arma de fuego",
    "CONTUNDENTES": "Contundentes",
    "LLAVE MAESTRA": "Herramientas (llave maestra, palancas)",
    "PALANCAS": "Herramientas (llave maestra, palancas)",
    "ESCOPOLAMINA": "Sustancias (escopolamina, químicos)",
    "ACIDO": "Sustancias (escopolamina, químicos)",
    "ALUCINOGENOS": "Sustancias (escopolamina, químicos)",
    "MEDICAMENTOS": "Sustancias (escopolamina, químicos)",
    "QUIMICOS": "Sustancias (escopolamina, químicos)",
    "SUSTANCIAS TOXICAS": "Sustancias (escopolamina, químicos)",
    "GASES": "Sustancias (escopolamina, químicos)",
    "ALIMENTOS VENCIDOS": "Sustancias (escopolamina, químicos)",
    "COMBUSTIBLE": "Sustancias (escopolamina, químicos)",
    "AGUA CALIENTE": "Sustancias (escopolamina, químicos)",
    "LLAMADA TELEFONICA": "Medios telefónicos / digitales",
    "REDES SOCIALES": "Medios telefónicos / digitales",
    "CARTA EXTORSIVA": "Medios telefónicos / digitales",
    "NO REPORTADO": "No reportado / por establecer",
    "POR ESTABLECER": "No reportado / por establecer",
}


def _limpiar_texto(s: pd.Series) -> pd.Series:
    """Quita espacios sobrantes y normaliza Unicode (NFC) sin perder tildes."""
    return (s.astype("string")
             .str.strip()
             .str.replace(r"\s+", " ", regex=True)
             .map(lambda x: unicodedata.normalize("NFC", x) if isinstance(x, str) else x))


def _titulo_es(texto: str) -> str:
    """'CIUDAD BOLÍVAR' -> 'Ciudad Bolívar'; respeta conectores en minúscula."""
    if texto in EXCEPCIONES_LOCALIDAD:
        return EXCEPCIONES_LOCALIDAD[texto]
    menores = {"de", "del", "la", "las", "los", "y", "a"}
    palabras = texto.lower().split()
    return " ".join(p if (i > 0 and p in menores) else p.capitalize() for i, p in enumerate(palabras))


def leer_crudo(ruta=None) -> tuple[pd.DataFrame, dict]:
    """Lee el CSV crudo como texto y separa las columnas de metadatos."""
    ruta = ruta or config.ARCHIVO_RAW
    crudo = pd.read_csv(ruta, sep=";", encoding="utf-8-sig", dtype=str, keep_default_na=False)
    crudo.columns = [c.strip() for c in crudo.columns]

    esperadas = set(RENOMBRAR) | set(COLUMNAS_METADATO)
    faltan = esperadas - set(crudo.columns)
    if faltan:
        raise ValueError(f"El archivo cambió de estructura. Faltan columnas: {sorted(faltan)}")

    meta = {}
    for col in COLUMNAS_METADATO:
        valores = [v for v in crudo[col].unique() if v.strip()]
        meta[col] = valores[0] if valores else None
    return crudo.drop(columns=COLUMNAS_METADATO), meta


def normalizar(crudo: pd.DataFrame) -> pd.DataFrame:
    """Aplica limpieza, tipado, etiquetas legibles y variables derivadas."""
    df = crudo.rename(columns=RENOMBRAR).copy()
    for c in ["sexo", "delito", "localidad", "arma_empleada", "ciclo_vital", "franja_dia"]:
        df[c] = _limpiar_texto(df[c]).str.upper()

    # Tipos numéricos (falla ruidosamente si aparece algo no numérico)
    for c in ["anio", "mes", "cod_localidad", "casos"]:
        df[c] = pd.to_numeric(df[c], errors="raise")
    df = df.astype({"anio": "int16", "mes": "int8", "cod_localidad": "int16", "casos": "int32"})

    # Conservamos el código original del arma antes de etiquetar
    df["arma_original"] = df["arma_empleada"]
    df["arma_grupo"] = df["arma_original"].map(GRUPOS_ARMA).fillna("Otros medios")

    # Etiquetas legibles para audiencia no técnica
    df["delito"] = df["delito"].map(ETIQUETAS_DELITO).fillna(df["delito"].map(_titulo_es))
    df["sexo"] = df["sexo"].map(ETIQUETAS_SEXO).fillna("No reportado")
    df["ciclo_vital"] = df["ciclo_vital"].map(ETIQUETAS_CICLO).fillna("No reportado")
    df["franja_dia"] = df["franja_dia"].map(ETIQUETAS_FRANJA)
    df["localidad"] = df["localidad"].map(_titulo_es)

    # Variables derivadas
    df["fecha"] = pd.to_datetime(dict(year=df["anio"], month=df["mes"], day=1))
    df["ciclo_vital"] = pd.Categorical(df["ciclo_vital"], categories=ORDEN_CICLO, ordered=True)
    df["franja_dia"] = pd.Categorical(df["franja_dia"], categories=ORDEN_FRANJA, ordered=True)

    columnas = ["fecha", "anio", "mes", "delito", "cod_localidad", "localidad", "sexo",
                "ciclo_vital", "franja_dia", "arma_grupo", "arma_original", "casos"]
    return df[columnas].sort_values(["fecha", "delito", "cod_localidad"]).reset_index(drop=True)


def validar(crudo: pd.DataFrame, df: pd.DataFrame, meta: dict) -> dict:
    """Pruebas de integridad. Lanza AssertionError si algo grave falla."""
    total_crudo = pd.to_numeric(crudo["CANTIDAD"]).sum()
    llave = ["anio", "mes", "delito", "localidad", "sexo", "arma_original", "ciclo_vital", "franja_dia"]

    assert df["casos"].sum() == total_crudo, "Se perdieron o duplicaron casos al normalizar"
    assert len(df) == len(crudo), "Cambió el número de filas"
    assert df.isna().sum().sum() == 0, "Hay valores nulos tras normalizar"
    assert (df["casos"] > 0).all(), "Hay conteos no positivos"
    assert df["mes"].between(1, 12).all(), "Meses fuera de rango"
    assert not df.duplicated(llave).any(), "Hay combinaciones duplicadas (rompe el formato tidy)"
    pares = df.groupby("cod_localidad")["localidad"].nunique()
    assert (pares == 1).all(), "Un código de localidad apunta a más de un nombre"

    # Alerta: completitud del último mes publicado (rezago típico de registro)
    mensual = df.groupby("fecha")["casos"].sum()
    ultimo = mensual.index.max()
    ref = mensual.iloc[-4:-1].mean()
    ratio = float(mensual.iloc[-1] / ref)

    reporte = {
        "filas": int(len(df)),
        "casos_totales": int(df["casos"].sum()),
        "periodo": [str(df["fecha"].min().date()), str(ultimo.date())],
        "fecha_consulta_fuente": meta.get("Fecha de consulta"),
        "datos_actualizados_hasta": meta.get("Datos actualizados hasta"),
        "delitos": sorted(df["delito"].unique().tolist()),
        "localidades": int(df["localidad"].nunique()),
        "categorias_arma_originales": int(df["arma_original"].nunique()),
        "grupos_arma": sorted(df["arma_grupo"].unique().tolist()),
        "validaciones_superadas": [
            "Total de casos conservado", "Mismo número de filas", "Sin nulos",
            "Conteos positivos", "Meses 1–12", "Sin duplicados en la llave tidy",
            "Código ↔ nombre de localidad 1:1",
        ],
        "alerta_ultimo_mes": {
            "mes": str(ultimo.date())[:7],
            "casos": int(mensual.iloc[-1]),
            "promedio_3_meses_previos": round(float(ref), 1),
            "proporcion": round(ratio, 3),
            "interpretacion": ("El último mes publicado está por debajo del promedio reciente: "
                               "probable rezago de registro. Se marca como PRELIMINAR en los gráficos.")
                              if ratio < 0.85 else "Sin señales de rezago.",
        },
    }
    return reporte


def escribir_diccionario(df: pd.DataFrame, reporte: dict) -> None:
    filas = [
        ("fecha", "fecha", "Primer día del mes del registro (derivada de año y mes)."),
        ("anio", "entero", "Año del hecho."),
        ("mes", "entero", "Mes del hecho (1–12)."),
        ("delito", "texto", "Delito de alto impacto (12 categorías, etiquetas legibles)."),
        ("cod_localidad", "entero", "Código oficial de localidad (1–20; 99 = sin localización)."),
        ("localidad", "texto", "Nombre de la localidad de Bogotá."),
        ("sexo", "texto", "Sexo de la víctima: Mujer, Hombre, No reportado."),
        ("ciclo_vital", "categoría ordenada", "Infancia, Adolescencia, Adultez, Vejez, No reportado."),
        ("franja_dia", "categoría ordenada", "Madrugada, Mañana, Tarde, Noche."),
        ("arma_grupo", "texto", "Agrupación analítica de las 43 armas originales en 9 grupos."),
        ("arma_original", "texto", "Arma o medio tal como viene en la fuente."),
        ("casos", "entero", "Número de casos (denuncias) en la combinación de la fila."),
    ]
    md = ["# Diccionario de datos — `delitos_alto_impacto_normalizado.csv.gz`", "",
          f"Periodo: {reporte['periodo'][0]} a {reporte['periodo'][1]} · "
          f"Filas: {reporte['filas']:,} · Casos: {reporte['casos_totales']:,}".replace(",", "."), "",
          f"Datos actualizados por la fuente hasta: {reporte['datos_actualizados_hasta']} "
          f"(consulta del {reporte['fecha_consulta_fuente']}).", "",
          "| Variable | Tipo | Descripción |", "|---|---|---|"]
    md += [f"| `{v}` | {t} | {d} |" for v, t, d in filas]
    md += ["", "## Grupos de arma", "", "| Arma original | Grupo |", "|---|---|"]
    pares = df[["arma_original", "arma_grupo"]].drop_duplicates().sort_values(["arma_grupo", "arma_original"])
    md += [f"| {a} | {g} |" for a, g in pares.itertuples(index=False)]
    md += ["", "> Nota: los registros son **denuncias** (casos conocidos por la Policía), no la "
           "ocurrencia real de los delitos."]
    config.ARCHIVO_DICCIONARIO.write_text("\n".join(md), encoding="utf-8")


def ejecutar(ruta=None) -> tuple[pd.DataFrame, dict]:
    crudo, meta = leer_crudo(ruta)
    df = normalizar(crudo)
    reporte = validar(crudo, df, meta)
    df.to_csv(config.ARCHIVO_NORMALIZADO, index=False, encoding="utf-8", compression="gzip")
    config.ARCHIVO_CALIDAD.write_text(json.dumps(reporte, indent=2, ensure_ascii=False), encoding="utf-8")
    escribir_diccionario(df, reporte)
    miles = lambda n: f"{n:,}".replace(",", ".")  # noqa: E731 - formato colombiano
    print(f"✔ Normalizado: {miles(reporte['filas'])} filas · {miles(reporte['casos_totales'])} casos · "
          f"{reporte['periodo'][0]} → {reporte['periodo'][1]}")
    print(f"  Alerta último mes: {reporte['alerta_ultimo_mes']['interpretacion']}")
    return df, reporte


def cargar() -> pd.DataFrame:
    """Carga la tabla normalizada con los tipos correctos (para los notebooks)."""
    df = pd.read_csv(config.ARCHIVO_NORMALIZADO, parse_dates=["fecha"])
    df["ciclo_vital"] = pd.Categorical(df["ciclo_vital"], categories=ORDEN_CICLO, ordered=True)
    df["franja_dia"] = pd.Categorical(df["franja_dia"], categories=ORDEN_FRANJA, ordered=True)
    return df


if __name__ == "__main__":
    ejecutar()
