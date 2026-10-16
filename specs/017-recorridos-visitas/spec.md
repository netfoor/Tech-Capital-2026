# Spec 017 · Recorridos y visitas

| | |
|---|---|
| Contexto | Durante y después de la visita: sesiones de recorrido consentidas, detección de paradas, confirmación de visitas, check-ins y diario |
| Prioridad | P0 |
| Estado | En curso |
| Depende de | 014 (modelo y API) |
| Habilita | 016 (PWA: pantallas de recorrido y diario), 019 (agregados de visitas confirmadas) |

## Bases que atiende

- §2 y §3 de la convocatoria: mejorar la experiencia **durante** (registro del recorrido, confirmación de lugares) y **después** de la visita (diario cronológico con tiempo observado y distancia estimada).
- §5: datos de primera parte con propósito específico, consentimiento por finalidad, minimización, retención breve de muestras crudas y borrado (derechos ARCO).
- §8: prototipo funcional y demostrable con trazas sintéticas etiquetadas.
- Contexto maestro §05 (Durante/Después), §07 (geolocalización, visitas y movilidad), §13.3 (endpoints P0), §14 (privacidad) y §18 (métricas del pipeline).
- Constitución XI (nadie es objeto de vigilancia) y XII (lo sintético se nota).

## Objetivo

Que una persona con cuenta pueda iniciar, pausar y detener un recorrido con consentimiento específico de ubicación; que el sistema detecte paradas y proponga visitas probables con su confianza; que la persona confirme, corrija o rechace cada una; que pueda hacer check-in sin GPS; y que vea su diario. Las muestras crudas nunca salen de la persona, no aparecen en registros y se purgan según la retención configurada.

## Historias de usuario

**H1 (P0).** Como visitante con cuenta, quiero iniciar un recorrido solo si di mi consentimiento de ubicación.
- Dado que no tengo un consentimiento vigente y otorgado de `ubicacion_sesion`, cuando pido `POST /sessions`, entonces recibo `403` con un mensaje que explica cómo otorgarlo.
- Dado un consentimiento vigente, cuando inicio, entonces la sesión guarda la versión del consentimiento.

**H2 (P0).** Como visitante, quiero pausar y detener la captura cuando quiera.
- Dado un recorrido en pausa, cuando la app envía muestras, entonces se rechazan con `409` y no se guarda nada.
- Dado que retiro el consentimiento, cuando la app envía muestras, entonces se rechazan con `403`.

**H3 (P0).** Como visitante, quiero que al detener el recorrido se me propongan los lugares donde me detuve.
- Dado un recorrido detenido, cuando pido `GET /sessions/{id}/visit-candidates`, entonces veo cada parada con su estado (`visita_probable`, `paso_cercano` o `desconocido`), su confianza, su duración observada y alternativas, sin coordenadas.
- Una parada cerca de un hotel no se presenta como hospedaje ni una parada en un restaurante como consumo.

**H4 (P0).** Como visitante, quiero confirmar, corregir o rechazar cada candidato.
- Dado un candidato, cuando lo confirmo, entonces queda una `ConfirmedVisit` con fuente `gps_confirmado`, precisión y confianza; si lo corrijo, con el lugar que elegí y fuente `manual`; si lo rechazo, no queda visita.

**H5 (P0).** Como visitante sin GPS, quiero registrar que estuve en un lugar.
- Dado `POST /checkins` con un `poi_id`, entonces queda un check-in sin ubicación.

**H6 (P0).** Como visitante, quiero ver mi diario.
- Dado `GET /me/diario`, entonces veo en orden cronológico mis visitas confirmadas, check-ins y recorridos con tiempo observado y distancia estimada.

**H7 (P0).** Como jurado, quiero ver el flujo completo con datos sintéticos claramente marcados.
- Dado `POST /sessions/demo`, entonces se crea un recorrido con `is_synthetic=true` cargado con una traza de `data/synthetic/` y procesado.

## Requisitos funcionales

