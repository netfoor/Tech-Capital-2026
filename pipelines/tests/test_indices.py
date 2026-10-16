import pandas as pd
import pytest

from radar import catalogo, config
from radar.radar import atencion, indices


def mensual_juguete(ocupaciones):
    """12 destinos con 24 meses; la ocupación de cada uno es la dada."""
    filas = []
    for destino, ocupacion in ocupaciones.items():
        for k in range(24):
            anio, mes = 2024 + (6 + k) // 12, (6 + k) % 12 + 1
            periodo = f"{anio}-{mes:02d}"
            for indicador, valor in (
                ("cuartos_disponibles", 100.0),
                ("cuartos_ocupados", float(ocupacion)),
                ("llegadas_turistas", 50.0),
            ):
                filas.append(
                    {
                        "destino_id": destino,
                        "nivel": "destino",
                        "periodo": periodo,
                        "indicador": indicador,
                        "valor": valor,
                    }
                )
    return pd.DataFrame(filas)


UNIVERSO = [f"d{i:02d}" for i in range(12)]
OCUPACION = {d: 30 + 3 * i for i, d in enumerate(UNIVERSO)}


def panel(valores):
    return pd.DataFrame(
        {
            "destino_id": UNIVERSO,
            "n_sesiones": 20,
            "k_sesiones": 1,
            "presencia_pct": valores,
        }
    )


def video(valores):
    return pd.DataFrame(
        {
            "destino_id": UNIVERSO,
            "consulta_id": "q",
            "n_resultados": 10,
            "k_menciones": valores,
            "proporcion": 0.0,
        }
    )


def test_clasificar_los_cuatro_cuadrantes():
    assert indices.clasificar(80, 80, 50, 50) == "consolidado"
    assert indices.clasificar(80, 20, 50, 50) == "atencion_sin_estancia"
    assert indices.clasificar(20, 80, 50, 50) == "demanda_poco_visible"
    assert indices.clasificar(20, 20, 50, 50) == "por_posicionar"
    assert indices.clasificar(50, 50, 50, 50) == "consolidado"


def test_con_dos_componentes_hay_indice_cuadrante_y_nota():
    mensual = mensual_juguete(OCUPACION)
    # atención alta en los primeros destinos (ocupación baja): atención sin estancia
    tablas = {
        "panel": panel([float(20 - i) for i in range(12)]),
        "video": video([12 - i for i in range(12)]),
    }
    tabla, cortes, disponibles = indices.calcular(mensual, tablas, UNIVERSO)
    assert disponibles == ["video", "panel"] or set(disponibles) == {"video", "panel"}
    assert len(tabla) == 12
    assert tabla["cuadrante"].notna().all()
    assert (tabla["componentes_disponibles"] == 2).all()
    assert cortes["desempeno"] == pytest.approx(50.0)
    assert tabla.loc[0, "indice_atencion"] == pytest.approx(100.0)
    assert tabla.loc[0, "indice_desempeno"] == pytest.approx(0.0)
    assert tabla.loc[0, "brecha"] == pytest.approx(100.0)
    assert tabla.loc[0, "cuadrante"] == "atencion_sin_estancia"
    assert tabla.loc[11, "cuadrante"] == "demanda_poco_visible"
    assert "Con solo 2 componentes" in tabla.loc[0, "notas"]
    # seis y seis en cada eje
    assert (tabla["indice_atencion"] >= cortes["atencion"]).sum() == 6


def test_con_un_componente_no_hay_indice():
    mensual = mensual_juguete(OCUPACION)
    tabla, _, disponibles = indices.calcular(mensual, {"panel": panel(list(range(12)))}, UNIVERSO)
    assert disponibles == ["panel"]
    assert tabla["indice_atencion"].isna().all()
    assert tabla["cuadrante"].isna().all()
    assert tabla["indice_desempeno"].notna().all()
    assert "Menos de 2 componentes" in tabla.loc[0, "notas"]


def test_sin_ningun_componente_solo_hay_desempeno():
    tabla, cortes, disponibles = indices.calcular(mensual_juguete(OCUPACION), {}, UNIVERSO)
    assert disponibles == []
    assert cortes["atencion"] is None
    assert tabla["ocupacion_12m"].notna().all()


def test_sensibilidad_marca_a_quien_cambia_al_omitir_un_componente():
    mensual = mensual_juguete(OCUPACION)
    # El tercer componente contradice a los otros dos en el destino 5.
    base = [float(20 - i) for i in range(12)]
    asistentes = pd.DataFrame(
        {
            "destino_id": UNIVERSO,
            "segmento": "brazo=controlado",
            "n": 100,
            "k": 1,
            "visibilidad_pct": [float(i) for i in range(12)],
            "ic95_bajo": 0.0,
            "ic95_alto": 1.0,
        }
    )
    tablas = {
        "panel": panel(base),
        "video": video([12 - i for i in range(12)]),
        "asistentes": asistentes,
    }
    tabla, _, disponibles = indices.calcular(mensual, tablas, UNIVERSO)
    assert len(disponibles) == 3
    assert tabla["sensible"].dtype == bool
    assert tabla["sensible"].any()


def test_catalogo_real_con_solo_desempeno():
    ruta = config.ruta(config.CURADO, "indicadores_oficiales_mensual.csv")
    if not ruta.exists():
        pytest.skip("Ejecuta `uv run radar indicadores` primero")
    mensual = pd.read_csv(ruta)
    universo = sorted(d.destino_id for d in catalogo.cargar() if d.pueblo_magico)
    tabla, _, disponibles = indices.calcular(mensual, atencion.cargar_tablas(), universo)
    assert len(tabla) == 12
    assert tabla["indice_desempeno"].notna().all()
    assert set(disponibles) <= set(atencion.COMPONENTES)
