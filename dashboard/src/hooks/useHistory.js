import { useState, useEffect } from 'react'
import { API_BASE } from '../api'

export function useHistory() {
  const [history, setHistory] = useState([])
  const [incidents, setIncidents] = useState([])

  useEffect(() => {
    const fetchH = async () => {
      try {
        const res = await fetch(`${API_BASE}/history`)
        if (res.ok) {
          const payload = await res.json()
          setHistory(payload.snapshots || payload)
        }
      } catch {}
    }
    const fetchI = async () => {
      try {
        const res = await fetch(`${API_BASE}/incidents/history?limit=20`)
        if (res.ok) {
          const payload = await res.json()
          setIncidents(payload.incidents || payload)
        }
      } catch {}
    }
    fetchH(); fetchI()
    const t1 = setInterval(fetchH, 10000)
    const t2 = setInterval(fetchI, 30000)
    return () => { clearInterval(t1); clearInterval(t2) }
  }, [])

  return { history, incidents }
}
