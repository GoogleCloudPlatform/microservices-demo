import { useState, useEffect, useCallback } from 'react'
import { useTopology } from './hooks/useTopology'
import { theme } from './styles/theme'
import SolarSystem from './components/SolarSystem'
import InfoPanel from './components/InfoPanel'
import ServiceDetail from './components/ServiceDetail'

const DOT_GRID = `radial-gradient(circle, #c8c0b0 1px, transparent 1px)`

export default function App() {
  const { data, connected, error, fetchWindow, triggerRemediation } = useTopology()
  const [selectedService, setSelectedService] = useState(null)
  const [windowData, setWindowData] = useState(null)
  const [windowLoading, setWindowLoading] = useState(false)

  const handleSelectService = useCallback(async (svc) => {
    if (svc === selectedService) {
      setSelectedService(null)
      setWindowData(null)
      return
    }
    setSelectedService(svc)
    setWindowLoading(true)
    const wd = await fetchWindow(svc)
    setWindowData(wd)
    setWindowLoading(false)
  }, [selectedService, fetchWindow])

  // Refresh window data every 5s when a service is selected
  useEffect(() => {
    if (!selectedService) return
    const interval = setInterval(async () => {
      const wd = await fetchWindow(selectedService)
      setWindowData(wd)
    }, 5000)
    return () => clearInterval(interval)
  }, [selectedService, fetchWindow])

  const selectedData = data?.services?.[selectedService]

  return (
    <div style={{
      width: '100vw', height: '100vh', display: 'flex', flexDirection: 'column',
      background: theme.bg,
      backgroundImage: DOT_GRID,
      backgroundSize: '24px 24px',
      fontFamily: theme.font,
      overflow: 'hidden',
    }}>
      {/* Top bar */}
      <div style={{
        height: 42, borderBottom: `2px solid ${theme.border}`,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '0 20px', background: theme.bg, flexShrink: 0,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <span style={{ fontSize: 13, fontWeight: 'bold', letterSpacing: 2, color: theme.text }}>
            ⊕ MISSION CONTROL
          </span>
          <span style={{ fontSize: 9, color: theme.textMuted, letterSpacing: 1 }}>
            AI OBSERVABILITY PLATFORM — SOLAR SYSTEM INTERFACE
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, fontSize: 10 }}>
          {data?.demo_mode && (
            <span style={{
              border: `1px solid #c45c0a`, color: '#c45c0a',
              padding: '2px 6px', fontSize: 9, letterSpacing: 1,
            }}>DEMO MODE</span>
          )}
          <span style={{ display: 'flex', alignItems: 'center', gap: 5, color: connected ? '#2a8a2a' : '#cc2222' }}>
            <span style={{
              width: 7, height: 7, borderRadius: '50%', display: 'inline-block',
              background: connected ? '#2a8a2a' : '#cc2222',
              animation: connected ? 'pulse 2s infinite' : 'none',
            }} />
            {connected ? 'CONNECTED' : `OFFLINE${error ? ': ' + error : ''}`}
          </span>
          {data && (
            <span style={{ color: theme.textMuted }}>
              {new Date(data.timestamp).toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>

      {/* Main layout */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* Solar system canvas */}
        <div style={{
          flex: 1, position: 'relative', borderRight: `2px solid ${theme.border}`,
          overflow: 'hidden',
        }}>
          <SolarSystem
            topology={data}
            selectedService={selectedService}
            onSelectService={handleSelectService}
          />
        </div>

        {/* Right panel */}
        <div style={{
          width: 300, flexShrink: 0, background: theme.bg,
          overflowY: 'auto',
        }}>
          <InfoPanel
            topology={data}
            selectedService={selectedService}
            serviceData={selectedData}
            windowData={windowData}
            onRemediate={triggerRemediation}
            onClose={() => { setSelectedService(null); setWindowData(null) }}
          >
            {selectedService && (
              <ServiceDetail
                service={selectedService}
                data={selectedData}
                windowData={windowLoading ? null : windowData}
                onRemediate={triggerRemediation}
                onClose={() => { setSelectedService(null); setWindowData(null) }}
              />
            )}
          </InfoPanel>
        </div>
      </div>

      {/* Bottom status bar */}
      <div style={{
        height: 26, borderTop: `1px solid ${theme.borderLight}`,
        display: 'flex', alignItems: 'center', padding: '0 16px', gap: 20,
        fontSize: 9, color: theme.textMuted, background: theme.bg, flexShrink: 0,
      }}>
        <span>Built with React + D3.js (2D) · All animations: CSS keyframes</span>
        <span style={{ marginLeft: 'auto' }}>
          {data ? `${Object.keys(data.services || {}).length} services monitored` : 'Connecting...'}
        </span>
        {selectedService && (
          <span style={{ color: '#c45c0a' }}>
            SELECTED: {selectedService} · Click again to deselect
          </span>
        )}
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: ${theme.bg}; }
        ::-webkit-scrollbar-thumb { background: #aaa; }
      `}</style>
    </div>
  )
}
