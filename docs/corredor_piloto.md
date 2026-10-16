# Corredor piloto

**Decisión:** el corredor piloto es «Centro Histórico de Puebla → San Pedro y San Andrés Cholula» (`corredor_id = puebla-cholula`), con una capa de los 12 Pueblos Mágicos como destinos alternativos de escala estatal. Es la propuesta por defecto de §08.6; aquí se confirma con datos.

## Criterios (§08.6)

1. **Relevancia para el problema.** El corredor reúne los dos polos que concentran la demanda hotelera del estado (Ciudad de Puebla y Cholula). Es donde el contraste «polo saturado contra alternativa» se ve mejor: los Pueblos Mágicos de la sierra tienen oferta cultural, pero muchos menos visitantes y menor ocupación hotelera (tabla de abajo).
2. **Disponibilidad de datos.** Es la zona con más POI documentados en las tres fuentes abiertas (OSM, SIC y DENUE), así que el recomendador tiene con qué trabajar desde el primer día.
3. **Verificación presencial.** El equipo puede recorrerlo en una tarde para auditar 8 a 15 POI con el formulario de accesibilidad (fuente «verificado por equipo», §08.2 F15).
4. **Brecha de información.** Aun en la zona mejor mapeada, la mayoría de los POI no declara ningún atributo de accesibilidad. Esa brecha es el hallazgo que la auditoría y los reportes de la comunidad (spec 018) van a cerrar.

## Delimitación

- **Corredor:** el rectángulo de `data/curado/corredores.csv`, que cubre el Centro Histórico de Puebla, San Andrés Cholula y San Pedro Cholula. Solo entran POI de los municipios 21114 (Puebla), 21119 (San Andrés Cholula) y 21140 (San Pedro Cholula).
- **Patrimonio y cultura** (museos, templos, sitios históricos, zonas arqueológicas, parques, miradores, mercados) se piden en todo el rectángulo.
- **Servicios** (alimentos, sanitarios, bancas y artesanías) solo a 1.2 km de tres centros: el centro de Puebla y las cabeceras de San Pedro y San Andrés Cholula (INEGI). Así el catálogo no se llena con los miles de restaurantes de la zona metropolitana.
- **Pueblos Mágicos:** un círculo de 1.5 km alrededor de cada cabecera (Cholula ya está dentro del corredor).

## Cifras

Las genera `uv run radar corredor reporte` desde `data/curado/`; no se editan a mano.

<!-- inicio:cifras (generado por `radar corredor reporte`; no editar a mano) -->

Serie hotelera del Observatorio Turístico, año completo más reciente (2025); catálogo de POI de la spec 012.

| Destino | Pueblo Mágico | Afluencia 2025 | % del estado | Ocupación % | Estadía (días) | POI en el catálogo |
|---|---|---|---|---|---|---|
| Ciudad de Puebla | no | 10,638,390 | 59.9 % | 60.0 | 1.86 | 719 |
| Cholula | sí | 1,200,129 | 6.8 % | 57.6 | 1.86 | 705 |
| Zacatlán | sí | 1,062,360 | 6.0 % | 52.2 | 1.80 | 164 |
| Chignahuapan | sí | 781,142 | 4.4 % | 45.3 | 1.80 | 60 |
| Atlixco | sí | 475,471 | 2.7 % | 44.2 | 1.79 | 80 |
| Cuetzalan | sí | 435,587 | 2.5 % | 41.3 | 1.83 | 64 |
| Huauchinango | sí | 276,964 | 1.6 % | 43.2 | 1.86 | 43 |
| Teziutlán | sí | 271,649 | 1.5 % | 39.9 | 1.83 | 39 |
| Xicotepec | sí | 201,202 | 1.1 % | 43.8 | 1.80 | 31 |
| Tlatlauquitepec | sí | 154,207 | 0.9 % | 36.0 | 1.80 | 28 |
| Huejotzingo | sí | 103,413 | 0.6 % | 48.2 | 1.83 | 20 |
| Tetela de Ocampo | sí | 81,658 | 0.5 % | 32.9 | 1.79 | 17 |
| Pahuatlán | sí | 74,144 | 0.4 % | 32.1 | 1.81 | 21 |

- POI del corredor: 1,424; de patrimonio y cultura (museos, sitios históricos, templos, zonas arqueológicas y centros culturales): 257.
- Cobertura de información de accesibilidad en el corredor: 2.9 % de los POI tienen algún atributo; 2.8 % tienen dato de acceso sin escalones.

<!-- fin:cifras -->

## Limitaciones

- La serie hotelera mide hospedaje en hoteles registrados; no cuenta excursionistas, que en Cholula son muchos.
- El número de POI refleja cuánto se ha mapeado cada lugar, no cuánta oferta real tiene.
- La cobertura de accesibilidad mide información disponible, no accesibilidad real.

Datos © OpenStreetMap contributors (ODbL 1.0); Sistema de Información Cultural/Secretaría de Cultura; DENUE y Marco Geoestadístico, INEGI; Observatorio Turístico del Estado de Puebla.
