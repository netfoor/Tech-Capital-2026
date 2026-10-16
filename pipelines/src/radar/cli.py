"""Comandos del radar. Uso: `uv run radar --help`."""

from __future__ import annotations

import sys
from typing import Annotated

import pandas as pd
import typer

from radar import catalogo, config, fuentes
from radar.indicadores import resumen, sectur_ot

app = typer.Typer(no_args_is_help=True, add_completion=False, help=__doc__)


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


corredor_app = typer.Typer(
    no_args_is_help=True,
    help="Catálogo del corredor Puebla–Cholula y de los Pueblos Mágicos (spec 012).",
)
app.add_typer(corredor_app, name="corredor")


@corredor_app.command("descargar")
def corredor_descargar(
    fuente: Annotated[
        list[str] | None,
        typer.Option("--fuente", help="Fuente a descargar: osm, sic o denue (se puede repetir)"),
    ] = None,
    rehacer: Annotated[
        bool, typer.Option(help="Vuelve a consultar Overpass aunque ya haya crudo del día")
    ] = False,
) -> None:
    """Con red: consulta Overpass, el SIC y el DENUE; guarda crudo, extractos y manifiestos."""
    from radar.corredor import descargar

    fecha = descargar.hoy()
    pendientes: list[str] = []
    for f in fuente or ["osm", "sic", "denue"]:
        typer.echo(f"Descargando {f}…")
        try:
            if f == "osm":
                descargar.descargar_osm(fecha, typer.echo, rehacer=rehacer)
            elif f == "sic":
                descargar.descargar_sic(fecha, typer.echo)
            elif f == "denue":
                descargar.descargar_denue(fecha, typer.echo)
            else:
                raise typer.BadParameter(f"Fuente desconocida: {f}")
        except typer.BadParameter:
            raise
        except Exception as e:  # una fuente caída no detiene a las demás
            pendientes.append(f"{f}: {e}")
            typer.secho(f"  {f} falló: {e}", fg=typer.colors.YELLOW, err=True)
    if pendientes:
        typer.secho(
            "Fuentes pendientes (documentar en la spec): " + "; ".join(pendientes),
            fg=typer.colors.YELLOW,
        )


@corredor_app.command("integrar")
def corredor_integrar() -> None:
    """Sin red: integra OSM, SIC y DENUE y escribe las tablas curadas de POI."""
    from radar.corredor import descargar, integrar

    problemas = [p for f in ("osm", "sic", "denue") for p in descargar.verificar_manifiesto(f)]
    _fallar_si(problemas, "Extractos")
    resultado = integrar.ejecutar()
    for linea in resultado.resumen():
        typer.echo(linea)


@corredor_app.command("reporte")
def corredor_reporte() -> None:
    """Sin red: escribe reports/calidad_datos.md y las cifras de docs/corredor_piloto.md."""
    from radar.corredor import calidad

    for ruta in calidad.escribir():
        typer.echo(f"Escrito {ruta}")


def main() -> None:  # pragma: no cover
    try:
        app()
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":  # pragma: no cover
    main()
