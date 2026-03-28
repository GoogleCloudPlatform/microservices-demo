const DEFAULT_API_BASE = '/api'

export function getApiBase(env = import.meta.env) {
  const envBase = env?.VITE_API_BASE_URL
  if (envBase && typeof envBase === 'string' && envBase.trim()) {
    return envBase.trim().replace(/\/$/, '')
  }
  return DEFAULT_API_BASE
}

export function getApiToken(env = import.meta.env) {
  const token = env?.VITE_AEGIS_API_TOKEN
  return token && typeof token === 'string' && token.trim() ? token.trim() : ''
}

export function getOperatorHeaders(env = import.meta.env) {
  const token = getApiToken(env)
  return token ? { 'X-Aegis-Token': token } : {}
}

export const API_BASE = getApiBase()
export const OPERATOR_HEADERS = getOperatorHeaders()

export function apiUrl(path) {
  const normalized = path.startsWith('/') ? path : `/${path}`
  return `${API_BASE}${normalized}`
}

export async function apiFetch(path, options = {}) {
  const headers = { ...(options.headers || {}) }
  return fetch(apiUrl(path), {
    credentials: 'include',
    ...options,
    headers,
  })
}

export async function apiJson(path, options = {}) {
  const res = await apiFetch(path, options)
  let payload = null
  try {
    payload = await res.json()
  } catch {
    payload = null
  }
  if (!res.ok) {
    const message = payload?.detail || payload?.message || `HTTP ${res.status}`
    const error = new Error(message)
    error.status = res.status
    error.payload = payload
    throw error
  }
  return payload
}
