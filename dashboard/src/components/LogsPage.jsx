import { useMemo, useState } from 'react'
import { API_BASE } from '../api'
import { useTheme } from '../ThemeContext'

function Section({ eyebrow, title, actions, children, theme }) {
  return (
    <section style={{ border: `1px solid ${theme.borderLight}`, borderRadius: 20, padding: 20, background: theme.card, minWidth: 0 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, alignItems: 'flex-start', marginBottom: 16 }}>
        <div>
          <div style={{ fontSize: 10, letterSpacing: '0.18em', textTransform: 'uppercase', color: theme.textMuted, marginBottom: 8 }}>
            {eyebrow}
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

function formatClock(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleTimeString('en-US', { hour12: false })
}

function downloadBlob(filename, content, type) {
  const blob = new Blob([content], { type })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  URL.revokeObjectURL(url)
}

function LogRow({ item, theme }) {
  const tone = item.level === 'ERROR' || item.level === 'CRITICAL' ? '#cc2222' : item.level === 'WARNING' ? '#c45c0a' : theme.textMuted
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '74px 92px minmax(0, 1fr)', gap: 12, padding: '12px 0', borderTop: `1px solid ${theme.borderLight}`, minWidth: 0 }}>
      <div style={{ fontSize: 10, color: tone, fontWeight: 700, letterSpacing: '0.1em', overflowWrap: 'anywhere' }}>{item.level}</div>
      <div style={{ fontSize: 10, color: theme.textMuted }}>{formatClock(item.created_at)}</div>
      <div style={{ minWidth: 0 }}>
        <div style={{ fontSize: 11, color: theme.text, lineHeight: 1.6, overflowWrap: 'anywhere' }}>{item.message}</div>
        <div style={{ fontSize: 9, color: theme.textDim, marginTop: 4, overflowWrap: 'anywhere' }}>{item.logger}</div>
      </div>
    </div>
  )
}

function EventRow({ item, theme }) {
  const tone = item.severity === 'critical' ? '#cc2222' : item.severity === 'warning' ? '#c45c0a' : theme.accent
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '12px minmax(0, 1fr)', gap: 12, paddingTop: 12 }}>
      <div style={{ display: 'flex', justifyContent: 'center' }}>
        <span style={{ width: 8, height: 8, borderRadius: '50%', background: tone, marginTop: 5 }} />
      </div>
      <div style={{ borderTop: `1px solid ${theme.borderLight}`, paddingTop: 12, minWidth: 0 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'flex-start' }}>
          <div style={{ fontSize: 11, color: theme.text, fontWeight: 700, lineHeight: 1.5, overflowWrap: 'anywhere' }}>{item.title}</div>
          <div style={{ fontSize: 9, color: theme.textDim }}>{formatClock(item.created_at)}</div>
        </div>
        <div style={{ fontSize: 10, color: theme.textMuted, lineHeight: 1.6, marginTop: 6, overflowWrap: 'anywhere' }}>{item.message}</div>
        <div style={{ fontSize: 9, color: tone, marginTop: 8, textTransform: 'uppercase', letterSpacing: '0.1em', overflowWrap: 'anywhere' }}>
          {item.category}{item.service ? ` · ${item.service}` : ''}{item.status ? ` · ${item.status}` : ''}
        </div>
      </div>
    </div>
  )
}

function StoryCard({ story, theme }) {
  return (
    <div style={{ border: `1px solid ${theme.borderLight}`, borderRadius: 18, padding: 16, background: theme.card, minWidth: 0 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'flex-start' }}>
        <div style={{ minWidth: 0 }}>
          <div style={{ fontFamily: theme.displayFont, fontSize: 22, lineHeight: 1, letterSpacing: '-0.03em', overflowWrap: 'anywhere' }}>
            {story.service}
          </div>
          <div style={{ fontSize: 11, color: theme.textMuted, marginTop: 6 }}>
            {story.events.length} recorded event{story.events.length === 1 ? '' : 's'}
          </div>
        </div>
        <div style={{ fontSize: 10, color: theme.textMuted }}>{formatClock(story.latestAt)}</div>
      </div>
      <div style={{ display: 'grid', gap: 8, marginTop: 12 }}>
        {story.events.slice(0, 4).map(item => (
          <div key={`${item.id}-${item.created_at}`} style={{ fontSize: 11, color: theme.textMuted, lineHeight: 1.6, overflowWrap: 'anywhere' }}>
            <span style={{ color: theme.text }}>{item.title}</span>
            {' · '}
            {item.message}
          </div>
        ))}
      </div>
      <div style={{ marginTop: 12, fontSize: 11, color: theme.text, lineHeight: 1.6, overflowWrap: 'anywhere' }}>
        {story.recovery}
      </div>
    </div>
  )
}

