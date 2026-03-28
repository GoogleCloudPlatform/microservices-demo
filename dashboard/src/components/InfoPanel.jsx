import { useTheme } from '../ThemeContext'

function MetricCard({ title, subtitle, value, status, statusLabel, theme }) {
  const statusColors = { OK: '#2a8a2a', DEGRADING: '#c45c0a', CRITICAL: '#cc2222', STABLE: theme.textMuted }
  return (
    <div style={{ border: `2px solid ${theme.border}`, padding: '10px 14px', marginBottom: 10, background: theme.card, fontFamily: theme.font }}>
      <div style={{ fontSize: 10, fontWeight: 'bold', color: theme.text, letterSpacing: 0.5 }}>{title}</div>
      {subtitle && <div style={{ fontSize: 9, color: theme.textMuted, marginTop: 1 }}>{subtitle}</div>}
      <div style={{ fontSize: 32, fontWeight: 'bold', color: status === 'CRITICAL' ? '#cc2222' : status === 'DEGRADING' ? '#c45c0a' : theme.text, margin: '6px 0 2px' }}>
        {value}
      </div>
      {statusLabel && (
        <div style={{ fontSize: 10, fontWeight: 'bold', color: statusColors[status] || theme.textMuted, letterSpacing: 1 }}>
          [{statusLabel}]
        </div>
      )}
    </div>
  )
}

export default function InfoPanel({ topology, children }) {
  const { theme } = useTheme()
  const health = topology?.health_score ?? '—'
  const momentum = topology?.failure_momentum ?? 0
  const rootCause = topology?.root_cause || {}
  const recommendation = topology?.recommendation || 'Monitoring...'
  const activeIncidents = topology?.active_incidents || []
  const recentIncidents = topology?.recent_incidents || []

  const healthStatus = health === '—' ? 'STABLE' : health < 60 ? 'CRITICAL' : health < 80 ? 'DEGRADING' : 'STABLE'
  const momentumStatus = Math.abs(momentum) < 2 ? 'STABLE' : momentum > 0 ? 'CRITICAL' : 'OK'

  return (
    <div style={{ width: '100%', height: '100%', overflowY: 'auto', padding: '14px', boxSizing: 'border-box', fontFamily: theme.font, background: theme.bg }}>
      <div style={{ fontSize: 11, fontWeight: 'bold', color: theme.textMuted, letterSpacing: 2, marginBottom: 14 }}>
        AEGIS CONTROL
      </div>

      <MetricCard title="System Health" subtitle="Overall service health score across the platform"
        value={health} status={healthStatus} statusLabel={healthStatus} theme={theme} />

      <MetricCard title="Failure Momentum" subtitle="How quickly overall platform risk is rising or falling"
        value={`${momentum > 0 ? '+' : ''}${momentum} points/min`}
        status={momentumStatus}
        statusLabel={momentumStatus === 'STABLE' ? 'STABLE' : momentumStatus === 'CRITICAL' ? 'RISING' : 'FALLING'}
        theme={theme} />

      <div style={{ border: `2px solid ${theme.border}`, padding: '10px 14px', marginBottom: 10, background: theme.card }}>
        <div style={{ fontSize: 10, fontWeight: 'bold', letterSpacing: 0.5, color: theme.text }}>Root Cause</div>
        <div style={{ fontSize: 9, color: theme.textMuted }}>Most likely source of the current issue cascade</div>
        {rootCause?.service ? (
          <>
            <div style={{ fontSize: 20, fontWeight: 'bold', color: '#c45c0a', margin: '6px 0 2px' }}>{rootCause.service}</div>
            <div style={{ fontSize: 10, color: theme.textMuted }}>Confidence: {Math.round((rootCause.confidence || 0) * 100)}%</div>
            <div style={{ fontSize: 9, color: '#c45c0a', marginTop: 2 }}>
              Detected issue: {rootCause.failure_type?.replace(/_/g, ' ')}
            </div>
          </>
        ) : (
          <div style={{ fontSize: 14, color: '#2a8a2a', margin: '6px 0 2px', fontWeight: 'bold' }}>System nominal</div>
        )}
      </div>

      <div style={{ border: `2px solid ${theme.border}`, padding: '10px 14px', marginBottom: 10, background: theme.card }}>
        <div style={{ fontSize: 10, fontWeight: 'bold', letterSpacing: 0.5, color: theme.text }}>Recommendation</div>
        <div style={{ fontSize: 9, color: theme.textMuted, marginTop: 6, lineHeight: 1.5 }}>{recommendation}</div>
      </div>

      <div style={{ border: `2px solid ${theme.border}`, padding: '10px 14px', marginBottom: 10, background: theme.card }}>
        <div style={{ fontSize: 10, fontWeight: 'bold', letterSpacing: 0.5, color: theme.text }}>Incident Summary</div>
        <div style={{ fontSize: 9, color: theme.textMuted, marginTop: 4 }}>
          Active incidents: {activeIncidents.length} · Recent incidents: {recentIncidents.length}
        </div>
        {activeIncidents.length > 0 ? (
          activeIncidents.slice(0, 2).map(inc => (
            <div key={inc.id} style={{ marginTop: 8, borderLeft: '2px solid #cc2222', paddingLeft: 8 }}>
              <div style={{ fontSize: 10, fontWeight: 'bold', color: '#cc2222' }}>{inc.root_cause_service}</div>
              <div style={{ fontSize: 9, color: theme.textMuted }}>
                {inc.failure_type?.replace(/_/g, ' ')} · phase: {inc.current_phase?.replace(/_/g, ' ')}
              </div>
            </div>
          ))
        ) : (
          <div style={{ fontSize: 10, color: '#2a8a2a', marginTop: 8 }}>No active incidents.</div>
        )}
      </div>

      {children && <div style={{ borderTop: `1px solid ${theme.borderLight}`, marginBottom: 12 }} />}
      {children}
    </div>
  )
}
