"""Comandos del radar. Uso: `uv run radar --help`."""

from __future__ import annotations

import sys

import pandas as pd
import typer

from radar import catalogo, config, fuentes
from radar.indicadores import resumen, sectur_ot
from radar.radar import atencion, indices

app = typer.Typer(no_args_is_help=True, add_completion=False, help=__doc__)
analisis = typer.Typer(no_args_is_help=True, help="Índices, brecha y cuadrantes (spec 008).")
app.add_typer(analisis, name="radar")


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


@analisis.command("calcular")
def calcular_radar() -> None:
    """Calcula `radar_destinos.csv` con los componentes que existan en `data/curado/`."""
    curado = config.ruta(config.CURADO)
    mensual = pd.read_csv(curado / "indicadores_oficiales_mensual.csv")
    universo = sorted(d.destino_id for d in catalogo.cargar() if d.pueblo_magico)
    tablas = atencion.cargar_tablas()
    tabla, cortes, disponibles = indices.calcular(mensual, tablas, universo)
    tabla.to_csv(curado / "radar_destinos.csv", index=False, float_format="%.4f")
    con_cuadrante = int(tabla["cuadrante"].notna().sum())
    typer.echo(
        f"{len(tabla)} destinos; componentes: {', '.join(disponibles) or 'ninguno'}; "
        f"con cuadrante: {con_cuadrante}"
    )
    if cortes["atencion"] is not None:
        typer.echo(
            f"Cortes: atención {cortes['atencion']:.1f}, desempeño {cortes['desempeno']:.1f}"
        )


def main() -> None:  # pragma: no cover
    try:
        app()
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":  # pragma: no cover
    main()
