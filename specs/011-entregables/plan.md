# Plan 011 · Entregables y presentación

## Mapa de entregables

| § | Entregable | Archivo | Se arma con |
|---|---|---|---|
| §9.1 | Descripción ejecutiva | `01-descripcion-ejecutiva.md` | `docs/producto/vision.md` resumido a una página |
| §9.2 | Problema y usuarios | `02-problema-y-usuarios.md` | `vision.md` y `evidencia.md` |
| §9.3 | Solución | `03-solucion.md` | Visión, cuadrantes de la spec 008 y capturas del sitio |
| §9.4 | Inventario de fuentes | `04-inventario-fuentes.md` | Generado por `radar entregables` |
| §9.5 | Justificación de datos | `05-justificacion-datos.md` | Para cada fuente: qué hipótesis atiende y por qué no hay una alternativa mejor |
| §9.6 | Procesos de datos | `06-procesos-de-datos.md` | Resumen de los `plan.md` de 002 a 008, con un diagrama de flujo |
| §9.7 | Arquitectura | `07-arquitectura.md` | `docs/arquitectura.md` y el diagrama del dominio |
| §9.8 | Prototipo | `08-prototipo.md` | URL, recorrido sugerido y enlace al repositorio |
| §9.9 | Resultados | `09-resultados.md` | Tablas generadas, hallazgos y limitaciones |
| §9.10 | Presentación | `10-pitch.md` y la presentación | Guion por tiempos |
| §9.11 | Modelo de IA | `docs/ia-responsable.md` | Specs 006 y 007 |
| §7 | Mentoría | `mentoria.md` | Los siete elementos que pide la §7 |
| §8 | Preguntas | `preguntas-del-jurado.md` | — |
| §8 y §17 | Operación y continuidad | `modelo-de-operacion.md` | Specs 010 y 006 (costos) |

## Guion base del pitch (≈ 6 minutos)

| Tiempo | Bloque | Qué se dice o muestra | Punto de la §8 |
|---|---|---|---|
| 0:00–0:40 | Problema | El turista decide en TikTok y en asistentes; el observatorio lo confirma (redes 39.7 %); el estado no mide qué ve ahí | Problema |
| 0:40–1:20 | Evidencia | Concentración (capital 59.9 %), Pueblos Mágicos con capacidad disponible y medición hotelera con factor fijo | Evidencia |
| 1:20–3:20 | Demostración | Mapa de brecha → un destino `por_posicionar` → su ficha → qué responden los asistentes en coreano frente a español → fuentes que citan | Funcionamiento |
| 3:20–4:00 | Datos e IA | Siete fuentes, panel con consentimiento, auditoría de 440 corridas con Wilson y clasificador validado con κ | Datos, metodología y papel de la IA |
| 4:00–5:00 | Impacto | Escenario de derrama de los destinos bajo la mediana, beneficio para el visitante y para los prestadores, desconcentración | Beneficios e impacto |
| 5:00–5:45 | Tianguis y operación | Fichas para citas, medición antes y después, piloto de noviembre a marzo, costos y extensión | Viabilidad y escalamiento |
| 5:45–6:00 | Cierre | Una frase y el equipo | — |

## Preguntas probables del jurado (semilla)

1. ¿Es legal obtener datos de TikTok así?
2. ¿Un panel de conocidos es representativo?
3. ¿Los asistentes no cambian sus respuestas todo el tiempo?
4. ¿Cómo saben que la atención causa visitas?
5. ¿Qué gana el visitante?
6. ¿Cuánto cuesta operarlo y quién lo opera?
7. ¿Por qué la Secretaría lo usaría en lugar de su agencia de medios?
8. ¿Qué pasa con la privacidad de quien comenta?
9. ¿Qué tan confiable es el clasificador?
10. ¿Por qué estos 12 destinos y no atractivos?
11. ¿Qué harían con un destino en «atención sin estancia»?
12. ¿Cómo escala a otros estados?
13. ¿Por qué la afluencia oficial sería un problema?
14. ¿Qué pasa si cambia el modelo de un asistente?
15. ¿Quién es dueño del proyecto y cómo seguiría?

## Generación con código

`radar entregables` (P1) usa plantillas simples con `str.format` para escribir el inventario y las tablas de resultados. Ninguna cifra de esos archivos se edita a mano.
