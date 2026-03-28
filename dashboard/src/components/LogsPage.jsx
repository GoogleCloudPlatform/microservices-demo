import { useMemo, useState } from 'react'
import { useTheme } from '../ThemeContext'

function Section({ eyebrow, title, children, theme }) {
  return (
    <section style={{ border: `1px solid ${theme.borderLight}`, borderRadius: 18, padding: 18, background: theme.card }}>
      <div style={{ fontSize: 10, letterSpacing: '0.18em', textTransform: 'uppercase', color: theme.textMuted, marginBottom: 8 }}>
        {eyebrow}
      </div>
      <h2 style={{ fontFamily: theme.displayFont, fontWeight: 400, fontSize: 26, margin: 0, marginBottom: 16, letterSpacing: '-0.03em' }}>
        {title}
      </h2>
      {children}
    </section>
  )
}

function LogRow({ item, theme }) {
  const tone = item.level === 'ERROR' || item.level === 'CRITICAL' ? '#cc2222' : item.level === 'WARNING' ? '#c45c0a' : theme.textMuted
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '74px 112px minmax(0, 1fr)', gap: 12, padding: '10px 0', borderTop: `1px solid ${theme.borderLight}` }}>
      <div style={{ fontSize: 10, color: tone, fontWeight: 'bold', letterSpacing: '0.1em' }}>{item.level}</div>
      <div style={{ fontSize: 10, color: theme.textMuted }}>{item.created_at ? new Date(item.created_at).toLocaleTimeString('en-US', { hour12: false }) : '—'}</div>
      <div>
        <div style={{ fontSize: 11, color: theme.text, lineHeight: 1.5 }}>{item.message}</div>
        <div style={{ fontSize: 9, color: theme.textDim, marginTop: 4 }}>{item.logger}</div>
      </div>
    </div>
  )
}

function EventRow({ item, theme }) {
  const tone = item.severity === 'critical' ? '#cc2222' : item.severity === 'warning' ? '#c45c0a' : theme.textMuted
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '12px minmax(0, 1fr)', gap: 10, paddingTop: 12 }}>
      <div style={{ display: 'flex', justifyContent: 'center' }}>
        <span style={{ width: 8, height: 8, borderRadius: '50%', background: tone, marginTop: 5 }} />
      </div>
      <div style={{ borderTop: `1px solid ${theme.borderLight}`, paddingTop: 12 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12 }}>
          <div style={{ fontSize: 11, color: theme.text, fontWeight: 'bold' }}>{item.title}</div>
          <div style={{ fontSize: 9, color: theme.textDim }}>{item.created_at ? new Date(item.created_at).toLocaleTimeString('en-US', { hour12: false }) : '—'}</div>
        </div>
        <div style={{ fontSize: 10, color: theme.textMuted, lineHeight: 1.5, marginTop: 6 }}>{item.message}</div>
        <div style={{ fontSize: 9, color: tone, marginTop: 6, textTransform: 'uppercase', letterSpacing: '0.1em' }}>
          {item.category}{item.service ? ` · ${item.service}` : ''}{item.status ? ` · ${item.status}` : ''}
        </div>
      </div>
    </div>
  )
}

