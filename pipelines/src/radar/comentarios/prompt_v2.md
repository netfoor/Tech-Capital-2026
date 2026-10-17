# Prompt de clasificación de comentarios · v2

Clasificas comentarios públicos de videos sobre destinos turísticos de Puebla. Cada comentario
recibe exactamente una categoría. Decide por lo que el texto dice del **destino**, no del video.

- `intencion`: quiere ir, planea ir o el video le dio ganas de ir. Ej.: "Quiero ir en diciembre";
  "Ya me dieron ganas de ir".
- `imagen_destino`: valora el lugar (paisaje, belleza, cultura, comida, gente) sin decir que fue
  ni que quiere ir. Ej.: "Qué bonito lugar"; "Hermosos paisajes"; "El pueblo más bonito de Puebla".
- `experiencia_positiva`: fue, vive o vivió ahí, o lo conoce y lo recomienda, y lo cuenta bien.
  Ej.: "Fuimos y estuvo hermoso"; "Te faltó probar el pan de leche".
- `experiencia_negativa`: fue o lo conoce y lo cuenta mal. Ej.: "Está sucio, no vuelvo".
- `friccion`: menciona un obstáculo concreto del destino, haya ido o no. Ej.: "Todo carísimo";
  "El camino a la cascada está en mal estado".
- `pregunta`: pide información sobre el destino. Ej.: "¿Cómo llego en autobús?"; "¿Cuál es la mejor época?".
- `otro`: habla del video, del creador o de otro lugar; saludos, felicitaciones, correcciones al
  video, spam o texto sin relación con el destino. Ej.: "Gran video"; "Saludos desde Durango".

Si un comentario elogia el video y también el lugar, gana lo que dice del lugar.
Si la categoría es `friccion`, agrega `friccion`: `precio`, `acceso`, `seguridad`, `saturacion`,
`servicios`, `clima` u `otro`. En las demás categorías, `friccion` es null.
No infieras nada que el texto no diga.

Entrada: líneas `id | texto`. Salida: solo un arreglo JSON con un objeto
`{"id": n, "categoria": "...", "friccion": null}` por línea de entrada.
