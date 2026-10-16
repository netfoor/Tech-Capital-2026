# Fichas de fuente

Una ficha por fuente de [`data/catalog/data_catalog.csv`](../data/catalog/data_catalog.csv). El inventario completo (las 21 columnas de §08.4) está en ese archivo; aquí va lo que hace falta para decidir si la fuente sirve y cómo citarla. Las cifras de cobertura y calidad están en [`reports/calidad_datos.md`](../reports/calidad_datos.md), generado desde los datos.

## OpenStreetMap vía Overpass API (`osm-overpass`)

- **Qué aporta:** POI turísticos (museos, templos, sitios históricos, miradores, mercados, artesanías, parques, alimentos, alojamiento y sanitarios) y las únicas etiquetas abiertas de accesibilidad física: `wheelchair`, `toilets:wheelchair`, `ramp`, `step_count`, `incline`, `surface`, `elevator`, `bench`.
- **Cómo se obtiene:** `radar corredor descargar --fuente osm`. Una consulta por zona, una a la vez, con pausa de 10 s y espera creciente si el servidor está saturado (uso justo de Overpass). La consulta exacta queda dentro de cada extracto.
- **Licencia:** ODbL 1.0. Atribución obligatoria: «© OpenStreetMap contributors», visible en cada mapa y en la documentación. Lo derivado de OSM se comparte con la misma licencia.
- **Privacidad:** el extracto no guarda el usuario ni el conjunto de cambios de cada edición.
- **Limitaciones:** la cobertura depende de quién mapea. La falta de una etiqueta no significa que el lugar sea accesible ni inaccesible: queda «sin verificar». Las etiquetas existentes no están verificadas por el equipo (`confianza=0.6`).

## Sistema de Información Cultural (`sic-cultura`)

- **Qué aporta:** directorio oficial de museos, zonas arqueológicas, centros culturales, teatros, galerías y casas de artesanías del estado, con dirección y coordenadas.
- **Cómo se obtiene:** `radar corredor descargar --fuente sic`. Descarga de `https://sic.cultura.gob.mx/opendata/d/0_<tabla>_directorio.csv`; el extracto conserva las filas de Puebla (`estado_id=21`) sin las columnas de contacto.
- **Licencia:** el portal sugiere este crédito: «"Directorio de museos", publicado por el Sistema de Información Cultural/Secretaría de Cultura. Consultado en <url> el <fecha>». No encontramos una licencia formal publicada: **NO VERIFICADO**.
- **Limitaciones:** algunas coordenadas faltan (vienen en 0) o están desplazadas; los recintos sin par en OSM a menos de 75 m entran como POI propio y pueden duplicar un lugar con otro nombre. No trae horarios, costos ni accesibilidad.

## DENUE de INEGI (`inegi-denue`)

- **Qué aporta:** la oferta formal de alojamiento (SCIAN 7211), alimentos y bebidas (7225), museos y sitios históricos (7121) y agencias de viajes (5615), con coordenadas y estrato de personal ocupado.
- **Cómo se obtiene:** sin token, por la descarga masiva de la entidad 21 (`denue_21_csv.zip`, edición 05_2026). Se filtra localmente por SCIAN y se guardan dos extractos: uno estatal compacto (para conteos por municipio) y uno detallado de las zonas de consulta (para enlazar con OSM). No hay `INEGI_DENUE_TOKEN`; la API queda como alternativa.
- **Licencia:** Términos de Libre Uso de la Información del INEGI.
- **Privacidad:** se excluyen teléfono, correo, sitio web y razón social; en unidades de personas físicas pueden ser datos personales.
- **Limitaciones:** la actualización se centra en establecimientos grandes. Los de alimentos y las agencias no entran como POI propio para no inundar el catálogo: solo se enlazan con OSM y se cuentan por municipio.

## Observatorio Turístico, serie hotelera (`sectur-ot-2026-06`)

- **Qué aporta:** ocupación, llegadas, estadía, afluencia y derrama por centro turístico, mensual de 2017 a junio de 2026 (spec 002). Es el lado de la demanda del análisis oferta–demanda.
- **Licencia:** información pública de gobierno; licencia formal NO VERIFICADO.
- **Limitaciones:** afluencia y derrama son derivadas por la fuente con un factor; solo cubre hoteles registrados.

## Observatorio Turístico, informe 2024 con la BUAP (`sectur-obs-2024-buap`)

- **Qué aporta:** perfil del visitante y medios por los que conoció el destino. Contexto para el pitch, no entra al catálogo.
- **Limitaciones:** porcentajes agregados sin microdatos.

## Marco Geoestadístico de INEGI (`inegi-mg-2025-12`)

- **Qué aporta:** límites municipales para asignar `municipio_cvegeo` a cada POI y validar que las coordenadas estén dentro del estado.
- **Licencia:** Términos de Libre Uso de la Información del INEGI.
- **Limitaciones:** simplificado al 4 %; un punto a pocos metros de un límite puede quedar en el municipio vecino.

## Cabeceras municipales de INEGI (`inegi-cabeceras`)

- **Qué aporta:** el centro de cada zona de consulta (incluida San Andrés Cholula, localidad 211190001).

## Pueblos Mágicos (`pueblos-magicos`)

- **Qué aporta:** la capa de destinos alternativos (`data/referencia/destinos.csv`).
- **Estado:** pendiente de cotejar con el catálogo federal (T001-06).

## Pendientes

- **Boletines del CEIGEP** (`ceigep-boletines`) y **Censo 2020 por AGEB** (`inegi-censo-2020-ageb`): registrados como pendientes para la spec 013.
