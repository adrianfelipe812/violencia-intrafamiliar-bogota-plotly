"""
artefacto.py — Paso 5: ensamblar las tres perlas en UN HTML autónomo.

Estructura narrativa del HTML (Nussbaumer Knaflic, 2015):
    BING  → encabezado con la Gran Idea y 4 cifras clave
    BANG  → Acto 1 (planteamiento) · Acto 2 (nudo) · Acto 3 (desenlace) · Síntesis
    BONGO → llamada a la acción que repite el mensaje + notas éticas

Autonomía: plotly.js se incrusta UNA sola vez dentro del archivo
(include_plotlyjs=True) → abre con doble clic, sin Python y sin internet.
"""
from __future__ import annotations

import json
from datetime import date

from src import config as C
from src import visual as V
from src.visual import es, signo

CSS = f"""
:root {{ --foco:{C.COLOR_FOCO}; --texto:{C.COLOR_TEXTO}; --suave:{C.COLOR_TEXTO_SUAVE};
        --linea:#E5E7EB; --fondo:#FFFFFF; --panel:#F8FAFC; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--fondo); color:var(--texto);
       font-family:{C.FUENTE_TIPOGRAFICA}; line-height:1.55; }}
.contenedor {{ max-width:1120px; margin:0 auto; padding:32px 20px 56px; }}
.etiqueta {{ font-size:12px; letter-spacing:.12em; text-transform:uppercase; color:var(--suave); font-weight:600; }}
h1 {{ font-size:clamp(26px,3.6vw,38px); line-height:1.2; margin:8px 0 14px; max-width:960px; }}
h1 em {{ font-style:normal; color:var(--foco); }}
.bajada {{ font-size:17px; color:#374151; max-width:880px; margin:0 0 26px; }}
.kpis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:14px; margin:0 0 36px; }}
.kpi {{ border:1px solid var(--linea); border-radius:10px; padding:16px 18px; background:var(--fondo); }}
.kpi b {{ display:block; font-size:34px; line-height:1.1; color:var(--foco); font-variant-numeric:tabular-nums; }}
.kpi span {{ font-size:14px; color:#374151; }}
.acto {{ border-top:1px solid var(--linea); padding-top:26px; margin-top:30px; }}
.acto h2 {{ font-size:21px; margin:4px 0 6px; }}
.acto p {{ max-width:860px; margin:0 0 12px; color:#374151; }}
.figura {{ width:100%; margin-top:8px; }}
.guia {{ font-size:13px; color:var(--suave); margin:2px 0 0; }}
.accion {{ margin-top:38px; border-left:5px solid var(--foco); background:#FFF7F2; padding:22px 24px; border-radius:6px; }}
.accion h2 {{ margin:0 0 10px; font-size:22px; }}
.accion ol {{ margin:8px 0 0 20px; padding:0; }}
.accion li {{ margin:6px 0; }}
.notas {{ margin-top:34px; font-size:13px; color:var(--suave); border-top:1px solid var(--linea); padding-top:16px; }}
.notas h3 {{ font-size:14px; color:var(--texto); margin:0 0 6px; }}
.notas li {{ margin:4px 0; }}
@media (max-width:640px) {{ .contenedor {{ padding:20px 14px 40px; }} .kpi b {{ font-size:28px; }} }}
"""


def _caja_historia(muestra: str, decision: str, precaucion: str = "") -> str:
    """Bloque «Qué decidir» (estilos en línea: se ve igual en el HTML y en el cuaderno).

    Solo dos o tres viñetas: el titular ya está en el gráfico; aquí va la evidencia que lo
    sostiene y la decisión que sugiere (sin repetir el mensaje).
    """
    extra = (f'<li style="margin:4px 0;color:{C.COLOR_TEXTO_SUAVE}"><b>Precaución:</b> {precaucion}</li>'
             if precaucion else "")
    return f"""<div style="margin:12px 0 4px;padding:14px 18px;background:#F8FAFC;border-left:4px solid {C.COLOR_FOCO};
border-radius:6px;font-family:{C.FUENTE_TIPOGRAFICA};font-size:14.5px;line-height:1.55;color:{C.COLOR_TEXTO};max-width:960px">
<ul style="margin:0 0 0 18px;padding:0">
<li style="margin:4px 0"><b>Evidencia:</b> {muestra}</li>
<li style="margin:4px 0"><b>Qué decidir:</b> {decision}</li>
{extra}
</ul></div>"""


