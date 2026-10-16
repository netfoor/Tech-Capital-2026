import pytest

from radar.comun.estadistica import mediana, percentiles, wilson


def test_percentiles_sin_empates():
    assert percentiles([10, 20, 30]) == [0.0, 50.0, 100.0]


def test_percentiles_con_empates_promedian_rango():
    # rangos 1, 2.5, 2.5, 4 con n = 4 -> (rango-1)/3*100
    p = percentiles([5, 7, 7, 9])
    assert p[0] == 0.0 and p[3] == 100.0
    assert p[1] == p[2] == pytest.approx(50.0)


def test_percentiles_todos_iguales_quedan_en_el_medio():
    assert percentiles([3, 3, 3, 3]) == [50.0, 50.0, 50.0, 50.0]


def test_percentiles_con_doce_valores():
    p = percentiles(list(range(12)))
    assert p[0] == 0.0 and p[-1] == 100.0
    assert p[6] == pytest.approx(6 / 11 * 100)


def test_percentiles_ignoran_nulos_y_conservan_posicion():
    p = percentiles([None, 1.0, float("nan"), 3.0, 2.0])
    assert p == [None, 0.0, None, 100.0, 50.0]


def test_percentiles_con_menos_de_dos_valores_no_hay():
    assert percentiles([4.0]) == [None]
    assert percentiles([]) == []
    assert percentiles([None, 2.0]) == [None, None]


def test_mediana():
    assert mediana([1, 3, 2]) == 2
    assert mediana([1, 2, 3, 4]) == 2.5
    with pytest.raises(ValueError):
        mediana([])


def test_wilson_valor_conocido():
    # 8/10 al 95 %: (0.490, 0.943) según la fórmula de Wilson
    bajo, alto = wilson(8, 10)
    assert bajo == pytest.approx(49.0, abs=0.2)
    assert alto == pytest.approx(94.3, abs=0.2)


def test_wilson_extremos_dentro_de_rango():
    bajo, alto = wilson(0, 20)
    assert bajo == 0.0 and 0 < alto < 20
    bajo, alto = wilson(20, 20)
    assert alto == 100.0 and 80 < bajo < 100


def test_wilson_sin_observaciones():
    assert wilson(0, 0) == (0.0, 100.0)


def test_wilson_valida_entradas():
    with pytest.raises(ValueError):
        wilson(5, 3)


def test_wilson_se_estrecha_con_mas_datos():
    a = wilson(5, 10)
    b = wilson(50, 100)
    assert (b[1] - b[0]) < (a[1] - a[0])
