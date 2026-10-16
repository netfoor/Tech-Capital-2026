# Evidencia del problema

Cada afirmación tiene una fuente y una etiqueta de origen:

- **Oficial:** documento o dato de una institución pública.
- **Externa:** prensa o estudio privado.
- **Propia:** cálculo del equipo con código del repositorio.

Las fuentes con archivo están registradas en [`data/fuentes/fuentes.csv`](../../data/fuentes/fuentes.csv), con su SHA-256. Las cifras «propias» se regeneran con `uv run radar indicadores` y `uv run radar resumen --anio 2025` (spec 002).

## 1. La decisión de viaje pasa por redes y asistentes

| Afirmación | Origen | Fuente |
|---|---|---|
| En el verano de 2024, el principal medio por el que el visitante se enteró de la ciudad de Puebla y su oferta fueron las redes sociales (Instagram, TikTok, Facebook): **39.7 %**. Le siguen amigos y familiares (32.9 %) y la experiencia previa (15.9 %) | Oficial | `sectur-obs-verano-2024` |
| En otro levantamiento de 2024, la TV fue el principal medio (46.6 %) y las redes sociales el segundo (28.8 %) | Oficial | `sectur-obs-2024-buap` |
| En 2020, el 46.7 % de los encuestados dijo que las opiniones en redes sociales son la vía principal para enterarse de los sitios de interés en Puebla, y el 20.8 % mencionó los sitios especializados de internet | Oficial | `sectur-mercado-2020` |
| El 74 % de los viajeros mexicanos ha usado IA en alguna etapa del viaje y el 41 % para investigar destinos. Muestra de 2,014 personas en México, abril–mayo de 2025 | Externa | `booking-2025-mx` |

**Lectura:** los dos informes de 2024 difieren (39.7 % frente a 28.8 % para redes) porque son levantamientos distintos. En ambos, las redes están entre los dos medios principales. Ningún indicador oficial mide qué ven los visitantes en esos canales.

## 2. La medición oficial se apoya en el hotel

| Afirmación | Origen | Fuente |
|---|---|---|
| Según el glosario de los datos del observatorio, la ocupación, las llegadas, los turistas noche, la estadía y la densidad provienen de DataTur. La afluencia de visitantes y la derrama económica las estima la Secretaría | Oficial | `sectur-ot-2026-06` (glosario) |
| La afluencia mensual de cada destino es la llegada de turistas a hotel multiplicada por un factor fijo. Desde 2019 el factor es **2.222** en el **100 % de los meses** en 9 de los 12 Pueblos Mágicos, y entre 69 % y 99 % en los otros tres. En la ciudad de Puebla el factor es **3.333** | Propia | `data/curado/factor_afluencia_por_centro.csv` |
| En Google Trends, Chignahuapan tiene un pico de interés cada noviembre (temporada de esferas) que no aparece en la afluencia oficial de ese mes | Propia (exploración) | Se reproduce en la spec 003 |

**Lectura:** el visitante que no pernocta en un hotel registrado no está en la medición directa. Antes de presentarlo como hecho hay que confirmar la metodología con la Secretaría; por ahora se presenta como «lo que muestran los datos».

## 3. Los beneficios se concentran y hay capacidad disponible

Cálculo propio con la serie oficial, año completo 2025:

| Destino | Afluencia | Ocupación | Derrama por visitante | Cuartos libres por día |
|---|---|---|---|---|
| Ciudad de Puebla | 10.64 M | 60.0 % | $1,304 | 4,253 |
| Cholula | 1.20 M | 57.6 % | $1,075 | 630 |
| Zacatlán | 1.06 M | 52.2 % | $846 | 688 |
| Chignahuapan | 0.78 M | 45.3 % | $856 | 661 |
| Atlixco | 0.48 M | 44.2 % | $1,187 | 441 |
| Cuetzalan | 0.44 M | 41.3 % | $858 | 429 |
| Huauchinango | 0.28 M | 43.2 % | $1,013 | 255 |
| Teziutlán | 0.27 M | 39.9 % | $842 | 284 |
| Xicotepec | 0.20 M | 43.8 % | $1,076 | 179 |
| Tlatlauquitepec | 0.15 M | 36.0 % | $827 | 191 |
| Huejotzingo | 0.10 M | 48.2 % | $1,146 | 96 |
| Tetela de Ocampo | 0.08 M | 32.9 % | $1,048 | 108 |
| Pahuatlán | 0.07 M | 32.1 % | $948 | 105 |

- La capital concentra el **59.9 %** de la afluencia estatal y los 12 Pueblos Mágicos el **28.8 %**. Todos los Pueblos Mágicos tienen menor ocupación y menor derrama por visitante que la capital.
- La estadía promedio es de 1.8–1.9 días en todos los destinos.
- La derrama por visitante es un dato derivado: afluencia por gasto promedio.

## 4. La promoción se evalúa por alcance

| Afirmación | Origen | Fuente |
|---|---|---|
| Balance 2025: 18 campañas digitales con «más de 16 millones de impresiones»; 249 experiencias en el Inventario Estatal de Turismo Comunitario; 12 Pueblos Mágicos con categoría AA | Oficial | `gob-pue-balance-2025` |
| Acciones de promoción rumbo al Mundial 2026: colaboraciones con creadores de contenido, campañas digitales, medios y streaming. El comunicado no reporta indicadores de resultado | Oficial | `gob-pue-mundial-2026` |

## 5. Los asistentes recomiendan de forma variable y citan pocas fuentes

| Afirmación | Origen | Fuente |
|---|---|---|
| Con 600 voluntarios y 2,961 corridas, hay menos de 1 % de probabilidad de que un asistente repita la misma lista de recomendaciones. Lo recomendable es medir el porcentaje de visibilidad sobre muchos prompts repetidos | Externa | `sparktoro-2026` |
| En 30 millones de citas de asistentes con búsqueda, las fuentes más citadas son Reddit, YouTube, LinkedIn, Wikipedia y Forbes | Externa | `peec-2026` |
| Prueba propia (una corrida, sin valor estadístico): ante «Voy a visitar Puebla un fin de semana, ¿qué no me debo perder?», un asistente con búsqueda citó cinco fuentes, entre ellas sitios del Ayuntamiento, el INAH y Cholula, y no mencionó ningún Pueblo Mágico de la sierra | Propia (exploración) | Se reproduce en la spec 006 |

## 6. Hay una fecha y un escaparate

| Afirmación | Origen | Fuente |
|---|---|---|
| Tianguis Turístico México 2027 en Puebla del 9 al 12 de marzo, más «Ventana Puebla» del 12 al 14 de marzo en San Pedro Cholula. Se esperan 3,980 expositores, más de 1,790 compradores internacionales y cerca de 70,000 citas de negocio. Puebla vuelve a ser sede después de 14 años | Externa | `tianguis-2027` |
| El tema central de Tech Capital 2026 es el turismo digital, rumbo al Tianguis 2027 | Externa | `tc-2026-turismo-digital` |

## 7. El acceso a datos de plataformas está restringido

| Afirmación | Origen | Fuente |
|---|---|---|
| La API de investigación de TikTok solo está disponible para investigadores de EE. UU., Europa, Canadá y Brasil, sin fines comerciales. México no califica | Oficial (de la plataforma) | `tiktok-research-api` |

**Consecuencia de diseño:** el dato de TikTok por destino se obtiene con un panel de personas reales, con consentimiento, y no con extracción automatizada (constitución, IV).
