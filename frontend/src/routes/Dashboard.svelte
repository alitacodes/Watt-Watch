<script>
    import { onMount } from 'svelte';
    
    let currentUser = null;
    let users = [];
    let errorMessage = '';
    let loading = true;

    // Mock Data for UI/UX demonstration
    let wastageData = {
        currentUsage: 4.2,
        detectedWastage: 0.8,
        savings: 12.50,
        efficiency: 82
    };

    let aiDetails = {
        model: 'YOLOv8s',
        status: 'Active',
        inferenceTime: '18ms',
        detections: 2,
        confidence: '94%'
    };

    let redacted = true;

    onMount(async () => {
        try {
            // Get current user info from auth status
            const authRes = await fetch('/api/v1/auth/status');
            if (authRes.ok) {
                const data = await authRes.json();
                currentUser = data;
            } else {
                window.location.href = '/login';
                return;
            }

            // If admin, fetch all users
            if (currentUser.type === 'admin') {
                const usersRes = await fetch('/api/v1/users');
                if (usersRes.ok) {
                    const userData = await usersRes.json();
                    users = userData.users || [];
                }
            }
        } catch (e) {
            errorMessage = 'Failed to connect to server';
        } finally {
            loading = false;
        }

        // Simulate some dynamic data updates for wastage
        const interval = setInterval(() => {
            wastageData.currentUsage = (4.0 + Math.random() * 0.5).toFixed(2);
            wastageData.efficiency = Math.floor(80 + Math.random() * 5);
        }, 3000);

        return () => clearInterval(interval);
    });

    function handleLogout() {
        window.location.href = '/logout';
    }

    async function deleteUser(userid) {
        if (!confirm(`Are you sure you want to delete user ${userid}?`)) return;

        const res = await fetch(`/api/v1/delete_user/${userid}`, { method: 'POST' });
        if (res.ok) {
            users = users.filter(u => u.userid !== userid);
        } else {
            const data = await res.json();
            errorMessage = data.error || 'Failed to delete user';
        }
    }
</script>

