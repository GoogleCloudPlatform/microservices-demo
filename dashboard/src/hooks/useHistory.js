import { useState, useEffect, useRef } from 'react'
import { apiFetch } from '../api'

const HISTORY_POLL_MS = 4000
const INCIDENT_POLL_MS = 4000

export function useHistory() {
  const [history, setHistory] = useState([])
  const [incidents, setIncidents] = useState([])
  const abortRef = useRef(null)

  useEffect(() => {
    const ctrl = new AbortController()
    abortRef.current = ctrl

    const fetchH = async () => {
      try {
        const res = await apiFetch('/history', { signal: ctrl.signal })
        if (res.ok) {
          const payload = await res.json()
          setHistory(Array.isArray(payload.snapshots || payload) ? (payload.snapshots || payload) : [])
        }
      } catch {}
    }
    const fetchI = async () => {
      try {
        const res = await apiFetch('/incidents/history?limit=20', { signal: ctrl.signal })
        if (res.ok) {
          const payload = await res.json()
          setIncidents(Array.isArray(payload.incidents || payload) ? (payload.incidents || payload) : [])
        }
      } catch {}
    }
    fetchH(); fetchI()
    const t1 = setInterval(fetchH, HISTORY_POLL_MS)
    const t2 = setInterval(fetchI, INCIDENT_POLL_MS)
    return () => {
      ctrl.abort()
      clearInterval(t1)
      clearInterval(t2)
    }
  }, [])

  return { history, incidents }
}
