"""Fotos de reportes: se validan y se vuelven a codificar sin metadatos (sin EXIF ni GPS)."""

import base64
import binascii
import io
import uuid
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, UnidentifiedImageError

FORMATOS = {
    "JPEG": ("image/jpeg", ".jpg"),
    "PNG": ("image/png", ".png"),
    "WEBP": ("image/webp", ".webp"),
}


class FotoInvalida(ValueError):
    pass


@dataclass(frozen=True)
class FotoLimpia:
    contenido: bytes
    tipo_mime: str
    extension: str


def decodificar(foto: str, max_bytes: int) -> bytes:
    if foto.startswith("data:"):
        _, _, foto = foto.partition(",")
    try:
        datos = base64.b64decode(foto, validate=True)
    except (binascii.Error, ValueError) as error:
        raise FotoInvalida("La foto no es base64 válido") from error
    if len(datos) > max_bytes:
        raise FotoInvalida(f"La foto pesa más de {max_bytes // (1024 * 1024)} MB")
    return datos


def limpiar(datos: bytes) -> FotoLimpia:
    """Vuelve a codificar solo los píxeles: no se copia EXIF, XMP, ICC ni GPS."""
    try:
        with Image.open(io.BytesIO(datos)) as imagen:
            formato = imagen.format
            if formato not in FORMATOS:
                raise FotoInvalida("Formato no admitido: usa JPEG, PNG o WebP")
            imagen.load()
            modo = "RGB" if formato == "JPEG" else ("RGBA" if "A" in imagen.mode else "RGB")
            pixeles = imagen.convert(modo)
            limpia = Image.new(modo, pixeles.size)
            limpia.paste(pixeles)
    except (UnidentifiedImageError, OSError) as error:
        raise FotoInvalida("La foto no es una imagen válida") from error
    salida = io.BytesIO()
    limpia.save(salida, format=formato)
    tipo_mime, extension = FORMATOS[formato]
    return FotoLimpia(salida.getvalue(), tipo_mime, extension)


def guardar(foto: FotoLimpia, directorio: Path) -> Path:
    directorio.mkdir(parents=True, exist_ok=True)
    ruta = directorio / f"{uuid.uuid4().hex}{foto.extension}"
    ruta.write_bytes(foto.contenido)
    return ruta
