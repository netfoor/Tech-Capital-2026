"""Propiedad central (constitución, XIII): una restricción indispensable nunca se viola.

Se generan catálogos y solicitudes aleatorias con semilla fija, incluidos los
casos frontera (confianza 0.6 y 0.59, valores no interpretables, estados raros,
horarios no interpretables), y se comprueba con el verificador independiente.
"""

import random
from pathlib import Path

import pytest

from app.recommender import AtributoAcc, POICandidato, Restricciones, SolicitudRuta, recomendar
from app.recommender.carga import cargar_catalogo
from app.recommender.verificador import verificar

DATOS = Path(__file__).parent / "datos"
CENTRO = (19.0433, -98.1981)
CATEGORIAS = ["museo", "templo", "galeria", "mercado", "cafe", "restaurante", "parque", "plaza",
              "mirador", "artesanias", "banio", "banio", "otro"]  # fmt: skip
HORARIOS = ["Mo-Su 08:00-20:00", "Tu-Su 10:00-17:00", "24/7", "", "Mo-Su sunrise-sunset",
            "Mo-Fr 10:00-14:00,16:00-19:00; Sa 10:00-14:00; Su off", "Sa,Su 11:00-15:00",
            None]  # fmt: skip
VALORES = ["si", "si", "si", "no", "limitado", "yes", "desconocido", ""]
ESTADOS = ["verificado", "verificado", "sin_verificar", "sin_verificar", "reportado", "otro"]
CONFIANZAS = [0.0, 0.3, 0.59, 0.6, 0.61, 0.9, 1.0]


def _atributo(rng: random.Random, valores=VALORES) -> AtributoAcc | None:
    if rng.random() < 0.25:
        return None
    return AtributoAcc(
        valor=rng.choice(valores),
        estado=rng.choice(ESTADOS),
        origen=rng.choice(["equipo", "osm", "comunidad", "prestador"]),
        confianza=rng.choice(CONFIANZAS),
    )


def _catalogo(rng: random.Random, n: int) -> list[POICandidato]:
    pois = []
    for i in range(n):
        acc = {}
        for nombre, valores in (
            ("acceso_sin_escalones", VALORES),
            ("banio_accesible", VALORES),
            ("pendiente_pct", ["0", "3.5", "6", "8.1", "12", "abc", "20%"]),
        ):
            a = _atributo(rng, valores)
            if a is not None:
                acc[nombre] = a
        pois.append(
            POICandidato(
                poi_id=f"p{i:03d}",
                nombre=f"Lugar {i}",
                categoria=rng.choice(CATEGORIAS),
                destino_id=rng.choice(["puebla", "cholula", "atlixco"]),
                corredor_id="c",
                lat=CENTRO[0] + rng.uniform(-0.012, 0.012),
                lon=CENTRO[1] + rng.uniform(-0.012, 0.012),
                costo_rango=rng.choice(["gratis", "bajo", "medio", "alto", None, "raro"]),
                horario_osm=rng.choice(HORARIOS),
                accesibilidad=acc,
                es_destino_alternativo=rng.random() < 0.4,
                popularidad=rng.random(),
                descripcion=rng.choice(["historia colonial", "comida típica", "arte", ""]),
            )
        )
    return pois


def _solicitud(rng: random.Random) -> SolicitudRuta:
    return SolicitudRuta(
        horas_disponibles=rng.choice([0.5, 1, 2, 3, 4, 5, 6, 8]),
        punto_partida=rng.choice([None, CENTRO, (CENTRO[0] + 0.005, CENTRO[1] - 0.004)]),
        intereses=rng.sample(
            ["historia", "arte", "gastronomia", "naturaleza", "religion"], rng.randint(0, 3)
        ),  # fmt: skip
        presupuesto=rng.choice([None, "gratis", "bajo", "medio", "alto"]),
        restricciones=Restricciones(
            sin_escalones=rng.random() < 0.6,
            banio_accesible=rng.random() < 0.4,
            descansos_cada_min=rng.choice([None, None, 20, 30, 45, 60]),
            pendiente_max_pct=rng.choice([None, None, 4.0, 6.0, 8.0]),
        ),
        incluir_alternativos=rng.random() < 0.8,
        hora_inicio=rng.choice(["08:00", "09:30", "10:00", "13:00", "16:00"]),
        dia_semana=rng.choice([None, 0, 1, 2, 3, 4, 5, 6]),
    )


@pytest.mark.parametrize("semilla", range(12))
def test_ninguna_violacion_en_catalogos_aleatorios(semilla):
    rng = random.Random(1000 + semilla)
    pois = _catalogo(rng, rng.randint(5, 35))
    por_id = {p.poi_id: p for p in pois}
    for _ in range(20):
        s = _solicitud(rng)
        r = recomendar(s, pois)
        violaciones = verificar(r, s, por_id)
        assert violaciones == [], (s, violaciones)
        # Lo que no tiene dato nunca entra en la ruta.
        if s.restricciones.sin_escalones:
            for p in r.paradas:
                if p.poi_id in por_id:
                    assert "acceso_sin_escalones" in por_id[p.poi_id].accesibilidad
        # Ninguna parada repetida (salvo baños de servicio).
        lugares = [p.poi_id for p in r.paradas if p.poi_id in por_id
                   and por_id[p.poi_id].categoria != "banio"]  # fmt: skip
        assert len(lugares) == len(set(lugares))
        assert r.explicacion.strip()


def test_ninguna_violacion_en_el_catalogo_sintetico():
    pois = cargar_catalogo(DATOS / "poi_sintetico.csv", DATOS / "poi_accesibilidad_sintetico.csv")
    por_id = {p.poi_id: p for p in pois}
    rng = random.Random(7)
    for _ in range(80):
        s = _solicitud(rng)
        r = recomendar(s, pois)
        assert verificar(r, s, por_id) == []
        assert all(p.motivo for p in r.paradas)
