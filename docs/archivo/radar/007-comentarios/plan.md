# Plan 007 · Clasificación de comentarios

## Módulos

| Archivo | Responsabilidad |
|---|---|
| `radar/comentarios/limpieza.py` | Quita menciones, URLs, correos y teléfonos; normaliza espacios |
| `radar/comentarios/prompt_v1.md` | Instrucciones, definiciones y ejemplos |
| `radar/comentarios/clasificar.py` | Llamada con salida estructurada `{categoria, subcategoria, confianza}`, por lotes de 20 comentarios, reanudable con caché por `sha1(texto_limpio)` |
| `radar/comentarios/validar.py` | κ de Cohen entre personas y del clasificador contra el consenso; matriz de confusión |
| `radar/comentarios/agregar.py` | Agregación por destino, fuente y categoría con supresión de celdas con n < 5 |

## Entradas y salidas

- Entradas privadas: `data/privado/comentarios/youtube.jsonl` y `tiktok.jsonl` (`destino_id`, `fuente`, `video_id` o `sesion_id`, `texto`, `fecha`, `me_gusta`).
- Salidas privadas: `data/privado/comentarios/clasificados.jsonl`.
- Salidas públicas: `data/curado/opinion_agregada.csv` y `data/curado/validacion_clasificador.json`.

## Procedimiento de validación

1. Se extraen 120 comentarios estratificados (10 por destino o todos si hay menos).
2. Dos personas los etiquetan sin ver al clasificador.
3. Las diferencias se resuelven por consenso.
4. Se calculan κ entre personas, κ del clasificador contra el consenso y la exactitud por categoría.
5. Si κ ≥ 0.6, se clasifica el resto; si no, se ajusta la taxonomía una vez (pregunta abierta de la spec).

## Pruebas

- Limpieza con casos de menciones, URLs y teléfonos.
- Supresión de celdas pequeñas.
- κ con un caso conocido de libro.
- El esquema de la salida rechaza categorías fuera de la taxonomía.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Pocos comentarios en destinos chicos | Se publica solo lo que pasa el umbral; la ficha dice «sin comentarios suficientes» |
| Sesgo de quien comenta | Se declara en la ficha y en «Cómo se hizo» |
