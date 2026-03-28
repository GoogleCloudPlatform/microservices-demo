import { describe, expect, it } from 'vitest'
import { apiUrl, getApiBase, getApiToken, getOperatorHeaders } from './api'

describe('getApiBase', () => {
  it('defaults to the in-app API path', () => {
    expect(getApiBase({})).toBe('/api')
  })

  it('normalizes a configured API base URL', () => {
    expect(getApiBase({ VITE_API_BASE_URL: 'https://example.com/api/' })).toBe('https://example.com/api')
  })
})

describe('apiUrl', () => {
  it('prefixes relative paths with /api', () => {
    expect(apiUrl('/health')).toBe('/api/health')
    expect(apiUrl('health')).toBe('/api/health')
  })
})

describe('operator auth helpers', () => {
  it('returns an empty token when unset', () => {
    expect(getApiToken({})).toBe('')
    expect(getOperatorHeaders({})).toEqual({})
  })

  it('builds the aegis token header when configured', () => {
    expect(getApiToken({ VITE_AEGIS_API_TOKEN: 'secret-token' })).toBe('secret-token')
    expect(getOperatorHeaders({ VITE_AEGIS_API_TOKEN: 'secret-token' })).toEqual({ 'X-Aegis-Token': 'secret-token' })
  })
})
