"""
generar_justificacion.py — Documento de justificación (PDF, máx. 3 páginas, APA 7.ª ed.).

Todas las cifras se leen de salidas/kpis.json (calculado desde los datos), de modo
que el PDF y el HTML nunca se contradicen. Los autores se toman de INTEGRANTES
en src/config.py. Se ejecuta con:

    python docs/generar_justificacion.py
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from reportlab.lib import colors  # noqa: E402
from reportlab.lib.enums import TA_JUSTIFY  # noqa: E402
from reportlab.lib.pagesizes import LETTER  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.lib.units import cm  # noqa: E402
from reportlab.pdfbase import pdfmetrics  # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont  # noqa: E402
from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer, Table,  # noqa: E402
                                TableStyle)

from src import config as C  # noqa: E402

_Paragraph = Paragraph


def Paragraph(texto, estilo, *args, **kwargs):  # noqa: N802
    """Espacio no separable antes de «%» para que el número y el signo no se partan entre líneas."""
    return _Paragraph(texto.replace(" %", "\u00a0%"), estilo, *args, **kwargs)


# ---------------------------------------------------------------- tipografía
def _registrar_fuente() -> tuple[str, str, str]:
    candidatos = [
        ("Arial", Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/arialbd.ttf"),
         Path("C:/Windows/Fonts/ariali.ttf")),
        ("DejaVu", Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
         Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
         Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf")),
        ("Liberation", Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
         Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
         Path("/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf")),
    ]
    for nombre, reg, bold, ital in candidatos:
        if reg.exists() and bold.exists() and ital.exists():
            pdfmetrics.registerFont(TTFont(nombre, str(reg)))
            pdfmetrics.registerFont(TTFont(nombre + "-B", str(bold)))
            pdfmetrics.registerFont(TTFont(nombre + "-I", str(ital)))
            pdfmetrics.registerFontFamily(nombre, normal=nombre, bold=nombre + "-B",
                                          italic=nombre + "-I", boldItalic=nombre + "-B")
            return nombre, nombre + "-B", nombre + "-I"
    return "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"


F, FB, FI = _registrar_fuente()
CORAL = colors.HexColor(C.COLOR_FOCO)
GRIS = colors.HexColor("#4B5563")

S_TIT = ParagraphStyle("tit", fontName=FB, fontSize=13.5, leading=17, spaceAfter=3, textColor=colors.black)
S_AUT = ParagraphStyle("aut", fontName=F, fontSize=9, leading=12, textColor=GRIS, spaceAfter=8)
S_H = ParagraphStyle("h", fontName=FB, fontSize=10.5, leading=13, spaceBefore=7, spaceAfter=3, textColor=CORAL)
S_P = ParagraphStyle("p", fontName=F, fontSize=9.4, leading=12.6, alignment=TA_JUSTIFY, spaceAfter=4)
S_GI = ParagraphStyle("gi", parent=S_P, fontName=FB, fontSize=10.2, leading=13.5, leftIndent=10,
                      borderPadding=(6, 8, 6, 8), backColor=colors.HexColor("#FFF4EC"),
                      borderColor=CORAL, borderWidth=0, spaceBefore=2, spaceAfter=8)
S_T = ParagraphStyle("t", fontName=F, fontSize=8.1, leading=10.2)
S_TB = ParagraphStyle("tb", parent=S_T, fontName=FB, textColor=colors.white)
S_REF = ParagraphStyle("ref", fontName=F, fontSize=8.4, leading=10.8, leftIndent=18, firstLineIndent=-18,
                       spaceAfter=2.5)


def palabra(n: int) -> str:
    return {1: "un", 2: "dos", 3: "tres", 4: "cuatro", 5: "cinco", 6: "seis"}.get(n, str(n))


def es(x: float, d: int = 0) -> str:
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def construir() -> Path:
    k = json.loads(C.ARCHIVO_KPIS.read_text(encoding="utf-8"))
    f, c, p = k["foco"], k["contraste"], k["perfil"]
    ua, ventana = k["ultimo_anio"], k["ventana"]
    top = k["top_localidades_aumento"]
    nombres5 = ", ".join(x["localidad"] for x in top[:-1]) + " y " + top[-1]["localidad"]
    alerta = k.get("calidad", {}).get("alerta_ultimo_mes", {})
    hasta = k.get("calidad", {}).get("datos_actualizados_hasta", "")
    _m = str(alerta.get("mes", ""))
    _meses = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
              "septiembre", "octubre", "noviembre", "diciembre"]
    mes_txt = f"{_meses[int(_m[5:7])]} de {_m[:4]}" if len(_m) == 7 else _m

    h = []
    h.append(Paragraph("La seguridad también se juega dentro de la casa: justificación de "
                       "una narrativa visual interactiva con Plotly", S_TIT))
    h.append(Paragraph(f"{C.INTEGRANTES_TEXTO}<br/>{C.CURSO} · {C.UNIVERSIDAD} · Docente: "
                       f"{C.DOCENTE} · {date.today().strftime('%d/%m/%Y')}", S_AUT))

    h.append(Paragraph("1. Gran Idea", S_H))
    h.append(Paragraph(
        f"La violencia intrafamiliar (VIF) está {es(f['cambio_pct'])} % por encima de su promedio histórico "
        "mientras el hurto retrocede: la seguridad de Bogotá también se juega dentro de la casa.", S_GI))
    h.append(Paragraph(
        f"<b>Audiencia:</b> el Consejo Distrital de Seguridad y las secretarías de Seguridad y de la Mujer, "
        f"personas que toman decisiones sin ser especialistas en datos. <b>Conflicto:</b> la agenda pública "
        f"celebra la caída del hurto a personas ({es(c['cambio_pct_vs_pico'])} % frente a su pico de "
        f"{c['anio_pico']}), mientras la VIF supera en {es(f['cambio_pct'])} % su promedio 2018–2022 "
        f"({es(f['actual'])} denuncias en {ventana} de {ua}) y pasa de {es(f['participacion_base_pct'])} % a "
        f"{es(f['participacion_pct'])} % de los delitos de alto impacto. El {es(p['pct_mujeres'])} % de las "
        f"víctimas son mujeres y el {es(p['pct_menores'])} %, niñas, niños o adolescentes. <b>Llamada a la "
        f"acción:</b> priorizar {nombres5}, que explican el {es(k['pct_aumento_top5'])} % del aumento; extender "
        f"la atención a la noche y la madrugada, donde ocurre el {es(p['pct_noche_madrugada'])} % de los casos y "
        f"solo {C.COMISARIAS['permanentes']} de las comisarías de familia atienden las 24 horas "
        f"({C.COMISARIAS['cita']}), y medir la VIF como indicador de seguridad al mismo nivel que el hurto.", S_P))

    h.append(Paragraph("2. Datos y preparación", S_H))
    h.append(Paragraph(
        "Trabajamos con datos oficiales y públicos, y comprobamos que la limpieza no alterara ningún conteo. "
        "La fuente es el microdato «Seguimiento a delitos de alto impacto» de la Secretaría Distrital de "
        "Seguridad, Convivencia y Justicia [SDSCJ] (2026), publicado en su Observatorio de Seguridad, Convivencia y "
        f"Justicia, con denuncias registradas hasta {hasta}. El código descarga el archivo y registra su huella "
        "SHA-256; lo normaliza a formato <i>tidy</i> (etiquetas legibles, tipos, categorías ordenadas, 43 armas en "
        "9 grupos) y ejecuta siete validaciones de integridad, como la conservación exacta del total de casos. "
        "Todas las cifras del HTML y de este documento salen de un único archivo de indicadores calculado desde "
        "los datos.",
        S_P))

    h.append(Paragraph("3. De la exploración a la explicación", S_H))
    h.append(Paragraph(
        "Probamos nueve gráficos rápidos y conservamos solo los tres que cuentan la historia. Con Plotly Express "
        "se exploraron volúmenes apilados, series mensuales, sexo, ciclo vital, localidad, franja, arma y "
        "estacionalidad (las «ostras»). Siguiendo a Nussbaumer Knaflic (2015), no se muestra el proceso: se "
        "conservan tres «perlas» que forman un arco de tres actos: <b>planteamiento</b> (¿qué cambia?), "
        "<b>nudo</b> (¿dónde?) y <b>desenlace</b> (¿cuándo actuar?), y una <b>síntesis</b> final que reúne el cambio "
        "en una sola figura. Para no repetir el mensaje, cada acto tiene un único titular (el del gráfico) y un "
        "bloque breve con la evidencia y la decisión. La técnica Bing-Bang-Bongo se aplica así: el "
        "título activo y las cifras clave anuncian el mensaje (Bing), las trazas con contraste aportan la evidencia "
        "(Bang) y las anotaciones y la caja de llamada a la acción lo repiten (Bongo).", S_P))

    h.append(Paragraph("4. Decisiones de diseño", S_H))
    filas = [
        ["Decisión", "Justificación teórica"],
        ["Acto 1: líneas de un índice (2018–2022 = 100)",
         "La intención es tendencia; el índice pone en una escala común delitos de volúmenes muy distintos. "
         "La posición en escala común es el canal más preciso (Munzner, 2014)."],
        ["Acto 2: barras horizontales ordenadas, eje en cero",
         "Ranking legible sin girar etiquetas; la longitud solo es honesta si parte de cero (Few, 2012; Cairo, 2019)."],
        ["Acto 3: mapa de calor secuencial desde 0 con valores en celda",
         "Patrón localidad × franja; un solo matiz ordenado evita fronteras falsas del arcoíris y el número "
         "escrito da redundancia (Ware, 2013)."],
        ["Síntesis: tres paneles de mancuernas (promedio 2018–2022 → 2026) para qué, dónde y cuándo",
         "Misma gramática visual en los tres paneles: el cambio se lee por posición en escala común (Munzner, "
         "2014) y la línea une el antes con el después (conexión, Gestalt; Ware, 2013)."],
        ["Gris para el contexto, coral #D55E00 para la VIF",
         "Atributo preatentivo: el ojo halla el foco sin buscar (Nussbaumer Knaflic, 2015; Ware, 2013). Coral "
         "y gris son distinguibles con daltonismo (Okabe y Ito, 2008)."],
        ["Etiquetado directo, sin leyenda, sin fondo ni bordes, rejilla mínima",
         "Proximidad (Gestalt) y máxima proporción datos-tinta (Tufte, 2001)."],
        ["Mismas 5 localidades en coral en los Actos 2 y 3",
         "Semejanza (Gestalt): el color enlaza los actos y reduce la carga cognitiva (Ware, 2013)."],
        ["Títulos activos con el hallazgo y subtítulo con unidades y periodo",
         "La conclusión se lee antes que los datos (Nussbaumer Knaflic, 2015)."],
    ]
    t = Table([[Paragraph(a, S_TB if i == 0 else S_T), Paragraph(b, S_TB if i == 0 else S_T)]
               for i, (a, b) in enumerate(filas)], colWidths=[5.6 * cm, 11.4 * cm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#374151")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.3, colors.HexColor("#E5E7EB")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    h.append(t)

    h.append(Paragraph("5. Interactividad con propósito", S_H))
    h.append(Paragraph(
        "Cada control existe para resolver una duda concreta de la audiencia. Se siguió el mantra «visión general "
        "primero, zoom y filtro, detalles bajo demanda» (Shneiderman, 1996), y solo se añadió un control cuando "
        "aporta, porque toda interacción tiene un costo cognitivo (Munzner, 2014). En el Acto 1, el menú «Comparar con…» permite auditar la afirmación central "
        "contra cualquier otro delito; en el Acto 2, tres botones alternan aumento absoluto, volumen y variación "
        "porcentual. Ambos usan <i>method=\"update\"</i>: cambian a la vez trazas, título, anotaciones y rango del eje, "
        "para que el texto nunca contradiga lo que se ve. El Acto 3 y la síntesis solo usan <i>hover</i>, porque un control más no "
        "aportaría. Cada figura dibuja menos de 300 puntos y los controles solo alternan trazas ya cargadas, de modo "
        "que la respuesta está por debajo de 0,1 s (medido en Chromium: entre 25 y 45 ms por actualización). El HTML incrusta plotly.js: abre con doble clic, sin Python ni "
        "internet, y la barra de herramientas se depuró (sin logo, lazo ni selección).", S_P))

    h.append(Paragraph("6. Ética visual y honestidad narrativa", S_H))
    h.append(Paragraph(
        "La historia solo afirma lo que los datos sostienen y declara sus límites. "
        f"(a) <b>Comparación justa:</b> todos los años suman solo {ventana}, los meses disponibles en {ua}. "
        "(b) <b>Sin <i>cherry-picking</i>:</b> la base es el promedio 2018–2022 y no 2023, el mínimo de la serie y "
        "año de cambios en el registro; usarlo inflaría el crecimiento (Cairo, 2019). Por la misma razón, el "
        f"titular no depende de 2023: frente a 2022 el aumento es {es(f['cambio_pct_vs_2022'])} %. "
        f"(c) <b>Mes preliminar:</b> {mes_txt} llega solo al {es(alerta.get('proporcion', 0) * 100)} % "
        "del promedio reciente; se marca con punto hueco y se advierte que las cifras serían conservadoras. "
        "(d) <b>Denuncias no son ocurrencia:</b> parte del aumento puede deberse a más denuncia; se declara en el HTML. "
        "(e) <b>Conteos, no tasas:</b> sin población por localidad, cada localidad se compara consigo misma. "
        "(f) Se excluyen del índice los delitos con menos de 100 casos al año, y del ranking de localidades la "
        "categoría «Sin localización», cuyo salto se explica en nota. (g) Las afirmaciones de los títulos se verifican con pruebas automáticas "
        "en el código antes de exportar.", S_P))

    h.append(Paragraph("Referencias", S_H))
    refs = [
        "Cairo, A. (2019). <i>How charts lie: Getting smarter about visual information</i>. W. W. Norton &amp; Company.",
        "Few, S. (2012). <i>Show me the numbers: Designing tables and graphs to enlighten</i> (2.ª ed.). Analytics Press.",
        "Grandas Medina, S. (2025, 21 de diciembre). <i>Conoce los horarios de atención de las Comisarías de "
        "Familia en Bogotá durante el fin de año</i>. Portal Bogotá, Alcaldía Mayor de Bogotá. "
        f"{C.COMISARIAS['url']}",
        "Munzner, T. (2014). <i>Visualization analysis and design</i>. CRC Press.",
        "Nussbaumer Knaflic, C. (2015). <i>Storytelling with data: A data visualization guide for business "
        "professionals</i>. Wiley.",
        "Okabe, M., y Ito, K. (2008). <i>Color universal design (CUD): How to make figures and presentations that "
        "are friendly to colorblind people</i>. J*Fly. https://jfly.uni-koeln.de/color/",
        "Secretaría Distrital de Seguridad, Convivencia y Justicia. (2026). <i>Seguimiento a delitos de alto "
        "impacto</i> [Conjunto de datos]. Observatorio de Seguridad, Convivencia y Justicia de Bogotá. "
        "https://oaiee.scj.gov.co/DatosDescarga/SIEDCO.csv",
        "Shneiderman, B. (1996). The eyes have it: A task by data type taxonomy for information visualizations. "
        "En <i>Proceedings 1996 IEEE Symposium on Visual Languages</i> (pp. 336–343). IEEE. "
        "https://doi.org/10.1109/VL.1996.545307",
        "Tufte, E. R. (2001). <i>The visual display of quantitative information</i> (2.ª ed.). Graphics Press.",
        "Ware, C. (2013). <i>Information visualization: Perception for design</i> (3.ª ed.). Morgan Kaufmann.",
    ]
    h += [Paragraph(r, S_REF) for r in refs]

    def pie(canvas, doc):
        canvas.saveState()
        canvas.setFont(F, 7.5)
        canvas.setFillColor(GRIS)
        canvas.drawRightString(LETTER[0] - 2 * cm, 1.2 * cm, f"{doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(str(C.ARCHIVO_PDF), pagesize=LETTER, leftMargin=2.2 * cm, rightMargin=2.2 * cm,
                            topMargin=1.9 * cm, bottomMargin=1.9 * cm,
                            title="Justificación – Narrativa visual VIF Bogotá", author=C.INTEGRANTES_TEXTO)
    doc.build(h, onFirstPage=pie, onLaterPages=pie)
    return C.ARCHIVO_PDF


if __name__ == "__main__":
    ruta = construir()
    try:
        from pypdf import PdfReader  # opcional, solo para verificar
        n = len(PdfReader(str(ruta)).pages)
        print(f"✔ PDF: {ruta} ({n} páginas)")
        assert n <= 3, "El documento supera 3 páginas"
    except ImportError:
        print(f"✔ PDF: {ruta}")
