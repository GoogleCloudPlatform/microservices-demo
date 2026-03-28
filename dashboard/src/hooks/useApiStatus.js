import { useState, useEffect, useRef, useCallback } from 'react'

const API_BASE = 'http://localhost:8001'
const POLL_INTERVAL = 2000
const MAX_HISTORY = 30

export function useApiStatus() {
  const [status, setStatus] = useState(null)
  const [history, setHistory] = useState([])
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
  const intervalRef = useRef(null)

  const fetchStatus = useCallback(async () => {
    // Manual timeout — AbortSignal.timeout() has patchy browser support
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), 4000)

    try {
      const res = await fetch(`${API_BASE}/status`, { signal: controller.signal })
      clearTimeout(timer)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()

      setStatus(data)
      setConnected(true)
      setError(null)
      setLoading(false)

      // Append to local history for chart
      setHistory(prev => {
        const snapshot = {
          timestamp: data.timestamp,
          scores: data.services
            ? Object.fromEntries(
                Object.entries(data.services).map(([svc, v]) => [svc, v.combined_score])
              )
            : {},
        }
        const next = [...prev, snapshot]
        return next.length > MAX_HISTORY ? next.slice(-MAX_HISTORY) : next
      })
    } catch (err) {
      clearTimeout(timer)
      // AbortError = timeout; TypeError = network down
      const msg = err.name === 'AbortError' ? 'Timeout (API slow or down)' : (err.message || 'Connection failed')
      setConnected(false)
      setError(msg)
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchStatus()
    intervalRef.current = setInterval(fetchStatus, POLL_INTERVAL)
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [fetchStatus])

  const triggerRemediation = useCallback(async (service, failureType) => {
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), 30000) // 30s for remediation
    try {
      const res = await fetch(`${API_BASE}/remediate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ service, failure_type: failureType }),
        signal: controller.signal,
      })
      clearTimeout(timer)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      return await res.json()
    } catch (err) {
      clearTimeout(timer)
      throw new Error(`Remediation failed: ${err.message}`)
    }
  }, [])

  return {
    status,
    history,
    connected,
    error,
    loading,
    triggerRemediation,
    refetch: fetchStatus,
  }
}
