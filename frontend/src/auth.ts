import Keycloak from 'keycloak-js';

export const keycloak = new Keycloak({
  url: import.meta.env.VITE_KEYCLOAK_URL ?? 'http://localhost:8080',
  realm: 'semcache',
  clientId: 'semcache-frontend',
});

let ready: Promise<boolean> | null = null;

export function initAuth(): Promise<boolean> {
  ready ??= keycloak.init({ onLoad: 'login-required', pkceMethod: 'S256', checkLoginIframe: false });
  return ready;
}

export async function token(): Promise<string> {
  try {
    await keycloak.updateToken(30);
  } catch {
    keycloak.login();
  }
  return keycloak.token ?? '';
}

export function logout() {
  keycloak.logout({ redirectUri: window.location.origin + '/' });
}
