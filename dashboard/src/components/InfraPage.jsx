import { useMemo } from 'react'
import { anomalyScoreColor, SERVICE_SHORT } from '../styles/theme'
import { useTheme } from '../ThemeContext'

function asArray(value) {
  return Array.isArray(value) ? value : []
}

function asObject(value) {
  return value && typeof value === 'object' && !Array.isArray(value) ? value : {}
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value))
}

function formatPercent(value, digits = 0) {
  const num = Number(value || 0)
  return `${num.toFixed(digits)}%`
}

function formatSigned(value, digits = 1, suffix = '') {
  const num = Number(value || 0)
  const prefix = num > 0 ? '+' : ''
  return `${prefix}${num.toFixed(digits)}${suffix}`
}

function formatTime(iso) {
  if (!iso) return 'Awaiting signal'
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return 'Awaiting signal'
  return date.toLocaleTimeString('en-US', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

function formatRelative(iso) {
  if (!iso) return 'No timestamp'
  const ts = new Date(iso).getTime()
  if (Number.isNaN(ts)) return 'No timestamp'
  const delta = Math.max(0, Math.round((Date.now() - ts) / 1000))
  if (delta < 60) return `${delta}s ago`
  if (delta < 3600) return `${Math.round(delta / 60)}m ago`
  return `${Math.round(delta / 3600)}h ago`
}

function formatNumber(value, digits = 0) {
  return Number(value || 0).toFixed(digits)
}

function formatStatusLabel(status) {
  return String(status || 'unknown').replace(/_/g, ' ')
}

function severityTone(score, theme) {
  return anomalyScoreColor(clamp(score, 0, 1), 'fill', theme)
}

function statusTone(status, score, theme) {
  if (status === 'critical') return severityTone(Math.max(score, 0.82), theme)
  if (status === 'warning') return severityTone(Math.max(score, 0.55), theme)
  return severityTone(Math.min(score, 0.18), theme)
}

function arrayToMap(items, key = 'service') {
  return asArray(items).reduce((acc, item) => {
    const itemKey = item?.[key]
    if (itemKey) acc[itemKey] = item
    return acc
  }, {})
}

function runtimeHealthScore(runtime) {
  if (!runtime?.exists) return 0.04
  if (!runtime?.running) return 0.2
  if (!runtime?.healthy) return 0.45
  return 0.98
}

function pressureScore(snapshot = {}) {
  return clamp(
    Math.max(
      snapshot.cpu_pressure || 0,
      snapshot.memory_pressure || 0,
      snapshot.network_pressure || 0,
      snapshot.combined_score || 0,
      (snapshot.error_rate_mean || 0) * 4
    ),
    0,
    1
  )
}

function restartScore(runtime) {
  return clamp((Number(runtime?.restart_count || 0) || 0) / 5, 0, 1)
}

function topMemoryMatches(services) {
  return Object.entries(asObject(services))
    .flatMap(([service, snapshot]) =>
      asArray(snapshot?.similar_incidents).map(match => ({
        service,
        ...match,
      }))
    )
    .sort((a, b) => (b.similarity_score || 0) - (a.similarity_score || 0))
    .slice(0, 6)
}

function latestServiceIncidents(services) {
  return Object.entries(asObject(services))
    .map(([service, snapshot]) => snapshot.latest_incident ? { service, ...snapshot.latest_incident } : null)
    .filter(Boolean)
    .sort((a, b) => {
      const ta = new Date(a.detected_at || 0).getTime()
      const tb = new Date(b.detected_at || 0).getTime()
      return tb - ta
    })
}

function miniSparkPath(points, width, height) {
  if (!points.length) return ''
  return points
    .map((value, index) => {
      const x = points.length === 1 ? width / 2 : (index / (points.length - 1)) * width
      const y = height - clamp(value, 0, 1) * height
      return `${index === 0 ? 'M' : 'L'} ${x.toFixed(2)} ${y.toFixed(2)}`
    })
    .join(' ')
}

function Section({ title, eyebrow, children, theme, tight = false }) {
  return (
    <section className="infra-section" style={{ '--section-gap': tight ? 'var(--infra-subsection-gap-tight)' : 'var(--infra-subsection-gap)' }}>
      <div className="infra-section-header">
        <span className="infra-section-eyebrow">{eyebrow}</span>
        <h2 className="infra-section-title" style={{ fontFamily: theme.displayFont }}>{title}</h2>
      </div>
      <div className="infra-section-body">{children}</div>
    </section>
  )
}

function SummaryCard({ label, value, meta, tone, theme }) {
  return (
    <div className="infra-summary-card">
      <span className="infra-summary-label">{label}</span>
      <div className="infra-summary-value" style={{ color: tone, fontFamily: theme.displayFont }}>{value}</div>
      <span className="infra-summary-meta">{meta}</span>
    </div>
  )
}

function Badge({ label, tone = 'muted' }) {
  return <span className={`infra-badge infra-badge-${tone}`}>{label}</span>
}

function StatusPill({ label, tone }) {
  return (
    <span className="infra-status-pill">
      <span className="infra-status-dot" style={{ background: tone }} />
      {label}
    </span>
  )
}

function TrendRibbon({ history, services, theme }) {
  const width = 520
  const height = 128
  const safeHistory = asArray(history)
  const avgScores = safeHistory.map(item => {
    const scores = Object.values(item.scores || {})
    if (!scores.length) return 0
    return scores.reduce((sum, value) => sum + value, 0) / scores.length
  })
  const alertCounts = safeHistory.map(item =>
    Object.values(item.scores || {}).filter(value => value > 0.7).length / Math.max(Object.keys(asObject(services)).length, 1)
  )
  const avgPath = miniSparkPath(avgScores, width, height)
  const alertPath = miniSparkPath(alertCounts, width, height)

  return (
    <div className="infra-chart-shell">
      <svg viewBox={`0 0 ${width} ${height}`} className="infra-trend-chart" preserveAspectRatio="none">
        {[0.25, 0.5, 0.75].map(mark => (
          <line
            key={mark}
            x1="0"
            y1={height - height * mark}
            x2={width}
            y2={height - height * mark}
            stroke="currentColor"
            strokeOpacity="0.09"
            strokeWidth="1"
          />
        ))}
        {avgPath && <path d={avgPath} fill="none" stroke={theme.accent} strokeWidth="2.1" strokeLinecap="round" />}
        {alertPath && <path d={alertPath} fill="none" stroke={theme.textMuted} strokeWidth="1.35" strokeDasharray="5 5" strokeLinecap="round" />}
      </svg>
      <div className="infra-chart-legend">
        <span><i style={{ background: theme.accent }} /> anomaly trend</span>
        <span><i style={{ background: theme.textMuted }} /> alert density</span>
      </div>
    </div>
  )
}

function RootCauseSpotlight({ topology, services, theme }) {
  const root = topology?.root_cause || {}
  const rootService = root.service
  const service = rootService ? services[rootService] : null
  const tone = statusTone(service?.status, service?.combined_score || root.confidence || 0, theme)

  return (
    <div className="infra-spotlight">
      <div>
        <div className="infra-kicker">Current suspected root cause</div>
        <div className="infra-headline" style={{ fontFamily: theme.displayFont }}>
          {rootService ? (SERVICE_SHORT[rootService] || rootService) : 'System nominal'}
        </div>
      </div>
      <div className="infra-spotlight-meta">
        <StatusPill label={rootService ? formatStatusLabel(root.failure_type || 'generic_anomaly') : 'no active root cause'} tone={tone} />
        <span>{rootService ? `${Math.round((root.confidence || 0) * 100)}% confidence` : 'No anomalous cascade detected'}</span>
      </div>
      <div className="infra-copy">
        {rootService
          ? `Blast radius across ${(root.affected_services || []).length || 1} service${(root.affected_services || []).length === 1 ? '' : 's'}. ${topology?.recommendation || ''}`
          : 'All monitored services are currently trending within the normal operating envelope.'}
      </div>
    </div>
  )
}

function FleetSummary({ services, theme, infrastructure }) {
  const entries = Object.entries(asObject(services))
  const summary = asObject(infrastructure?.fleet_summary)
  const active = entries.filter(([, svc]) => svc.latest_incident?.status === 'active')
  const isolated = active.filter(([, svc]) => svc.latest_incident?.containment?.containment_mode === 'isolate')
  const manualRequired = active.filter(([, svc]) => svc.latest_incident?.containment?.manual_required)

  const rows = [
    { label: 'healthy', value: summary.healthy ?? entries.filter(([, svc]) => svc.status === 'normal').length, tone: severityTone(0.12, theme) },
    { label: 'warning', value: summary.warning ?? entries.filter(([, svc]) => svc.status === 'warning').length, tone: severityTone(0.55, theme) },
    { label: 'critical', value: summary.critical ?? entries.filter(([, svc]) => svc.status === 'critical').length, tone: severityTone(0.92, theme) },
    { label: 'isolated', value: summary.isolated ?? isolated.length, tone: theme.accent },
    { label: 'manual required', value: summary.manual_required ?? manualRequired.length, tone: theme.text },
  ]

  return (
    <div className="infra-metric-grid">
      {rows.map(row => (
        <div key={row.label} className="infra-mini-card">
          <span className="infra-mini-label">{row.label}</span>
          <strong style={{ color: row.tone }}>{row.value}</strong>
        </div>
      ))}
    </div>
  )
}

function WorkloadMatrix({ services, topology, theme, workloads, demoRun }) {
  const ranked = Object.entries(asObject(services))
    .map(([service, snapshot]) => ({
      service,
      snapshot,
      score: snapshot.combined_score || 0,
    }))
    .sort((a, b) => b.score - a.score)

  const affected = new Set(topology?.root_cause?.affected_services || [])

  return (
    <div className="infra-workload-list">
      {ranked.map(({ service, snapshot }) => {
        const status = snapshot.status || 'normal'
        const runtime = workloads?.[service]?.runtime || {}
        const runtimeScore = runtimeHealthScore(runtime)
        const anomalyPressure = pressureScore(snapshot)
        const restartPressure = restartScore(runtime)
        const tone = statusTone(
          !runtime.exists || !runtime.running || !runtime.healthy ? 'critical' : status,
          Math.max(anomalyPressure, 1 - runtimeScore),
          theme
        )
        const workload = snapshot.latest_incident?.decision?.target || workloads?.[service]?.service || service
        const state = runtime.status || snapshot.latest_incident?.status || (status === 'normal' ? 'stable' : 'watch')
        const cpuPercent = workloads?.[service]?.cpu_percent ?? snapshot.cpu_mean ?? 0
        const memoryPercent = workloads?.[service]?.memory_percent ?? snapshot.mem_mean ?? 0
        const networkValue = (workloads?.[service]?.network_rx_mbps || 0) + (workloads?.[service]?.network_tx_mbps || 0)
        const demoActive = demoRun?.service === service && demoRun?.status === 'running'
        const signalRows = [
          ['runtime', runtimeScore, runtime.healthy ? 'healthy' : runtime.running ? 'degraded' : runtime.exists ? 'stopped' : 'missing'],
          ['pressure', anomalyPressure, `${Math.round((snapshot.combined_score || 0) * 100)} score`],
          ['restarts', restartPressure, `${runtime.restart_count || 0}`],
        ]

        return (
          <div key={service} className="infra-workload-row">
            <div className="infra-workload-main">
              <div className="infra-workload-title-wrap">
                <span className="infra-service-mark" style={{ background: tone }} />
                <div>
                  <div className="infra-workload-title" style={{ fontFamily: theme.displayFont }}>
                    {SERVICE_SHORT[service] || service}
                  </div>
                  <div className="infra-workload-sub">
                    {workload} · {state} {affected.has(service) ? '· in blast radius' : ''}{demoActive ? ' · demo target' : ''}
                  </div>
                </div>
              </div>
              <div className="infra-badge-row">
                <Badge label={formatStatusLabel(status)} tone={status === 'critical' ? 'critical' : status === 'warning' ? 'warning' : 'ok'} />
                <Badge label={runtime.healthy ? 'runtime healthy' : runtime.running ? 'runtime degraded' : runtime.exists ? 'runtime stopped' : 'runtime missing'} tone={runtime.healthy ? 'ok' : 'critical'} />
                {demoActive && <Badge label={`demo ${formatStatusLabel(demoRun.stage)}`} tone="warning" />}
                {(snapshot.feature_flags || []).slice(0, 2).map(flag => (
                  <Badge key={flag} label={flag.replace(/_/g, ' ')} />
                ))}
              </div>
              <div className="infra-workload-sub">
                CPU {formatPercent(cpuPercent || 0)} · memory {formatPercent(memoryPercent || 0)} · network {formatNumber(networkValue || 0, 2)} Mbps
              </div>
            </div>
            <div className="infra-signal-stack">
              {signalRows.map(([label, rawValue, displayValue]) => (
                <div key={label} className="infra-signal-row">
                  <span>{label}</span>
                  <div className="infra-signal-bar">
                    <span style={{ width: `${clamp((rawValue || 0) * 100, 8, 100)}%`, background: tone }} />
                  </div>
                  <span>{displayValue}</span>
                </div>
              ))}
            </div>
          </div>
        )
      })}
    </div>
  )
}

function ClusterReadyPanels({ theme, services, infrastructure }) {
  const cluster = infrastructure?.cluster
  if (cluster?.available) {
    const rows = [
      ['Nodes ready', `${cluster.nodes?.ready || 0}/${cluster.nodes?.total || 0}`],
      ['Running pods', `${cluster.pods?.running || 0}/${cluster.pods?.total || 0}`],
      ['Pending pods', `${cluster.pods?.pending || 0}`],
      ['Failed pods', `${cluster.pods?.failed || 0}`],
      ['Unavailable deployments', `${cluster.deployments?.unavailable || 0}/${cluster.deployments?.total || 0}`],
    ]
    return (
      <div className="infra-placeholder-grid">
        {rows.map(([title, copy]) => (
          <div key={title} className="infra-placeholder-card">
            <div className="infra-placeholder-top">
              <span className="infra-placeholder-dot" style={{ background: theme.accent }} />
              <span className="infra-placeholder-label">{title}</span>
            </div>
            <div className="infra-placeholder-copy">{copy}</div>
          </div>
        ))}
        <div className="infra-placeholder-card infra-placeholder-card-accent">
          <div className="infra-placeholder-top">
            <span className="infra-placeholder-label">Cluster summary</span>
            <Badge label={cluster.platform} tone="ok" />
          </div>
          <div className="infra-placeholder-copy">{cluster.summary}</div>
        </div>
      </div>
    )
  }

  const rows = [
    ['Node readiness', 'Awaiting Kubernetes node telemetry'],
    ['Control plane', 'Awaiting API server / scheduler / etcd health feed'],
    ['Replica posture', 'Awaiting desired vs ready deployment counts'],
    ['Capacity saturation', 'Awaiting CPU, memory, and ephemeral disk headroom'],
    ['Autoscaling', 'Awaiting HPA and eviction signals'],
  ]

  return (
    <div className="infra-placeholder-grid">
      {rows.map(([title, copy]) => (
        <div key={title} className="infra-placeholder-card">
          <div className="infra-placeholder-top">
            <span className="infra-placeholder-dot" style={{ background: theme.textDim }} />
            <span className="infra-placeholder-label">{title}</span>
          </div>
          <div className="infra-placeholder-copy">{copy}</div>
        </div>
      ))}
      <div className="infra-placeholder-card infra-placeholder-card-accent">
        <div className="infra-placeholder-top">
          <span className="infra-placeholder-label">Mode</span>
          <Badge label={`${infrastructure?.environment?.orchestrator || 'docker'} live`} tone="ok" />
        </div>
        <div className="infra-placeholder-copy">
          {Object.keys(asObject(services)).length} app workloads are monitored now. This panel is already laid out for node, pod, deployment, rollout, and HPA metrics once the Kubernetes feed is wired.
        </div>
      </div>
    </div>
  )
}

function StackHealth({ topology, services, theme, infrastructure }) {
  const trackedServices = Object.values(asObject(services))
  const logRich = trackedServices.filter(service => (service.recent_logs || []).length > 0).length
  const filledWindows = trackedServices.filter(service => service.window_filled).length
  const traceReady = ['frontend', 'productcatalogservice', 'currencyservice', 'paymentservice', 'emailservice', 'checkoutservice', 'recommendationservice', 'cartservice']
  const infraObs = infrastructure?.observability || {}

  const items = [
    {
      name: 'Prometheus',
      status: infraObs.prometheus?.available ? 'active' : topology ? 'configured' : 'waiting',
      detail: infraObs.prometheus?.available
        ? `${infraObs.prometheus.healthy_targets || 0}/${infraObs.prometheus.active_targets || 0} scrape targets healthy`
        : topology ? `${filledWindows}/${trackedServices.length || 1} windows filled` : 'Awaiting topology payload',
      meta: infraObs.prometheus?.error || 'scrape freshness derived from backend update cadence',
    },
    {
      name: 'Loki',
      status: infraObs.loki?.available ? 'active' : logRich > 0 ? 'configured' : 'waiting',
      detail: `${logRich} services with live recent log samples`,
      meta: infraObs.loki?.error || 'log ingest visibility is live through Loki cache',
    },
    {
      name: 'Promtail',
      status: infraObs.promtail?.available ? 'active' : topology ? 'configured' : 'waiting',
      detail: infraObs.promtail?.available ? 'promtail readiness endpoint reachable' : 'shipping pipeline provisioned',
      meta: infraObs.promtail?.error || 'dropped lines and lag are telemetry-ready placeholders',
    },
    {
      name: 'Jaeger',
      status: infraObs.jaeger?.available ? 'active' : topology ? 'configured' : 'waiting',
      detail: infraObs.jaeger?.available
        ? `${infraObs.jaeger.service_count || 0} traced services discovered`
        : `${traceReady.length} services trace-ready in compose`,
      meta: infraObs.jaeger?.error || 'latency-heavy service ranking awaits trace query aggregation',
    },
    {
      name: 'Grafana',
      status: infraObs.grafana?.available ? 'active' : topology ? 'configured' : 'waiting',
      detail: infraObs.grafana?.available ? 'health endpoint reachable' : 'datasources provisioned',
      meta: infraObs.grafana?.error || 'dashboard responsiveness awaits live datasource probing',
    },
    {
      name: 'Pipeline',
      status: trackedServices.some(service => service.model_state === 'warming_up') ? 'warming' : 'active',
      detail: trackedServices.some(service => service.model_state === 'warming_up')
        ? 'live telemetry is filling the model windows'
        : 'live inference and remediation active',
      meta: infraObs.otel_collector?.available ? 'ingest -> features -> detect -> remediate -> collector online' : 'ingest -> features -> detect -> remediate',
    },
  ]

  return (
    <div className="infra-stack-grid">
      {items.map(item => {
        const tone = item.status === 'active'
          ? severityTone(0.18, theme)
          : item.status === 'configured'
            ? theme.accent
            : item.status === 'demo'
              ? severityTone(0.55, theme)
              : theme.textDim
        return (
          <div key={item.name} className="infra-stack-card">
            <div className="infra-stack-top">
              <span className="infra-stack-name" style={{ fontFamily: theme.displayFont }}>{item.name}</span>
              <StatusPill label={item.status} tone={tone} />
            </div>
            <div className="infra-stack-detail">{item.detail}</div>
            <div className="infra-stack-meta">{item.meta}</div>
          </div>
        )
      })}
    </div>
  )
}

function PipelineReadiness({ services, topology, theme }) {
  const tracked = Object.values(asObject(services))
  const filled = tracked.filter(service => service.window_filled).length
  const flagged = tracked.filter(service => (service.feature_flags || []).length > 0).length
  const withMemory = tracked.filter(service => (service.similar_incidents || []).length > 0).length
  const stages = [
    { label: 'ingest', value: `${filled}/${tracked.length || 1}`, meta: 'windows ready' },
    { label: 'features', value: `${flagged}`, meta: 'services with active flags' },
    { label: 'decision', value: `${(topology?.active_incidents || []).length}`, meta: 'active incident workflows' },
    { label: 'memory', value: `${withMemory}`, meta: 'services with recall matches' },
  ]

  return (
    <div className="infra-readiness">
      {stages.map(stage => (
        <div key={stage.label} className="infra-readiness-card">
          <span className="infra-mini-label">{stage.label}</span>
          <strong style={{ fontFamily: theme.displayFont }}>{stage.value}</strong>
          <span className="infra-summary-meta">{stage.meta}</span>
        </div>
      ))}
    </div>
  )
}

function RecentChangeSummary({ topology, infrastructure, theme }) {
  const timeline = asArray(topology?.timeline).slice(0, 4)
  const latestOutcome = asArray(topology?.recent_incidents).find(item => item.status === 'resolved')
  const predictiveAlerts = asArray(topology?.predictive_alerts)
  const demoRun = topology?.demo_run

  const items = [
    {
      label: 'latest remediation',
      value: latestOutcome?.decision?.action ? formatStatusLabel(latestOutcome.decision.action) : 'No closure yet',
      meta: latestOutcome?.operator_summary || 'No resolved incident has been recorded in the current history window.',
    },
    {
      label: 'preventive alerts',
      value: `${predictiveAlerts.length}`,
      meta: predictiveAlerts.length
        ? `${predictiveAlerts[0]?.service || 'A service'} is currently under predictive watch.`
        : 'No predictive alert is active right now.',
    },
    {
      label: 'demo run',
      value: demoRun ? `${SERVICE_SHORT[demoRun.service] || demoRun.service} · ${formatStatusLabel(demoRun.stage)}` : 'No demo active',
      meta: demoRun?.summary_text || 'Use the demo button to inject a failure and watch the full recovery path populate this page.',
    },
    {
      label: 'latest timeline marker',
      value: timeline[0]?.title || 'Awaiting event flow',
      meta: timeline[0]?.message || 'The persisted timeline feed will summarize remediation and recovery here.',
    },
    {
      label: 'cluster posture',
      value: infrastructure?.cluster?.available ? 'Kubernetes live' : 'Telemetry ready',
      meta: infrastructure?.cluster?.summary || 'Node, pod, rollout, and capacity panels are waiting on the full cluster feed.',
    },
  ]

  return (
    <div className="infra-recent-grid">
      {items.map(item => (
        <div key={item.label} className="infra-note-item">
          <div className="infra-kicker">{item.label}</div>
          <div className="infra-copy" style={{ color: theme.text, fontSize: 13 }}>
            {item.value}
          </div>
          <div className="infra-summary-meta">{item.meta}</div>
        </div>
      ))}
    </div>
  )
}

function IncidentsRail({ topology, incidents, services, theme }) {
  const active = asArray(topology?.active_incidents)
  const historyFeed = [...active, ...asArray(incidents)]
    .sort((a, b) => new Date(b.detected_at || b.created_at || 0).getTime() - new Date(a.detected_at || a.created_at || 0).getTime())
    .slice(0, 8)

  if (!historyFeed.length) {
    return (
      <div className="infra-empty">
        <div className="infra-headline" style={{ fontFamily: theme.displayFont }}>No incident pressure</div>
        <div className="infra-copy">The remediation rail will populate as soon as the backend records an incident lifecycle.</div>
      </div>
    )
  }

  return (
    <div className="infra-timeline">
      {historyFeed.map((incident, index) => {
        const service = incident.root_cause_service || incident.service || 'unknown'
        const snapshot = services[service] || {}
        const tone = statusTone(snapshot.status || incident.status, snapshot.combined_score || 0.7, theme)
        const mode = incident.containment?.containment_mode || 'observe'
        const manual = incident.containment?.manual_required
        return (
          <div key={`${incident.id || service}-${index}`} className="infra-timeline-item">
            <div className="infra-timeline-axis">
              <span className="infra-timeline-node" style={{ background: tone }} />
              {index < historyFeed.length - 1 && <span className="infra-timeline-line" />}
            </div>
            <div className="infra-timeline-body">
              <div className="infra-timeline-top">
                <span className="infra-workload-title" style={{ fontFamily: theme.displayFont }}>{SERVICE_SHORT[service] || service}</span>
                <span className="infra-summary-meta">{formatRelative(incident.detected_at || incident.created_at)}</span>
              </div>
              <div className="infra-badge-row">
                <Badge label={formatStatusLabel(incident.failure_type || 'generic_anomaly')} tone={incident.status === 'resolved' ? 'ok' : 'critical'} />
                <Badge label={formatStatusLabel(mode)} tone={mode === 'escalate' ? 'critical' : mode === 'isolate' ? 'warning' : 'muted'} />
                {manual && <Badge label="manual required" tone="warning" />}
              </div>
              <div className="infra-copy">
                {incident.operator_summary || incident.evaluation?.message || incident.decision?.rationale || 'Awaiting evaluation narrative.'}
              </div>
              <div className="infra-summary-meta">
                action: {incident.decision?.action || incident.proposal?.proposed_action || 'pending'} · retry {incident.retry_count || 0}
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

function MemoryRecall({ services, theme, infrastructure }) {
  const memoryRecent = asArray(infrastructure?.memory?.recent)
  const matches = memoryRecent.length
    ? memoryRecent.map(match => ({ service: match.service, ...match }))
    : topMemoryMatches(services)

  if (!matches.length) {
    return (
      <div className="infra-placeholder-card">
        <div className="infra-placeholder-top">
          <span className="infra-placeholder-label">Incident memory</span>
          <Badge label="warming up" />
        </div>
        <div className="infra-placeholder-copy">
          Similar-failure recall will appear here once repeat incidents are stored in the remediation memory layer.
        </div>
      </div>
    )
  }

  return (
    <div className="infra-memory-list">
      {matches.map((match, index) => (
        <div key={`${match.incident_id || index}-${match.service}`} className="infra-memory-item">
          <div className="infra-memory-top">
            <span className="infra-workload-title" style={{ fontFamily: theme.displayFont }}>
              {SERVICE_SHORT[match.service] || match.service}
            </span>
            <span className="infra-summary-meta">{Math.round((match.similarity_score || 0) * 100)}% match</span>
          </div>
          <div className="infra-copy">
            {match.evidence_summary || match.notes || 'No evidence summary available yet.'}
          </div>
          <div className="infra-summary-meta">
            action {match.selected_action || 'n/a'} · outcome {match.outcome || 'unknown'}
          </div>
        </div>
      ))}
    </div>
  )
}

function OperatorNotes({ topology, services, theme, infrastructure }) {
  const recent = latestServiceIncidents(services).slice(0, 3)
  const clusterLabel = infrastructure?.environment?.orchestrator || topology?.environment || 'docker compose'

  return (
    <div className="infra-notes">
      <div className="infra-placeholder-card infra-placeholder-card-accent">
        <div className="infra-placeholder-top">
          <span className="infra-placeholder-label">Cluster mode</span>
          <Badge label={clusterLabel} tone="ok" />
        </div>
        <div className="infra-placeholder-copy">
          Kubernetes management cards are already designed into this page. When kube telemetry lands, this rail can surface node readiness, pending pods, rollout state, HPA signals, and namespace pressure without another redesign.
        </div>
      </div>
      {recent.map(item => (
        <div key={item.id} className="infra-note-item">
          <div className="infra-note-title" style={{ fontFamily: theme.displayFont }}>
            {SERVICE_SHORT[item.service] || item.service}
          </div>
          <div className="infra-copy">
            {item.operator_summary || item.evaluation?.message || 'Recent incident archived without operator summary.'}
          </div>
        </div>
      ))}
    </div>
  )
}

export default function InfraPage({ topology, history, incidents, connected, infrastructure }) {
  const { theme, dark } = useTheme()
  const safeTopology = asObject(topology)
  const safeInfrastructure = asObject(infrastructure)
  const safeHistory = asArray(history)
  const safeIncidents = asArray(incidents)
  const services = asObject(safeTopology.services)
  const workloads = arrayToMap(safeInfrastructure.workloads)
  const serviceEntries = Object.entries(services)
  const healthScore = Number.isFinite(safeTopology.health_score) ? safeTopology.health_score : null
  const alerts = asArray(safeTopology.alerts)
  const activeIncidents = asArray(safeTopology.active_incidents)
  const warningCount = serviceEntries.filter(([, svc]) => svc.status === 'warning').length
  const criticalCount = serviceEntries.filter(([, svc]) => svc.status === 'critical').length
  const latestOutcome = useMemo(() => {
    const feed = [...asArray(safeTopology.recent_incidents), ...safeIncidents]
    const resolved = feed.find(item => item.status === 'resolved')
    return resolved || feed[0] || null
  }, [safeTopology.recent_incidents, safeIncidents])

  const topCards = [
    {
      label: 'global health',
      value: healthScore == null ? '—' : `${healthScore}`,
      meta: serviceEntries.length ? `${serviceEntries.length} monitored services` : 'Awaiting topology feed',
      tone: severityTone(clamp(1 - ((healthScore ?? 100) / 100), 0, 1), theme),
    },
    {
      label: 'active incidents',
      value: `${activeIncidents.length}`,
      meta: activeIncidents.length ? `${criticalCount} critical services in focus` : 'No active remediation workflow',
      tone: activeIncidents.length ? severityTone(0.86, theme) : severityTone(0.12, theme),
    },
    {
      label: 'alerts',
      value: `${alerts.length}`,
      meta: `${criticalCount} critical · ${warningCount} warning`,
      tone: alerts.length ? severityTone(0.62, theme) : theme.textMuted,
    },
    {
      label: 'automation',
      value: connected ? 'Online' : 'Offline',
      meta: latestOutcome ? `Last action ${formatRelative(latestOutcome.detected_at || latestOutcome.created_at)}` : 'No recorded action yet',
      tone: connected ? theme.accent : severityTone(0.92, theme),
    },
    {
      label: 'prometheus freshness',
      value: safeInfrastructure.timestamp ? formatRelative(safeInfrastructure.timestamp) : safeTopology.timestamp ? formatRelative(safeTopology.timestamp) : '—',
      meta: safeInfrastructure?.observability?.prometheus?.available
        ? `${safeInfrastructure.observability.prometheus.healthy_targets || 0}/${safeInfrastructure.observability.prometheus.active_targets || 0} targets healthy`
        : safeTopology.timestamp ? `Updated ${formatTime(safeTopology.timestamp)}` : 'Awaiting backend poll',
      tone: safeInfrastructure?.observability?.prometheus?.available || safeTopology.timestamp ? severityTone(0.2, theme) : theme.textDim,
    },
    {
      label: 'trace activity',
      value: safeTopology.services && Object.values(safeTopology.services).some(service => service.model_state === 'warming_up') ? 'Warming' : 'Live',
      meta: safeTopology.services && Object.values(safeTopology.services).some(service => service.model_state === 'warming_up')
        ? 'ML windows are filling from live telemetry'
        : 'Inference + remediation pipeline active',
      tone: safeTopology.services && Object.values(safeTopology.services).some(service => service.model_state === 'warming_up') ? severityTone(0.55, theme) : theme.accent,
    },
  ]

  return (
    <div
      className={`infra-page ${dark ? 'infra-dark' : 'infra-light'}`}
      style={{
        '--infra-bg': theme.bg,
        '--infra-card': theme.card,
        '--infra-line': theme.borderLight,
        '--infra-border': theme.border,
        '--infra-text': theme.text,
        '--infra-muted': theme.textMuted,
        '--infra-dim': theme.textDim,
        '--infra-accent': theme.accent,
        '--infra-soft': dark ? 'rgba(255,255,255,0.035)' : 'rgba(26,26,26,0.03)',
        '--infra-soft-strong': dark ? 'rgba(255,255,255,0.06)' : 'rgba(26,26,26,0.05)',
        '--infra-page-padding': '28px',
        '--infra-section-padding': '20px',
        '--infra-header-gap': '18px',
        '--infra-subsection-gap': '16px',
        '--infra-subsection-gap-tight': '12px',
        '--infra-card-gap': '12px',
        '--infra-rail-gap': '22px',
      }}
    >
      <div className="infra-header">
        <div>
          <span className="infra-page-kicker">Infrastructure</span>
          <h1 className="infra-page-title" style={{ fontFamily: theme.displayFont }}>
            Cluster health, observability, and remediation
          </h1>
        </div>
        <div className="infra-header-meta">
          <StatusPill label={connected ? 'backend connected' : 'backend offline'} tone={connected ? theme.accent : severityTone(0.92, theme)} />
          <Badge label={Object.values(services).some(service => service.model_state === 'warming_up') ? 'model warmup' : 'live inference'} tone={Object.values(services).some(service => service.model_state === 'warming_up') ? 'warning' : 'ok'} />
          <Badge label={safeInfrastructure?.cluster?.available ? 'kubernetes live' : 'kubernetes ready'} />
        </div>
      </div>

      <div className="infra-summary-rail">
        {topCards.map(card => (
          <SummaryCard key={card.label} {...card} theme={theme} />
        ))}
      </div>

      <div className="infra-main-grid">
        <div className="infra-main-left">
          <Section title="Cluster & Workload Health" eyebrow="Live now + ready states" theme={theme}>
            <div className="infra-subsection">
              <div className="infra-kicker">Runtime service saturation</div>
              <WorkloadMatrix services={services} topology={safeTopology} theme={theme} workloads={workloads} demoRun={safeTopology.demo_run} />
            </div>
            <div className="infra-subsection">
              <div className="infra-kicker">Kubernetes management panels</div>
              <ClusterReadyPanels theme={theme} services={services} infrastructure={safeInfrastructure} />
            </div>
          </Section>

          <Section title="System Overview" eyebrow="Overview" theme={theme}>
            <RootCauseSpotlight topology={safeTopology} services={services} theme={theme} />
            <div className="infra-dual">
              <div className="infra-subsection">
                <div className="infra-kicker">Environment identity</div>
                <div className="infra-definition-list">
                  <div><span>environment</span><strong>{safeInfrastructure?.environment?.cluster_name || 'online-boutique'}</strong></div>
                  <div><span>mode</span><strong>{safeInfrastructure?.environment?.orchestrator || 'docker'}</strong></div>
                  <div><span>namespace</span><strong>{safeInfrastructure?.environment?.namespace || 'default / local'}</strong></div>
                  <div><span>collector</span><strong>{safeInfrastructure?.environment?.collector_ready ? 'collector configured' : 'collector pending'}</strong></div>
                </div>
              </div>
              <div className="infra-subsection">
                <div className="infra-kicker">Fleet summary</div>
                <FleetSummary services={services} theme={theme} infrastructure={safeInfrastructure} />
              </div>
            </div>
            <div className="infra-subsection">
              <div className="infra-kicker">Recent change summary</div>
              <RecentChangeSummary topology={safeTopology} infrastructure={safeInfrastructure} theme={theme} />
            </div>
            <div className="infra-subsection">
              <div className="infra-kicker">Failure momentum and anomaly ribbon</div>
              <div className="infra-ribbon-meta">
                <span>{formatSigned(safeTopology?.failure_momentum || 0, 1, ' points/min')}</span>
                <span>{safeHistory.length || 0} stored snapshots</span>
              </div>
              <TrendRibbon history={safeHistory} services={services} theme={theme} />
            </div>
          </Section>

          <Section title="Service Telemetry Lens" eyebrow="High-signal comparisons" theme={theme}>
            <div className="infra-telemetry-grid">
              {Object.entries(services)
                .sort((a, b) => (b[1].combined_score || 0) - (a[1].combined_score || 0))
                .slice(0, 6)
                .map(([service, snapshot]) => {
                  const runtime = workloads[service] || {}
                  const tone = statusTone(snapshot.status, snapshot.combined_score || 0, theme)
                  const cpuValue = runtime.cpu_percent ?? snapshot.cpu_mean ?? 0
                  const memoryValue = runtime.memory_percent ?? snapshot.mem_mean ?? 0
                  const networkValue = (runtime.network_rx_mbps || 0) + (runtime.network_tx_mbps || 0)
                  return (
                    <div key={service} className="infra-telemetry-card">
                      <div className="infra-telemetry-top">
                        <span className="infra-workload-title" style={{ fontFamily: theme.displayFont }}>
                          {SERVICE_SHORT[service] || service}
                        </span>
                        <span className="infra-summary-meta">{Math.round((snapshot.combined_score || 0) * 100)}</span>
                      </div>
                      <div className="infra-telemetry-row">
                        <span>CPU usage</span>
                        <strong style={{ color: tone }}>{formatPercent(cpuValue)}</strong>
                      </div>
                      <div className="infra-telemetry-row">
                        <span>Memory usage</span>
                        <strong>{formatPercent(memoryValue)}</strong>
                      </div>
                      <div className="infra-telemetry-row">
                        <span>Error rate</span>
                        <strong>{formatPercent((snapshot.error_rate_mean || 0) * 100, 1)}</strong>
                      </div>
                      <div className="infra-telemetry-row">
                        <span>{networkValue > 0 ? 'Network Mbps' : 'Logs per second'}</span>
                        <strong>{networkValue > 0 ? formatNumber(networkValue, 2) : formatNumber(snapshot.log_volume_per_sec || 0, 2)}</strong>
                      </div>
                    </div>
                  )
                })}
            </div>
          </Section>
        </div>

        <div className="infra-main-right">
          <Section title="Incidents & Remediation" eyebrow="Retry · isolate · reroute · escalate" theme={theme} tight>
            <IncidentsRail topology={safeTopology} incidents={safeIncidents} services={services} theme={theme} />
          </Section>

          <Section title="Memory Recall" eyebrow="Previous failures" theme={theme} tight>
            <MemoryRecall services={services} theme={theme} infrastructure={safeInfrastructure} />
          </Section>

          <Section title="Operator Notes" eyebrow="Ready states and archived context" theme={theme} tight>
            <OperatorNotes topology={safeTopology} services={services} theme={theme} infrastructure={safeInfrastructure} />
          </Section>
        </div>
      </div>

      <div className="infra-bottom-band">
        <Section title="Observability Stack Health" eyebrow="Metrics · logs · traces" theme={theme}>
          <div className="infra-bottom-grid">
            <div className="infra-subsection">
              <div className="infra-kicker">Stack posture</div>
              <StackHealth topology={safeTopology} services={services} theme={theme} infrastructure={safeInfrastructure} />
            </div>
            <div className="infra-subsection">
              <div className="infra-kicker">Pipeline readiness</div>
              <PipelineReadiness services={services} topology={safeTopology} theme={theme} />
            </div>
          </div>
        </Section>
      </div>

      <style>{`
        .infra-page {
          flex: 1;
          min-height: 0;
          overflow-y: auto;
          padding: var(--infra-page-padding) var(--infra-page-padding) 36px;
          background:
            radial-gradient(circle at top left, color-mix(in srgb, var(--infra-accent) 8%, transparent), transparent 28%),
            linear-gradient(to bottom, transparent, transparent),
            var(--infra-bg);
          color: var(--infra-text);
        }
        .infra-page * {
          box-sizing: border-box;
        }
        .infra-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 20px;
          padding-bottom: 20px;
          margin-bottom: var(--infra-header-gap);
          border-bottom: 1px solid var(--infra-line);
        }
        .infra-page-kicker,
        .infra-section-eyebrow,
        .infra-summary-label,
        .infra-mini-label,
        .infra-kicker,
        .infra-placeholder-label {
          text-transform: uppercase;
          letter-spacing: 0.18em;
          font-size: 10px;
          color: var(--infra-muted);
        }
        .infra-page-title {
          margin-top: 8px;
          max-width: 720px;
          font-size: clamp(28px, 3vw, 44px);
          line-height: 0.98;
          font-weight: 400;
          letter-spacing: -0.03em;
        }
        .infra-header-meta {
          display: flex;
          flex-wrap: wrap;
          justify-content: flex-end;
          gap: 10px;
        }
        .infra-summary-rail {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
          gap: var(--infra-card-gap);
          margin-bottom: calc(var(--infra-card-gap) * 2);
        }
        .infra-summary-card,
        .infra-section,
        .infra-mini-card,
        .infra-stack-card,
        .infra-telemetry-card,
        .infra-placeholder-card,
        .infra-memory-item,
        .infra-note-item,
        .infra-readiness-card {
          background: linear-gradient(180deg, var(--infra-soft) 0%, transparent 100%);
          border: 1px solid var(--infra-line);
          border-radius: 18px;
          backdrop-filter: blur(6px);
        }
        .infra-summary-card {
          padding: 16px;
          display: flex;
          flex-direction: column;
          gap: 8px;
          min-width: 0;
        }
        .infra-summary-value {
          font-size: 30px;
          line-height: 1;
          margin: 8px 0 0;
          font-weight: 500;
          letter-spacing: -0.04em;
          overflow-wrap: anywhere;
        }
        .infra-summary-meta,
        .infra-copy,
        .infra-stack-meta,
        .infra-stack-detail,
        .infra-workload-sub,
        .infra-ribbon-meta,
        .infra-placeholder-copy,
        .infra-definition-list span,
        .infra-definition-list strong,
        .infra-telemetry-row,
        .infra-badge,
        .infra-status-pill,
        .infra-chart-legend span {
          font-family: ${theme.font};
        }
        .infra-summary-meta,
        .infra-copy,
        .infra-stack-meta,
        .infra-workload-sub,
        .infra-placeholder-copy {
          font-size: 11px;
          line-height: 1.5;
          color: var(--infra-muted);
        }
        .infra-main-grid {
          display: grid;
          grid-template-columns: minmax(0, 1.6fr) minmax(300px, 0.78fr);
          gap: var(--infra-rail-gap);
          align-items: start;
          margin-bottom: var(--infra-rail-gap);
        }
        .infra-main-left {
          display: flex;
          flex-direction: column;
          gap: var(--infra-rail-gap);
          min-width: 0;
        }
        .infra-main-right {
          display: flex;
          flex-direction: column;
          gap: var(--infra-rail-gap);
          min-width: 0;
        }
        .infra-bottom-band {
          display: flex;
          flex-direction: column;
          gap: var(--infra-card-gap);
        }
        .infra-bottom-grid {
          display: grid;
          grid-template-columns: minmax(0, 1.12fr) minmax(300px, 0.88fr);
          gap: var(--infra-rail-gap);
          align-items: start;
        }
        .infra-section {
          padding: var(--infra-section-padding);
          min-width: 0;
        }
        .infra-section-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 14px;
          margin-bottom: 18px;
        }
        .infra-section-title {
          font-size: 26px;
          font-weight: 400;
          letter-spacing: -0.03em;
          line-height: 1;
          margin: 0;
        }
        .infra-section-body {
          display: flex;
          flex-direction: column;
          gap: max(var(--section-gap), 14px);
          min-width: 0;
        }
        .infra-spotlight {
          display: flex;
          flex-direction: column;
          gap: 12px;
          padding: 20px;
          border-radius: 18px;
          background: var(--infra-soft);
          border: 1px solid var(--infra-line);
        }
        .infra-headline {
          font-size: 28px;
          line-height: 1;
          letter-spacing: -0.04em;
          font-weight: 400;
        }
        .infra-spotlight-meta,
        .infra-badge-row,
        .infra-placeholder-top,
        .infra-memory-top,
        .infra-timeline-top,
        .infra-stack-top,
        .infra-chart-legend,
        .infra-ribbon-meta {
          display: flex;
          flex-wrap: wrap;
          gap: 8px 10px;
          align-items: center;
        }
        .infra-dual {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
          gap: var(--infra-card-gap);
        }
        .infra-subsection {
          display: flex;
          flex-direction: column;
          gap: var(--infra-card-gap);
          min-width: 0;
        }
        .infra-definition-list {
          display: grid;
          gap: 8px;
        }
        .infra-definition-list div {
          display: flex;
          justify-content: space-between;
          gap: 12px;
          padding-bottom: 8px;
          border-bottom: 1px solid var(--infra-line);
        }
        .infra-definition-list strong {
          color: var(--infra-text);
          font-weight: 500;
          font-size: 11px;
          text-transform: uppercase;
          letter-spacing: 0.06em;
        }
        .infra-metric-grid,
        .infra-readiness,
        .infra-stack-grid,
        .infra-placeholder-grid,
        .infra-telemetry-grid {
          display: grid;
          gap: 12px;
        }
        .infra-metric-grid {
          grid-template-columns: repeat(auto-fit, minmax(128px, 1fr));
        }
        .infra-mini-card,
        .infra-readiness-card {
          padding: 14px 12px;
          display: flex;
          flex-direction: column;
          gap: 8px;
          align-items: flex-start;
          justify-content: flex-start;
          min-width: 0;
        }
        .infra-mini-card strong,
        .infra-readiness-card strong {
          font-size: 24px;
          line-height: 1;
          font-weight: 500;
          overflow-wrap: anywhere;
        }
        .infra-chart-shell {
          padding: 14px 14px 10px;
          background: var(--infra-soft);
          border: 1px solid var(--infra-line);
          border-radius: 18px;
        }
        .infra-trend-chart {
          width: 100%;
          height: 128px;
          color: var(--infra-text);
        }
        .infra-chart-legend {
          margin-top: 8px;
          color: var(--infra-muted);
          font-size: 10px;
          letter-spacing: 0.08em;
          text-transform: uppercase;
        }
        .infra-chart-legend i {
          display: inline-block;
          width: 14px;
          height: 2px;
          vertical-align: middle;
          margin-right: 6px;
        }
        .infra-workload-list,
        .infra-timeline,
        .infra-memory-list,
        .infra-notes {
          display: flex;
          flex-direction: column;
          gap: var(--infra-card-gap);
        }
        .infra-workload-row {
          display: grid;
          grid-template-columns: minmax(0, 1.15fr) minmax(220px, 0.85fr);
          gap: 14px;
          padding: 15px 16px;
          border-radius: 18px;
          background: var(--infra-soft);
          border: 1px solid var(--infra-line);
          min-width: 0;
        }
        .infra-workload-main,
        .infra-signal-stack {
          display: flex;
          flex-direction: column;
          gap: 10px;
          min-width: 0;
        }
        .infra-workload-title-wrap {
          display: flex;
          gap: 12px;
          align-items: flex-start;
          min-width: 0;
        }
        .infra-workload-title-wrap > div {
          min-width: 0;
        }
        .infra-service-mark,
        .infra-status-dot,
        .infra-placeholder-dot,
        .infra-timeline-node {
          width: 10px;
          height: 10px;
          border-radius: 999px;
          flex: 0 0 auto;
        }
        .infra-workload-title,
        .infra-stack-name,
        .infra-note-title {
          font-size: 20px;
          line-height: 1;
          font-weight: 400;
          letter-spacing: -0.03em;
          overflow-wrap: anywhere;
        }
        .infra-badge-row {
          align-items: flex-start;
          min-width: 0;
        }
        .infra-badge,
        .infra-status-pill {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          padding: 5px 9px;
          border-radius: 999px;
          border: 1px solid var(--infra-line);
          font-size: 9px;
          letter-spacing: 0.1em;
          text-transform: uppercase;
          color: var(--infra-muted);
          background: transparent;
          max-width: 100%;
          overflow-wrap: anywhere;
          white-space: normal;
        }
        .infra-badge-ok {
          color: #2f8e54;
          border-color: color-mix(in srgb, #2f8e54 50%, var(--infra-line));
        }
        .infra-badge-warning {
          color: #c27a12;
          border-color: color-mix(in srgb, #c27a12 50%, var(--infra-line));
        }
        .infra-badge-critical {
          color: #cb4741;
          border-color: color-mix(in srgb, #cb4741 50%, var(--infra-line));
        }
        .infra-signal-row,
        .infra-telemetry-row {
          display: grid;
          grid-template-columns: minmax(84px, 0.9fr) minmax(0, 1fr) minmax(74px, auto);
          gap: 10px;
          align-items: center;
          font-size: 10px;
          letter-spacing: 0.1em;
          text-transform: uppercase;
          color: var(--infra-muted);
          min-width: 0;
        }
        .infra-signal-row > span,
        .infra-telemetry-row > span,
        .infra-signal-row strong,
        .infra-telemetry-row strong {
          min-width: 0;
          overflow-wrap: anywhere;
        }
        .infra-signal-bar {
          height: 7px;
          border-radius: 999px;
          background: var(--infra-soft-strong);
          overflow: hidden;
        }
        .infra-signal-bar span {
          display: block;
          height: 100%;
          border-radius: inherit;
        }
        .infra-placeholder-grid {
          grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        }
        .infra-placeholder-card {
          padding: 16px;
          min-height: 0;
          display: flex;
          flex-direction: column;
          justify-content: flex-start;
          gap: 10px;
          min-width: 0;
        }
        .infra-placeholder-card-accent {
          background:
            linear-gradient(180deg, color-mix(in srgb, var(--infra-accent) 8%, transparent), transparent 80%),
            var(--infra-soft);
        }
        .infra-stack-grid {
          grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        }
        .infra-stack-card,
        .infra-telemetry-card,
        .infra-memory-item,
        .infra-note-item {
          padding: 15px 16px;
          min-width: 0;
        }
        .infra-telemetry-grid {
          grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        }
        .infra-telemetry-card {
          display: flex;
          flex-direction: column;
          gap: 10px;
          justify-content: flex-start;
          min-height: 0;
        }
        .infra-telemetry-top {
          display: flex;
          justify-content: space-between;
          gap: 12px;
          align-items: flex-start;
          min-width: 0;
        }
        .infra-telemetry-top > span:first-child {
          min-width: 0;
        }
        .infra-timeline-item {
          display: grid;
          grid-template-columns: 20px minmax(0, 1fr);
          gap: 12px;
        }
        .infra-timeline-axis {
          display: flex;
          flex-direction: column;
          align-items: center;
        }
        .infra-timeline-line {
          width: 1px;
          flex: 1;
          background: var(--infra-line);
          margin-top: 8px;
        }
        .infra-timeline-body {
          padding: 0 0 14px;
          border-bottom: 1px solid var(--infra-line);
        }
        .infra-empty {
          padding: 18px;
          background: var(--infra-soft);
          border: 1px solid var(--infra-line);
          border-radius: 18px;
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
        .infra-recent-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
          gap: var(--infra-card-gap);
        }
        .infra-copy,
        .infra-summary-meta,
        .infra-placeholder-copy,
        .infra-workload-sub,
        .infra-summary-label,
        .infra-mini-label,
        .infra-kicker,
        .infra-placeholder-label {
          overflow-wrap: anywhere;
        }
        @media (max-width: 1360px) {
          .infra-main-grid,
          .infra-bottom-grid {
            grid-template-columns: minmax(0, 1fr);
          }
        }
        @media (max-width: 960px) {
          .infra-page {
            padding: 20px 16px 28px;
          }
          .infra-header,
          .infra-dual,
          .infra-workload-row,
          .infra-placeholder-grid,
          .infra-stack-grid,
          .infra-telemetry-grid,
          .infra-metric-grid,
          .infra-summary-rail {
            grid-template-columns: minmax(0, 1fr);
          }
          .infra-header {
            flex-direction: column;
          }
          .infra-workload-row {
            display: flex;
            flex-direction: column;
          }
        }
      `}</style>
    </div>
  )
}