def _comisarias_txt() -> str:
    k = C.COMISARIAS
    total = k["permanentes"] + k["semipermanentes"] + k["diurnas"]
    return (f"de las {total} comisarías de familia con sede fija, {k['diurnas']} cierran a las {k['cierre_diurnas']}, "
            f"{k['semipermanentes']} a las {k['cierre_semipermanentes']} y solo {k['permanentes']} atienden las 24 horas "
            f"(<a href=\"{k['url']}\" style=\"color:inherit\">{k['cita']}</a>)")


def historias(df, kpis: dict) -> list[str]:
    """Evidencia + decisión debajo de cada gráfico (todas las cifras salen de los datos)."""
    from src import analisis as A

    f, c, p = kpis["foco"], kpis["contraste"], kpis["perfil"]
    ua, ventana = kpis["ultimo_anio"], kpis["ventana"]
    top = kpis["top_localidades_aumento"]
    nombres5 = [x["localidad"] for x in top]
    sig = kpis["siguientes_localidades"]
    siguientes = ", ".join(sig[:-1]) + " y " + sig[-1]
    pct5 = kpis["pct_aumento_top5"]

    h1 = _caja_historia(
        f"{es(f['actual'])} denuncias en {ventana} de {ua} frente a un promedio de {es(f['base'])} en 2018–2022 "
        f"({signo(f['cambio_pct'])} %); frente a 2022, antes de los cambios de registro de 2023, el aumento es "
        f"{signo(f['cambio_pct_vs_2022'])} %. Su peso en los delitos de alto impacto pasó de "
        f"{es(f['participacion_base_pct'])} % a {es(f['participacion_pct'])} %, mientras el hurto a personas está "
        f"{es(abs(c['cambio_pct_vs_pico']))} % por debajo de su pico de {c['anio_pico']}.",
        "medir la violencia intrafamiliar como indicador de seguridad en el tablero distrital, con meta y "
        "seguimiento trimestral, al mismo nivel que el hurto.",
        "son denuncias, no todos los hechos; parte del aumento puede deberse a que hoy se denuncia más.")

    lista = "; ".join(f"{x['localidad']} ({signo(x['aumento'])})" for x in top)
    h2 = _caja_historia(
        f"{lista}: juntas suman el {es(pct5)} % del aumento. {siguientes} quedan muy cerca del quinto lugar.",
        f"asignar primero a {', '.join(nombres5[:-1])} y {nombres5[-1]} las comisarías de familia móviles y los "
        "equipos psicosociales, y revisar la priorización cada trimestre.",
        "son conteos, no tasas (la fuente no trae población por localidad): una localidad más poblada tiende a "
        "tener más casos.")

    dfv, _, _ = A.ventana_comparable(df)
    tabla = A.vif_franja_localidad(dfv, ua)
    maximo = tabla.idxmax(axis=1)
    lider = int((maximo == "Madrugada").sum())
    h3 = _caja_historia(
        f"noche y madrugada reúnen el {es(p['pct_noche_madrugada'])} % de las denuncias de {ua}; la madrugada es la "
        f"franja con más casos en {lider} de las {len(tabla)} localidades con casos ubicables. En cuanto a la "
        f"oferta, {_comisarias_txt()}.",
        "extender el horario de atención de las comisarías a la noche y la madrugada, empezando por las cinco "
        "localidades priorizadas.",
        "la franja del día es la registrada en la denuncia; el horario de las comisarías es el habitual publicado "
        "por la Alcaldía.")
    return [h1, h2, h3]


