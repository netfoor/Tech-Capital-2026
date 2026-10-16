"""Genera el catálogo sintético de prueba del recomendador (spec 015).

DATOS SINTÉTICOS DE DEMOSTRACIÓN: los nombres son inventados, las coordenadas
caen en zonas plausibles del corredor Centro Histórico de Puebla → Cholula y
los atributos de accesibilidad se sortean con semilla fija. No describen
ningún lugar real. Cada fila lleva ``is_synthetic=true``.

Uso (desde ``backend/``)::

    uv run python ../analysis/02a_catalogo_sintetico.py
"""

from __future__ import annotations

import csv
import random
from pathlib import Path

SEMILLA = 2026
RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "backend" / "tests" / "datos"

COLUMNAS_POI = [
    "poi_id", "nombre", "categoria", "subcategoria", "destino_id", "corredor_id",
    "municipio_cvegeo", "lat", "lon", "direccion", "horario_osm", "costo_rango",
    "descripcion", "fuentes", "osm_id", "denue_id", "sic_id", "match_score",
    "is_synthetic", "popularidad", "es_destino_alternativo",
]  # fmt: skip
COLUMNAS_ACC = [
    "poi_id", "atributo", "valor", "origen", "fecha", "confianza", "estado", "evidencia",
    "is_synthetic",
]  # fmt: skip

# (clave, nombre, destino, municipio, centro lat/lon, radio m, alternativo, n)
ZONAS = [
    ("cen", "Centro", "puebla", "21114", (19.0433, -98.1981), 550, False, 14),
    ("nor", "Barrio Norte", "puebla", "21114", (19.0500, -98.1905), 350, True, 6),
    ("sur", "Barrio Sur", "puebla", "21114", (19.0365, -98.1925), 350, True, 5),
    ("cho", "Cholula Centro", "cholula", "21140", (19.0632, -98.3058), 450, False, 10),
    ("ton", "Cholula Sur", "cholula", "21119", (19.0335, -98.2960), 400, True, 5),
]

CATEGORIAS = [
    ("museo", "Museo", ["historia virreinal y colonial", "arte y pintura", "talavera y artesanía"]),
    ("templo", "Templo", ["templo barroco con fachada de talavera", "capilla colonial"]),
    ("galeria", "Galería", ["galería de arte contemporáneo", "exposición de escultura"]),
    ("mercado", "Mercado", ["mercado de comida tradicional y mole", "dulces típicos y antojitos"]),
    ("artesanias", "Taller", ["artesanías de talavera", "tienda de artesanos locales"]),
    ("cafe", "Café", ["café de especialidad", "cocina tradicional"]),
    ("restaurante", "Restaurante", ["comida poblana y mole", "cocina de antojitos"]),
    ("parque", "Jardín", ["parque con árboles y bancas", "jardín al aire libre"]),
    ("plaza", "Plaza", ["plaza tradicional del barrio", "plaza con vista a la catedral"]),
    ("mirador", "Mirador", ["mirador con vista panorámica", "cerro con vista"]),
    ("zona_arqueologica", "Zona arqueológica", ["pirámide prehispánica y ruinas"]),
    ("barrio", "Callejón", ["callejón tradicional con vecinos y fachadas"]),
]

HORARIOS = [
    "Tu-Su 10:00-17:00",
    "Mo-Su 09:00-18:00",
    "Mo-Sa 08:00-20:00; Su 09:00-14:00",
    "24/7",
    "Mo-Fr 10:00-14:00,16:00-19:00; Sa 10:00-14:00; Su off",
    "Tu-Su 10:00-17:00; PH off",  # no interpretable a propósito
    "",
    "Mo-Su sunrise-sunset",  # no interpretable a propósito
]
COSTOS = ["gratis", "gratis", "bajo", "bajo", "medio", "alto", ""]


def _desplazar(rng: random.Random, centro: tuple[float, float], radio: float):
    dlat = rng.uniform(-radio, radio) / 111_320
    dlon = rng.uniform(-radio, radio) / 105_000
    return round(centro[0] + dlat, 6), round(centro[1] + dlon, 6)


def _acceso(rng: random.Random) -> tuple[str, str, str, float] | None:
    x = rng.random()
    if x < 0.35:
        return ("si", "verificado", "equipo", round(rng.uniform(0.8, 0.95), 2))
    if x < 0.50:
        return ("si", "sin_verificar", "osm", round(rng.uniform(0.6, 0.75), 2))
    if x < 0.60:
        return ("si", "sin_verificar", "comunidad", round(rng.uniform(0.3, 0.55), 2))
    if x < 0.68:
        return ("no", "verificado", "equipo", 0.9)
    if x < 0.72:
        return ("limitado", "sin_verificar", "osm", 0.7)
    if x < 0.76:
        return ("si", "reportado", "comunidad", 0.7)
    return None


