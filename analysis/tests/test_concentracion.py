"""Prueba de las medidas de concentración contra un cálculo a mano (T013-01)."""

import pandas as pd
import pytest

from concentracion import gini, hhi, participaciones

# Fixture pequeño: cuatro centros con 50, 30, 15 y 5 llegadas (total 100).
FIXTURE = pd.Series([50.0, 30.0, 15.0, 5.0], index=["capital", "cholula", "pm_a", "pm_b"])


def test_participacion_a_mano():
    # 30 / 100 = 0.30
    s = participaciones(FIXTURE)
    assert s["cholula"] == pytest.approx(0.30)
    assert s.sum() == pytest.approx(1.0)


def test_hhi_a_mano():
    # 0.50² + 0.30² + 0.15² + 0.05² = 0.25 + 0.09 + 0.0225 + 0.0025 = 0.365
    assert hhi(FIXTURE) == pytest.approx(0.365)


def test_hhi_extremos():
    assert hhi([1, 1, 1, 1]) == pytest.approx(0.25)
    assert hhi([7, 0, 0]) == pytest.approx(1.0)


def test_gini_a_mano():
    # Orden: 5, 15, 30, 50; Σ i·x = 5 + 30 + 90 + 200 = 325
    # G = 2·325 / (4·100) − 5/4 = 1.625 − 1.25 = 0.375
    assert gini(FIXTURE) == pytest.approx(0.375)
    assert gini([3, 3, 3]) == pytest.approx(0.0)


def test_valores_invalidos():
    with pytest.raises(ValueError):
        hhi([])
    with pytest.raises(ValueError):
        hhi([1, -1])
    with pytest.raises(ValueError):
        gini([0, 0])
