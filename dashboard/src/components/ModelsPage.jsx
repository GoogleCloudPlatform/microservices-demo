import { useTheme } from '../ThemeContext'
import { anomalyScoreColor, SERVICE_SHORT } from '../styles/theme'

function Section({ title, kicker, children, theme }) {
  return (
    <section style={{ border: `1px solid ${theme.borderLight}`, borderRadius: 18, padding: 18, background: theme.card }}>
      <div style={{ fontSize: 10, letterSpacing: '0.18em', textTransform: 'uppercase', color: theme.textMuted, marginBottom: 8 }}>
        {kicker}
      </div>
      <h2 style={{ fontFamily: theme.displayFont, fontWeight: 400, fontSize: 26, margin: 0, marginBottom: 16, letterSpacing: '-0.03em' }}>
        {title}
      </h2>
      {children}
    </section>
  )
}

function MetricCard({ label, value, meta, color, theme }) {
  return (
    <div style={{ border: `1px solid ${theme.borderLight}`, borderRadius: 16, padding: 14, background: theme.card }}>
      <div style={{ fontSize: 10, letterSpacing: '0.18em', textTransform: 'uppercase', color: theme.textMuted }}>{label}</div>
      <div style={{ fontFamily: theme.displayFont, fontSize: 30, lineHeight: 1, marginTop: 10, color }}>{value}</div>
      <div style={{ fontSize: 11, color: theme.textMuted, marginTop: 10, lineHeight: 1.5 }}>{meta}</div>
    </div>
  )
}

function formatValue(value) {
  if (value == null) return '—'
  return Number(value).toFixed(3)
}

