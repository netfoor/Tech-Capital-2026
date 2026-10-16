# Piloto de geolocalización en búsquedas de Google (Atlixco y Teziutlán)

Estado: protocolo propuesto; las búsquedas se hacen a mano desde el navegador del equipo.
Relacionado con T003-07 (comparación de búsquedas por ubicación).

## Pregunta
¿Cambia lo que Google muestra por la ubicación declarada, y cuánto de la diferencia se debe a la hora y no a la geografía?

## Reglas
- Sin VPN, sin sesión de Google, ventana de incógnito, `hl=es&gl=mx`.
- Pausa de 15–20 s entre búsquedas. Si aparece un CAPTCHA, se detiene el bloque; no se evade.
- Las consultas no cambian entre condiciones: `qué hacer en Atlixco`, `qué hacer en Teziutlán`, `Atlixco turismo`, `Teziutlán turismo`.

## Condiciones (3)
- A. Sin ubicación declarada (solo la IP real, Puebla).
- B. Coordenadas de Atlixco (18.9087, -98.4307) con DevTools > Sensors, más `uule` de "Atlixco,Puebla,Mexico".
- C. Coordenadas de Teziutlán (19.8167, -97.3592) con DevTools > Sensors, más `uule` de "Teziutlan,Puebla,Mexico".

Las coordenadas solo afectan a la API del navegador; `uule` es el parámetro que Google lee para la URL (`&uule=w+CAIQICI` + carácter de longitud + nombre en base64).

## Verificación de la ubicación interpretada
Al pie de la página de resultados Google escribe la ubicación que usó ("Puebla, Pue. – Según tu actividad…" o similar). Se copia ese texto en `ubicacion_interpretada`. Si no coincide con la declarada, la fila se marca `valida=no` y no entra al análisis.

## Diseño
4 consultas × 3 condiciones × 6 bloques = 72 búsquedas. En cada bloque el orden de las condiciones se alterna (A-B-C, C-B-A, …) y se reparte en la mañana, tarde y noche. Con eso la hora no coincide con una sola condición. La condición A repetida entre bloques mide el ruido de test-retest: las diferencias entre B y C solo cuentan si superan la variación entre repeticiones de A.

## Registro
`registro-plantilla.csv`, una fila por búsqueda: id, fecha_hora_utc, hora_local, consulta, condicion, ubicacion_declarada, metodo, ip, asn, ubicacion_interpretada, hl_gl, navegador, top10_dominios, paquete_local, sha256_html, captura, valida, notas.

## Análisis previsto
Traslape de dominios del top 10 entre condiciones (índice de Jaccard), presencia y posición de resultados del propio municipio y del paquete local; comparar B-C contra A-A.

## Límites
Muestra pequeña, un solo equipo y una sola IP: sirve para decidir si vale la pena una medición mayor, no para generalizar. Un servicio de pago de SERP solo se contrata con aprobación previa.
