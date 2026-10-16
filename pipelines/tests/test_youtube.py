import json
from datetime import date
from pathlib import Path

import pytest

from radar import catalogo
from radar.senales import youtube

MUESTRA = json.loads((Path(__file__).parent / "datos" / "youtube_muestra.json").read_text("utf-8"))
HOY = date(2026, 10, 16)
DESTINOS = catalogo.cargar()


@pytest.fixture(scope="module")
def consultas():
    return youtube.cargar_consultas()


def test_consultas_del_protocolo(consultas):
    es = [c for c in consultas if c.tipo == "generica" and c.idioma == "es"]
    en = [c for c in consultas if c.tipo == "generica" and c.idioma == "en"]
    especificas = [c for c in consultas if c.tipo == "especifica"]
    assert len(es) == 4 and len(en) == 2 and len(especificas) == 13
    pm = {d.destino_id for d in DESTINOS if d.pueblo_magico} | {"puebla"}
    assert {c.consulta_id.removeprefix("e-") for c in especificas} == pm


def test_la_cuota_estimada_cabe_y_el_tope_se_respeta(consultas):
    unidades = youtube.estimar_cuota(consultas)
    assert unidades == 1900 + 6 + 39
    assert youtube.comprobar_cuota(consultas) == unidades
    demasiadas = consultas * 5
    with pytest.raises(ValueError, match="tope"):
        youtube.comprobar_cuota(demasiadas)


def test_presencia_cuenta_destinos_en_titulo_y_descripcion(consultas):
    tabla = youtube.presencia(consultas, MUESTRA["resultados"], DESTINOS, HOY)
    fila = tabla[(tabla.destino_id == "cholula") & (tabla.consulta_id == "g-es-1")].iloc[0]
    assert (fila.n_resultados, fila.k_menciones) == (3, 2)
    assert fila.proporcion == pytest.approx(2 / 3)
    descripcion = tabla[(tabla.destino_id == "cuetzalan") & (tabla.consulta_id == "g-es-2")].iloc[0]
    assert descripcion.k_menciones == 1  # solo en la descripción
    assert set(tabla.fecha_consulta) == {"2026-10-16"}


def test_videos_por_destino_ignora_homonimos_y_agrega(consultas):
    tabla = youtube.videos_por_destino(
        consultas, MUESTRA["resultados"], MUESTRA["detalles"], DESTINOS, HOY
    )
    cuetzalan = tabla[tabla.destino_id == "cuetzalan"].iloc[0]
    assert cuetzalan.n_videos == 3  # b3 no menciona al destino
    assert cuetzalan.vistas_total == 6300
    assert cuetzalan.vistas_mediana == 1000
    assert cuetzalan.comentarios_total == 63


def test_videos_principales_son_los_mas_vistos_del_destino(consultas):
    principales = youtube.videos_principales(
        consultas, MUESTRA["resultados"], MUESTRA["detalles"], DESTINOS
    )
    assert principales["cuetzalan"] == ["b2", "b1", "b4"]
    assert "b3" not in principales["cuetzalan"]


def test_comentarios_sin_autor_ni_canal():
    registros = [youtube.comentario_anonimo(h, "b2", "cuetzalan") for h in MUESTRA["hilos"]]
    assert len(registros) == 2
    for r in registros:
        assert set(r) == {"video_id", "destino_id", "texto", "me_gusta", "fecha"}
        assert not youtube.tiene_campos_prohibidos(r)
    assert youtube.tiene_campos_prohibidos({"authorDisplayName": "x"})
    assert youtube.tiene_campos_prohibidos({"channelId": "x"})


def test_ejecutar_con_cliente_falso_guarda_crudo_y_cuenta_cuota(tmp_path, consultas):
    llamadas = []

    def http(endpoint, params):
        llamadas.append(endpoint)
        if endpoint == "search":
            ident = next(
                (
                    k
                    for k, c in {c.consulta_id: c for c in consultas}.items()
                    if c.texto == params["q"]
                )
            )
            return {"items": MUESTRA["resultados"].get(ident, [])}
        if endpoint == "videos":
            return {
                "items": [
                    {"id": i, **d}
                    for i, d in MUESTRA["detalles"].items()
                    if i in params["id"].split(",") and d
                ]
            }
        return {"items": MUESTRA["hilos"]}

    cliente = youtube.Cliente(llave="x", http=http, carpeta=tmp_path)
    pres, vids, comentarios = youtube.ejecutar(
        DESTINOS, consultas, cliente, HOY, con_comentarios=True
    )
    assert llamadas.count("search") == 19
    assert cliente.unidades >= 1900
    assert list(tmp_path.glob("yt-g-es-1-20261016.json"))
    assert not pres.empty and not vids.empty
    assert comentarios and all(not youtube.tiene_campos_prohibidos(c) for c in comentarios)
    destino_ids = {c["destino_id"] for c in comentarios}
    assert "cuetzalan" in destino_ids


def test_comentarios_desactivados_no_rompen_la_corrida(tmp_path):
    def http(endpoint, params):
        raise youtube.ErrorApi(403, "commentsDisabled")

    cliente = youtube.Cliente(llave="x", http=http, carpeta=tmp_path)
    assert youtube.descargar_comentarios(cliente, {"cuetzalan": ["b1"]}, HOY) == []
