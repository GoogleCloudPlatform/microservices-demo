import { useEffect, useState } from 'react'
import { API_BASE } from '../api'

export function useInfrastructure() {
  const [infrastructure, setInfrastructure] = useState(null)

  useEffect(() => {
    let cancelled = false

    const fetchInfrastructure = async () => {
      try {
        const res = await fetch(`${API_BASE}/infrastructure`)
        if (!res.ok) return
        const payload = await res.json()
        if (!cancelled) setInfrastructure(payload)
      } catch {}
    }

    fetchInfrastructure()
    const timer = setInterval(fetchInfrastructure, 5000)

    return () => {
      cancelled = true
      clearInterval(timer)
    }
  }, [])

  return infrastructure
}
