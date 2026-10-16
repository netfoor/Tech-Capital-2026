import json
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from radar import catalogo
from radar.senales import trends

MUESTRA = Path(__file__).parent / "datos" / "trends_muestra.json"
TERMINOS = {d.destino_id: d.terminos_es[0] for d in catalogo.cargar()}


def serie(**columnas):
    n = len(next(iter(columnas.values())))
    periodos = [f"2025-{m:02d}" for m in range(1, n + 1)]
    return pd.DataFrame(columnas, index=pd.Index(periodos, name="periodo"))


def test_lotes_por_defecto_cubren_los_12_y_no_pasan_de_5_terminos():
    lotes = trends.armar_lotes(TERMINOS)
    assert [lote.nombre for lote in lotes] == ["A", "B", "C"]
    assert all(len(lote.ids) <= 5 for lote in lotes)
    assert all(lote.ids[0] == "cholula" for lote in lotes)
    cubiertos = {d for lote in lotes for d in lote.ids}
    pm = {d.destino_id for d in catalogo.cargar() if d.pueblo_magico}
    assert cubiertos == pm


def test_lote_con_mas_de_cinco_terminos_falla():
    plan = (("X", ("a", "b", "c", "d", "e"), None),)
    with pytest.raises(ValueError, match="más de 5"):
        trends.armar_lotes({k: k for k in "abcde"} | {"cholula": "c"}, plan=plan)


def test_destino_sin_termino_falla():
    with pytest.raises(ValueError, match="Faltan términos"):
        trends.armar_lotes({"cholula": "Cholula"})


def test_factor_de_reescalado_usa_la_media_del_rango():
    ref = pd.Series([100, 50, 50, 100])
    lote = pd.Series([50, 25, 25, 50])
    assert trends.factor_reescalado(ref, lote) == pytest.approx(2.0)
    with pytest.raises(ValueError):
        trends.factor_reescalado(ref, pd.Series([0, 0, 0, 0]))


def test_bajo_volumen():
    assert trends.es_bajo_volumen(pd.Series([0, 0, 1, 0]))
    assert not trends.es_bajo_volumen(pd.Series([5, 6, 0, 7]))


def test_dos_lotes_con_el_ancla_a_escalas_distintas_dan_series_iguales():
    # Misma verdad, pero el lote B vio el ancla a la mitad de escala.
    lotes = [
        trends.Lote("A", "c", ("x",), terminos={"c": "C", "x": "X"}),
        trends.Lote("B", "c", ("y",), terminos={"c": "C", "y": "Y"}),
    ]
    series = {
        "A": serie(c=[100, 80, 60, 40], x=[10, 20, 30, 40]),
        "B": serie(c=[50, 40, 30, 20], y=[5, 10, 15, 20]),
    }
    largo, detalle = trends.reescalar(lotes, series)
    assert detalle["B"]["factor"] == pytest.approx(2.0)
    y = largo[largo["destino_id"] == "y"]["interes_ajustado"].tolist()
    assert y == pytest.approx([10, 20, 30, 40])


def test_encadenamiento_con_ancla_de_segundo_nivel():
    lotes = [
        trends.Lote("A", "c", ("x", "q"), terminos={"c": "C", "x": "X", "q": "Q"}),
        trends.Lote("C", "c", ("q", "z"), ancla2="q", terminos={"c": "C", "q": "Q", "z": "Z"}),
    ]
    series = {
        "A": serie(c=[100, 100, 100, 100], x=[1, 1, 1, 1], q=[10, 20, 30, 40]),
        "C": serie(c=[0, 0, 0, 0], q=[20, 40, 60, 80], z=[4, 4, 8, 8]),
    }
    largo, detalle = trends.reescalar(lotes, series)
    assert detalle["C"]["ancla"] == "q"
    assert detalle["C"]["factor"] == pytest.approx(0.5)
    z = largo[largo["destino_id"] == "z"]["interes_ajustado"].tolist()
    assert z == pytest.approx([2, 2, 4, 4])


