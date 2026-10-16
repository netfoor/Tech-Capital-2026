# Contratos

Forma de cada archivo JSON que consume el sitio (`web/public/datos/`), escrita en JSON Schema 2020-12. El exportador (`radar exportar`, spec 009) valida cada archivo contra su esquema antes de escribirlo. Si uno no pasa, no se escribe ninguno.

| Archivo publicado | Esquema | Lo produce (contexto · spec) | Lo usa (sección del sitio) | Desde |
|---|---|---|---|---|
| `manifiesto.json` | [`manifiesto.schema.json`](manifiesto.schema.json) | Publicación · 009 | Pie, y Datos y código | Primera versión |
| `destinos.json` | [`destinos.schema.json`](destinos.schema.json) | Catálogo · 001 | Todas | Primera versión |
| `geo/municipios.json`, `geo/estado.json` | [`geo.schema.json`](geo.schema.json) | Catálogo · 001 | Inicio y Radar | Primera versión |
| `radar.json` | [`radar.schema.json`](radar.schema.json) | Radar · 008 (el desempeño sale de 002) | Inicio, Radar y Para el Tianguis | Primera versión, solo con desempeño |
| `evidencia.json` | [`evidencia.schema.json`](evidencia.schema.json) | Indicadores · 002 y registro de fuentes | El problema | Primera versión |
| `metodo.json` | [`metodo.schema.json`](metodo.schema.json) | Publicación · 009 | Cómo se hizo | Primera versión |
| `fichas/<destino_id>.json` | [`ficha.schema.json`](ficha.schema.json) | Radar · 008, con 002, 004, 005, 006 y 007 | Fichas de destino | Con 008 |
| `asistentes.json` | [`asistentes.schema.json`](asistentes.schema.json) | Asistentes · 006 | Lo que responden los asistentes | Con 006 |
| `redes.json` | [`redes.schema.json`](redes.schema.json) | Señales · 004, Panel · 005 y Comentarios · 007 | Lo que se ve en redes | Con 005 |

[`comun.schema.json`](comun.schema.json) define los tipos compartidos: `destino_id`, `periodo`, porcentaje, componente del radar y proporción con intervalo de Wilson.

## Reglas

1. **Orden de cambio.** Un cambio de contrato se hace primero aquí, después en el exportador y al final en el sitio. Si cambia el significado de un campo, se anota en la spec que lo produce.
2. **Lo que falta va en `null`.** Los bloques que dependen de una fuente que todavía no existe se publican en `null` y no se omiten. El sitio muestra «pendiente» en lugar de inventar.
3. **Sin identidad personal.** Ningún contrato tiene campos como `usuario`, `autor`, `nombre_participante` o `texto_comentario`. Lo revisa `pipelines/tests/test_contratos.py`.
4. **Unidades.** Porcentajes de 0 a 100 (`pct`, `*_pct`, `ocupacion_12m` e índices). Proporciones de 0 a 1 (`proporcion`). Fechas en ISO 8601 y periodos en `AAAA-MM`.
5. **Redondeo en el exportador.** Porcentajes a 1 decimal, pesos a enteros y coordenadas a 4 decimales. El sitio no redondea de nuevo.

## Validar

```bash
cd pipelines
uv run pytest tests/test_contratos.py   # esquemas válidos, referencias resueltas y campos prohibidos
uv run radar exportar --validar         # el paquete de datos contra los esquemas (T009-02)
```

Desde Python, con las referencias entre archivos:

```python
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

esquemas = {p.name: json.loads(p.read_text()) for p in Path("contracts").glob("*.schema.json")}
registro = Registry().with_resources(
    (nombre, Resource.from_contents(esquema)) for nombre, esquema in esquemas.items()
)
Draft202012Validator(esquemas["radar.schema.json"], registry=registro).validate(instancia)
```
