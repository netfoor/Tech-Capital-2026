# Protocolo del panel · versión v1

Instrucciones para cada participante. Toma menos de 10 minutos.

## Antes de empezar

- Usa **tu cuenta habitual de TikTok** en tu teléfono. No crees una cuenta nueva ni cierres sesión: nos interesa lo que TikTok te muestra a ti.
- Lee y acepta el aviso de privacidad en el formulario.

## Paso 1. Cuatro búsquedas

Escribe cada búsqueda **exactamente igual**, sin elegir sugerencias, y quédate en la pestaña que aparece por defecto:

| Clave | Búsqueda |
|---|---|
| C1 | qué visitar en Puebla |
| C2 | pueblos mágicos de Puebla |
| C3 | fin de semana en Puebla |
| C4 | lugares bonitos cerca de Puebla |

En cada búsqueda:
1. Toma capturas de pantalla hasta cubrir los **primeros 12 resultados**. Normalmente son dos o tres capturas.
2. No abras los videos todavía.

## Paso 2. Comentarios (opcional)

Abre **el primer video** de la búsqueda C2, abre los comentarios y toma **una captura** de los primeros comentarios que aparecen.

## Paso 3. Tu asistente (opcional)

Si usas un asistente como ChatGPT o Gemini, pídele recomendaciones como lo harías normalmente para un fin de semana en Puebla. Después comparte el **enlace de la conversación** o pega el texto de la respuesta en el formulario.

## Paso 4. Cinco preguntas

1. Rango de edad: 18–24, 25–34, 35–44 o 45 o más.
2. Estado donde vives (o país, si vives fuera de México).
3. ¿Has visitado algún Pueblo Mágico de Puebla? ¿Cuál?
4. ¿Con qué frecuencia usas TikTok para buscar lugares a dónde ir? Nunca, a veces o seguido.
5. ¿Usas asistentes de IA para planear viajes? Nunca, a veces o seguido.

## Paso 5. Enviar

Sube las capturas y responde en el formulario. Gracias.

---

## Reglas de codificación (para el equipo)

| Campo | Regla |
|---|---|
| `posicion` | Orden de lectura en la cuadrícula: de izquierda a derecha y de arriba abajo, del 1 al 12 |
| `destino_id` | Destino del catálogo que se menciona en el texto visible de la tarjeta (título o texto sobre la miniatura). Si se mencionan varios, se registra una fila por destino con la misma posición. Si no hay destino reconocible, se deja vacío |
| `vistas_visibles` | Número que muestra la tarjeta, convertido («1.2M» = 1,200,000). Vacío si no aparece |
| `tipo_contenido` | `recorrido` (visita a un lugar), `lista` (varios lugares), `comida`, `evento` u `otro` |
| Lo que no se registra | Nombre o usuario del creador, rostros, texto de comentarios, datos del perfil del participante |

Dos personas codifican de forma independiente el 20 % de las sesiones para medir el acuerdo.
