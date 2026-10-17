# Validación manual de la detección de menciones (T006-11)

Fecha: 17 de octubre de 2026. Muestra: 60 respuestas de asistentes, 12 por idioma (es, en, fr, ko, zh), elegidas al azar con semilla fija (`radar asistentes muestra-menciones`). El equipo revisó cada respuesta y anotó los destinos detectados de más (`sobran`) y los que faltaron (`faltan`). Las respuestas completas están en `data/privado/asistentes/validacion_menciones.csv`; no se versionan porque contienen el texto íntegro de las respuestas.

## Criterio

Se valida si el destino aparece **como recomendación**, no solo si su nombre aparece en el texto:

| # | Decisión | Efecto | Filas |
|---|---|---|---|
| 1 | Ciudad de Puebla solo como salida, regreso o referencia de distancia no es recomendación. Si es base de hospedaje real o destino principal, se conserva | `sobran`, con nota | 20 filas |
| 2 | Destino citado solo como saturado o a evitar | `sobran` | 9, 13, 30 |
| 3 | Referencia de ruta o ubicación («vía Teziutlán», «cerca de Pahuatlán») | `sobran` | 13, 14 |
| 4 | Atractivo sin nombrar su municipio (Honey, probablemente Huauchinango) | solo nota; no va a `faltan` | 14 |
| 5 | Tehuacán detectado solo por «Reserva Tehuacán-Cuicatlán» | `sobran` | 17, 25, 29, 42, 44, 49 |
| 6 | Mención solo en una oferta futura o circuito alterno (Tepeaca) | `sobran`; una mención breve dentro de una lista se conserva | 25; conservadas 4, 20, 31, 50, 55, 56 |
| 7 | Ciudad de Puebla como destino principal y no detectada | `faltan` | 3, 5, 6, 11, 19, 28, 34, 35, 36 |
| 8 | Destino detectado que no aparece en el texto | `sobran` | 23 (Tlatlauquitepec), 40 (Atlixco) |
| 9 | Destinos fuera del catálogo, menciones breves y atractivos dentro de un destino | solo notas; los enlaces son fuentes, no destinos | todas |

## Resultado

| Alcance | Detecciones correctas | Sobran | Faltan | Precisión | Exhaustividad |
|---|---|---|---|---|---|
| Todos los destinos | 247 | 38 | 9 | 0.87 | 0.97 |
| Sin la Ciudad de Puebla (referencia, no entra al radar) | 220 | 18 | 0 | 0.92 | 1.00 |

Cifras en `data/curado/validacion_menciones.json` (`radar asistentes validar-menciones`).

## Lo que encontramos

- **Sesgo con la capital.** El detector cuenta a la Ciudad de Puebla cuando solo es el punto de salida (20 casos) y la pierde cuando es el destino principal de los prompts de fin de semana (9 casos). No afecta el índice del radar, porque la capital es referencia, pero sí su visibilidad publicada.
- **Tehuacán sobrecontado** por la Reserva de la Biosfera Tehuacán-Cuicatlán (6 casos).
- **Una lista de nombres no distingue recomendar de mencionar**: destinos saturados, «a evitar» o usados como referencia de ruta se cuentan como menciones.
- **Fuera del catálogo** aparecen con frecuencia Africam Safari, Santa María Tonantzintla, Cantona y Huaquechula.

Tareas que salen de aquí: T006-16 (capital como origen), T006-17 (Tehuacán-Cuicatlán), T006-18 (recomendación frente a mención) y T001-08 (ampliar el catálogo).
