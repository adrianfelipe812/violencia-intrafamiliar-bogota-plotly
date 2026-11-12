"""
analisis.py — Paso 3: tablas analíticas que sostienen la historia.

Regla de oro de comparación (la misma que usa el Observatorio):
cuando se comparan años, solo se suman los meses que existen en TODOS los
años comparados. Como 2026 llega hasta septiembre, cada año se suma de enero a
septiembre ("ventana comparable"). Comparar 9 meses de 2026 contra 12 de 2025
sería una distorsión ética (Cairo, 2019).
"""
from __future__ import annotations

import pandas as pd

from src import config


def ventana_comparable(df: pd.DataFrame) -> tuple[pd.DataFrame, int, int]:
    """Filtra enero..último mes del último año. Devuelve (df_filtrado, ultimo_anio, ultimo_mes)."""
    ultimo_anio = int(df["anio"].max())
    ultimo_mes = int(df.loc[df["anio"] == ultimo_anio, "mes"].max())
    return df[df["mes"] <= ultimo_mes].copy(), ultimo_anio, ultimo_mes


def tabla_anual(dfv: pd.DataFrame) -> pd.DataFrame:
    """Casos por delito y año (ventana comparable). Filas = delito, columnas = año."""
    return dfv.pivot_table(index="delito", columns="anio", values="casos", aggfunc="sum", fill_value=0)


def tabla_indice(anual: pd.DataFrame) -> pd.DataFrame:
    """Índice base promedio 2018–2022 = 100, solo delitos con volumen suficiente."""
    base = anual[config.ANIOS_BASE].mean(axis=1)
    suficientes = anual.min(axis=1) >= config.UMBRAL_CASOS_INDICE
    indice = anual.loc[suficientes].div(base[suficientes], axis=0) * 100
    return indice


def resumen_delitos(anual: pd.DataFrame, ultimo_anio: int) -> pd.DataFrame:
    """Base, valor actual, cambio absoluto/porcentual y años consecutivos al alza."""
    base = anual[config.ANIOS_BASE].mean(axis=1)
    actual = anual[ultimo_anio]
    racha = {}
    for delito, fila in anual.iterrows():
        n, anios = 0, sorted(anual.columns)
        for a, b in zip(anios[::-1][1:], anios[::-1]):  # recorre hacia atrás
            if fila[b] > fila[a]:
                n += 1
            else:
                break
        racha[delito] = n
    out = pd.DataFrame({
        "base_2018_2022": base.round(1),
        f"casos_{ultimo_anio}": actual,
        "cambio_abs": (actual - base).round(1),
        "cambio_pct": ((actual / base - 1) * 100).round(1),
        "anios_consecutivos_al_alza": pd.Series(racha),
        "participacion_pct": (actual / actual.sum() * 100).round(1),
    })
    return out.sort_values("cambio_abs", ascending=False)


def vif_por_localidad(dfv: pd.DataFrame, ultimo_anio: int) -> pd.DataFrame:
    """Violencia intrafamiliar por localidad: base 2018–2022 vs. año actual."""
    vif = dfv[dfv["delito"] == config.DELITO_FOCO]
    p = vif.pivot_table(index="localidad", columns="anio", values="casos", aggfunc="sum", fill_value=0)
    out = pd.DataFrame({
        "base": p[config.ANIOS_BASE].mean(axis=1),
        "actual": p[ultimo_anio],
    })
    out["aumento"] = out["actual"] - out["base"]
    out["cambio_pct"] = (out["actual"] / out["base"] - 1) * 100
    return out.round(1)


def vif_franja_localidad(dfv: pd.DataFrame, ultimo_anio: int) -> pd.DataFrame:
    vif = dfv[(dfv["delito"] == config.DELITO_FOCO) & (dfv["anio"] == ultimo_anio)
              & (dfv["localidad"] != "Sin localización")]
    t = vif.pivot_table(index="localidad", columns="franja_dia", values="casos",
                        aggfunc="sum", fill_value=0, observed=False)
    return t[t.sum(axis=1) > 0]  # fuera filas sin casos (p. ej., Sumapaz)


def cambio_franjas(dfv: pd.DataFrame, ultimo_anio: int) -> pd.DataFrame:
    """Violencia intrafamiliar por franja del día: promedio 2018–2022 vs. año actual."""
    vif = dfv[dfv["delito"] == config.DELITO_FOCO]
    p = vif.pivot_table(index="franja_dia", columns="anio", values="casos", aggfunc="sum",
                        fill_value=0, observed=False)
    out = pd.DataFrame({"base": p[config.ANIOS_BASE].mean(axis=1), "actual": p[ultimo_anio]})
    out["aumento"] = out["actual"] - out["base"]
    out["cambio_pct"] = (out["actual"] / out["base"] - 1) * 100
    out["part_base"] = out["base"] / out["base"].sum() * 100
    out["part_actual"] = out["actual"] / out["actual"].sum() * 100
    out.index = out.index.astype(str)
    return out.round(1)


