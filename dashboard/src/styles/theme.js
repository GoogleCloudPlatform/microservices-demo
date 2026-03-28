export const lightTheme = {
  bg: '#f4f0e8',
  bgDot: '#c8c0b0',
  card: '#ffffff',
  border: '#1a1a1a',
  borderLight: '#999',
  text: '#1a1a1a',
  textMuted: '#555',
  textDim: '#888',
  accent: '#c45c0a',
  accentLight: '#e88040',
  normal: '#ffffff',
  normalStroke: '#2a2a2a',
  warning: '#ffe4b5',
  warningStroke: '#c45c0a',
  critical: '#ffb3b3',
  criticalStroke: '#cc2222',
  font: "'IBM Plex Mono', 'Courier New', monospace",
  displayFont: "'IBM Plex Sans Condensed', 'Manrope', sans-serif",
  sansFont: "'Manrope', 'IBM Plex Sans Condensed', sans-serif",
}

export const darkTheme = {
  bg: '#0d1117',
  bgDot: '#1e2228',
  card: '#161b22',
  border: '#c9d1d9',
  borderLight: '#30363d',
  text: '#e6edf3',
  textMuted: '#8b949e',
  textDim: '#484f58',
  accent: '#ff7b35',
  accentLight: '#ff9955',
  normal: '#1c2333',
  normalStroke: '#58a6ff',
  warning: '#2d1e00',
  warningStroke: '#e3b341',
  critical: '#1f0505',
  criticalStroke: '#f85149',
  font: "'IBM Plex Mono', 'Courier New', monospace",
  displayFont: "'IBM Plex Sans Condensed', 'Manrope', sans-serif",
  sansFont: "'Manrope', 'IBM Plex Sans Condensed', sans-serif",
}

// Default export for legacy imports (light theme)
export const theme = lightTheme

export const ORBIT_CONFIGS = {
  'redis-cart':            { ring: 1, angle: 0 },
  'productcatalogservice': { ring: 2, angle: 0 },
  'paymentservice':        { ring: 2, angle: 60 },
  'shippingservice':       { ring: 2, angle: 120 },
  'emailservice':          { ring: 2, angle: 180 },
  'currencyservice':       { ring: 2, angle: 240 },
  'adservice':             { ring: 2, angle: 300 },
  'cartservice':           { ring: 3, angle: 250 },
  'recommendationservice': { ring: 3, angle: 80 },
  'checkoutservice':       { ring: 4, angle: 320 },
  'frontend':              { ring: 5, angle: 45 },
}

export const RING_RADII = [0, 100, 195, 300, 390, 480]

export const SERVICE_SHORT = {
  frontend: 'frontend',
  productcatalogservice: 'catalog',
  cartservice: 'cart',
  recommendationservice: 'recommend',
  checkoutservice: 'checkout',
  paymentservice: 'payment',
  shippingservice: 'shipping',
  emailservice: 'email',
  currencyservice: 'currency',
  adservice: 'adservice',
  'redis-cart': 'redis',
}

function clamp01(value) {
  return Math.max(0, Math.min(1, value))
}

function hexToRgb(hex) {
  const clean = hex.replace('#', '')
  const normalized = clean.length === 3
    ? clean.split('').map(ch => ch + ch).join('')
    : clean
  const int = Number.parseInt(normalized, 16)
  return {
    r: (int >> 16) & 255,
    g: (int >> 8) & 255,
    b: int & 255,
  }
}

function rgbToHex({ r, g, b }) {
  const toHex = (value) => Math.round(value).toString(16).padStart(2, '0')
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`
}

function mixHex(a, b, t) {
  const left = hexToRgb(a)
  const right = hexToRgb(b)
  const pct = clamp01(t)
  return rgbToHex({
    r: left.r + (right.r - left.r) * pct,
    g: left.g + (right.g - left.g) * pct,
    b: left.b + (right.b - left.b) * pct,
  })
}

export function anomalyScoreColor(score, part = 'fill', t = lightTheme) {
  const pct = clamp01(score)
  const stops = part === 'stroke'
    ? ['#1f7a3d', '#c97512', '#b52222']
    : ['#62c66f', '#f0a43c', '#e14b42']

  if (pct <= 0.5) {
    return mixHex(stops[0], stops[1], pct / 0.5)
  }
  return mixHex(stops[1], stops[2], (pct - 0.5) / 0.5)
}

export function anomalyGlowColor(score) {
  const pct = clamp01(score)
  if (pct < 0.35) return 'rgba(58, 166, 85, 0.14)'
  if (pct < 0.7) return 'rgba(240, 164, 60, 0.14)'
  return 'rgba(225, 75, 66, 0.16)'
}

export function getPlanetPos(service, cx = 490, cy = 340) {
  const cfg = ORBIT_CONFIGS[service]
  if (!cfg) return { x: cx, y: cy }
  const r = RING_RADII[cfg.ring]
  const rad = (cfg.angle - 90) * Math.PI / 180
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) }
}

export function statusColor(status, part = 'fill', t = lightTheme) {
  if (part === 'fill') {
    if (status === 'critical') return t.critical
    if (status === 'warning') return t.warning
    return t.normal
  }
  if (part === 'stroke') {
    if (status === 'critical') return t.criticalStroke
    if (status === 'warning') return t.warningStroke
    return t.normalStroke
  }
}
