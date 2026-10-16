"""Evaluación offline reproducible del recomendador inclusivo (spec 015, §10.1).

Compara el motor contra tres líneas base con 40 perfiles de solicitud
sintéticos (rotulados ``is_synthetic=true``) y 12 planes multi-día:

- violaciones de restricciones indispensables (objetivo: 0),
- cobertura de destinos alternativos,
- diversidad (zonas de 500 m y destinos distintos),
- tiempo usado contra disponible,
- latencia p50 y p95.

Catálogo: usa ``data/curado/poi.csv`` y ``data/curado/poi_accesibilidad.csv``
(contrato de la spec 012) si existen; si no, el catálogo sintético de
``backend/tests/datos/``.

Uso (desde ``backend/``)::

    uv run python ../analysis/02_eval_recomendador.py

Escribe ``reports/eval_recomendador.md``, ``reports/eval_recomendador.csv`` y
``reports/eval_recomendador_multidia.csv``. Todo es determinista salvo la
columna de latencia, que depende de la máquina.
"""

from __future__ import annotations

import csv
import random
import statistics
import sys
import time
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "backend"))

from app.recommender import (  # noqa: E402
    Restricciones,
    SolicitudMultidia,
    SolicitudRuta,
    planear_multidia,
    recomendar,
)
from app.recommender.baselines import BASELINES  # noqa: E402
from app.recommender.carga import cargar_catalogo  # noqa: E402
from app.recommender.config import CONFIG_DEFECTO, Config, Pesos  # noqa: E402
from app.recommender.elegibilidad import es_servicio  # noqa: E402
from app.recommender.geo import zona  # noqa: E402
from app.recommender.ranking import VOCABULARIO_INTERESES, IndiceTfidf, consulta  # noqa: E402
from app.recommender.tipos import RespuestaRuta  # noqa: E402
from app.recommender.verificador import INDISPENSABLES, verificar  # noqa: E402

SEMILLA = 2026
N_PERFILES = 40
N_MULTIDIA = 12
REPORTES = RAIZ / "reports"
# Ablaciones: el mismo motor sin un término del ranking, para medir su aporte.
ABLACIONES = {
    "motor_sin_diversidad": Config(pesos=Pesos(diversidad=0.0, repetir_zona=0.0)),
    "motor_sin_pertinencia": Config(pesos=Pesos(pertinencia=0.0)),
}
METODOS = ["motor", *BASELINES, *ABLACIONES]
NOMBRE_METODO = {
    "motor": "Motor inclusivo",
    "popularidad": "Baseline popularidad",
    "cercania": "Baseline cercanía",
    "popularidad_filtro_ingenuo": "Baseline popularidad + filtro ingenuo",
    "motor_sin_diversidad": "Ablación: motor sin diversidad",
    "motor_sin_pertinencia": "Ablación: motor sin pertinencia",
}


def cargar() -> tuple[list, str, bool]:
    poi = RAIZ / "data" / "curado" / "poi.csv"
    acc = RAIZ / "data" / "curado" / "poi_accesibilidad.csv"
    if poi.exists():
        pois = cargar_catalogo(poi, acc if acc.exists() else None)
        return pois, "data/curado/poi.csv", all(p.is_synthetic for p in pois)
    datos = RAIZ / "backend" / "tests" / "datos"
    pois = cargar_catalogo(datos / "poi_sintetico.csv", datos / "poi_accesibilidad_sintetico.csv")
    return pois, "backend/tests/datos/poi_sintetico.csv (SINTÉTICO)", True


def anclas(pois) -> list[tuple[float, float] | None]:
    """Puntos de partida: centroide de cada destino, más «sin punto de partida»."""
    por_destino: dict[str, list] = {}
    for p in pois:
        if not es_servicio(p):
            por_destino.setdefault(p.destino_id or "sin-destino", []).append(p)
    salida: list[tuple[float, float] | None] = [None]
    for d in sorted(por_destino):
        g = por_destino[d]
        salida.append(
            (round(sum(p.lat for p in g) / len(g), 6), round(sum(p.lon for p in g) / len(g), 6))
        )
    return salida


