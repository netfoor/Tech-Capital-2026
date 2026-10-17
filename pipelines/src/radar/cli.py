"""Comandos del radar. Uso: `uv run radar --help`."""

from __future__ import annotations

import sys
from typing import Annotated

import pandas as pd
import typer

from radar import catalogo, config, fuentes
from radar.entregables import generar
from radar.exportar import paquete
from radar.indicadores import resumen, sectur_ot
from radar.radar import atencion, desempeno, indices

app = typer.Typer(no_args_is_help=True, add_completion=False, help=__doc__)
analisis = typer.Typer(no_args_is_help=True, help="Índices, brecha y cuadrantes (spec 008).")
app.add_typer(analisis, name="radar")
senales = typer.Typer(no_args_is_help=True, help="Señales de atención digital (specs 003 y 004).")
app.add_typer(senales, name="senales")
asistentes = typer.Typer(no_args_is_help=True, help="Auditoría de asistentes (spec 006).")
app.add_typer(asistentes, name="asistentes")
comentarios = typer.Typer(no_args_is_help=True, help="Clasificación de comentarios (spec 007).")
app.add_typer(comentarios, name="comentarios")


def _fallar_si(problemas: list[str], titulo: str) -> None:
    if problemas:
        typer.secho(f"{titulo}: {len(problemas)} problema(s)", fg=typer.colors.RED, err=True)
        for p in problemas[:30]:
            typer.echo(f"  - {p}", err=True)
        raise typer.Exit(code=1)
    typer.secho(f"{titulo}: correcto", fg=typer.colors.GREEN)


@app.command("fuentes")
def verificar_fuentes() -> None:
    """Comprueba que los archivos de fuentes existan y coincidan con su SHA-256."""
    _fallar_si(fuentes.verificar(), "Fuentes")


@app.command("catalogo")
def verificar_catalogo() -> None:
    """Valida el catálogo de destinos."""
    destinos = catalogo.cargar()
    _fallar_si(catalogo.validar(destinos), f"Catálogo ({len(destinos)} destinos)")


@app.command("indicadores")
def indicadores() -> None:
    """Ingiere el PDF del Observatorio Turístico y escribe las tablas curadas."""
    destinos = catalogo.cargar()
    pdf = fuentes.archivo(sectur_ot.FUENTE_ID)
    crudo = sectur_ot.leer_tabla(pdf)
    errores, huecos = sectur_ot.comprobar_acumulados(crudo)
    _fallar_si(errores, "Acumulados del PDF")
    for hueco in huecos:
        typer.secho(f"  Hueco en la fuente: {hueco}", fg=typer.colors.YELLOW)
    tabla = sectur_ot.a_tabla_larga(crudo, destinos)
    _fallar_si(sectur_ot.comprobar_coherencia(tabla), "Coherencia interna")

    salida = config.ruta(config.CURADO)
    salida.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(salida / "indicadores_oficiales_mensual.csv", index=False, float_format="%.4f")
    anual = resumen.anual(tabla)
    anual.to_csv(salida / "indicadores_oficiales_anual.csv", index=False, float_format="%.4f")
    factor = sectur_ot.factor_afluencia(tabla)
    factor.to_csv(salida / "factor_afluencia_por_centro.csv", index=False)

    typer.echo(
        f"{len(tabla):,} valores; {tabla['centro_ot'].nunique()} centros; "
        f"periodos {tabla['periodo'].min()} a {tabla['periodo'].max()}"
    )


@app.command("resumen")
def ver_resumen(anio: int = typer.Option(2025, help="Año completo a resumir")) -> None:
    """Imprime el resumen anual por destino (para revisar la evidencia)."""
    anual = pd.read_csv(config.ruta(config.CURADO, "indicadores_oficiales_anual.csv"))
    del_anio = anual[(anual["anio"] == anio) & (anual["meses"] == 12)]
    columnas = [
        "centro_ot",
        "afluencia_visitantes",
        "ocupacion_pct",
        "estadia_promedio_dias",
        "derrama_por_visitante_mxn",
        "cuartos_libres_por_dia",
    ]
    pd.set_option("display.width", 200)
    typer.echo(del_anio[columnas].round(2).to_string(index=False))
    p = resumen.participacion(anual, anio)
    pm = del_anio[
        del_anio["destino_id"].isin([d.destino_id for d in catalogo.cargar() if d.pueblo_magico])
    ]
    typer.echo(
        f"\nCapital: {p['capital_pct']:.1f} % de la afluencia estatal. "
        f"12 Pueblos Mágicos: {pm['afluencia_visitantes'].sum() / p['estado'] * 100:.1f} %."
    )


