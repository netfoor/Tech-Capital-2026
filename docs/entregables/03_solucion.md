# Descripción de la solución

## Para el visitante (PWA, `/`)

| Fase | Funcionalidad | Estado |
|---|---|---|
| Antes | Descubrir en lista (vista principal accesible) o en mapa; filtros por interés, destino, costo, «sin escalones», «baño accesible» y «solo verificados» | Implementado |
| Antes | Ficha con nueve atributos de accesibilidad: valor, estado, origen y fecha; sin dato = «Sin verificar» | Implementado |
| Antes | Guardar en mi mapa sin cuenta, con etiquetas y nota privada | Implementado |
| Antes | Planear desde cero o desde mis guardados (varios días), con explicación, advertencias, datos desconocidos y alternativas | Implementado |
| Durante | Recorrido consentido con GPS y check-in | En desarrollo (spec 017) |
| Después | Reseña en ocho dimensiones y reporte de barrera con foto sin EXIF | Implementado |

## Para la Secretaría (tablero, `/admin`)

| Módulo | Datos | Estado |
|---|---|---|
| Oferta–demanda | Serie oficial del Observatorio: concentración (HHI), ocupación, cuartos libres y destinos alternativos | Real |
| Inclusión | Cobertura de información de accesibilidad por destino y atributo; barreras y prioridades | Real |
| Panorama y Experiencia | Visitas, permanencia y satisfacción, con supresión k | Sintético etiquetado |
| Moderación | Aceptar o rechazar reportes; la ficha cambia y queda auditado | Real |

Cada gráfico tiene su ficha metodológica (fórmula, denominador, fuente y limitación) y una tabla de datos alternativa. Las fichas viven en [`backend/metrics/definitions.yaml`](../../backend/metrics/definitions.yaml).

## Privacidad

Los datos personales viven en un esquema aparte (`private`) que nunca sale en respuestas públicas. Los agregados tienen umbral k, la ubicación solo se registra en sesiones consentidas y existen los derechos de acceso y borrado (`GET /me/export`, `DELETE /me`). Cada regla tiene pruebas automáticas.
