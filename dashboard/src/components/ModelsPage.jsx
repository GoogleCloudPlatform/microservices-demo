import { useMemo } from 'react'
import { useTheme } from '../ThemeContext'
import { anomalyScoreColor, SERVICE_SHORT } from '../styles/theme'

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value))
}

function formatValue(value, digits = 3) {
  if (value == null || Number.isNaN(Number(value))) return '—'
  return Number(value).toFixed(digits)
}

function formatPercent(value) {
  if (value == null || Number.isNaN(Number(value))) return '—'
  return `${Math.round(Number(value) * 100)}%`
}

function formatClock(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleTimeString('en-US', { hour12: false })
}

function labelize(value) {
  return String(value || 'unknown').replace(/_/g, ' ')
}

function sparkPath(points, width = 180, height = 42) {
  const clean = points.filter(point => typeof point?.score === 'number')
  if (!clean.length) return ''
  return clean
    .map((point, index) => {
      const x = clean.length === 1 ? width / 2 : (index / (clean.length - 1)) * width
      const y = height - clamp(point.score || 0, 0, 1) * height
      return `${index === 0 ? 'M' : 'L'} ${x.toFixed(2)} ${y.toFixed(2)}`
    })
    .join(' ')
}

function Section({ title, kicker, children, theme, actions }) {
  return (
    <section style={{ border: `1px solid ${theme.borderLight}`, borderRadius: 22, padding: 20, background: theme.card, minWidth: 0 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, alignItems: 'flex-start', marginBottom: 16 }}>
        <div style={{ minWidth: 0 }}>
          <div style={{ fontSize: 10, letterSpacing: '0.18em', textTransform: 'uppercase', color: theme.textMuted, marginBottom: 8 }}>
            {kicker}
          </div>
          <h2 style={{ fontFamily: theme.displayFont, fontWeight: 400, fontSize: 28, margin: 0, letterSpacing: '-0.03em' }}>
            {title}
          </h2>
        </div>
        {actions}
      </div>
      {children}
    </section>
  )
}

function MetricCard({ label, value, meta, color, theme }) {
  return (
    <div style={{ border: `1px solid ${theme.borderLight}`, borderRadius: 18, padding: 16, background: theme.card, minWidth: 0 }}>
      <div style={{ fontSize: 10, letterSpacing: '0.18em', textTransform: 'uppercase', color: theme.textMuted }}>{label}</div>
      <div style={{ fontFamily: theme.displayFont, fontSize: 30, lineHeight: 1, marginTop: 10, color, overflowWrap: 'anywhere' }}>{value}</div>
      <div style={{ fontSize: 11, color: theme.textMuted, marginTop: 10, lineHeight: 1.6, overflowWrap: 'anywhere' }}>{meta}</div>
    </div>
  )
}

function StatusPill({ text, tone, theme }) {
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 6,
        border: `1px solid ${theme.borderLight}`,
        borderRadius: 999,
        padding: '6px 10px',
        fontSize: 10,
        letterSpacing: '0.12em',
        textTransform: 'uppercase',
        color: tone,
        overflowWrap: 'anywhere',
      }}
    >
      <span style={{ width: 6, height: 6, borderRadius: '50%', background: tone }} />
      {text}
    </span>
  )
}

function EmptyState({ text, theme }) {
  return (
    <div style={{ fontSize: 11, color: theme.textMuted, lineHeight: 1.7, minWidth: 0 }}>
      {text}
    </div>
  )
}