def perfiles(pois) -> list[SolicitudRuta]:
    rng = random.Random(SEMILLA)
    puntos = anclas(pois)
    intereses = sorted(VOCABULARIO_INTERESES)
    salida = [
        # Escena de valor §06.8: 4 h, sin escalones, descansos frecuentes y costo bajo.
        SolicitudRuta(
            horas_disponibles=4,
            punto_partida=puntos[1] if len(puntos) > 1 else None,
            intereses=["historia", "gastronomia"],
            presupuesto="bajo",
            restricciones=Restricciones(sin_escalones=True, descansos_cada_min=30),
            hora_inicio="10:00",
            dia_semana=5,
        )
    ]
    while len(salida) < N_PERFILES:
        salida.append(
            SolicitudRuta(
                horas_disponibles=rng.choice([2, 3, 4, 5, 6]),
                punto_partida=rng.choice(puntos),
                intereses=rng.sample(intereses, rng.randint(1, 3)),
                presupuesto=rng.choice([None, "gratis", "bajo", "medio", "alto"]),
                restricciones=Restricciones(
                    sin_escalones=rng.random() < 0.5,
                    banio_accesible=rng.random() < 0.3,
                    descansos_cada_min=rng.choice([30, 45, 60]) if rng.random() < 0.4 else None,
                    pendiente_max_pct=rng.choice([6.0, 8.0]) if rng.random() < 0.3 else None,
                ),
                hora_inicio=rng.choice(["09:00", "10:00", "12:00"]),
                dia_semana=rng.choice([None, 0, 1, 2, 3, 4, 5, 6]),
            )
        )
    return salida


REPETICIONES_LATENCIA = 3


def ejecutar(metodo: str, s: SolicitudRuta, pois) -> tuple[RespuestaRuta, float]:
    """Corre el método y devuelve la latencia mínima de 3 repeticiones (como timeit)."""
    tiempos = []
    for _ in range(REPETICIONES_LATENCIA):
        t0 = time.perf_counter()
        if metodo == "motor":
            r = recomendar(s, pois)
        elif metodo in ABLACIONES:
            r = recomendar(s, pois, ABLACIONES[metodo])
        else:
            r = BASELINES[metodo](s, pois)
        tiempos.append((time.perf_counter() - t0) * 1000)
    return r, min(tiempos)


def describir_restricciones(r: Restricciones) -> str:
    partes = []
    if r.sin_escalones:
        partes.append("sin_escalones")
    if r.banio_accesible:
        partes.append("banio_accesible")
    if r.descansos_cada_min:
        partes.append(f"descansos_{r.descansos_cada_min}")
    if r.pendiente_max_pct is not None:
        partes.append(f"pendiente_{r.pendiente_max_pct:g}")
    return "+".join(partes) or "ninguna"


def p95(valores: list[float]) -> float:
    if not valores:
        return 0.0
    orden = sorted(valores)
    return orden[min(len(orden) - 1, int(round(0.95 * (len(orden) - 1))))]


