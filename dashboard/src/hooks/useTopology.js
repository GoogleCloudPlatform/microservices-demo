import { useState, useEffect, useRef, useCallback } from 'react'
import { API_BASE, OPERATOR_HEADERS } from '../api'
const POLL_MS = 2000

export function useTopology() {
  const [data, setData] = useState(null)
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState(null)
  const intervalRef = useRef(null)

  const fetchTopology = useCallback(async () => {
    const ctrl = new AbortController()
    const timer = setTimeout(() => ctrl.abort(), 4000)
    try {
      const res = await fetch(`${API_BASE}/topology`, { signal: ctrl.signal })
      clearTimeout(timer)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const json = await res.json()
      setData(json)
      setConnected(true)
      setError(null)
    } catch (e) {
      clearTimeout(timer)
      setConnected(false)
      setError(e.name === 'AbortError' ? 'API timeout' : e.message)
    }
  }, [])

  useEffect(() => {
    fetchTopology()
    intervalRef.current = setInterval(fetchTopology, POLL_MS)
    return () => clearInterval(intervalRef.current)
  }, [fetchTopology])

  const fetchWindow = useCallback(async (service) => {
    try {
      const res = await fetch(`${API_BASE}/window/${service}`)
      return await res.json()
    } catch { return null }
  }, [])

  const triggerRemediation = useCallback(async (service, failureType = 'generic_anomaly') => {
    const res = await fetch(`${API_BASE}/remediate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...OPERATOR_HEADERS },
      body: JSON.stringify({ service, failure_type: failureType }),
    })
    return await res.json()
  }, [])

  const triggerDemo = useCallback(async (service = 'recommendationservice', owner = 'operator') => {
    const res = await fetch(`${API_BASE}/demo/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...OPERATOR_HEADERS },
      body: JSON.stringify({ service, owner }),
    })
    if (!res.ok) {
      const payload = await res.json().catch(() => ({}))
      throw new Error(payload?.detail || `HTTP ${res.status}`)
    }
    return await res.json()
  }, [])

  return { data, connected, error, fetchWindow, triggerRemediation, triggerDemo }
}
