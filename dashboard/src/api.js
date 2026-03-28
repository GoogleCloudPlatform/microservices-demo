const DEFAULT_API_BASE = '/api'

export function getApiBase(env = import.meta.env) {
  const envBase = env?.VITE_API_BASE_URL
  if (envBase && typeof envBase === 'string' && envBase.trim()) {
    return envBase.trim().replace(/\/$/, '')
  }
  return DEFAULT_API_BASE
}

export const API_BASE = getApiBase()
