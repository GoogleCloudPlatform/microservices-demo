import { useEffect, useState } from 'react'
import { API_BASE } from '../api'

export function useModelInsights() {
  const [insights, setInsights] = useState(null)

  useEffect(() => {
    let cancelled = false

    const fetchInsights = async () => {
      try {
        const res = await fetch(`${API_BASE}/ml/insights`)
        if (!res.ok) return
        const payload = await res.json()
        if (!cancelled) setInsights(payload)
      } catch {}
    }

    fetchInsights()
    const timer = setInterval(fetchInsights, 5000)

    return () => {
      cancelled = true
      clearInterval(timer)
    }
  }, [])

  return insights
}
