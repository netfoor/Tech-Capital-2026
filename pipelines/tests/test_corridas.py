import json
from datetime import date

import pytest

from radar.asistentes import corridas
from radar.asistentes.proveedores import RespuestaAsistente

PROMPTS = [
    corridas.Prompt("ES-C01", "es", "MX", "casual", "uno"),
    corridas.Prompt("ES-C02", "es", "MX", "casual", "dos"),
    corridas.Prompt("EN-C01", "en", "US", "casual", "three"),
]


class Falso:
    def __init__(self, nombre, modelo="m-1"):
        self.nombre = nombre
        self.modelo = modelo
        self.llamadas = []

    def consultar(self, texto):
        self.llamadas.append(texto)
        return RespuestaAsistente(texto=f"{self.nombre}: {texto}", modelo=self.modelo, busco=True)


def proveedores():
    return {"openai": Falso("openai"), "gemini": Falso("gemini", "g-1")}


def test_el_plan_cuenta_prompts_por_proveedores_por_repeticiones(tmp_path):
    pendientes, total = corridas.plan(PROMPTS, proveedores(), 3, carpeta=tmp_path)
    assert total == 3 * 2 * 3 == len(pendientes)


def test_el_orden_es_aleatorio_pero_reproducible(tmp_path):
    a, _ = corridas.plan(PROMPTS, proveedores(), 3, semilla=7, carpeta=tmp_path)
    b, _ = corridas.plan(PROMPTS, proveedores(), 3, semilla=7, carpeta=tmp_path)
    c, _ = corridas.plan(PROMPTS, proveedores(), 3, semilla=8, carpeta=tmp_path)
    assert a == b
    assert a != c


def test_filtra_por_idioma(tmp_path):
    pendientes, total = corridas.plan(PROMPTS, proveedores(), 2, carpeta=tmp_path, idiomas={"en"})
    assert total == 4
    assert {c.prompt.idioma for c in pendientes} == {"en"}


def test_ejecuta_escribe_jsonl_y_respeta_el_tope(tmp_path):
    p = proveedores()
    pendientes, _ = corridas.plan(PROMPTS, p, 1, carpeta=tmp_path)
    lineas = list(
        corridas.ejecutar(
            pendientes, p, tmp_path, tope=4, dormir=lambda s: None, hoy=lambda: date(2026, 10, 16)
        )
    )
    assert len(lineas) == 4
    archivo = tmp_path / "2026-10-16.jsonl"
    escritas = [json.loads(x) for x in archivo.read_text(encoding="utf-8").splitlines()]
    assert len(escritas) == 4
    primera = escritas[0]
    assert primera["brazo"] == "controlado" and primera["con_busqueda"] is True
    assert len(primera["corrida_id"]) == 12
    assert len(primera["sha256_respuesta"]) == 64


def test_reanudar_no_duplica(tmp_path):
    p = proveedores()
    pendientes, total = corridas.plan(PROMPTS, p, 2, carpeta=tmp_path)
    list(corridas.ejecutar(pendientes, p, tmp_path, tope=5, dormir=lambda s: None))
    restantes, total2 = corridas.plan(PROMPTS, p, 2, carpeta=tmp_path)
    assert total2 == total and len(restantes) == total - 5
    list(corridas.ejecutar(restantes, p, tmp_path, dormir=lambda s: None))
    final, _ = corridas.plan(PROMPTS, p, 2, carpeta=tmp_path)
    assert final == []
    lineas = [
        json.loads(x)
        for archivo in tmp_path.glob("*.jsonl")
        for x in archivo.read_text(encoding="utf-8").splitlines()
    ]
    claves = {(x["prompt_id"], x["proveedor"], x["modelo"], x["repeticion"]) for x in lineas}
    assert len(lineas) == len(claves) == total


def test_corrida_id_es_estable_y_depende_de_la_fecha():
    a = corridas.corrida_id("ES-C01", "openai", "m", 1, "2026-10-16")
    assert a == corridas.corrida_id("ES-C01", "openai", "m", 1, "2026-10-16")
    assert a != corridas.corrida_id("ES-C01", "openai", "m", 1, "2026-10-17")


def test_reintenta_429_y_5xx_pero_no_otros_errores():
    esperas = []

    class Inestable:
        nombre, modelo = "x", "m"
        n = 0

        def consultar(self, texto):
            self.n += 1
            if self.n == 1:
                raise RuntimeError("Error code: 429 - rate limit")
            if self.n == 2:
                raise RuntimeError("Error code: 503 unavailable")
            return RespuestaAsistente("ok", "m", False)

    r = corridas.consultar_con_reintentos(Inestable(), "t", espera_base=1, dormir=esperas.append)
    assert r.texto == "ok" and esperas == [1, 2]

    class Malo:
        nombre, modelo = "x", "m"

        def consultar(self, texto):
            raise RuntimeError("Error code: 400 prompt inválido")

    with pytest.raises(RuntimeError):
        corridas.consultar_con_reintentos(Malo(), "t", dormir=esperas.append)


def test_carga_solo_prompts_revisados(tmp_path):
    ruta = tmp_path / "p.csv"
    ruta.write_text(
        "prompt_id,idioma,mercado,tono,texto,origen,revisado\n"
        "A,es,MX,casual,hola,equipo,true\nB,ko,KR,casual,안녕,equipo,false\n",
        encoding="utf-8",
    )
    assert [p.prompt_id for p in corridas.cargar_prompts(ruta)] == ["A"]


def test_corpus_real_tiene_22_prompts_revisados():
    prompts = corridas.cargar_prompts()
    assert len(prompts) == 22
    por_idioma = {i: sum(p.idioma == i for p in prompts) for i in {p.idioma for p in prompts}}
    assert por_idioma == {"es": 9, "en": 4, "fr": 3, "ko": 3, "zh": 3}


def test_estimacion_de_tokens():
    assert corridas.estimar_tokens(10) == (15000, 5000)
