from radar import catalogo
from radar.texto import normalizar


def test_catalogo_valido():
    destinos = catalogo.cargar()
    assert catalogo.validar(destinos) == []


def test_doce_pueblos_magicos_con_coordenadas():
    pm = [d for d in catalogo.cargar() if d.pueblo_magico]
    assert len(pm) == 12
    assert {d.destino_id for d in pm} >= {"cuetzalan", "zacatlan", "cholula", "pahuatlan"}


def test_cholula_agrupa_dos_municipios():
    cholula = next(d for d in catalogo.cargar() if d.destino_id == "cholula")
    assert set(cholula.municipios_cvegeo) == {"21140", "21119"}


def test_normalizar_ignora_acentos_y_puntuacion():
    assert normalizar("Pahuatlán") == "pahuatlan"
    assert normalizar("Cd.Puebla") == "cd puebla"
    assert normalizar("  San Andrés   Cholula ") == "san andres cholula"