def evaluar_rutas(pois, solicitudes):
    por_id = {p.poi_id: p for p in pois}
    atractivos = [p for p in pois if not es_servicio(p)]
    indice = IndiceTfidf.construir(atractivos)
    # Calentamiento para no medir la importación.
    for m in METODOS:
        ejecutar(m, solicitudes[0], pois)
    filas = []
    respuestas = {}
    for i, s in enumerate(solicitudes):
        for m in METODOS:
            r, ms = ejecutar(m, s, pois)
            respuestas[(i, m)] = r
            v = verificar(r, s, por_id, CONFIG_DEFECTO)
            indisp = [x for x in v if x.tipo in INDISPENSABLES]
            lugares = [
                por_id[p.poi_id]
                for p in r.paradas
                if p.poi_id in por_id and not es_servicio(por_id[p.poi_id])
            ]
            terminos = {it: consulta(it) for it in s.intereses}
            coincide = [
                any(indice.similitud(ts, p.poi_id) > 0.05 for ts in terminos.values())
                for p in lugares
            ]
            n = len(lugares)
            filas.append(
                {
                    "perfil_id": f"perfil-{i + 1:02d}",
                    "is_synthetic": "true",
                    "metodo": m,
                    "horas": s.horas_disponibles,
                    "hora_inicio": s.hora_inicio,
                    "dia_semana": "" if s.dia_semana is None else s.dia_semana,
                    "con_punto_partida": s.punto_partida is not None,
                    "intereses": "+".join(s.intereses),
                    "presupuesto": s.presupuesto or "",
                    "restricciones": describir_restricciones(s.restricciones),
                    "n_paradas": n,
                    "ruta_vacia": n == 0,
                    "violaciones_indispensables": len(indisp),
                    "viol_sin_escalones": sum(x.tipo == "sin_escalones" for x in v),
                    "viol_pendiente": sum(x.tipo == "pendiente" for x in v),
                    "viol_banio": sum(x.tipo == "banio_accesible" for x in v),
                    "viol_descansos": sum(x.tipo == "descansos" for x in v),
                    "viol_tiempo": sum(x.tipo == "tiempo" for x in v),
                    "viol_horario": sum(x.tipo == "horario" for x in v),
                    "viol_presupuesto": sum(x.tipo == "presupuesto" for x in v),
                    "cobertura_alternativos": (
                        sum(p.es_destino_alternativo for p in lugares) / n if n else 0.0
                    ),
                    "zonas_distintas": len({zona(p.lat, p.lon) for p in lugares}),
                    "destinos_distintos": len({p.destino_id for p in lugares}),
                    "popularidad_media": (sum(p.popularidad for p in lugares) / n if n else 0.0),
                    "coincidencia_intereses": (sum(coincide) / n if n else 0.0),
                    "tiempo_usado_min": r.metricas["tiempo_usado_min"],
                    "tiempo_disponible_min": r.metricas["tiempo_disponible_min"],
                    "uso_tiempo": r.metricas["tiempo_usado_min"]
                    / r.metricas["tiempo_disponible_min"],
                    "n_alternativos_ofrecidos": len(r.alternativos),
                    "latencia_ms": ms,
                }
            )
    return filas, respuestas


def resumen_por_metodo(filas, filtro=lambda f: True):
    tabla = {}
    for m in METODOS:
        fs = [f for f in filas if f["metodo"] == m and filtro(f)]
        if not fs:
            continue
        no_vacias = [f for f in fs if not f["ruta_vacia"]]

        def media(clave, conjunto):
            return statistics.fmean(f[clave] for f in conjunto) if conjunto else 0.0

        tabla[m] = {
            "n": len(fs),
            "perfiles_con_violacion": sum(f["violaciones_indispensables"] > 0 for f in fs),
            "violaciones_indispensables": sum(f["violaciones_indispensables"] for f in fs),
            "viol_sin_escalones": sum(f["viol_sin_escalones"] for f in fs),
            "viol_pendiente": sum(f["viol_pendiente"] for f in fs),
            "viol_banio": sum(f["viol_banio"] for f in fs),
            "viol_descansos": sum(f["viol_descansos"] for f in fs),
            "viol_otras": sum(
                f["viol_tiempo"] + f["viol_horario"] + f["viol_presupuesto"] for f in fs
            ),
            "rutas_vacias": sum(f["ruta_vacia"] for f in fs),
            "paradas_media": media("n_paradas", fs),
            "cobertura_alternativos": media("cobertura_alternativos", no_vacias),
            "zonas_distintas": media("zonas_distintas", no_vacias),
            "destinos_distintos": media("destinos_distintos", no_vacias),
            "popularidad_media": media("popularidad_media", no_vacias),
            "coincidencia_intereses": media("coincidencia_intereses", no_vacias),
            "uso_tiempo": media("uso_tiempo", fs),
            "latencia_p50": statistics.median(f["latencia_ms"] for f in fs),
            "latencia_p95": p95([f["latencia_ms"] for f in fs]),
        }
    return tabla


