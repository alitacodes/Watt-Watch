import { useState } from "react";

const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

  * { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg-primary: #0a0e0f;
    --bg-secondary: #111618;
    --bg-card: #141a1c;
    --bg-card2: #0f1416;
    --border: #1e2a2d;
    --border-bright: #2eff8b44;
    --green: #2eff8b;
    --green-dim: #1a9954;
    --green-muted: rgba(46,255,139,0.10);
    --green-glow: rgba(46,255,139,0.18);
    --red: #ff4d6d;
    --red-dim: rgba(255,77,109,0.15);
    --text-primary: #d4e8e0;
    --text-secondary: #7a9a90;
    --text-dim: #4a6a62;
    --mono: 'Share Tech Mono', monospace;
  }

  body {
    background: var(--bg-primary);
    font-family: 'Rajdhani', sans-serif;
    color: var(--text-primary);
  }

  .login-root {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-primary);
    position: relative;
    overflow: hidden;
  }

  /* Animated grid background */
  .bg-grid {
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(46,255,139,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(46,255,139,0.03) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none;
  }

  /* Radial glow in center */
  .bg-glow {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(46,255,139,0.06) 0%, transparent 70%);
    pointer-events: none;
  }

  /* Corner decorations */
  .corner {
    position: absolute;
    width: 60px;
    height: 60px;
    border-color: rgba(46,255,139,0.15);
    border-style: solid;
  }
  .corner.tl { top: 24px; left: 24px; border-width: 2px 0 0 2px; }
  .corner.tr { top: 24px; right: 24px; border-width: 2px 2px 0 0; }
  .corner.bl { bottom: 24px; left: 24px; border-width: 0 0 2px 2px; }
  .corner.br { bottom: 24px; right: 24px; border-width: 0 2px 2px 0; }

  /* Scan line animation */
  .scanline {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(46,255,139,0.25), transparent);
    animation: scan 4s linear infinite;
    pointer-events: none;
  }

  @keyframes scan {
    0% { top: 0; opacity: 1; }
    90% { opacity: 0.6; }
    100% { top: 100%; opacity: 0; }
  }

  /* Login card */
  .login-card {
    position: relative;
    width: 420px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 0 60px rgba(46,255,139,0.06), 0 24px 60px rgba(0,0,0,0.5);
    z-index: 2;
  }

  /* Top accent bar */
  .card-accent {
    height: 3px;
    background: linear-gradient(90deg, transparent, var(--green), var(--green), transparent);
    opacity: 0.7;
  }

  .card-header {
    padding: 28px 32px 20px;
    border-bottom: 1px solid var(--border);
    text-align: center;
  }

  .logo-mark {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
  }

  .logo-icon {
    width: 36px;
    height: 36px;
    border: 1.5px solid var(--green-dim);
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--green-muted);
    color: var(--green);
    font-size: 16px;
  }

  .logo-label {
    font-family: var(--mono);
    font-size: 17px;
    font-weight: 700;
    letter-spacing: 0.14em;
    color: var(--green);
  }

  .card-title {
    font-size: 20px;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: 0.04em;
    margin-bottom: 6px;
  }

  .card-subtitle {
    font-size: 12px;
    color: var(--text-secondary);
    font-family: var(--mono);
    letter-spacing: 0.08em;
  }

  /* Session ID badge */
  .session-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-top: 10px;
    padding: 4px 12px;
    background: var(--bg-card2);
    border: 1px solid var(--border);
    border-radius: 3px;
    font-size: 9px;
    font-family: var(--mono);
    color: var(--text-dim);
    letter-spacing: 0.1em;
  }

  .session-dot {
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 5px var(--green);
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
  }

  /* Form */
  .card-body {
    padding: 28px 32px 24px;
  }

  .field {
    margin-bottom: 18px;
  }

  .field-label {
    font-size: 9px;
    font-family: var(--mono);
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-bottom: 7px;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .field-label-dot {
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: var(--green-dim);
  }

  .field-input-wrap {
    position: relative;
  }

  .field-icon {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-dim);
    display: flex;
    align-items: center;
    pointer-events: none;
  }

  .field-input {
    width: 100%;
    background: var(--bg-primary);
    border: 1px solid var(--border);
    border-radius: 5px;
    padding: 11px 12px 11px 36px;
    font-size: 13px;
    font-family: var(--mono);
    color: var(--text-primary);
    letter-spacing: 0.04em;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
  }

  .field-input::placeholder { color: var(--text-dim); font-size: 12px; }

  .field-input:focus {
    border-color: var(--green-dim);
    box-shadow: 0 0 0 3px var(--green-muted);
  }

  .field-input.error {
    border-color: var(--red);
    box-shadow: 0 0 0 3px var(--red-dim);
  }

  /* Show/hide password toggle */
  .pw-toggle {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: var(--text-dim);
    cursor: pointer;
    display: flex;
    align-items: center;
    padding: 2px;
    transition: color 0.15s;
  }
  .pw-toggle:hover { color: var(--text-secondary); }

  /* Error message */
  .error-msg {
    margin-top: 14px;
    padding: 10px 14px;
    background: var(--red-dim);
    border: 1px solid rgba(255,77,109,0.3);
    border-radius: 4px;
    font-size: 11px;
    font-family: var(--mono);
    color: var(--red);
    letter-spacing: 0.06em;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  /* Submit button */
  .login-btn {
    width: 100%;
    margin-top: 22px;
    padding: 13px;
    background: var(--green-muted);
    border: 1px solid var(--green-dim);
    border-radius: 5px;
    color: var(--green);
    font-size: 13px;
    font-family: var(--mono);
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    position: relative;
    overflow: hidden;
  }

  .login-btn:hover:not(:disabled) {
    background: rgba(46,255,139,0.18);
    border-color: var(--green);
    box-shadow: 0 0 20px rgba(46,255,139,0.15);
  }

  .login-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* Spinner */
  .spinner {
    width: 14px;
    height: 14px;
    border: 2px solid rgba(46,255,139,0.3);
    border-top-color: var(--green);
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }

  @keyframes spin { to { transform: rotate(360deg); } }

  /* Card footer */
  .card-footer {
    padding: 14px 32px 20px;
    border-top: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .footer-note {
    font-size: 9px;
    font-family: var(--mono);
    color: var(--text-dim);
    letter-spacing: 0.08em;
  }

  .footer-link {
    font-size: 10px;
    font-family: var(--mono);
    color: var(--green-dim);
    cursor: pointer;
    letter-spacing: 0.08em;
    transition: color 0.15s;
    text-decoration: none;
  }
  .footer-link:hover { color: var(--green); }

  /* Success state */
  .success-overlay {
    position: absolute;
    inset: 0;
    background: var(--bg-card);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 14px;
    z-index: 10;
    animation: fadeIn 0.3s ease;
  }

  @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

  .success-icon {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: var(--green-muted);
    border: 2px solid var(--green-dim);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--green);
    font-size: 24px;
    box-shadow: 0 0 24px rgba(46,255,139,0.2);
  }

  .success-title {
    font-size: 16px;
    font-weight: 700;
    color: var(--green);
    font-family: var(--mono);
    letter-spacing: 0.12em;
  }

  .success-sub {
    font-size: 10px;
    color: var(--text-secondary);
    font-family: var(--mono);
    letter-spacing: 0.08em;
  }

  /* Back link */
  .back-link {
    position: absolute;
    top: 24px;
    left: 24px;
    z-index: 5;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    font-family: var(--mono);
    color: var(--text-dim);
    cursor: pointer;
    letter-spacing: 0.08em;
    transition: color 0.15s;
  }
  .back-link:hover { color: var(--green); }
`;

export default function Login({ onNavigateToDashboard }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const sessionId = "SES-" + Math.random().toString(36).slice(2, 8).toUpperCase();

  const handleLogin = async () => {
    if (!username.trim() || !password.trim()) {
      setError("All fields are required.");
      return;
    }

    setError("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:5000/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setSuccess(true);
        // Navigate to dashboard after a short delay
        setTimeout(() => {
          if (onNavigateToDashboard) onNavigateToDashboard();
        }, 1800);
      } else {
        setError(data.message || "Invalid credentials. Access denied.");
      }
    } catch (err) {
      setError("Cannot reach server. Check backend connection.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleLogin();
  };

  return (
    <>
      <style>{styles}</style>
      <div className="login-root">
        {/* Background effects */}
        <div className="bg-grid" />
        <div className="bg-glow" />
        <div className="scanline" />
        <div className="corner tl" />
        <div className="corner tr" />
        <div className="corner bl" />
        <div className="corner br" />

        {/* Back to dashboard link */}
        {onNavigateToDashboard && (
          <div className="back-link" onClick={onNavigateToDashboard}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="15 18 9 12 15 6"/>
            </svg>
            Back to Dashboard
          </div>
        )}

        {/* Login card */}
        <div className="login-card">
          <div className="card-accent" />

          {/* Success overlay */}
          {success && (
            <div className="success-overlay">
              <div className="success-icon">✓</div>
              <div className="success-title">ACCESS GRANTED</div>
              <div className="success-sub">Redirecting to dashboard…</div>
            </div>
          )}

          {/* Header */}
          <div className="card-header">
            <div className="logo-mark">
              <div className="logo-icon">⚡</div>
              <span className="logo-label">WATT-WATCH</span>
            </div>
            <div className="card-title">System Authentication</div>
            <div className="card-subtitle">Authorized personnel only</div>
            <div className="session-badge">
              <span className="session-dot" />
              SESSION: {sessionId}
            </div>
          </div>

          {/* Body / Form */}
          <div className="card-body">
            {/* Username */}
            <div className="field">
              <div className="field-label">
                <span className="field-label-dot" />
                Username / ID
              </div>
              <div className="field-input-wrap">
                <span className="field-icon">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                  </svg>
                </span>
                <input
                  className={`field-input${error ? " error" : ""}`}
                  type="text"
                  placeholder="Enter username"
                  value={username}
                  onChange={(e) => { setUsername(e.target.value); setError(""); }}
                  onKeyDown={handleKeyDown}
                  autoComplete="username"
                />
              </div>
            </div>

            {/* Password */}
            <div className="field">
              <div className="field-label">
                <span className="field-label-dot" />
                Password
              </div>
              <div className="field-input-wrap">
                <span className="field-icon">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                  </svg>
                </span>
                <input
                  className={`field-input${error ? " error" : ""}`}
                  type={showPw ? "text" : "password"}
                  placeholder="Enter password"
                  value={password}
                  onChange={(e) => { setPassword(e.target.value); setError(""); }}
                  onKeyDown={handleKeyDown}
                  autoComplete="current-password"
                  style={{ paddingRight: "38px" }}
                />
                <button
                  className="pw-toggle"
                  onClick={() => setShowPw((v) => !v)}
                  tabIndex={-1}
                  type="button"
                >
                  {showPw ? (
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
                      <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
                      <line x1="1" y1="1" x2="23" y2="23"/>
                    </svg>
                  ) : (
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                      <circle cx="12" cy="12" r="3"/>
                    </svg>
                  )}
                </button>
              </div>
            </div>

            {/* Error */}
            {error && (
              <div className="error-msg">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                {error}
              </div>
            )}

            {/* Submit */}
            <button
              className="login-btn"
              onClick={handleLogin}
              disabled={loading}
              type="button"
            >
              {loading ? (
                <>
                  <span className="spinner" />
                  Authenticating…
                </>
              ) : (
                <>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/>
                    <polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/>
                  </svg>
                  Authenticate
                </>
              )}
            </button>
          </div>

          {/* Footer */}
          <div className="card-footer">
            <span className="footer-note">WATT-WATCH v1.0 · Secure Login</span>
            <a className="footer-link" href="#">Forgot Password?</a>
          </div>
        </div>
      </div>
    </>
  );
}
