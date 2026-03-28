import { theme, getScoreColor } from '../styles/theme'

const FAILURE_ICONS = {
  memory_leak: '💾',
  cpu_starvation: '⚡',
  network_latency: '🌐',
  generic_anomaly: '⚠️',
  none: '✓',
}

const FAILURE_LABELS = {
  memory_leak: 'Memory Leak',
  cpu_starvation: 'CPU Starvation',
  network_latency: 'Network Latency',
  generic_anomaly: 'Generic Anomaly',
  none: 'Normal',
}

export default function RootCausePanel({ rootCause, recommendation }) {
  const service = rootCause?.service || rootCause?.root_cause
  const confidence = rootCause?.confidence ?? 0
  const failureType = rootCause?.failure_type || 'none'
  const affected = rootCause?.affected_services || []
  const path = rootCause?.propagation_path || []
  const hasAnomaly = service && confidence > 0.1

  return (
    <div>
      {/* Status */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          marginBottom: '16px',
          padding: '12px 16px',
          background: hasAnomaly
            ? 'rgba(255, 71, 87, 0.08)'
            : 'rgba(46, 213, 115, 0.08)',
          border: `1px solid ${hasAnomaly ? 'rgba(255,71,87,0.3)' : 'rgba(46,213,115,0.3)'}`,
          borderRadius: '10px',
        }}
      >
        <span style={{ fontSize: '24px' }}>
          {FAILURE_ICONS[failureType] || '⚠️'}
        </span>
        <div>
          <div
            style={{
              fontSize: '14px',
              fontWeight: 600,
              color: hasAnomaly ? theme.colors.alertRed : theme.colors.success,
            }}
          >
            {hasAnomaly ? `Root Cause: ${service}` : 'System Normal'}
          </div>
          <div style={{ fontSize: '12px', color: theme.colors.textMuted }}>
            {hasAnomaly
              ? `${FAILURE_LABELS[failureType]} — ${Math.round(confidence * 100)}% confidence`
              : 'No anomalies detected'}
          </div>
        </div>
      </div>

      {/* Propagation path */}
      {path.length > 0 && (
        <div style={{ marginBottom: '12px' }}>
          <div
            style={{
              fontSize: '11px',
              color: theme.colors.textMuted,
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              marginBottom: '8px',
            }}
          >
            Propagation Path
          </div>
          <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '4px' }}>
            {path.map((svc, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span
                  style={{
                    background: i === 0 ? theme.colors.alertRed : theme.colors.cardBorder,
                    color: theme.colors.text,
                    fontSize: '11px',
                    padding: '3px 8px',
                    borderRadius: '4px',
                    fontWeight: i === 0 ? 700 : 400,
                  }}
                >
                  {svc}
                </span>
                {i < path.length - 1 && (
                  <span style={{ color: theme.colors.textMuted, fontSize: '12px' }}>→</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Affected services count */}
      {affected.length > 0 && (
        <div style={{ marginBottom: '12px' }}>
          <span
            style={{
              fontSize: '12px',
              color: theme.colors.textMuted,
            }}
          >
            Affected services:{' '}
            <span style={{ color: theme.colors.warning, fontWeight: 600 }}>
              {affected.length}
            </span>
          </span>
        </div>
      )}

      {/* Recommendation */}
      {recommendation && (
        <div
          style={{
            padding: '10px 14px',
            background: theme.colors.cardBorder,
            borderRadius: '8px',
            fontSize: '12px',
            color: theme.colors.textMuted,
            lineHeight: 1.5,
            borderLeft: `3px solid ${theme.colors.accent}`,
          }}
        >
          {recommendation}
        </div>
      )}
    </div>
  )
}
