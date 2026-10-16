# 2. Definición del problema y beneficiarios

> Borrador (spec 013). Las cifras no se escriben aquí a mano: cada una se cita por su número en «Cifras clave para el pitch» de [`reports/01_problema.md`](../../reports/01_problema.md), que genera `analysis/01_problema.py` desde `data/curado/`. El detalle, con fuente, fecha de consulta, denominador y limitaciones, está en ese reporte.

## El problema

La visita turística en Puebla se concentra en pocos polos (la capital y Cholula), mientras otros destinos con oferta cultural reciben poca demanda. Al mismo tiempo, el visitante no encuentra información confiable y unificada sobre costo, horarios y, sobre todo, accesibilidad física de los lugares. Quien tiene una necesidad de movilidad, viaja con personas mayores o con poco presupuesto planea a ciegas o se queda en los sitios más conocidos. La Secretaría tiene indicadores hoteleros agregados, pero no señales finas sobre permanencia, satisfacción y barreras por destino o corredor.

## Lo que muestran los datos

1. **La demanda se concentra.** La capital y Cholula reciben más de la mitad de las llegadas a hotel del Estado (cifra clave 1; serie 2017–2026 y HHI en la sección A del reporte).
2. **Los Pueblos Mágicos llenan menos cuartos.** La ocupación de los 11 Pueblos Mágicos sin Cholula está claramente por debajo de la de la capital (cifra clave 2).
3. **Hay destinos alternativos con capacidad libre.** Casi todos los Pueblos Mágicos tienen oferta cultural registrada y ocupación por debajo del promedio estatal (cifra clave 3; criterio y tabla ordenada en la sección C).
4. **La oferta registrada también se concentra**, sobre todo museos, sitios históricos y agencias (cifra clave 4; sección B).
5. **Casi no hay información de accesibilidad.** Muy pocos lugares tienen algún dato de accesibilidad en fuentes abiertas y casi ningún sanitario público dice si su baño es accesible (cifras clave 5 y 6; sección D). Esto mide cobertura de información, no el nivel de accesibilidad de los lugares.

Figuras: [`docs/pitch/figuras/`](../pitch/figuras/).

**Lectura honesta.** Son resultados descriptivos: no prueban por qué ocurre la concentración (puede influir el acceso, la distancia o el tamaño de la planta hotelera). La serie hotelera solo ve a quien duerme en un hotel registrado. Faltan dos análisis por falta de datos descargados: población residente con discapacidad motriz por AGEB (Censo 2020) y pendiente del entorno peatonal (modelo de elevación).

## Beneficiarios (§02.5)

- **Visitantes**, en especial personas con discapacidad, personas mayores, familias con carriola, presupuestos bajos y quienes visitan por primera vez.
- **Prestadores pequeños y comunitarios**, sobre todo en los destinos alternativos.
- **Comunidades receptoras**, que reciben una parte más equilibrada de los beneficios.
- **Secretaría de Desarrollo Turístico y municipios**, que obtienen indicadores agregados con fuente y nivel de confianza para decidir dónde mejorar accesos, señalización y servicios.

## Hipótesis a validar (§02.4)

Son hipótesis, no hechos. Los datos de arriba no las prueban.

- **H1.** Los visitantes con restricciones de movilidad, edad o presupuesto no encuentran información suficiente para planear y, por eso, se concentran en pocos sitios o renuncian.
- **H2.** Una recomendación explicable que respete restricciones e incluya destinos alternativos aumenta la aceptación de rutas fuera de los polos principales.
- **H3.** Las barreras reportadas por visitantes, agregadas y moderadas, permiten priorizar intervenciones concretas (rampa, baño, señalética) en corredores específicos.

Validación mínima prevista: 5–10 entrevistas cortas o una encuesta breve con consentimiento y sin datos personales. Si no se logra durante el hackathon, se dirá explícitamente. Estado: NO VERIFICADO.

## Fuera de alcance de la afirmación (§02.6)

La muestra de usuarios de la aplicación no representa al turismo de Puebla. Solo se reporta el comportamiento observado de participantes.
