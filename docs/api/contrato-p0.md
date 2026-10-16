# Contrato de la API P0

Contrato entre el backend (spec 014) y la PWA (spec 016). Los campos JSON van en snake_case y en español. Un cambio a este documento va en el PR con la línea `contrato:` y se hace antes que el código.

- Base local: `http://localhost:8000`. OpenAPI en `/docs` y `/openapi.json`.
- Errores: el formato de FastAPI, `{"detail": "..."}` (o una lista de errores de validación con código 422).
- Autenticación: `Authorization: Bearer <access_token>`. Explorar lugares, destinos e itinerarios **no** requiere cuenta.
- Roles: `visitante`, `viewer`, `analista`, `admin`. El registro siempre crea `visitante`.
- Datos sintéticos: todo objeto con `is_synthetic: true` se muestra con la etiqueta «DATOS SINTÉTICOS DE DEMOSTRACIÓN».

## Tipos comunes

### Atributos de accesibilidad

Los nueve atributos: `acceso_sin_escalones`, `rampa`, `banio_accesible`, `elevador`, `superficie`, `asientos`, `estacionamiento_reservado`, `pendiente_pct`, `numero_escalones`.

```json
"accesibilidad": {
  "acceso_sin_escalones": {"valor": "si", "estado": "verificado", "origen": "equipo_verificador", "confianza": 0.9, "fecha": "2026-10-10"},
  "banio_accesible": {"valor": null, "estado": "sin_verificar", "origen": null, "confianza": null, "fecha": null}
}
```

- `accesibilidad` trae **siempre** los nueve atributos. Sin dato: `valor = null` y `estado = "sin_verificar"`. Nunca se interpreta como accesible.
- `valor`: `"si"`, `"no"` o `"limitado"` en atributos binarios; un número en texto en `pendiente_pct` y `numero_escalones`; texto libre en `superficie`.
- `estado` ∈ `verificado`, `sin_verificar`, `reportado`, `en_moderacion`.
- `confianza` entre 0 y 1. `fecha` en ISO `AAAA-MM-DD`.

### `cobertura_accesibilidad`

- `verificada`: `acceso_sin_escalones` y `banio_accesible` están verificados.
- `parcial`: al menos un atributo verificado.
- `sin_verificar`: ningún atributo verificado.

### `POIResumen`

```json
{
  "poi_id": "osm-n123",
  "nombre": "Zócalo de Atlixco",
  "categoria": "plaza",
  "destino_id": "atlixco",
  "corredor_id": "atlixco-cholula",
  "lat": 18.9088,
  "lon": -98.4341,
  "costo_rango": "gratis",
  "accesibilidad": { "...": "los nueve atributos" },
  "cobertura_accesibilidad": "parcial",
  "is_synthetic": false
}
```

`costo_rango` ∈ `gratis`, `bajo`, `medio`, `alto` o `null` (sin dato).

### `POIDetalle`

`POIResumen` más:

```json
{
  "descripcion": "…",
  "direccion": "…",
  "horario_osm": "Mo-Su 09:00-18:00",
  "fuentes": [{"id": "osm", "nombre": "OpenStreetMap", "url": "https://www.openstreetmap.org"}],
  "barreras_reportadas": [{"tipo": "escalones", "estado": "en_moderacion", "fecha": "2026-10-16"}]
}
```

`barreras_reportadas[].estado` ∈ `en_moderacion`, `aceptado`. Los reportes rechazados no aparecen. Nunca se incluye quién reportó.

## Catálogo (sin cuenta)

### `GET /pois`

Parámetros (todos opcionales):

| Parámetro | Tipo | Efecto |
|---|---|---|
| `q` | texto | Busca en nombre y descripción, sin distinguir acentos ni mayúsculas |
| `categoria` | texto | Igualdad exacta |
| `destino_id`, `corredor_id` | texto | Igualdad exacta |
| `costo_max` | `gratis`\|`bajo`\|`medio`\|`alto` | Costo menor o igual. Los lugares sin costo conocido se excluyen |
| `sin_escalones` | bool | `acceso_sin_escalones = "si"` |
| `banio_accesible` | bool | `banio_accesible = "si"` |
| `solo_verificados` | bool | Los filtros de accesibilidad solo cuentan atributos `verificado`. Sin otro filtro de accesibilidad, devuelve lugares con cobertura `verificada` o `parcial` |
| `limit` | 1–500, por omisión 50 | |
| `offset` | ≥ 0, por omisión 0 | |

