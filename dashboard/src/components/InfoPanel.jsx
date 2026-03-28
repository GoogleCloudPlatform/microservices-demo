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

function TimelineItem({ event, theme }) {
  const tones = { critical: '#cc2222', warning: '#c45c0a', info: theme.textMuted }
  const tone = tones[event?.severity] || theme.textMuted
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '12px minmax(0, 1fr)', gap: 8, marginTop: 10 }}>
      <div style={{ display: 'flex', justifyContent: 'center' }}>
        <span style={{ width: 8, height: 8, borderRadius: '50%', background: tone, marginTop: 4 }} />
      </div>
      <div>
        <div style={{ fontSize: 10, color: theme.text, fontWeight: 'bold' }}>{event?.title || 'Event'}</div>
        <div style={{ fontSize: 9, color: theme.textMuted, marginTop: 2, lineHeight: 1.5 }}>{event?.message}</div>
        <div style={{ fontSize: 8, color: theme.textDim, marginTop: 4, textTransform: 'uppercase', letterSpacing: 1 }}>
          {event?.service ? `${event.service} · ` : ''}{event?.created_at ? new Date(event.created_at).toLocaleTimeString('en-US', { hour12: false }) : ''}
        </div>
      </div>
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
  const predictiveAlerts = topology?.predictive_alerts || []
  const topPredictiveAlert = [...predictiveAlerts].sort((a, b) => (b.lstm_score || 0) - (a.lstm_score || 0))[0]
  const timeline = topology?.timeline || []

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
        <div style={{ fontSize: 10, fontWeight: 'bold', letterSpacing: 0.5, color: theme.text }}>Pre-Failure Predictor</div>
        <div style={{ fontSize: 9, color: theme.textMuted }}>LSTM-based early warning and preventive action planner</div>
        {topPredictiveAlert ? (
          <>
            <div style={{ fontSize: 20, fontWeight: 'bold', color: topPredictiveAlert.severity === 'critical' ? '#cc2222' : '#c45c0a', margin: '8px 0 2px' }}>
              {topPredictiveAlert.service}
            </div>
            <div style={{ fontSize: 9, color: theme.textMuted, lineHeight: 1.5 }}>
              {topPredictiveAlert.message}
            </div>
            <div style={{ fontSize: 9, color: theme.textMuted, marginTop: 8 }}>
              Predicted window: {topPredictiveAlert.predicted_window} · LSTM risk {Math.round((topPredictiveAlert.lstm_score || 0) * 100)}%
            </div>
            <div style={{ marginTop: 8 }}>
              {(topPredictiveAlert.preventive_actions || []).slice(0, 2).map(item => (
                <div key={item.action} style={{ borderLeft: `2px solid ${item.automatic ? '#cc2222' : theme.accent}`, paddingLeft: 8, marginTop: 6 }}>
                  <div style={{ fontSize: 9, color: theme.text, fontWeight: 'bold' }}>
                    {item.action.replace(/_/g, ' ')}{item.automatic ? ' · automatic' : ''}
                  </div>
                  <div style={{ fontSize: 8, color: theme.textMuted, lineHeight: 1.5 }}>{item.summary}</div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div style={{ fontSize: 10, color: '#2a8a2a', marginTop: 8 }}>No pre-failure alert is active.</div>
        )}
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

      <div style={{ border: `2px solid ${theme.border}`, padding: '10px 14px', marginBottom: 10, background: theme.card }}>
        <div style={{ fontSize: 10, fontWeight: 'bold', letterSpacing: 0.5, color: theme.text }}>Live Timeline</div>
        <div style={{ fontSize: 9, color: theme.textMuted }}>Backend events, preventive actions, and remediation milestones</div>
        {timeline.length > 0 ? (
          timeline.slice(0, 6).map(event => <TimelineItem key={`${event.id}-${event.created_at}`} event={event} theme={theme} />)
        ) : (
          <div style={{ fontSize: 10, color: theme.textMuted, marginTop: 8 }}>Timeline will populate as the system observes events.</div>
        )}
      </div>

      {children && <div style={{ borderTop: `1px solid ${theme.borderLight}`, marginBottom: 12 }} />}
      {children}
    </div>
  )
}
