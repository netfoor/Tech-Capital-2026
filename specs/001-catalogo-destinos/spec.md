# Spec 001 · Catálogo de destinos

| | |
|---|---|
| Contexto | Catálogo territorial (núcleo compartido) |
| Prioridad | P0 |
| Estado | En curso: semilla y validación listas |
| Depende de | — |
| Habilita | Todas las demás specs |

## Bases que atiende

DAT-01, DAT-03 y DAT-04 (§5: integrar fuentes con una llave común documentada), FIN-08 (el mapa como parte del funcionamiento).

## Objetivo

Que cualquier dato de cualquier fuente se pueda asociar sin ambigüedad a un destino. Para eso se definen los destinos que analiza el radar con identidad estable, claves INEGI, ubicación, geometría y nombres en cada idioma del estudio.

## Historias de usuario

**H1 (P0).** Como analista, quiero un identificador único por destino para unir datos oficiales, señales digitales y respuestas de asistentes.
- Dado el catálogo, cuando se valida, entonces hay 12 Pueblos Mágicos, los `destino_id` son únicos y cada centro del Observatorio Turístico corresponde a lo más a un destino.

**H2 (P0).** Como persona que usa el sitio, quiero ver cada destino en su lugar real del mapa del estado.
- Dado un destino, cuando se dibuja el mapa, entonces su punto cae dentro de su municipio según el Marco Geoestadístico de INEGI.

**H3 (P0).** Como responsable de la auditoría de asistentes, quiero los nombres de cada destino en español, inglés, francés, coreano y chino para reconocer menciones.
- Dado un destino y un idioma del estudio, cuando se consulta `terminos_idiomas.csv`, entonces existe al menos un término y su origen (fuente o transliteración verificada).

**H4 (P1).** Como analista, quiero los temas de Google Trends (identificadores `/m/…` o `/g/…`) de cada destino para no confundir, por ejemplo, Zacatlán (municipio) con otras acepciones.
- Dado un destino, cuando se consultan sus términos de Trends, entonces hay un tema validado o la anotación de que se usa texto libre.

## Requisitos funcionales

- **FR-001-01** `data/referencia/destinos.csv` con las columnas definidas en `docs/dominio/modelo-de-datos.md`.
- **FR-001-02** Validación automática (`uv run radar catalogo`): 12 Pueblos Mágicos, unicidad, claves INEGI válidas, cabecera dentro del primer municipio y coordenadas dentro de Puebla.
- **FR-001-03** Geometrías en `data/referencia/geo/`: municipios de Puebla simplificados y contorno estatal, con su fuente registrada.
- **FR-001-04** `data/referencia/terminos_idiomas.csv` con términos en fr, ko y zh para los 12 Pueblos Mágicos y la capital.
- **FR-001-05** Función `catalogo.detectar(texto, idioma) -> list[(destino_id, posicion)]` que reconoce menciones en un texto usando los términos. No distingue acentos ni mayúsculas, respeta límites de palabra en alfabetos latinos y devuelve el orden de aparición.
- **FR-001-06** (P1) `data/referencia/trends_temas.csv` con `destino_id`, `tema_id`, `etiqueta`, `verificado`.

## Requisitos no funcionales

- La validación termina en menos de 1 segundo.
- Cualquier cambio al catálogo pasa la validación antes del commit.

## Fuera de alcance

- Atractivos individuales (pirámide, cascadas, museos). El radar trabaja a nivel de destino.
- Destinos fuera de Puebla.

## Preguntas abiertas

- ¿Conviene separar Cholula en San Pedro y San Andrés en el radar? Por ahora no: el Pueblo Mágico es «Cholula» y el observatorio publica ese agregado.
- Las zonas son una agrupación de trabajo. Si la Secretaría tiene una regionalización turística oficial, se adopta.
