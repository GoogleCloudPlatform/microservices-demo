import { useTheme } from '../ThemeContext'

function panelStyles(theme) {
  return {
    shell: {
      width: '100%',
      height: '100%',
      overflowY: 'auto',
      padding: '14px',
      boxSizing: 'border-box',
      fontFamily: theme.font,
      background: theme.bg,
      color: theme.text,
    },
    sectionLabel: {
      fontSize: 11,
      fontWeight: 700,
      color: theme.textMuted,
      letterSpacing: 2,
      marginBottom: 14,
    },
    card: {
      border: `1px solid ${theme.borderLight}`,
      padding: '12px 14px',
      marginBottom: 10,
      background: theme.card,
      display: 'flex',
      flexDirection: 'column',
      gap: 8,
    },
    cardTitle: {
      fontSize: 10,
      fontWeight: 700,
      color: theme.text,
      letterSpacing: 1.2,
      textTransform: 'uppercase',
      lineHeight: 1.3,
    },
    cardSubtitle: {
      fontSize: 9,
      color: theme.textMuted,
      lineHeight: 1.5,
    },
    value: {
      fontFamily: theme.displayFont,
      fontSize: 30,
      lineHeight: 0.95,
      letterSpacing: '-0.03em',
      color: theme.text,
    },
    meta: {
      fontSize: 9,
      color: theme.textMuted,
      lineHeight: 1.55,
    },
    badge: {
      fontSize: 9,
      fontWeight: 700,
      letterSpacing: 1,
      textTransform: 'uppercase',
    },
    strongText: {
      fontFamily: theme.displayFont,
      fontSize: 20,
      lineHeight: 1,
      letterSpacing: '-0.03em',
      color: theme.text,
    },
  }
}

function statusTone(status, theme) {
  return status === 'CRITICAL'
    ? '#cc2222'
    : status === 'DEGRADING'
      ? '#c45c0a'
      : status === 'OK'
        ? '#2a8a2a'
        : theme.textMuted
}

function MetricCard({ title, subtitle, value, status, statusLabel, theme, styles }) {
  return (
    <div style={styles.card}>
      <div style={styles.cardTitle}>{title}</div>
      {subtitle && <div style={styles.cardSubtitle}>{subtitle}</div>}
      <div style={{ ...styles.value, color: statusTone(status, theme) }}>{value}</div>
      {statusLabel && (
        <div style={{ ...styles.badge, color: statusTone(status, theme) }}>
          {statusLabel}
        </div>
      )}
    </div>
  )
}

function PanelCard({ title, subtitle, children, styles }) {
  return (
    <div style={styles.card}>
      <div style={styles.cardTitle}>{title}</div>
      {subtitle && <div style={styles.cardSubtitle}>{subtitle}</div>}
      {children}
    </div>
  )
}

function TimelineItem({ event, theme, styles }) {
  const tones = { critical: '#cc2222', warning: '#c45c0a', info: theme.textMuted }
  const tone = tones[event?.severity] || theme.textMuted
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '12px minmax(0, 1fr)', gap: 8, marginTop: 2 }}>
      <div style={{ display: 'flex', justifyContent: 'center' }}>
        <span style={{ width: 8, height: 8, borderRadius: '50%', background: tone, marginTop: 4 }} />
      </div>
      <div style={{ minWidth: 0 }}>
        <div style={{ fontSize: 10, color: theme.text, fontWeight: 700, lineHeight: 1.4 }}>{event?.title || 'Event'}</div>
        <div style={{ ...styles.meta, marginTop: 2, overflowWrap: 'anywhere' }}>{event?.message}</div>
        <div style={{ fontSize: 8, color: theme.textDim, marginTop: 4, textTransform: 'uppercase', letterSpacing: 1, overflowWrap: 'anywhere' }}>
          {event?.service ? `${event.service} · ` : ''}{event?.created_at ? new Date(event.created_at).toLocaleTimeString('en-US', { hour12: false }) : ''}
        </div>
      </div>
    </div>
  )
}

