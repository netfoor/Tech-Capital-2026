# Prototipo funcional

- **En línea:** https://puebla-viva-360.vercel.app. Ahí están la app del visitante, `/admin` (Secretaría, con cuenta de demostración) y `/pitch/` (presentación).
- **Local:** `make instalar && make demo && make dev`.
- **Recorrido de la demo:** [`docs/pitch/demo.md`](../pitch/demo.md).

Todas las pruebas automáticas corren con `make verificar`:

- backend con PostGIS real: API, autorización, privacidad, recomendador y tablero;
- pipelines y análisis;
- frontend: interfaz y accesibilidad (axe).
