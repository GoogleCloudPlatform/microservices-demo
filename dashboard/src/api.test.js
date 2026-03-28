import { describe, expect, it } from 'vitest'
import { getApiBase } from './api'

describe('getApiBase', () => {
  it('defaults to the in-app API path', () => {
    expect(getApiBase({})).toBe('/api')
  })

  it('normalizes a configured API base URL', () => {
    expect(getApiBase({ VITE_API_BASE_URL: 'https://example.com/api/' })).toBe('https://example.com/api')
  })
})
