# Plan 002 · Indicadores oficiales

## Fuente

`data/fuentes/sectur-puebla/datos-ot-a-junio-2026.pdf` (`sectur-ot-2026-06`), 29 páginas: 26 de tablas y 3 de glosario. Se descargó de la página de indicadores del Observatorio Turístico el 15 de octubre de 2026.

## Módulos

| Archivo | Responsabilidad |
|---|---|
| `radar/indicadores/sectur_ot.py` | Capa anticorrupción: leer el PDF, corregir nombres, asignar procedencia, recortar meses no publicados y comprobar acumulados y coherencia |
| `radar/indicadores/resumen.py` | Agregados anuales y participación de la capital y de los Pueblos Mágicos |
| `radar/cli.py` | Comandos `indicadores` y `resumen` |

## Pasos de la ingesta

1. `fuentes.archivo("sectur-ot-2026-06")` y verificación de la SHA-256.
2. `leer_tabla`: cada fila con 16 celdas y año numérico pasa a ser un registro con 12 meses y el acumulado.
3. `comprobar_acumulados`: si hay diferencia y los 12 meses están completos, es un error; si hay meses en blanco, es un hueco de la fuente y se reporta.
4. `a_tabla_larga`: resuelve el centro (exacto, prefijo único o alias), traduce el indicador, asigna la procedencia y descarta valores vacíos.
5. `_recortar_meses_sin_publicar`: hay centros con 0.00 en julio–diciembre de 2026; se cortan en el último mes publicado.
6. `comprobar_coherencia`: unicidad de la llave y ocupación = ocupados / disponibles.
7. Escritura de las tres tablas.

## Resultados actuales (corrida del 15 de octubre de 2026)

- 20,843 valores, 22 centros, de 2017-01 a 2026-06.
- Un hueco de la fuente: Atlixco, cuartos ocupados, septiembre de 2018 (el acumulado lo incluye pero el mes está en blanco).
- Factor de afluencia: 2.222 en todos los centros salvo la capital (3.333). Desde 2019 se usa el 100 % de los meses en 9 de los 12 Pueblos Mágicos.
- 2025: la capital tiene el 59.9 % de la afluencia estatal y los 12 Pueblos Mágicos el 28.8 %.

## Pruebas

`tests/test_indicadores.py`:
- huellas de las fuentes;
- corrección de indicadores y centros cortados;
- números vacíos;
- cobertura de los 12 Pueblos Mágicos;
- procedencia según el glosario;
- sin meses no publicados;
- unicidad de la llave.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Un PDF nuevo cambia el formato | Las comprobaciones de acumulados detectan lecturas erróneas; la prueba de centros falla si aparece un nombre nuevo |
| Interpretar la derrama como dato medido | Procedencia `derivado` en la tabla y trama en el sitio |
