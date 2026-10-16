# Tareas 008 · Radar

## P0

- [x] T008-01 [P] `tests/test_arquitectura.py`: ningún contexto importa a otro, salvo los módulos compartidos (`catalogo`, `config`, `fuentes`, `texto`, `comun`). Verificación: la prueba pasa y falla con una importación prohibida de ejemplo.
- [x] T008-02 [P] `radar/comun/estadistica.py` con percentiles con empates y Wilson. Si ya existe por T005-05, se reutiliza. Verificación: pruebas.
- [ ] T008-03 `desempeno.py`: periodo de referencia y métricas. Ya se puede hacer con los datos de 002. Verificación: `ocupacion_12m` de Cuetzalan coincide con el cálculo manual desde el CSV mensual.
- [ ] T008-04 `atencion.py`: carga opcional de cada componente y percentiles. Verificación: con solo 2 componentes disponibles, el índice se calcula y las notas lo dicen.
- [ ] T008-05 `indices.py`: índices, brecha, cuadrantes y sensibilidad, y el comando `radar radar calcular`. Verificación: `radar_destinos.csv` con 12 filas y cuadrante en todas las que tienen ≥ 2 componentes.
- [ ] T008-06 Revisión de sentido común: ¿los cuadrantes son coherentes con lo que sabe el equipo? Los casos sorprendentes se anotan en `09-resultados.md` con su explicación. Verificación: nota escrita.

## P1

- [ ] T008-07 [P] `escenarios.py` y `escenarios_derrama.csv`. Verificación: prueba con números de juguete y filas para los destinos bajo la mediana.
- [ ] T008-08 [P] `rezago.py` y `modelo_rezago.csv`. Depende de T003-04. Verificación: pruebas sintéticas y tabla con la interpretación por destino.
