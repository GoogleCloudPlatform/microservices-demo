import { useState } from 'react'
import { theme, SERVICE_SHORT } from '../styles/theme'

function MetricBar({ label, value, max = 100, unit = '%', color = '#c45c0a' }) {
  const pct = Math.min((value / max) * 100, 100)
  return (
    <div style={{ marginBottom: 8 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
        <span style={{ fontSize: 10, color: theme.textMuted }}>{label}</span>
        <span style={{ fontSize: 10, color: theme.text, fontWeight: 'bold' }}>
          {typeof value === 'number' ? value.toFixed(1) : value}{unit}
        </span>
      </div>
      <div style={{ height: 4, background: '#e0d8c8', borderRadius: 2 }}>
        <div style={{
          height: '100%', width: `${pct}%`, background: pct > 70 ? '#cc2222' : pct > 40 ? '#c45c0a' : '#2a8a2a',
          borderRadius: 2, transition: 'width 0.5s ease',
        }} />
      </div>
    </div>
  )
}

function MiniSparkline({ data, color = '#c45c0a' }) {
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
  const [remediating, setRemediating] = useState(false)
  const [remResult, setRemResult] = useState(null)

  const handleRemediate = async () => {
    setRemediating(true)
    try {
      const result = await onRemediate(service, data?.failure_type || 'generic_anomaly')
      setRemResult(result?.result)
    } catch (e) {
      setRemResult({ success: false, error: e.message })
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

  const boxStyle = {
    border: `1px solid ${theme.borderLight}`,
    padding: '10px 12px',
    marginBottom: 10,
    background: theme.card,
  }

  return (
    <div style={{ fontFamily: theme.font, height: '100%', overflowY: 'auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
        <div>
          <div style={{ fontSize: 13, fontWeight: 'bold', color: theme.text }}>{service}</div>
          <div style={{
            fontSize: 10, color: status === 'critical' ? '#cc2222' : status === 'warning' ? '#c45c0a' : '#2a8a2a',
            fontWeight: 'bold', textTransform: 'uppercase', marginTop: 2,
          }}>
            {status} · anomaly {Math.round(score * 100)}
          </div>
        </div>
        <button onClick={onClose} style={{
          background: 'none', border: `1px solid ${theme.borderLight}`,
          cursor: 'pointer', padding: '2px 8px', fontSize: 11, fontFamily: theme.font, color: theme.text,
        }}>✕</button>
      </div>

      {/* CPU / MEM / Network */}
      <div style={boxStyle}>
        <div style={{ fontSize: 10, fontWeight: 'bold', color: theme.textMuted, marginBottom: 8, letterSpacing: 1 }}>
          RESOURCES
        </div>
        <MetricBar label="CPU" value={data?.cpu_mean || 0} color="#c45c0a" />
        <MetricBar label="Memory" value={data?.mem_mean || 0} color="#5588cc" />
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 6 }}>
          <div style={{ fontSize: 10 }}>
            <span style={{ color: theme.textMuted }}>net_rx </span>
            <span style={{ color: theme.text }}>{(data?.net_rx_mean || 0).toFixed(3)} MB/s</span>
          </div>
          <div style={{ fontSize: 10 }}>
            <span style={{ color: theme.textMuted }}>net_tx </span>
            <span style={{ color: theme.text }}>{(data?.net_tx_mean || 0).toFixed(3)} MB/s</span>
          </div>
        </div>
      </div>

      {/* Sparklines */}
      {obs.length > 0 && (
        <div style={boxStyle}>
          <div style={{ fontSize: 10, fontWeight: 'bold', color: theme.textMuted, marginBottom: 8, letterSpacing: 1 }}>
            TRENDS (last {obs.length} samples)
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {[['CPU%', cpuHistory, '#c45c0a'], ['MEM%', memHistory, '#5588cc'], ['ERR%', errHistory, '#cc2222']].map(([label, hist, col]) => (
              <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontSize: 9, color: theme.textMuted, width: 30 }}>{label}</span>
                <MiniSparkline data={hist} color={col} />
                <span style={{ fontSize: 9, color: theme.textDim }}>
                  {hist.length > 0 ? `${hist[hist.length - 1].toFixed(1)}` : '—'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Log features */}
      <div style={boxStyle}>
        <div style={{ fontSize: 10, fontWeight: 'bold', color: theme.textMuted, marginBottom: 8, letterSpacing: 1 }}>
          LOG SIGNALS
        </div>
        {[
          ['Error rate', `${((data?.error_rate_mean || 0) * 100).toFixed(2)}%`],
          ['Warn rate', `${((data?.warn_rate_mean || 0) * 100).toFixed(2)}%`],
          ['Log vol', `${(data?.log_volume_per_sec || 0).toFixed(1)}/s`],
          ['Exceptions', (data?.exception_count_mean || 0).toFixed(1)],
          ['Entropy', (data?.template_entropy_mean || 0).toFixed(2)],
          ['Error Δ', data?.error_rate_slope > 0 ? `+${(data.error_rate_slope * 1000).toFixed(2)}‰/s` : `${((data?.error_rate_slope || 0) * 1000).toFixed(2)}‰/s`],
        ].map(([k, v]) => (
          <div key={k} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
            <span style={{ fontSize: 10, color: theme.textMuted }}>{k}</span>
            <span style={{ fontSize: 10, color: theme.text, fontWeight: 'bold' }}>{v}</span>
          </div>
        ))}
      </div>

      {/* Feature flags */}
      {flags.length > 0 && (
        <div style={boxStyle}>
          <div style={{ fontSize: 10, fontWeight: 'bold', color: theme.textMuted, marginBottom: 6, letterSpacing: 1 }}>
            FLAGS
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
            {flags.map(f => (
              <span key={f} style={{
                fontSize: 9, padding: '2px 6px', border: `1px solid #c45c0a`,
                color: '#c45c0a', fontFamily: theme.font,
              }}>{f}</span>
            ))}
          </div>
        </div>
      )}

      {/* Recent logs */}
      {logs.length > 0 && (
        <div style={boxStyle}>
          <div style={{ fontSize: 10, fontWeight: 'bold', color: theme.textMuted, marginBottom: 6, letterSpacing: 1 }}>
            RECENT LOGS
          </div>
          {logs.map((log, i) => (
            <div key={i} style={{
              fontSize: 9, color: log.includes('ERROR') || log.includes('CRITICAL') ? '#cc2222' : log.includes('WARN') ? '#c45c0a' : theme.textMuted,
              fontFamily: theme.font, marginBottom: 4, wordBreak: 'break-all',
              borderLeft: `2px solid ${log.includes('ERROR') ? '#cc2222' : log.includes('WARN') ? '#c45c0a' : '#ccc'}`,
              paddingLeft: 6,
            }}>{log.slice(0, 80)}{log.length > 80 ? '…' : ''}</div>
          ))}
        </div>
      )}

      {/* Remediate button */}
      <button
        onClick={handleRemediate}
        disabled={remediating}
        style={{
          width: '100%', padding: '8px', fontFamily: theme.font, fontSize: 11,
          fontWeight: 'bold', border: `2px solid ${theme.border}`,
          background: remediating ? '#eee' : theme.border, color: remediating ? '#999' : '#fff',
          cursor: remediating ? 'not-allowed' : 'pointer', letterSpacing: 1,
          transition: 'all 0.2s',
        }}
      >
        {remediating ? '⏳ REMEDIATING...' : '⚙ TRIGGER REMEDIATION'}
      </button>

      {remResult && (
        <div style={{
          marginTop: 8, padding: 8, fontSize: 10, fontFamily: theme.font,
          border: `1px solid ${remResult.success ? '#2a8a2a' : '#cc2222'}`,
          color: remResult.success ? '#2a8a2a' : '#cc2222', background: '#fff',
        }}>
          {remResult.success ? `✓ Done in ${remResult.elapsed_s}s` : `✗ Failed`}
        </div>
      )}
    </div>
  )
}
