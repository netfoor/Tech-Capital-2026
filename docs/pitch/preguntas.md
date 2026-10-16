# Preguntas previsibles del jurado

**¿De dónde salen los datos de accesibilidad?**
Hoy, de OpenStreetMap (etiquetas `wheelchair`, `toilets:wheelchair`), siempre como «sin verificar». En el piloto se suman tres orígenes: auditoría del equipo con formulario, prestadores y reportes de visitantes moderados. Cada atributo guarda su origen, fecha y confianza. Una sola opinión no certifica.

**Solo el 2.2 % tiene datos. ¿Entonces la app no sirve?**
Ese número es el hallazgo. La app ya sirve para descubrir y planear, y es honesta sobre lo que no sabe. Cada reporte moderado aumenta la cobertura. El tablero muestra a la Secretaría dónde invertir en levantar información primero.

**¿Por qué es IA y no un filtro?**
Hay cuatro etapas: elegibilidad dura, ranking multiobjetivo (intereses con TF-IDF, cercanía, diversidad territorial y calidad del dato), secuenciación con ventanas de horario (inserción y 2-opt) y explicación. Se compara contra dos líneas base: popularidad y cercanía. Ninguna de las dos respeta las restricciones (219 y 237 violaciones contra 0). El detalle está en `docs/ia/model_card_recomendador.md`.

**¿La Secretaría ve a las personas?**
No. La ubicación solo se registra en una sesión que la persona inicia y puede pausar. El tablero ve agregados y suprime los grupos con menos de k observaciones. Los datos personales viven en un esquema aparte y nunca salen en una respuesta pública. Hay pruebas automáticas de esto.

**¿Los usuarios de la app representan al turismo de Puebla?**
No. Por eso los indicadores oficiales (DataTur) y los de la app se muestran por separado, cada uno con su n. Lo sintético se etiqueta siempre.

**¿Cuánto cuesta operarlo?**
El prototipo corre en planes gratuitos: Vercel para la app y la API, y Neon para Postgres con PostGIS. Un piloto estatal agrega almacenamiento de fotos, verificación en campo y moderación. Ver `docs/viabilidad.md`.

**¿Cómo se escala a otros destinos?**
DENUE, Marco Geoestadístico, SIC, OpenStreetMap y DataTur tienen cobertura nacional. Se agrega un corredor en `data/curado/corredores.csv` y se corre la ingesta.

**¿Qué no funciona todavía?**
El recorrido con GPS está en desarrollo; la demo usa trazas sintéticas etiquetadas. Falta la auditoría presencial de 8 a 15 lugares. Los pesos del recomendador no están calibrados con usuarios reales.