- **FR-017-01** Endpoints `POST /sessions`, `GET /sessions`, `GET /sessions/{id}`, `POST /sessions/{id}/samples`, `POST /sessions/{id}/pause`, `POST /sessions/{id}/resume`, `POST /sessions/{id}/stop`, `GET /sessions/{id}/visit-candidates`, `POST /visits/confirm`, `POST /checkins`, `GET /me/diario` y `POST /sessions/demo`, documentados en `docs/api/contrato-p0.md`.
- **FR-017-02** Las sesiones y las muestras exigen un consentimiento vigente (`otorgado = true`, `revocado_en IS NULL`) de finalidad `ubicacion_sesion`. Cada muestra guarda la versión del consentimiento con que se tomó.
- **FR-017-03** Lote de muestras: de 1 a 500 por petición; `lat` ∈ [-90, 90], `lon` ∈ [-180, 180], `precision_m` ∈ [0, 10 000]; máximo 20 000 muestras por sesión (configurable). Las muestras con fecha futura, anteriores al inicio de la sesión o repetidas se descartan y se cuentan.
- **FR-017-04** Pipeline puro en `app/pipeline/visitas.py`: validación temporal y espacial → duplicados → saltos imposibles (velocidad > 2.5 m/s, configurable) → detección de paradas (radio y duración mínima configurables) → duración observada y huecos → asociación probabilística a POI (distancia, precisión, extensión del lugar y horario) → estado y confianza → resumen. Los parámetros son EXPERIMENTALES y se documentan en `docs/calibracion_gps.md`.
- **FR-017-05** Estados de candidato: `visita_probable`, `visita_confirmada`, `paso_cercano`, `desconocido`. Solo la persona convierte un candidato en `visita_confirmada`.
- **FR-017-06** Trazas sintéticas deterministas (`app/pipeline/trazas_sinteticas.py`, semilla fija) sobre POI reales del corredor Puebla–Cholula, con ruido gaussiano de 5–20 m, huecos, duplicados y saltos; cada fila con `is_synthetic=true` y una tabla de verdad aparte.
- **FR-017-07** Evaluación reproducible (`app/pipeline/evaluar.py`) que escribe `reports/eval_visitas.md`: precisión de asociación a POI, error de permanencia y tasa de indeterminadas, con n y sensibilidad a los parámetros.
- **FR-017-08** Retención: `app/privacy/retencion.py` purga las muestras crudas más viejas que la retención (la menor entre `RETENCION_MUESTRAS_DIAS` y la preferencia de la persona). Comando `uv run python -m app.privacy.retencion`.

## Requisitos no funcionales

- Ninguna respuesta de estos endpoints devuelve muestras crudas ni coordenadas; solo `GET /me/export` las devuelve, y solo a su dueña (constitución XI). Hay una prueba explícita.
- Autorización horizontal: la sesión, los candidatos y las visitas de otra persona responden `404`.
- Los registros no contienen coordenadas (§14); el pipeline no registra posiciones.
- `DELETE /me` borra sesiones, muestras, candidatos, visitas y check-ins (prueba).
- Pruebas sin servicios externos; la traza de prueba se genera en memoria con la misma función.

## Fuera de alcance

- Captura en segundo plano (limitación real de las PWA) y la interfaz de la PWA (spec 016).
- Agregación protegida de visitas para el tablero (spec 019).
- Publicación de visitas con difuminado territorial (capa social, P1).
- Calibración con una traza real del equipo en el corredor: queda pendiente en `docs/calibracion_gps.md`.

## Preguntas abiertas

- 2026-10-16. §07 menciona confirmar, corregir o rechazar, pero §13.3 no trae un endpoint para reanudar. Se agrega `POST /sessions/{id}/resume`; sin él, una pausa sería un fin.
- 2026-10-16. Una persona tiene a lo más un recorrido `activa` o `pausada`. Iniciar otro responde `409` con el id del que sigue abierto.
- 2026-10-16. Corregir un candidato crea la visita con `fuente_evidencia = manual` (el lugar lo eligió la persona, no el GPS) y `confianza` igual a la probabilidad que el pipeline le daba a ese lugar (0 si no estaba entre las alternativas).
- 2026-10-16. Un check-in no crea `ConfirmedVisit`: el diario muestra visitas confirmadas y check-ins como entradas distintas para no contarlas dos veces.
- 2026-10-16. El horario se evalúa en hora del centro de México con desfase fijo UTC−6 (sin horario de verano desde 2022). Solo se interpreta el subconjunto de `opening_hours` de OSM que aparece en el catálogo (`24/7`, días `Mo-Su` y rangos `HH:MM-HH:MM`, también los que cruzan medianoche); lo demás cuenta como horario desconocido.
- 2026-10-16. `paso_cercano` se limita a categorías de interés turístico (museo, templo, zona arqueológica, parque, sitio histórico, mirador, mercado, centro cultural, artesanías) para no pedir confirmación por cada comercio junto a la banqueta.
