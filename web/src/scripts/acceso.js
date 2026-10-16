// Acceso a la plataforma con Cognito Hosted UI: código de autorización con PKCE (ADR-0009, FR-009-09).
// Sin configuración de Cognito, la plataforma corre en modo local y entra sin cuenta (FR-009-10).

const DOMINIO = import.meta.env.PUBLIC_COGNITO_DOMINIO ?? '';
const CLIENTE = import.meta.env.PUBLIC_COGNITO_CLIENTE_ID ?? '';

export const modoLocal = !DOMINIO || !CLIENTE;

const CLAVE_SESION = 'radar.sesion';
const CLAVE_VERIFICADOR = 'radar.pkce';
const CLAVE_ESTADO = 'radar.estado';
const CLAVE_DESTINO = 'radar.destino';

const urlRegreso = () => `${window.location.origin}/plataforma/`;
const urlSalida = () => `${window.location.origin}/`;

function base64url(bytes) {
  let texto = '';
  bytes.forEach((b) => (texto += String.fromCharCode(b)));
  return btoa(texto).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function aleatorio(n = 32) {
  return base64url(crypto.getRandomValues(new Uint8Array(n)));
}

async function reto(verificador) {
  const huella = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(verificador));
  return base64url(new Uint8Array(huella));
}

function leerCarga(token) {
  const parte = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
  const relleno = parte.padEnd(Math.ceil(parte.length / 4) * 4, '=');
  const bytes = Uint8Array.from(atob(relleno), (c) => c.charCodeAt(0));
  return JSON.parse(new TextDecoder().decode(bytes));
}

/** Sesión vigente ({correo, exp, local}) o null. En modo local siempre hay sesión. */
export function sesion() {
  if (modoLocal) return { correo: null, exp: null, local: true };
  try {
    const guardada = JSON.parse(sessionStorage.getItem(CLAVE_SESION) ?? 'null');
    if (!guardada || guardada.exp * 1000 <= Date.now()) {
      sessionStorage.removeItem(CLAVE_SESION);
      return null;
    }
    return { correo: guardada.correo, exp: guardada.exp, local: false };
  } catch {
    return null;
  }
}

/** Lleva a la Hosted UI. Guarda la ruta actual para volver a ella después. */
export async function iniciarSesion() {
  const verificador = aleatorio(48);
  const estado = aleatorio(16);
  sessionStorage.setItem(CLAVE_VERIFICADOR, verificador);
  sessionStorage.setItem(CLAVE_ESTADO, estado);
  sessionStorage.setItem(CLAVE_DESTINO, window.location.hash);

  const parametros = new URLSearchParams({
    response_type: 'code',
    client_id: CLIENTE,
    redirect_uri: urlRegreso(),
    scope: 'openid email profile',
    state: estado,
    code_challenge: await reto(verificador),
    code_challenge_method: 'S256',
  });
  window.location.assign(`https://${DOMINIO}/oauth2/authorize?${parametros}`);
}

/**
 * Si la página vuelve de la Hosted UI con ?code, cambia el código por el token.
 * Devuelve true si se completó un inicio de sesión. Lanza un error con mensaje en español si falla.
 */
export async function completarInicio() {
  if (modoLocal) return false;
  const consulta = new URLSearchParams(window.location.search);
  if (consulta.has('error')) {
    limpiarUrl();
    throw new Error(consulta.get('error_description') ?? consulta.get('error'));
  }
  const codigo = consulta.get('code');
  if (!codigo) return false;

  const estadoEsperado = sessionStorage.getItem(CLAVE_ESTADO);
  const verificador = sessionStorage.getItem(CLAVE_VERIFICADOR);
  sessionStorage.removeItem(CLAVE_ESTADO);
  sessionStorage.removeItem(CLAVE_VERIFICADOR);
  if (!estadoEsperado || consulta.get('state') !== estadoEsperado || !verificador) {
    limpiarUrl();
    throw new Error('la respuesta del inicio de sesión no corresponde a esta pestaña');
  }

  const respuesta = await fetch(`https://${DOMINIO}/oauth2/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'authorization_code',
      client_id: CLIENTE,
      code: codigo,
      redirect_uri: urlRegreso(),
      code_verifier: verificador,
    }),
  });
  if (!respuesta.ok) {
    limpiarUrl();
    throw new Error('Cognito rechazó el código de acceso');
  }
  const { id_token: tokenId } = await respuesta.json();
  const carga = leerCarga(tokenId);
  sessionStorage.setItem(
    CLAVE_SESION,
    JSON.stringify({ correo: carga.email ?? carga['cognito:username'], exp: carga.exp }),
  );
  limpiarUrl(sessionStorage.getItem(CLAVE_DESTINO) ?? '');
  sessionStorage.removeItem(CLAVE_DESTINO);
  return true;
}

function limpiarUrl(fragmento = window.location.hash) {
  window.history.replaceState(null, '', `/plataforma/${fragmento}`);
}

/** Borra la sesión y sale también de la Hosted UI. */
export function cerrarSesion() {
  sessionStorage.removeItem(CLAVE_SESION);
  if (modoLocal) {
    window.location.assign('/');
    return;
  }
  const parametros = new URLSearchParams({ client_id: CLIENTE, logout_uri: urlSalida() });
  window.location.assign(`https://${DOMINIO}/logout?${parametros}`);
}
