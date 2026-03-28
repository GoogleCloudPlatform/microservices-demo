import { getPlanetPos, statusColor, SERVICE_SHORT, theme } from '../styles/theme'

const PLANET_RADIUS = {
  normal: 22,
  warning: 26,
  critical: 28,
}

export default function PlanetNode({ service, data, isSelected, isRootCause, onClick }) {
  const pos = getPlanetPos(service)
  const status = data?.status || 'normal'
  const score = data?.combined_score || 0
  const r = PLANET_RADIUS[status]
  const fill = statusColor(status, 'fill')
  const stroke = statusColor(status, 'stroke')
  const shortName = SERVICE_SHORT[service] || service
  const isAnomaly = status !== 'normal'
  const scoreLabel = Math.round(score * 100)

  // CPU/MEM mini arc (shows CPU as partial arc around planet)
  const cpu = Math.min(data?.cpu_mean || 0, 100)
  const mem = Math.min(data?.mem_mean || 0, 100)

  // SVG arc path for CPU usage indicator
  const arcPath = (pct, outerR, innerR = outerR - 4, startAngle = -90) => {
    const sweep = (pct / 100) * 360
    const endAngle = startAngle + sweep
    const toRad = a => a * Math.PI / 180
    const x1 = Math.cos(toRad(startAngle)) * outerR
    const y1 = Math.sin(toRad(startAngle)) * outerR
    const x2 = Math.cos(toRad(endAngle)) * outerR
    const y2 = Math.sin(toRad(endAngle)) * outerR
    const large = sweep > 180 ? 1 : 0
    return `M ${x1} ${y1} A ${outerR} ${outerR} 0 ${large} 1 ${x2} ${y2}`
  }

  return (
    <g
      transform={`translate(${pos.x}, ${pos.y})`}
      onClick={() => onClick(service)}
      style={{ cursor: 'pointer' }}
      className={isAnomaly ? 'planet-anomaly' : ''}
    >
      {/* Selection ring */}
      {isSelected && (
        <circle r={r + 8} fill="none" stroke="#555" strokeWidth="1.5" strokeDasharray="4 3" />
      )}

      {/* Root cause ring */}
      {isRootCause && (
        <circle r={r + 12} fill="none" stroke="#c45c0a" strokeWidth="2"
          style={{ animation: 'spin 4s linear infinite' }}
        />
      )}

      {/* Glow for anomalous */}
      {isAnomaly && (
        <circle r={r + 6} fill={status === 'critical' ? 'rgba(255,0,0,0.12)' : 'rgba(196,92,10,0.12)'}
          style={{ animation: 'pulse 2s ease-in-out infinite' }}
        />
      )}

      {/* Planet body */}
      <circle
        r={r}
        fill={fill}
        stroke={stroke}
        strokeWidth={isSelected || isRootCause ? 2.5 : 1.5}
      />

      {/* CPU arc indicator (orange arc outside planet) */}
      {cpu > 0 && (
        <path
          d={arcPath(cpu, r + 5)}
          fill="none"
          stroke="#c45c0a"
          strokeWidth="3"
          strokeLinecap="round"
          opacity="0.8"
        />
      )}

      {/* Memory arc (inner, blue-ish) */}
      {mem > 0 && (
        <path
          d={arcPath(mem, r + 5, r + 1, 90)}
          fill="none"
          stroke="#5588cc"
          strokeWidth="2"
          strokeLinecap="round"
          opacity="0.6"
        />
      )}

      {/* Anomaly lightning bolt */}
      {isAnomaly && (
        <text x={-4} y={4} fontSize="11" fill={status === 'critical' ? '#cc0000' : '#c45c0a'}
          style={{ userSelect: 'none', pointerEvents: 'none' }}
        >⚡</text>
      )}

      {/* Score label (center of planet for normal, top for anomalous) */}
      {!isAnomaly && (
        <text textAnchor="middle" dy="4px" fontSize="9" fontFamily="'IBM Plex Mono', monospace"
          fill="#555" style={{ userSelect: 'none', pointerEvents: 'none' }}
        >{scoreLabel}</text>
      )}

      {/* Anomaly score above planet */}
      {isAnomaly && (
        <text x={0} y={-r - 10} textAnchor="middle" fontSize="10"
          fontFamily="'IBM Plex Mono', monospace" fill="#c45c0a" fontWeight="bold"
          style={{ userSelect: 'none', pointerEvents: 'none' }}
        >
          {`${scoreLabel}`}
        </text>
      )}

      {/* Service name below */}
      <text textAnchor="middle" dy={r + 16} fontSize="9"
        fontFamily="'IBM Plex Mono', monospace" fill="#333"
        style={{ userSelect: 'none', pointerEvents: 'none' }}
      >{shortName}</text>
    </g>
  )
}