function ServiceTrendCard({ service, theme }) {
  const tone = anomalyScoreColor(service.combined_score || 0, 'fill', theme)
  const prediction = service.predictive_alert
  const path = sparkPath(service.score_history || [])
  const primaryAction = prediction?.preventive_actions?.[0]

  return (
    <div style={{ border: `1px solid ${theme.borderLight}`, borderRadius: 18, padding: 16, background: theme.card, minWidth: 0 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'flex-start', marginBottom: 12 }}>
        <div style={{ minWidth: 0 }}>
          <div style={{ fontFamily: theme.displayFont, fontSize: 24, lineHeight: 1, letterSpacing: '-0.03em', overflowWrap: 'anywhere' }}>
            {SERVICE_SHORT[service.service] || service.service}
          </div>
          <div style={{ fontSize: 11, color: theme.textMuted, marginTop: 6, lineHeight: 1.5, overflowWrap: 'anywhere' }}>
            state {labelize(service.model_state)} · sequence fill {Math.round((service.sequence_fill || 0) * 100)}%
          </div>
        </div>
        <div style={{ textAlign: 'right', minWidth: 66 }}>
          <div style={{ fontFamily: theme.displayFont, fontSize: 28, lineHeight: 1, color: tone }}>
            {Math.round((service.combined_score || 0) * 100)}
          </div>
          <div style={{ fontSize: 11, color: theme.textMuted, marginTop: 6 }}>combined</div>
        </div>
      </div>

      <div style={{ border: `1px solid ${theme.borderLight}`, borderRadius: 14, padding: 12, background: 'transparent' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, fontSize: 11, color: theme.textMuted, marginBottom: 8 }}>
          <span>score trajectory</span>
          <span>{(service.score_history || []).length} live snapshots</span>
        </div>
        <svg viewBox="0 0 180 42" style={{ width: '100%', height: 46, display: 'block', color: theme.text }}>
          <path d={path} fill="none" stroke={tone} strokeWidth="2.2" strokeLinecap="round" />
        </svg>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: 10, marginTop: 12 }}>
        <div style={{ minWidth: 0 }}>
          <div style={{ fontSize: 10, letterSpacing: '0.14em', textTransform: 'uppercase', color: theme.textMuted }}>IF</div>
          <div style={{ fontSize: 15, marginTop: 6, overflowWrap: 'anywhere' }}>{formatValue(service.if_score)}</div>
        </div>
        <div style={{ minWidth: 0 }}>
          <div style={{ fontSize: 10, letterSpacing: '0.14em', textTransform: 'uppercase', color: theme.textMuted }}>LSTM</div>
          <div style={{ fontSize: 15, marginTop: 6, overflowWrap: 'anywhere' }}>{formatValue(service.lstm_score)}</div>
        </div>
        <div style={{ minWidth: 0 }}>
          <div style={{ fontSize: 10, letterSpacing: '0.14em', textTransform: 'uppercase', color: theme.textMuted }}>Flags</div>
          <div style={{ fontSize: 15, marginTop: 6, overflowWrap: 'anywhere' }}>{(service.feature_flags || []).slice(0, 2).join(', ') || 'none'}</div>
        </div>
      </div>

      <div style={{ marginTop: 12, fontSize: 11, color: theme.textMuted, lineHeight: 1.6, overflowWrap: 'anywhere' }}>
        {prediction
          ? `Predictive alert: ${labelize(prediction.failure_type)} · ${primaryAction?.summary || prediction.message || 'preventive action ready'}`
          : 'No predictive alert is active for this service right now.'}
      </div>
    </div>
  )
}