export default function InfoPanel({ topology, children }) {
  const { theme } = useTheme()
  const styles = panelStyles(theme)
  const health = topology?.health_score ?? '—'
  const momentum = topology?.failure_momentum ?? 0
  const rootCause = topology?.root_cause || {}
  const recommendation = topology?.recommendation || 'Monitoring the live platform state.'
  const activeIncidents = topology?.active_incidents || []
  const recentIncidents = topology?.recent_incidents || []
  const predictiveAlerts = topology?.predictive_alerts || []
  const topPredictiveAlert = [...predictiveAlerts].sort((a, b) => (b.lstm_score || 0) - (a.lstm_score || 0))[0]
  const timeline = topology?.timeline || []

  const healthStatus = health === '—' ? 'STABLE' : health < 60 ? 'CRITICAL' : health < 80 ? 'DEGRADING' : 'STABLE'
  const momentumStatus = Math.abs(momentum) < 2 ? 'STABLE' : momentum > 0 ? 'CRITICAL' : 'OK'

  return (
    <div style={styles.shell}>
      <div style={styles.sectionLabel}>AEGIS CONTROL</div>

      <MetricCard
        title="System Health"
        subtitle="Overall platform health across the monitored service graph."
        value={health}
        status={healthStatus}
        statusLabel={healthStatus}
        theme={theme}
        styles={styles}
      />

      <MetricCard
        title="Failure Momentum"
        subtitle="How quickly system risk is rising or falling."
        value={`${momentum > 0 ? '+' : ''}${momentum} points/min`}
        status={momentumStatus}
        statusLabel={momentumStatus === 'STABLE' ? 'Stable' : momentumStatus === 'CRITICAL' ? 'Rising' : 'Falling'}
        theme={theme}
        styles={styles}
      />

      <PanelCard
        title="Root Cause"
        subtitle="Most likely origin of the current anomaly cascade."
        styles={styles}
      >
        {rootCause?.service ? (
          <>
            <div style={{ ...styles.strongText, color: '#c45c0a' }}>{rootCause.service}</div>
            <div style={styles.meta}>Confidence {Math.round((rootCause.confidence || 0) * 100)}%</div>
            <div style={{ ...styles.meta, color: '#c45c0a' }}>
              Detected condition: {rootCause.failure_type?.replace(/_/g, ' ')}
            </div>
          </>
        ) : (
          <div style={{ ...styles.strongText, color: '#2a8a2a' }}>System nominal</div>
        )}
      </PanelCard>

      <PanelCard
        title="Recommendation"
        subtitle="Current operator-facing guidance from the backend pipeline."
        styles={styles}
      >
        <div style={styles.meta}>{recommendation}</div>
      </PanelCard>

      <PanelCard
        title="Pre-Failure Predictor"
        subtitle="LSTM-led early warning and preventive action planning."
        styles={styles}
      >
        {topPredictiveAlert ? (
          <>
            <div style={{ ...styles.strongText, color: topPredictiveAlert.severity === 'critical' ? '#cc2222' : '#c45c0a' }}>
              {topPredictiveAlert.service}
            </div>
            <div style={styles.meta}>{topPredictiveAlert.message}</div>
            <div style={styles.meta}>
              Predicted window {topPredictiveAlert.predicted_window} · LSTM risk {Math.round((topPredictiveAlert.lstm_score || 0) * 100)}%
            </div>
            <div style={{ display: 'grid', gap: 6 }}>
              {(topPredictiveAlert.preventive_actions || []).slice(0, 2).map(item => (
                <div key={item.action} style={{ borderLeft: `2px solid ${item.automatic ? '#cc2222' : theme.accent}`, paddingLeft: 8 }}>
                  <div style={{ fontSize: 9, color: theme.text, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 0.8 }}>
                    {item.action.replace(/_/g, ' ')}{item.automatic ? ' · automatic' : ''}
                  </div>
                  <div style={styles.meta}>{item.summary}</div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div style={{ ...styles.meta, color: '#2a8a2a' }}>No pre-failure alert is active.</div>
        )}
      </PanelCard>

      <PanelCard
        title="Incident Summary"
        subtitle="Current remediation pressure and recent incident volume."
        styles={styles}
      >
        <div style={styles.meta}>
          Active incidents {activeIncidents.length} · Recent incidents {recentIncidents.length}
        </div>
        {activeIncidents.length > 0 ? (
          activeIncidents.slice(0, 2).map(inc => (
            <div key={inc.id} style={{ borderLeft: '2px solid #cc2222', paddingLeft: 8 }}>
              <div style={{ fontSize: 10, fontWeight: 700, color: '#cc2222' }}>{inc.root_cause_service}</div>
              <div style={styles.meta}>
                {inc.failure_type?.replace(/_/g, ' ')} · phase {inc.current_phase?.replace(/_/g, ' ')}
              </div>
            </div>
          ))
        ) : (
          <div style={{ ...styles.meta, color: '#2a8a2a' }}>No active incidents.</div>
        )}
      </PanelCard>

      <PanelCard
        title="Live Timeline"
        subtitle="Backend events, preventive actions, and remediation milestones."
        styles={styles}
      >
        {timeline.length > 0 ? (
          timeline.slice(0, 6).map(event => <TimelineItem key={`${event.id}-${event.created_at}`} event={event} theme={theme} styles={styles} />)
        ) : (
          <div style={styles.meta}>Timeline entries will appear as the platform records live events.</div>
        )}
      </PanelCard>

      {children && <div style={{ borderTop: `1px solid ${theme.borderLight}`, marginBottom: 12 }} />}
      {children}
    </div>
  )
}
