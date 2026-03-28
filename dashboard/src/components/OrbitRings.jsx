import { RING_RADII, theme } from '../styles/theme'

const CX = 490, CY = 340

export default function OrbitRings({ anomalousRings = new Set() }) {
  return (
    <g className="orbit-rings">
      {RING_RADII.slice(1).map((r, i) => (
        <circle
          key={r}
          cx={CX} cy={CY} r={r}
          fill="none"
          stroke={theme.border}
          strokeWidth="0.5"
          strokeDasharray="3 6"
          opacity="0.35"
          style={{ animation: `orbitSpin${i % 2 === 0 ? 'CW' : 'CCW'} ${60 + i * 15}s linear infinite` }}
        />
      ))}
      {/* Cluster core */}
      <circle cx={CX} cy={CY} r={8} fill={theme.border} />
      <circle cx={CX} cy={CY} r={14} fill="none" stroke={theme.border} strokeWidth="1" />
      <text x={CX} y={CY + 26} textAnchor="middle" fontSize="9"
        fontFamily="'IBM Plex Mono', monospace" fill="#555">Cluster Core</text>
    </g>
  )
}
