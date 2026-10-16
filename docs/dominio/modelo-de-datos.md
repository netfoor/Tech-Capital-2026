# Modelo de datos

Tablas que cada contexto publica en `data/curado/`. Son CSV en UTF-8, con encabezado y punto decimal. Esta es la definición vigente: cualquier cambio de columnas se hace aquí primero y después en el código.

**Convenciones**
- `destino_id` es la llave del catálogo. `periodo` es `AAAA-MM`. `fecha_consulta` es `AAAA-MM-DD` en la hora de Ciudad de México.
- Cada tabla tiene `fuente_id`, que remite a `data/fuentes/fuentes.csv`, o una columna de corrida o consulta que remite a su registro crudo.
- La columna «Versionado» indica si el archivo entra en git: **sí** (curado), **no** (crudo o privado).

## Catálogo territorial

### `data/referencia/destinos.csv` · versionado: sí

| Columna | Tipo | Notas |
|---|---|---|
| `destino_id` | texto, llave | slug en minúsculas |
| `nombre` | texto | |
| `tipo` | `pueblo_magico` \| `ciudad` | |
| `pueblo_magico` | booleano | |
| `municipios_cvegeo` | texto | claves de 5 dígitos separadas por `;` |
| `cabecera_cvegeo` | texto | clave de localidad de 9 dígitos |
| `cabecera` | texto | nombre oficial INEGI |
| `lat`, `lon` | decimal | WGS84 |
| `altitud_m` | entero | |
| `zona` | texto | agrupación de trabajo |
| `centro_ot` | texto | nombre del centro en el Observatorio Turístico |
| `terminos_es`, `terminos_en` | texto | variantes separadas por `\|` |
| `hashtags` | texto | separados por `\|` |

Las variantes en francés, coreano y chino viven en `data/referencia/terminos_idiomas.csv` (spec 006): `destino_id`, `idioma`, `termino`, `origen`, `verificado`.

## Desempeño turístico

### `indicadores_oficiales_mensual.csv` · versionado: sí

| Columna | Tipo | Notas |
|---|---|---|
| `centro_ot` | texto | |
| `destino_id` | texto | vacío para agregados y subcentros |
| `nivel` | `destino` \| `subcentro` \| `agregado` | |
| `anio`, `mes` | entero | |
| `periodo` | texto | |
| `indicador` | texto | ver el lenguaje ubicuo |
| `valor` | decimal | |
| `unidad` | texto | |
| `procedencia` | `medido` \| `derivado` | |
| `fuente_id` | texto | |

Llave: (`centro_ot`, `indicador`, `anio`, `mes`).

### `indicadores_oficiales_anual.csv` · versionado: sí

Suma anual de indicadores aditivos y cocientes recalculados: `ocupacion_pct`, `estadia_promedio_dias`, `derrama_por_visitante_mxn` y `cuartos_libres_por_dia`. La columna `meses` indica si el año está completo.

### `factor_afluencia_por_centro.csv` · versionado: sí

`centro_ot`, `factor_mas_frecuente`, `meses`, `proporcion_meses_con_ese_factor`, `proporcion_desde_2019`.

## Atención digital

### `interes_busqueda_mensual.csv` · versionado: sí

| Columna | Tipo | Notas |
|---|---|---|
| `destino_id` | texto | |
| `termino` | texto | término o tema (`/m/…`) usado |
| `geo` | texto | `MX`, `MX-PUE`, `US`… |
| `periodo` | texto | |
| `interes` | entero 0–100 | valor de Trends en su lote |
| `ancla` | texto | término ancla del lote |
| `interes_ajustado` | decimal | interés del destino entre el interés del ancla en el mismo lote y periodo, multiplicado por 100 |
| `consulta_id` | texto | remite a `data/crudo/trends/` |
| `fecha_consulta` | fecha | |

### `videos_por_destino.csv` · versionado: sí

| Columna | Tipo | Notas |
|---|---|---|
| `destino_id` | texto | |
| `consulta` | texto | texto de búsqueda |
| `idioma`, `region` | texto | |
| `n_videos` | entero | resultados considerados (máximo 10) |
| `vistas_mediana`, `vistas_total` | entero | |
| `comentarios_total` | entero | |
| `antiguedad_mediana_dias` | entero | |
| `fecha_consulta` | fecha | |

El detalle por video (`data/crudo/youtube/`) no se versiona por los términos de la API.

### `presencia_youtube.csv` · versionado: sí

`destino_id`, `consulta_id`, `n_resultados`, `k_menciones`, `proporcion`. Proporción de resultados de las consultas genéricas que mencionan el destino (spec 004).

## Panel ciudadano

### `panel_observaciones.csv` · versionado: sí (anonimizado)

