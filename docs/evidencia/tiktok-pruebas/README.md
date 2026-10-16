# Pruebas de búsqueda en TikTok (16 de octubre de 2026)

**Qué es.** Prueba exploratoria hecha para documentar la posibilidad de usar video corto como tercer componente de atención. No es un componente del radar y sus cifras no entran al índice.

**Cómo se hizo.** Con una cuenta de prueba del equipo con sesión iniciada, en el navegador de una computadora ubicada en Puebla/Tlaxcala, se buscó «<destino> Puebla» en la pestaña de videos y se leyeron los 11 o 12 primeros resultados (autor, texto, «me gusta»). La clasificación «visita explícita» o «noticias o sucesos» la hizo una persona leyendo el texto del video. Datos: `busqueda-por-destino.csv`.

**Qué se observó.**
- En 10 de los 12 destinos la mayoría de los resultados son contenido de visita (qué hacer, dónde ir, fechas de ferias).
- Teziutlán es la excepción: de 12 resultados solo 3 son de visita y 5 son noticias o sucesos. Esto es consistente con que el radar lo marque como `demanda_poco_visible`, pero es una sola búsqueda y no prueba una causa.
- Algunos videos con muchos «me gusta» no son turísticos (por ejemplo, una nota de seguridad en Huejotzingo o una fiesta en Cholula), por lo que el total de «me gusta» no sirve como medida de atención turística sin filtrar el contenido.
- La cuenta de prueba no tiene videos propios. Los comentarios de videos ya publicados de otros usuarios están en `comentarios-muestra.md`.

**Pruebas que no se pudieron hacer, y por qué.**
- **Sin sesión:** desde un navegador sin cuenta (y con idioma y zona horaria de México) la búsqueda devuelve 0 resultados y pide iniciar sesión. Por tanto, sin cuenta no hay medición posible.
- **Cambiar de estado:** TikTok decide la ubicación por dirección IP, no por la configuración del navegador, así que simular otro estado desde el navegador no cambia lo que se ve. Hacerlo de verdad requiere una conexión desde ese estado (por ejemplo, una VPN con salida allí), que no se usó. Queda como siguiente paso, y se anota como posibilidad.

**Límites.** Una búsqueda por destino, un solo día, una sola cuenta, resultados ordenados por TikTok (mezclan relevancia y popularidad), 11 o 12 resultados por búsqueda. Las cifras son descriptivas.

## Comparación con otra ubicación (VPN gratuita, Canadá)

Se repitieron las 12 búsquedas el mismo día, con la misma cuenta de prueba, desde una conexión VPN gratuita con salida en Montreal, Canadá. Datos: `comparacion-ubicacion.csv` (autores que aparecen en ambas búsquedas).

- Los resultados cambian, pero se mantiene un núcleo: entre 3 y 8 de cada 10 a 12 autores se repiten, según el destino (en total 76 coincidencias en 12 destinos). Atlixco, Chignahuapan, Huauchinango y Tetela de Ocampo son los más estables; Teziutlán y Xicotepec los que más cambian.
- Teziutlán es el caso notable: desde Puebla 5 de 12 resultados eran noticias de sucesos y desde Canadá solo 1. La explicación no se puede aislar: pudo ser la ubicación o el momento, porque las búsquedas se hicieron con casi una hora de diferencia en un tema noticioso. Se deja como hipótesis, no como hallazgo.
- Con la VPN gratuita no hay salida en México, así que no se pudo probar un estado distinto de Puebla. La prueba por estado queda pendiente y requiere una conexión con salida en cada uno.
- Interpretación: la ubicación sí influye en lo que TikTok muestra, por lo que una medición de atención con video corto tendría que fijar y registrar desde dónde se consulta, como se hace con el idioma y la semilla en los asistentes.