Respuesta `200`: `{"items": POIResumen[], "total": int}`. Orden: `nombre`, luego `poi_id`.

### `GET /pois/{poi_id}`

`200` con `POIDetalle`; `404` si no existe.

### `GET /destinos`

`200`: `{"items": [{"destino_id", "nombre", "pueblo_magico", "lat", "lon", "zona"}]}`, ordenado por `nombre`.

## Itinerarios (sin cuenta; si hay token se asocia al usuario)

### `POST /itineraries/recommend`

```json
{
  "horas_disponibles": 4,
  "punto_partida": {"lat": 18.90, "lon": -98.43},
  "intereses": ["museo", "plaza"],
  "presupuesto": "bajo",
  "restricciones": {"sin_escalones": true, "banio_accesible": false, "descansos_cada_min": 30, "pendiente_max_pct": 6},
  "incluir_alternativos": true
}
```

Solo `horas_disponibles` (0 < h ≤ 24) es obligatorio. `intereses` se compara con `categoria`.

Respuesta `200`:

```json
{
  "itinerario_id": 12,
  "paradas": [
    {"orden": 1, "poi": POIResumen, "llegada_min": 0, "estancia_min": 45, "traslado_min": 0,
     "motivo": "…", "advertencias": ["Baño accesible sin verificar"]}
  ],
  "no_incluidos": [{"poi_id": "…", "motivo": "No cumple «sin escalones»: dato sin verificar"}],
  "alternativos": [POIResumen],
  "explicacion": "…",
  "datos_desconocidos": ["banio_accesible en Museo X"]
}
```

`llegada_min` cuenta minutos desde el inicio del recorrido. Una restricción indispensable nunca se viola: si el dato falta, el lugar va a `no_incluidos`. El punto de partida no se guarda.

### `POST /itineraries/from-saved`

```json
{"poi_ids": ["…"], "dias": 2, "horas_por_dia": 6, "restricciones": {"sin_escalones": true}}
```

`dias` 1–14, `horas_por_dia` 0–24. Respuesta `200`:

```json
{
  "itinerario_id": 13,
  "dias": [{"dia": 1, "paradas": [Parada]}],
  "no_incluidos": [{"poi_id": "…", "motivo": "…"}],
  "alternativos": [POIResumen]
}
```

`Parada` tiene la misma forma que en `/itineraries/recommend`. Un `poi_id` desconocido va a `no_incluidos` con motivo «No existe en el catálogo».

## Cuenta

### `POST /auth/registro`

`{"correo": "ana@ejemplo.mx", "contrasena": "al menos 8 caracteres", "nombre_visible": "Ana"}` (`nombre_visible` opcional). `201`:

```json
{"access_token": "…", "token_type": "bearer", "usuario": {"id": "uuid", "correo": "…", "rol": "visitante", "nombre_visible": "Ana"}}
```

`409` si el correo ya existe.

### `POST /auth/login`

`{"correo", "contrasena"}`. `200` con la misma forma; `401` si no coincide.

### `GET /me`

`200` con `usuario`. Requiere token.

## Guardados y listas (requieren token)

### `POST /saved-places`

`{"poi_id"?, "nombre_propio"?, "nota"?, "url_origen"?, "plataforma_origen"?}`. Hace falta `poi_id` o `nombre_propio` (lugar propio sin verificar). `201` con `LugarGuardado`; si el POI ya estaba guardado, `200` con el existente.

```json
{"id": 1, "poi_id": "…", "nombre_propio": null, "nota": "…", "url_origen": null, "plataforma_origen": null,
 "creado_en": "2026-10-16T12:00:00Z", "poi": POIResumen}
```

### `GET /saved-places`

