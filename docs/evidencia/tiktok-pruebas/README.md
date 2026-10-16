# Pruebas de búsqueda en TikTok (16 de octubre de 2026)

**Qué es.** Prueba exploratoria hecha para documentar la posibilidad de usar video corto como tercer componente de atención. No es un componente del radar y sus cifras no entran al índice.

**Cómo se hizo.** Con una cuenta de prueba del equipo con sesión iniciada, en el navegador de una computadora ubicada en Puebla/Tlaxcala, se buscó «<destino> Puebla» en la pestaña de videos y se leyeron los 11 o 12 primeros resultados (autor, texto, «me gusta»). La clasificación «visita explícita» o «noticias o sucesos» la hizo una persona leyendo el texto del video. Datos: `busqueda-por-destino.csv`.

**Qué se observó.**
- En 10 de los 12 destinos la mayoría de los resultados son contenido de visita (qué hacer, dónde ir, fechas de ferias).
- Teziutlán es la excepción: de 12 resultados solo 3 son de visita y 5 son noticias o sucesos. Esto es consistente con que el radar lo marque como `demanda_poco_visible`, pero es una sola búsqueda y no prueba una causa.
- Algunos videos con muchos «me gusta» no son turísticos (por ejemplo, una nota de seguridad en Huejotzingo o una fiesta en Cholula), por lo que el total de «me gusta» no sirve como medida de atención turística sin filtrar el contenido.
- La cuenta de prueba no tiene videos propios, así que no hubo comentarios de la propia cuenta que analizar.

**Pruebas que no se pudieron hacer, y por qué.**
- **Sin sesión:** desde un navegador sin cuenta (y con idioma y zona horaria de México) la búsqueda devuelve 0 resultados y pide iniciar sesión. Por tanto, sin cuenta no hay medición posible.
- **Cambiar de estado:** TikTok decide la ubicación por dirección IP, no por la configuración del navegador, así que simular otro estado desde el navegador no cambia lo que se ve. Hacerlo de verdad requiere una conexión desde ese estado (por ejemplo, una VPN con salida allí), que no se usó. Queda como siguiente paso, y se anota como posibilidad.

**Límites.** Una búsqueda por destino, un solo día, una sola cuenta, resultados ordenados por TikTok (mezclan relevancia y popularidad), 11 o 12 resultados por búsqueda. Las cifras son descriptivas.
