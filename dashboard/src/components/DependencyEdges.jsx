import { getPlanetPos, theme } from '../styles/theme'

const CX = 490, CY = 340

export default function DependencyEdges({ graph, services, selectedService, propagationPath }) {
  if (!graph) return null

  const edges = []
  Object.entries(graph).forEach(([from, deps]) => {
    deps.forEach(to => {
      if (!getPlanetPos(from) || !getPlanetPos(to)) return
      edges.push({ from, to })
    })
  })

  return (
    <g className="dependency-edges">
      <defs>
        <marker id="arrow-normal" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
          <path d="M0,0 L0,6 L6,3 z" fill="#999" />
        </marker>
        <marker id="arrow-alert" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
          <path d="M0,0 L0,6 L6,3 z" fill="#c45c0a" />
        </marker>
      </defs>
      {edges.map(({ from, to }) => {
        const p1 = getPlanetPos(from)
        const p2 = getPlanetPos(to)

        // Quadratic bezier control point: slightly toward center
        const mx = (p1.x + p2.x) / 2
        const my = (p1.y + p2.y) / 2
        const dx = CX - mx, dy = CY - my
        const len = Math.sqrt(dx*dx + dy*dy) || 1
        const cpx = mx + dx/len * 30
        const cpy = my + dy/len * 30

        const isPropagate = propagationPath && (propagationPath.includes(from) || propagationPath.includes(to))
        const fromStatus = services?.[from]?.status
        const isAlert = fromStatus === 'warning' || fromStatus === 'critical'
        const isSelected = from === selectedService || to === selectedService

        const strokeColor = isPropagate ? '#c45c0a' : isSelected ? '#555' : '#bbb'
        const strokeWidth = isPropagate ? 1.5 : isSelected ? 1.2 : 0.8
        const dashArray = isPropagate ? '6 3' : isSelected ? 'none' : '4 4'
        const markerId = isAlert || isPropagate ? 'arrow-alert' : 'arrow-normal'

        return (
          <path
            key={`${from}-${to}`}
            d={`M ${p1.x} ${p1.y} Q ${cpx} ${cpy} ${p2.x} ${p2.y}`}
            fill="none"
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            strokeDasharray={dashArray}
            markerEnd={`url(#${markerId})`}
            opacity={isSelected || isPropagate ? 1 : 0.6}
            style={isPropagate ? { animation: 'dashFlow 1.5s linear infinite' } : {}}
          />
        )
      })}
    </g>
  )
}
