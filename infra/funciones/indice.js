// Agrega index.html a las rutas de carpeta (/ruta/ y /ruta) para servir páginas estáticas desde S3.
function handler(event) {
  var request = event.request;
  var uri = request.uri;

  if (uri.endsWith('/')) {
    request.uri = uri + 'index.html';
  } else if (uri.split('/').pop().indexOf('.') === -1) {
    request.uri = uri + '/index.html';
  }

  return request;
}
