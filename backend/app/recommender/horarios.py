"""Parser conservador de ``opening_hours`` de OpenStreetMap.

Solo interpreta el subconjunto frecuente: ``24/7``, días (``Mo``…``Su``,
rangos y listas), rangos de horas separados por coma, ``off`` y ``closed``.
Cualquier otra cosa (feriados ``PH``, meses, ``sunrise``, comentarios, ``+``)
hace que el horario completo se considere **no interpretable**: el lugar no
se descarta, se marca «horario sin verificar».
"""

from __future__ import annotations

import re

Horario = dict[int, list[tuple[int, int]]]

DIAS = {"mo": 0, "tu": 1, "we": 2, "th": 3, "fr": 4, "sa": 5, "su": 6}
NOMBRES_DIA = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")

_RE_HORA = re.compile(r"^(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})$")
_RE_DIA = re.compile(r"^([A-Za-z]{2})(?:\s*-\s*([A-Za-z]{2}))?$")


def _minutos(h: str, m: str) -> int | None:
    hh, mm = int(h), int(m)
    if hh > 24 or mm > 59 or (hh == 24 and mm != 0):
        return None
    return hh * 60 + mm


def _parsear_dias(texto: str) -> list[int] | None:
    dias: list[int] = []
    for parte in texto.split(","):
        coincide = _RE_DIA.match(parte.strip())
        if not coincide:
            return None
        ini = DIAS.get(coincide.group(1).lower())
        fin = DIAS.get(coincide.group(2).lower()) if coincide.group(2) else ini
        if ini is None or fin is None:
            return None
        d = ini
        while True:
            if d not in dias:
                dias.append(d)
            if d == fin:
                break
            d = (d + 1) % 7
    return dias


def _parsear_horas(texto: str) -> list[tuple[int, int]] | None:
    rangos: list[tuple[int, int]] = []
    for parte in texto.split(","):
        coincide = _RE_HORA.match(parte.strip())
        if not coincide:
            return None
        ini = _minutos(coincide.group(1), coincide.group(2))
        fin = _minutos(coincide.group(3), coincide.group(4))
        if ini is None or fin is None:
            return None
        if fin <= ini:
            # Cruza la medianoche: para rutas diurnas se recorta a las 24:00.
            fin = 24 * 60
        rangos.append((ini, fin))
    return sorted(rangos)


def parsear(texto: str | None) -> Horario | None:
    """Devuelve {día: [(inicio_min, fin_min), …]} o ``None`` si no se interpreta."""
    if texto is None:
        return None
    texto = texto.strip()
    if not texto:
        return None
    if texto == "24/7":
        return {d: [(0, 24 * 60)] for d in range(7)}
    horario: Horario = {d: [] for d in range(7)}
    for regla in texto.split(";"):
        regla = regla.strip()
        if not regla:
            continue
        partes = regla.split(None, 1)
        dias = _parsear_dias(partes[0]) if re.match(r"^[A-Za-z]{2}\b", partes[0]) else None
        if dias is not None:
            if len(partes) < 2:
                return None
            resto = partes[1].strip()
        else:
            if re.match(r"^[A-Za-z]", partes[0]):
                return None  # PH, meses, sunrise, etc.
            dias = list(range(7))
            resto = regla
        if resto.lower() in {"off", "closed"}:
            rangos: list[tuple[int, int]] = []
        else:
            rangos = _parsear_horas(resto)
            if rangos is None:
                return None
        for d in dias:
            horario[d] = list(rangos)
    return horario


def ventanas(horario: Horario, dia: int | None) -> list[tuple[int, int]]:
    """Ventanas de apertura para un día. Sin día: intersección de los días que abre."""
    if dia is not None:
        return list(horario.get(dia % 7, []))
    abiertos = [horario[d] for d in range(7) if horario.get(d)]
    if not abiertos:
        return []
    comun = abiertos[0]
    for otro in abiertos[1:]:
        nuevo: list[tuple[int, int]] = []
        for a0, a1 in comun:
            for b0, b1 in otro:
                ini, fin = max(a0, b0), min(a1, b1)
                if fin > ini:
                    nuevo.append((ini, fin))
        comun = nuevo
    return sorted(comun)


def dias_cerrados(horario: Horario) -> list[int]:
    return [d for d in range(7) if not horario.get(d)]


def hora_a_minutos(hora: str) -> int:
    hh, mm = hora.strip().split(":")
    valor = _minutos(hh, mm)
    if valor is None:
        raise ValueError(f"Hora no válida: {hora!r}")
    return valor
