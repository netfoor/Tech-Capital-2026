# Reporte de calidad de datos · Catálogo del corredor

Generado por `uv run radar corredor reporte` desde los extractos de `data/fuentes/corredor/` (spec 012). No se edita a mano.

Fecha de consulta de los extractos: OSM: 2026-10-16; SIC: 2026-10-16; DENUE: 2026-10-16.

## Conteos por fuente

| Fuente | Registros leídos | En el catálogo como POI propio | Enlazados a otro POI |
|---|---|---|---|
| OSM (Overpass) | 1672 | 1376 | — |
| SIC (Secretaría de Cultura), Puebla | 309 | 120 | 20 |
| DENUE (INEGI), zonas de consulta | 9827 | 495 | 357 |

- Elementos de OSM sin categoría del contrato o sin nombre: 230 (incluye 18 bancas, que no entran como POI).
- Elementos de OSM fuera de las zonas o de los municipios del corredor: 25.
- Descartados por coordenadas ausentes o fuera del estado: 1 (SIC sin coordenadas válidas: 0).
- Oferta DENUE estatal (SCIAN 7211, 7225, 7121, 5615): 46,491 establecimientos en 216 municipios.

## POI por categoría y zona

| Categoría | Atlixco | Chignahuapan | Cuetzalan | Huauchinango | Huejotzingo | Pahuatlán | Tetela de Ocampo | Teziutlán | Tlatlauquitepec | Xicotepec | Zacatlán | corredor | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| alojamiento | 47 | 43 | 41 | 27 | 9 | 11 | 8 | 19 | 17 | 18 | 74 | 322 | 636 |
| artesanias | 3 | 6 | 1 | 1 | 1 | 7 | 0 | 1 | 1 | 0 | 2 | 120 | 143 |
| banio | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 13 | 15 |
| cafe | 4 | 2 | 3 | 0 | 1 | 0 | 2 | 3 | 1 | 0 | 13 | 116 | 145 |
| centro_cultural | 2 | 0 | 1 | 1 | 1 | 0 | 2 | 3 | 1 | 1 | 2 | 68 | 82 |
| mercado | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 1 | 1 | 14 | 21 |
| mirador | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 |
| museo | 2 | 3 | 3 | 2 | 2 | 0 | 4 | 0 | 1 | 1 | 9 | 74 | 101 |
| otro | 3 | 0 | 5 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 8 | 18 | 36 |
| parque | 5 | 2 | 2 | 7 | 0 | 1 | 1 | 4 | 3 | 7 | 4 | 86 | 122 |
| restaurante | 7 | 0 | 5 | 2 | 0 | 0 | 0 | 4 | 2 | 0 | 48 | 477 | 545 |
| sitio_historico | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 1 | 27 | 30 |
| templo | 7 | 2 | 3 | 2 | 4 | 1 | 0 | 2 | 2 | 1 | 2 | 81 | 107 |
| zona_arqueologica | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 7 |
| Total | 80 | 60 | 64 | 43 | 20 | 21 | 17 | 39 | 28 | 31 | 164 | 1424 | 1991 |

## Nulos en `poi.csv`

| Columna | Vacíos | % |
|---|---|---|
| poi_id | 0 | 0.0 % |
| nombre | 0 | 0.0 % |
| categoria | 0 | 0.0 % |
| subcategoria | 0 | 0.0 % |
| destino_id | 0 | 0.0 % |
| corredor_id | 567 | 28.5 % |
| municipio_cvegeo | 0 | 0.0 % |
| lat | 0 | 0.0 % |
| lon | 0 | 0.0 % |
| direccion | 736 | 37.0 % |
| horario_osm | 1835 | 92.2 % |
| costo_rango | 0 | 0.0 % |
| descripcion | 1944 | 97.6 % |
| fuentes | 0 | 0.0 % |
| osm_id | 615 | 30.9 % |
| denue_id | 1139 | 57.2 % |
| sic_id | 1851 | 93.0 % |
| match_score | 1626 | 81.7 % |
| is_synthetic | 0 | 0.0 % |

## Duplicados

- `poi_id` repetidos: 0.
- Elementos de OSM fundidos (mismo nombre y categoría a menos de 30 m): 40.
- Recintos del SIC repetidos entre tablas: 0.
- Filas de accesibilidad repetidas (`poi_id`, `atributo`): 0.
- Posibles duplicados entre fuentes por revisar (nombre con similitud ≥ 0.90, entre 75 y 300 m): 12. No se funden en automático; la lista sale de `integrar.posibles_duplicados`.

## Enlaces entre fuentes

Regla: nombre difuso con puntaje ≥ 0.80 y distancia < 75 m, entre categorías compatibles; cada POI recibe a lo más un registro de cada fuente.

- POI con al menos un enlace: 365 de 1,991 (18.3 %).
- SIC con OSM: 20 de 140 recintos del SIC en las zonas.
- DENUE con POI: alojamiento 97; alimentos 237; museos y sitios históricos 23.
- Puntaje de enlace: mínimo 0.80, mediana 1.00.

## Cobertura de información de accesibilidad

Proporción de POI con al menos un atributo de accesibilidad declarado en OSM. Mide cuánto se sabe, no qué tan accesibles son los lugares: un POI sin dato queda «sin verificar».

| Zona | POI | Con algún atributo | Cobertura de información | Con dato de acceso sin escalones | % acceso |
|---|---|---|---|---|---|
| Corredor Puebla–Cholula | 1424 | 42 | 2.9 % | 40 | 2.8 % |
| Atlixco | 80 | 1 | 1.2 % | 1 | 1.2 % |
| Chignahuapan | 60 | 0 | 0.0 % | 0 | 0.0 % |
| Cuetzalan | 64 | 0 | 0.0 % | 0 | 0.0 % |
| Huauchinango | 43 | 0 | 0.0 % | 0 | 0.0 % |
| Huejotzingo | 20 | 0 | 0.0 % | 0 | 0.0 % |
| Pahuatlán | 21 | 0 | 0.0 % | 0 | 0.0 % |
| Tetela de Ocampo | 17 | 0 | 0.0 % | 0 | 0.0 % |
| Teziutlán | 39 | 0 | 0.0 % | 0 | 0.0 % |
| Tlatlauquitepec | 28 | 0 | 0.0 % | 0 | 0.0 % |
| Xicotepec | 31 | 0 | 0.0 % | 0 | 0.0 % |
| Zacatlán | 164 | 0 | 0.0 % | 0 | 0.0 % |
| Total | 1991 | 43 | 2.2 % | 41 | 2.1 % |

- Valores de acceso sin escalones: no: 5, parcial: 7, si: 29.
- Filas por atributo: acceso_sin_escalones: 41, banio_accesible: 1, superficie: 1.
- Sanitarios públicos con dato de baño accesible: 1 de 15 (6.7 %).

## Limitaciones

- OSM depende de quién mapea: la ausencia de un lugar o de una etiqueta no prueba que no exista.
- Las coordenadas del SIC y del DENUE pueden estar desplazadas; lo no enlazado entra como POI propio y puede duplicar un lugar de OSM con otro nombre.
- Los límites municipales están simplificados al 4 %: un punto cerca de un límite puede quedar en el municipio vecino.
- Las etiquetas de accesibilidad de OSM no están verificadas por el equipo (`estado=sin_verificar`, `confianza=0.6`).

Datos © OpenStreetMap contributors (ODbL 1.0). Directorios del Sistema de Información Cultural/Secretaría de Cultura. DENUE, INEGI.
