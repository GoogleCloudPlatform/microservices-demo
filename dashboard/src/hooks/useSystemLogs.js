import { useEffect, useState } from 'react'
import { API_BASE } from '../api'

export function useSystemLogs() {
  const [events, setEvents] = useState([])
  const [logs, setLogs] = useState([])
  const [timestamp, setTimestamp] = useState(null)

  useEffect(() => {
    let cancelled = false

    const fetchAll = async () => {
      try {
        const [eventsRes, logsRes] = await Promise.all([
          fetch(`${API_BASE}/events?limit=120`),
          fetch(`${API_BASE}/logs?limit=250`),
        ])

        if (eventsRes.ok) {
          const payload = await eventsRes.json()
          if (!cancelled) {
            setEvents(payload.events || [])
            setTimestamp(payload.timestamp || new Date().toISOString())
          }
        }
        if (logsRes.ok) {
          const payload = await logsRes.json()
          if (!cancelled) {
            setLogs(payload.logs || [])
            setTimestamp(payload.timestamp || new Date().toISOString())
          }
        }
      } catch {}
    }

    fetchAll()
    const timer = setInterval(fetchAll, 3000)

    return () => {
      cancelled = true
      clearInterval(timer)
    }
  }, [])

  return { events, logs, timestamp }
}
