"""Capa anticorrupción de la API de YouTube (spec 004).

Se llama al API REST directamente. Todas las llamadas pasan por `Cliente`, que cuenta las
unidades de cuota y guarda lo crudo; los agregados se calculan sobre lo guardado, así que
pueden rehacerse sin red. Los comentarios se guardan sin autor ni canal.
"""

from __future__ import annotations

import json
import os
import statistics
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

import pandas as pd

from radar import catalogo, config

URL_BASE = "https://www.googleapis.com/youtube/v3"
COSTO_BUSQUEDA = 100
COSTO_LISTA = 1
TOPE_CUOTA = 8000
RESULTADOS_GENERICA = 25
RESULTADOS_ESPECIFICA = 10
VIDEOS_CON_COMENTARIOS = 3
COMENTARIOS_POR_VIDEO = 100
CAMPOS_PROHIBIDOS = ("author", "channel")


@dataclass(frozen=True)
class Consulta:
    consulta_id: str
    tipo: str  # generica | especifica
    texto: str
    idioma: str
    region: str

    @property
    def max_resultados(self) -> int:
        return RESULTADOS_GENERICA if self.tipo == "generica" else RESULTADOS_ESPECIFICA


def cargar_consultas(ruta: Path | None = None) -> list[Consulta]:
    ruta = ruta or config.ruta(config.REFERENCIA, "consultas_video.csv")
    tabla = pd.read_csv(ruta, dtype=str, keep_default_na=False)
    return [Consulta(**fila) for fila in tabla.to_dict("records")]


