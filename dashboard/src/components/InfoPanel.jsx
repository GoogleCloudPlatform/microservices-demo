import { theme } from '../styles/theme'

function MetricCard({ title, subtitle, value, status, statusLabel }) {
  const statusColors = { OK: '#2a8a2a', DEGRADING: '#c45c0a', CRITICAL: '#cc2222', STABLE: '#555' }
  return (
    <div style={{
      border: `2px solid ${theme.border}`, padding: '10px 14px', marginBottom: 10,
      background: theme.card, fontFamily: theme.font,
    }}>
      <div style={{ fontSize: 10, fontWeight: 'bold', color: theme.text, letterSpacing: 0.5 }}>{title}</div>
      {subtitle && <div style={{ fontSize: 9, color: theme.textMuted, marginTop: 1 }}>{subtitle}</div>}
      <div style={{ fontSize: 32, fontWeight: 'bold', color: status === 'CRITICAL' ? '#cc2222' : status === 'DEGRADING' ? '#c45c0a' : theme.text, margin: '6px 0 2px' }}>
        {value}
      </div>
      {statusLabel && (
        <div style={{ fontSize: 10, fontWeight: 'bold', color: statusColors[status] || '#555', letterSpacing: 1 }}>
          [{statusLabel}]
        </div>
      )}
    </div>
  )
}

export default function InfoPanel({ topology, selectedService, serviceData, windowData, onRemediate, onClose, children }) {
  const health = topology?.health_score ?? '—'
  const momentum = topology?.failure_momentum ?? 0
  const rootCause = topology?.root_cause || {}
  const recommendation = topology?.recommendation || 'Monitoring...'

  const healthStatus = health === '—' ? 'STABLE' : health < 60 ? 'CRITICAL' : health < 80 ? 'DEGRADING' : 'STABLE'
  const momentumStatus = Math.abs(momentum) < 2 ? 'STABLE' : momentum > 0 ? 'CRITICAL' : 'OK'

  return (
    <div style={{
      width: '100%', height: '100%', overflowY: 'auto',
      padding: '14px', boxSizing: 'border-box',
      fontFamily: theme.font,
    }}>
      <div style={{ fontSize: 11, fontWeight: 'bold', color: theme.textMuted, letterSpacing: 2, marginBottom: 14 }}>
        MISSION CONTROL
      </div>

      <MetricCard
        title="Health Score"
        subtitle="H = w₁×avg(A) + w₂×avg(P)"
        value={health}
        status={healthStatus}
        statusLabel={healthStatus}
      />

      <MetricCard
        title="Failure Momentum"
        subtitle="M = dP/dt"
        value={`${momentum > 0 ? '+' : ''}${momentum} pts/min`}
        status={momentumStatus}
        statusLabel={momentumStatus === 'STABLE' ? 'STABLE' : momentumStatus === 'CRITICAL' ? 'RISING' : 'FALLING'}
      />

      {/* Root Cause */}
      <div style={{
        border: `2px solid ${theme.border}`, padding: '10px 14px', marginBottom: 10,
        background: theme.card,
      }}>
        <div style={{ fontSize: 10, fontWeight: 'bold', letterSpacing: 0.5 }}>Root Cause</div>
        <div style={{ fontSize: 9, color: theme.textMuted }}>Graph BFS ↑</div>
        {rootCause?.service ? (
          <>
            <div style={{ fontSize: 20, fontWeight: 'bold', color: '#c45c0a', margin: '6px 0 2px' }}>
              {rootCause.service}
            </div>
            <div style={{ fontSize: 10, color: theme.textMuted }}>
              confidence: {Math.round((rootCause.confidence || 0) * 100)}%
            </div>
            <div style={{ fontSize: 9, color: '#c45c0a', marginTop: 2 }}>
              {rootCause.failure_type?.replace('_', ' ')}
            </div>
          </>
        ) : (
          <div style={{ fontSize: 14, color: '#2a8a2a', margin: '6px 0 2px', fontWeight: 'bold' }}>
            NOMINAL
          </div>
        )}
      </div>

      {/* Action / Recommendation */}
      <div style={{
        border: `2px solid ${theme.border}`, padding: '10px 14px', marginBottom: 10,
        background: theme.card,
      }}>
        <div style={{ fontSize: 10, fontWeight: 'bold', letterSpacing: 0.5 }}>Recommendation</div>
        <div style={{ fontSize: 9, color: theme.textMuted, marginTop: 6, lineHeight: 1.5 }}>
          {recommendation}
        </div>
      </div>

      {/* Divider */}
      {children && (
        <div style={{ borderTop: `1px solid ${theme.borderLight}`, marginBottom: 12 }} />
      )}

      {/* ServiceDetail injected here */}
      {children}
    </div>
  )
}
