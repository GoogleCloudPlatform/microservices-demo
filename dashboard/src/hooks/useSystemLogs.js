import { useEffect, useRef, useState } from 'react'
import { apiFetch } from '../api'

const POLL_MS = 2000

export function useSystemLogs() {
  const [events, setEvents] = useState([])
  const [logs, setLogs] = useState([])
  const [timestamp, setTimestamp] = useState(null)
  const abortRef = useRef(null)

  const fetchAll = async () => {
    abortRef.current?.abort()
    const ctrl = new AbortController()
    abortRef.current = ctrl
    try {
      const [eventsRes, logsRes] = await Promise.all([
        apiFetch('/events?limit=120', { signal: ctrl.signal }),
        apiFetch('/logs?limit=250', { signal: ctrl.signal }),
      ])

      if (!ctrl.signal.aborted && eventsRes.ok) {
        const payload = await eventsRes.json()
        setEvents(payload.events || [])
        setTimestamp(payload.timestamp || new Date().toISOString())
      }
      if (!ctrl.signal.aborted && logsRes.ok) {
        const payload = await logsRes.json()
        setLogs(payload.logs || [])
        setTimestamp(payload.timestamp || new Date().toISOString())
      }
    } catch {}
  }

  useEffect(() => {
    fetchAll()
    const timer = setInterval(fetchAll, POLL_MS)

    return () => {
      abortRef.current?.abort()
      clearInterval(timer)
    }
  }, [])

  return { events, logs, timestamp, refreshLogs: fetchAll }
}