export default function ModelsPage({ insights, connected }) {
  const { theme, dark } = useTheme()
  const services = insights?.services || []
  const models = insights?.models || {}
  const readyServices = services.filter(service => service.model_state === 'ready')
  const warmingServices = services.filter(service => service.model_state !== 'ready')
  const hottest = services.slice(0, 6)

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
        <div>
          <div style={{ fontSize: 10, letterSpacing: '0.18em', textTransform: 'uppercase', color: theme.textMuted }}>Models</div>
          <h1 style={{ fontFamily: theme.displayFont, fontSize: 'clamp(28px, 3vw, 44px)', lineHeight: 0.98, margin: '8px 0 0', fontWeight: 400, letterSpacing: '-0.03em', maxWidth: 760 }}>
            Real-time model telemetry for anomaly scoring, sequence readiness, and feature drivers
          </h1>
        </div>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', justifyContent: 'flex-end' }}>
          <span style={{ border: `1px solid ${theme.borderLight}`, borderRadius: 999, padding: '6px 10px', fontSize: 10, color: connected ? theme.accent : theme.textMuted }}>
            {connected ? 'backend connected' : 'backend offline'}
          </span>
          <span style={{ border: `1px solid ${theme.borderLight}`, borderRadius: 999, padding: '6px 10px', fontSize: 10, color: models.isolation_forest?.loaded ? theme.accent : theme.textMuted }}>
            {models.isolation_forest?.loaded ? 'models loaded' : 'models unavailable'}
          </span>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: 12, marginBottom: 22 }}>
        <MetricCard label="Services Ready" value={readyServices.length} meta={`${warmingServices.length} still warming the LSTM window`} color={theme.accent} theme={theme} />
        <MetricCard label="Isolation Forest" value={models.isolation_forest?.feature_count || '—'} meta={`features · ${models.isolation_forest?.type || 'unloaded'}`} color={anomalyScoreColor(0.2, 'fill', theme)} theme={theme} />
        <MetricCard label="LSTM Window" value={models.lstm?.window_size || '—'} meta={`${models.lstm?.feature_count || '—'} features per timestep`} color={anomalyScoreColor(0.5, 'fill', theme)} theme={theme} />
        <MetricCard label="Last Refresh" value={insights?.timestamp ? new Date(insights.timestamp).toLocaleTimeString('en-US', { hour12: false }) : '—'} meta="live backend model telemetry" color={theme.text} theme={theme} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.08fr) minmax(320px, 0.92fr)', gap: 18, alignItems: 'start' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
          <Section title="Service Model States" kicker="Scoreboard" theme={theme}>
            <div style={{ display: 'grid', gap: 10 }}>
              {services.map(service => {
                const tone = anomalyScoreColor(service.combined_score || 0, 'fill', theme)
                return (
                  <div key={service.service} style={{ border: `1px solid ${theme.borderLight}`, borderRadius: 14, padding: 14, background: dark ? 'rgba(255,255,255,0.03)' : 'rgba(26,26,26,0.025)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'flex-start' }}>
                      <div>
                        <div style={{ fontFamily: theme.displayFont, fontSize: 24, lineHeight: 1, letterSpacing: '-0.03em' }}>{SERVICE_SHORT[service.service] || service.service}</div>
                        <div style={{ fontSize: 11, color: theme.textMuted, marginTop: 6 }}>
                          state {service.model_state.replace(/_/g, ' ')} · sequence fill {Math.round((service.sequence_fill || 0) * 100)}%
                        </div>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontFamily: theme.displayFont, fontSize: 26, lineHeight: 1, color: tone }}>{Math.round((service.combined_score || 0) * 100)}</div>
                        <div style={{ fontSize: 11, color: theme.textMuted, marginTop: 6 }}>combined score</div>
                      </div>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: 10, marginTop: 14 }}>
                      <div>
                        <div style={{ fontSize: 10, letterSpacing: '0.14em', textTransform: 'uppercase', color: theme.textMuted }}>IF</div>
                        <div style={{ fontSize: 14, marginTop: 6 }}>{formatValue(service.if_score)}</div>
                      </div>
                      <div>
                        <div style={{ fontSize: 10, letterSpacing: '0.14em', textTransform: 'uppercase', color: theme.textMuted }}>LSTM</div>
                        <div style={{ fontSize: 14, marginTop: 6 }}>{formatValue(service.lstm_score)}</div>
                      </div>
                      <div>
                        <div style={{ fontSize: 10, letterSpacing: '0.14em', textTransform: 'uppercase', color: theme.textMuted }}>Flags</div>
                        <div style={{ fontSize: 14, marginTop: 6 }}>{(service.feature_flags || []).slice(0, 2).join(', ') || 'none'}</div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </Section>

          <Section title="Top Model Pressure" kicker="Most anomalous services" theme={theme}>
            <div style={{ display: 'grid', gap: 12 }}>
              {hottest.map(service => {
                const tone = anomalyScoreColor(service.combined_score || 0, 'fill', theme)
                return (
                  <div key={service.service} style={{ display: 'grid', gridTemplateColumns: '140px minmax(0, 1fr)', gap: 14, alignItems: 'start', borderTop: `1px solid ${theme.borderLight}`, paddingTop: 12 }}>
                    <div>
                      <div style={{ fontFamily: theme.displayFont, fontSize: 22 }}>{SERVICE_SHORT[service.service] || service.service}</div>
                      <div style={{ fontSize: 11, color: theme.textMuted, marginTop: 4 }}>combined {formatValue(service.combined_score)}</div>
                    </div>
                    <div style={{ display: 'grid', gap: 8 }}>
                      {(service.if_contributors || []).slice(0, 4).map(item => (
                        <div key={item.feature}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: theme.textMuted, marginBottom: 4 }}>
                            <span>{item.feature.replace(/_/g, ' ')}</span>
                            <span>z {item.z_score?.toFixed ? item.z_score.toFixed(2) : item.z_score}</span>
                          </div>
                          <div style={{ height: 6, background: theme.borderLight, borderRadius: 999 }}>
                            <div style={{ width: `${Math.min((item.z_score || 0) * 14, 100)}%`, height: '100%', borderRadius: 999, background: tone }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )
              })}
            </div>
          </Section>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
          <Section title="Model Registry" kicker="Loaded artifacts" theme={theme}>
            <div style={{ display: 'grid', gap: 12 }}>
              {[
                ['Isolation Forest', models.isolation_forest],
                ['LSTM', models.lstm],
              ].map(([name, model]) => (
                <div key={name} style={{ border: `1px solid ${theme.borderLight}`, borderRadius: 14, padding: 14, background: dark ? 'rgba(255,255,255,0.03)' : 'rgba(26,26,26,0.025)' }}>
                  <div style={{ fontFamily: theme.displayFont, fontSize: 22 }}>{name}</div>
                  <div style={{ fontSize: 11, color: theme.textMuted, marginTop: 8, lineHeight: 1.6 }}>
                    <div>loaded: {model?.loaded ? 'yes' : 'no'}</div>
                    <div>type: {model?.type || 'unknown'}</div>
                    {model?.feature_count != null && <div>features: {model.feature_count}</div>}
                    {model?.window_size != null && <div>window: {model.window_size}</div>}
                    {model?.threshold != null && <div>threshold: {Number(model.threshold).toFixed(6)}</div>}
                    <div style={{ wordBreak: 'break-all' }}>path: {model?.path || 'n/a'}</div>
                  </div>
                </div>
              ))}
            </div>
          </Section>

          <Section title="Latest Sequence Lens" kicker="Per-service latest timestep features" theme={theme}>
            <div style={{ display: 'grid', gap: 12 }}>
              {services.slice(0, 6).map(service => (
                <div key={service.service} style={{ border: `1px solid ${theme.borderLight}`, borderRadius: 14, padding: 14, background: dark ? 'rgba(255,255,255,0.03)' : 'rgba(26,26,26,0.025)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'center' }}>
                    <div style={{ fontFamily: theme.displayFont, fontSize: 20 }}>{SERVICE_SHORT[service.service] || service.service}</div>
                    <div style={{ fontSize: 11, color: theme.textMuted }}>state {service.model_state.replace(/_/g, ' ')}</div>
                  </div>
                  <div style={{ display: 'grid', gap: 8, marginTop: 10 }}>
                    {(service.sequence_highlights || []).slice(0, 5).map(item => (
                      <div key={item.feature} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: theme.textMuted }}>
                        <span>{item.feature.replace(/_/g, ' ')}</span>
                        <span style={{ color: theme.text }}>{Number(item.value).toFixed(3)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </Section>
        </div>
      </div>
    </div>
  )
}
