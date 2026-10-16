"""OpenStreetMap vía Overpass API: consulta, lectura y mapeo a categoría y accesibilidad.

Datos © OpenStreetMap contributors, disponibles bajo la Open Database License (ODbL 1.0).
"""

from __future__ import annotations

import re
import time
from collections.abc import Iterable
from dataclasses import dataclass

from radar.corredor.zonas import Centro, Corredor

FUENTE_ID = "osm-overpass"

SERVIDORES = (
    "https://overpass-api.de/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
)
AGENTE = "PueblaViva360/0.1 (Hackathon Tech Capital 2026; ingesta de POI turisticos)"

CONFIANZA_OSM = 0.6

# Lo que se pide en todo el rectángulo del corredor o en el círculo de un Pueblo Mágico.
FILTROS_PATRIMONIO = (
    '["tourism"]',
    '["historic"]',
    '["amenity"~"^(place_of_worship|marketplace|arts_centre|theatre)$"]',
    '["leisure"~"^(park|garden)$"]["name"]',
)
# Lo que solo se pide cerca de los centros (en el corredor hay miles de restaurantes).
FILTROS_SERVICIOS = (
    '["amenity"~"^(restaurant|cafe|toilets|bench)$"]',
    '["shop"~"^(craft|gift|art)$"]',
    '["craft"]["name"]',
)


def _lineas(filtros: Iterable[str], area: str) -> list[str]:
    return [f"  nwr{f}({area});" for f in filtros]


def consulta_corredor(corredor: Corredor, centros: Iterable[Centro], timeout: int = 180) -> str:
    caja = f"{corredor.lat_min},{corredor.lon_min},{corredor.lat_max},{corredor.lon_max}"
    lineas = _lineas(FILTROS_PATRIMONIO, caja)
    for c in centros:
        lineas += _lineas(FILTROS_SERVICIOS, f"around:{c.radio_m},{c.lat:.7f},{c.lon:.7f}")
    cuerpo = "\n".join(lineas)
    return f"[out:json][timeout:{timeout}];\n(\n{cuerpo}\n);\nout center meta;\n"


def consulta_centro(centro: Centro, timeout: int = 180) -> str:
    area = f"around:{centro.radio_m},{centro.lat:.7f},{centro.lon:.7f}"
    cuerpo = "\n".join(_lineas(FILTROS_PATRIMONIO + FILTROS_SERVICIOS, area))
    return f"[out:json][timeout:{timeout}];\n(\n{cuerpo}\n);\nout center meta;\n"


def consultar(
    consulta: str,
    servidores: tuple[str, ...] = SERVIDORES,
    intentos: int = 8,
    espera_inicial_s: float = 15.0,
) -> tuple[bytes, str]:
    """Envía la consulta con espera creciente entre intentos. Devuelve (cuerpo, url)."""
    import httpx

    espera = espera_inicial_s
    ultimo = ""
    for intento in range(intentos):
        url = servidores[intento % len(servidores)]
        try:
            r = httpx.post(
                url,
                data={"data": consulta},
                headers={"User-Agent": AGENTE, "Accept": "application/json"},
                timeout=240,
            )
            if r.status_code == 200 and r.content.lstrip().startswith(b"{"):
                return r.content, url
            ultimo = f"{url}: HTTP {r.status_code}"
        except httpx.HTTPError as e:
            ultimo = f"{url}: {type(e).__name__}"
        time.sleep(espera)
        espera = min(espera * 2, 120.0)
    raise RuntimeError(f"Overpass no respondió después de {intentos} intentos ({ultimo})")


SIN_PERSONAS = ("user", "uid", "changeset")


def compactar(respuesta: dict, consulta: str) -> dict:
    """Extracto versionable: elementos ordenados, sin usuario ni conjunto de cambios de OSM."""
    elementos = [
        {k: v for k, v in e.items() if k not in SIN_PERSONAS}
        for e in sorted(respuesta.get("elements", []), key=lambda e: (e["type"], e["id"]))
    ]
    return {"osm3s": respuesta.get("osm3s", {}), "consulta": consulta, "elements": elementos}


@dataclass(frozen=True)
class Elemento:
    tipo: str  # node, way, relation
    id: int
    lat: float
    lon: float
    etiquetas: dict[str, str]
    fecha: str  # AAAA-MM-DD de la última edición

    @property
    def osm_id(self) -> str:
        return f"{self.tipo}/{self.id}"

    @property
    def poi_id(self) -> str:
        return f"osm-{self.tipo[0]}{self.id}"


def leer(respuesta: dict) -> list[Elemento]:
    elementos = []
    for e in respuesta.get("elements", []):
        if "lat" in e:
            lat, lon = e["lat"], e["lon"]
        elif "center" in e:
            lat, lon = e["center"]["lat"], e["center"]["lon"]
        else:
            continue
        elementos.append(
            Elemento(
                tipo=e["type"],
                id=int(e["id"]),
                lat=float(lat),
                lon=float(lon),
                etiquetas={str(k): str(v) for k, v in (e.get("tags") or {}).items()},
                fecha=str(e.get("timestamp", ""))[:10],
            )
        )
    return elementos


