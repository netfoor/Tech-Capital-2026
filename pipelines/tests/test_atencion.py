import pandas as pd
import pytest

from radar.radar import atencion

UNIVERSO = ["a", "b", "c", "d"]


def busqueda():
    filas = []
    for destino, valor in {"a": 10.0, "b": 20.0, "c": 30.0, "d": 40.0}.items():
        for periodo in ("2025-06", "2025-07", "2026-06"):
            filas.append(
                {"destino_id": destino, "geo": "MX", "periodo": periodo, "interes_ajustado": valor}
            )
    # fuera del periodo de referencia o de otra región: no cuenta
    filas.append({"destino_id": "a", "geo": "MX", "periodo": "2024-01", "interes_ajustado": 999.0})
    filas.append({"destino_id": "a", "geo": "US", "periodo": "2026-01", "interes_ajustado": 999.0})
    return pd.DataFrame(filas)


def test_busqueda_media_en_el_periodo_y_percentil():
    r, disponibles, notas = atencion.calcular(
        {"busqueda": busqueda()}, UNIVERSO, "2025-07", "2026-06"
    )
    assert disponibles == ["busqueda"]
    assert r["atencion_busqueda_valor"].tolist() == [10.0, 20.0, 30.0, 40.0]
    assert r["atencion_busqueda_n"].tolist() == [2, 2, 2, 2]
    assert r["atencion_busqueda_pctl"].tolist() == pytest.approx([0, 100 / 3, 200 / 3, 100])
    assert notas == []


def test_componentes_sin_tabla_quedan_vacios_sin_imputar():
    r, disponibles, _ = atencion.calcular({"busqueda": busqueda()}, UNIVERSO, "2025-07", "2026-06")
    assert "atencion_panel_pctl" in r.columns
    assert r["atencion_panel_pctl"].isna().all()
    assert "panel" not in disponibles


def test_dos_componentes_disponibles():
    panel = pd.DataFrame(
        {
            "destino_id": UNIVERSO,
            "n_sesiones": [20] * 4,
            "k_sesiones": [1, 2, 3, 4],
            "presencia_pct": [5.0, 10.0, 15.0, 20.0],
        }
    )
    _, disponibles, _ = atencion.calcular(
        {"busqueda": busqueda(), "panel": panel}, UNIVERSO, "2025-07", "2026-06"
    )
    assert disponibles == ["busqueda", "panel"]


def test_video_es_proporcion_de_resultados():
    video = pd.DataFrame(
        {
            "destino_id": ["a", "a", "b", "b"],
            "consulta_id": ["q1", "q2", "q1", "q2"],
            "n_resultados": [10, 10, 10, 10],
            "k_menciones": [2, 4, 0, 1],
            "proporcion": [0.2, 0.4, 0.0, 0.1],
        }
    )
    r, disponibles, _ = atencion.calcular({"video": video}, ["a", "b"], "2025-07", "2026-06")
    assert r["atencion_video_valor"].tolist() == pytest.approx([30.0, 5.0])
    assert disponibles == ["video"]


def test_asistentes_prefiere_brazo_controlado_y_usa_total_si_falta():
    base = {"destino_id": UNIVERSO, "n": [100] * 4, "k": [1, 2, 3, 4]}
    tabla = pd.concat(
        [
            pd.DataFrame({**base, "segmento": "total", "visibilidad_pct": [9.0, 9.0, 9.0, 9.0]}),
            pd.DataFrame(
                {**base, "segmento": "brazo=controlado", "visibilidad_pct": [1.0, 2.0, 3.0, 4.0]}
            ),
        ]
    )
    r, _, notas = atencion.calcular({"asistentes": tabla}, UNIVERSO, "2025-07", "2026-06")
    assert r["atencion_asistentes_valor"].tolist() == [1.0, 2.0, 3.0, 4.0]
    assert notas == []
    solo_total = tabla[tabla["segmento"] == "total"]
    r, _, notas = atencion.calcular({"asistentes": solo_total}, UNIVERSO, "2025-07", "2026-06")
    assert r["atencion_asistentes_valor"].tolist() == [9.0] * 4
    assert any("total" in n for n in notas)


def test_componente_con_un_solo_destino_no_se_usa():
    panel = pd.DataFrame(
        {"destino_id": ["a"], "n_sesiones": [20], "k_sesiones": [3], "presencia_pct": [15.0]}
    )
    r, disponibles, notas = atencion.calcular({"panel": panel}, UNIVERSO, "2025-07", "2026-06")
    assert disponibles == []
    assert r["atencion_panel_pctl"].isna().all()
    assert any("panel" in n for n in notas)


def test_cargar_tablas_ignora_las_que_no_existen(tmp_path):
    (tmp_path / "presencia_panel.csv").write_text(
        "destino_id,n_sesiones,k_sesiones,presencia_pct,ic95_bajo,ic95_alto\n", encoding="utf-8"
    )
    assert list(atencion.cargar_tablas(tmp_path)) == ["panel"]
