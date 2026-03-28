export const theme = {
  colors: {
    bg: '#0a0e1a',
    card: '#1a1f2e',
    cardBorder: '#2a3050',
    accent: '#00d4ff',
    accentDim: '#0099bb',
    alertRed: '#ff4757',
    warning: '#ffa502',
    success: '#2ed573',
    text: '#e0e6ff',
    textMuted: '#8892b0',
    textDim: '#4a5580',
  },
  status: {
    normal: '#2ed573',
    warning: '#ffa502',
    critical: '#ff4757',
  },
  shadows: {
    card: '0 4px 20px rgba(0, 0, 0, 0.4)',
    glow: '0 0 20px rgba(0, 212, 255, 0.2)',
  },
}

export const getStatusColor = (status) => {
  switch (status) {
    case 'critical': return theme.colors.alertRed
    case 'warning': return theme.colors.warning
    case 'normal': return theme.colors.success
    default: return theme.colors.textMuted
  }
}

export const getScoreColor = (score) => {
  if (score >= 0.7) return theme.colors.alertRed
  if (score >= 0.4) return theme.colors.warning
  return theme.colors.success
}
