# 5. Justificación de la selección de los datos

Cada familia de fuentes responde a una pregunta del radar y a una hipótesis de [`../producto/vision.md`](../producto/vision.md). El inventario con huellas está en [`../../data/fuentes/fuentes.csv`](../../data/fuentes/fuentes.csv) y los campos de cada tabla en [`../dominio/modelo-de-datos.md`](../dominio/modelo-de-datos.md).

| Familia | Qué aporta | Por qué esta fuente | Hipótesis | Spec |
|---|---|---|---|---|
| Serie oficial del Observatorio Turístico | Ocupación, llegadas, estadía, derrama y afluencia por destino y mes, 2017–2026 | Es la medición oficial que la Secretaría ya usa; permite comparar sin pedir datos privados | H1, H2 | 002 |
| Marco Geoestadístico y catálogo de destinos | Claves y límites municipales; términos de búsqueda en cinco idiomas | Une todas las fuentes por el mismo identificador de destino | Todas | 001 |
| Google Trends | Interés de búsqueda mensual por destino | Señal pública de intención de viaje, con serie larga y repetible | H2 | 003 |
| Asistentes conversacionales | Visibilidad de cada destino y fuentes citadas, por idioma y proveedor | Es un canal nuevo de decisión de viaje que nadie mide | H1, H3 | 006 |
| YouTube y sus comentarios | Presencia en video y fricciones declaradas por los visitantes | Fuente con API oficial; los comentarios explican la brecha entre atención y estancia | H4 | 004, 007 |
| Panel de TikTok | Qué ve en TikTok una muestra de personas al buscar cada destino | La API de investigación de TikTok no está disponible para México; un panel con consentimiento es el camino legítimo | H1, H4 | 005 |
| Estudios del Observatorio sobre cómo se informa el visitante | Magnitud de las redes como medio de información | Evidencia oficial del problema | H1 | 001 |

## Criterios aplicados

1. **Oficial primero:** lo que la Secretaría mide es la referencia; las señales digitales se cruzan con ella.
2. **Con permiso:** no se usan datos de plataformas obtenidos con automatización o cuentas ajenas.
3. **Reproducible:** toda fuente tiene URL, fecha de consulta y huella SHA-256, y toda tabla curada se genera con código.
4. **Sin datos personales publicados:** del panel y de los comentarios solo se publican agregados.
5. **Nulo antes que inventado:** un dato que falta se deja vacío y se explica; nunca se rellena.