def generar() -> tuple[list[dict], list[dict]]:
    rng = random.Random(SEMILLA)
    pois: list[dict] = []
    acc: list[dict] = []

    def agregar_acc(pid, atributo, valor, estado, origen, confianza, fecha="2026-10-15"):
        acc.append(
            {
                "poi_id": pid, "atributo": atributo, "valor": valor, "origen": origen,
                "fecha": fecha, "confianza": f"{confianza:.2f}", "estado": estado,
                "evidencia": "sintético", "is_synthetic": "true",
            }
        )  # fmt: skip

    for clave, nombre_zona, destino, cvegeo, centro, radio, alternativo, n in ZONAS:
        for i in range(n):
            cat, etiqueta, descripciones = CATEGORIAS[(i + len(clave)) % len(CATEGORIAS)]
            if clave != "cho" and cat == "zona_arqueologica":
                cat, etiqueta, descripciones = CATEGORIAS[0]
            pid = f"syn-{clave}-{i + 1:02d}"
            lat, lon = _desplazar(rng, centro, radio)
            pop = rng.uniform(0.1, 0.4) if alternativo else rng.uniform(0.6, 0.95)
            pois.append(
                {
                    "poi_id": pid,
                    "nombre": f"{etiqueta} {nombre_zona} {i + 1} (sintético)",
                    "categoria": cat,
                    "subcategoria": "",
                    "destino_id": destino,
                    "corredor_id": "centro-cholula",
                    "municipio_cvegeo": cvegeo,
                    "lat": f"{lat:.6f}",
                    "lon": f"{lon:.6f}",
                    "direccion": "",
                    "horario_osm": rng.choice(HORARIOS),
                    "costo_rango": rng.choice(COSTOS),
                    "descripcion": rng.choice(descripciones),
                    "fuentes": "sintetico",
                    "osm_id": "",
                    "denue_id": "",
                    "sic_id": "",
                    "match_score": "",
                    "is_synthetic": "true",
                    "popularidad": f"{pop:.4f}",
                    "es_destino_alternativo": "true" if alternativo else "false",
                }
            )
            a = _acceso(rng)
            if a:
                agregar_acc(pid, "acceso_sin_escalones", a[0], a[1], a[2], a[3])
            if rng.random() < 0.3:
                agregar_acc(pid, "banio_accesible", "si", "verificado", "equipo", 0.9)
            if rng.random() < 0.55:
                pend = rng.uniform(0, 14) if cat != "mirador" else rng.uniform(8, 18)
                estado = "verificado" if rng.random() < 0.6 else "sin_verificar"
                agregar_acc(pid, "pendiente_pct", f"{pend:.1f}", estado, "equipo", 0.85)
        # Baños públicos de la zona.
        for j in range(2 if clave in ("cen", "cho") else 1):
            pid = f"syn-{clave}-b{j + 1}"
            lat, lon = _desplazar(rng, centro, radio * 0.8)
            pois.append(
                {
                    "poi_id": pid, "nombre": f"Sanitario público {nombre_zona} {j + 1} (sintético)",
                    "categoria": "banio", "subcategoria": "sanitario", "destino_id": destino,
                    "corredor_id": "centro-cholula", "municipio_cvegeo": cvegeo,
                    "lat": f"{lat:.6f}", "lon": f"{lon:.6f}", "direccion": "",
                    "horario_osm": "Mo-Su 08:00-20:00", "costo_rango": "bajo",
                    "descripcion": "sanitario público", "fuentes": "sintetico", "osm_id": "",
                    "denue_id": "", "sic_id": "", "match_score": "", "is_synthetic": "true",
                    "popularidad": "0.0000", "es_destino_alternativo": "false",
                }
            )  # fmt: skip
            accesible = j == 0
            agregar_acc(
                pid, "banio_accesible", "si" if accesible else "no", "verificado", "equipo", 0.9
            )
            agregar_acc(pid, "acceso_sin_escalones", "si", "verificado", "equipo", 0.9)
            agregar_acc(pid, "pendiente_pct", "2.0", "verificado", "equipo", 0.9)

    # Caso de historia: verificado y después una barrera reportada (gana la reciente).
    agregar_acc("syn-cen-01", "acceso_sin_escalones", "si", "verificado", "equipo", 0.9,
                "2026-09-01")  # fmt: skip
    agregar_acc("syn-cen-01", "acceso_sin_escalones", "si", "reportado", "comunidad", 0.7,
                "2026-10-16")  # fmt: skip
    return pois, acc


def escribir(ruta: Path, columnas: list[str], filas: list[dict]) -> None:
    with ruta.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columnas, lineterminator="\n")
        w.writeheader()
        w.writerows(filas)


def main() -> None:
    pois, acc = generar()
    DESTINO.mkdir(parents=True, exist_ok=True)
    escribir(DESTINO / "poi_sintetico.csv", COLUMNAS_POI, pois)
    escribir(DESTINO / "poi_accesibilidad_sintetico.csv", COLUMNAS_ACC, acc)
    print(f"{len(pois)} POI y {len(acc)} atributos sintéticos en {DESTINO}")


if __name__ == "__main__":
    main()