export default function ModelsPage({ insights, topology, history, connected }) {
  const { theme, dark } = useTheme()
  const services = insights?.services || []
  const models = insights?.models || {}
  const summary = insights?.summary || {}
  const predictiveAlerts = useMemo(
    () => [...(topology?.predictive_alerts || insights?.predictive_alerts || [])].sort((a, b) => (b.lstm_score || 0) - (a.lstm_score || 0)),
    [insights?.predictive_alerts, topology?.predictive_alerts]
  )
  const dominantFeatures = insights?.dominant_features || []
  const readyServices = services.filter(service => service.model_state === 'ready')
  const warmingServices = services.filter(service => service.model_state !== 'ready')
  const activeServices = services.filter(service => (service.score_history || []).some(point => typeof point?.score === 'number'))
  const topServices = services.slice(0, 6)
  const recentHistory = history || []

  const coverage = useMemo(() => {
    if (!recentHistory.length || !services.length) return 'Awaiting live history'
    return `${recentHistory.length} snapshots across ${services.length} monitored services`
  }, [recentHistory.length, services.length])

  const featureDrivers = dominantFeatures.slice(0, 6)
  const sequenceLeaders = services
    .filter(service => (service.sequence_highlights || []).length)
    .slice(0, 4)
  const topRiskService = services[0] || null
  const latestTimestamp = insights?.timestamp || topology?.timestamp || null
  const loadedCount = [models.isolation_forest?.loaded, models.lstm?.loaded].filter(Boolean).length
  const modelLoadHealthy = Boolean(models.isolation_forest?.loaded && models.lstm?.loaded)

  return (
    <div
      style={{
        flex: 1,
        overflowY: 'auto',
        padding: '28px 28px 36px',
        color: theme.text,
        background:
          `radial-gradient(circle at top left, ${dark ? 'rgba(255,123,53,0.08)' : 'rgba(196,92,10,0.08)'}, transparent 26%), ${theme.bg}`,
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 20, alignItems: 'flex-start', borderBottom: `1px solid ${theme.borderLight}`, paddingBottom: 20, marginBottom: 24 }}>
        <div style={{ minWidth: 0 }}>
          <div style={{ fontSize: 10, letterSpacing: '0.18em', textTransform: 'uppercase', color: theme.textMuted }}>Model Insights</div>
          <h1 style={{ fontFamily: theme.displayFont, fontSize: 'clamp(28px, 3vw, 44px)', lineHeight: 0.98, margin: '8px 0 0', fontWeight: 400, letterSpacing: '-0.03em', maxWidth: 840 }}>
            Live Isolation Forest and LSTM telemetry for anomaly pressure, pre-failure prediction, and feature movement
          </h1>
        </div>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', justifyContent: 'flex-end' }}>
          <StatusPill text={connected ? 'backend connected' : 'backend offline'} tone={connected ? theme.accent : '#cc2222'} theme={theme} />
          <StatusPill text={modelLoadHealthy ? 'models loaded' : `${loadedCount}/2 models loaded`} tone={modelLoadHealthy ? theme.accent : '#c45c0a'} theme={theme} />
          <StatusPill text={latestTimestamp ? `updated ${formatClock(latestTimestamp)}` : 'awaiting telemetry'} tone={theme.textMuted} theme={theme} />
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12, marginBottom: 22 }}>
        <MetricCard label="Services Ready" value={summary.ready_service_count ?? readyServices.length} meta={`${warmingServices.length} services still warming or running IF-only`} color={theme.accent} theme={theme} />
        <MetricCard label="Predictive Alerts" value={predictiveAlerts.length} meta="live LSTM-led pre-failure warnings with preventive actions" color={anomalyScoreColor(0.62, 'fill', theme)} theme={theme} />
        <MetricCard label="Highest LSTM Risk" value={summary.highest_lstm_service ? `${SERVICE_SHORT[summary.highest_lstm_service] || summary.highest_lstm_service} · ${formatPercent(summary.highest_lstm_score)}` : '—'} meta="top sequence-driven failure risk right now" color={anomalyScoreColor(summary.highest_lstm_score || 0, 'fill', theme)} theme={theme} />
        <MetricCard label="Highest IF Drift" value={summary.highest_if_service ? `${SERVICE_SHORT[summary.highest_if_service] || summary.highest_if_service} · ${formatPercent(summary.highest_if_score)}` : '—'} meta="largest current feature-space deviation" color={anomalyScoreColor(summary.highest_if_score || 0, 'fill', theme)} theme={theme} />
        <MetricCard label="History Coverage" value={recentHistory.length || '—'} meta={coverage} color={theme.text} theme={theme} />
        <MetricCard label="Live Risk Leader" value={topRiskService ? `${SERVICE_SHORT[topRiskService.service] || topRiskService.service} · ${Math.round((topRiskService.combined_score || 0) * 100)}` : '—'} meta={topRiskService ? `model state ${labelize(topRiskService.model_state)}` : 'awaiting scored services'} color={topRiskService ? anomalyScoreColor(topRiskService.combined_score || 0, 'fill', theme) : theme.textMuted} theme={theme} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.08fr) minmax(320px, 0.92fr)', gap: 18, alignItems: 'start' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 18, minWidth: 0 }}>
          <Section title="Service Risk Trajectories" kicker="Live score movement" theme={theme}>
            {topServices.length ? (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 12 }}>
                {topServices.map(service => <ServiceTrendCard key={service.service} service={service} theme={theme} />)}
              </div>
            ) : (
              <EmptyState text="No model-backed service telemetry is available yet. This section will populate once the backend publishes scored service windows." theme={theme} />
            )}
          </Section>

          <Section title="Pre-Failure Predictor" kicker="LSTM-led live alerts" theme={theme}>
            <div style={{ display: 'grid', gap: 12 }}>
              {predictiveAlerts.length ? predictiveAlerts.map(alert => {
                const tone = anomalyScoreColor(alert.lstm_score || alert.combined_score || 0, 'fill', theme)
                const actions = alert.preventive_actions || []
                return (
                  <div key={`${alert.service}-${alert.detected_at || alert.updated_at || alert.timestamp || 'now'}`} style={{ borderTop: `1px solid ${theme.borderLight}`, paddingTop: 12, display: 'grid', gap: 8, minWidth: 0 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'flex-start' }}>
                      <div style={{ minWidth: 0 }}>
                        <div style={{ fontFamily: theme.displayFont, fontSize: 22, overflowWrap: 'anywhere' }}>{SERVICE_SHORT[alert.service] || alert.service}</div>
                        <div style={{ fontSize: 11, color: theme.textMuted, marginTop: 4, lineHeight: 1.5, overflowWrap: 'anywhere' }}>
                          {labelize(alert.failure_type)} · LSTM risk {formatPercent(alert.lstm_score)} · combined {formatValue(alert.combined_score)}
                        </div>
                      </div>
                      <div style={{ color: tone, fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.14em', overflowWrap: 'anywhere' }}>
                        {alert.status || 'active'}
                      </div>
                    </div>
                    <div style={{ fontSize: 11, color: theme.text, lineHeight: 1.7, overflowWrap: 'anywhere' }}>
                      {alert.message}
                    </div>
                    <div style={{ display: 'grid', gap: 8 }}>
                      {actions.slice(0, 2).map(action => (
                        <div key={`${alert.service}-${action.action}`} style={{ borderLeft: `2px solid ${action.automatic ? '#cc2222' : theme.accent}`, paddingLeft: 10, minWidth: 0 }}>
                          <div style={{ fontSize: 10, color: theme.text, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', overflowWrap: 'anywhere' }}>
                            {labelize(action.action)}{action.automatic ? ' · automatic' : ''}
                          </div>
                          <div style={{ fontSize: 11, color: theme.textMuted, lineHeight: 1.6, marginTop: 4, overflowWrap: 'anywhere' }}>
                            {action.summary}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )
              }) : (
                <EmptyState text="No active pre-failure alerts are open right now. This section updates from the live predictive alert stream generated by the loaded LSTM model." theme={theme} />
              )}
            </div>
          </Section>

          <Section title="Coverage and Warm-Up" kicker="Runtime scoring posture" theme={theme}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12 }}>
              <div style={{ border: `1px solid ${theme.borderLight}`, borderRadius: 18, padding: 16, background: theme.card }}>
                <div style={{ fontSize: 10, color: theme.textMuted, textTransform: 'uppercase', letterSpacing: '0.16em' }}>Actively scored</div>
                <div style={{ fontFamily: theme.displayFont, fontSize: 28, marginTop: 10, lineHeight: 1 }}>{activeServices.length}</div>
                <div style={{ fontSize: 11, color: theme.textMuted, marginTop: 10, lineHeight: 1.6 }}>
                  Services with at least one recorded score in the recent model history.
                </div>
              </div>
              <div style={{ border: `1px solid ${theme.borderLight}`, borderRadius: 18, padding: 16, background: theme.card }}>
                <div style={{ fontSize: 10, color: theme.textMuted, textTransform: 'uppercase', letterSpacing: '0.16em' }}>LSTM ready</div>
                <div style={{ fontFamily: theme.displayFont, fontSize: 28, marginTop: 10, lineHeight: 1 }}>{readyServices.length}</div>
                <div style={{ fontSize: 11, color: theme.textMuted, marginTop: 10, lineHeight: 1.6 }}>
                  Services whose sequence windows are full enough for the LSTM to contribute directly.
                </div>
              </div>
              <div style={{ border: `1px solid ${theme.borderLight}`, borderRadius: 18, padding: 16, background: theme.card }}>
                <div style={{ fontSize: 10, color: theme.textMuted, textTransform: 'uppercase', letterSpacing: '0.16em' }}>Still warming</div>
                <div style={{ fontFamily: theme.displayFont, fontSize: 28, marginTop: 10, lineHeight: 1 }}>{warmingServices.length}</div>
                <div style={{ fontSize: 11, color: theme.textMuted, marginTop: 10, lineHeight: 1.6 }}>
                  Services still building enough telemetry for sequence-aware predictions.
                </div>
              </div>
            </div>
          </Section>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 18, minWidth: 0 }}>
          <Section title="Model Registry" kicker="Loaded runtime artifacts" theme={theme}>
            <div style={{ display: 'grid', gap: 12 }}>
              {[
                ['Isolation Forest', models.isolation_forest],
                ['LSTM', models.lstm],
              ].map(([name, model]) => (
                <div key={name} style={{ border: `1px solid ${theme.borderLight}`, borderRadius: 16, padding: 16, background: dark ? 'rgba(255,255,255,0.03)' : 'rgba(26,26,26,0.025)', minWidth: 0 }}>
                  <div style={{ fontFamily: theme.displayFont, fontSize: 22, overflowWrap: 'anywhere' }}>{name}</div>
                  <div style={{ fontSize: 11, color: theme.textMuted, marginTop: 8, lineHeight: 1.7, overflowWrap: 'anywhere' }}>
                    <div>loaded: {model?.loaded ? 'yes' : 'no'}</div>
                    <div>type: {model?.type || 'unknown'}</div>
                    {model?.feature_count != null && <div>features: {model.feature_count}</div>}
                    {model?.window_size != null && <div>sequence window: {model.window_size}</div>}
                    {model?.threshold != null && <div>threshold: {Number(model.threshold).toFixed(6)}</div>}
                    <div>artifact: {model?.path || 'n/a'}</div>
                  </div>
                </div>
              ))}
            </div>
          </Section>

          <Section title="Dominant Feature Pressure" kicker="Isolation Forest contributors" theme={theme}>
            <div style={{ display: 'grid', gap: 10 }}>
              {featureDrivers.length ? featureDrivers.map(item => (
                <div key={item.feature} style={{ minWidth: 0 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, fontSize: 11, color: theme.textMuted, marginBottom: 6 }}>
                    <span style={{ overflowWrap: 'anywhere' }}>{labelize(item.feature)}</span>
                    <span style={{ color: theme.text }}>{formatValue(item.weight)}</span>
                  </div>
                  <div style={{ height: 7, background: theme.borderLight, borderRadius: 999 }}>
                    <div style={{ width: `${Math.min((item.weight || 0) * 10, 100)}%`, height: '100%', borderRadius: 999, background: theme.accent }} />
                  </div>
                </div>
              )) : (
                <EmptyState text="Feature pressure will appear here as soon as live service telemetry fills the scoring windows." theme={theme} />
              )}
            </div>
          </Section>

          <Section title="Sequence Lens" kicker="Latest LSTM timestep features" theme={theme}>
            <div style={{ display: 'grid', gap: 12 }}>
              {sequenceLeaders.length ? sequenceLeaders.map(service => (
                <div key={service.service} style={{ border: `1px solid ${theme.borderLight}`, borderRadius: 16, padding: 16, background: dark ? 'rgba(255,255,255,0.03)' : 'rgba(26,26,26,0.025)', minWidth: 0 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'center' }}>
                    <div style={{ fontFamily: theme.displayFont, fontSize: 21, overflowWrap: 'anywhere' }}>{SERVICE_SHORT[service.service] || service.service}</div>
                    <div style={{ fontSize: 11, color: theme.textMuted, overflowWrap: 'anywhere' }}>{labelize(service.model_state)}</div>
                  </div>
                  <div style={{ display: 'grid', gap: 8, marginTop: 12 }}>
                    {(service.sequence_highlights || []).slice(0, 5).map(item => (
                      <div key={item.feature} style={{ display: 'flex', justifyContent: 'space-between', gap: 12, fontSize: 11, color: theme.textMuted }}>
                        <span style={{ overflowWrap: 'anywhere' }}>{labelize(item.feature)}</span>
                        <span style={{ color: theme.text }}>{formatValue(item.value)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )) : (
                <EmptyState text="Sequence-level features will populate here when the live LSTM window has enough fresh telemetry to rank the latest timestep." theme={theme} />
              )}
            </div>
          </Section>
        </div>
      </div>
    </div>
  )
}