def evaluar_multidia(pois):
    rng = random.Random(SEMILLA + 1)
    por_id = {p.poi_id: p for p in pois}
    atractivos = sorted(p.poi_id for p in pois if not es_servicio(p))
    filas = []
    for i in range(N_MULTIDIA):
        seleccion = rng.sample(atractivos, min(len(atractivos), rng.randint(8, 16)))
        sol = SolicitudMultidia(
            poi_ids=seleccion,
            dias=rng.choice([2, 3]),
            horas_por_dia=rng.choice([6, 8]),
            restricciones=Restricciones(
                sin_escalones=rng.random() < 0.5,
                banio_accesible=rng.random() < 0.3,
                descansos_cada_min=rng.choice([30, 45]) if rng.random() < 0.4 else None,
            ),
            dia_semana_inicio=rng.choice([None, 4, 5]),
        )
        t0 = time.perf_counter()
        r = planear_multidia(sol, pois)
        ms = (time.perf_counter() - t0) * 1000
        violaciones = 0
        for d, paradas in enumerate(r.dias):
            dia = None if sol.dia_semana_inicio is None else (sol.dia_semana_inicio + d) % 7
            s = SolicitudRuta(
                horas_disponibles=sol.horas_por_dia,
                restricciones=sol.restricciones,
                hora_inicio=sol.hora_inicio,
                dia_semana=dia,
            )
            rr = RespuestaRuta(paradas, [], [], "", [], {"linea_tiempo": r.metricas[
                "linea_tiempo_por_dia"][d]})  # fmt: skip
            violaciones += sum(x.tipo in INDISPENSABLES for x in verificar(rr, s, por_id))
        asignados = [p.poi_id for d in r.dias for p in d if p.poi_id in seleccion]
        m = r.metricas
        filas.append(
            {
                "plan_id": f"plan-{i + 1:02d}",
                "is_synthetic": "true",
                "n_seleccionados": len(seleccion),
                "dias": sol.dias,
                "horas_por_dia": sol.horas_por_dia,
                "restricciones": describir_restricciones(sol.restricciones),
                "n_asignados": m["n_asignados"],
                "n_no_asignados": m["n_no_asignados"],
                "duplicados": len(asignados) - len(set(asignados)),
                "violaciones_indispensables": violaciones,
                "distancia_total_m": m["distancia_total_m"],
                "n_asignados_orden_ingenuo": m["n_asignados_orden_ingenuo"],
                "distancia_orden_ingenuo_m": m["distancia_orden_ingenuo_m"],
                "distancia_por_lugar_m": (
                    m["distancia_total_m"] / m["n_asignados"] if m["n_asignados"] else 0.0
                ),
                "distancia_por_lugar_ingenuo_m": (
                    m["distancia_orden_ingenuo_m"] / m["n_asignados_orden_ingenuo"]
                    if m["n_asignados_orden_ingenuo"]
                    else 0.0
                ),
                "cruces_entre_dias": m["cruces_entre_dias"],
                "cruces_entre_dias_orden_ingenuo": m["cruces_entre_dias_orden_ingenuo"],
                "motivos_no_asignados": " | ".join(sorted({mo for _, mo in r.no_incluidos})),
                "latencia_ms": ms,
            }
        )
    return filas


def escribir_csv(ruta: Path, filas: list[dict]) -> None:
    with ruta.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]), lineterminator="\n")
        w.writeheader()
        for fila in filas:
            w.writerow({k: (f"{v:.4f}" if isinstance(v, float) else v) for k, v in fila.items()})


def _f(x: float, nd: int = 2) -> str:
    return f"{x:.{nd}f}"


