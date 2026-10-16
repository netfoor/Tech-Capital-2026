import pytest

from app.recommender.horarios import dias_cerrados, hora_a_minutos, parsear, ventanas


def test_24_7():
    h = parsear("24/7")
    assert h is not None
    assert all(h[d] == [(0, 1440)] for d in range(7))


def test_rango_de_dias_y_horas():
    h = parsear("Tu-Su 10:00-17:00")
    assert h[0] == []
    assert h[1] == [(600, 1020)]
    assert h[6] == [(600, 1020)]
    assert dias_cerrados(h) == [0]


def test_varias_reglas_y_rangos():
    h = parsear("Mo-Fr 10:00-14:00,16:00-19:00; Sa 10:00-14:00; Su off")
    assert h[2] == [(600, 840), (960, 1140)]
    assert h[5] == [(600, 840)]
    assert h[6] == []


def test_regla_posterior_sustituye():
    h = parsear("Mo-Su 09:00-18:00; Mo off")
    assert h[0] == []
    assert h[1] == [(540, 1080)]


def test_lista_de_dias_y_rango_que_da_la_vuelta():
    h = parsear("Sa-Mo 08:00-12:00")
    assert [d for d in range(7) if h[d]] == [0, 5, 6]
    h = parsear("Mo,We 10:00-12:00")
    assert [d for d in range(7) if h[d]] == [0, 2]


def test_horas_sin_dias_aplican_a_todos():
    h = parsear("09:00-17:00")
    assert all(h[d] == [(540, 1020)] for d in range(7))


def test_cruce_de_medianoche_se_recorta():
    h = parsear("Fr 18:00-02:00")
    assert h[4] == [(1080, 1440)]


@pytest.mark.parametrize(
    "texto",
    [
        None,
        "",
        "   ",
        "Mo-Su sunrise-sunset",
        "Tu-Su 10:00-17:00; PH off",
        "Jan-Mar Mo-Fr 09:00-17:00",
        "Mo-Fr 09:00+",
        'Mo-Fr 09:00-17:00 "con cita"',
        "Mo-Fr 25:00-26:00",
        "Lu-Vi 09:00-17:00",
        "Mo-Fr",
        "abierto",
    ],
)
def test_no_interpretables_devuelven_none(texto):
    assert parsear(texto) is None


def test_ventanas_por_dia_y_sin_dia_es_interseccion():
    h = parsear("Mo-Fr 09:00-17:00; Sa 10:00-14:00; Su off")
    assert ventanas(h, 5) == [(600, 840)]
    assert ventanas(h, 6) == []
    assert ventanas(h, None) == [(600, 840)]


def test_hora_a_minutos():
    assert hora_a_minutos("10:30") == 630
    with pytest.raises(ValueError):
        hora_a_minutos("25:00")
