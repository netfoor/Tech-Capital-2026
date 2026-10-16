# Evidencia de análisis y resultados

| Resultado | Dónde |
|---|---|
| Concentración de la demanda, desajuste oferta–demanda y brecha de accesibilidad | [`reports/01_problema.md`](../../reports/01_problema.md) y [`reports/figuras/`](../../reports/figuras/) |
| Calidad e integración de datos | [`reports/calidad_datos.md`](../../reports/calidad_datos.md) |
| Recomendador contra líneas base, ablaciones y planes de varios días | [`reports/eval_recomendador.md`](../../reports/eval_recomendador.md) |

## Lo que no funcionó o no alcanzó

- Con tan poca información de accesibilidad, la mayoría de las rutas con «sin escalones» quedan muy cortas o vacías. El motor no relaja la restricción: lo reporta.
- Con el catálogo real, las líneas base cubren más destinos alternativos que el motor, porque arman más paradas sin filtrar.
- Los pesos del ranking no están calibrados con usuarios reales.
- Panorama y Experiencia del tablero solo tienen datos sintéticos, y el recorrido con GPS sigue en desarrollo.
- La concentración (HHI) bajó entre 2021 y 2025, pero parte del cambio puede deberse a qué hoteles mide cada centro. Falta confirmarlo con la Secretaría.