| Columna | Tipo | Notas |
|---|---|---|
| `sesion_id` | texto | |
| `participante_id` | texto | `Pnn` |
| `rango_edad` | `18-24` \| `25-34` \| `35-44` \| `45+` | |
| `region_residencia` | texto | estado o país, no ciudad |
| `plataforma` | `tiktok` | |
| `consulta_id` | texto | consulta del protocolo |
| `posicion` | entero | 1 a 12 |
| `destino_id` | texto | vacío si el resultado no corresponde a un destino del catálogo |
| `vistas_visibles` | entero | lo que muestra la tarjeta, si aparece |
| `tipo_contenido` | `recorrido` \| `lista` \| `comida` \| `evento` \| `otro` | |
| `fecha` | fecha | |
| `version_protocolo` | texto | |

### `presencia_panel.csv` · versionado: sí

`destino_id`, `n_sesiones`, `k_sesiones`, `presencia_pct`, `ic95_bajo`, `ic95_alto`. Proporción de sesiones en que el destino aparece entre los 12 primeros resultados de al menos una consulta (spec 005).

`data/privado/panel/` (no versionado) guarda los consentimientos, las capturas y los datos de contacto.

## Visibilidad en asistentes

### `asistentes_corridas.csv` · versionado: sí

`corrida_id`, `prompt_id`, `brazo`, `proveedor`, `modelo`, `idioma`, `mercado`, `tono`, `con_busqueda`, `busco`, `repeticion`, `fecha`, `sha256_respuesta`, `archivo_crudo`, `tokens_entrada`, `tokens_salida`.

Las respuestas crudas (`data/crudo/asistentes/*.jsonl`) **no se versionan**: los términos de cada proveedor sobre guardar y redistribuir respuestas con búsqueda no se han revisado. Su SHA-256 queda en `sha256_respuesta`, y el equipo las conserva para auditoría. Las del brazo real se quedan en `data/privado/`.

### `asistentes_ejemplos.csv` · versionado: sí

`corrida_id`, `idioma`, `proveedor`, `prompt`, `fragmento` (máximo 600 caracteres), `destinos_mencionados` (separados por `|`), `dominios` (separados por `|`). Una respuesta por idioma, elegida con semilla fija entre las corridas de OpenAI con búsqueda. Es lo único del texto de las respuestas que se publica.

### `asistentes_menciones.csv` · versionado: sí

`corrida_id`, `destino_id`, `orden`, `metodo` (`terminos` \| `extractor`).

### `asistentes_citas.csv` · versionado: sí

`corrida_id`, `url`, `dominio`, `tipo_dominio` (`gobierno` \| `medio` \| `blog` \| `agencia_viajes` \| `red_social` \| `enciclopedia` \| `otro`).

### `asistentes_visibilidad.csv` · versionado: sí

`destino_id`, `segmento` (por ejemplo `proveedor=openai;idioma=es`), `n`, `k`, `visibilidad_pct`, `ic95_bajo`, `ic95_alto`.

## Opinión del visitante

### `opinion_agregada.csv` · versionado: sí

`destino_id`, `fuente` (`youtube` \| `tiktok`), `categoria`, `subcategoria`, `n`, `proporcion`, `modelo`, `fecha`. Solo celdas con n ≥ 5.

### `validacion_clasificador.json` · versionado: sí

Tamaño de la muestra, κ entre personas, κ contra el clasificador, matriz de confusión y versión del prompt.

## Análisis

### `radar_destinos.csv` · versionado: sí

| Columna | Tipo | Notas |
|---|---|---|
| `destino_id` | texto | |
| `periodo_ref` | texto | último periodo oficial usado |
| `ocupacion_12m` | decimal | % medido |
| `cuartos_libres_dia_12m` | decimal | |
| `llegadas_12m` | entero | |
| `crecimiento_llegadas_pct` | decimal | últimos 12 meses frente a los 12 previos |
| `atencion_busqueda_pctl`, `atencion_video_pctl`, `atencion_panel_pctl`, `atencion_asistentes_pctl` | decimal 0–100 | vacío si no hay dato |
| `componentes_disponibles` | entero | |
| `indice_atencion`, `indice_desempeno` | decimal 0–100 | |
| `brecha` | decimal | |
| `cuadrante` | texto | |
| `notas` | texto | advertencias de datos |

### `modelo_rezago.csv` · versionado: sí

`destino_id`, `especificacion`, `mape_modelo`, `mape_linea_base`, `mejora_pct`, `periodo_prueba`, `n_meses`.

### `escenarios_derrama.csv` · versionado: sí

`destino_id`, `supuesto_pp`, `cuartos_adicionales_mes`, `turistas_adicionales_mes`, `visitantes_adicionales_mes`, `derrama_adicional_mes_mxn`, `metodo`.

## Publicación

Los JSON del sitio y sus esquemas están en [`contracts/`](../../contracts/).
