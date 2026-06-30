import Cookies from "js-cookie";

export function setCookie(key: string, value: string, option: Cookies.CookieAttributes = {}) {
  Cookies.set(key, value, option);
}

export function getClientCookie(key: string) {
  return Cookies.get(key);
}

export async function getServerCookie(key: string) {
  const { cookies } = await import("next/headers");
  const cookieStore = await cookies();
  return cookieStore.get(key)?.value;
}

const THEME_MODE = "theme-mode";

export function saveMode(mode: string) {
  setCookie(THEME_MODE, mode, { expires: 1, path: "/" });
}

export function getClientMode() {
  const mode = getClientCookie(THEME_MODE);
  return mode === "light" ? "light" : "dark";
}

export async function getServerMode() {
  const mode = await getServerCookie(THEME_MODE);
  return mode === "light" ? "light" : "dark";
}