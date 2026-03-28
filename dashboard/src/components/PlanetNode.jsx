import { anomalyGlowColor, anomalyScoreColor, getPlanetPos, SERVICE_SHORT } from '../styles/theme'
import { useTheme } from '../ThemeContext'

// Dynamic planet radius: 16–26px based on stress
function getRadius(service, data) {
  const base = 16
  const score = data?.combined_score || 0
  const cpu   = (data?.cpu_mean || 0) / 100
  const mem   = (data?.mem_mean || 0) / 100
  const stress = Math.max(score, cpu * 0.4, mem * 0.3)
  const radius = Math.round(base + stress * 10)  // 16 → 26
  return service === 'redis-cart' ? Math.max(12, radius - 3) : radius
}

// Animated arc ring using stroke-dasharray (starts at 12 o'clock via rotate(-90deg))
function RingArc({ radius, pct, color, strokeW = 2.5, anomaly = false }) {
  const safePct = Number.isFinite(pct) ? Math.max(0, Math.min(pct, 100)) : 0
  const circ = 2 * Math.PI * radius
  const dash = safePct / 100 * circ
  const gap  = circ - dash
  return (
    <g style={{ transform: 'rotate(-90deg)' }}>
      {/* Track */}
      <circle r={radius} fill="none" stroke={color} strokeWidth={strokeW}
        opacity={anomaly ? 0.22 : 0.13} />
      {/* Fill */}
      {dash > 0.5 && (
        <circle r={radius} fill="none" stroke={color} strokeWidth={strokeW}
          strokeDasharray={`${dash.toFixed(2)} ${gap.toFixed(2)}`}
          strokeLinecap="round"
          opacity={anomaly ? 1.0 : 0.85}
          style={{ transition: 'stroke-dasharray 0.5s ease' }}
        />
      )}
    </g>
  )
}

function contrastTextColor(fill, theme) {
  const hex = (fill || '').replace('#', '')
  if (hex.length !== 6) return theme.text
  const r = Number.parseInt(hex.slice(0, 2), 16)
  const g = Number.parseInt(hex.slice(2, 4), 16)
  const b = Number.parseInt(hex.slice(4, 6), 16)
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
  return luminance < 0.58 ? '#f8fafc' : '#111827'
}

export default function PlanetNode({ service, data, isSelected, isRootCause, onClick, orbitRing = 2 }) {
  const { theme } = useTheme()
  const pos      = getPlanetPos(service)
  const status   = data?.status || 'normal'
  const score    = data?.combined_score || 0
  const r        = getRadius(service, data)
  const fill     = anomalyScoreColor(score, 'fill', theme)
  const stroke   = anomalyScoreColor(score, 'stroke', theme)
  const scoreText = contrastTextColor(fill, theme)
  const scoreOutline = scoreText === '#f8fafc' ? 'rgba(15, 23, 42, 0.55)' : 'rgba(255, 255, 255, 0.55)'
  const shortName = SERVICE_SHORT[service] || service
  const isAnomaly = status !== 'normal'

  // Metric values
  const cpu      = Math.min(data?.cpu_mean   || 0, 100)
  const mem      = Math.min(data?.mem_mean   || 0, 100)
  const errRate  = Math.min(data?.features?.error_rate_pct ?? data?.error_rate ?? 0, 100)
  const anomScore = Math.min((score || 0) * 100, 100)
  const scoreLabel = Math.round(score * 100)

  // Ring offsets — scale tighter for inner orbit (ring 1 = redis)
  const rs = orbitRing === 1 ? 0.6 : 1.0
  const R1 = r + Math.round(7  * rs)   // CPU
  const R2 = r + Math.round(13 * rs)   // MEM
  const R3 = r + Math.round(19 * rs)   // Error
  const R4 = r + Math.round(25 * rs)   // Anomaly
  const ringStroke = orbitRing === 1 ? 2 : 2.5

  return (
    <g
      transform={`translate(${pos.x}, ${pos.y})`}
      onClick={() => onClick(service)}
      style={{ cursor: 'pointer' }}
    >
      {/* Anomaly ambient glow */}
      {isAnomaly && (
        <circle r={R4 + 5} fill={anomalyGlowColor(score)}
          style={{ animation: 'pulse 2s ease-in-out infinite' }}
        />
      )}

      {/* Root cause spinning ring */}
      {isRootCause && (
        <circle r={R4 + 10} fill="none" stroke="#c45c0a" strokeWidth="1.5"
          strokeDasharray="6 4"
          style={{ animation: 'spin 3s linear infinite', transformOrigin: '0 0' }}
        />
      )}

      {/* Selection dashed ring */}
      {isSelected && (
        <circle r={R4 + 8} fill="none" stroke={theme.text} strokeWidth="1.5"
          strokeDasharray="5 3" opacity="0.6" />
      )}

      {/* Concentric metric rings */}
      <RingArc radius={R1} pct={cpu}       color="#c45c0a" strokeW={ringStroke} anomaly={isAnomaly} />
      <RingArc radius={R2} pct={mem}       color="#5588cc" strokeW={ringStroke} anomaly={isAnomaly} />
      <RingArc radius={R3} pct={errRate}   color="#cc2222" strokeW={ringStroke - 0.5} anomaly={isAnomaly} />
      <RingArc radius={R4} pct={anomScore} color="#9944bb" strokeW={ringStroke - 0.5} anomaly={isAnomaly} />

      {/* Planet body */}
      <circle r={r} fill={fill} stroke={stroke}
        strokeWidth={isSelected || isRootCause ? 2.5 : 1.5}
        style={{ transition: 'r 0.5s ease, fill 0.35s ease, stroke 0.35s ease' }}
      />

      {/* Score label in center */}
      <text textAnchor="middle" dy="4px"
        fontSize={r > 20 ? '10' : '9'}
        fontFamily="'IBM Plex Mono', monospace"
        fill={scoreText}
        stroke={scoreOutline}
        strokeWidth="0.7"
        paintOrder="stroke"
        fontWeight={score >= 0.35 ? 'bold' : '600'}
        style={{ userSelect: 'none', pointerEvents: 'none', transition: 'fill 0.35s ease, stroke 0.35s ease' }}
      >
        {scoreLabel}
      </text>

      {/* Service name */}
      <text textAnchor="middle" dy={r + 14} fontSize="10"
        fontFamily="'IBM Plex Mono', monospace" fill={theme.text}
        style={{ userSelect: 'none', pointerEvents: 'none' }}
      >
        {shortName}
      </text>

      {/* CPU / MEM compact stats */}
      <text textAnchor="middle" dy={r + 26} fontSize="10"
        fontFamily="'IBM Plex Mono', monospace" fill={theme.textMuted}
        style={{ userSelect: 'none', pointerEvents: 'none' }}
      >
        {`CPU ${Math.round(cpu)}% · Memory ${Math.round(mem)}%`}
      </text>

      {/* Error badge */}
      {errRate > 0.5 && (
        <text textAnchor="middle" dy={r + 38} fontSize="9"
          fontFamily="'IBM Plex Mono', monospace" fill="#cc2222"
          style={{ userSelect: 'none', pointerEvents: 'none' }}
        >
          {`ERRORS ${Math.round(errRate)}%`}
        </text>
      )}
    </g>
  )
}
