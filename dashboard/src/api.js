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
