import json

from radar import catalogo
from radar.asistentes import extractor


def corrida(i, idioma):
    return {"corrida_id": f"c{i}", "idioma": idioma, "texto": f"texto {i}"}


def test_solo_anota_ko_y_zh_sin_cache(tmp_path):
    cs = [corrida(1, "ko"), corrida(2, "zh"), corrida(3, "es"), corrida(4, "ko")]
    cache = {"c4": {"corrida_id": "c4", "destinos": []}}
    assert [c["corrida_id"] for c in extractor.pendientes(cs, cache)] == ["c1", "c2"]


def test_ejecutar_guarda_en_cache_y_no_repite(tmp_path):
    llamadas = []

    def llamar(instruccion):
        llamadas.append(instruccion)
        return '{"destinos": ["cholula"]}'

    cs = [corrida(1, "ko"), corrida(2, "zh")]
    destinos = catalogo.cargar()
    r = list(extractor.ejecutar(cs, destinos, llamar, tmp_path, concurrencia=2, modelo="m"))
    assert len(r) == 2 and len(llamadas) == 2
    guardado = [json.loads(x) for x in (tmp_path / "extraidos.jsonl").read_text().splitlines()]
    assert {g["corrida_id"] for g in guardado} == {"c1", "c2"}
    assert list(extractor.ejecutar(cs, destinos, llamar, tmp_path)) == []
    assert len(llamadas) == 2
