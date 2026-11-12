# Diccionario de datos — `delitos_alto_impacto_normalizado.csv.gz`

Periodo: 2018-01-01 a 2026-09-01 · Filas: 376.185 · Casos: 1.934.083

Datos actualizados por la fuente hasta: 30/09/2026 (consulta del 17/10/2026).

| Variable | Tipo | Descripción |
|---|---|---|
| `fecha` | fecha | Primer día del mes del registro (derivada de año y mes). |
| `anio` | entero | Año del hecho. |
| `mes` | entero | Mes del hecho (1–12). |
| `delito` | texto | Delito de alto impacto (12 categorías, etiquetas legibles). |
| `cod_localidad` | entero | Código oficial de localidad (1–20; 99 = sin localización). |
| `localidad` | texto | Nombre de la localidad de Bogotá. |
| `sexo` | texto | Sexo de la víctima: Mujer, Hombre, No reportado. |
| `ciclo_vital` | categoría ordenada | Infancia, Adolescencia, Adultez, Vejez, No reportado. |
| `franja_dia` | categoría ordenada | Madrugada, Mañana, Tarde, Noche. |
| `arma_grupo` | texto | Agrupación analítica de las 43 armas originales en 9 grupos. |
| `arma_original` | texto | Arma o medio tal como viene en la fuente. |
| `casos` | entero | Número de casos (denuncias) en la combinación de la fila. |

## Grupos de arma

| Arma original | Grupo |
|---|---|
| ARMA BLANCA / CORTOPUNZANTE | Arma blanca / cortopunzante |
| ARMA DE FUEGO | Arma de fuego |
| ARMA TRAUMATICA | Arma de fuego |
| CONTUNDENTES | Contundentes |
| LLAVE MAESTRA | Herramientas (llave maestra, palancas) |
| PALANCAS | Herramientas (llave maestra, palancas) |
| CARTA EXTORSIVA | Medios telefónicos / digitales |
| LLAMADA TELEFONICA | Medios telefónicos / digitales |
| REDES SOCIALES | Medios telefónicos / digitales |
| NO REPORTADO | No reportado / por establecer |
| POR ESTABLECER | No reportado / por establecer |
| ALMOHADA | Otros medios |
| ARTEFACTO EXPLOSIVO / CARGA DINAMITA | Otros medios |
| ARTEFACTO INCENDIARIO | Otros medios |
| BOLSA PLASTICA | Otros medios |
| CARRO BOMBA | Otros medios |
| CINTAS / CINTURON | Otros medios |
| CUERDA/SOGA/CADENA | Otros medios |
| DIRECTA | Otros medios |
| ESPOSAS | Otros medios |
| GRANADA DE MANO | Otros medios |
| JERINGA | Otros medios |
| MINA ANTIPERSONA | Otros medios |
| MIXTA | Otros medios |
| MOTO | Otros medios |
| OLLABOMBA | Otros medios |
| PAPA EXPLOSIVA | Otros medios |
| PAQUETE BOMBA | Otros medios |
| PERRO | Otros medios |
| POLVORA (FUEGOS PIROTECNICOS) | Otros medios |
| PRENDAS DE VESTIR | Otros medios |
| VEHICULO | Otros medios |
| SIN EMPLEO DE ARMAS | Sin empleo de armas |
| ACIDO | Sustancias (escopolamina, químicos) |
| AGUA CALIENTE | Sustancias (escopolamina, químicos) |
| ALIMENTOS VENCIDOS | Sustancias (escopolamina, químicos) |
| ALUCINOGENOS | Sustancias (escopolamina, químicos) |
| COMBUSTIBLE | Sustancias (escopolamina, químicos) |
| ESCOPOLAMINA | Sustancias (escopolamina, químicos) |
| GASES | Sustancias (escopolamina, químicos) |
| MEDICAMENTOS | Sustancias (escopolamina, químicos) |
| QUIMICOS | Sustancias (escopolamina, químicos) |
| SUSTANCIAS TOXICAS | Sustancias (escopolamina, químicos) |

> Nota: los registros son **denuncias** (casos conocidos por la Policía), no la ocurrencia real de los delitos.