import { getStatusColor, getScoreColor, theme } from '../styles/theme'

const SERVICE_ICONS = {
  frontend: '🌐',
  productcatalogservice: '📦',
  cartservice: '🛒',
  recommendationservice: '⭐',
  checkoutservice: '💳',
  paymentservice: '💰',
  shippingservice: '🚚',
  emailservice: '📧',
  currencyservice: '💱',
  adservice: '📢',
  'redis-cart': '🗄️',
}

const SERVICE_SHORT = {
  frontend: 'Frontend',
  productcatalogservice: 'Catalog',
  cartservice: 'Cart',
  recommendationservice: 'Recommend',
  checkoutservice: 'Checkout',
  paymentservice: 'Payment',
  shippingservice: 'Shipping',
  emailservice: 'Email',
  currencyservice: 'Currency',
  adservice: 'AdService',
  'redis-cart': 'Redis',
}

function ServiceCard({ name, data, isRootCause }) {
  const score = data?.combined_score ?? 0
  const status = data?.status ?? 'normal'
  const statusColor = getStatusColor(status)
  const scoreColor = getScoreColor(score)
  const scorePercent = Math.round(score * 100)
  const icon = SERVICE_ICONS[name] || '⚙️'
  const shortName = SERVICE_SHORT[name] || name

  return (
    <div
      style={{
        background: theme.colors.card,
        border: `1px solid ${isRootCause ? theme.colors.alertRed : theme.colors.cardBorder}`,
        borderRadius: '12px',
        padding: '16px',
        position: 'relative',
        boxShadow: isRootCause
          ? `0 0 16px rgba(255,71,87,0.3)`
          : theme.shadows.card,
        transition: 'all 0.3s ease',
        cursor: 'default',
      }}
    >
      {isRootCause && (
        <div
          style={{
            position: 'absolute',
            top: '-8px',
            right: '8px',
            background: theme.colors.alertRed,
            color: '#fff',
            fontSize: '10px',
            fontWeight: 700,
            padding: '2px 6px',
            borderRadius: '4px',
            letterSpacing: '0.5px',
          }}
        >
          ROOT CAUSE
        </div>
      )}

      {/* Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '12px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '20px' }}>{icon}</span>
          <div>
            <div
              style={{
                fontSize: '13px',
                fontWeight: 600,
                color: theme.colors.text,
              }}
            >
              {shortName}
            </div>
            <div style={{ fontSize: '10px', color: theme.colors.textMuted }}>
              {name}
            </div>
          </div>
        </div>
        <div
          style={{
            width: '10px',
            height: '10px',
            borderRadius: '50%',
            background: statusColor,
            boxShadow: `0 0 8px ${statusColor}`,
          }}
        />
      </div>

      {/* Score bar */}
      <div style={{ marginBottom: '8px' }}>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '6px',
          }}
        >
          <span
            style={{
              fontSize: '11px',
              color: theme.colors.textMuted,
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
            }}
          >
            Anomaly Score
          </span>
          <span
            style={{
              fontSize: '18px',
              fontWeight: 700,
              color: scoreColor,
              fontVariantNumeric: 'tabular-nums',
            }}
          >
            {scorePercent}
          </span>
        </div>
        <div
          style={{
            height: '4px',
            background: theme.colors.cardBorder,
            borderRadius: '2px',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              height: '100%',
              width: `${scorePercent}%`,
              background: scoreColor,
              borderRadius: '2px',
              transition: 'width 0.5s ease',
            }}
          />
        </div>
      </div>

      {/* Sub-scores */}
      <div
        style={{
          display: 'flex',
          gap: '8px',
          fontSize: '10px',
          color: theme.colors.textMuted,
        }}
      >
        <span>IF: {Math.round((data?.if_score ?? 0) * 100)}</span>
        <span style={{ color: theme.colors.textDim }}>|</span>
        <span>LSTM: {Math.round((data?.lstm_score ?? 0) * 100)}</span>
        <span style={{ color: theme.colors.textDim }}>|</span>
        <span
          style={{
            color: statusColor,
            fontWeight: 600,
            textTransform: 'uppercase',
          }}
        >
          {status}
        </span>
      </div>
    </div>
  )
}

export default function ServiceGrid({ services, rootCauseService }) {
  if (!services) {
    return (
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
          gap: '16px',
        }}
      >
        {Array.from({ length: 11 }).map((_, i) => (
          <div
            key={i}
            style={{
              background: theme.colors.card,
              border: `1px solid ${theme.colors.cardBorder}`,
              borderRadius: '12px',
              height: '120px',
              opacity: 0.5,
            }}
          />
        ))}
      </div>
    )
  }

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
        gap: '16px',
      }}
    >
      {Object.entries(services).map(([name, data]) => (
        <ServiceCard
          key={name}
          name={name}
          data={data}
          isRootCause={name === rootCauseService}
        />
      ))}
    </div>
  )
}