def test_un_destino_en_dos_lotes_conserva_el_de_referencia():
    lotes = [
        trends.Lote("A", "c", ("q",), terminos={"c": "C", "q": "Q"}),
        trends.Lote("B", "c", ("q",), terminos={"c": "C", "q": "Q"}),
    ]
    series = {
        "A": serie(c=[100, 100], q=[10, 20]),
        "B": serie(c=[50, 50], q=[99, 99]),
    }
    largo, _ = trends.reescalar(lotes, series)
    q = largo[largo["destino_id"] == "q"]
    assert q["lote"].unique().tolist() == ["A"]
    assert q["interes"].tolist() == [10, 20]


def test_consulta_id_y_timeframe():
    assert trends.consulta_id("MX", "A", date(2026, 10, 15)) == "trends-MX-A-20261015"
    assert trends.timeframe("2017-01-01", date(2026, 10, 15)) == "2017-01-01 2026-09-30"
    assert trends.ultimo_mes_cerrado(date(2026, 1, 3)) == date(2025, 12, 31)


def test_reintentos_con_espera_exponencial_ante_429():
    esperas = []
    intentos = {"n": 0}

    def consulta():
        intentos["n"] += 1
        if intentos["n"] < 3:
            raise RuntimeError("code 429 Too Many Requests")
        return pd.DataFrame({"a": [1]})

    r = trends.consultar_con_reintentos(consulta, espera_base=10, dormir=esperas.append)
    assert len(r) == 1
    assert esperas == [10, 20]


def test_otros_errores_no_se_reintentan():
    esperas = []

    def consulta():
        raise RuntimeError("500")

    with pytest.raises(RuntimeError):
        trends.consultar_con_reintentos(consulta, dormir=esperas.append)
    assert esperas == []


def test_se_rinde_tras_los_reintentos():
    def consulta():
        raise RuntimeError("429")

    with pytest.raises(RuntimeError):
        trends.consultar_con_reintentos(consulta, reintentos=2, dormir=lambda s: None)


def test_crudo_descarta_meses_parciales():
    lote = trends.Lote("A", "c", ("x",), terminos={"c": "C", "x": "X"})
    datos = pd.DataFrame(
        {"C": [100, 90], "X": [10, 5], "isPartial": [False, True]},
        index=pd.to_datetime(["2025-01-01", "2025-02-01"]),
    )
    r = trends.crudo_desde_tabla(lote, "MX", "2025-01-01 2025-02-28", datos, date(2026, 10, 15))
    assert [f["fecha"] for f in r["filas"]] == ["2025-01-01"]
    assert r["destinos"] == ["c", "x"]


def test_guardar_crudo_escribe_json(tmp_path):
    r = {"consulta_id": "trends-MX-A-20261015", "filas": []}
    ruta = trends.guardar_crudo(r, tmp_path)
    assert json.loads(ruta.read_text(encoding="utf-8"))["consulta_id"] == r["consulta_id"]


def test_integracion_con_la_respuesta_guardada():
    registros = {r["lote"]: r for r in json.loads(MUESTRA.read_text(encoding="utf-8"))}
    lotes = trends.armar_lotes(
        {
            d: registros[lote]["terminos"][registros[lote]["destinos"].index(d)]
            for lote in registros
            for d in registros[lote]["destinos"]
        }
    )
    tabla = trends.tabla_curada(lotes, registros, "MX")
    assert set(tabla["destino_id"]) == {d for lote in lotes for d in lote.ids}
    assert tabla["destino_id"].nunique() == 12
    assert list(tabla.columns)[:4] == ["destino_id", "termino", "geo", "periodo"]
    assert (tabla["geo"] == "MX").all()
    # Pahuatlán vive en el lote C, donde Cholula no registra nada: ancla de segundo nivel.
    pahuatlan = tabla[tabla["destino_id"] == "pahuatlan"]
    assert pahuatlan["ancla"].unique().tolist() == ["cuetzalan"]
    assert pahuatlan["interes_ajustado"].tolist() == pytest.approx([2, 2, 4, 4, 2, 2])
    # Cuetzalan sale del lote de referencia
    assert tabla[tabla["destino_id"] == "cuetzalan"]["consulta_id"].unique().tolist() == [
        "trends-MX-A-20261015"
    ]
    # Ningún destino con todos los meses en cero
    suma = tabla.groupby("destino_id")["interes"].sum()
    assert (suma > 0).all()
