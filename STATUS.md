# Estado del proyecto

Última actualización: 2026-10-17. Se separan siempre **producto objetivo**, **MVP implementado**, **demo sintética** y **resultado medido**.

## En producción

https://puebla-viva-360.vercel.app ([`docs/despliegue.md`](docs/despliegue.md)).

## Hecho (MVP implementado)

| Spec | Qué | PR |
|---|---|---|
| Fundación | ADR-0010, backend, frontend, PostGIS, CI y documentos | #1 |
| 012 | Catálogo real: 1,991 lugares (OSM, SIC, DENUE) y 46,491 establecimientos del DENUE | #4 |
| 013 | Análisis del problema reproducible, con figuras | #7 |
| 014 | Modelo de datos (32 entidades), API P0, cuentas con roles, reportes, moderación y privacidad | #3, #9 |
| 015 | Recomendador inclusivo con líneas base, evaluación y ficha del modelo | #5 |
| 016 | PWA del visitante: descubrir, ficha, guardar, planear, reportar y reseñar | #8 |
| 019 | Tablero: Oferta–demanda e Inclusión con datos reales; Panorama y Experiencia sintéticos etiquetados; moderación | #10, #11 |
| 023 | Presentación con QR, guiones, preguntas del jurado y entregables | este PR |
| Despliegue | Vercel con Neon (ADR-0011) | #6 |

## Demo sintética

- Panorama y Experiencia del tablero usan visitantes, visitas y reseñas sintéticos (`app.services.demo_tablero`), siempre con la etiqueta visible.
- La evaluación del recomendador usa perfiles de solicitud sintéticos sobre el catálogo real.

## Pendiente

- **017, recorridos y visitas con GPS:** en desarrollo, sin mergear.
- **020, accesibilidad y seguridad:** falta la prueba manual con lector de pantalla y la auditoría formal. Las pruebas automáticas con axe de la PWA ya pasan.
- **021 (MCP) y 022 (importar enlaces, compartir, intención → visita):** P1, no empezadas.
- **Datos de accesibilidad:** falta la auditoría presencial de 8 a 15 lugares.

## Para decidir con el equipo

- **Módulos del Radar en `pipelines/`** (`senales`, `asistentes`, `radar`): la app no los usa. Propuesta: reutilizar la auditoría de asistentes como módulo P1 del tablero, o retirarlos.
- **Contactos de negocios en los extractos de OSM** (`data/fuentes/corredor/osm/`): 191 teléfonos y correos de establecimientos. Son públicos (ODbL), pero conviene filtrarlos.
- **CI de GitHub:** el dueño del repositorio debe habilitar Actions.
- **Licencia del código.**
