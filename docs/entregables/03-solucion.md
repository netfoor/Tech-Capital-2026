# 3. Descripción de la solución

## Qué hace el radar

Para cada Pueblo Mágico calcula dos índices entre 0 y 100, comparados con los otros once, y los cruza:

- **Atención digital:** qué tanto aparece el destino en el buscador de Google, en los asistentes conversacionales y, cuando existan, en YouTube y en el panel de TikTok.
- **Desempeño real:** la ocupación hotelera de los últimos 12 meses publicados por el Observatorio Turístico.

La diferencia entre ambos es la **brecha**. Con ella y los cortes en la mediana de cada eje, cada destino cae en uno de cuatro cuadrantes con una recomendación:

| Cuadrante | Recomendación |
|---|---|
| Consolidado | Mantener lo que funciona |
| Atención sin estancia | Convertir la atención en pernocta: motivos para quedarse y resolver fricciones |
| Demanda poco visible | Crecer con contenido |
| Por posicionar | Priorizar la promoción si la experiencia es buena |

## Qué tiene de nuevo

1. **Auditoría de asistentes.** Un corpus de prompts en español, inglés, francés, coreano y chino se corre muchas veces en dos proveedores. Se mide el porcentaje de corridas en que aparece cada destino, con su intervalo, y qué fuentes citan los asistentes.
2. **Cruce con lo oficial.** La atención se compara con la ocupación de la propia estadística de la Secretaría, de modo que cada hallazgo se pueda leer como una acción: qué destino promover, resolver o mantener.
3. **Verificable.** Cada cifra del sitio sale de una tabla curada por código; el navegador comprueba la huella SHA-256 de cada archivo.

## Qué ve cada usuario

| Vista | Para qué |
|---|---|
| Radar | Mapa por brecha, tabla de los 12 destinos y gráfica de cuadrantes, con selección compartida |
| Fichas | Una hoja por destino, imprimible en una carta, para cada cita del Tianguis |
| Asistentes | Visibilidad por destino con alternas de idioma y proveedor, fuentes citadas y un ejemplo de respuesta |
| Redes | Presencia en el panel y en YouTube (se completa con esas fuentes) |
| Página pública | El problema, el uso en el Tianguis, el método con sus límites y las descargas |

## Lo que la solución no hace

- No afirma causalidad: el cuadrante es una posición relativa.
- No sustituye la medición oficial: la complementa.
- Presenta como provisional lo que aún no se valida (detección de menciones, panel, YouTube).

Detalle del método: [`07-arquitectura.md`](07-arquitectura.md) y [`06-procesos-de-datos.md`](06-procesos-de-datos.md).