@senales.command("youtube")
def senales_youtube(
    sin_comentarios: bool = typer.Option(False, help="No descarga comentarios"),
) -> None:
    """Consulta YouTube y escribe `presencia_youtube.csv` y `videos_por_destino.csv`."""
    from radar.senales import youtube

    config.cargar_entorno()
    destinos = catalogo.cargar()
    consultas = youtube.cargar_consultas()
    unidades = youtube.comprobar_cuota(consultas, not sin_comentarios)
    typer.echo(f"Cuota estimada: {unidades} unidades de 10,000 diarias")
    cliente = youtube.Cliente()
    presencia, videos, comentarios = youtube.ejecutar(
        destinos, consultas, cliente, con_comentarios=not sin_comentarios
    )
    salida = config.ruta(config.CURADO)
    salida.mkdir(parents=True, exist_ok=True)
    presencia.to_csv(salida / "presencia_youtube.csv", index=False, float_format="%.4f")
    videos.to_csv(salida / "videos_por_destino.csv", index=False, float_format="%.4f")
    if not sin_comentarios:
        ruta = youtube.escribir_comentarios(comentarios)
        typer.echo(f"{len(comentarios)} comentarios en {ruta.relative_to(config.raiz())}")
    typer.echo(f"Cuota usada: {cliente.unidades} unidades; {len(videos)} destinos con video")


@senales.command("trends")
def senales_trends(
    geo: str = typer.Option("MX", help="Región de Google Trends"),
    desde: str = typer.Option("2017-01-01", help="Inicio de la serie (AAAA-MM-DD)"),
    pausa: float = typer.Option(60.0, help="Segundos de pausa entre lotes (y base de reintentos)"),
    desde_crudo: bool = typer.Option(
        False,
        "--desde-crudo",
        help="Rehace la tabla con lo guardado en data/crudo/trends/, sin red",
    ),
) -> None:
    """Consulta Google Trends y escribe `interes_busqueda_mensual.csv` (red residencial)."""
    from radar.senales import trends

    destinos = [d for d in catalogo.cargar() if d.pueblo_magico]
    if desde_crudo:
        lotes = trends.armar_lotes(trends.terminos_de_consulta(destinos))
        registros = trends.registros_guardados(geo)
        faltan = [lote.nombre for lote in lotes if lote.nombre not in registros]
        if faltan:
            typer.secho(f"Falta crudo de los lotes {', '.join(faltan)}", fg="red", err=True)
            raise typer.Exit(code=1)
        tabla = trends.tabla_curada(lotes, registros, geo)
    else:
        config.cargar_entorno()
        tabla = trends.ejecutar(destinos, geo=geo, desde=desde, pausa=pausa)
    vacios = trends.destinos_sin_senal(tabla)
    if vacios:
        typer.secho(f"Sin señal en todos los meses: {', '.join(vacios)}", fg="red", err=True)
        raise typer.Exit(code=1)
    salida = config.ruta(config.CURADO)
    salida.mkdir(parents=True, exist_ok=True)
    ruta = salida / "interes_busqueda_mensual.csv"
    if ruta.exists():  # conserva las otras regiones (MX alimenta el radar; US es complementaria)
        previa = pd.read_csv(ruta, dtype={"periodo": str})
        if "geo" in previa.columns:
            otras = previa[previa["geo"] != geo]
            tabla = pd.concat([otras, tabla], ignore_index=True)
    tabla = tabla.sort_values(["geo", "destino_id", "periodo"]).reset_index(drop=True)
    tabla.to_csv(ruta, index=False, float_format="%.4f")
    typer.echo(
        f"{tabla['destino_id'].nunique()} destinos; periodos {tabla['periodo'].min()} "
        f"a {tabla['periodo'].max()}; {len(tabla):,} filas"
    )


def _proveedores(nombres: list[str]):
    from radar.asistentes import proveedores

    return {n: proveedores.crear(n) for n in nombres}


def _parametros_corridas(proveedor, idioma, repeticiones, semilla):
    from radar.asistentes import corridas

    nombres = proveedor or ["openai", "gemini"]
    prov = _proveedores(nombres)
    prompts = corridas.cargar_prompts()
    idiomas = set(idioma) if idioma else None
    pendientes, total = corridas.plan(prompts, prov, repeticiones, semilla=semilla, idiomas=idiomas)
    return prov, pendientes, total


