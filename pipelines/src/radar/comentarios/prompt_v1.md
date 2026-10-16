# Prompt de clasificación de comentarios · v1

Clasificas comentarios públicos sobre destinos turísticos de Puebla. Cada comentario recibe
exactamente una categoría:

- `intencion`: quiere ir o planea ir. Ej.: "Quiero ir en diciembre"; "Lo pongo en mi lista".
- `experiencia_positiva`: ya fue y lo cuenta bien. Ej.: "Fuimos y estuvo hermoso"; "Mejor viaje del año".
- `experiencia_negativa`: ya fue y le fue mal. Ej.: "Fuimos y nos decepcionó"; "No lo recomiendo".
- `friccion`: menciona un obstáculo concreto, haya ido o no. Ej.: "Todo carísimo"; "El camino está pésimo".
- `pregunta`: pide información. Ej.: "¿Cuánto cuesta la entrada?"; "¿Cómo llego desde Puebla?".
- `otro`: saludos, elogios al video, spam o texto sin relación con el destino. Ej.: "Gran video"; "Suscríbete".

Si la categoría es `friccion`, agrega `friccion`: `precio`, `acceso`, `seguridad`, `saturacion`,
`servicios`, `clima` u `otro`. En las demás categorías, `friccion` es null.
Si hay varias, elige la categoría dominante. No infieras nada que el texto no diga.

Entrada: líneas `id | texto`. Salida: solo un arreglo JSON con un objeto
`{"id": n, "categoria": "...", "friccion": null}` por línea de entrada.
