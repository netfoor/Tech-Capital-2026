# Viabilidad y costos

| Escenario | Componentes | Costo |
|---|---|---|
| Prototipo (hoy) | Vercel (app y API) y Neon (plan gratuito: 1 GB y 100 horas de cómputo al mes) | Sin costo de infraestructura |
| Piloto (corredor y 12 Pueblos Mágicos) | Lo anterior en planes de pago, almacenamiento de fotos, verificación en campo de lugares y moderación de reportes | Por cotizar. Lo que más cuesta es el trabajo en campo y la moderación, no la nube |
| Estatal | Más corredores y colaboración con prestadores y colectivos de personas con discapacidad | Por cotizar con la Secretaría |

**Escala.** DENUE, Marco Geoestadístico, SIC, OpenStreetMap y DataTur tienen cobertura nacional. Para sumar un corredor, se agrega en `data/curado/corredores.csv` y se corre la ingesta.

**Riesgos y cómo se mitigan:**

- **Arranque sin usuarios:** el módulo Oferta–demanda da valor desde el primer día.
- **Sesgo de quién usa la app:** se muestra n y no se extrapola.
- **Datos de accesibilidad desactualizados:** cada dato lleva fuente y fecha, y las correcciones se moderan.