def construir_html(df, kpis: dict, ruta=None) -> str:
    ruta = ruta or C.ARCHIVO_HTML
    f, c, p = kpis["foco"], kpis["contraste"], kpis["perfil"]
    ua, ventana = kpis["ultimo_anio"], kpis["ventana"]
    top = kpis["top_localidades_aumento"]
    _m = str(kpis.get("calidad", {}).get("alerta_ultimo_mes", {}).get("mes", ""))
    _meses = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
              "septiembre", "octubre", "noviembre", "diciembre"]
    mes_txt = f"{_meses[int(_m[5:7])]} de {_m[:4]}" if len(_m) == 7 else _m
    nombres5 = ", ".join(x["localidad"] for x in top[:-1]) + " y " + top[-1]["localidad"]
    k = C.COMISARIAS

    figs = [V.figura_indice(df, kpis), V.figura_localidades(df, kpis), V.figura_franjas(df, kpis),
            V.figura_sintesis(df, kpis)]
    divs = [fig.to_html(full_html=False, include_plotlyjs=(i == 0), config=V.CONFIG_PLOTLY,
                        div_id=f"perla{i + 1}", default_width="100%") for i, fig in enumerate(figs)]

    hist = historias(df, kpis)
    calidad = kpis.get("calidad", {})
    alerta = calidad.get("alerta_ultimo_mes", {})

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Violencia intrafamiliar en Bogotá · Secretaría de Seguridad {ua}</title>
<meta name="description" content="Narrativa visual interactiva con Plotly sobre la violencia intrafamiliar en Bogotá (datos de la Secretaría Distrital de Seguridad, Convivencia y Justicia).">
<style>{CSS}</style>
</head>
<body>
<main class="contenedor">

<!-- ================= BING: la Gran Idea ================= -->
<div class="etiqueta">Seguridad en Bogotá · denuncias de delitos de alto impacto · Secretaría de Seguridad · {ventana} 2018–{ua}</div>
<h1>La <em>violencia intrafamiliar</em> está {es(f['cambio_pct'])} % por encima de su promedio histórico mientras
el hurto retrocede: la seguridad de Bogotá también se juega dentro de la casa.</h1>
<p class="bajada">Para el Consejo Distrital de Seguridad y las secretarías de Seguridad y de la Mujer: es el delito
de alto impacto que más casos suma y el aumento se concentra en cinco localidades y en las horas en que casi
todas las comisarías están cerradas.</p>

<section class="kpis" aria-label="Cifras clave">
  <div class="kpi"><b>{signo(f['cambio_pct'])} %</b><span>denuncias frente al promedio 2018–2022 ({es(f['actual'])} casos en {ventana} {ua})</span></div>
  <div class="kpi"><b>{es(p['pct_mujeres'])} %</b><span>de las víctimas son mujeres</span></div>
  <div class="kpi"><b>{es(p['pct_menores'])} %</b><span>son niñas, niños o adolescentes</span></div>
  <div class="kpi"><b>{es(p['pct_noche_madrugada'])} %</b><span>de los casos ocurre de noche o de madrugada</span></div>
</section>

<!-- ================= BANG: tres actos ================= -->
<section class="acto">
  <div class="etiqueta">Acto 1 · Planteamiento · ¿Qué está cambiando?</div>
  <p class="guia">Cada línea compara un delito con su propio promedio 2018–2022 (= 100). Use el menú para comparar
  con otro delito; el punto hueco de {ua} incluye un mes preliminar ({mes_txt}).</p>
  <div class="figura">{divs[0]}</div>
  {hist[0]}
</section>

<section class="acto">
  <div class="etiqueta">Acto 2 · Nudo · ¿Dónde crece?</div>
  <p class="guia">Las barras parten de cero. Los botones cambian la métrica y las cinco localidades conservan el color.</p>
  <div class="figura">{divs[1]}</div>
  {hist[1]}
</section>

