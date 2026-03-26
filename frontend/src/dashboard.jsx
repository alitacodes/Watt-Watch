import { useState } from "react";

const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: #0a0e0f;
    font-family: 'Rajdhani', sans-serif;
    color: #c8d8d0;
  }

  :root {
    --bg-primary: #0a0e0f;
    --bg-secondary: #111618;
    --bg-card: #141a1c;
    --bg-card2: #0f1416;
    --border: #1e2a2d;
    --border-bright: #243035;
    --green: #2eff8b;
    --green-dim: #1a9954;
    --green-muted: rgba(46,255,139,0.12);
    --orange: #ff8c42;
    --orange-dim: rgba(255,140,66,0.15);
    --red: #ff4d6d;
    --red-dim: rgba(255,77,109,0.15);
    --yellow: #ffc542;
    --yellow-dim: rgba(255,197,66,0.15);
    --teal: #2ee8c8;
    --teal-dim: rgba(46,232,200,0.1);
    --text-primary: #d4e8e0;
    --text-secondary: #7a9a90;
    --text-dim: #4a6a62;
    --mono: 'Share Tech Mono', monospace;
  }

  .app {
    display: flex;
    height: 100vh;
    overflow: hidden;
    background: var(--bg-primary);
  }

  /* SIDEBAR */
  .sidebar {
    width: 210px;
    min-width: 210px;
    background: var(--bg-secondary);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    padding: 0;
  }

  .sidebar-logo {
    padding: 20px 20px 16px;
    border-bottom: 1px solid var(--border);
  }

  .logo-text {
    font-family: var(--mono);
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: var(--green);
  }

  .logo-sub {
    font-size: 11px;
    color: var(--text-secondary);
    margin-top: 4px;
    letter-spacing: 0.05em;
  }

  .sidebar-user {
    padding: 16px 20px;
    border-bottom: 1px solid var(--border);
  }

  .user-name {
    font-size: 14px;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: 0.04em;
  }

  .user-status {
    font-size: 11px;
    color: var(--green-dim);
    margin-top: 2px;
    font-family: var(--mono);
    letter-spacing: 0.05em;
  }

  .sidebar-nav {
    padding: 12px 0;
    flex: 1;
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 600;
    color: var(--text-secondary);
    cursor: pointer;
    letter-spacing: 0.05em;
    transition: all 0.15s;
    border-left: 2px solid transparent;
  }

  .nav-item:hover { color: var(--text-primary); background: rgba(46,255,139,0.04); }

  .nav-item.active {
    color: var(--green);
    background: var(--green-muted);
    border-left: 2px solid var(--green);
  }

  /* Login nav item special styling */
  .nav-item.login-item {
    color: var(--text-dim);
    border-top: 1px solid var(--border);
    margin-top: auto;
  }

  .nav-item.login-item:hover {
    color: var(--green);
    background: var(--green-muted);
  }

  .nav-icon {
    width: 16px;
    height: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0.8;
  }

  .efficiency-box {
    margin: 16px;
    padding: 14px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 6px;
  }

  .eff-label {
    font-size: 10px;
    color: var(--text-dim);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-family: var(--mono);
    margin-bottom: 6px;
  }

  .eff-value {
    font-size: 26px;
    font-weight: 700;
    color: var(--green);
    font-family: var(--mono);
    line-height: 1;
  }

  .eff-delta {
    font-size: 11px;
    color: var(--green-dim);
    margin-top: 4px;
  }

  /* MAIN */
  .main {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    display: flex;
    flex-direction: column;
  }

  /* TOPBAR */
  .topbar {
    height: 48px;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
    flex-shrink: 0;
  }

  .topbar-left {
    display: flex;
    gap: 16px;
    align-items: center;
  }

  .status-badge {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    font-family: var(--mono);
    letter-spacing: 0.06em;
    color: var(--text-secondary);
  }

  .dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    animation: pulse 2s infinite;
  }

  .dot.green { background: var(--green); box-shadow: 0 0 6px var(--green); }
  .dot.orange { background: var(--orange); box-shadow: 0 0 6px var(--orange); animation: none; }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
  }

  .topbar-right {
    display: flex;
    gap: 16px;
    align-items: center;
  }

  .topbar-icon {
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-secondary);
    cursor: pointer;
    border-radius: 4px;
    transition: all 0.15s;
  }
  .topbar-icon:hover { background: var(--bg-card); color: var(--text-primary); }

  /* CONTENT */
  .content {
    flex: 1;
    display: flex;
    gap: 0;
  }

  .content-left {
    flex: 1;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    overflow: hidden;
  }

  .content-right {
    width: 250px;
    min-width: 250px;
    background: var(--bg-secondary);
    border-left: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    overflow-y: auto;
  }

  /* STAT CARDS */
  .stat-cards {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
  }

  .stat-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 16px 18px;
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    transition: border-color 0.2s;
  }

  .stat-card:hover { border-color: var(--border-bright); }

  .stat-label {
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-dim);
    font-family: var(--mono);
    margin-bottom: 8px;
  }

  .stat-value {
    font-size: 30px;
    font-weight: 700;
    font-family: var(--mono);
    line-height: 1;
  }

  .stat-value.green { color: var(--green); }
  .stat-value.orange { color: var(--orange); }
  .stat-value.yellow { color: var(--yellow); }

  .stat-sub {
    font-size: 11px;
    color: var(--text-secondary);
    margin-top: 4px;
    letter-spacing: 0.03em;
  }

  .stat-icon {
    width: 36px;
    height: 36px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
  }

  .stat-icon.green { background: var(--green-muted); color: var(--green); }
  .stat-icon.orange { background: var(--orange-dim); color: var(--orange); }
  .stat-icon.yellow { background: var(--yellow-dim); color: var(--yellow); }

  /* VIDEO FEED */
  .video-section {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 6px;
    overflow: hidden;
    flex: 1;
  }

  .video-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 16px;
    border-bottom: 1px solid var(--border);
  }

  .video-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    font-family: var(--mono);
    letter-spacing: 0.08em;
    color: var(--text-primary);
  }

  .cam-icon {
    color: var(--green);
  }

  .hd-badge {
    background: var(--green-muted);
    border: 1px solid var(--green-dim);
    color: var(--green);
    font-size: 9px;
    font-family: var(--mono);
    letter-spacing: 0.1em;
    padding: 2px 7px;
    border-radius: 3px;
  }

  .video-body {
    position: relative;
    background: #070d0f;
    min-height: 240px;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
  }

  .video-grid {
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(46,255,139,0.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(46,255,139,0.04) 1px, transparent 1px);
    background-size: 40px 40px;
  }

  .video-privacy-text {
    font-family: var(--mono);
    font-size: 11px;
    letter-spacing: 0.18em;
    color: rgba(46,255,139,0.3);
    text-transform: uppercase;
    z-index: 1;
  }

  .detection-box {
    position: absolute;
    top: 40px;
    left: 38%;
    z-index: 3;
  }

  .detection-frame {
    width: 120px;
    height: 110px;
    border: 1.5px solid var(--red);
    position: relative;
    border-radius: 2px;
  }

  .detection-frame::before, .detection-frame::after {
    content: '';
    position: absolute;
    width: 10px;
    height: 10px;
    border-color: var(--red);
    border-style: solid;
  }
  .detection-frame::before { top: -1px; left: -1px; border-width: 2px 0 0 2px; }
  .detection-frame::after { bottom: -1px; right: -1px; border-width: 0 2px 2px 0; }

  .detection-label {
    position: absolute;
    top: -26px;
    left: 0;
    background: rgba(255,77,109,0.15);
    border: 1px solid var(--red);
    padding: 3px 8px;
    font-size: 9px;
    font-family: var(--mono);
    color: var(--red);
    letter-spacing: 0.06em;
    white-space: nowrap;
    border-radius: 2px;
  }

  .detection-id {
    position: absolute;
    top: -26px;
    left: -30px;
    background: var(--bg-card2);
    border: 1px solid var(--border);
    padding: 3px 6px;
    font-size: 9px;
    font-family: var(--mono);
    color: var(--text-dim);
    border-radius: 2px;
  }

  /* Silhouette */
  .silhouette {
    position: absolute;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    opacity: 0.22;
    z-index: 2;
  }

  .sil-head {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: var(--teal);
  }

  .sil-body {
    width: 36px;
    height: 48px;
    background: var(--teal);
    border-radius: 4px 4px 0 0;
    clip-path: polygon(10% 0%, 90% 0%, 100% 100%, 0% 100%);
  }

  /* TABLE */
  .table-section {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 6px;
    overflow: hidden;
  }

  .table-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 18px;
    border-bottom: 1px solid var(--border);
  }

  .table-title {
    font-size: 11px;
    font-family: var(--mono);
    letter-spacing: 0.1em;
    color: var(--text-primary);
    text-transform: uppercase;
  }

  .view-all {
    font-size: 11px;
    color: var(--green);
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 4px;
    letter-spacing: 0.05em;
    font-family: var(--mono);
  }

  .table-wrap table {
    width: 100%;
    border-collapse: collapse;
  }

  .table-wrap th {
    font-size: 9px;
    font-family: var(--mono);
    letter-spacing: 0.12em;
    color: var(--text-dim);
    text-transform: uppercase;
    padding: 8px 18px;
    text-align: left;
    background: var(--bg-card2);
    border-bottom: 1px solid var(--border);
  }

  .table-wrap td {
    padding: 11px 18px;
    font-size: 13px;
    color: var(--text-primary);
    border-bottom: 1px solid var(--border);
    font-weight: 500;
  }

  .table-wrap tr:last-child td { border-bottom: none; }
  .table-wrap tr:hover td { background: rgba(46,255,139,0.02); }

  .appliance-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--green);
    display: inline-block;
    margin-right: 6px;
    box-shadow: 0 0 5px var(--green);
  }

  .status-pill {
    font-size: 9px;
    font-family: var(--mono);
    letter-spacing: 0.09em;
    padding: 3px 9px;
    border-radius: 3px;
    font-weight: 700;
    display: inline-block;
  }

  .pill-waste { background: var(--red-dim); color: var(--red); border: 1px solid rgba(255,77,109,0.3); }
  .pill-ok { background: var(--green-muted); color: var(--green); border: 1px solid rgba(46,255,139,0.3); }
  .pill-pending { background: var(--yellow-dim); color: var(--yellow); border: 1px solid rgba(255,197,66,0.3); }

  /* RIGHT PANEL */
  .panel-section {
    border-bottom: 1px solid var(--border);
  }

  .panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px 8px;
  }

  .panel-title {
    font-size: 10px;
    font-family: var(--mono);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-secondary);
  }

  /* AI Logic Stream */
  .logic-item {
    padding: 10px 16px;
    border-left: 2px solid transparent;
    border-bottom: 1px solid var(--border);
    cursor: pointer;
    transition: all 0.15s;
  }

  .logic-item:last-child { border-bottom: none; }
  .logic-item:hover { background: rgba(46,255,139,0.03); }
  .logic-item.active-room { border-left-color: var(--green); }

  .logic-room-id {
    font-size: 9px;
    font-family: var(--mono);
    color: var(--text-dim);
    letter-spacing: 0.08em;
    margin-bottom: 3px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .logic-ppl {
    font-size: 9px;
    font-family: var(--mono);
    color: var(--text-dim);
  }

  .logic-appliance {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: 0.04em;
    margin-bottom: 3px;
  }

  .logic-decision {
    font-size: 9px;
    font-family: var(--mono);
    letter-spacing: 0.07em;
    font-weight: 700;
  }

  .dec-waste { color: var(--red); }
  .dec-ok { color: var(--green); }
  .dec-keep { color: var(--yellow); }
  .dec-terminate { color: var(--orange); }

  /* Alerts */
  .alert-item {
    padding: 11px 16px;
    border-bottom: 1px solid var(--border);
    display: flex;
    gap: 10px;
    align-items: flex-start;
  }

  .alert-item:last-child { border-bottom: none; }

  .alert-icon {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    flex-shrink: 0;
    margin-top: 1px;
  }

  .alert-icon.red { background: var(--red-dim); color: var(--red); }
  .alert-icon.yellow { background: var(--yellow-dim); color: var(--yellow); }
  .alert-icon.green { background: var(--green-muted); color: var(--green); }

  .alert-title {
    font-size: 12px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 3px;
    letter-spacing: 0.03em;
  }

  .alert-desc {
    font-size: 10px;
    color: var(--text-secondary);
    line-height: 1.4;
    font-family: 'Inter', sans-serif;
    margin-bottom: 3px;
  }

  .alert-tag {
    font-size: 9px;
    font-family: var(--mono);
    letter-spacing: 0.08em;
    padding: 1px 6px;
    border-radius: 2px;
    display: inline-block;
    margin-top: 2px;
  }

  .alert-tag.red { background: var(--red-dim); color: var(--red); }
  .alert-tag.yellow { background: var(--yellow-dim); color: var(--yellow); }
  .alert-tag.green { background: var(--green-muted); color: var(--green); }

  .clear-btn {
    margin: 12px 16px;
    width: calc(100% - 32px);
    padding: 9px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 4px;
    color: var(--text-secondary);
    font-size: 11px;
    font-family: var(--mono);
    letter-spacing: 0.08em;
    cursor: pointer;
    text-align: center;
    transition: all 0.15s;
  }

  .clear-btn:hover {
    border-color: var(--border-bright);
    color: var(--text-primary);
    background: var(--bg-card2);
  }

  /* Savings */
  .savings-box {
    padding: 16px;
    background: linear-gradient(135deg, #0f1d1a 0%, #0a1412 100%);
    border-top: 1px solid var(--border);
  }

  .savings-label {
    font-size: 9px;
    font-family: var(--mono);
    letter-spacing: 0.14em;
    color: var(--green-dim);
    text-transform: uppercase;
    margin-bottom: 8px;
  }

  .savings-value {
    font-size: 28px;
    font-family: var(--mono);
    font-weight: 700;
    color: var(--green);
    line-height: 1;
  }

  .savings-currency {
    font-size: 13px;
    color: var(--green-dim);
    margin-left: 4px;
  }

  .savings-note {
    font-size: 10px;
    color: var(--text-secondary);
    margin-top: 8px;
    font-family: 'Inter', sans-serif;
    line-height: 1.4;
  }

  .savings-note strong { color: var(--green); font-weight: 600; }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

  /* NAV DIVIDER */
  .nav-divider {
    height: 1px;
    background: var(--border);
    margin: 6px 0;
  }
`;

const rooms = [
  { name: "Room 101", people: 0, appliance: "AC On", status: "WASTE DETECTED", pillClass: "pill-waste" },
  { name: "Room 102", people: 3, appliance: "AC On", status: "OPERATIONAL OK", pillClass: "pill-ok" },
  { name: "Conference A", people: 12, appliance: "Full Load", status: "OPERATIONAL OK", pillClass: "pill-ok" },
  { name: "Room 204", people: 1, appliance: "Lights Standby", status: "PENDING LOGIC", pillClass: "pill-pending" },
];

const logicStream = [
  { room: "101", id: "9921", appliance: "AC Status: ACTIVE", ppl: 0, decision: "WASTE DETECTED", decClass: "dec-waste", active: true },
  { room: "102", id: "9924", appliance: "AC Status: ACTIVE", ppl: 3, decision: "OK (IN USE)", decClass: "dec-ok" },
  { room: "204", id: "9930", appliance: "LIGHTS: STANDBY", ppl: 1, decision: "KEEP ACTIVE", decClass: "dec-keep" },
  { room: "305", id: "9942", appliance: "PROJECTOR: ON", ppl: 0, decision: "TERMINATE POWER", decClass: "dec-terminate" },
];

const alerts = [
  {
    type: "red",
    icon: "⚡",
    title: "Room 101 wasting energy",
    desc: "AC running for 45m with 0 occupancy detected.",
    tag: "2.4kwh leaked",
    tagType: "red",
  },
  {
    type: "yellow",
    icon: "⚠",
    title: "Room 204 low activity",
    desc: "Single occupant detected. AC remains active per policy.",
    tag: "Status: Monitoring",
    tagType: "yellow",
  },
  {
    type: "green",
    icon: "✓",
    title: "HVAC Optimization Complete",
    desc: "Zone 4 (Floors 10-12) successfully synchronized.",
    tag: "Eff: +4.2%",
    tagType: "green",
  },
];

export default function WattWatchDashboard({ onNavigateToLogin }) {
  const [activeNav, setActiveNav] = useState("Dashboard");

  const handleNavClick = (label) => {
    if (label === "Login") {
      if (onNavigateToLogin) onNavigateToLogin();
      return;
    }
    setActiveNav(label);
  };

  return (
    <>
      <style>{styles}</style>
      <div className="app">
        {/* SIDEBAR */}
        <aside className="sidebar">
          <div className="sidebar-logo">
            <div className="logo-text">WATT-WATCH</div>
          </div>
          <div className="sidebar-user">
            <div className="user-name">System Admin</div>
            <div className="user-status">Monitoring Active</div>
          </div>
          <nav className="sidebar-nav">
            {[
              { label: "Dashboard", icon: "⊞" },
              { label: "Rooms", icon: "▣" },
              { label: "History", icon: "◷" },
              { label: "Settings", icon: "⚙" },
            ].map(({ label, icon }) => (
              <div
                key={label}
                className={`nav-item${activeNav === label ? " active" : ""}`}
                onClick={() => handleNavClick(label)}
              >
                <span className="nav-icon">{icon}</span>
                {label}
              </div>
            ))}

            {/* Divider before Login */}
            <div className="nav-divider" style={{ marginTop: "auto" }} />

            {/* Login Nav Item */}
            <div
              className="nav-item login-item"
              onClick={() => handleNavClick("Login")}
            >
              <span className="nav-icon">
                {/* Lock icon */}
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
              </span>
              Login
            </div>
          </nav>
          <div className="efficiency-box">
            <div className="eff-label">Efficiency Rating</div>
            <div className="eff-value">92%</div>
            <div className="eff-delta">+2.4%</div>
          </div>
        </aside>

        {/* MAIN */}
        <div className="main">
          {/* TOPBAR */}
          <div className="topbar">
            <div className="topbar-left">
              <div className="status-badge">
                <span className="dot green" /> System Online
              </div>
              <div className="status-badge">
                <span className="dot orange" /> Camera Active
              </div>
            </div>
            <div className="topbar-right">
              <div className="topbar-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="3"/><circle cx="12" cy="12" r="9"/>
                  <line x1="12" y1="3" x2="12" y2="1"/><line x1="12" y1="23" x2="12" y2="21"/>
                </svg>
              </div>
              <div className="topbar-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M23 7l-7 5 7 5V7z"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
                </svg>
              </div>
              <div className="topbar-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
                </svg>
              </div>
            </div>
          </div>

          {/* CONTENT */}
          <div className="content">
            <div className="content-left">
              {/* STAT CARDS */}
              <div className="stat-cards">
                <div className="stat-card">
                  <div>
                    <div className="stat-label">Total Rooms</div>
                    <div className="stat-value green">24</div>
                    <div className="stat-sub">Active units</div>
                  </div>
                  <div className="stat-icon green">▣</div>
                </div>
                <div className="stat-card">
                  <div>
                    <div className="stat-label">Waste Detected</div>
                    <div className="stat-value orange">5</div>
                    <div className="stat-sub">Rooms flagged</div>
                  </div>
                  <div className="stat-icon orange">⚠</div>
                </div>
                <div className="stat-card">
                  <div>
                    <div className="stat-label">Energy Waste</div>
                    <div className="stat-value yellow">124.5</div>
                    <div className="stat-sub">kWh Total</div>
                  </div>
                  <div className="stat-icon yellow">⚡</div>
                </div>
              </div>

              {/* VIDEO FEED */}
              <div className="video-section">
                <div className="video-header">
                  <div className="video-title">
                    <span className="cam-icon">▶</span>
                    Live Video Feed – Privacy Mode Enabled
                  </div>
                  <div className="hd-badge">HD 1080P</div>
                </div>
                <div className="video-body">
                  <div className="video-grid" />
                  <div className="video-privacy-text">Privacy Mask Active</div>

                  {/* Silhouette */}
                  <div className="silhouette">
                    <div className="sil-head" />
                    <div className="sil-body" />
                  </div>

                  {/* Detection box */}
                  <div className="detection-box">
                    <div className="detection-id">ID: 40</div>
                    <div className="detection-label">APPLIANCE: AC_01 | STATUS: WASTE</div>
                    <div className="detection-frame" />
                  </div>
                </div>
              </div>

              {/* TABLE */}
              <div className="table-section">
                <div className="table-header">
                  <div className="table-title">Room Status Overview</div>
                  <div className="view-all">View All Rooms →</div>
                </div>
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Room Name</th>
                        <th>Person Count</th>
                        <th>Appliance Status</th>
                        <th>Final Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {rooms.map((r) => (
                        <tr key={r.name}>
                          <td>{r.name}</td>
                          <td>{r.people}</td>
                          <td>
                            <span className="appliance-dot" />
                            {r.appliance}
                          </td>
                          <td>
                            <span className={`status-pill ${r.pillClass}`}>{r.status}</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            {/* RIGHT PANEL */}
            <aside className="content-right">
              {/* AI Logic Stream */}
              <div className="panel-section">
                <div className="panel-header">
                  <div className="panel-title">AI Logic Stream</div>
                  <span style={{ color: "var(--text-dim)", fontSize: 14, cursor: "pointer" }}>⊕</span>
                </div>
                {logicStream.map((item) => (
                  <div key={item.id} className={`logic-item${item.active ? " active-room" : ""}`}>
                    <div className="logic-room-id">
                      <span>ROOM: {item.room} | ID: #{item.id}</span>
                      <span className="logic-ppl">Ppl: {item.ppl}</span>
                    </div>
                    <div className="logic-appliance">{item.appliance}</div>
                    <div className={`logic-decision ${item.decClass}`}>DECISION: {item.decision}</div>
                  </div>
                ))}
              </div>

              {/* System Alerts */}
              <div className="panel-section">
                <div className="panel-header">
                  <div className="panel-title">System Alerts</div>
                </div>
                {alerts.map((a, i) => (
                  <div key={i} className="alert-item">
                    <div className={`alert-icon ${a.type}`}>{a.icon}</div>
                    <div>
                      <div className="alert-title">{a.title}</div>
                      <div className="alert-desc">{a.desc}</div>
                      <span className={`alert-tag ${a.tagType}`}>{a.tag}</span>
                    </div>
                  </div>
                ))}
                <button className="clear-btn">Clear All Notifications</button>
              </div>

              {/* Savings */}
              <div className="savings-box">
                <div className="savings-label">Total Savings Today</div>
                <div>
                  <span className="savings-value">$42.80</span>
                  <span className="savings-currency">USD</span>
                </div>
                <div className="savings-note">
                  Estimated carbon footprint reduction equivalent to{" "}
                  <strong>14.2kg CO2</strong>.
                </div>
              </div>
            </aside>
          </div>
        </div>
      </div>
    </>
  );
}
