import { useState } from 'react'
import { theme } from '../styles/theme'

export default function RemediationPanel({ rootCause, triggerRemediation }) {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const service = rootCause?.service || rootCause?.root_cause
  const failureType = rootCause?.failure_type || 'generic_anomaly'
  const hasTarget = service && failureType !== 'none'

  const handleRemediate = async () => {
    if (!hasTarget || loading) return
    setLoading(true)
    setResult(null)
    setError(null)

    try {
      const res = await triggerRemediation(service, failureType)
      setResult(res)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const buttonStyle = {
    padding: '10px 20px',
    borderRadius: '8px',
    border: 'none',
    fontSize: '13px',
    fontWeight: 600,
    cursor: hasTarget && !loading ? 'pointer' : 'not-allowed',
    transition: 'all 0.2s ease',
    letterSpacing: '0.3px',
  }

  return (
    <div>
      {/* Target info */}
      <div style={{ marginBottom: '14px' }}>
        {hasTarget ? (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              padding: '10px 14px',
              background: 'rgba(255, 71, 87, 0.08)',
              border: `1px solid rgba(255,71,87,0.2)`,
              borderRadius: '8px',
              fontSize: '13px',
            }}
          >
            <span>🎯</span>
            <div>
              <div style={{ color: theme.colors.text, fontWeight: 600 }}>
                {service}
              </div>
              <div style={{ color: theme.colors.textMuted, fontSize: '11px' }}>
                {failureType.replace(/_/g, ' ')}
              </div>
            </div>
          </div>
        ) : (
          <div
            style={{
              padding: '10px 14px',
              background: 'rgba(46, 213, 115, 0.08)',
              border: `1px solid rgba(46,213,115,0.2)`,
              borderRadius: '8px',
              fontSize: '13px',
              color: theme.colors.success,
            }}
          >
            No remediation target — system healthy
          </div>
        )}
      </div>

      {/* Remediate button */}
      <button
        onClick={handleRemediate}
        disabled={!hasTarget || loading}
        style={{
          ...buttonStyle,
          background: hasTarget && !loading
            ? 'linear-gradient(135deg, #ff4757, #c0392b)'
            : theme.colors.cardBorder,
          color: hasTarget && !loading ? '#fff' : theme.colors.textMuted,
          width: '100%',
          marginBottom: '12px',
        }}
      >
        {loading ? '⟳ Remediating...' : '⚡ Trigger Remediation'}
      </button>

      {/* Result */}
      {result && (
        <div
          style={{
            padding: '12px 14px',
            background: result.result?.success
              ? 'rgba(46, 213, 115, 0.08)'
              : 'rgba(255, 71, 87, 0.08)',
            border: `1px solid ${result.result?.success ? 'rgba(46,213,115,0.3)' : 'rgba(255,71,87,0.3)'}`,
            borderRadius: '8px',
            fontSize: '12px',
          }}
        >
          <div
            style={{
              fontWeight: 600,
              color: result.result?.success ? theme.colors.success : theme.colors.alertRed,
              marginBottom: '6px',
            }}
          >
            {result.result?.success ? '✓ Remediation Successful' : '✗ Remediation Failed'}
          </div>
          <div style={{ color: theme.colors.textMuted, marginBottom: '4px' }}>
            Elapsed: {result.result?.elapsed_s?.toFixed(2)}s
            {result.result?.within_target ? ` (within ${result.result?.target_s}s target)` : ` (exceeded ${result.result?.target_s}s target)`}
          </div>
          {result.result?.actions_taken?.map((a, i) => (
            <div key={i} style={{ color: theme.colors.text, fontSize: '11px' }}>
              • {a}
            </div>
          ))}
          {result.result?.demo_mode && (
            <div style={{ color: theme.colors.textMuted, fontSize: '10px', marginTop: '4px' }}>
              (Demo mode — no actual Docker action)
            </div>
          )}
        </div>
      )}

      {/* Error */}
      {error && (
        <div
          style={{
            padding: '10px 14px',
            background: 'rgba(255, 71, 87, 0.08)',
            border: `1px solid rgba(255,71,87,0.3)`,
            borderRadius: '8px',
            fontSize: '12px',
            color: theme.colors.alertRed,
          }}
        >
          Error: {error}
        </div>
      )}
    </div>
  )
}
