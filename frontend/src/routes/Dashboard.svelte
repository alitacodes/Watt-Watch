<script>
    import { onMount, onDestroy } from 'svelte';
    import Sidebar from '../components/Sidebar.svelte';

    let currentUser = null;
    let errorMessage = '';
    let loading = true;
    let showRoomPanel = true;
    let redacted = true;
    let timeStr = '';
    let clockInterval;

    let stats = { totalRooms: 0, wasteKw: 0, totalKw: 0 };
    let rooms = [];

    function tick() {
        timeStr = new Date().toLocaleTimeString('en-US', { hour12: false });
    }

    onMount(async () => {
        tick();
        clockInterval = setInterval(tick, 1000);

        try {
            const authRes = await fetch('/api/v1/auth/status');
            if (!authRes.ok) { window.location.href = '/login'; return; }
            currentUser = await authRes.json();

            const [statsRes, roomsRes] = await Promise.all([
                fetch('/api/v1/stats'),
                fetch('/api/v1/rooms'),
            ]);
            if (statsRes.ok)  stats = await statsRes.json();
            if (roomsRes.ok) {
                const data = await roomsRes.json();
                rooms = data.rooms || [];
            }
        } catch (e) {
            console.error('Dashboard init error', e);
            errorMessage = 'Failed to connect to server';
        } finally {
            loading = false;
        }
    });

    onDestroy(() => clearInterval(clockInterval));

    $: videoSrc = redacted
        ? 'http://127.0.0.1:5000/video/127.0.0.1/5001/'
        : 'http://127.0.0.1:5000/video/127.0.0.1/5001/admin';

    function statusColor(s = '') {
        const v = s.toLowerCase();
        if (v === 'occupied') return '#50fa7b';
        if (v === 'vacant')   return '#6272a4';
        return '#ffb86c'; 
    }
</script>