`200`: `{"items": LugarGuardado[], "total": int}`. Solo los del usuario del token.

### `DELETE /saved-places/{id}`

`204`. `404` si no es del usuario.

### `POST /lists`

`{"nombre": "Fin de semana", "etiquetas": ["familia"]}`. `201`: `{"id", "nombre", "etiquetas", "items": []}`.

### `GET /lists`

`200`: `{"items": [{"id", "nombre", "etiquetas", "items": [{"id", "saved_place_id", "poi_id"}]}]}`.

### `POST /lists/{id}/items`

`{"saved_place_id"?: int, "poi_id"?: str}`. Con `poi_id` se guarda el lugar si no estaba guardado. `201`: `{"id", "list_id", "saved_place_id", "poi_id"}`. `404` si la lista no es del usuario.

## Reseñas y barreras (requieren token)

### `POST /reviews`

```json
{"poi_id": "…", "dimensiones": {"accesibilidad": 4, "limpieza": 5, "servicio": 4, "precio_percibido": 3,
 "senalizacion": 2, "comodidad": 4, "inclusion": 4, "global": 4}, "texto": "…"}
```

Cada dimensión es un entero 1–5. `global` es obligatoria; las demás son opcionales. `201`: `{"review_id", "poi_id", "dimensiones", "texto", "creado_en"}`. La reseña es privada por defecto.

### `POST /reports/barrier`

`{"poi_id", "tipo", "descripcion"?, "foto"?}`. `tipo` ∈ `escalones`, `rampa_bloqueada`, `sin_banio_accesible`, `superficie`, `senalizacion`, `otro`. `foto`: imagen JPEG, PNG o WebP en base64 (con o sin prefijo `data:`), máximo 5 MB; se guarda sin metadatos (sin EXIF). `201`:

```json
{"report_id": 7, "moderation_case_id": 7, "estado": "en_moderacion"}
```

## Moderación (rol `analista` o `admin`)

### `GET /moderation?estado=abierto`

`estado` ∈ `abierto`, `aceptado`, `rechazado` (por omisión `abierto`). `200`: `{"items": [{"id", "poi_id", "tipo", "atributo", "estado", "descripcion", "creado_en"}]}`.

### `POST /moderation/{id}/decision`

`{"decision": "aceptar"|"rechazar", "nota"?}`. `200`:

```json
{"id": 7, "estado": "aceptado", "atributo_actualizado": {"atributo": "acceso_sin_escalones", "valor": "no", "estado": "reportado"}}
```

Aceptar actualiza el atributo (`estado = "reportado"`, `origen = "comunidad"`) según el tipo, registra `AccessibilityEvidence` y `AuditEvent`. La siguiente recomendación ya lo considera.

| `tipo` | Atributo | Valor |
|---|---|---|
| `escalones` | `acceso_sin_escalones` | `no` |
| `rampa_bloqueada` | `rampa` | `no` |
| `sin_banio_accesible` | `banio_accesible` | `no` |
| `superficie` | `superficie` | `irregular` |
| `senalizacion`, `otro` | ninguno | — |

`403` para otros roles, `404` si no existe, `409` si ya se decidió.

## Privacidad (requieren token)

### `POST /consents`

`{"finalidad", "otorgado": bool, "version": "2026-10"}`. `finalidad` ∈ `ubicacion_sesion`, `resenas`, `fotos`, `analitica_agregada`. `201`: `{"id", "finalidad", "otorgado", "version", "fecha"}`. Un consentimiento nuevo de la misma finalidad revoca el anterior.

### `GET /me/export`

`200` con todos los datos de la persona: `usuario`, `consentimientos`, `preferencias_privacidad`, `preferencias_accesibilidad`, `guardados`, `listas`, `resenas`, `reportes`, `itinerarios`, `visitas`, `checkins`, `sesiones`.

### `DELETE /me`

`204`. Borra todas las filas de la persona en `private`. Los casos de moderación quedan sin vínculo a la persona.

## Reservados

Registrados sin endpoints todavía: `/sessions`, `/visits`, `/checkins` (spec 017) y `/b2b` (spec 019).
