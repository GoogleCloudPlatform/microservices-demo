import { useState, useEffect, useRef, useCallback } from 'react'
import { OPERATOR_HEADERS, apiFetch, apiJson } from '../api'
const POLL_MS = 2000

export function useTopology() {
  const [data, setData] = useState(null)
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState(null)
  const abortRef = useRef(null)
  const inFlightRef = useRef(false)

  const fetchTopology = useCallback(async () => {
    if (inFlightRef.current) return
    inFlightRef.current = true
    abortRef.current?.abort()
    const ctrl = new AbortController()
    abortRef.current = ctrl
    const timer = setTimeout(() => ctrl.abort(), 4000)
    try {
      const json = await apiJson('/topology', { signal: ctrl.signal })
      clearTimeout(timer)
      if (!ctrl.signal.aborted) {
        setData(json)
        setConnected(true)
        setError(null)
      }
    } catch (e) {
      clearTimeout(timer)
      if (!ctrl.signal.aborted) {
        setConnected(false)
        setError(e.name === 'AbortError' ? 'API timeout' : e.message)
      }
    } finally {
      inFlightRef.current = false
    }
  }, [])

  useEffect(() => {
    fetchTopology()
    const interval = setInterval(fetchTopology, POLL_MS)
    return () => {
      clearInterval(interval)
      abortRef.current?.abort()
    }
  }, [fetchTopology])

  const fetchWindow = useCallback(async (service, signal) => {
    try {
      const res = await apiFetch(`/window/${service}`, signal ? { signal } : undefined)
      if (!res.ok) return null
      return await res.json()
    } catch { return null }
  }, [])

  const triggerRemediation = useCallback(async (service, failureType = 'generic_anomaly') => {
    try {
      const res = await apiFetch('/remediate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...OPERATOR_HEADERS },
        body: JSON.stringify({ service, failure_type: failureType }),
      })
      if (!res.ok) {
        const payload = await res.json().catch(() => ({}))
        throw new Error(payload?.detail || `HTTP ${res.status}`)
      }
      return await res.json()
    } catch (e) {
      return { result: { status: 'manual_required', operator_summary: e.message } }
    }
  }, [])

  const triggerDemo = useCallback(async (service = 'recommendationservice', owner = 'operator') => {
    const res = await apiFetch('/demo/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...OPERATOR_HEADERS },
      body: JSON.stringify({ service, owner }),
    })
    if (!res.ok) {
      const payload = await res.json().catch(() => ({}))
      throw new Error(payload?.detail || `HTTP ${res.status}`)
    }
    return await res.json()
  }, [])

  return { data, connected, error, fetchWindow, triggerRemediation, triggerDemo, refreshTopology: fetchTopology }
}
