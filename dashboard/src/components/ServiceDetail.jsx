import { useState } from 'react'
import { useTheme } from '../ThemeContext'

function detailStyles(theme) {
  return {
    shell: {
      fontFamily: theme.font,
      color: theme.text,
    },
    headerTitle: {
      fontFamily: theme.displayFont,
      fontSize: 20,
      lineHeight: 1,
      letterSpacing: '-0.03em',
      color: theme.text,
    },
    headerMeta: {
      fontSize: 10,
      color: theme.textMuted,
      fontWeight: 700,
      textTransform: 'uppercase',
      letterSpacing: 1,
      marginTop: 4,
      lineHeight: 1.4,
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
    title: {
      fontSize: 10,
      fontWeight: 700,
      color: theme.text,
      letterSpacing: 1.2,
      textTransform: 'uppercase',
      lineHeight: 1.3,
    },
    subtitle: {
      fontSize: 9,
      color: theme.textMuted,
      lineHeight: 1.5,
    },
    meta: {
      fontSize: 9,
      color: theme.textMuted,
      lineHeight: 1.55,
      overflowWrap: 'anywhere',
    },
    key: {
      fontSize: 10,
      color: theme.textMuted,
      lineHeight: 1.4,
    },
    value: {
      fontSize: 10,
      color: theme.text,
      fontWeight: 700,
      lineHeight: 1.4,
    },
  }
}

function MetricBar({ label, value, theme, styles }) {
  const pct = Math.min(value, 100)
  return (
    <div style={{ marginBottom: 8 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, marginBottom: 4 }}>
        <span style={styles.key}>{label}</span>
        <span style={styles.value}>{value.toFixed(1)}%</span>
      </div>
      <div style={{ height: 4, background: theme.borderLight, borderRadius: 2 }}>
        <div style={{ height: '100%', width: `${pct}%`, background: pct > 70 ? '#cc2222' : pct > 40 ? '#c45c0a' : '#2a8a2a', borderRadius: 2, transition: 'width 0.5s ease' }} />
      </div>
    </div>
  )
}

function MiniSparkline({ data, color = '#c45c0a', theme }) {
  if (!data || data.length < 2) return <span style={{ color: theme.textDim, fontSize: 10 }}>—</span>
  const max = Math.max(...data, 0.001)
  const width = 80
  const height = 24
  const pts = data.map((v, i) => `${(i / (data.length - 1)) * width},${height - (v / max) * height}`).join(' ')
  return (
    <svg width={width} height={height} style={{ verticalAlign: 'middle' }}>
      <polyline points={pts} fill="none" stroke={color} strokeWidth="1.5" />
    </svg>
  )
}

function DetailCard({ title, subtitle, children, styles }) {
  return (
    <div style={styles.card}>
      <div style={styles.title}>{title}</div>
      {subtitle && <div style={styles.subtitle}>{subtitle}</div>}
      {children}
    </div>
  )
}

export default function ServiceDetail({ service, data, windowData, onRemediate, onClose }) {
  const { theme } = useTheme()
  const styles = detailStyles(theme)
  const [remediating, setRemediating] = useState(false)
  const [remResult, setRemResult] = useState(null)

  const handleRemediate = async () => {
    setRemediating(true)
    try {
      const result = await onRemediate(service, data?.latest_incident?.failure_type || data?.failure_type || 'generic_anomaly')
      setRemResult(result)
    } catch (e) {
      setRemResult({ result: { status: 'manual_required', operator_summary: e.message } })
    }
    setRemediating(false)
  }

  const obs = windowData?.observations || []
  const cpuHistory = obs.map(o => o.cpu_percent)
  const memHistory = obs.map(o => o.mem_percent)
  const errHistory = obs.map(o => o.error_rate * 100)

  const status = data?.status || 'normal'
  const score = data?.combined_score || 0
  const flags = data?.feature_flags || []
  const logs = data?.recent_logs || []
  const latestIncident = data?.latest_incident || null
  const similarIncidents = data?.similar_incidents || []
  const predictiveAlert = data?.predictive_alert || null
  const statusColor = status === 'critical' ? '#cc2222' : status === 'warning' ? '#c45c0a' : '#2a8a2a'

  return (
    <div style={styles.shell}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12, marginBottom: 12 }}>
        <div style={{ minWidth: 0 }}>
          <div style={styles.headerTitle}>{service}</div>
          <div style={{ ...styles.headerMeta, color: statusColor }}>
            {status} · anomaly score {Math.round(score * 100)}/100
          </div>
        </div>
        <button onClick={onClose} style={{ background: 'none', border: `1px solid ${theme.borderLight}`, cursor: 'pointer', padding: '2px 8px', fontSize: 11, fontFamily: theme.font, color: theme.text }}>
          ✕
        </button>
      </div>

      <DetailCard
        title="Resource Usage"
        subtitle="Current resource saturation and network movement."
        styles={styles}
      >
        <MetricBar label="CPU usage" value={data?.cpu_mean || 0} theme={theme} styles={styles} />
        <MetricBar label="Memory usage" value={data?.mem_mean || 0} theme={theme} styles={styles} />
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, marginTop: 4 }}>
          <span style={styles.key}>Network in <span style={styles.value}>{(data?.net_rx_mean || 0).toFixed(3)} MB/s</span></span>
          <span style={styles.key}>Network out <span style={styles.value}>{(data?.net_tx_mean || 0).toFixed(3)} MB/s</span></span>
        </div>
      </DetailCard>

      {obs.length > 0 && (
        <DetailCard
          title="Recent Trends"
          subtitle={`${obs.length} recent samples from the live service window.`}
          styles={styles}
        >
          {[['CPU usage', cpuHistory, '#c45c0a'], ['Memory usage', memHistory, '#5588cc'], ['Error rate', errHistory, '#cc2222']].map(([label, hist, col]) => (
            <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
              <span style={{ ...styles.key, width: 68 }}>{label}</span>
              <MiniSparkline data={hist} color={col} theme={theme} />
              <span style={{ fontSize: 9, color: theme.textDim }}>{hist.length > 0 ? hist[hist.length - 1].toFixed(1) : '—'}</span>
            </div>
          ))}
        </DetailCard>
      )}

      <DetailCard
        title="Log and Error Signals"
        subtitle="Error volume, warnings, and logging behavior in the current window."
        styles={styles}
      >
        {[
          ['Error rate', `${((data?.error_rate_mean || 0) * 100).toFixed(2)}%`],
          ['Warning rate', `${((data?.warn_rate_mean || 0) * 100).toFixed(2)}%`],
          ['Log volume', `${(data?.log_volume_per_sec || 0).toFixed(1)}/s`],
          ['Exceptions detected', (data?.exception_count_mean || 0).toFixed(1)],
          ['Log pattern entropy', (data?.template_entropy_mean || 0).toFixed(2)],
        ].map(([k, v]) => (
          <div key={k} style={{ display: 'flex', justifyContent: 'space-between', gap: 12 }}>
            <span style={styles.key}>{k}</span>
            <span style={styles.value}>{v}</span>
          </div>
        ))}
      </DetailCard>

      {flags.length > 0 && (
        <DetailCard
          title="Detected Conditions"
          subtitle="Current feature flags raised by the scoring pipeline."
          styles={styles}
        >
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
            {flags.map(flag => (
              <span key={flag} style={{ fontSize: 9, padding: '2px 6px', border: `1px solid ${theme.accent}`, color: theme.accent, fontFamily: theme.font }}>
                {flag.replace(/_/g, ' ')}
              </span>
            ))}
          </div>
        </DetailCard>
      )}

      {predictiveAlert && predictiveAlert.status !== 'resolved' && (
        <DetailCard
          title="Pre-Failure Alert"
          subtitle="Latest predictive warning for this service."
          styles={styles}
        >
          <div style={{ fontSize: 11, color: predictiveAlert.severity === 'critical' ? '#cc2222' : '#c45c0a', fontWeight: 700 }}>
            LSTM risk {Math.round((predictiveAlert.lstm_score || 0) * 100)}% · {predictiveAlert.failure_type?.replace(/_/g, ' ')}
          </div>
          <div style={styles.meta}>{predictiveAlert.message}</div>
          {(predictiveAlert.preventive_actions || []).slice(0, 2).map(item => (
            <div key={item.action} style={styles.meta}>
              <span style={{ color: theme.text, fontWeight: 700 }}>{item.action.replace(/_/g, ' ')}</span> · {item.summary}
            </div>
          ))}
        </DetailCard>
      )}

      {latestIncident && (
        <DetailCard
          title="Incident History and Memory"
          subtitle="Latest incident plus related memory matches."
          styles={styles}
        >
          <div style={{ fontSize: 10, fontWeight: 700, color: theme.text }}>Latest incident</div>
          <div style={styles.meta}>
            {latestIncident.failure_type?.replace(/_/g, ' ')} · {latestIncident.status}
          </div>
          {latestIncident.decision && <div style={styles.meta}>Chosen action: {latestIncident.decision.action}</div>}
          {similarIncidents.slice(0, 2).map(match => (
            <div key={match.incident_id} style={{ borderTop: `1px solid ${theme.borderLight}`, paddingTop: 6, marginTop: 6 }}>
              <div style={{ fontSize: 10, color: theme.text, fontWeight: 700 }}>{match.failure_type?.replace(/_/g, ' ')}</div>
              <div style={styles.meta}>Past action: {match.selected_action} · outcome: {match.outcome}</div>
            </div>
          ))}
        </DetailCard>
      )}

      {logs.length > 0 && (
        <DetailCard
          title="Recent Logs"
          subtitle="Latest log excerpts cached for this service."
          styles={styles}
        >
          {logs.map((log, index) => (
            <div
              key={index}
              style={{
                fontSize: 9,
                color: log.includes('ERROR') ? '#cc2222' : log.includes('WARN') ? '#c45c0a' : theme.textMuted,
                fontFamily: theme.font,
                marginBottom: 4,
                wordBreak: 'break-all',
                borderLeft: `2px solid ${log.includes('ERROR') ? '#cc2222' : log.includes('WARN') ? '#c45c0a' : theme.borderLight}`,
                paddingLeft: 6,
                lineHeight: 1.5,
              }}
            >
              {log.slice(0, 80)}{log.length > 80 ? '…' : ''}
            </div>
          ))}
        </DetailCard>
      )}

      <button
        onClick={handleRemediate}
        disabled={remediating}
        style={{
          width: '100%',
          padding: '8px',
          fontFamily: theme.font,
          fontSize: 11,
          fontWeight: 700,
          border: `2px solid ${theme.border}`,
          background: remediating ? theme.borderLight : theme.border,
          color: theme.bg,
          cursor: remediating ? 'not-allowed' : 'pointer',
          letterSpacing: 1,
          transition: 'all 0.2s',
        }}
      >
        {remediating ? '⏳ RUNNING REMEDIATION...' : '⚙ RUN REMEDIATION'}
      </button>

      {remResult && (
        <div
          style={{
            marginTop: 8,
            padding: 8,
            fontSize: 10,
            fontFamily: theme.font,
            border: `1px solid ${(remResult?.result?.status || remResult?.status) === 'resolved' ? '#2a8a2a' : '#cc2222'}`,
            color: (remResult?.result?.status || remResult?.status) === 'resolved' ? '#2a8a2a' : '#cc2222',
            background: theme.card,
            lineHeight: 1.5,
          }}
        >
          {(remResult?.result?.status || remResult?.status) === 'resolved' ? '✓ Remediation resolved the issue' : '✗ Remediation did not fully resolve the issue'}
          {remResult?.result?.operator_summary && <div style={{ marginTop: 4, color: theme.textMuted }}>{remResult.result.operator_summary}</div>}
        </div>
      )}
    </div>
  )
}
