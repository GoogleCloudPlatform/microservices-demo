import { useEffect, useRef, useState } from 'react'
import { API_BASE } from '../api'

const POLL_MS = 2000

export function useModelInsights() {
  const [insights, setInsights] = useState(null)
  const abortRef = useRef(null)

  const fetchInsights = async () => {
    abortRef.current?.abort()
    const ctrl = new AbortController()
    abortRef.current = ctrl
    try {
      const res = await fetch(`${API_BASE}/ml/insights`, { signal: ctrl.signal })
      if (!res.ok) return
      const payload = await res.json()
      if (!ctrl.signal.aborted) setInsights(payload)
    } catch {}
  }

  useEffect(() => {
    fetchInsights()
    const timer = setInterval(fetchInsights, POLL_MS)

    return () => {
      abortRef.current?.abort()
      clearInterval(timer)
    }
  }, [])

  return { insights, refreshInsights: fetchInsights }
}
