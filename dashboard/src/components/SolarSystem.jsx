import { useRef, useEffect, useState, useCallback } from 'react'
import * as d3 from 'd3'
import { ORBIT_CONFIGS, theme } from '../styles/theme'
import OrbitRings from './OrbitRings'
import DependencyEdges from './DependencyEdges'
import PlanetNode from './PlanetNode'

const CX = 490, CY = 340
const ALL_SERVICES = Object.keys(ORBIT_CONFIGS)

export default function SolarSystem({ topology, selectedService, onSelectService }) {
  const svgRef = useRef(null)
  const gRef = useRef(null)
  const [transform, setTransform] = useState('translate(0,0) scale(1)')

  useEffect(() => {
    if (!svgRef.current || !gRef.current) return
    const zoom = d3.zoom()
      .scaleExtent([0.4, 2.5])
      .on('zoom', (event) => {
        const t = event.transform
        setTransform(`translate(${t.x},${t.y}) scale(${t.k})`)
      })
    d3.select(svgRef.current).call(zoom)
    return () => d3.select(svgRef.current).on('.zoom', null)
  }, [])

  const services = topology?.services || {}
  const graph = topology?.dependency_graph || {}
  const rootCause = topology?.root_cause || {}
  const propagationPath = rootCause?.propagation_path || []

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      {/* Connection status */}
      <div style={{
        position: 'absolute', top: 8, left: 12, zIndex: 10,
        fontFamily: theme.font, fontSize: '10px', color: theme.textMuted,
        display: 'flex', alignItems: 'center', gap: 6,
      }}>
        <span style={{
          display: 'inline-block', width: 7, height: 7, borderRadius: '50%',
          background: topology ? '#2a8a2a' : '#cc2222',
          boxShadow: topology ? '0 0 6px #2a8a2a' : '0 0 6px #cc2222',
        }} />
        {topology ? 'LIVE' : 'OFFLINE'}
        {topology && (
          <span style={{ color: theme.textDim, marginLeft: 8 }}>
            {`H=${topology.health_score} | M=${topology.failure_momentum > 0 ? '+' : ''}${topology.failure_momentum} pts/min`}
          </span>
        )}
      </div>

      {/* Reset zoom button */}
      <button
        onClick={() => {
          d3.select(svgRef.current).call(
            d3.zoom().transform, d3.zoomIdentity
          )
          setTransform('translate(0,0) scale(1)')
        }}
        style={{
          position: 'absolute', bottom: 10, left: 12, zIndex: 10,
          fontFamily: theme.font, fontSize: '10px', padding: '3px 8px',
          border: `1px solid ${theme.border}`, background: theme.bg,
          cursor: 'pointer', color: theme.text,
        }}
      >RESET VIEW</button>

      <svg
        ref={svgRef}
        viewBox="0 0 1000 680"
        style={{ width: '100%', height: '100%', background: 'transparent' }}
      >
        {/* CSS animations */}
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
            .planet-anomaly { filter: drop-shadow(0 0 4px rgba(196,92,10,0.5)); }
            g circle { transition: r 0.4s ease; }
          `}</style>
        </defs>

        <g ref={gRef} transform={transform}>
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
            />
          ))}
        </g>
      </svg>
    </div>
  )
}