ALOJAMIENTO = {"hotel", "hostel", "guest_house", "motel", "apartment", "chalet"}


def categoria(t: dict[str, str]) -> tuple[str, str] | None:
    """Categoría y subcategoría del contrato, o None si el elemento no es un POI."""
    tourism, historic, amenity = t.get("tourism", ""), t.get("historic", ""), t.get("amenity", "")
    leisure, shop, craft = t.get("leisure", ""), t.get("shop", ""), t.get("craft", "")
    if tourism == "museum" or amenity == "museum":
        return "museo", "museum"
    if historic == "archaeological_site":
        return "zona_arqueologica", t.get("site_type", "archaeological_site")
    if amenity == "place_of_worship":
        return "templo", t.get("building", "") or t.get("religion", "") or "place_of_worship"
    if tourism == "viewpoint":
        return "mirador", "viewpoint"
    if amenity == "marketplace":
        return "mercado", "marketplace"
    if shop in {"craft", "gift", "art"}:
        return "artesanias", f"shop={shop}"
    if craft:
        return "artesanias", f"craft={craft}"
    if amenity in {"arts_centre", "theatre"}:
        return "centro_cultural", amenity
    if tourism == "gallery":
        return "centro_cultural", "gallery"
    if amenity == "restaurant":
        return "restaurante", t.get("cuisine", "") or "restaurant"
    if amenity == "cafe":
        return "cafe", "cafe"
    if tourism in ALOJAMIENTO:
        return "alojamiento", tourism
    if amenity == "toilets":
        return "banio", "toilets"
    if leisure in {"park", "garden"}:
        return "parque", leisure
    if historic:
        return "sitio_historico", historic
    if tourism in {"attraction", "theme_park", "zoo", "picnic_site", "artwork"}:
        return "otro", tourism
    if tourism == "information" and t.get("information") == "office":
        return "otro", "information_office"
    return None


def nombre(t: dict[str, str], cat: str) -> str:
    for clave in ("name", "name:es", "official_name", "alt_name"):
        if t.get(clave, "").strip():
            return t[clave].strip()
    if cat == "banio":
        return "Sanitarios (sin nombre en OpenStreetMap)"
    return ""


def es_poi(e: Elemento) -> tuple[str, str] | None:
    """Categoría si el elemento entra al catálogo: con nombre (salvo baños) y no banca."""
    if e.etiquetas.get("amenity") == "bench":
        return None
    cat = categoria(e.etiquetas)
    if cat is None or not nombre(e.etiquetas, cat[0]):
        return None
    return cat


def costo(t: dict[str, str]) -> str:
    fee = t.get("fee", "").strip().lower()
    if fee == "no":
        return "gratis"
    return "desconocido"


def direccion(t: dict[str, str]) -> str:
    calle = t.get("addr:street", "").strip()
    numero = t.get("addr:housenumber", "").strip()
    partes = [" ".join(p for p in (calle, numero) if p)]
    for clave in ("addr:suburb", "addr:city"):
        if t.get(clave, "").strip():
            partes.append(t[clave].strip())
    return ", ".join(p for p in partes if p)


_SI_NO = {"yes": "si", "designated": "si", "limited": "parcial", "no": "no"}
_NUMERO = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*%?\s*$")


def accesibilidad(e: Elemento, cat: str) -> list[dict[str, object]]:
    """Filas de `poi_accesibilidad.csv` a partir de las etiquetas presentes. Nunca infiere."""
    t = e.etiquetas
    filas: list[dict[str, object]] = []

    def agregar(atributo: str, valor: str, clave: str) -> None:
        filas.append(
            {
                "poi_id": e.poi_id,
                "atributo": atributo,
                "valor": valor,
                "origen": "osm",
                "fecha": e.fecha,
                "confianza": CONFIANZA_OSM,
                "estado": "sin_verificar",
                "evidencia": f"osm:{e.osm_id} {clave}={t[clave]}",
            }
        )

    def si_no(clave: str, atributo: str) -> None:
        valor = _SI_NO.get(t.get(clave, "").strip().lower())
        if valor:
            agregar(atributo, valor, clave)

    si_no("wheelchair", "banio_accesible" if cat == "banio" else "acceso_sin_escalones")
    if cat != "banio" or "wheelchair" not in t:
        si_no("toilets:wheelchair", "banio_accesible")
    if "ramp:wheelchair" in t:
        si_no("ramp:wheelchair", "rampa")
    else:
        si_no("ramp", "rampa")
    si_no("elevator", "elevador")
    si_no("bench", "asientos")
    if t.get("step_count", "").strip().isdigit():
        agregar("numero_escalones", str(int(t["step_count"])), "step_count")
    m = _NUMERO.match(t.get("incline", ""))
    if m:
        agregar("pendiente_pct", m.group(1), "incline")
    if t.get("surface", "").strip():
        agregar("superficie", t["surface"].strip(), "surface")
    capacidad = t.get("capacity:disabled", "").strip()
    if capacidad.isdigit():
        agregar(
            "estacionamiento_reservado", "si" if int(capacidad) > 0 else "no", "capacity:disabled"
        )
    elif "parking:disabled" in t:
        si_no("parking:disabled", "estacionamiento_reservado")
    return filas
