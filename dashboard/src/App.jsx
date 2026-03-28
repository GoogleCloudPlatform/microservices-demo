import { theme } from './styles/theme'
import { useApiStatus } from './hooks/useApiStatus'
import ServiceGrid from './components/ServiceGrid'
import AnomalyChart from './components/AnomalyChart'
import AlertPanel from './components/AlertPanel'
import RootCausePanel from './components/RootCausePanel'
import RemediationPanel from './components/RemediationPanel'

const cardStyle = {
  background: theme.colors.card,
  border: `1px solid ${theme.colors.cardBorder}`,
  borderRadius: '14px',
  padding: '20px',
  boxShadow: theme.shadows.card,
}

const sectionTitle = {
  fontSize: '12px',
  fontWeight: 700,
  color: theme.colors.textMuted,
  textTransform: 'uppercase',
  letterSpacing: '1px',
  marginBottom: '16px',
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
}

export default function App() {
  const { status, history, connected, error, loading, triggerRemediation } =
    useApiStatus()

  const services = status?.services || null
  const rootCause = status?.root_cause || null
  const alerts = status?.alerts || []
  const recommendation = status?.recommendation || ''
  const demoMode = status?.demo_mode ?? true
  const rootCauseService = rootCause?.service || rootCause?.root_cause

  return (
    <div
      style={{
        minHeight: '100vh',
        background: theme.colors.bg,
        color: theme.colors.text,
        fontFamily: "'Segoe UI', system-ui, sans-serif",
      }}
    >
      {/* Top bar */}
      <div
        style={{
          background: 'rgba(26, 31, 46, 0.95)',
          backdropFilter: 'blur(10px)',
          borderBottom: `1px solid ${theme.colors.cardBorder}`,
          padding: '0 24px',
          height: '60px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          position: 'sticky',
          top: 0,
          zIndex: 100,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            style={{
              fontSize: '20px',
              fontWeight: 700,
              background: `linear-gradient(135deg, ${theme.colors.accent}, #a29bfe)`,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            AI Observability Platform
          </div>
          {demoMode && (
            <span
              style={{
                background: 'rgba(255, 165, 2, 0.15)',
                border: `1px solid rgba(255,165,2,0.4)`,
                color: theme.colors.warning,
                fontSize: '10px',
                fontWeight: 700,
                padding: '3px 8px',
                borderRadius: '4px',
                letterSpacing: '0.5px',
              }}
            >
              DEMO MODE
            </span>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          {/* Connection status */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div
              style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                background: connected ? theme.colors.success : theme.colors.alertRed,
                boxShadow: connected
                  ? `0 0 8px ${theme.colors.success}`
                  : `0 0 8px ${theme.colors.alertRed}`,
              }}
            />
            <span
              style={{
                fontSize: '12px',
                color: connected ? theme.colors.success : theme.colors.alertRed,
              }}
            >
              {loading
                ? 'Connecting...'
                : connected
                ? 'Connected'
                : `Disconnected${error ? ': ' + error : ''}`}
            </span>
          </div>

          {/* Alert badge */}
          {alerts.length > 0 && (
            <div
              style={{
                background: theme.colors.alertRed,
                color: '#fff',
                fontSize: '11px',
                fontWeight: 700,
                padding: '3px 8px',
                borderRadius: '10px',
                animation: 'pulse 1.5s infinite',
              }}
            >
              {alerts.length} ALERT{alerts.length !== 1 ? 'S' : ''}
            </div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.6; }
        }
      `}</style>

      {/* Main content */}
      <div style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto' }}>
        {/* Service Grid */}
        <div style={{ ...cardStyle, marginBottom: '24px' }}>
          <div style={sectionTitle}>
            <span>⚙️</span>
            <span>Service Health</span>
            <span
              style={{
                marginLeft: 'auto',
                fontSize: '11px',
                color: theme.colors.textDim,
                fontWeight: 400,
                textTransform: 'none',
                letterSpacing: 0,
              }}
            >
              Score 0–100 (higher = more anomalous)
            </span>
          </div>
          <ServiceGrid services={services} rootCauseService={rootCauseService} />
        </div>

        {/* Charts + Alerts row */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '2fr 1fr',
            gap: '24px',
            marginBottom: '24px',
          }}
        >
          {/* Anomaly Chart */}
          <div style={cardStyle}>
            <div style={sectionTitle}>
              <span>📈</span>
              <span>Anomaly Score Trends</span>
              <span
                style={{
                  marginLeft: 'auto',
                  fontSize: '11px',
                  color: theme.colors.textDim,
                  fontWeight: 400,
                  textTransform: 'none',
                  letterSpacing: 0,
                }}
              >
                Top 3 services — last 30 samples
              </span>
            </div>
            <AnomalyChart history={history} />
          </div>

          {/* Alert Panel */}
          <div style={cardStyle}>
            <div style={sectionTitle}>
              <span>🚨</span>
              <span>Active Alerts</span>
            </div>
            <AlertPanel alerts={alerts} />
          </div>
        </div>

        {/* Root Cause + Remediation row */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '24px',
          }}
        >
          {/* Root Cause */}
          <div style={cardStyle}>
            <div style={sectionTitle}>
              <span>🔍</span>
              <span>Root Cause Analysis</span>
            </div>
            <RootCausePanel
              rootCause={rootCause}
              recommendation={recommendation}
            />
          </div>

          {/* Remediation */}
          <div style={cardStyle}>
            <div style={sectionTitle}>
              <span>🔧</span>
              <span>Self-Healing Remediation</span>
            </div>
            <RemediationPanel
              rootCause={rootCause}
              triggerRemediation={triggerRemediation}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
