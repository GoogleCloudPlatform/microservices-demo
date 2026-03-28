import { useCallback, useEffect, useState } from 'react'
import { apiJson } from '../api'

export function useAuth() {
  const [config, setConfig] = useState(null)
  const [user, setUser] = useState(null)
  const [authenticated, setAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const refreshAuth = useCallback(async () => {
    setLoading(true)
    try {
      const authConfig = await apiJson('/auth/config')
      setConfig(authConfig)
      if (!authConfig.login_required) {
        setAuthenticated(true)
        setUser(null)
        setError(null)
        return
      }

      const me = await apiJson('/auth/me')
      setAuthenticated(Boolean(me.authenticated))
      setUser(me.user || null)
      setError(null)
    } catch (authError) {
      setAuthenticated(false)
      setUser(null)
      setError(authError.message)
    } finally {
      setLoading(false)
    }
  }, [])

  const loginWithGoogle = useCallback(async (credential) => {
    const payload = await apiJson('/auth/google', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ credential }),
    })
    setAuthenticated(Boolean(payload.authenticated))
    setUser(payload.user || null)
    setError(null)
    return payload
  }, [])

  const logout = useCallback(async () => {
    await apiJson('/auth/logout', { method: 'POST' })
    setAuthenticated(false)
    setUser(null)
  }, [])

  useEffect(() => {
    refreshAuth()
  }, [refreshAuth])

  return {
    config,
    user,
    authenticated,
    loading,
    error,
    refreshAuth,
    loginWithGoogle,
    logout,
  }
}
