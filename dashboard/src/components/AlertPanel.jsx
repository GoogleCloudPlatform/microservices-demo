import { theme, getScoreColor } from '../styles/theme'

function formatTime(isoStr) {
  if (!isoStr) return ''
  try {
    const d = new Date(isoStr)
    return d.toLocaleTimeString()
  } catch {
    return isoStr
  }
}

function AlertItem({ alert }) {
  const scoreColor = getScoreColor(alert.score)
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '10px 14px',
        background: 'rgba(255, 71, 87, 0.08)',
        border: `1px solid rgba(255, 71, 87, 0.2)`,
        borderRadius: '8px',
        marginBottom: '8px',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div
          style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: theme.colors.alertRed,
            boxShadow: `0 0 8px ${theme.colors.alertRed}`,
            animation: 'pulse 1.5s infinite',
          }}
        />
        <div>
          <div
            style={{
              fontSize: '13px',
              fontWeight: 600,
              color: theme.colors.text,
            }}
          >
            {alert.service}
          </div>
          <div style={{ fontSize: '11px', color: theme.colors.textMuted }}>
            {formatTime(alert.timestamp)}
          </div>
        </div>
      </div>
      <div style={{ textAlign: 'right' }}>
        <div
          style={{
            fontSize: '18px',
            fontWeight: 700,
            color: scoreColor,
          }}
        >
          {Math.round(alert.score * 100)}
        </div>
        <div
          style={{
            fontSize: '10px',
            color: theme.colors.alertRed,
            textTransform: 'uppercase',
            fontWeight: 600,
          }}
        >
          {alert.status}
        </div>
      </div>
    </div>
  )
}

export default function AlertPanel({ alerts }) {
  const hasAlerts = alerts && alerts.length > 0

  return (
    <div>
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
      `}</style>

      {!hasAlerts ? (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            padding: '12px 14px',
            background: 'rgba(46, 213, 115, 0.08)',
            border: `1px solid rgba(46, 213, 115, 0.2)`,
            borderRadius: '8px',
            color: theme.colors.success,
            fontSize: '13px',
          }}
        >
          <span>✓</span>
          <span>No active alerts — system healthy</span>
        </div>
      ) : (
        <div>
          <div
            style={{
              fontSize: '12px',
              color: theme.colors.alertRed,
              fontWeight: 600,
              marginBottom: '8px',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
            }}
          >
            {alerts.length} Active Alert{alerts.length !== 1 ? 's' : ''}
          </div>
          {alerts.map((alert, i) => (
            <AlertItem key={i} alert={alert} />
          ))}
        </div>
      )}
    </div>
  )
}
