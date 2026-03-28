import { useState, useEffect, useCallback } from 'react'
import { useTopology } from './hooks/useTopology'
import { useHistory } from './hooks/useHistory'
import { useInfrastructure } from './hooks/useInfrastructure'
import { ThemeProvider, useTheme } from './ThemeContext'
import SolarSystem from './components/SolarSystem'
import InfoPanel from './components/InfoPanel'
import ServiceDetail from './components/ServiceDetail'
import InfraPage from './components/InfraPage'

function getPageFromLocation() {
  if (typeof window === 'undefined') return 'solar'
  const hash = window.location.hash.replace('#', '').trim().toLowerCase()
  return hash === 'infra' ? 'infra' : 'solar'
}

function AppInner() {
  const { theme, dark, setDark } = useTheme()
  const { data, connected, error, fetchWindow, triggerRemediation } = useTopology()
  const { history, incidents } = useHistory()
  const infrastructure = useInfrastructure()
  const [selectedService, setSelectedService] = useState(null)
  const [windowData, setWindowData] = useState(null)
  const [windowLoading, setWindowLoading] = useState(false)
  const [page, setPage] = useState(getPageFromLocation)
  const [, setTick] = useState(0)

  useEffect(() => {
    const t = setInterval(() => setTick(n => n + 1), 500)
    return () => clearInterval(t)
  }, [])

  useEffect(() => {
    const onHashChange = () => setPage(getPageFromLocation())
    window.addEventListener('hashchange', onHashChange)
    onHashChange()
    return () => window.removeEventListener('hashchange', onHashChange)
  }, [])

  useEffect(() => {
    const nextHash = page === 'infra' ? '#infra' : '#solar'
    if (window.location.hash !== nextHash) {
      window.history.replaceState(null, '', nextHash)
    }
  }, [page])

  const handleSelectService = useCallback(async (svc) => {
    if (svc === selectedService) { setSelectedService(null); setWindowData(null); return }
    setSelectedService(svc)
    setWindowLoading(true)
    const wd = await fetchWindow(svc)
    setWindowData(wd)
    setWindowLoading(false)
  }, [selectedService, fetchWindow])

  useEffect(() => {
    if (!selectedService) return
    const interval = setInterval(async () => {
      const wd = await fetchWindow(selectedService)
      setWindowData(wd)
    }, 5000)
    return () => clearInterval(interval)
  }, [selectedService, fetchWindow])

  const selectedData = data?.services?.[selectedService]
  const DOT_GRID = `radial-gradient(circle, ${theme.bgDot} 1px, transparent 1px)`

  const navBtn = (key, label, hint) => ({
    style: {
      fontFamily: theme.displayFont || theme.font,
      fontSize: 12,
      fontWeight: page === key ? 600 : 400,
      letterSpacing: 0.8,
      padding: '7px 14px 8px',
      borderRadius: 999,
      border: `1px solid ${page === key ? theme.border : theme.borderLight}`,
      background: page === key ? theme.border : 'transparent',
      color: page === key ? theme.bg : theme.text,
      cursor: 'pointer',
      transition: 'all 0.2s',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'flex-start',
      minWidth: 132,
    },
    onClick: () => setPage(key),
    children: (
      <>
        <span>{label}</span>
        <span style={{
          fontFamily: theme.font,
          fontSize: 8,
          letterSpacing: 1.2,
          color: page === key ? theme.bg : theme.textMuted,
          marginTop: 2,
          textTransform: 'uppercase',
        }}>
          {hint}
        </span>
      </>
    ),
  })

  return (
    <div style={{ width: '100vw', height: '100vh', display: 'flex', flexDirection: 'column', background: theme.bg, backgroundImage: DOT_GRID, backgroundSize: '24px 24px', fontFamily: theme.font, overflow: 'hidden' }}>
      {/* Top bar */}
      <div style={{ minHeight: 58, borderBottom: `2px solid ${theme.border}`, display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 20px', background: theme.bg, flexShrink: 0, gap: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 20, minWidth: 0 }}>
          <span style={{ fontSize: 24, fontWeight: 900, letterSpacing: 6, color: theme.text, lineHeight: 1 }}>AEGIS</span>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <button {...navBtn('solar', 'SOLAR SYSTEM', 'Service topology')} />
            <button {...navBtn('infra', 'INFRASTRUCTURE', 'Cluster operations')} />
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, fontSize: 10, flexWrap: 'wrap', justifyContent: 'flex-end' }}>
          <span style={{
            fontFamily: theme.font,
            color: theme.textMuted,
            letterSpacing: 1.4,
            textTransform: 'uppercase',
          }}>
            {page === 'infra' ? 'View: Infrastructure' : 'View: Solar System'}
          </span>
          {data?.demo_mode && <span style={{ border: `1px solid ${theme.accent}`, color: theme.accent, padding: '2px 6px', fontSize: 9, letterSpacing: 1 }}>DEMO SCORING ACTIVE</span>}
          <span style={{ display: 'flex', alignItems: 'center', gap: 5, color: connected ? '#2a8a2a' : '#cc2222' }}>
            <span style={{ width: 7, height: 7, borderRadius: '50%', display: 'inline-block', background: connected ? '#2a8a2a' : '#cc2222', animation: connected ? 'pulse 2s infinite' : 'none' }} />
            {connected ? 'Backend connected' : `Backend offline${error ? `: ${error}` : ''}`}
          </span>
          <span style={{ color: theme.textMuted }}>{new Date().toLocaleTimeString('en-US', { hour12: false })}</span>
          <button onClick={() => setDark(d => !d)} style={{ fontFamily: theme.font, fontSize: 10, padding: '3px 10px', border: `1px solid ${theme.borderLight}`, background: 'transparent', color: theme.textMuted, cursor: 'pointer', letterSpacing: 1 }}>
            {dark ? '☀ LIGHT' : '◑ DARK'}
          </button>
        </div>
      </div>

      {page === 'solar' ? (
        <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
          <div style={{ flex: 1, position: 'relative', borderRight: `2px solid ${theme.border}`, overflow: 'hidden' }}>
            <SolarSystem topology={data} selectedService={selectedService} onSelectService={handleSelectService} />
          </div>
          <div style={{ width: 300, flexShrink: 0, background: theme.bg, overflowY: 'auto' }}>
            <InfoPanel topology={data}>
              {selectedService && (
                <ServiceDetail service={selectedService} data={selectedData} windowData={windowLoading ? null : windowData} onRemediate={triggerRemediation} onClose={() => { setSelectedService(null); setWindowData(null) }} />
              )}
            </InfoPanel>
          </div>
        </div>
      ) : (
        <InfraPage topology={data} history={history} incidents={incidents} connected={connected} infrastructure={infrastructure} />
      )}

      <div style={{ height: 26, borderTop: `1px solid ${theme.borderLight}`, display: 'flex', alignItems: 'center', padding: '0 16px', gap: 20, fontSize: 9, color: theme.textMuted, background: theme.bg, flexShrink: 0 }}>
        <span>{page === 'infra' ? 'Direct link: #infra' : 'Direct link: #solar'}</span>
        <span style={{ marginLeft: 'auto' }}>{data ? `${Object.keys(data.services || {}).length} services monitored` : 'Connecting...'}</span>
        {selectedService && page === 'solar' && <span style={{ color: theme.accent }}>SELECTED: {selectedService} · Click again to deselect</span>}
      </div>

      <style>{`
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: ${theme.bg}; }
        ::-webkit-scrollbar-thumb { background: ${theme.borderLight}; }
      `}</style>
    </div>
  )
}

export default function App() {
  return (
    <ThemeProvider>
      <AppInner />
    </ThemeProvider>
  )
}