export default function LogsPage({ events, logs, connected }) {
  const { theme, dark } = useTheme()
  const [levelFilter, setLevelFilter] = useState('ALL')

  const filteredLogs = useMemo(() => {
    if (levelFilter === 'ALL') return logs
    return logs.filter(item => item.level === levelFilter)
  }, [logs, levelFilter])

  const summary = useMemo(() => {
    const counts = { ERROR: 0, WARNING: 0, INFO: 0 }
    logs.forEach(item => {
      if (item.level === 'ERROR' || item.level === 'CRITICAL') counts.ERROR += 1
      else if (item.level === 'WARNING') counts.WARNING += 1
      else counts.INFO += 1
    })
    return counts
  }, [logs])

  const buttonStyle = active => ({
    fontSize: 10,
    letterSpacing: '0.12em',
    textTransform: 'uppercase',
    border: `1px solid ${active ? theme.border : theme.borderLight}`,
    background: active ? theme.border : 'transparent',
    color: active ? theme.bg : theme.textMuted,
    padding: '6px 10px',
    borderRadius: 999,
    cursor: 'pointer',
  })

  return (
    <div
      style={{
        flex: 1,
        overflowY: 'auto',
        padding: '28px 28px 36px',
        color: theme.text,
        background: `radial-gradient(circle at top left, ${dark ? 'rgba(255,123,53,0.08)' : 'rgba(196,92,10,0.08)'}, transparent 24%), ${theme.bg}`,
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 20, alignItems: 'flex-start', borderBottom: `1px solid ${theme.borderLight}`, paddingBottom: 20, marginBottom: 24 }}>
        <div>
          <div style={{ fontSize: 10, letterSpacing: '0.18em', textTransform: 'uppercase', color: theme.textMuted }}>System Logs</div>
          <h1 style={{ fontFamily: theme.displayFont, fontSize: 'clamp(28px, 3vw, 44px)', lineHeight: 0.98, margin: '8px 0 0', fontWeight: 400, letterSpacing: '-0.03em', maxWidth: 760 }}>
            Persisted timeline and backend logs for predictive alerts, remediation, and platform health
          </h1>
        </div>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', justifyContent: 'flex-end' }}>
          <span style={{ border: `1px solid ${theme.borderLight}`, borderRadius: 999, padding: '6px 10px', fontSize: 10, color: connected ? theme.accent : theme.textMuted }}>
            {connected ? 'backend connected' : 'backend offline'}
          </span>
          <span style={{ border: `1px solid ${theme.borderLight}`, borderRadius: 999, padding: '6px 10px', fontSize: 10, color: theme.textMuted }}>
            {events.length} events · {logs.length} logs in memory window
          </span>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: 12, marginBottom: 22 }}>
        {[
          ['Errors', summary.ERROR, '#cc2222', 'critical and error-level backend records'],
          ['Warnings', summary.WARNING, '#c45c0a', 'predictive and operational warnings'],
          ['Info', summary.INFO, theme.accent, 'startup, lifecycle, and healthy closures'],
          ['Latest event', events[0]?.service || '—', theme.text, events[0]?.title || 'awaiting persisted events'],
        ].map(([label, value, color, meta]) => (
          <div key={label} style={{ border: `1px solid ${theme.borderLight}`, borderRadius: 16, padding: 14, background: theme.card }}>
            <div style={{ fontSize: 10, letterSpacing: '0.18em', textTransform: 'uppercase', color: theme.textMuted }}>{label}</div>
            <div style={{ fontFamily: theme.displayFont, fontSize: 30, lineHeight: 1, marginTop: 10, color }}>{value}</div>
            <div style={{ fontSize: 11, color: theme.textMuted, marginTop: 10, lineHeight: 1.5 }}>{meta}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(340px, 0.9fr) minmax(0, 1.1fr)', gap: 18 }}>
        <Section eyebrow="Timeline" title="Event Flow" theme={theme}>
          <div style={{ display: 'grid', gap: 2 }}>
            {events.length > 0 ? events.slice(0, 20).map(item => <EventRow key={`${item.id}-${item.created_at}`} item={item} theme={theme} />) : (
              <div style={{ fontSize: 11, color: theme.textMuted }}>No persisted events yet.</div>
            )}
          </div>
        </Section>

        <Section eyebrow="Database-backed log stream" title="System Logs" theme={theme}>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 10 }}>
            {['ALL', 'ERROR', 'WARNING', 'INFO'].map(level => (
              <button key={level} type="button" onClick={() => setLevelFilter(level)} style={buttonStyle(levelFilter === level)}>
                {level}
              </button>
            ))}
          </div>
          <div style={{ display: 'grid' }}>
            {filteredLogs.length > 0 ? filteredLogs.slice(0, 80).map(item => (
              <LogRow key={`${item.id}-${item.created_at}`} item={item} theme={theme} />
            )) : (
              <div style={{ fontSize: 11, color: theme.textMuted }}>No logs match the current filter.</div>
            )}
          </div>
        </Section>
      </div>
    </div>
  )
}
