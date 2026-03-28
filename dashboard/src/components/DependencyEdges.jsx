import { getPlanetPos, ORBIT_CONFIGS } from '../styles/theme'
import { useTheme } from '../ThemeContext'

const CX = 490, CY = 340
const PLANET_R = 28

function offsetPoint(p1, p2, offset) {
  const dx = p2.x - p1.x
  const dy = p2.y - p1.y
  const len = Math.sqrt(dx * dx + dy * dy) || 1
  return { x: p1.x + (dx / len) * offset, y: p1.y + (dy / len) * offset }
}

export default function DependencyEdges({ graph, services, selectedService, propagationPath }) {
  const { theme } = useTheme()
  if (!graph) return null

  const edges = []
  Object.entries(graph).forEach(([from, deps]) => {
    (Array.isArray(deps) ? deps : []).forEach(to => {
      if (!ORBIT_CONFIGS[from] || !ORBIT_CONFIGS[to]) return
      edges.push({ from, to })
    })
  })

  return (
    <g className="dependency-edges">
      <defs>
        <marker id="arrow-normal" markerWidth="10" markerHeight="8"
          refX="9" refY="4" orient="auto" markerUnits="userSpaceOnUse">
          <path d="M0,0.5 L0,7.5 L10,4 z" fill="#666" opacity="0.85" />
        </marker>
        <marker id="arrow-alert" markerWidth="10" markerHeight="8"
          refX="9" refY="4" orient="auto" markerUnits="userSpaceOnUse">
          <path d="M0,0.5 L0,7.5 L10,4 z" fill="#c45c0a" />
        </marker>
        <marker id="arrow-propagate" markerWidth="12" markerHeight="10"
          refX="11" refY="5" orient="auto" markerUnits="userSpaceOnUse">
          <path d="M0,0.5 L0,9.5 L12,5 z" fill="#cc2222" />
        </marker>
        <marker id="arrow-broken" markerWidth="10" markerHeight="8"
          refX="9" refY="4" orient="auto" markerUnits="userSpaceOnUse">
          <path d="M0,0.5 L0,7.5 L10,4 z" fill="#ff4444" />
        </marker>
        <marker id="arrow-selected" markerWidth="10" markerHeight="8"
          refX="9" refY="4" orient="auto" markerUnits="userSpaceOnUse">
          <path d="M0,0.5 L0,7.5 L10,4 z" fill="#222" />
        </marker>
        <filter id="edge-glow" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="2.5" result="blur" />
          <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>

      {edges.map(({ from, to }) => {
        const rawP1 = getPlanetPos(from)
        const rawP2 = getPlanetPos(to)
        const p1 = offsetPoint(rawP1, rawP2, PLANET_R)
        const p2 = offsetPoint(rawP2, rawP1, PLANET_R)

        const mx = (p1.x + p2.x) / 2
        const my = (p1.y + p2.y) / 2
        const dx = CX - mx, dy = CY - my
        const len = Math.sqrt(dx * dx + dy * dy) || 1
        const cpx = mx + (dx / len) * 35
        const cpy = my + (dy / len) * 35

        // Bezier midpoint at t=0.5
        const midX = 0.25 * p1.x + 0.5 * cpx + 0.25 * p2.x
        const midY = 0.25 * p1.y + 0.5 * cpy + 0.25 * p2.y

        const isPropagate = propagationPath && (
          propagationPath.includes(from) || propagationPath.includes(to)
        )
        const fromSvc = services?.[from]
        const toSvc = services?.[to]
        // Broken chain: either endpoint is critical with high score
        const isBroken = (
          (fromSvc?.status === 'critical' && (fromSvc?.combined_score || 0) > 0.65) ||
          (toSvc?.status === 'critical' && (toSvc?.combined_score || 0) > 0.65)
        )
        const isAlert = fromSvc?.status === 'warning' || fromSvc?.status === 'critical'
        const isSelected = from === selectedService || to === selectedService

        let strokeColor, strokeWidth, dashArray, markerId, opacity, filterAttr

        if (isBroken) {
          strokeColor = '#ff4444'
          strokeWidth = 2.5
          dashArray = '3 9'
          markerId = 'arrow-broken'
          opacity = 1
          filterAttr = 'url(#edge-glow)'
        } else if (isPropagate) {
          strokeColor = '#cc2222'
          strokeWidth = 3
          dashArray = '8 5'
          markerId = 'arrow-propagate'
          opacity = 1
          filterAttr = 'url(#edge-glow)'
        } else if (isSelected) {
          strokeColor = theme.text
          strokeWidth = 2.5
          dashArray = 'none'
          markerId = 'arrow-selected'
          opacity = 1
          filterAttr = undefined
        } else if (isAlert) {
          strokeColor = '#c45c0a'
          strokeWidth = 2
          dashArray = '5 4'
          markerId = 'arrow-alert'
          opacity = 0.9
          filterAttr = undefined
        } else {
          strokeColor = theme.textDim
          strokeWidth = 1.5
          dashArray = 'none'
          markerId = 'arrow-normal'
          opacity = 0.65
          filterAttr = undefined
        }

        return (
          <g key={`${from}-${to}`}>
            <path
              d={`M ${p1.x} ${p1.y} Q ${cpx} ${cpy} ${p2.x} ${p2.y}`}
              fill="none"
              stroke={strokeColor}
              strokeWidth={strokeWidth}
              strokeDasharray={dashArray}
              markerEnd={`url(#${markerId})`}
              opacity={opacity}
              filter={filterAttr}
              style={isPropagate ? { animation: 'dashFlow 1.2s linear infinite' } : {}}
            />
            {/* Broken chain break symbol */}
            {isBroken && (
              <text x={midX} y={midY} textAnchor="middle" dominantBaseline="middle"
                fontSize="13" fill="#ff4444"
                style={{ userSelect: 'none', pointerEvents: 'none', fontWeight: 'bold' }}>
                ✕
              </text>
            )}
          </g>
        )
      })}
    </g>
  )
}
