import { RING_RADII } from '../styles/theme'
import { useTheme } from '../ThemeContext'

const CX = 490, CY = 340

export default function OrbitRings() {
  const { theme } = useTheme()
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
          opacity="0.25"
          style={{ animation: `orbitSpin${i % 2 === 0 ? 'CW' : 'CCW'} ${60 + i * 15}s linear infinite` }}
        />
      ))}
    </g>
  )
}
