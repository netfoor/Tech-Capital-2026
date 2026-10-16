import pytest

from radar import catalogo
from radar.asistentes import menciones

DESTINOS = catalogo.cargar()
TERMINOS = catalogo.cargar_terminos_idiomas()


def ids(texto, idioma, extraidos=None):
    return [
        (m.destino_id, m.metodo)
        for m in menciones.menciones_de_respuesta(texto, idioma, DESTINOS, TERMINOS, extraidos)
    ]


@pytest.mark.parametrize(
    ("texto", "idioma", "esperado"),
    [
        ("Visita Cuetzalan y Zacatlán", "es", ["cuetzalan", "zacatlan"]),
        ("Try Cholula and Atlixco", "en", ["cholula", "atlixco"]),
        ("Visitez Cholula puis Zacatlán", "fr", ["cholula", "zacatlan"]),
        ("Le centre historique de Puebla est classé", "fr", ["puebla"]),
        ("Puebla est un État", "fr", []),
        ("Explore the historic center of Puebla", "en", ["puebla"]),
    ],
)
def test_latinos(texto, idioma, esperado):
    assert [d for d, _ in ids(texto, idioma)] == esperado


def test_zh_puebla_estado_no_cuenta_como_capital():
    assert ids("普埃布拉州有很多小镇", "zh") == []


def test_zh_cholula_y_atlixco_por_terminos():
    r = ids("去聖佩德羅喬盧拉和阿特利斯科", "zh")
    assert ("cholula", "terminos") in r and ("atlixco", "terminos") in r


def test_el_extractor_agrega_lo_que_los_terminos_no_hallaron():
    r = ids("去奎察兰", "zh", extraidos=["cuetzalan", "puebla"])
    assert r == [("cuetzalan", "extractor"), ("puebla", "extractor")]


def test_el_extractor_no_duplica_lo_hallado_por_terminos():
    r = ids("Cholula 추천", "ko", extraidos=["cholula", "zacatlan"])
    assert r == [("cholula", "terminos"), ("zacatlan", "extractor")]


def test_orden_de_las_menciones():
    ms = menciones.menciones_de_respuesta("Zacatlán, luego Cuetzalan", "es", DESTINOS, TERMINOS)
    assert [(m.destino_id, m.orden) for m in ms] == [("zacatlan", 1), ("cuetzalan", 2)]


def test_leer_respuesta_del_extractor():
    salida = 'Claro:\n```json\n{"destinos": ["cuetzalan", "inventado", "cuetzalan", "puebla"]}\n```'
    assert menciones.leer_respuesta_extractor(salida, DESTINOS) == ["cuetzalan", "puebla"]
    assert menciones.leer_respuesta_extractor("sin json", DESTINOS) == []
    assert menciones.leer_respuesta_extractor("{roto", DESTINOS) == []


def test_extraer_usa_la_instruccion_con_el_catalogo():
    vistas = []

    def llamar(instruccion):
        vistas.append(instruccion)
        return '{"destinos": ["atlixco"]}'

    assert menciones.extraer("texto", DESTINOS, llamar) == ["atlixco"]
    assert "atlixco: Atlixco" in vistas[0] and "solo con JSON" in vistas[0]
