import json

import pandas as pd
import pytest

from radar.comentarios import agregar, clasificar, limpieza, validar


def test_limpieza_quita_datos_personales():
    t = limpiar = limpieza.limpiar(
        "Hola @maria_22 mira https://x.com/a escríbeme a ana@mail.com o al 222 123 4567"
    )
    assert "@maria" not in t and "http" not in t and "ana@" not in t and "4567" not in t
    assert limpiar.startswith("Hola [usuario]")


def comentarios(n):
    return [{"video_id": "v", "destino_id": "cholula", "texto": f"texto {i}"} for i in range(n)]


def falso(salida_categoria="intencion"):
    llamadas = []

    def llamar(instruccion):
        llamadas.append(instruccion)
        ids = [
            int(x.split(" | ")[0]) for x in instruccion.splitlines() if x.split(" | ")[0].isdigit()
        ]
        return json.dumps([{"id": i, "categoria": salida_categoria, "friccion": None} for i in ids])

    return llamar, llamadas


def test_clasificar_reanuda_con_cache(tmp_path):
    llamar, llamadas = falso()
    ruta = tmp_path / "c.jsonl"
    cs = comentarios(45)
    assert len(clasificar.clasificar(cs, llamar, ruta, lote=20)) == 45
    assert len(llamadas) == 3
    clasificar.clasificar(cs, llamar, ruta, lote=20)
    assert len(llamadas) == 3


def test_salida_invalida_se_reintenta(tmp_path):
    ruta = tmp_path / "c.jsonl"
    assert clasificar.clasificar(comentarios(3), lambda _: "no es json", ruta) == {}
    llamar, _ = falso()
    assert len(clasificar.clasificar(comentarios(3), llamar, ruta)) == 3


def test_friccion_solo_si_categoria_friccion(tmp_path):
    def llamar(_):
        return '[{"id": 0, "categoria": "pregunta", "friccion": "precio"}]'

    r = clasificar.clasificar(comentarios(1), llamar, tmp_path / "c.jsonl")
    assert next(iter(r.values()))["friccion"] is None


def test_kappa():
    assert validar.kappa(["a", "b"], ["a", "b"]) == 1.0
    assert validar.kappa(["a", "a", "b", "b"], ["a", "b", "a", "b"]) == pytest.approx(0.0)
    with pytest.raises(ValueError):
        validar.kappa([], [])


def test_agregado_suprime_celdas_pequenas_y_no_tiene_texto():
    cs = (
        [{"destino_id": "d1", "categoria": "intencion", "friccion": None}] * 30
        + [{"destino_id": "d1", "categoria": "friccion", "friccion": "precio"}] * 5
        + [{"destino_id": "d1", "categoria": "pregunta", "friccion": None}] * 4
        + [{"destino_id": "d2", "categoria": "intencion", "friccion": None}] * 10
    )
    df = agregar.opinion_agregada(cs)
    assert isinstance(df, pd.DataFrame)
    assert (df["n"] >= 5).all()
    assert set(df["destino_id"]) == {"d1"}
    assert "pregunta" not in set(df["valor"])
    assert "texto" not in df.columns