@asistentes.command("plan")
def asistentes_plan(
    proveedor: Annotated[list[str] | None, typer.Option(help="openai o gemini (repetible)")] = None,
    idioma: Annotated[
        list[str] | None, typer.Option(help="es, en, fr, ko o zh (repetible)")
    ] = None,
    repeticiones: Annotated[int, typer.Option(help="Repeticiones por prompt y proveedor")] = 10,
    semilla: Annotated[int, typer.Option(help="Semilla del orden aleatorio")] = 2026,
) -> None:
    """Cuenta las corridas pendientes y estima los tokens, sin llamar a ningún servicio."""
    from radar.asistentes import corridas

    config.cargar_entorno()
    _, pendientes, total = _parametros_corridas(proveedor, idioma, repeticiones, semilla)
    entrada, salida = corridas.estimar_tokens(len(pendientes))
    typer.echo(
        f"Plan: {total} corridas; hechas: {total - len(pendientes)}; pendientes: {len(pendientes)}"
    )
    typer.echo(f"Tokens estimados de lo pendiente: {entrada:,} de entrada y {salida:,} de salida")


@asistentes.command("correr")
def asistentes_correr(
    proveedor: Annotated[list[str] | None, typer.Option(help="openai o gemini (repetible)")] = None,
    idioma: Annotated[
        list[str] | None, typer.Option(help="es, en, fr, ko o zh (repetible)")
    ] = None,
    repeticiones: Annotated[int, typer.Option(help="Repeticiones por prompt y proveedor")] = 10,
    semilla: Annotated[int, typer.Option(help="Semilla del orden aleatorio")] = 2026,
    tope: Annotated[int | None, typer.Option(help="Máximo de corridas de esta ejecución")] = None,
    concurrencia: Annotated[int, typer.Option(help="Llamadas simultáneas")] = 1,
    max_segundos: Annotated[
        float | None, typer.Option(help="No iniciar corridas nuevas pasado este tiempo")
    ] = None,
) -> None:
    """Ejecuta las corridas pendientes y las guarda en data/crudo/asistentes/ (reanudable)."""
    from radar.asistentes import corridas

    config.cargar_entorno()
    prov, pendientes, total = _parametros_corridas(proveedor, idioma, repeticiones, semilla)
    destino = min(len(pendientes), tope) if tope else len(pendientes)
    typer.echo(f"{destino} corridas por ejecutar de {total} en el plan")
    hechas = 0
    for linea in corridas.ejecutar(
        pendientes,
        prov,
        tope=tope,
        semilla=semilla,
        concurrencia=concurrencia,
        limite_segundos=max_segundos,
    ):
        hechas += 1
        typer.echo(
            f"[{hechas}/{destino}] {linea['prompt_id']} {linea['proveedor']} "
            f"#{linea['repeticion']} busco={linea['busco']} "
            f"tokens={linea['tokens_entrada']}/{linea['tokens_salida']}"
        )


@asistentes.command("extraer")
def asistentes_extraer(
    concurrencia: Annotated[int, typer.Option(help="Llamadas simultáneas")] = 8,
) -> None:
    """Anota con un modelo las respuestas en ko y zh y guarda el resultado en caché."""
    from radar.asistentes import extractor, procesar

    config.cargar_entorno()
    destinos = catalogo.cargar()
    corridas = procesar.leer_corridas()
    por_hacer = len(extractor.pendientes(corridas, extractor.cargar_cache()))
    typer.echo(f"{por_hacer} respuestas por anotar")
    hechas = sum(
        1
        for _ in extractor.ejecutar(
            corridas, destinos, extractor.llamar_gemini(), concurrencia=concurrencia
        )
    )
    typer.echo(f"{hechas} anotadas")