<main class="dashboard-wrapper">
    <nav class="sidebar">
        <div class="logo">
            <span class="bolt">⚡</span>
            <h2>Watt-Watch</h2>
        </div>
        
        <div class="nav-links">
            <a href="#dashboard" class="active">
                <i class="icon">📊</i> Dashboard
            </a>
            <a href="#monitoring">
                <i class="icon">📹</i> Monitoring
            </a>
            <a href="#analytics">
                <i class="icon">📈</i> Analytics
            </a>
            {#if currentUser?.type === 'admin'}
                <a href="#admin">
                    <i class="icon">⚙️</i> Admin
                </a>
            {/if}
        </div>

        <div class="user-profile">
            {#if currentUser}
                <div class="avatar">
                    {currentUser.userid[0].toUpperCase()}
                </div>
                <div class="user-meta">
                    <span class="username">{currentUser.userid}</span>
                    <span class="role">{currentUser.type.toUpperCase()}</span>
                </div>
                <button on:click={handleLogout} title="Logout" class="btn-logout">🚪</button>
            {/if}
        </div>
    </nav>

    <div class="main-content">
        {#if loading}
            <div class="loader-container">
                <div class="loader"></div>
                <p>Initializing Watt-Watch Systems...</p>
            </div>
        {:else}
            <header>
                <div class="header-info">
                    <h1>Energy Intelligence Dashboard</h1>
                    <p>Real-time surveillance and consumption tracking</p>
                </div>
                <div class="status-indicators">
                    <div class="status-item">
                        <span class="dot live"></span> System Live
                    </div>
                </div>
            </header>

            <div class="grid-layout">
                <!-- CCTV Monitor SECTION -->
                <div class="card glass cctv-card">
                    <div class="card-header">
                        <h3>CCTV Live Stream</h3>
                        <div class="cctv-actions">
                            {#if currentUser?.type === 'admin'}
                                <button 
                                    class="btn-toggle-redact" 
                                    on:click={() => redacted = !redacted}
                                    class:is-raw={!redacted}
                                >
                                    {redacted ? "🔓 SHOW RAW" : "🔒 REDACT"}
                                </button>
                            {/if}
                            <span class="badge live">REC</span>
                        </div>
                    </div>
                    <div class="video-container">
                        <!-- Connecting to the backend stream endpoint -->
                        <img 
                            src={redacted 
                                ? "http://127.0.0.1:5000/video/127.0.0.1/5001/" 
                                : "http://127.0.0.1:5000/video/127.0.0.1/5001/admin"} 
                            alt="CCTV Feed" 
                            class="cctv-feed"
                            on:error={(e) => e.target.src = 'https://placehold.co/640x360/1a1d27/50fa7b?text=Searching+for+Camera+Signal...'}
                        />
                        <div class="stream-overlay">
                            <span class="timestamp">{new Date().toLocaleTimeString()}</span>
                            <span class="cam-label">CAM_01 - FRONT_DESK</span>
                        </div>
                    </div>
                </div>

                <!-- ELECTRICITY WASTEAGE SECTION -->
                <div class="card glass metrics-card">
                    <div class="card-header">
                        <h3>Electricity Usage</h3>
                        <span class="badge usage">kW/h</span>
                    </div>
                    <div class="metrics-grid">
                        <div class="metric-item">
                            <span class="label">Current Load</span>
                            <span class="value">{wastageData.currentUsage} <small>kW</small></span>
                            <div class="progress-bg"><div class="progress-bar" style="width: 65%"></div></div>
                        </div>
                        <div class="metric-item highlight">
                            <span class="label">Wastage Detected</span>
                            <span class="value warning">{wastageData.detectedWastage} <small>kW</small></span>
                            <span class="subtext">AI identified idle devices</span>
                        </div>
                        <div class="metric-item">
                            <span class="label">Est. Savings</span>
                            <span class="value success">${wastageData.savings}</span>
                            <span class="subtext">Monthly projection</span>
                        </div>
                        <div class="metric-item">
                            <span class="label">Efficiency Score</span>
                            <span class="value">{wastageData.efficiency}%</span>
                            <div class="efficiency-ring" style="--percent: {wastageData.efficiency}">
                                <svg width="60" height="60">
                                    <circle cx="30" cy="30" r="25"></circle>
                                    <circle cx="30" cy="30" r="25" class="fg"></circle>
                                </svg>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- AI CONTROLLER DETAILS SECTION -->
                <div class="card glass ai-card">
                    <div class="card-header">
                        <h3>AI Controller Details</h3>
                        <span class="badge ai">YOLOv8</span>
                    </div>
                    <div class="ai-stats">
                        <div class="ai-stat">
                            <span>Model Engine</span>
                            <span>{aiDetails.model}</span>
                        </div>
                        <div class="ai-stat">
                            <span>System Status</span>
                            <span class="success">{aiDetails.status}</span>
                        </div>
                        <div class="ai-stat">
                            <span>Inference Latency</span>
                            <span>{aiDetails.inferenceTime}</span>
                        </div>
                        <div class="ai-stat">
                            <span>Active Detections</span>
                            <span class="pulse-text">{aiDetails.detections} Persons</span>
                        </div>
                        <div class="ai-stat">
                            <span>Mean Confidence</span>
                            <span>{aiDetails.confidence}</span>
                        </div>
                    </div>
                    <div class="model-visual">
                        <div class="scanner"></div>
                        <span>Neural Network Active</span>
                    </div>
                </div>

                <!-- ADMIN SECTION -->
                {#if currentUser?.type === 'admin'}
                    <div class="card glass admin-card full-width">
                        <div class="card-header">
                            <h3>User Management</h3>
                        </div>
                        <div class="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>User ID</th>
                                        <th>Rank</th>
                                        <th>Status</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {#each users as user}
                                        <tr>
                                            <td>{user.userid}</td>
                                            <td>
                                                <span class="rank-badge" class:admin={user.type === 'admin'}>
                                                    {user.type.toUpperCase()}
                                                </span>
                                            </td>
                                            <td><span class="dot online"></span> Online</td>
                                            <td>
                                                {#if user.userid !== currentUser.userid}
                                                    <button on:click={() => deleteUser(user.userid)} class="btn-delete">REMOVE</button>
                                                {/if}
                                            </td>
                                        </tr>
                                    {/each}
                                </tbody>
                            </table>
                        </div>
                    </div>
                {/if}
            </div>
        {/if}
    </div>
</main>

<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

    :global(body) {
        margin: 0;
        padding: 0;
        font-family: 'Outfit', sans-serif;
        background: #090b10;
        color: #e2e8f0;
        overflow: hidden;
    }

    .dashboard-wrapper {
        display: flex;
        height: 100vh;
        width: 100vw;
    }

    /* Sidebar Styles */
    .sidebar {
        width: 260px;
        background: rgba(15, 17, 26, 0.95);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        display: flex;
        flex-direction: column;
        padding: 2rem 1.5rem;
    }

    .logo {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 3rem;
    }

    .bolt {
        font-size: 1.5rem;
        background: linear-gradient(135deg, #50fa7b, #8be9fd);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .logo h2 {
        margin: 0;
        font-size: 1.4rem;
        letter-spacing: -1px;
    }

    .nav-links {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        flex: 1;
    }

    .nav-links a {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
        text-decoration: none;
        color: #94a3b8;
        border-radius: 12px;
        transition: all 0.3s ease;
    }

    .nav-links a:hover, .nav-links a.active {
        background: rgba(80, 250, 123, 0.1);
        color: #50fa7b;
    }

    .user-profile {
        margin-top: auto;
        background: rgba(255, 255, 255, 0.03);
        padding: 1rem;
        border-radius: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .avatar {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #bd93f9, #ff79c6);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
    }

    .user-meta {
        display: flex;
        flex-direction: column;
        flex: 1;
    }

    .username {
        font-weight: 600;
        font-size: 0.9rem;
    }

    .role {
        font-size: 0.7rem;
        color: #94a3b8;
    }

    .btn-logout {
        background: transparent;
        border: none;
        cursor: pointer;
        font-size: 1.2rem;
        opacity: 0.6;
        transition: opacity 0.3s;
    }

    .btn-logout:hover {
        opacity: 1;
    }

    /* Main Content */
    .main-content {
        flex: 1;
        padding: 2rem 3rem;
        overflow-y: auto;
        background: radial-gradient(circle at top right, rgba(80, 250, 123, 0.05), transparent);
    }

    header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 2.5rem;
    }

    header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(to right, #fff, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    header p {
        margin: 0.5rem 0 0 0;
        color: #94a3b8;
    }

    .status-item {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(80, 250, 123, 0.1);
        color: #50fa7b;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }

    .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }

    .dot.live {
        background: #50fa7b;
        box-shadow: 0 0 10px #50fa7b;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.5); opacity: 0.5; }
        100% { transform: scale(1); opacity: 1; }
    }

    /* Grid Layout */
    .grid-layout {
        display: grid;
        grid-template-columns: 2fr 1fr;
        grid-template-rows: auto auto;
        gap: 1.5rem;
    }

    .card {
        padding: 1.5rem;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }

    .glass {
        background: rgba(26, 29, 39, 0.4);
        backdrop-filter: blur(12px);
    }

    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .card-header h3 {
        margin: 0;
        font-size: 1.1rem;
        color: #fff;
    }

    .cctv-actions {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .btn-toggle-redact {
        background: rgba(139, 233, 253, 0.1);
        color: #8be9fd;
        border: 1px solid rgba(139, 233, 253, 0.2);
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 0.7rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .btn-toggle-redact:hover {
        background: #8be9fd;
        color: #000;
        transform: translateY(-1px);
    }

    .btn-toggle-redact.is-raw {
        background: rgba(255, 184, 108, 0.1);
        color: #ffb86c;
        border-color: rgba(255, 184, 108, 0.2);
    }

    .btn-toggle-redact.is-raw:hover {
        background: #ffb86c;
        color: #000;
    }

    .badge {
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.7rem;
        font-weight: 800;
    }

    .badge.live { background: #ff5555; color: #fff; }
    .badge.usage { background: #bd93f9; color: #fff; }
    .badge.ai { background: #8be9fd; color: #000; }

    /* CCTV Styles */
    .video-container {
        position: relative;
        border-radius: 16px;
        overflow: hidden;
        aspect-ratio: 16/9;
        background: #000;
    }

    .cctv-feed {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .stream-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        padding: 1rem;
        display: flex;
        justify-content: space-between;
        background: linear-gradient(to bottom, rgba(0,0,0,0.7), transparent);
        font-family: monospace;
        font-size: 0.8rem;
        color: #50fa7b;
    }

    /* Metrics Styles */
    .metrics-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
    }

    .metric-item {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .metric-item .label {
        font-size: 0.8rem;
        color: #94a3b8;
    }

    .metric-item .value {
        font-size: 1.8rem;
        font-weight: 700;
    }

    .value.warning { color: #ffb86c; }
    .value.success { color: #50fa7b; }

    .progress-bg {
        height: 6px;
        background: rgba(255,255,255,0.05);
        border-radius: 3px;
    }

    .progress-bar {
        height: 100%;
        background: #50fa7b;
        border-radius: 3px;
    }

    .subtext {
        font-size: 0.7rem;
        color: #64748b;
    }

    /* Efficiency Ring */
    .efficiency-ring {
        position: relative;
        width: 60px;
        height: 60px;
    }

    .efficiency-ring circle {
        fill: none;
        stroke: rgba(255,255,255,0.05);
        stroke-width: 5;
    }

    .efficiency-ring .fg {
        stroke: #50fa7b;
        stroke-dasharray: 157;
        stroke-dashoffset: calc(157 - (157 * var(--percent)) / 100);
        stroke-linecap: round;
        transition: stroke-dashoffset 1s ease-out;
    }

    /* AI Stats */
    .ai-stats {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }

    .ai-stat {
        display: flex;
        justify-content: space-between;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }

    .ai-stat label { font-size: 0.8rem; color: #94a3b8; }
    .ai-stat span { font-weight: 600; font-size: 0.9rem; }

    .pulse-text {
        color: #8be9fd;
        animation: textPulse 2s infinite;
    }

    @keyframes textPulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }

    .model-visual {
        margin-top: auto;
        padding: 1.5rem;
        background: rgba(0,0,0,0.2);
        border-radius: 16px;
        position: relative;
        overflow: hidden;
        text-align: center;
    }

    .scanner {
        height: 2px;
        background: #8be9fd;
        width: 100%;
        position: absolute;
        top: 0;
        left: 0;
        animation: scan 3s linear infinite;
        box-shadow: 0 0 15px #8be9fd;
    }

    @keyframes scan {
        0% { top: 0; }
        100% { top: 100%; }
    }

    /* Admin Table */
    .full-width { grid-column: span 2; }

    .table-container {
        overflow-x: auto;
    }

    table {
        width: 100%;
        border-collapse: collapse;
    }

    th {
        text-align: left;
        padding: 12px;
        color: #94a3b8;
        font-weight: 500;
        font-size: 0.85rem;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }

    td {
        padding: 16px 12px;
        font-size: 0.9rem;
    }

    .rank-badge {
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.7rem;
        background: rgba(139, 233, 253, 0.1);
        color: #8be9fd;
    }

    .rank-badge.admin {
        background: rgba(255, 85, 85, 0.1);
        color: #ff5555;
    }

    .dot.online { background: #50fa7b; }

    .btn-delete {
        background: rgba(255, 85, 85, 0.1);
        color: #ff5555;
        border: 1px solid rgba(255, 85, 85, 0.2);
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 0.7rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s;
    }

    .btn-delete:hover {
        background: #ff5555;
        color: #fff;
    }

    /* Loader */
    .loader-container {
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 1.5rem;
    }

    .loader {
        width: 48px;
        height: 48px;
        border: 3px solid rgba(80, 250, 123, 0.1);
        border-radius: 50%;
        border-top-color: #50fa7b;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    /* Responsive */
    @media (max-width: 1100px) {
        .grid-layout { grid-template-columns: 1fr; }
        .full-width { grid-column: span 1; }
    }
</style>