def perfil_victimas(dfv: pd.DataFrame, ultimo_anio: int) -> dict:
    vif = dfv[(dfv["delito"] == config.DELITO_FOCO) & (dfv["anio"] == ultimo_anio)]
    total = vif["casos"].sum()
    sexo = vif.groupby("sexo")["casos"].sum() / total * 100
    ciclo = vif.groupby("ciclo_vital", observed=False)["casos"].sum() / total * 100
    franja = vif.groupby("franja_dia", observed=False)["casos"].sum() / total * 100
    sin_arma = vif.loc[vif["arma_grupo"] == "Sin empleo de armas", "casos"].sum() / total * 100
    return {
        "total": int(total),
        "pct_mujeres": round(float(sexo.get("Mujer", 0)), 1),
        "pct_menores": round(float(ciclo.get("Infancia", 0) + ciclo.get("Adolescencia", 0)), 1),
        "pct_vejez": round(float(ciclo.get("Vejez", 0)), 1),
        "pct_madrugada": round(float(franja.get("Madrugada", 0)), 1),
        "pct_noche_madrugada": round(float(franja.get("Madrugada", 0) + franja.get("Noche", 0)), 1),
        "pct_sin_arma": round(float(sin_arma), 1),
        "franja": franja.round(1).to_dict(),
        "ciclo": ciclo.round(1).to_dict(),
    }


def serie_mensual(df: pd.DataFrame, delitos: list[str]) -> pd.DataFrame:
    return (df[df["delito"].isin(delitos)]
            .groupby(["fecha", "delito"], as_index=False)["casos"].sum())


def construir_kpis(df: pd.DataFrame, reporte_calidad: dict | None = None) -> dict:
    """Calcula todas las cifras que cita el HTML y el PDF (una sola fuente de verdad)."""
    dfv, ua, um = ventana_comparable(df)
    anual = tabla_anual(dfv)
    resumen = resumen_delitos(anual, ua)
    loc = vif_por_localidad(dfv, ua).drop(index="Sin localización", errors="ignore")
    foco, contraste = resumen.loc[config.DELITO_FOCO], resumen.loc[config.DELITO_CONTRASTE]
    perfil = perfil_victimas(dfv, ua)
    top_loc = loc.sort_values("aumento", ascending=False).head(5)
    pico_contraste = int(anual.loc[config.DELITO_CONTRASTE].idxmax())
    kpis = {
        "ultimo_anio": ua,
        "ultimo_mes": um,
        "ventana": f"enero–{['', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'][um]}",
        "foco": {
            "delito": config.DELITO_FOCO,
            "base": float(foco["base_2018_2022"]),
            "actual": int(foco[f"casos_{ua}"]),
            "cambio_pct": float(foco["cambio_pct"]),
            "cambio_abs": float(foco["cambio_abs"]),
            "racha": int(foco["anios_consecutivos_al_alza"]),
            "participacion_pct": float(foco["participacion_pct"]),
            "participacion_base_pct": round(float(
                anual.loc[config.DELITO_FOCO, config.ANIOS_BASE].sum()
                / anual[config.ANIOS_BASE].sum().sum() * 100), 1),
            "ranking_cambio_abs": int(list(resumen.index).index(config.DELITO_FOCO) + 1),
            # Robustez: comparación contra 2022, el último año antes de los cambios de registro de 2023
            "casos_2022": int(anual.loc[config.DELITO_FOCO, 2022]),
            "cambio_pct_vs_2022": round(float((foco[f"casos_{ua}"] / anual.loc[config.DELITO_FOCO, 2022] - 1) * 100), 1),
        },
        "contraste": {
            "delito": config.DELITO_CONTRASTE,
            "actual": int(contraste[f"casos_{ua}"]),
            "cambio_pct_vs_base": float(contraste["cambio_pct"]),
            "anio_pico": pico_contraste,
            "pico": int(anual.loc[config.DELITO_CONTRASTE, pico_contraste]),
            "cambio_pct_vs_pico": round(float(
                (contraste[f"casos_{ua}"] / anual.loc[config.DELITO_CONTRASTE, pico_contraste] - 1) * 100), 1),
        },
        "unicos_con_racha_3": resumen.index[resumen["anios_consecutivos_al_alza"] >= 3].tolist(),
        "perfil": perfil,
        "top_localidades_aumento": [
            {"localidad": l, "base": float(r.base), "actual": int(r.actual),
             "aumento": float(r.aumento), "cambio_pct": float(r.cambio_pct)}
            for l, r in top_loc.iterrows()],
        "franjas": cambio_franjas(dfv, ua).to_dict(orient="index"),
        "siguientes_localidades": loc.sort_values("aumento", ascending=False).iloc[5:8].index.tolist(),
        "pct_aumento_top5": round(float(top_loc["aumento"].sum() / loc["aumento"].clip(lower=0).sum() * 100), 1),
        "sin_localizacion": {
            str(a): int(dfv[(dfv["delito"] == config.DELITO_FOCO) & (dfv["anio"] == a)
                            & (dfv["localidad"] == "Sin localización")]["casos"].sum())
            for a in (config.ANIOS_BASE[-1], ua)},
        "resumen_delitos": resumen.reset_index().rename(columns={"index": "delito"}).to_dict(orient="records"),
    }
    if reporte_calidad:
        kpis["calidad"] = {k: reporte_calidad[k] for k in
                           ("periodo", "datos_actualizados_hasta", "fecha_consulta_fuente", "alerta_ultimo_mes")}
    return kpis