def estimar_cuota(consultas: list[Consulta], con_comentarios: bool = True) -> int:
    """Unidades que gastaría una corrida completa."""
    busquedas = len(consultas) * COSTO_BUSQUEDA
    videos = -(-sum(c.max_resultados for c in consultas) // 50) * COSTO_LISTA
    especificas = sum(1 for c in consultas if c.tipo == "especifica")
    comentarios = especificas * VIDEOS_CON_COMENTARIOS * COSTO_LISTA if con_comentarios else 0
    return busquedas + videos + comentarios


def comprobar_cuota(consultas: list[Consulta], con_comentarios: bool = True) -> int:
    unidades = estimar_cuota(consultas, con_comentarios)
    if unidades > TOPE_CUOTA:
        raise ValueError(f"La corrida gastaría {unidades} unidades; el tope es {TOPE_CUOTA}")
    return unidades


class Cliente:
    """Cliente mínimo. `http` se puede sustituir en pruebas."""

    def __init__(
        self,
        llave: str | None = None,
        http: Callable[[str, dict], dict] | None = None,
        carpeta: Path | None = None,
    ) -> None:
        self.llave = llave
        self._http = http or self._http_real
        self.carpeta = carpeta or config.ruta(config.CRUDO, "youtube")
        self.unidades = 0

    def _http_real(self, endpoint: str, params: dict) -> dict:  # pragma: no cover - requiere red
        import httpx

        respuesta = httpx.get(f"{URL_BASE}/{endpoint}", params=params, timeout=30)
        if respuesta.status_code != 200:
            try:
                motivo = respuesta.json()["error"]["errors"][0]["reason"]
            except (ValueError, KeyError, IndexError):
                motivo = respuesta.text[:120]
            raise ErrorApi(respuesta.status_code, motivo)
        return respuesta.json()

    def llamar(self, endpoint: str, costo: int, **params) -> dict:
        if self.llave is None:
            llave = os.environ.get("YOUTUBE_API_KEY")
            if not llave:
                raise RuntimeError("Falta YOUTUBE_API_KEY en .env")
            self.llave = llave
        self.unidades += costo
        return self._http(endpoint, {**params, "key": self.llave})

    def guardar(self, nombre: str, datos: dict) -> Path:
        self.carpeta.mkdir(parents=True, exist_ok=True)
        ruta = self.carpeta / nombre
        ruta.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
        return ruta


class ErrorApi(Exception):
    def __init__(self, estado: int, motivo: str) -> None:
        super().__init__(f"{estado} {motivo}")
        self.estado = estado
        self.motivo = motivo


def _sello(hoy: date) -> str:
    return hoy.strftime("%Y%m%d")


def buscar(cliente: Cliente, c: Consulta, hoy: date) -> dict:
    datos = cliente.llamar(
        "search",
        COSTO_BUSQUEDA,
        part="snippet",
        type="video",
        q=c.texto,
        regionCode=c.region,
        relevanceLanguage=c.idioma,
        maxResults=c.max_resultados,
    )
    cliente.guardar(f"yt-{c.consulta_id}-{_sello(hoy)}.json", datos)
    return datos


def estadisticas(cliente: Cliente, ids: list[str], hoy: date) -> dict[str, dict]:
    """`videos.list` en bloques de 50; devuelve {video_id: item}."""
    salida: dict[str, dict] = {}
    unicos = list(dict.fromkeys(ids))
    for i in range(0, len(unicos), 50):
        bloque = unicos[i : i + 50]
        datos = cliente.llamar(
            "videos", COSTO_LISTA, part="statistics,snippet", id=",".join(bloque)
        )
        cliente.guardar(f"yt-videos-{i // 50 + 1:02d}-{_sello(hoy)}.json", datos)
        for item in datos.get("items", []):
            salida[item["id"]] = item
    return salida


def id_de_video(item: dict) -> str:
    ident = item["id"]
    return ident["videoId"] if isinstance(ident, dict) else ident


def texto_de(item: dict) -> str:
    snip = item.get("snippet", {})
    return f"{snip.get('title', '')}\n{snip.get('description', '')}"


def destinos_mencionados(item: dict, idioma: str, destinos=None) -> set[str]:
    return {m.destino_id for m in catalogo.detectar(texto_de(item), idioma, destinos)}


def presencia(
    consultas: list[Consulta],
    resultados: dict[str, list[dict]],
    destinos,
    fecha: date,
) -> pd.DataFrame:
    """Proporción de los resultados de cada genérica que mencionan a cada destino."""
    filas = []
    for c in (x for x in consultas if x.tipo == "generica"):
        items = resultados.get(c.consulta_id, [])
        menciones = [destinos_mencionados(i, c.idioma, destinos) for i in items]
        n = len(items)
        for d in destinos:
            k = sum(1 for m in menciones if d.destino_id in m)
            filas.append(
                {
                    "destino_id": d.destino_id,
                    "consulta_id": c.consulta_id,
                    "n_resultados": n,
                    "k_menciones": k,
                    "proporcion": (k / n) if n else float("nan"),
                    "fecha_consulta": fecha.isoformat(),
                }
            )
    return pd.DataFrame(filas)


def _entero(valor) -> int:
    try:
        return int(valor)
    except (TypeError, ValueError):
        return 0


def _dias(publicado: str, hoy: date) -> int:
    momento = datetime.fromisoformat(publicado.replace("Z", "+00:00")).astimezone(UTC)
    return (hoy - momento.date()).days


def videos_por_destino(
    consultas: list[Consulta],
    resultados: dict[str, list[dict]],
    detalles: dict[str, dict],
    destinos,
    fecha: date,
) -> pd.DataFrame:
    """De los videos de la consulta específica, los que mencionan el destino y su audiencia."""
    filas = []
    for c in (x for x in consultas if x.tipo == "especifica"):
        destino_id = c.consulta_id.removeprefix("e-")
        destino = next((d for d in destinos if d.destino_id == destino_id), None)
        if destino is None:
            continue
        propios = []
        for item in resultados.get(c.consulta_id, []):
            if destino_id not in destinos_mencionados(item, c.idioma, destinos):
                continue
            det = detalles.get(id_de_video(item))
            if det is None:
                continue
            est = det.get("statistics", {})
            propios.append(
                (
                    _entero(est.get("viewCount")),
                    _entero(est.get("commentCount")),
                    _dias(det["snippet"]["publishedAt"], fecha),
                )
            )
        vistas = [p[0] for p in propios]
        filas.append(
            {
                "destino_id": destino_id,
                "consulta_id": c.consulta_id,
                "n_videos": len(propios),
                "vistas_total": sum(vistas),
                "vistas_mediana": statistics.median(vistas) if vistas else 0,
                "comentarios_total": sum(p[1] for p in propios),
                "antiguedad_dias_mediana": statistics.median([p[2] for p in propios])
                if propios
                else float("nan"),
                "fecha_consulta": fecha.isoformat(),
            }
        )
    return pd.DataFrame(filas)


def videos_principales(
    consultas: list[Consulta],
    resultados: dict[str, list[dict]],
    detalles: dict[str, dict],
    destinos,
) -> dict[str, list[str]]:
    """Los videos con más vistas de cada destino, entre los que lo mencionan."""
    salida: dict[str, list[str]] = {}
    for c in (x for x in consultas if x.tipo == "especifica"):
        destino_id = c.consulta_id.removeprefix("e-")
        candidatos = []
        for item in resultados.get(c.consulta_id, []):
            vid = id_de_video(item)
            det = detalles.get(vid)
            if det and destino_id in destinos_mencionados(item, c.idioma, destinos):
                candidatos.append((_entero(det.get("statistics", {}).get("viewCount")), vid))
        candidatos.sort(reverse=True)
        salida[destino_id] = [v for _, v in candidatos[:VIDEOS_CON_COMENTARIOS]]
    return salida


def comentario_anonimo(hilo: dict, video_id: str, destino_id: str) -> dict:
    """Solo texto, me gusta y fecha. Nunca el autor ni el canal."""
    s = hilo["snippet"]["topLevelComment"]["snippet"]
    return {
        "video_id": video_id,
        "destino_id": destino_id,
        "texto": s.get("textDisplay", ""),
        "me_gusta": _entero(s.get("likeCount")),
        "fecha": s.get("publishedAt", ""),
    }


def descargar_comentarios(
    cliente: Cliente, principales: dict[str, list[str]], hoy: date
) -> list[dict]:
    comentarios: list[dict] = []
    for destino_id, videos in principales.items():
        for vid in videos:
            try:
                datos = cliente.llamar(
                    "commentThreads",
                    COSTO_LISTA,
                    part="snippet",
                    videoId=vid,
                    maxResults=COMENTARIOS_POR_VIDEO,
                    order="relevance",
                    textFormat="plainText",
                )
            except ErrorApi as error:
                if error.motivo in {"commentsDisabled", "videoNotFound"}:
                    continue
                raise
            cliente.guardar(f"yt-comentarios-{vid}-{_sello(hoy)}.json", datos)
            comentarios += [comentario_anonimo(h, vid, destino_id) for h in datos.get("items", [])]
    return comentarios


def escribir_comentarios(comentarios: list[dict], ruta: Path | None = None) -> Path:
    ruta = ruta or config.ruta(config.PRIVADO, "comentarios", "youtube.jsonl")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", encoding="utf-8") as f:
        for c in comentarios:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    return ruta


def tiene_campos_prohibidos(registro: dict) -> bool:
    return any(k.lower().startswith(CAMPOS_PROHIBIDOS) for k in registro)


def ejecutar(
    destinos,
    consultas: list[Consulta] | None = None,
    cliente: Cliente | None = None,
    hoy: date | None = None,
    con_comentarios: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, list[dict]]:
    hoy = hoy or date.today()
    consultas = consultas or cargar_consultas()
    comprobar_cuota(consultas, con_comentarios)
    cliente = cliente or _cliente_por_defecto()
    resultados = {c.consulta_id: buscar(cliente, c, hoy).get("items", []) for c in consultas}
    ids = [id_de_video(i) for items in resultados.values() for i in items]
    detalles = estadisticas(cliente, ids, hoy)
    pres = presencia(consultas, resultados, destinos, hoy)
    vids = videos_por_destino(consultas, resultados, detalles, destinos, hoy)
    comentarios: list[dict] = []
    if con_comentarios:
        principales = videos_principales(consultas, resultados, detalles, destinos)
        comentarios = descargar_comentarios(cliente, principales, hoy)
    return pres, vids, comentarios


def _cliente_por_defecto() -> Cliente:
    config.cargar_entorno()
    return Cliente()
