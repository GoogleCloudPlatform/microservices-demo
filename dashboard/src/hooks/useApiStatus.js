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
    try {
      const res = await fetch(`${API_BASE}/status`, {
        signal: AbortSignal.timeout(3000),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()

      setStatus(data)
      setConnected(true)
      setError(null)
      setLoading(false)

      // Add to history: record combined scores for top services
      setHistory(prev => {
        const snapshot = {
          timestamp: data.timestamp,
          scores: data.services
            ? Object.fromEntries(
                Object.entries(data.services).map(([svc, v]) => [
                  svc,
                  v.combined_score,
                ])
              )
            : {},
        }
        const next = [...prev, snapshot]
        return next.length > MAX_HISTORY ? next.slice(-MAX_HISTORY) : next
      })
    } catch (err) {
      setConnected(false)
      setError(err.message || 'Connection failed')
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
    try {
      const res = await fetch(`${API_BASE}/remediate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ service, failure_type: failureType }),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      return await res.json()
    } catch (err) {
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
