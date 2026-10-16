# Tareas 005 · Panel ciudadano y TikTok

## Preparación (urgente: el panel necesita tiempo para juntar respuestas)

- [ ] T005-01 Llenar el contacto del aviso de privacidad (`consentimiento.md`) y revisar su redacción jurídica. Verificación: el aviso no tiene marcadores pendientes.
- [ ] T005-02 Crear el formulario con los campos del plan, carga de capturas a una carpeta privada y aceptación obligatoria. Verificación: un envío de prueba completo.
- [ ] T005-03 Sesión piloto del equipo con el protocolo v1: tomar el tiempo, revisar que las cuatro consultas den 12 resultados y ajustar el texto si hace falta. Verificación: tiempo menor a 10 minutos; cambios registrados como `v1.1` si los hubo.
- [ ] T005-04 Mensaje de convocatoria para conocidos y familiares con el enlace del formulario, enviado por los canales del equipo. Verificación: convocatoria enviada; contador de respuestas.

## Procesamiento

- [ ] T005-05 [P] `radar/comun/estadistica.py` con el intervalo de Wilson y sus pruebas. Verificación: `uv run pytest tests/test_estadistica.py`.
- [ ] T005-06 Plantilla `data/privado/panel/codificacion.csv` y codificación manual de las sesiones recibidas, según las reglas del protocolo. Verificación: ≥ 15 sesiones codificadas.
- [ ] T005-07 Doble codificación del 20 % de las sesiones y acuerdo reportado. Verificación: porcentaje de acuerdo en el destino anotado en `09-resultados.md`.
- [ ] T005-08 `radar panel consolidar`: validación, anonimización y presencia con Wilson. Verificación: `panel_observaciones.csv` y `presencia_panel.csv` sin columnas prohibidas (prueba automática).
- [ ] T005-09 Entregar los enlaces y textos del brazo real a la spec 006 (`data/privado/asistentes/brazo_real.csv`). Verificación: archivo con `participante_id`, `texto`, `enlace`, `autoriza_publicar`.

## P1

- [ ] T005-10 [P] Lector automático de capturas y validación contra la codificación manual. Verificación: coincidencia en el destino ≥ 0.9.
- [ ] T005-11 [P] Captura de comentarios de TikTok a `data/privado/comentarios/tiktok.jsonl`, transcrita de las capturas sin autor. Verificación: archivo con `destino_id`, `texto` y `fuente=tiktok`.