def tabla_md(tabla: dict) -> list[str]:
    lineas = [
        "| Método | n | Perfiles con ≥1 violación | Violaciones indispensables "
        "(escalones / pendiente / baño / descansos) | Otras violaciones | Rutas vacías | "
        "Paradas (media) | Cobertura alternativos | Zonas distintas | Popularidad media | "
        "Coincidencia de intereses | Tiempo usado / disponible | Latencia p50 / p95 (ms) |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for m, t in tabla.items():
        lineas.append(
            f"| {NOMBRE_METODO[m]} | {t['n']} | {t['perfiles_con_violacion']} "
            f"({100 * t['perfiles_con_violacion'] / t['n']:.0f} %) | "
            f"{t['violaciones_indispensables']} ({t['viol_sin_escalones']} / "
            f"{t['viol_pendiente']} / {t['viol_banio']} / {t['viol_descansos']}) | "
            f"{t['viol_otras']} | {t['rutas_vacias']} | {_f(t['paradas_media'])} | "
            f"{_f(t['cobertura_alternativos'])} | {_f(t['zonas_distintas'])} | "
            f"{_f(t['popularidad_media'])} | {_f(t['coincidencia_intereses'])} | "
            f"{_f(t['uso_tiempo'])} | {_f(t['latencia_p50'], 1)} / {_f(t['latencia_p95'], 1)} |"
        )
    return lineas


def main() -> None:
    pois, fuente, sintetico = cargar()
    solicitudes = perfiles(pois)
    filas, respuestas = evaluar_rutas(pois, solicitudes)
    multidia = evaluar_multidia(pois)
    REPORTES.mkdir(exist_ok=True)
    escribir_csv(REPORTES / "eval_recomendador.csv", filas)
    escribir_csv(REPORTES / "eval_recomendador_multidia.csv", multidia)

    total = resumen_por_metodo(filas)
    con_restr = resumen_por_metodo(filas, lambda f: f["restricciones"] != "ninguna")
    escalones = resumen_por_metodo(filas, lambda f: "sin_escalones" in f["restricciones"])
    n_atr = sum(1 for p in pois if not es_servicio(p))
    n_serv = len(pois) - n_atr

    motor = [f for f in filas if f["metodo"] == "motor"]
    vacias = [f for f in motor if f["ruta_vacia"]]
    cortas = [f for f in motor if not f["ruta_vacia"] and f["uso_tiempo"] < 0.5]

    lineas = [
        "# Evaluación offline del recomendador inclusivo",
        "",
        "> **DATOS SINTÉTICOS DE DEMOSTRACIÓN.** Los perfiles de solicitud son sintéticos"
        + (" y el catálogo también." if sintetico else "; el catálogo es real."),
        "> No hay retroalimentación de usuarios reales todavía: estas cifras miden el"
        " comportamiento del algoritmo, no la satisfacción de visitantes.",
        "",
        f"- Fecha de corrida: {date.today().isoformat()}",
        f"- Catálogo: `{fuente}`: {n_atr} atractivos y {n_serv} servicios (baños).",
        f"- Perfiles de ruta: n = {len(solicitudes)} (semilla {SEMILLA}); planes multi-día:"
        f" n = {len(multidia)}.",
        "- Generado por `analysis/02_eval_recomendador.py`. Detalle por perfil en"
        " `reports/eval_recomendador.csv` y `reports/eval_recomendador_multidia.csv`.",
        "- Violaciones medidas por el verificador independiente"
        " (`backend/app/recommender/verificador.py`), el mismo para todos los métodos.",
        "",
        "## Rutas: motor contra baselines (todos los perfiles)",
        "",
        *tabla_md(total),
        "",
        f"## Solo perfiles con alguna restricción indispensable (n = {con_restr['motor']['n']})",
        "",
        *tabla_md(con_restr),
        "",
        f"## Solo perfiles con «sin escalones» (n = {escalones['motor']['n']})",
        "",
        *tabla_md(escalones),
        "",
        "## Cómo leer las columnas",
        "",
        "- **Violaciones indispensables**: paradas sin acceso sin escalones confiable, con"
        " pendiente no confiable o mayor, tramos de más de"
        f" {CONFIG_DEFECTO.intervalo_banio_min} min sin baño accesible y tramos continuos"
        " más largos que el intervalo de descanso pedido. Objetivo: 0.",
        "- **Otras violaciones**: tiempo total, horario verificable y presupuesto conocido.",
        "- **Cobertura alternativos**: proporción de paradas en destinos alternativos"
        " (media de rutas no vacías).",
        "- **Zonas distintas**: celdas de 500 m distintas por ruta.",
        "- **Coincidencia de intereses**: proporción de paradas cuyo texto coincide con algún"
        " interés según la misma similitud TF-IDF que usa el motor; favorece al motor por"
        " construcción y se reporta solo como control.",
        "- **Latencia**: mínimo de 3 corridas por perfil (criterio de `timeit`, que reduce el"
        " ruido de otros procesos) en una laptop de desarrollo; p50 y p95 sobre los perfiles."
        " No es determinista y cambia con la carga de la máquina.",
        "- **Ablaciones**: el mismo motor con el peso de diversidad (y la penalización por"
        " repetir zona) en 0, o con el peso de pertinencia en 0. Miden cuánto aporta cada"
        " término; las restricciones duras siguen activas.",
        "",
        "## Multi-día",
        "",
        "| Plan | Lugares | Días × h | Restricciones | Asignados (motor / ingenuo) |"
        " Distancia por lugar m (motor / ingenuo) | Cruces entre días (motor / ingenuo) |"
        " Duplicados | Violaciones |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for f in multidia:
        lineas.append(
            f"| {f['plan_id']} | {f['n_seleccionados']} | {f['dias']} × {f['horas_por_dia']} |"
            f" {f['restricciones']} | {f['n_asignados']} / {f['n_asignados_orden_ingenuo']} |"
            f" {f['distancia_por_lugar_m']:.0f} / {f['distancia_por_lugar_ingenuo_m']:.0f} |"
            f" {f['cruces_entre_dias']} / {f['cruces_entre_dias_orden_ingenuo']} |"
            f" {f['duplicados']} | {f['violaciones_indispensables']} |"
        )
    asign = sum(f["n_asignados"] for f in multidia)
    asign_ing = sum(f["n_asignados_orden_ingenuo"] for f in multidia)
    dist = sum(f["distancia_total_m"] for f in multidia)
    dist_ing = sum(f["distancia_orden_ingenuo_m"] for f in multidia)
    lineas += [
        "",
        f"Totales: {asign} lugares asignados contra {asign_ing} del orden ingenuo;"
        f" {dist / max(asign, 1):.0f} m por lugar asignado contra"
        f" {dist_ing / max(asign_ing, 1):.0f} m; cruces entre días"
        f" {sum(f['cruces_entre_dias'] for f in multidia)} contra"
        f" {sum(f['cruces_entre_dias_orden_ingenuo'] for f in multidia)};"
        f" duplicados {sum(f['duplicados'] for f in multidia)};"
        f" violaciones indispensables {sum(f['violaciones_indispensables'] for f in multidia)}.",
        "El orden ingenuo es la lista del usuario partida en días consecutivos, con la misma"
        " simulación (horarios, descansos y baños), sin reordenar.",
        "",
        "## Fallos y límites observados",
        "",
        f"- Rutas vacías del motor: {len(vacias)} de {len(motor)}.",
    ]
    for f in vacias:
        i = int(f["perfil_id"].split("-")[1]) - 1
        lineas.append(
            f"  - {f['perfil_id']} ({f['horas']} h, {f['restricciones']}, presupuesto"
            f" «{f['presupuesto'] or 'sin tope'}»): {respuestas[(i, 'motor')].explicacion}"
        )
    lineas.append(
        f"- Rutas del motor que usan menos de la mitad del tiempo: {len(cortas)} de {len(motor)}."
        " Suele pasar cuando la restricción deja pocos lugares con dato confiable: el motor"
        " prefiere una ruta corta a una que viole una necesidad."
    )
    for f in cortas[:8]:
        lineas.append(
            f"  - {f['perfil_id']}: {f['n_paradas']} parada(s), {f['tiempo_usado_min']} de"
            f" {f['tiempo_disponible_min']} min, restricciones {f['restricciones']},"
            f" presupuesto «{f['presupuesto'] or 'sin tope'}»."
        )
    m_t, p_t = total["motor"], total["popularidad"]
    lineas += [
        f"- Paradas por ruta: el motor arma {m_t['paradas_media']:.2f} en promedio contra"
        f" {p_t['paradas_media']:.2f} de la baseline de popularidad. La diferencia es el costo"
        " de no violar restricciones y de insertar descansos y baños.",
        "- La distancia es en línea recta × 1.3; la pendiente entre paradas no se mide.",
        "- El catálogo de esta corrida es sintético: las cifras no describen lugares reales.",
        "",
    ]
    (REPORTES / "eval_recomendador.md").write_text("\n".join(lineas), encoding="utf-8")
    print("\n".join(tabla_md(total)))
    print(f"Escrito en {REPORTES}")


if __name__ == "__main__":
    main()