@asistentes.command("muestra-menciones")
def asistentes_muestra_menciones() -> None:
    """Crea la muestra de 60 respuestas para validar a mano la detección de menciones (T006-11)."""
    from radar.asistentes import procesar, validacion

    corridas = procesar.leer_corridas()
    menciones: dict[str, list[str]] = {}
    tabla = pd.read_csv(config.ruta(config.CURADO, "asistentes_menciones.csv"))
    for fila in tabla.sort_values(["corrida_id", "orden"]).itertuples():
        menciones.setdefault(fila.corrida_id, []).append(fila.destino_id)
    nombres = {d.destino_id: d.nombre for d in catalogo.cargar()}
    filas = validacion.muestra(corridas, menciones, nombres)
    ruta = config.ruta(config.PRIVADO, "asistentes", "validacion_menciones.csv")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    if ruta.exists():
        typer.secho(
            f"Ya existe {ruta.relative_to(config.raiz())}; no se sobrescribe",
            fg=typer.colors.YELLOW,
        )
        raise typer.Exit(code=1)
    pd.DataFrame(filas, columns=validacion.COLUMNAS).to_csv(ruta, index=False)
    typer.echo(f"{len(filas)} respuestas en {ruta.relative_to(config.raiz())}")


@asistentes.command("validar-menciones")
def asistentes_validar_menciones() -> None:
    """Calcula precisión y exhaustividad de la detección con la muestra revisada."""
    import json

    from radar.asistentes import validacion

    ruta = config.ruta(config.PRIVADO, "asistentes", "validacion_menciones.csv")
    filas = pd.read_csv(ruta).fillna("").to_dict("records")
    r = validacion.metricas(filas)
    salida = config.ruta(config.CURADO, "validacion_menciones.json")
    salida.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    typer.echo(f"Precisión {r['precision']} · exhaustividad {r['exhaustividad']}")


@asistentes.command("procesar")
def asistentes_procesar() -> None:
    """Escribe las cinco tablas curadas de asistentes a partir de lo crudo."""
    from radar.asistentes import procesar

    tablas = procesar.ejecutar_y_escribir(catalogo.cargar())
    for nombre, tabla in tablas.items():
        typer.echo(f"{nombre}: {len(tabla):,} filas")


@analisis.command("calcular")
def calcular_radar() -> None:
    """Calcula `radar_destinos.csv` con los componentes que existan en `data/curado/`."""
    curado = config.ruta(config.CURADO)
    mensual = pd.read_csv(curado / "indicadores_oficiales_mensual.csv")
    universo = sorted(d.destino_id for d in catalogo.cargar() if d.pueblo_magico)
    tablas = atencion.cargar_tablas()
    tabla, cortes, disponibles = indices.calcular(mensual, tablas, universo)
    tabla.to_csv(curado / "radar_destinos.csv", index=False, float_format="%.4f")
    referencia = desempeno.calcular(mensual, ["puebla"])
    referencia.to_csv(curado / "radar_referencia.csv", index=False, float_format="%.4f")
    con_cuadrante = int(tabla["cuadrante"].notna().sum())
    typer.echo(
        f"{len(tabla)} destinos; componentes: {', '.join(disponibles) or 'ninguno'}; "
        f"con cuadrante: {con_cuadrante}"
    )
    if cortes["atencion"] is not None:
        typer.echo(
            f"Cortes: atención {cortes['atencion']:.1f}, desempeño {cortes['desempeno']:.1f}"
        )


@app.command("exportar")
def exportar(
    validar: Annotated[
        bool, typer.Option("--validar", help="Solo valida contra contratos, sin escribir.")
    ] = False,
) -> None:
    """Arma el paquete de datos del sitio, lo valida contra `contracts/` y lo firma (spec 009)."""
    armado = paquete.armar()
    _fallar_si(paquete.validar(armado), "Contratos")
    if validar:
        return
    destino = paquete.escribir(armado)
    typer.echo(f"Paquete escrito en {destino} ({len(armado)} archivos de datos)")


@app.command("entregables")
def entregables() -> None:
    """Genera el inventario de fuentes y las tablas de resultados de `docs/entregables/`."""
    cambiados = generar.generar()
    typer.echo("Actualizados: " + ", ".join(cambiados) if cambiados else "Sin cambios")


def main() -> None:  # pragma: no cover
    try:
        app()
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":  # pragma: no cover
    main()