export default function LogsPage({ events, logs, timestamp, topology, connected }) {
  const { theme, dark } = useTheme()
  const [levelFilter, setLevelFilter] = useState('ALL')
  const [downloading, setDownloading] = useState(false)

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

  const stories = useMemo(() => {
    const grouped = new Map()
    events.forEach(item => {
      const key = item.service || item.category || 'platform'
      if (!grouped.has(key)) {
        grouped.set(key, { service: key, latestAt: item.created_at, events: [] })
      }
      const story = grouped.get(key)
      story.events.push(item)
      if ((story.latestAt || '') < (item.created_at || '')) story.latestAt = item.created_at
    })
    return Array.from(grouped.values())
      .map(story => {
        const recoveryEvent = story.events.find(item => item.status === 'closed' || /recovered|resolved|healthy/i.test(item.title || ''))
        return {
          ...story,
          recovery: recoveryEvent
            ? `Recovery path recorded: ${recoveryEvent.title}.`
            : 'Recovery is still in progress or awaiting an explicit closure event.',
        }
      })
      .sort((a, b) => (b.latestAt || '').localeCompare(a.latestAt || ''))
      .slice(0, 8)
  }, [events])

  const latestTimeline = topology?.timeline || []
  const activeIncidents = topology?.active_incidents || []

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

  async function downloadReport(format) {
    try {
      setDownloading(true)
      const res = await fetch(`${API_BASE}/logs/report?format=${format}&event_limit=200&log_limit=300`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      if (format === 'json') {
        const payload = await res.json()
        downloadBlob(`aegis-system-report-${Date.now()}.json`, JSON.stringify(payload, null, 2), 'application/json')
      } else {
        const text = await res.text()
        downloadBlob(`aegis-system-report-${Date.now()}.md`, text, 'text/markdown')
      }
    } finally {
      setDownloading(false)
    }
  }

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
          <h1 style={{ fontFamily: theme.displayFont, fontSize: 'clamp(28px, 3vw, 44px)', lineHeight: 0.98, margin: '8px 0 0', fontWeight: 400, letterSpacing: '-0.03em', maxWidth: 820 }}>
            Live database-backed event flow, backend logs, recovery stories, and downloadable operational reports
          </h1>
        </div>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', justifyContent: 'flex-end' }}>
          <span style={{ border: `1px solid ${theme.borderLight}`, borderRadius: 999, padding: '6px 10px', fontSize: 10, color: connected ? theme.accent : theme.textMuted }}>
            {connected ? 'backend connected' : 'backend offline'}
          </span>
          <span style={{ border: `1px solid ${theme.borderLight}`, borderRadius: 999, padding: '6px 10px', fontSize: 10, color: theme.textMuted }}>
            refreshes every 3s · {timestamp ? formatClock(timestamp) : 'awaiting refresh'}
          </span>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12, marginBottom: 22 }}>
        {[
          ['Errors', summary.ERROR, '#cc2222', 'critical and error-level backend records'],
          ['Warnings', summary.WARNING, '#c45c0a', 'predictive and operational warnings'],
          ['Info', summary.INFO, theme.accent, 'startup, lifecycle, and recovery confirmations'],
          ['Active incidents', activeIncidents.length, theme.text, activeIncidents.length ? 'open remediation workflows' : 'no incident currently open'],
          ['Latest timeline event', latestTimeline[0]?.service || '—', theme.text, latestTimeline[0]?.title || 'awaiting persisted events'],
        ].map(([label, value, color, meta]) => (
          <div key={label} style={{ border: `1px solid ${theme.borderLight}`, borderRadius: 18, padding: 16, background: theme.card }}>
            <div style={{ fontSize: 10, letterSpacing: '0.18em', textTransform: 'uppercase', color: theme.textMuted }}>{label}</div>
            <div style={{ fontFamily: theme.displayFont, fontSize: 30, lineHeight: 1, marginTop: 10, color, overflowWrap: 'anywhere' }}>{value}</div>
            <div style={{ fontSize: 11, color: theme.textMuted, marginTop: 10, lineHeight: 1.6, overflowWrap: 'anywhere' }}>{meta}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.15fr) minmax(320px, 0.85fr)', gap: 18, marginBottom: 18 }}>
        <Section eyebrow="Timeline" title="Live Event Flow" theme={theme}>
          <div style={{ display: 'grid', gap: 2 }}>
            {events.length > 0 ? events.slice(0, 24).map(item => <EventRow key={`${item.id}-${item.created_at}`} item={item} theme={theme} />) : (
              <div style={{ fontSize: 11, color: theme.textMuted }}>No persisted events yet.</div>
            )}
          </div>
        </Section>

        <Section
          eyebrow="Export and recovery reporting"
          title="Operational Report"
          theme={theme}
          actions={(
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              <button type="button" onClick={() => downloadReport('markdown')} disabled={downloading} style={buttonStyle(false)}>
                {downloading ? 'Preparing…' : 'Download Markdown'}
              </button>
              <button type="button" onClick={() => downloadReport('json')} disabled={downloading} style={buttonStyle(false)}>
                Download JSON
              </button>
            </div>
          )}
        >
          <div style={{ display: 'grid', gap: 12 }}>
            <div style={{ fontSize: 11, color: theme.textMuted, lineHeight: 1.7 }}>
              Reports are generated directly from the persisted SQLite event and log history. Each export captures the live failure timeline, backend log stream, and recovery markers for later review.
            </div>
            <div style={{ display: 'grid', gap: 12 }}>
              {stories.length ? stories.slice(0, 3).map(story => <StoryCard key={story.service} story={story} theme={theme} />) : (
                <div style={{ fontSize: 11, color: theme.textMuted, lineHeight: 1.6 }}>
                  Recovery stories will appear here as soon as the platform records incidents, preventive actions, and closure events.
                </div>
              )}
            </div>
          </div>
        </Section>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(300px, 0.92fr) minmax(0, 1.08fr)', gap: 18 }}>
        <Section eyebrow="Incident narratives" title="Restoration Stories" theme={theme}>
          <div style={{ display: 'grid', gap: 12 }}>
            {stories.length ? stories.map(story => <StoryCard key={`${story.service}-${story.latestAt}`} story={story} theme={theme} />) : (
              <div style={{ fontSize: 11, color: theme.textMuted }}>No service narratives yet.</div>
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
            {filteredLogs.length > 0 ? filteredLogs.slice(0, 120).map(item => (
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
