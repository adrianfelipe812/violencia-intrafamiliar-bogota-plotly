# Bitácora de decisiones y correspondencia con la rúbrica (nivel Estratégico, 4,6–5,0)

## Criterio 1 · Principios de diseño y ética visual
| Descriptor del nivel Estratégico | Evidencia en el proyecto |
|---|---|
| Elimina todo el caos (máxima proporción datos-tinta) | `plot_bgcolor="white"`, sin bordes ni leyendas, rejilla `#F1F5F9` solo en el eje de valores, barra de herramientas depurada (`visual.CONFIG_PLOTLY`). |
| Atributos preatentivos de manera magistral | Coral `#D55E00` solo para el protagonista; gris pizarra para el contraste (hurto); gris claro y fino para el contexto. Grosor 4,5 / 2,5 / 1,4 px. Las mismas 5 localidades conservan el coral en los Actos 2 y 3. |
| Gestalt | Proximidad (etiquetas al final de la línea), región común (banda de pandemia), semejanza (color constante entre actos), cierre (caja de llamada a la acción). |
| Reglas éticas (base cero en barras) | `_rango()` en `visual.py` fuerza que todo eje de barras incluya el 0; mapa de calor con `zmin=0`; índice con línea de referencia en 100. |
| Sin distorsiones ni cherry-picking | Ventana enero–septiembre para todos los años; base 2018–2022 (no 2023); último mes marcado como preliminar; exclusión documentada de delitos con < 100 casos/año y de «Sin localización». |
| Justifica con citas APA 7 | `docs/Documento_justificacion_APA7.pdf`: cada decisión con su cita; 9 referencias, todas citadas en el texto y viceversa. |

## Criterio 2 · Implementación técnica e interactividad en Plotly
| Descriptor | Evidencia |
|---|---|
| Plotly con dominio técnico (Express o Graph Objects) | Exploración con Plotly Express (cuaderno 02); producto final con Graph Objects, `updatemenus`, `customdata` + `hovertemplate`, `separators=",."`, ejes fijos. |
| Interactividad justificada | Acto 1: menú *Comparar con…* para auditar la afirmación. Acto 2: botones de métrica. Acto 3: solo hover. Cada control usa `method="update"` y reescribe título y anotaciones (sin disonancia, Sesión 5). |
| Funciona fluidamente (< 0,1 s) | < 300 puntos por figura; los controles solo alternan trazas ya cargadas. Medición con `Plotly.update` en Chromium: entre 25 y 45 ms por actualización en dos mediciones (menú del Acto 1 y botones del Acto 2). |
| HTML totalmente autónomo | `include_plotlyjs=True` una sola vez; sin CDN ni archivos locales (verificado en el cuaderno 03). |
| Código limpio | Módulos con una responsabilidad cada uno, docstrings, configuración centralizada, validaciones que detienen el flujo si algo falla. |

## Criterio 3 · Contexto y estructura narrativa
| Descriptor | Evidencia |
|---|---|
| Audiencia, conflicto y llamada a la acción impecables | Encabezado del HTML (audiencia explícita), conflicto hurto vs. VIF, caja final con tres acciones concretas y medibles. |
| Bing-Bang-Bongo en el HTML | Bing = título + 4 cifras clave; Bang = tres actos con contraste preatentivo; Bongo = figura de síntesis con conclusiones + caja de llamada a la acción. |
| Guía al usuario sin esfuerzo | Cada acto tiene una etiqueta, un título-pregunta, un párrafo de lectura y una instrucción breve de uso de los controles. |

## Decisiones analíticas registradas
1. **Delito foco:** violencia intrafamiliar, por ser el mayor aumento absoluto sobre su línea base (+61 %; +67 % frente a 2022), verificado con `assert`. La racha de tres años (2023 → 2026) no se usa en el titular porque arranca en 2023, año con cambios de registro.
2. **Ventana comparable:** meses 1..último mes del último año (regla del Observatorio).
3. **Línea base:** promedio 2018–2022. Alternativa descartada: 2023 (mínimo; anomalías de registro: alto «no reportado», proporción atípica de hombres).
4. **Último mes:** se compara con el promedio de los tres meses previos; si está por debajo del 85 %, se marca como preliminar.
5. **Sin tasas por población:** la fuente no trae población; se evita mezclar fuentes sin documentar y se compara cada localidad consigo misma.
6. **Agrupación de armas:** 43 → 9 grupos, conservando la categoría original en `arma_original`.
7. **Oferta institucional nocturna:** afirmación sustentada con el horario habitual de las comisarías de familia publicado por el Portal Bogotá (Grandas Medina, 2025): 23 cierran a las 4:00 p. m., 5 a las 11:00 p. m. y 2 atienden 24 horas.
8. **Redundancia:** cada acto tiene un único titular (el del gráfico) y un bloque breve de evidencia y decisión; se eliminaron los párrafos que repetían el mensaje.
9. **Síntesis:** figura final de mancuernas (promedio 2018–2022 → 2026) que generaliza qué, dónde y cuándo cambió, con conclusiones por panel. Reveló un matiz que el Acto 3 por sí solo no mostraba: la madrugada sigue siendo la franja con más casos, pero el crecimiento se dio en la tarde y la noche.
