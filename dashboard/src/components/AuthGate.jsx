import { useEffect, useRef, useState } from 'react'

function GoogleButton({ clientId, onCredential, onError, ready, theme }) {
  const buttonRef = useRef(null)
  const initializedRef = useRef(false)

  useEffect(() => {
    if (!ready || !clientId || !buttonRef.current || initializedRef.current || !window.google?.accounts?.id) {
      return
    }
    window.google.accounts.id.initialize({
      client_id: clientId,
      callback: (response) => {
        if (response?.credential) {
          onCredential(response.credential)
        } else {
          onError?.('Google sign-in did not return a credential.')
        }
      },
    })
    buttonRef.current.innerHTML = ''
    window.google.accounts.id.renderButton(buttonRef.current, {
      type: 'standard',
      theme: 'outline',
      size: 'large',
      shape: 'pill',
      text: 'signin_with',
      width: 280,
    })
    initializedRef.current = true
  }, [clientId, onCredential, onError, ready])

  return (
    <div>
      <div
        ref={buttonRef}
        style={{
          minHeight: 44,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      />
      {!ready ? (
        <div style={{ marginTop: 12, fontSize: 11, letterSpacing: 1, color: theme.textMuted, textTransform: 'uppercase' }}>
          Loading Google Identity Services…
        </div>
      ) : null}
    </div>
  )
}

export default function AuthGate({ theme, config, loading, error, onLogin }) {
  const [scriptReady, setScriptReady] = useState(Boolean(window.google?.accounts?.id))

  useEffect(() => {
    if (window.google?.accounts?.id) {
      setScriptReady(true)
      return
    }
    const timer = window.setInterval(() => {
      if (window.google?.accounts?.id) {
        setScriptReady(true)
        window.clearInterval(timer)
      }
    }, 250)
    return () => window.clearInterval(timer)
  }, [])

  return (
    <div
      style={{
        width: '100vw',
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: theme.bg,
        backgroundImage: `radial-gradient(circle, ${theme.bgDot} 1px, transparent 1px)`,
        backgroundSize: '24px 24px',
        padding: 24,
      }}
    >
      <div
        style={{
          width: 'min(720px, 100%)',
          border: `1px solid ${theme.border}`,
          background: theme.card,
          boxShadow: theme.shadow,
          padding: '34px 34px 30px',
          display: 'grid',
          gap: 18,
        }}
      >
        <div style={{ display: 'grid', gap: 10 }}>
          <div style={{ fontFamily: theme.displayFont || theme.font, fontSize: 13, letterSpacing: 2.2, color: theme.textMuted, textTransform: 'uppercase' }}>
            AEGIS Access
          </div>
          <div style={{ fontFamily: theme.displayFont || theme.font, fontSize: 42, lineHeight: 0.95, color: theme.text }}>
            Sign in with Google to open the live control surface.
          </div>
          <div style={{ fontSize: 14, lineHeight: 1.7, color: theme.textMuted, maxWidth: 560 }}>
            Any Google user can enter the monitoring surface. Operator actions can still be restricted separately through backend configuration.
          </div>
        </div>

        <div
          style={{
            border: `1px solid ${theme.borderLight}`,
            background: theme.panel,
            padding: '18px 20px',
            display: 'grid',
            gap: 12,
          }}
        >
          <div style={{ fontSize: 11, letterSpacing: 1.5, textTransform: 'uppercase', color: theme.textMuted }}>
            Google Identity
          </div>
          {config?.google_client_id ? (
            <GoogleButton clientId={config.google_client_id} onCredential={onLogin} onError={() => {}} ready={scriptReady} theme={theme} />
          ) : (
            <div style={{ fontSize: 13, lineHeight: 1.6, color: theme.textMuted }}>
              Google sign-in is enabled, but the backend is missing a Google client ID. Set <code>AEGIS_GOOGLE_CLIENT_ID</code> before publishing the site.
            </div>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap' }}>
          <div style={{ fontSize: 11, letterSpacing: 1.4, textTransform: 'uppercase', color: theme.textMuted }}>
            {loading ? 'Checking current session…' : 'Awaiting sign-in'}
          </div>
          {error ? (
            <div style={{ fontSize: 12, color: theme.accent }}>
              {error}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  )
}
