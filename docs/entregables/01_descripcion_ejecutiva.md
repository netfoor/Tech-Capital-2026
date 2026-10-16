# Descripción ejecutiva

**Puebla Viva 360** es una plataforma de experiencias turísticas inclusivas para el visitante y de inteligencia territorial para la Secretaría de Desarrollo Turístico de Puebla.

**Problema.** La visita se concentra en la capital y Cholula, mientras los Pueblos Mágicos con oferta cultural tienen ocupación por debajo del promedio estatal. Casi ningún lugar turístico publica información de accesibilidad: quien tiene una necesidad de movilidad, viaja con personas mayores o con poco presupuesto planea a ciegas. Cifras en [`reports/01_problema.md`](../../reports/01_problema.md).

**Solución.** Una PWA que arma rutas que respetan restricciones (sin escalones, baño accesible, descansos, presupuesto) y explica por qué recomienda cada lugar y qué no sabe. Un tablero que muestra a la Secretaría la concentración de la demanda, los destinos alternativos con capacidad libre y la brecha de información de accesibilidad. Un reporte de barrera moderado cambia la ficha, llega al tablero y mejora la siguiente ruta.

**Datos.** INEGI (DENUE, Marco Geoestadístico), Secretaría de Cultura (SIC), OpenStreetMap y el Observatorio Turístico, integrados y trazables con SHA-256.

**IA.** Un recomendador de cuatro etapas (elegibilidad dura, ranking multiobjetivo, secuenciación con horarios y explicación) evaluado contra líneas base de popularidad y cercanía ([`reports/eval_recomendador.md`](../../reports/eval_recomendador.md)).

**Siguiente paso.** Piloto en el corredor Puebla–Cholula y los Pueblos Mágicos rumbo al Tianguis Turístico 2027.

Prototipo: https://puebla-viva-360.vercel.app
