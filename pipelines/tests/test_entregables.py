"""Documentos de entrega generados (T011-08): deben ser estables y coincidir con los datos."""

from radar.entregables import generar


def test_el_inventario_tiene_las_siete_partes_por_fuente():
    texto = generar.inventario()
    fuentes = texto.count("\n## ")
    for campo in ("Qué", "Por qué", "De dónde", "Cómo", "Calidad", "Preparación", "Evidencia"):
        assert texto.count(f"- **{campo}:**") == fuentes


def test_regenerar_no_cambia_el_archivo():
    assert generar.generar() in ([], ["04-inventario-fuentes.md", "09-resultados.md"])
    assert generar.generar() == []


def test_el_bloque_generado_reemplaza_solo_su_zona():
    texto = f"# T\n\n## A\n\n{generar.INICIO}\nviejo\n{generar.FIN}\n\n## B\n\nmanual\n"
    nuevo = generar.escribir_resultados(texto, "nuevo\n")
    assert "nuevo" in nuevo and "viejo" not in nuevo and "manual" in nuevo
