"""Taxonomía fija de la spec 007 y esquema de la salida del clasificador."""

CATEGORIAS = [
    "intencion",
    "experiencia_positiva",
    "experiencia_negativa",
    "friccion",
    "pregunta",
    "otro",
]
FRICCIONES = ["precio", "acceso", "seguridad", "saturacion", "servicios", "clima", "otro"]

ESQUEMA_SALIDA = {
    "type": "object",
    "required": ["id", "categoria"],
    "properties": {
        "id": {"type": "integer"},
        "categoria": {"enum": CATEGORIAS},
        "friccion": {"enum": FRICCIONES + [None]},
    },
    "additionalProperties": False,
}
