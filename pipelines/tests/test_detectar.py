import pytest

from radar import catalogo

DESTINOS = catalogo.cargar()
TERMINOS = {
    ("cuetzalan", "fr"): ("Cuetzalan",),
    ("zacatlan", "ko"): ("사카틀란",),
    ("cholula", "ko"): ("촐룰라",),
    ("cuetzalan", "zh"): ("奎察兰",),
    ("puebla", "zh"): ("普埃布拉市",),
}


def ids(texto: str, idioma: str = "es") -> list[str]:
    return [m.destino_id for m in catalogo.detectar(texto, idioma, DESTINOS, TERMINOS)]


@pytest.mark.parametrize(
    ("texto", "idioma", "esperado"),
    [
        ("Te recomiendo Cuetzalan y Zacatlán.", "es", ["cuetzalan", "zacatlan"]),
        ("Visit Zacatlan, then Cuetzalan.", "en", ["zacatlan", "cuetzalan"]),
        ("ZACATLÁN de las Manzanas es bonito", "es", ["zacatlan"]),
        ("zacatlan", "es", ["zacatlan"]),
        ("Pahuatlán, Puebla, tiene papel amate", "es", ["pahuatlan"]),
        ("Pahuatlan Mexico is lovely", "en", ["pahuatlan"]),
        ("Un día en Cuetzalan du Progrès", "fr", ["cuetzalan"]),
        ("Atlixco en primavera y Huejotzingo en carnaval", "es", ["atlixco", "huejotzingo"]),
        ("Teziutlán y Tlatlauquitepec", "es", ["teziutlan", "tlatlauquitepec"]),
        ("Tetela de Ocampo tiene bosques", "es", ["tetela-de-ocampo"]),
        ("Xicotepec de Juárez y Huauchinango", "es", ["xicotepec", "huauchinango"]),
        ("Chignahuapan vende esferas", "es", ["chignahuapan"]),
    ],
)
def test_detecta_en_alfabeto_latino(texto, idioma, esperado):
    assert ids(texto, idioma) == esperado


def test_puebla_sola_no_cuenta():
    assert ids("Quiero viajar a Puebla en diciembre") == []
    assert ids("El estado de Puebla tiene mucho que ofrecer", "es") == []


@pytest.mark.parametrize(
    "texto",
    [
        "Pasa un día en la ciudad de Puebla",
        "Puebla capital tiene buena comida",
        "El centro histórico de Puebla es patrimonio",
    ],
)
def test_puebla_con_calificativo_si_cuenta(texto):
    assert ids(texto) == ["puebla"]


def test_puebla_city_en_ingles():
    assert ids("Puebla city has great food", "en") == ["puebla"]


def test_gana_el_termino_mas_largo():
    menciones = catalogo.detectar("San Pedro Cholula es muy visitado", "es", DESTINOS, TERMINOS)
    assert len(menciones) == 1
    assert menciones[0].destino_id == "cholula"
    assert menciones[0].termino == "San Pedro Cholula"


def test_atlixco_puebla_no_se_confunde_con_la_capital():
    assert ids("Atlixco, Puebla") == ["atlixco"]


def test_limites_de_palabra():
    assert ids("Teziutlanes inventado") == []
    assert ids("xCuetzalanx") == []


def test_orden_de_aparicion_y_una_mencion_por_destino():
    menciones = catalogo.detectar(
        "Zacatlán, Cuetzalan, otra vez Zacatlán", "es", DESTINOS, TERMINOS
    )
    assert [m.destino_id for m in menciones] == ["zacatlan", "cuetzalan"]
    assert menciones[0].posicion < menciones[1].posicion


def test_texto_vacio():
    assert ids("") == []


def test_idioma_no_soportado():
    with pytest.raises(ValueError):
        catalogo.detectar("hola", "de", DESTINOS, TERMINOS)


def test_coreano_por_subcadena_exacta():
    assert ids("푸에블라 주의 사카틀란과 촐룰라를 추천합니다", "ko") == ["zacatlan", "cholula"]


def test_chino_por_subcadena_exacta():
    assert ids("普埃布拉市和奎察兰都值得去", "zh") == ["puebla", "cuetzalan"]


def test_ko_no_detecta_terminos_zh_ni_al_reves():
    assert ids("奎察兰", "ko") == []
    assert ids("사카틀란", "zh") == []


def test_ko_tambien_detecta_nombre_latino():
    assert ids("추천: Cuetzalan", "ko") == ["cuetzalan"]


def test_terminos_no_verificados_no_se_usan(tmp_path):
    ruta = tmp_path / "t.csv"
    ruta.write_text(
        "destino_id,idioma,termino,origen,verificado\n"
        "atlixco,ko,아틀릭스코,https://ko.wikipedia.org/wiki/x,false\n",
        encoding="utf-8",
    )
    assert catalogo.cargar_terminos_idiomas(ruta) == {}


def test_catalogo_real_de_terminos_carga():
    terminos = catalogo.cargar_terminos_idiomas()
    assert all(isinstance(v, tuple) for v in terminos.values())


def test_terminos_idiomas_cubren_13_destinos_en_3_idiomas_con_origen():
    import csv

    from radar import config

    ruta = config.ruta(config.REFERENCIA, "terminos_idiomas.csv")
    filas = list(csv.DictReader(ruta.open(encoding="utf-8")))
    assert len(filas) == 39
    assert {f["idioma"] for f in filas} == {"fr", "ko", "zh"}
    assert {f["destino_id"] for f in filas} <= {d.destino_id for d in DESTINOS}
    assert all(f["origen"].strip() and f["termino"].strip() for f in filas)
    assert all(f["verificado"] in {"true", "false"} for f in filas)
