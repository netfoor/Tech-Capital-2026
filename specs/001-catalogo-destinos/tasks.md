# Tareas 001 · Catálogo de destinos

Formato: `[ ]` pendiente, `[~]` en curso, `[x]` hecha. `[P]` = paralelizable con otras tareas de esta spec.

## Base

- [x] T001-01 Semilla `data/referencia/destinos.csv` con claves, cabeceras y coordenadas de INEGI. Verificación: `uv run radar catalogo` dice «correcto».
- [x] T001-02 Geometrías simplificadas de municipios y contorno estatal, registradas en `data/fuentes/fuentes.csv`. Verificación: `uv run radar fuentes`.
- [x] T001-03 `catalogo.py` con carga y validación, más pruebas. Verificación: `uv run pytest tests/test_catalogo.py`.

## Términos y detección

- [ ] T001-04 [P] `data/referencia/terminos_idiomas.csv` con términos fr, ko y zh de los 12 Pueblos Mágicos y la capital, con la columna `origen` (URL de la fuente consultada) y `verificado`. Verificación: 13 destinos × 3 idiomas, cada fila con origen.
- [ ] T001-05 Función `catalogo.detectar(texto, idioma)` según el plan (límites de palabra, término más largo y regla de «Puebla»). Depende de T001-04 solo para ko y zh. Verificación: `uv run pytest tests/test_detectar.py` con al menos 20 casos.
- [ ] T001-06 Confirmar la lista de Pueblos Mágicos en el catálogo federal y anotar la URL en `data/fuentes/fuentes.csv` (`sectur-pueblos-magicos`). Verificación: fila nueva en el registro.

## Trends (P1)

- [ ] T001-07 [P] `data/referencia/trends_temas.csv`: para cada destino, buscar el tema con `pytrends.suggestions()` desde una red residencial y verificar que la etiqueta corresponda al municipio. Verificación: 13 filas; las que no tienen tema llevan `verificado=false` y la nota «texto libre».
