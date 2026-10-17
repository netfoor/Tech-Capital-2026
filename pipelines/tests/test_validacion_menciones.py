from radar.asistentes import validacion


def corrida(i, idioma):
    return {"corrida_id": f"c{i}", "idioma": idioma, "proveedor": "p", "prompt": "q", "texto": "t"}


def test_muestra_estratificada_y_con_nombres():
    cs = [corrida(i, idioma) for idioma in ("es", "en") for i in range(20 if idioma == "es" else 5)]
    cs = [dict(c, corrida_id=f"{c['idioma']}{c['corrida_id']}") for c in cs]
    m = {"esc0": ["cholula", "atlixco"]}
    filas = validacion.muestra(cs, m, {"cholula": "Cholula", "atlixco": "Atlixco"}, por_idioma=12)
    assert sum(f["idioma"] == "es" for f in filas) == 12
    assert sum(f["idioma"] == "en" for f in filas) == 5
    assert all(set(f) == set(validacion.COLUMNAS) for f in filas)


def test_metricas():
    filas = [
        {"detectados": "Cholula | Atlixco", "sobran": "Atlixco", "faltan": "Cuetzalan"},
        {"detectados": "Zacatlán", "sobran": "", "faltan": ""},
        {"detectados": "", "sobran": "", "faltan": ""},
    ]
    r = validacion.metricas(filas)
    assert (r["verdaderos_positivos"], r["falsos_positivos"], r["falsos_negativos"]) == (2, 1, 1)
    assert r["precision"] == round(2 / 3, 3) and r["exhaustividad"] == round(2 / 3, 3)
