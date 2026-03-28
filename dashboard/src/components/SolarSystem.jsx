import { useRef, useEffect } from 'react'
import * as d3 from 'd3'
import { ORBIT_CONFIGS } from '../styles/theme'
import { useTheme } from '../ThemeContext'
import OrbitRings from './OrbitRings'
import DependencyEdges from './DependencyEdges'
import PlanetNode from './PlanetNode'

const CX = 490, CY = 340
const ALL_SERVICES = Object.keys(ORBIT_CONFIGS)

const RING_LEGEND = [
  { color: '#c45c0a', label: 'CPU usage', key: 'cpu_mean' },
  { color: '#5588cc', label: 'Memory usage', key: 'mem_mean' },
  { color: '#cc2222', label: 'Error rate', key: 'error_rate_mean', scale: 100 },
  { color: '#9944bb', label: 'Anomaly score', key: 'combined_score', scale: 100 },
]

export default function SolarSystem({ topology, selectedService, onSelectService }) {
  const { theme } = useTheme()
  const svgRef = useRef(null)
  const gRef   = useRef(null)
  const transformRef = useRef('translate(0,0) scale(1)')
  const [, forceUpdate] = [null, () => {}]

  useEffect(() => {
    if (!svgRef.current || !gRef.current) return
    const zoom = d3.zoom()
      .scaleExtent([0.35, 2.5])
      .on('zoom', (event) => {
        const t = event.transform
        gRef.current.setAttribute('transform', `translate(${t.x},${t.y}) scale(${t.k})`)
      })
    d3.select(svgRef.current).call(zoom)
    return () => d3.select(svgRef.current).on('.zoom', null)
  }, [])

  const services = topology?.services || {}
  const graph = topology?.dependency_graph || {}
  const rootCause = topology?.root_cause || {}
  const propagationPath = rootCause?.propagation_path || []
  const selData = services[selectedService]

  // Legend values for selected service
  const legendValues = RING_LEGEND.map(({ color, label, key, scale }) => {
    let val = null
    if (key && selData) {
      val = selData[key] ?? selData?.features?.[key]
      if (val != null && scale) val = val * scale
    }
    return { color, label, val }
  })

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      {/* Live / offline indicator */}
      <div style={{
        position: 'absolute', top: 8, left: 12, zIndex: 10,
        fontFamily: theme.font, fontSize: '10px', color: theme.textMuted,
        display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap',
      }}>
        <span style={{
          display: 'inline-block', width: 7, height: 7, borderRadius: '50%',
          background: topology ? '#2a8a2a' : '#cc2222',
          boxShadow: topology ? '0 0 6px #2a8a2a' : '0 0 6px #cc2222',
        }} />
        {topology ? 'Live backend data' : 'Backend offline'}
        {topology && (
          <span style={{ color: theme.textDim, marginLeft: 8, display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            <span>System health: {topology.health_score}/100</span>
            <span>
              Failure momentum: {topology.failure_momentum > 0 ? '+' : ''}{topology.failure_momentum} points/min
            </span>
          </span>
        )}
      </div>

      {/* Reset zoom */}
      <button
        onClick={() => {
          if (svgRef.current) {
            d3.select(svgRef.current).call(d3.zoom().transform, d3.zoomIdentity)
            gRef.current.setAttribute('transform', 'translate(0,0) scale(1)')
          }
        }}
        style={{
          position: 'absolute', bottom: 36, right: 12, zIndex: 10,
          fontFamily: theme.font, fontSize: '10px', padding: '3px 8px',
          border: `1px solid ${theme.borderLight}`, background: theme.bg,
          cursor: 'pointer', color: theme.textMuted,
        }}
      >RESET VIEW</button>

      {/* Bottom-left ring legend (always visible) */}
      <div style={{
        position: 'absolute', bottom: 36, left: 12, zIndex: 10,
        background: theme.card, border: `1px solid ${theme.borderLight}`,
        padding: '8px 14px', fontFamily: theme.font,
        minWidth: 176,
      }}>
        <div style={{ fontSize: 8, color: theme.textMuted, marginBottom: 7, letterSpacing: 1.5, fontWeight: 'bold' }}>
          {selectedService ? `${selectedService.toUpperCase()} SIGNALS` : 'SERVICE SIGNALS'}
        </div>
        {legendValues.map(({ color, label, val }) => (
          <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 5 }}>
            <div style={{ width: 10, height: 10, borderRadius: '50%', background: color, flexShrink: 0 }} />
            <span style={{ fontSize: 10, color: theme.textMuted, width: 74 }}>{label}</span>
            <span style={{ fontSize: 10, color: theme.text, fontWeight: 'bold' }}>
              {val != null ? `${Math.round(val)}%` : '—'}
            </span>
          </div>
        ))}
      </div>

      <svg
        ref={svgRef}
        viewBox="0 0 1000 680"
        style={{ width: '100%', height: '100%', background: 'transparent' }}
      >
        <defs>
          <style>{`
            @keyframes pulse {
              0%, 100% { opacity: 0.7; transform: scale(1); }
              50% { opacity: 1; transform: scale(1.3); }
            }
            @keyframes orbitSpinCW {
              from { transform-origin: ${CX}px ${CY}px; transform: rotate(0deg); }
              to   { transform-origin: ${CX}px ${CY}px; transform: rotate(360deg); }
            }
            @keyframes orbitSpinCCW {
              from { transform-origin: ${CX}px ${CY}px; transform: rotate(0deg); }
              to   { transform-origin: ${CX}px ${CY}px; transform: rotate(-360deg); }
            }
            @keyframes spin {
              from { transform: rotate(0deg); }
              to   { transform: rotate(360deg); }
            }
            @keyframes dashFlow {
              from { stroke-dashoffset: 0; }
              to   { stroke-dashoffset: -20; }
            }
          `}</style>
        </defs>

        <g ref={gRef} transform="translate(0,0) scale(1)">
          <OrbitRings />
          <DependencyEdges
            graph={graph}
            services={services}
            selectedService={selectedService}
            propagationPath={propagationPath}
          />
          {ALL_SERVICES.map(svc => (
            <PlanetNode
              key={svc}
              service={svc}
              data={services[svc]}
              isSelected={selectedService === svc}
              isRootCause={rootCause?.service === svc}
              onClick={onSelectService}
              orbitRing={ORBIT_CONFIGS[svc].ring}
            />
          ))}
        </g>
      </svg>
    </div>
  )
}