<section class="acto">
  <div class="etiqueta">Acto 3 · Desenlace · ¿Cuándo actuar?</div>
  <p class="guia">Más intenso = más casos (escala desde 0). Pase el cursor para ver el peso de cada franja en la localidad.</p>
  <div class="figura">{divs[2]}</div>
  {hist[2]}
</section>

<section class="acto">
  <div class="etiqueta">Síntesis · El cambio en una sola mirada</div>
  <p class="guia">Cada mancuerna va del promedio 2018–2022 (○) a {ua} (●): cuanto más larga, mayor el cambio.
  El coral marca lo que la historia pide mirar.</p>
  <div class="figura">{divs[3]}</div>
</section>

<!-- ================= BONGO: llamada a la acción ================= -->
<section class="accion">
  <h2>Llamada a la acción</h2>
  <p>La violencia intrafamiliar ya es el {es(f['participacion_pct'])} % de los delitos de alto impacto y es el que
  más casos suma sobre su promedio histórico. Proponemos al Consejo Distrital de Seguridad tres acciones:</p>
  <ol>
    <li><b>Priorizar {nombres5}</b> en la asignación de comisarías de familia móviles y equipos psicosociales.</li>
    <li><b>Extender la atención a la noche y la madrugada</b>, donde ocurre el {es(p['pct_noche_madrugada'])} % de
    los casos y hoy solo {k['permanentes']} comisarías atienden las 24 horas.</li>
    <li><b>Medir la violencia intrafamiliar como indicador de seguridad</b> en el tablero distrital, al mismo nivel
    que el hurto, con meta y seguimiento trimestral.</li>
  </ol>
</section>

<section class="notas">
  <h3>Notas metodológicas y éticas</h3>
  <ul>
    <li><b>Denuncias, no ocurrencia:</b> parte del aumento puede deberse a una mayor disposición a denunciar o a
    mejores canales; aun así, más denuncias implican más demanda de atención institucional.</li>
    <li><b>Comparación justa:</b> todos los años suman solo {ventana}, los meses disponibles en {ua}. La línea base
    es el promedio 2018–2022; 2023 no se usa como referencia porque es el mínimo de la serie y el año con cambios
    en el registro. Frente a 2022 el aumento es {signo(f['cambio_pct_vs_2022'])} %.</li>
    <li><b>Mes preliminar:</b> {mes_txt} registra {es(alerta.get('casos', 0))} casos en total, el
    {es(alerta.get('proporcion', 0) * 100)} % del promedio de los tres meses previos (probable rezago de registro):
    las cifras de {ua} serían conservadoras.</li>
    <li><b>Conteos, no tasas:</b> la fuente no incluye población por localidad; el Acto 2 compara cada localidad
    consigo misma.</li>
    <li><b>Excluidos del índice:</b> delitos con menos de {C.UMBRAL_CASOS_INDICE} casos al año (secuestro y hurto
    a entidades financieras), cuyo índice sería inestable.</li>
  </ul>
  <p>{C.FUENTE_TEXTO} Datos actualizados hasta {calidad.get('datos_actualizados_hasta', '')}
  (consulta {calidad.get('fecha_consulta_fuente', '')}). Horario de comisarías: Grandas Medina (2025), Portal Bogotá,
  <a href="{k['url']}" style="color:inherit">bogota.gov.co</a>. Elaboración: {C.INTEGRANTES_TEXTO} ·
  {C.CURSO}, {C.UNIVERSIDAD}, {date.today().year}. Generado con Python y Plotly.</p>
</section>

</main>
</body>
</html>"""
    ruta.write_text(html, encoding="utf-8")
    print(f"✔ HTML autónomo: {ruta} ({ruta.stat().st_size / 1e6:.1f} MB)")
    return str(ruta)


def guardar_kpis(kpis: dict) -> None:
    C.ARCHIVO_KPIS.write_text(json.dumps(kpis, indent=2, ensure_ascii=False, default=float), encoding="utf-8")