<div class="dashboard-wrapper">
    <Sidebar active="dashboard" {currentUser} />

    <div class="main-content">
        {#if loading}
            <div class="loader-wrap">
                <div class="loader"></div>
                <p>Initializing Watt-Watch…</p>
            </div>
        {:else}
            <header class="page-header">
                <div>
                    <h1>Energy Intelligence Dashboard</h1>
                    <p class="subtitle">Real-time surveillance &amp; consumption tracking</p>
                </div>
                <div class="header-right">
                    <div class="live-badge"><span class="dot-live"></span>System Live</div>
                </div>
            </header>

            <div class="top-stats">
                <div class="stat-card glass" id="stat-rooms">
                    <span class="stat-label">Total Rooms</span>
                    <strong class="stat-val">{stats.totalRooms}</strong>
                </div>
                <div class="stat-card glass" id="stat-waste">
                    <span class="stat-label">Waste Detected</span>
                    <strong class="stat-val warning">{stats.wasteKw} <small>kW</small></strong>
                </div>
                <div class="stat-card glass" id="stat-energy">
                    <span class="stat-label">Energy Usage</span>
                    <strong class="stat-val">{stats.totalKw} <small>kW</small></strong>
                </div>
                <button class="notif-btn" id="btn-notifications" title="Notifications">🔔</button>
            </div>

            <div class="dashboard-grid" class:panel-open={showRoomPanel}>

                <div class="card glass cctv-card">
                    <div class="card-header">
                        <h3>CCTV Live Stream</h3>
                        <div class="cctv-actions">
                            {#if currentUser?.type === 'admin'}
                                <button
                                    id="btn-redact-toggle"
                                    class="btn-pill"
                                    class:is-raw={!redacted}
                                    on:click={() => redacted = !redacted}
                                >
                                    {redacted ? '🔓 SHOW RAW' : '🔒 REDACT'}
                                </button>
                            {/if}
                            <span class="badge-rec">● REC</span>
                        </div>
                    </div>

                    <div class="video-wrap">
                        <img
                            id="cctv-feed"
                            src={videoSrc}
                            alt="CCTV Feed"
                            class="cctv-feed"
                            on:error={(e) => e.target.src =
                                'https://placehold.co/640x360/090b10/50fa7b?text=Searching+for+Camera+Signal...'}
                        />
                        <div class="stream-overlay">
                            <span class="timestamp">{timeStr}</span>
                            <span class="cam-label">CAM_01 · MAIN_LOBBY</span>
                        </div>
                    </div>

                    <div class="room-footer glass">
                        <span class="footer-label">Current Feed</span>
                        <span class="footer-val">Main Lobby — Floor 1</span>
                    </div>
                </div>

                <div class="card glass metrics-card">
                    <div class="card-header">
                        <h3>Electricity Usage</h3>
                        <span class="badge-kw">kW/h</span>
                    </div>
                    <div class="metrics-grid">
                        <div class="metric-item">
                            <span class="m-label">Current Load</span>
                            <span class="m-value">{stats.totalKw}<small> kW</small></span>
                            <div class="prog-bg">
                                <div class="prog-bar" style="width:{Math.min((stats.totalKw/200)*100,100)}%"></div>
                            </div>
                        </div>
                        <div class="metric-item highlight">
                            <span class="m-label">Wastage Detected</span>
                            <span class="m-value warning">{stats.wasteKw}<small> kW</small></span>
                            <span class="m-sub">AI identified idle devices</span>
                        </div>
                        <div class="metric-item">
                            <span class="m-label">Est. Savings</span>
                            <span class="m-value success">₹{Math.round(stats.wasteKw * 8 * 30)}</span>
                            <span class="m-sub">Monthly projection</span>
                        </div>
                        <div class="metric-item">
                            <span class="m-label">Efficiency Score</span>
                            <span class="m-value">{stats.totalKw > 0 ? Math.round((1 - stats.wasteKw / stats.totalKw) * 100) : 100}%</span>
                            <div class="eff-bar-wrap">
                                <div class="eff-bar" style="width:{stats.totalKw > 0 ? Math.round((1 - stats.wasteKw / stats.totalKw) * 100) : 100}%"></div>
                            </div>
                        </div>
                    </div>
                </div>

                {#if showRoomPanel}
                    <aside class="room-panel glass" id="room-overview-panel">
                        <h3>Room Overview</h3>
                        <div class="room-scroll">
                            {#if rooms.length === 0}
                                <p class="empty-hint">No room data available.</p>
                            {/if}
                            {#each rooms as room}
                                <div class="room-row">
                                    <span class="room-id">Room {room.room_id}</span>
                                    <div class="room-right">
                                        <span class="room-kw">{room.current_usage_kw ?? '—'} kW</span>
                                        <span class="status-dot" style="background:{statusColor(room.status)};box-shadow:0 0 6px {statusColor(room.status)}"></span>
                                    </div>
                                </div>
                            {/each}
                        </div>
                        <a href="/rooms" class="view-all-btn" id="btn-view-all-rooms">View All Rooms →</a>
                    </aside>
                {/if}

                <button
                    id="btn-toggle-panel"
                    class="toggle-panel-btn"
                    on:click={() => showRoomPanel = !showRoomPanel}
                    title={showRoomPanel ? 'Hide panel' : 'Show panel'}
                >
                    {showRoomPanel ? '›' : '‹'}
                </button>
            </div>
        {/if}
    </div>
</div>

<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

    :global(body) {
        margin: 0; padding: 0;
        font-family: 'Outfit', sans-serif;
        background: #090b10;
        color: #e2e8f0;
        overflow: hidden;
    }

    .dashboard-wrapper {
        display: flex;
        height: 100vh;
        width: 100vw;
        overflow: hidden;
    }

    .main-content {
        flex: 1;
        padding: 2rem 2.5rem;
        overflow-y: auto;
        background: radial-gradient(circle at 80% 10%, rgba(80,250,123,0.04), transparent 50%);
        display: flex;
        flex-direction: column;
        gap: 1.4rem;
    }

    .loader-wrap {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 1.5rem;
        color: #64748b;
    }

    .loader {
        width: 44px; height: 44px;
        border: 3px solid rgba(80,250,123,0.1);
        border-top-color: #50fa7b;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    @keyframes spin { to { transform: rotate(360deg); } }

    .page-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }

    .page-header h1 {
        margin: 0;
        font-size: 1.75rem;
        font-weight: 700;
        background: linear-gradient(to right, #fff, #94a3b8);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .subtitle { margin: 4px 0 0; color: #64748b; font-size: 0.9rem; }
    .header-right { display: flex; align-items: center; gap: 1rem; }

    .live-badge {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(80,250,123,0.08);
        color: #50fa7b;
        border: 1px solid rgba(80,250,123,0.15);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .dot-live {
        width: 7px; height: 7px;
        border-radius: 50%;
        background: #50fa7b;
        box-shadow: 0 0 8px #50fa7b;
        animation: pulse 2s infinite;
        display: inline-block;
    }

    @keyframes pulse {
        0%,100% { transform: scale(1); opacity: 1; }
        50%      { transform: scale(1.6); opacity: 0.5; }
    }

    .top-stats {
        display: flex;
        gap: 1rem;
        align-items: center;
    }

    .stat-card {
        flex: 1;
        padding: 1rem 1.4rem;
        border-radius: 16px;
        display: flex;
        flex-direction: column;
        gap: 4px;
    }

    .stat-label { font-size: 0.75rem; color: #64748b; font-weight: 500; }
    .stat-val {
        font-size: 1.6rem;
        font-weight: 700;
        color: #f8fafc;
    }
    .stat-val small { font-size: 0.8rem; color: #94a3b8; font-weight: 400; }
    .stat-val.warning { color: #ffb86c; }

    .notif-btn {
        width: 42px; height: 42px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        font-size: 1.1rem;
        cursor: pointer;
        transition: all 0.2s;
        flex-shrink: 0;
    }
    .notif-btn:hover { background: rgba(255,255,255,0.08); transform: translateY(-1px); }

    .dashboard-grid {
        display: grid;
        grid-template-columns: 1fr;
        grid-template-rows: auto auto;
        gap: 1.2rem;
        position: relative;
        flex: 1;
    }

    .dashboard-grid.panel-open {
        grid-template-columns: 1fr 1fr 260px;
        grid-template-rows: 1fr;
    }

    .glass {
        background: rgba(18, 21, 32, 0.55);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255,255,255,0.05);
    }

    .card {
        padding: 1.4rem;
        border-radius: 20px;
        display: flex;
        flex-direction: column;
        gap: 1.2rem;
        min-height: 0;
    }

    .card-header h3 { margin: 0; font-size: 1rem; color: #fff; font-weight: 600; }

    .cctv-actions { display: flex; align-items: center; gap: 10px; }

    .btn-pill {
        background: rgba(139,233,253,0.1);
        color: #8be9fd;
        border: 1px solid rgba(139,233,253,0.2);
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 0.7rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.2s;
        font-family: inherit;
    }
    .btn-pill:hover { background: #8be9fd; color: #000; }

    .btn-pill.is-raw {
        background: rgba(255,184,108,0.1);
        color: #ffb86c;
        border-color: rgba(255,184,108,0.2);
    }
    .btn-pill.is-raw:hover { background: #ffb86c; color: #000; }

    .badge-rec {
        font-size: 0.65rem;
        font-weight: 800;
        color: #ff5555;
        letter-spacing: 1px;
        animation: blink 1.2s infinite;
    }
    @keyframes blink { 50% { opacity: 0.3; } }

    .video-wrap {
        position: relative;
        border-radius: 14px;
        overflow: hidden;
        aspect-ratio: 16/9;
        background: #000;
        flex: 1;
    }
    .cctv-feed { width: 100%; height: 100%; object-fit: cover; display: block; }

    .stream-overlay {
        position: absolute;
        top: 0; left: 0; width: 100%;
        padding: 0.8rem 1rem;
        display: flex;
        justify-content: space-between;
        background: linear-gradient(to bottom, rgba(0,0,0,0.65), transparent);
        font-family: monospace;
        font-size: 0.75rem;
        color: #50fa7b;
        box-sizing: border-box;
    }

    .room-footer {
        border-radius: 12px;
        padding: 0.7rem 1rem;
    }
    .footer-label { font-size: 0.75rem; color: #64748b; }
    .footer-val   { font-size: 0.85rem; color: #e2e8f0; font-weight: 500; }

    .badge-kw {
        background: rgba(189,147,249,0.2);
        color: #bd93f9;
        border-radius: 6px;
        padding: 3px 10px;
        font-size: 0.7rem;
        font-weight: 700;
    }

    .metrics-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.2rem;
        flex: 1;
    }

    .metric-item {
        display: flex;
        flex-direction: column;
        gap: 6px;
        padding: 1rem;
        background: rgba(255,255,255,0.02);
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.04);
    }
    .metric-item.highlight { border-color: rgba(255,184,108,0.15); }

    .m-label  { font-size: 0.75rem; color: #64748b; }
    .m-value  { font-size: 1.5rem; font-weight: 700; color: #f8fafc; }
    .m-value small { font-size: 0.75rem; color: #94a3b8; font-weight: 400; }
    .m-value.warning { color: #ffb86c; }
    .m-value.success { color: #50fa7b; }
    .m-sub    { font-size: 0.7rem; color: #475569; }

    .prog-bg { height: 5px; background: rgba(255,255,255,0.05); border-radius: 3px; }
    .prog-bar { height: 100%; background: linear-gradient(to right,#50fa7b,#8be9fd); border-radius: 3px; transition: width 1s ease; }

    .eff-bar-wrap { height: 5px; background: rgba(255,255,255,0.05); border-radius: 3px; }
    .eff-bar { height: 100%; background: linear-gradient(to right,#bd93f9,#ff79c6); border-radius: 3px; transition: width 1s ease; }

    .room-panel {
        border-radius: 20px;
        padding: 1.4rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
        overflow: hidden;
    }
    .room-panel h3 { margin: 0; font-size: 1rem; color: #fff; }

    .room-scroll {
        flex: 1;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .room-scroll::-webkit-scrollbar { width: 3px; }
    .room-scroll::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }

    .room-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 9px 10px;
        border-radius: 10px;
        border-bottom: 1px solid rgba(255,255,255,0.04);
        transition: background 0.15s;
    }
    .room-row:hover { background: rgba(255,255,255,0.03); }

    .room-id  { font-size: 0.85rem; color: #e2e8f0; }
    .room-right { display: flex; align-items: center; gap: 10px; }
    .room-kw  { font-size: 0.75rem; color: #64748b; }
    .status-dot { width: 7px; height: 7px; border-radius: 50%; }

    .empty-hint { color: #475569; font-size: 0.85rem; text-align: center; padding: 2rem 0; }

    .view-all-btn {
        display: block;
        text-align: center;
        padding: 9px;
        border-radius: 10px;
        background: rgba(80,250,123,0.08);
        color: #50fa7b;
        text-decoration: none;
        font-size: 0.8rem;
        font-weight: 600;
        transition: background 0.2s;
    }
    .view-all-btn:hover { background: rgba(80,250,123,0.15); }

    .toggle-panel-btn {
        position: absolute;
        right: -14px;
        top: 50%;
        transform: translateY(-50%);
        width: 28px; height: 28px;
        background: rgba(18,21,32,0.9);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 50%;
        color: #94a3b8;
        cursor: pointer;
        font-size: 1.1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10;
        transition: all 0.2s;
        line-height: 1;
        padding: 0;
    }
    .toggle-panel-btn:hover { background: rgba(80,250,123,0.1); color: #50fa7b; }

    @media (max-width: 1100px) {
        .dashboard-grid.panel-open { grid-template-columns: 1fr 260px; grid-template-rows: auto auto; }
        :global(.room-panel) { grid-column: 1 / -1; }
    }
</style>