import { Component, useState, useEffect, useCallback, useRef } from 'react'
import { useTopology } from './hooks/useTopology'
import { useHistory } from './hooks/useHistory'
import { useInfrastructure } from './hooks/useInfrastructure'
import { useModelInsights } from './hooks/useModelInsights'
import { useSystemLogs } from './hooks/useSystemLogs'
import { useAuth } from './hooks/useAuth'
import { ThemeProvider, useTheme } from './ThemeContext'
import SolarSystem from './components/SolarSystem'
import InfoPanel from './components/InfoPanel'
import ServiceDetail from './components/ServiceDetail'
import InfraPage from './components/InfraPage'
import ModelsPage from './components/ModelsPage'
import LogsPage from './components/LogsPage'
import AuthGate from './components/AuthGate'

class PageBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, message: '' }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, message: error?.message || 'Unknown page error' }
  }

  componentDidUpdate(prevProps) {
    if (prevProps.resetKey !== this.props.resetKey && this.state.hasError) {
      this.setState({ hasError: false, message: '' })
    }
  }

  render() {
    const { theme, label } = this.props
    if (this.state.hasError) {
      return (
        <div style={{ flex: 1, padding: 32, color: theme.text, background: theme.bg, overflowY: 'auto' }}>
          <div style={{ maxWidth: 760, border: `1px solid ${theme.borderLight}`, background: theme.card, padding: 24 }}>
            <div style={{ fontSize: 12, letterSpacing: 1.6, textTransform: 'uppercase', color: theme.textMuted, marginBottom: 10 }}>
              {label || 'Page Error'}
            </div>
            <div style={{ fontSize: 28, lineHeight: 1.05, marginBottom: 12 }}>
              This page hit a rendering error.
            </div>
            <div style={{ fontSize: 12, lineHeight: 1.6, color: theme.textMuted }}>
              The rest of the dashboard is still available. Navigate to another tab or try refreshing.
            </div>
            <div style={{ marginTop: 16, fontSize: 11, color: theme.accent }}>
              {this.state.message}
            </div>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}

function getPageFromLocation() {
  if (typeof window === 'undefined') return 'solar'
  const hash = window.location.hash.replace('#', '').trim().toLowerCase()
  if (hash === 'infra') return 'infra'
  if (hash === 'models') return 'models'
  if (hash === 'logs') return 'logs'
  return 'solar'
}

function DashboardApp({ auth, onLogout }) {
  const { theme, dark, setDark } = useTheme()
  const { data, connected, error, fetchWindow, triggerRemediation, triggerDemo, refreshTopology } = useTopology()
  const { history, incidents } = useHistory()
  const { infrastructure, refreshInfrastructure } = useInfrastructure()
  const { insights: modelInsights, refreshInsights } = useModelInsights()
  const systemLogs = useSystemLogs()
  const [selectedService, setSelectedService] = useState(null)
  const [windowData, setWindowData] = useState(null)
  const [windowLoading, setWindowLoading] = useState(false)
  const [page, setPage] = useState(getPageFromLocation)
  const [demoBusy, setDemoBusy] = useState(false)
  const windowAbortRef = useRef(null)

  useEffect(() => {
    const onHashChange = () => setPage(getPageFromLocation())
    window.addEventListener('hashchange', onHashChange)
    onHashChange()
    return () => window.removeEventListener('hashchange', onHashChange)
  }, [])

  useEffect(() => {
    const nextHash = page === 'infra' ? '#infra' : page === 'models' ? '#models' : page === 'logs' ? '#logs' : '#solar'
    if (window.location.hash !== nextHash) {
      window.history.replaceState(null, '', nextHash)
    }
  }, [page])

  const handleSelectService = useCallback(async (svc) => {
    if (svc === selectedService) { setSelectedService(null); setWindowData(null); return }
    windowAbortRef.current?.abort()
    const ctrl = new AbortController()
    windowAbortRef.current = ctrl
    setSelectedService(svc)
    setWindowLoading(true)
    const wd = await fetchWindow(svc, ctrl.signal)
    if (!ctrl.signal.aborted) {
      setWindowData(wd)
      setWindowLoading(false)
    }
  }, [selectedService, fetchWindow])

  useEffect(() => {
    if (!selectedService) return
    const ctrl = new AbortController()
    windowAbortRef.current = ctrl
    const interval = setInterval(async () => {
      const wd = await fetchWindow(selectedService, ctrl.signal)
      if (!ctrl.signal.aborted) setWindowData(wd)
    }, 5000)
    return () => {
      ctrl.abort()
      clearInterval(interval)
    }
  }, [selectedService, fetchWindow])

  const selectedData = data?.services?.[selectedService]
  const latestDemo = data?.demo_run || null
  const demoRunning = latestDemo?.status === 'running'
  const canOperate = !auth?.config?.login_required || Boolean(auth?.user?.operator)
  const DOT_GRID = `radial-gradient(circle, ${theme.bgDot} 1px, transparent 1px)`

  const handleDemoRun = useCallback(async () => {
    setDemoBusy(true)
    try {
      await triggerDemo('recommendationservice', auth?.user?.email || auth?.user?.name || 'operator')
      refreshTopology()
      refreshInfrastructure()
      refreshInsights()
      systemLogs.refreshLogs()
      setPage('logs')
    } catch (demoError) {
      console.error('Demo run failed to start:', demoError)
    } finally {
      setDemoBusy(false)
    }
  }, [auth, refreshInfrastructure, refreshInsights, refreshTopology, systemLogs, triggerDemo])

  const navBtn = (key, label, hint) => ({
    type: 'button',
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
            <button {...navBtn('models', 'MODEL INSIGHTS', 'ML telemetry')} />
            <button {...navBtn('logs', 'SYSTEM LOGS', 'Timeline and persistence')} />
            <button
              onClick={handleDemoRun}
              disabled={demoBusy || demoRunning || !canOperate}
              style={{
                fontFamily: theme.displayFont || theme.font,
                fontSize: 12,
                fontWeight: 600,
                letterSpacing: 0.8,
                padding: '7px 14px 8px',
                borderRadius: 999,
                border: `1px solid ${demoRunning ? theme.accent : theme.borderLight}`,
                background: demoRunning ? theme.accent : 'transparent',
                color: demoRunning ? theme.bg : theme.text,
                cursor: demoBusy || demoRunning || !canOperate ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-start',
                minWidth: 132,
                opacity: demoBusy || demoRunning || !canOperate ? 0.8 : 1,
              }}
            >
              <span>{demoRunning ? 'DEMO RUNNING' : demoBusy ? 'STARTING DEMO' : 'RUN DEMO'}</span>
              <span style={{
                fontFamily: theme.font,
                fontSize: 8,
                letterSpacing: 1.2,
                color: demoRunning ? theme.bg : theme.textMuted,
                marginTop: 2,
                textTransform: 'uppercase',
              }}>
                {demoRunning ? latestDemo?.service || 'Autonomous recovery' : canOperate ? 'Attack + autonomous fix' : 'Operator access required'}
              </span>
            </button>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, fontSize: 10, flexWrap: 'wrap', justifyContent: 'flex-end' }}>
          {auth?.user ? (
            <span style={{ display: 'flex', alignItems: 'center', gap: 8, color: theme.text }}>
              {auth.user.picture_url ? (
                <img
                  src={auth.user.picture_url}
                  alt={auth.user.name || auth.user.email}
                  style={{ width: 22, height: 22, borderRadius: '50%', objectFit: 'cover', border: `1px solid ${theme.borderLight}` }}
                />
              ) : null}
              <span style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', lineHeight: 1.1 }}>
                <span style={{ fontSize: 10 }}>{auth.user.name || auth.user.email}</span>
                <span style={{ color: theme.textMuted, fontSize: 8, letterSpacing: 1.2, textTransform: 'uppercase' }}>
                  {auth.user.operator ? 'operator' : 'viewer'}
                </span>
              </span>
            </span>
          ) : null}
          <span style={{ display: 'flex', alignItems: 'center', gap: 5, color: connected ? '#2a8a2a' : '#cc2222' }}>
            <span style={{ width: 7, height: 7, borderRadius: '50%', display: 'inline-block', background: connected ? '#2a8a2a' : '#cc2222', animation: connected ? 'pulse 2s infinite' : 'none' }} />
            {connected ? 'Backend connected' : `Backend offline${error ? `: ${error}` : ''}`}
          </span>
          <span style={{ color: theme.textMuted }}>{new Date().toLocaleTimeString('en-US', { hour12: false })}</span>
          {auth?.config?.login_required ? (
            <button
              onClick={onLogout}
              style={{
                fontFamily: theme.font,
                fontSize: 10,
                padding: '3px 10px',
                border: `1px solid ${theme.borderLight}`,
                background: 'transparent',
                color: theme.textMuted,
                cursor: 'pointer',
                letterSpacing: 1,
              }}
            >
              LOG OUT
            </button>
          ) : null}
          <button onClick={() => setDark(d => !d)} style={{ fontFamily: theme.font, fontSize: 10, padding: '3px 10px', border: `1px solid ${theme.borderLight}`, background: 'transparent', color: theme.textMuted, cursor: 'pointer', letterSpacing: 1 }}>
            {dark ? '☀ LIGHT' : '◑ DARK'}
          </button>
        </div>
      </div>

      {page === 'solar' ? (
        <PageBoundary resetKey={`solar-${data?.timestamp || 'none'}`} theme={theme} label="Solar System">
          <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
            <div style={{ flex: 1, position: 'relative', borderRight: `2px solid ${theme.border}`, overflow: 'hidden' }}>
              <SolarSystem topology={data} selectedService={selectedService} onSelectService={handleSelectService} />
            </div>
            <div style={{ width: 300, flexShrink: 0, background: theme.bg, overflowY: 'auto' }}>
              <InfoPanel topology={data}>
                {selectedService && selectedData && (
                  <ServiceDetail service={selectedService} data={selectedData} windowData={windowLoading ? null : windowData} onRemediate={canOperate ? triggerRemediation : null} onClose={() => { setSelectedService(null); setWindowData(null) }} />
                )}
              </InfoPanel>
            </div>
          </div>
        </PageBoundary>
      ) : page === 'infra' ? (
        <PageBoundary resetKey={`infra-${data?.timestamp || 'none'}-${infrastructure?.timestamp || 'none'}`} theme={theme} label="Infrastructure">
          <InfraPage topology={data} history={history} incidents={incidents} connected={connected} infrastructure={infrastructure} />
        </PageBoundary>
      ) : page === 'models' ? (
        <PageBoundary resetKey={`models-${data?.timestamp || 'none'}`} theme={theme} label="Model Insights">
          <ModelsPage insights={modelInsights} topology={data} history={history} connected={connected} />
        </PageBoundary>
      ) : (
        <PageBoundary resetKey={`logs-${systemLogs.timestamp || 'none'}`} theme={theme} label="System Logs">
          <LogsPage events={systemLogs.events} logs={systemLogs.logs} timestamp={systemLogs.timestamp} topology={data} connected={connected} />
        </PageBoundary>
      )}

      <div style={{ height: 26, borderTop: `1px solid ${theme.borderLight}`, display: 'flex', alignItems: 'center', padding: '0 16px', gap: 20, fontSize: 9, color: theme.textMuted, background: theme.bg, flexShrink: 0 }}>
        <span>{page === 'infra' ? 'Direct link: #infra' : page === 'models' ? 'Direct link: #models' : page === 'logs' ? 'Direct link: #logs' : 'Direct link: #solar'}</span>
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

function AppInner() {
  const { theme } = useTheme()
  const auth = useAuth()

  const handleLogin = useCallback(async (credential) => {
    await auth.loginWithGoogle(credential)
    await auth.refreshAuth()
  }, [auth])

  const handleLogout = useCallback(async () => {
    await auth.logout()
  }, [auth])

  if (auth.loading && !auth.config) {
    return (
      <div style={{ width: '100vw', height: '100vh', display: 'grid', placeItems: 'center', background: theme.bg, color: theme.textMuted }}>
        Checking access…
      </div>
    )
  }

  if (auth.config?.login_required && !auth.authenticated) {
    return <AuthGate theme={theme} config={auth.config} loading={auth.loading} error={auth.error} onLogin={handleLogin} />
  }

  return <DashboardApp auth={auth} onLogout={handleLogout} />
}

export default function App() {
  return (
    <ThemeProvider>
      <AppInner />
    </ThemeProvider>
  )
}