def _leer_comentarios() -> list[dict]:
    import json

    ruta = config.ruta(config.PRIVADO, "comentarios", "youtube.jsonl")
    if not ruta.exists():
        typer.secho("Falta data/privado/comentarios/youtube.jsonl", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    return [json.loads(x) for x in ruta.read_text(encoding="utf-8").splitlines() if x.strip()]


@comentarios.command("muestra")
def comentarios_muestra(
    n: int = typer.Option(120, help="Tamaño de la muestra de validación"),
) -> None:
    """Crea `validacion.csv` (privado) estratificado por destino, para etiquetar a mano."""
    import random

    todos = _leer_comentarios()
    por_destino: dict[str, list[dict]] = {}
    for c in todos:
        por_destino.setdefault(c["destino_id"], []).append(c)
    azar = random.Random(7)
    cuota = max(1, n // len(por_destino))
    filas = []
    for _destino, items in sorted(por_destino.items()):
        filas += azar.sample(items, min(cuota, len(items)))
    ruta = config.ruta(config.PRIVADO, "comentarios", "validacion.csv")
    cols = ["video_id", "destino_id", "texto", "etiqueta_a", "etiqueta_b", "consenso"]
    pd.DataFrame(
        [
            {**{k: c[k] for k in cols[:3]}, "etiqueta_a": "", "etiqueta_b": "", "consenso": ""}
            for c in filas
        ]
    ).to_csv(ruta, index=False)
    typer.echo(f"{len(filas)} comentarios en {ruta.relative_to(config.raiz())}")


@comentarios.command("clasificar")
def comentarios_clasificar(
    solo_muestra: bool = typer.Option(False, help="Solo la muestra de validación"),
    proveedor: str = typer.Option("gemini", help="gemini u openai"),
) -> None:
    """Clasifica (reanudable) y escribe `opinion_agregada.csv` (n ≥ 5 por celda)."""
    from radar.asistentes import extractor
    from radar.comentarios import agregar, clasificar

    config.cargar_entorno()
    todos = _leer_comentarios()
    if solo_muestra:
        ruta_v = config.ruta(config.PRIVADO, "comentarios", "validacion.csv")
        claves = set(pd.read_csv(ruta_v)["texto"])
        todos = [c for c in todos if c["texto"] in claves]
    llamar = clasificar.llamar_openai() if proveedor == "openai" else extractor.llamar_gemini()
    cache = clasificar.clasificar(
        todos,
        llamar,
        config.ruta(config.PRIVADO, "comentarios", "clasificados.jsonl"),
        modelo=proveedor,
    )
    hechos = [cache[clasificar.clave(c)] for c in todos if clasificar.clave(c) in cache]
    typer.echo(f"{len(hechos)} de {len(todos)} comentarios clasificados")
    if solo_muestra:
        return
    tabla = agregar.opinion_agregada(hechos)
    salida = config.ruta(config.CURADO, "opinion_agregada.csv")
    tabla.to_csv(salida, index=False, float_format="%.4f")
    typer.echo(f"{len(tabla)} filas en {salida.relative_to(config.raiz())}")


@comentarios.command("validar")
def comentarios_validar() -> None:
    """κ entre personas, de la tercera etiqueta y del clasificador contra el consenso final."""
    import json

    from radar.comentarios import clasificar, validar

    df = pd.read_csv(config.ruta(config.PRIVADO, "comentarios", "validacion.csv")).fillna("")
    final = "consenso_final" if "consenso_final" in df.columns else "consenso"
    df = df[df[final] != ""]
    if len(df) < 30:
        typer.secho(
            "Faltan etiquetas: se necesitan al menos 30 filas", fg=typer.colors.RED, err=True
        )
        raise typer.Exit(code=1)
    cache = clasificar.cargar_cache(
        config.ruta(config.PRIVADO, "comentarios", "clasificados.jsonl")
    )
    filas = df.to_dict("records")
    faltan = [r for r in filas if clasificar.clave(r) not in cache]
    if faltan:
        typer.secho(
            f"{len(faltan)} filas sin clasificar con {clasificar.VERSION}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)
    pred = [cache[clasificar.clave(r)]["categoria"] for r in filas]
    informe = validar.informe(list(df["etiqueta_a"]), list(df["etiqueta_b"]), list(df[final]), pred)
    informe["version_prompt"] = clasificar.VERSION
    informe["consenso_usado"] = final
    if "etiqueta_c" in df.columns:
        informe["kappa_etiqueta_c_vs_consenso_humano"] = round(
            validar.kappa(list(df["etiqueta_c"]), list(df["consenso"])), 3
        )
        informe["cambios_consenso_final_vs_humano"] = int((df[final] != df["consenso"]).sum())
    ruta = config.ruta(config.CURADO, "validacion_clasificador.json")
    ruta.write_text(json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")
    typer.echo(
        f"κ personas {informe['kappa_entre_personas']} · "
        f"κ clasificador {informe['kappa_clasificador']} (umbral 0.6)"
    )
