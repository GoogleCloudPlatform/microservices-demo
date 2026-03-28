export const theme = {
  bg: '#f4f0e8',
  bgDot: '#d8d0c0',
  card: '#ffffff',
  border: '#1a1a1a',
  borderLight: '#999',
  text: '#1a1a1a',
  textMuted: '#555',
  textDim: '#888',
  accent: '#c45c0a',
  accentLight: '#e88040',

  // Status
  normal: '#ffffff',
  normalStroke: '#2a2a2a',
  warning: '#ffe4b5',
  warningStroke: '#c45c0a',
  critical: '#ffb3b3',
  criticalStroke: '#cc2222',

  font: "'IBM Plex Mono', 'Courier New', monospace",
}

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

export const RING_RADII = [0, 100, 185, 285, 370, 460]

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

export function getPlanetPos(service, cx = 490, cy = 340) {
  const cfg = ORBIT_CONFIGS[service]
  if (!cfg) return { x: cx, y: cy }
  const r = RING_RADII[cfg.ring]
  const rad = (cfg.angle - 90) * Math.PI / 180
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) }
}

export function statusColor(status, part = 'fill') {
  if (part === 'fill') {
    if (status === 'critical') return theme.critical
    if (status === 'warning') return theme.warning
    return theme.normal
  }
  if (part === 'stroke') {
    if (status === 'critical') return theme.criticalStroke
    if (status === 'warning') return theme.warningStroke
    return theme.normalStroke
  }
}
