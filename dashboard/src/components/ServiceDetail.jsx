import { useState } from 'react'
import { useTheme } from '../ThemeContext'

function MetricBar({ label, value, color = '#c45c0a', theme }) {
  const pct = Math.min(value, 100)
  return (
    <div style={{ marginBottom: 8 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
        <span style={{ fontSize: 10, color: theme.textMuted }}>{label}</span>
        <span style={{ fontSize: 10, color: theme.text, fontWeight: 'bold' }}>{value.toFixed(1)}%</span>
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
  const W = 80, H = 24
  const pts = data.map((v, i) => `${(i / (data.length - 1)) * W},${H - (v / max) * H}`).join(' ')
  return (
    <svg width={W} height={H} style={{ verticalAlign: 'middle' }}>
      <polyline points={pts} fill="none" stroke={color} strokeWidth="1.5" />
    </svg>
  )
}

export default function ServiceDetail({ service, data, windowData, onRemediate, onClose }) {
  const { theme } = useTheme()
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
  const box = { border: `1px solid ${theme.borderLight}`, padding: '10px 12px', marginBottom: 10, background: theme.card }

  return (
    <div style={{ fontFamily: theme.font, color: theme.text }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
        <div>
          <div style={{ fontSize: 13, fontWeight: 'bold', color: theme.text }}>{service}</div>
          <div style={{ fontSize: 10, color: status === 'critical' ? '#cc2222' : status === 'warning' ? '#c45c0a' : '#2a8a2a', fontWeight: 'bold', textTransform: 'uppercase', marginTop: 2 }}>
            {status} · anomaly score {Math.round(score * 100)}/100
          </div>
        </div>
        <button onClick={onClose} style={{ background: 'none', border: `1px solid ${theme.borderLight}`, cursor: 'pointer', padding: '2px 8px', fontSize: 11, fontFamily: theme.font, color: theme.text }}>✕</button>
      </div>

      <div style={box}>
        <div style={{ fontSize: 10, fontWeight: 'bold', color: theme.textMuted, marginBottom: 8, letterSpacing: 1 }}>RESOURCE USAGE</div>
        <MetricBar label="CPU usage" value={data?.cpu_mean || 0} color="#c45c0a" theme={theme} />
        <MetricBar label="Memory" value={data?.mem_mean || 0} color="#5588cc" theme={theme} />
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 6, fontSize: 10 }}>
          <span style={{ color: theme.textMuted }}>Network in <span style={{ color: theme.text }}>{(data?.net_rx_mean || 0).toFixed(3)} MB/s</span></span>
          <span style={{ color: theme.textMuted }}>Network out <span style={{ color: theme.text }}>{(data?.net_tx_mean || 0).toFixed(3)} MB/s</span></span>
        </div>
      </div>

      {obs.length > 0 && (
        <div style={box}>
          <div style={{ fontSize: 10, fontWeight: 'bold', color: theme.textMuted, marginBottom: 8, letterSpacing: 1 }}>RECENT TRENDS ({obs.length} samples)</div>
          {[['CPU usage', cpuHistory, '#c45c0a'], ['Memory usage', memHistory, '#5588cc'], ['Error rate', errHistory, '#cc2222']].map(([label, hist, col]) => (
            <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
              <span style={{ fontSize: 9, color: theme.textMuted, width: 62 }}>{label}</span>
              <MiniSparkline data={hist} color={col} theme={theme} />
              <span style={{ fontSize: 9, color: theme.textDim }}>{hist.length > 0 ? hist[hist.length - 1].toFixed(1) : '—'}</span>
            </div>
          ))}
        </div>
      )}

      <div style={box}>
        <div style={{ fontSize: 10, fontWeight: 'bold', color: theme.textMuted, marginBottom: 8, letterSpacing: 1 }}>LOG AND ERROR SIGNALS</div>
        {[
          ['Error rate', `${((data?.error_rate_mean || 0) * 100).toFixed(2)}%`],
          ['Warning rate', `${((data?.warn_rate_mean || 0) * 100).toFixed(2)}%`],
          ['Log volume', `${(data?.log_volume_per_sec || 0).toFixed(1)}/s`],
          ['Exceptions detected', (data?.exception_count_mean || 0).toFixed(1)],
          ['Log pattern entropy', (data?.template_entropy_mean || 0).toFixed(2)],
        ].map(([k, v]) => (
          <div key={k} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
            <span style={{ fontSize: 10, color: theme.textMuted }}>{k}</span>
            <span style={{ fontSize: 10, color: theme.text, fontWeight: 'bold' }}>{v}</span>
          </div>
        ))}
      </div>

      {flags.length > 0 && (
        <div style={box}>
          <div style={{ fontSize: 10, fontWeight: 'bold', color: theme.textMuted, marginBottom: 6, letterSpacing: 1 }}>DETECTED CONDITIONS</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
            {flags.map(f => (
              <span key={f} style={{ fontSize: 9, padding: '2px 6px', border: `1px solid ${theme.accent}`, color: theme.accent, fontFamily: theme.font }}>
                {f.replace(/_/g, ' ')}
              </span>
            ))}
          </div>
        </div>
      )}

      {latestIncident && (
        <div style={box}>
          <div style={{ fontSize: 10, fontWeight: 'bold', color: theme.textMuted, marginBottom: 6, letterSpacing: 1 }}>INCIDENT HISTORY AND MEMORY</div>
          <div style={{ fontSize: 10, fontWeight: 'bold', color: theme.text }}>Latest incident</div>
          <div style={{ fontSize: 10, color: theme.textMuted, marginTop: 2 }}>
            {latestIncident.failure_type?.replace(/_/g, ' ')} · {latestIncident.status}
          </div>
          {latestIncident.decision && <div style={{ fontSize: 10, color: theme.textMuted, marginTop: 2 }}>Chosen action: {latestIncident.decision.action}</div>}
          {similarIncidents.slice(0, 2).map(m => (
            <div key={m.incident_id} style={{ borderTop: `1px solid ${theme.borderLight}`, paddingTop: 6, marginTop: 6 }}>
              <div style={{ fontSize: 10, color: theme.text, fontWeight: 'bold' }}>{m.failure_type?.replace(/_/g, ' ')}</div>
              <div style={{ fontSize: 9, color: theme.textMuted }}>Past action: {m.selected_action} · outcome: {m.outcome}</div>
            </div>
          ))}
        </div>
      )}

      {logs.length > 0 && (
        <div style={box}>
          <div style={{ fontSize: 10, fontWeight: 'bold', color: theme.textMuted, marginBottom: 6, letterSpacing: 1 }}>RECENT LOGS</div>
          {logs.map((log, i) => (
            <div key={i} style={{ fontSize: 9, color: log.includes('ERROR') ? '#cc2222' : log.includes('WARN') ? '#c45c0a' : theme.textMuted, fontFamily: theme.font, marginBottom: 4, wordBreak: 'break-all', borderLeft: `2px solid ${log.includes('ERROR') ? '#cc2222' : log.includes('WARN') ? '#c45c0a' : theme.borderLight}`, paddingLeft: 6 }}>{log.slice(0, 80)}{log.length > 80 ? '…' : ''}</div>
          ))}
        </div>
      )}

      <button onClick={handleRemediate} disabled={remediating} style={{ width: '100%', padding: '8px', fontFamily: theme.font, fontSize: 11, fontWeight: 'bold', border: `2px solid ${theme.border}`, background: remediating ? theme.borderLight : theme.border, color: theme.bg, cursor: remediating ? 'not-allowed' : 'pointer', letterSpacing: 1, transition: 'all 0.2s' }}>
        {remediating ? '⏳ RUNNING REMEDIATION...' : '⚙ RUN REMEDIATION'}
      </button>

      {remResult && (
        <div style={{ marginTop: 8, padding: 8, fontSize: 10, fontFamily: theme.font, border: `1px solid ${(remResult?.result?.status || remResult?.status) === 'resolved' ? '#2a8a2a' : '#cc2222'}`, color: (remResult?.result?.status || remResult?.status) === 'resolved' ? '#2a8a2a' : '#cc2222', background: theme.card }}>
          {(remResult?.result?.status || remResult?.status) === 'resolved' ? '✓ Remediation resolved the issue' : '✗ Remediation did not fully resolve the issue'}
          {remResult?.result?.operator_summary && <div style={{ marginTop: 4, color: theme.textMuted }}>{remResult.result.operator_summary}</div>}
        </div>
      )}
    </div>
  )
}
