# Spec 011 · Entregables y presentación

| | |
|---|---|
| Contexto | Entregables |
| Prioridad | P0 |
| Estado | Pendiente (estructura creada en `docs/entregables/`) |
| Depende de | 008 y 009 para resultados y demostración; el resto puede avanzar desde ya |
| Habilita | La evaluación final |

## Bases que atiende

ENT-01 a ENT-11 (§9), MEN-01 (§7), FIN-02 a FIN-12 (§8), RUB-01, RUB-05, RUB-06 y RUB-08, PI-01 y PI-02 (§14 y §15) y CON-01 (§17).

## Objetivo

Que cada entregable de la convocatoria exista, esté completo, sea consistente con los datos del repositorio y se pueda presentar en el tiempo disponible, con respuestas preparadas para el jurado.

## Historias de usuario

**H1 (P0).** Como jurado, quiero encontrar cada entregable de la §9 sin buscar.
- Dado `docs/entregables/README.md`, cuando lo abro, entonces cada entregable tiene su archivo, su estado y la sección de la convocatoria que atiende.

**H2 (P0).** Como jurado, quiero que las cifras del pitch coincidan con las del sitio.
- Dado el pitch, cuando comparo sus cifras con `data/curado/`, entonces coinciden. Las tablas de resultados e inventario se generan con código (`radar entregables`), no a mano.

**H3 (P0).** Como equipo, quiero un guion que quepa en el tiempo.
- Dado `10-pitch.md`, cuando se ensaya, entonces dura entre 5 y 7 minutos. Si el comité confirma otra duración, se ajusta. El guion cubre los ocho puntos de la §8 y tiene una demostración de respaldo.

**H4 (P0).** Como equipo, quiero respuestas preparadas a las preguntas difíciles.
- Dado `preguntas-del-jurado.md`, cuando se revisa, entonces hay al menos 15 preguntas con respuesta breve y su evidencia: privacidad, legalidad de TikTok, representatividad del panel, variabilidad de los asistentes, causalidad, costos, escalamiento, qué gana el visitante y por qué no es solo un tablero.

**H5 (P0).** Como Secretaría, quiero saber cómo se operaría el radar después del hackathon.
- Dado `modelo-de-operacion.md`, cuando lo leo, entonces encuentro el ciclo mensual, los roles, los costos con fuente, el piloto de noviembre de 2026 a marzo de 2027 con su forma de medir el efecto y la extensión a otros destinos.

## Requisitos funcionales

- **FR-011-01** Archivos de `docs/entregables/`:
  - `01` a `09`, y `10-pitch.md`;
  - `mentoria.md`;
  - `preguntas-del-jurado.md`;
  - `modelo-de-operacion.md`;
  - el entregable 11 remite a `docs/ia-responsable.md`.
- **FR-011-02** `radar entregables` (P1) genera:
  - `04-inventario-fuentes.md`, desde `data/fuentes/fuentes.csv` más las tablas curadas, con los siete campos de la §5: qué, por qué, de dónde, cómo, calidad, preparación y evidencia;
  - las tablas de `09-resultados.md`, desde `data/curado/`.
- **FR-011-03** Presentación ejecutiva de 10 a 12 diapositivas, con diseño sobrio (fondo claro y títulos en negritas, sin tarjetas ni etiquetas en mayúsculas) y las cifras tomadas de los archivos generados.
- **FR-011-04** Demostración de respaldo: capturas o video corto del recorrido del sitio y el sitio servido sin conexión (T009-13).
- **FR-011-05** Revisión del tutor sobre la metodología, registrada en `docs/decisiones/` si cambia algo.

## Fuera de alcance

- Registro formal de derechos de autor (§15): se menciona como siguiente paso.

## Preguntas abiertas

- Duración exacta del pitch y día de presentación: se confirman con el comité y se registran aquí.
