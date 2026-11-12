"""
visual.py — Paso 4: las tres "perlas" en Plotly Graph Objects.

Cada figura sigue la matriz de la Sesión 4: Bing (título activo) · Bang (trazas
con contraste preatentivo) · Bongo (capa de anotación + hover narrativo).

Decisiones transversales
------------------------
* Gris para el contexto, un solo color (coral #D55E00) para el protagonista.
* Sin fondo gris, sin bordes, rejilla mínima: máxima proporción datos-tinta.
* Etiquetado directo en lugar de leyenda (proximidad, Gestalt).
* Formato numérico colombiano: separators=",." → 43.013 y 61,2 %.
* Ejes con rangos fijos ("blindados") para que la interacción no los mueva.
* Cada control que cambia datos cambia TAMBIÉN título y anotaciones
  (method="update"), para no generar disonancia (Sesión 5).
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from src import config as C
from src import analisis as A


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def es(x: float, d: int = 0) -> str:
    """Formato colombiano: 43013 -> '43.013' · 61.24 (d=1) -> '61,2'."""
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def palabra(n: int) -> str:
    """3 -> 'tres' (los números pequeños se leen mejor en palabras)."""
    return {1: "un", 2: "dos", 3: "tres", 4: "cuatro", 5: "cinco", 6: "seis"}.get(n, str(n))


def signo(x: float, d: int = 0) -> str:
    return ("+" if x >= 0 else "−") + es(abs(x), d)


EJE = dict(showline=True, linewidth=1, linecolor=C.COLOR_EJE, mirror=False,
           showgrid=False, zeroline=False, ticks="", tickfont=dict(color=C.COLOR_TEXTO_SUAVE, size=12),
           title_font=dict(color=C.COLOR_TEXTO_SUAVE, size=12))

CONFIG_PLOTLY = {
    "displaylogo": False,
    "responsive": True,
    "scrollZoom": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d", "zoomIn2d", "zoomOut2d",
                               "hoverCompareCartesian", "hoverClosestCartesian", "toggleSpikelines"],
    "toImageButtonOptions": {"format": "png", "filename": "VIF_Bogota_SDSCJ", "scale": 2},
}


def _layout_base(fig: go.Figure, titulo: str, subtitulo: str, alto: int, margen_der: int = 40,
                 margen_sup: int = 110) -> None:
    fig.update_layout(
        title=dict(text=f"<b>{titulo}</b><br><sup style='color:{C.COLOR_TEXTO_SUAVE}'>{subtitulo}</sup>",
                   x=0, xanchor="left", y=0.97, yanchor="top",
                   font=dict(size=19, color=C.COLOR_TEXTO, family=C.FUENTE_TIPOGRAFICA)),
        font=dict(family=C.FUENTE_TIPOGRAFICA, color=C.COLOR_TEXTO),
        plot_bgcolor="white", paper_bgcolor="white",
        separators=",.",
        height=alto, autosize=True,
        margin=dict(l=20, r=margen_der, t=margen_sup, b=60),
        showlegend=False,
        hoverlabel=dict(bgcolor="white", bordercolor=C.COLOR_EJE,
                        font=dict(family=C.FUENTE_TIPOGRAFICA, size=13, color=C.COLOR_TEXTO)),
    )


def _menu(botones: list[dict], x: float = 0, y: float = 1.0, tipo: str = "dropdown") -> list[dict]:
    return [dict(type=tipo, direction="down" if tipo == "dropdown" else "right", showactive=True,
                 x=x, xanchor="left", y=y, yanchor="bottom", pad=dict(t=0, r=6),
                 bgcolor="white", bordercolor=C.COLOR_EJE, borderwidth=1,
                 font=dict(size=12, color=C.COLOR_TEXTO), buttons=botones, active=0)]


def _nota(texto: str, x, y, color: str, ax: int = 0, ay: int = 0, flecha: bool = True,
          xref: str = "x", yref: str = "y", xanchor: str = "center", caja: bool = True,
          size: int = 12) -> dict:
    d = dict(x=x, y=y, xref=xref, yref=yref, text=texto, showarrow=flecha, ax=ax, ay=ay,
             arrowhead=2, arrowsize=1, arrowwidth=1.2, arrowcolor=color, xanchor=xanchor,
             align="left", font=dict(color=color, size=size))
    if caja:
        d.update(bgcolor="rgba(255,255,255,0.94)", bordercolor=color, borderwidth=1, borderpad=5)
    return d


# ---------------------------------------------------------------------------
# PERLA 1 · Acto 1 (Planteamiento): el único delito que no deja de crecer
# ---------------------------------------------------------------------------
def figura_indice(df: pd.DataFrame, kpis: dict) -> go.Figure:
    dfv, ua, um = A.ventana_comparable(df)
    anual = A.tabla_anual(dfv)
    indice = A.tabla_indice(anual)
    anios = list(indice.columns)
    foco, contraste = C.DELITO_FOCO, C.DELITO_CONTRASTE
    # Orden de dibujo: contexto primero, protagonistas encima (z-order)
    delitos = [d for d in indice.index if d not in (foco, contraste)] + [contraste, foco]
    ventana = kpis["ventana"]

    simbolos = ["circle"] * (len(anios) - 1) + ["circle-open"]  # último año = preliminar
    fig = go.Figure()
    for d in delitos:
        notas_hover = [f"Casos {ventana}: {es(anual.loc[d, a])}" +
                       ("<br><i>Septiembre preliminar: posible subregistro</i>" if a == ua else "")
                       for a in anios]
        fig.add_trace(go.Scatter(
            x=anios, y=indice.loc[d].round(1), name=d, mode="lines+markers",
            customdata=notas_hover,
            marker=dict(symbol=simbolos, size=6, line=dict(width=1.5)),
            hovertemplate=f"<b>{d} · %{{x}}</b><br>Índice: %{{y:.0f}} (2018–2022 = 100)"
                          "<br>%{customdata}<extra></extra>",
        ))

    def estilo(destacado: str, referencia: str | None):
        colores, anchos, tam, borde = [], [], [], []
        for d in delitos:
            if d == destacado:
                colores.append(C.COLOR_FOCO); anchos.append(4.5); tam.append(9); borde.append(1.5)
            elif d == referencia:
                colores.append(C.COLOR_CONTRASTE); anchos.append(2.5); tam.append(6); borde.append(1.5)
            else:
                colores.append(C.COLOR_CONTEXTO); anchos.append(1.4); tam.append(0); borde.append(0)
        return {"line.color": colores, "marker.color": colores, "line.width": anchos, "marker.size": tam,
                "marker.line.width": borde}

    ymax = float(indice.max().max())
    rango_y = [max(0, float(indice.min().min()) - 28), ymax + 20]

    def anot_fijas() -> list[dict]:
        return [
            _nota("Pandemia", 2020, rango_y[1] - 4, C.COLOR_TEXTO_SUAVE, flecha=False, caja=False, size=11),
        ]

    def etiqueta_final(d: str, color: str, negrita=True) -> dict:
        v = indice.loc[d, ua]
        txt = f"<b>{d}</b><br>{es(v)}" if negrita else f"{d} {es(v)}"
        return dict(x=ua, y=v, xref="x", yref="y", text=txt, showarrow=False, xanchor="left",
                    xshift=10, align="left", font=dict(color=color, size=12))

    f = kpis["foco"]
    # Titular: solo lo que se sostiene sin depender de 2023 (año con cambios de registro).
    if f["ranking_cambio_abs"] == 1:
        titulo_hist = (f"La violencia intrafamiliar es el delito que más creció: "
                       f"{signo(f['cambio_abs'])} casos sobre su promedio 2018–2022")
    else:
        titulo_hist = (f"La violencia intrafamiliar está {es(f['cambio_pct'])} % por encima "
                       f"de su promedio 2018–2022")
    sub_hist = (f"Índice de denuncias {ventana} (promedio 2018–2022 = 100, línea punteada) · {ua}: "
                f"{signo(f['cambio_pct'], 0)} % sobre su línea base<br>El hurto a personas, en cambio, "
                f"retrocede {es(abs(kpis['contraste']['cambio_pct_vs_pico']), 0)} % desde su pico de "
                f"{kpis['contraste']['anio_pico']}")
    anot_hist = anot_fijas() + [
        etiqueta_final(foco, C.COLOR_FOCO), etiqueta_final(contraste, C.COLOR_CONTRASTE),
        _nota(f"<b>{signo(f['cambio_pct'])} %</b> sobre su promedio 2018–2022.<br>"
              f"Incluso frente a 2022 (antes de los cambios<br>de registro de 2023): "
              f"<b>{signo(f['cambio_pct_vs_2022'])} %</b>", ua - 1, indice.loc[foco, ua - 1],
              C.COLOR_FOCO, ax=-160, ay=-60),
        _nota("2023: mínimo y cambios de registro<br>(por eso no se usa como base)",
              2023, indice.loc[foco, 2023], C.COLOR_TEXTO_SUAVE, ax=40, ay=48, caja=False, size=11),
    ]

    botones = [dict(label="📖 La historia: violencia intrafamiliar", method="update",
                    args=[estilo(foco, contraste),
                          {"title.text": f"<b>{titulo_hist}</b><br><sup style='color:{C.COLOR_TEXTO_SUAVE}'>{sub_hist}</sup>",
                           "annotations": anot_hist}])]
    for d in [x for x in indice.sort_values(ua, ascending=False).index if x != foco]:
        v = indice.loc[d, ua]
        tit = f"{d}: índice {es(v)} en {ua} ({signo(v - 100)} % frente a 2018–2022)"
        sub = (f"Compárelo con la violencia intrafamiliar (gris oscuro, índice {es(indice.loc[foco, ua])})"
               f"<br>Denuncias {ventana}, promedio 2018–2022 = 100")
        botones.append(dict(label=f"Comparar con: {d}", method="update",
                            args=[estilo(d, foco),
                                  {"title.text": f"<b>{tit}</b><br><sup style='color:{C.COLOR_TEXTO_SUAVE}'>{sub}</sup>",
                                   "annotations": anot_fijas() + [etiqueta_final(d, C.COLOR_FOCO),
                                                                  etiqueta_final(foco, C.COLOR_CONTRASTE)]}]))

    for k, v in estilo(foco, contraste).items():  # estado inicial = botón 1
        for tr, val in zip(fig.data, v):
            anidado = val
            for parte in reversed(k.split(".")):  # "marker.line.width" -> {"marker": {"line": {...}}}
                anidado = {parte: anidado}
            tr.update(anidado)

    _layout_base(fig, titulo_hist, sub_hist, alto=590, margen_der=170, margen_sup=150)
    fig.update_layout(
        annotations=anot_hist,
        updatemenus=_menu(botones, x=0, y=1.02),
        hovermode="closest",
        xaxis=dict(EJE, tickvals=anios, range=[anios[0] - 0.3, ua + 0.3], fixedrange=True),
        yaxis=dict(EJE, showline=False, showgrid=True, gridcolor=C.COLOR_GRILLA, range=rango_y,
                   fixedrange=True, title="Índice (2018–2022 = 100)"),
        shapes=[
            dict(type="line", xref="paper", x0=0, x1=1, y0=100, y1=100,
                 line=dict(color=C.COLOR_EJE, width=1, dash="dot"), layer="below"),
            dict(type="rect", x0=2019.5, x1=2020.5, yref="paper", y0=0, y1=1,
                 fillcolor="#F1F5F9", line_width=0, layer="below"),
        ],
    )
    return fig


# ---------------------------------------------------------------------------
# PERLA 2 · Acto 2 (Nudo): dónde crece
# ---------------------------------------------------------------------------
def figura_localidades(df: pd.DataFrame, kpis: dict) -> go.Figure:
    dfv, ua, um = A.ventana_comparable(df)
    loc = A.vif_por_localidad(dfv, ua).drop(index="Sin localización", errors="ignore")
    top5 = loc.sort_values("aumento", ascending=False).head(5).index.tolist()
    ventana = kpis["ventana"]

    metricas = [
        ("aumento", "Aumento de casos frente a 2018–2022", lambda v: signo(v),
         "Casos {} {} menos promedio {}".format(ventana, ua, "2018–2022")),
        ("actual", f"Casos {ua}", lambda v: es(v), f"Denuncias de violencia intrafamiliar, {ventana} {ua}"),
        ("cambio_pct", "Variación %", lambda v: signo(v) + " %",
         "Variación porcentual frente al promedio 2018–2022 (cuidado: bases pequeñas inflan el %)"),
    ]
    fig = go.Figure()
    for i, (col, nombre, fmt, _) in enumerate(metricas):
        orden = loc.sort_values(col, ascending=True)
        colores = [C.COLOR_FOCO if l in top5 else C.COLOR_CONTEXTO for l in orden.index]
        hover = [f"<b>{l}</b><br>Promedio 2018–2022: {es(r.base)}<br>{ua}: {es(r.actual)}"
                 f"<br>Cambio: {signo(r.aumento)} casos ({signo(r.cambio_pct)} %)"
                 for l, r in orden.iterrows()]
        fig.add_trace(go.Bar(
            y=orden.index, x=orden[col], orientation="h", name=nombre, visible=(i == 0),
            marker=dict(color=colores, line_width=0), width=0.72,
            text=[fmt(v) for v in orden[col]], textposition="outside", cliponaxis=False,
            textfont=dict(size=11, color=[C.COLOR_FOCO if l in top5 else C.COLOR_TEXTO_SUAVE
                                          for l in orden.index]),
            customdata=hover, hovertemplate="%{customdata}<extra></extra>",
        ))

    pct5 = kpis["pct_aumento_top5"]
    nombres5 = ", ".join(top5[:-1]) + " y " + top5[-1]
    crecen = int((loc["aumento"] > 0).sum())
    top_pct = loc.sort_values("cambio_pct", ascending=False).head(3)
    dup = ", ".join(f"{l} ({signo(r.cambio_pct)} %)" for l, r in top_pct.iterrows())
    titulos = {
        "aumento": (f"Cinco localidades explican el {es(pct5)} % del aumento de la violencia intrafamiliar",
                    f"{nombres5} · aumento de denuncias {ventana} {ua} frente al promedio 2018–2022"),
        "actual": (f"Dónde se denuncia hoy: las mismas cinco localidades encabezan el volumen",
                   f"Denuncias de violencia intrafamiliar {ventana} {ua} por localidad"),
        "cambio_pct": (f"En porcentaje el crecimiento es generalizado: {crecen} de {len(loc)} localidades suben",
                       f"Mayores alzas: {dup} · variación % frente a 2018–2022<br>Las bases pequeñas "
                       "inflan el %: lea también el aumento absoluto"),
    }

    def anot(col):
        top = loc.loc[top5[0]]
        base = [_nota("«Sin localización» se excluye: pasó de "
                      f"{es(kpis['sin_localizacion'][str(C.ANIOS_BASE[-1])])} a "
                      f"{es(kpis['sin_localizacion'][str(ua)])} casos (cambio de registro).",
                      0, -0.155, C.COLOR_TEXTO_SUAVE, flecha=False, caja=False, xref="paper",
                      yref="paper", xanchor="left", size=11)]
        if col == "aumento":
            sig = loc.sort_values("aumento", ascending=False).iloc[5:8]
            cerca = ", ".join(f"{l} ({signo(r.aumento)})" for l, r in sig.iloc[:-1].iterrows())
            cerca += f" y {sig.index[-1]} ({signo(sig.iloc[-1].aumento)})"
            base.append(_nota(f"<b>{top5[0]} lidera</b>: {signo(top.aumento)} casos ({es(top.base)} → "
                              f"{es(top.actual)}).<br>{cerca}<br>quedan muy cerca del quinto lugar: "
                              "también requieren atención.",
                              0.98, 0.30, C.COLOR_FOCO, flecha=False, xref="paper", yref="paper",
                              xanchor="right"))
        return base

    botones = []
    for i, (col, nombre, _, sub_eje) in enumerate(metricas):
        t, s = titulos[col]
        botones.append(dict(label=nombre, method="update",
                            args=[{"visible": [j == i for j in range(len(metricas))]},
                                  {"title.text": f"<b>{t}</b><br><sup style='color:{C.COLOR_TEXTO_SUAVE}'>{s}</sup>",
                                   "annotations": anot(col), "xaxis.title.text": sub_eje,
                                   "xaxis.range": _rango(loc[col]),
                                   "xaxis.tickformat": ",.0f"}]))

    t0, s0 = titulos["aumento"]
    _layout_base(fig, t0, s0, alto=640, margen_der=70, margen_sup=140)
    fig.update_layout(
        annotations=anot("aumento"),
        updatemenus=_menu(botones, x=0, y=1.02, tipo="buttons"),
        bargap=0.25, hovermode="closest",
        xaxis=dict(EJE, showline=False, showgrid=True, gridcolor=C.COLOR_GRILLA, zeroline=True,
                   zerolinecolor=C.COLOR_EJE, zerolinewidth=1, range=_rango(loc["aumento"]),
                   fixedrange=True, title=metricas[0][3], tickformat=",.0f"),
        yaxis=dict(EJE, showline=False, fixedrange=True, tickfont=dict(size=12, color=C.COLOR_TEXTO)),
    )
    fig.update_layout(margin=dict(b=115))
    return fig


def _rango(serie: pd.Series) -> list[float]:
    """Rango que SIEMPRE incluye el cero (integridad de barras) + aire para etiquetas."""
    lo, hi = float(min(0, serie.min())), float(max(0, serie.max()))
    span = hi - lo
    return [lo - (0.12 * span if lo < 0 else 0), hi + 0.16 * span]


# ---------------------------------------------------------------------------
# PERLA 3 · Acto 3 (Desenlace): cuándo actuar
# ---------------------------------------------------------------------------
def figura_franjas(df: pd.DataFrame, kpis: dict) -> go.Figure:
    dfv, ua, um = A.ventana_comparable(df)
    tabla = A.vif_franja_localidad(dfv, ua)
    tabla = tabla.loc[tabla.sum(axis=1).sort_values(ascending=True).index]  # mayor arriba
    franjas = list(tabla.columns)
    top5 = [x["localidad"] for x in kpis["top_localidades_aumento"]]
    ventana = kpis["ventana"]

    pct_fila = tabla.div(tabla.sum(axis=1), axis=0) * 100
    custom = [[f"{es(pct_fila.loc[l, f], 0)} % de los casos de {l}" for f in franjas] for l in tabla.index]
    fig = go.Figure(go.Heatmap(
        z=tabla.values, x=franjas, y=tabla.index, zmin=0,
        colorscale=[[0, "#FFF8F3"], [0.35, "#F5B48A"], [0.7, "#E07A3F"], [1, "#A13F00"]],
        xgap=3, ygap=3, texttemplate="%{z:,.0f}", textfont=dict(size=11),
        customdata=custom, showscale=False,
        hovertemplate="<b>%{y} · %{x}</b><br>%{z:,.0f} denuncias (" + ventana + f" {ua})"
                      "<br>%{customdata}<extra></extra>",
    ))
    p = kpis["perfil"]
    t = (f"Noche y madrugada concentran el {es(p['pct_noche_madrugada'])} % de los casos, "
         "cuando casi todas las comisarías están cerradas")
    s = (f"Denuncias de violencia intrafamiliar por localidad y franja del día, {ventana} {ua} · "
         "color más intenso = más casos (escala desde 0)")
    _layout_base(fig, t, s, alto=700, margen_der=30, margen_sup=120)
    # Resaltar en el eje las 5 localidades del Acto 2 (consistencia narrativa)
    etiquetas = [f"<span style='color:{C.COLOR_FOCO}'><b>{l}</b></span>" if l in top5 else l
                 for l in tabla.index]
    fig.update_layout(
        xaxis=dict(EJE, side="top", showline=False, fixedrange=True,
                   tickfont=dict(size=13, color=C.COLOR_TEXTO)),
        yaxis=dict(EJE, showline=False, fixedrange=True, tickvals=list(tabla.index), ticktext=etiquetas),
        annotations=[
            _nota(f"<b>Madrugada</b>: {es(p['pct_madrugada'])} % del total, la franja con más casos en casi todas<br>"
                  f"las localidades. <b>Noche</b>: {es(p['pct_noche_madrugada'] - p['pct_madrugada'])} %.",
                  "Madrugada", -0.02,
                  C.COLOR_FOCO, flecha=False, xref="x", yref="paper", caja=True, size=12,
                  xanchor="left") | {"yanchor": "top", "xshift": -110},
            _nota("En coral: las 5 localidades<br>con mayor aumento (Acto 2)", 1.0, -0.02,
                  C.COLOR_TEXTO_SUAVE, flecha=False, xref="paper", yref="paper", caja=False,
                  xanchor="right", size=11) | {"yanchor": "top"},
        ],
        margin=dict(b=90),
    )
    return fig


# ---------------------------------------------------------------------------
# SÍNTESIS · el cambio en una sola figura (qué, dónde y cuándo)
# ---------------------------------------------------------------------------
def figura_sintesis(df: pd.DataFrame, kpis: dict) -> go.Figure:
    """Tres paneles de mancuernas con la misma gramática visual: ○ promedio 2018–2022 → ● año actual.

    Generaliza los tres actos: qué delito cambió (Acto 1), dónde (Acto 2) y en qué franja (Acto 3).
    La mancuerna codifica el cambio con POSICIÓN sobre una escala común (el canal más preciso,
    Munzner, 2014) y la línea que une los dos puntos aplica el principio de conexión (Gestalt).
    """
    from plotly.subplots import make_subplots

    dfv, ua, um = A.ventana_comparable(df)
    anual = A.tabla_anual(dfv)
    base_d = anual[C.ANIOS_BASE].mean(axis=1)
    delitos = pd.DataFrame({"base": base_d, "actual": anual[ua]})
    delitos = delitos[delitos[["base", "actual"]].max(axis=1) >= 4000]       # los 6 de mayor volumen
    delitos["aumento"] = delitos["actual"] - delitos["base"]
    delitos = delitos.sort_values("aumento")
    # Panel de delitos en índice (promedio = 100): el hurto (~80.000) aplastaría a los demás (~5.000)
    delitos_idx = delitos.assign(base_real=delitos["base"], actual_real=delitos["actual"],
                                 actual=delitos["actual"] / delitos["base"] * 100, base=100.0)

    loc = A.vif_por_localidad(dfv, ua).drop(index="Sin localización", errors="ignore")
    loc = loc.sort_values("aumento", ascending=False).head(8).sort_values("aumento")
    top5 = [x["localidad"] for x in kpis["top_localidades_aumento"]]

    fr = A.cambio_franjas(dfv, ua).loc[["Noche", "Tarde", "Mañana", "Madrugada"]]  # madrugada arriba

    f = kpis["foco"]
    fig = make_subplots(
        rows=1, cols=3, horizontal_spacing=0.13,
        subplot_titles=(
            "<b>¿Qué cambió?</b> Delitos de alto impacto",
            "<b>¿Dónde?</b> Violencia intrafamiliar por localidad",
            "<b>¿Cuándo?</b> Violencia intrafamiliar por franja",
        ),
    )

    def mancuernas(tabla: pd.DataFrame, col: int, destacados: list[str], etiqueta_pct: bool = True):
        for nombre, r in tabla.iterrows():
            foco = nombre in destacados
            color = C.COLOR_FOCO if foco else C.COLOR_CONTEXTO
            oscuro = C.COLOR_FOCO if foco else C.COLOR_TEXTO_SUAVE
            b_real = r.get("base_real", r.base)
            a_real = r.get("actual_real", r.actual)
            cambio = (a_real / b_real - 1) * 100
            hover = (f"<b>{nombre}</b><br>Promedio 2018–2022: {es(b_real)}<br>{ua}: {es(a_real)}"
                     f"<br>Cambio: {signo(a_real - b_real)} ({signo(cambio)} %)<extra></extra>")
            fig.add_trace(go.Scatter(x=[r.base, r.actual], y=[nombre, nombre], mode="lines",
                                     line=dict(color=color, width=5 if foco else 3),
                                     hoverinfo="skip", showlegend=False), row=1, col=col)
            fig.add_trace(go.Scatter(x=[r.base], y=[nombre], mode="markers", showlegend=False,
                                     marker=dict(size=10, color="white", line=dict(color=oscuro, width=2)),
                                     hovertemplate=hover), row=1, col=col)
            fig.add_trace(go.Scatter(x=[r.actual], y=[nombre], mode="markers+text", showlegend=False,
                                     marker=dict(size=11, color=oscuro),
                                     text=[f" {signo(cambio)} % " if etiqueta_pct else ""],
                                     textposition="middle right" if cambio >= 0 else "middle left",
                                     textfont=dict(size=11, color=oscuro), hovertemplate=hover),
                          row=1, col=col)

    mancuernas(delitos_idx, 1, [C.DELITO_FOCO])
    mancuernas(loc, 2, top5)
    mancuernas(fr, 3, fr["cambio_pct"].nlargest(2).index.tolist())

    p = kpis["perfil"]
    top2 = fr["cambio_pct"].nlargest(2)
    titulo = (f"Del promedio 2018–2022 a {ua}: la violencia intrafamiliar es el delito que más casos suma,<br>"
              f"con el aumento concentrado en cinco localidades y en la {top2.index[0].lower()} "
              f"y la {top2.index[1].lower()}")
    sub = (f"○ promedio 2018–2022 → ● {kpis['ventana']} {ua} · el % es el cambio frente al promedio · "
           "delitos en índice (promedio = 100); localidades y franjas en casos")
    _layout_base(fig, titulo, sub, alto=580, margen_der=40, margen_sup=165)

    conclusiones = [
        (f"La VIF suma <b>{signo(f['cambio_abs'])}</b> casos ({signo(f['cambio_pct'])} %):<br>"
         "el mayor aumento; el hurto a personas<br>crece poco y el hurto a comercio cae.", "x domain"),
        (f"Estas cinco explican el <b>{es(kpis['pct_aumento_top5'])} %</b><br>del aumento; las tres siguientes<br>"
         "están muy cerca.", "x2 domain"),
        (f"La madrugada sigue siendo la franja<br>con más casos, pero el crecimiento<br>"
         f"se dio en la <b>{top2.index[0].lower()}</b> ({signo(top2.iloc[0])} %) y la "
         f"<b>{top2.index[1].lower()}</b> ({signo(top2.iloc[1])} %).<br>Noche + madrugada: "
         f"<b>{es(p['pct_noche_madrugada'])} %</b> de los casos.", "x3 domain"),
    ]
    anots = list(fig.layout.annotations)
    for a in anots:  # títulos de panel alineados a la izquierda
        a.update(xanchor="left", x=a.x - 0.13, font=dict(size=13, color=C.COLOR_TEXTO))
    for texto, xref in conclusiones:
        anots.append(dict(x=0, y=-0.14, xref=xref, yref="paper", text=texto, showarrow=False,
                          xanchor="left", yanchor="top", align="left",
                          font=dict(size=11.5, color=C.COLOR_TEXTO)))
    fig.update_layout(annotations=anots, hovermode="closest", margin=dict(b=150))
    fig.update_xaxes(EJE, showline=False, showgrid=True, gridcolor=C.COLOR_GRILLA, fixedrange=True,
                     tickformat=",.0f", nticks=4)
    fig.update_yaxes(EJE, showline=False, fixedrange=True, tickfont=dict(size=11.5, color=C.COLOR_TEXTO))
    lo, hi = float(delitos_idx["actual"].min()), float(delitos_idx["actual"].max())
    fig.update_xaxes(range=[min(lo, 100) - 40, max(hi, 100) + 45], tickvals=[50, 100, 150], row=1, col=1)
    # aire a la derecha para las etiquetas de porcentaje
    for i, t in [(2, loc), (3, fr)]:
        lo, hi = float(t[["base", "actual"]].min().min()), float(t[["base", "actual"]].max().max())
        fig.update_xaxes(range=[max(0, lo - 0.08 * (hi - lo)), hi + 0.35 * (hi - lo)], row=1, col=i)
    fig.update_xaxes(tickangle=0)
    return fig
