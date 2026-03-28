import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'
import { theme } from '../styles/theme'

const CHART_COLORS = [
  '#00d4ff',
  '#ff4757',
  '#ffa502',
  '#2ed573',
  '#a29bfe',
  '#fd79a8',
]

function getTopServices(history, n = 3) {
  if (!history || history.length === 0) return []

  // Find services with highest average score
  const latest = history[history.length - 1]?.scores || {}
  const sorted = Object.entries(latest).sort(([, a], [, b]) => b - a)
  return sorted.slice(0, n).map(([svc]) => svc)
}

function prepareChartData(history, services) {
  return history.map((snapshot, i) => {
    const point = { tick: i }
    for (const svc of services) {
      point[svc] = Math.round((snapshot.scores?.[svc] ?? 0) * 100)
    }
    return point
  })
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div
      style={{
        background: theme.colors.card,
        border: `1px solid ${theme.colors.cardBorder}`,
        borderRadius: '8px',
        padding: '10px 14px',
        fontSize: '12px',
      }}
    >
      {payload.map((p) => (
        <div
          key={p.dataKey}
          style={{
            color: p.color,
            marginBottom: '4px',
            display: 'flex',
            justifyContent: 'space-between',
            gap: '16px',
          }}
        >
          <span>{p.dataKey}</span>
          <span style={{ fontWeight: 700 }}>{p.value}</span>
        </div>
      ))}
    </div>
  )
}

export default function AnomalyChart({ history }) {
  const topServices = getTopServices(history, 3)
  const data = prepareChartData(history, topServices)

  if (!history || history.length === 0) {
    return (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '200px',
          color: theme.colors.textMuted,
          fontSize: '14px',
        }}
      >
        Waiting for data...
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
        <CartesianGrid
          strokeDasharray="3 3"
          stroke={theme.colors.cardBorder}
          opacity={0.5}
        />
        <XAxis
          dataKey="tick"
          tick={{ fill: theme.colors.textMuted, fontSize: 10 }}
          tickLine={false}
          axisLine={{ stroke: theme.colors.cardBorder }}
          label={{ value: 'Time (2s intervals)', position: 'insideBottom', offset: -2, fill: theme.colors.textMuted, fontSize: 10 }}
        />
        <YAxis
          domain={[0, 100]}
          tick={{ fill: theme.colors.textMuted, fontSize: 10 }}
          tickLine={false}
          axisLine={{ stroke: theme.colors.cardBorder }}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend
          wrapperStyle={{
            fontSize: '11px',
            color: theme.colors.textMuted,
          }}
        />
        <ReferenceLine
          y={70}
          stroke={theme.colors.alertRed}
          strokeDasharray="4 4"
          opacity={0.6}
          label={{ value: 'Alert', position: 'right', fill: theme.colors.alertRed, fontSize: 10 }}
        />
        <ReferenceLine
          y={40}
          stroke={theme.colors.warning}
          strokeDasharray="4 4"
          opacity={0.4}
        />
        {topServices.map((svc, i) => (
          <Line
            key={svc}
            type="monotone"
            dataKey={svc}
            stroke={CHART_COLORS[i % CHART_COLORS.length]}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  )
}
