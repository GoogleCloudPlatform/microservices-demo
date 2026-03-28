import { useEffect, useRef, useState } from 'react'
import { apiFetch } from '../api'

const POLL_MS = 2000

export function useInfrastructure() {
  const [infrastructure, setInfrastructure] = useState(null)
  const abortRef = useRef(null)

  const fetchInfrastructure = async () => {
    abortRef.current?.abort()
    const ctrl = new AbortController()
    abortRef.current = ctrl
    try {
      const res = await apiFetch('/infrastructure', { signal: ctrl.signal })
      if (!res.ok) return
      const payload = await res.json()
      if (!ctrl.signal.aborted) setInfrastructure(payload)
    } catch {}
  }

  useEffect(() => {
    fetchInfrastructure()
    const timer = setInterval(fetchInfrastructure, POLL_MS)

    return () => {
      abortRef.current?.abort()
      clearInterval(timer)
    }
  }, [])

  return { infrastructure, refreshInfrastructure: fetchInfrastructure }
}
