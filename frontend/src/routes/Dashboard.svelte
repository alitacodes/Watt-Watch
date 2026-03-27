<script>
    import { onMount, onDestroy } from 'svelte';
    import Sidebar from '../components/Sidebar.svelte';

    let currentUser = null;
    let errorMessage = '';
    let loading = true;
    let redacted = true;
    let timeStr = '';
    let clockInterval;
    let pollInterval;
    let isRefreshing = false;

    let stats = { totalRooms: 0, wasteKw: 0, totalKw: 0 };
    let rooms = [];
    let selectedRoom = null;

    const dummyAlerts = [
        { room_id: 1, status: 'occupied', message: 'Motion detected in Room 1', time: '18:14' },
        { room_id: 2, status: 'vacant',   message: 'Room 2 left idle for 45 min', time: '17:52' },
        { room_id: 3, status: 'warning',  message: 'High power draw in Room 3', time: '17:40' },
        { room_id: 1, status: 'warning',  message: 'AC running in empty zone (Zone 2)', time: '17:31' },
        { room_id: 4, status: 'occupied', message: 'Motion detected in Room 4', time: '17:10' },
        { room_id: 2, status: 'warning',  message: 'Lights on — no occupancy detected', time: '16:58' },
        { room_id: 3, status: 'vacant',   message: 'Room 3 cleared, devices still on', time: '16:44' },
    ];

    function tick() {
        timeStr = new Date().toLocaleTimeString('en-US', { hour12: false });
    }

    async function fetchLiveData() {
        try {
            isRefreshing = true;
            const [statsRes, roomsRes, alertsRes] = await Promise.all([
                fetch('/api/v1/stats'),
                fetch('/api/v1/room_list/'),
                fetch('/api/v1/alerts'),
            ]);
            if (statsRes.ok)  stats = await statsRes.json();
            if (roomsRes.ok) {
                const data = await roomsRes.json();
                rooms = data.rooms || [];
                stats.totalRooms = rooms.length;

                if (selectedRoom) {
                    selectedRoom = rooms.find(r => String(r.room_id) === String(selectedRoom.room_id)) || selectedRoom;
                }
            }
        } catch (e) {
            console.error('Poll error', e);
        } finally {
            setTimeout(() => { isRefreshing = false; }, 1000);
        }
    }

    onMount(async () => {
        tick();
        clockInterval = setInterval(tick, 1000);

        try {
            const authRes = await fetch('/api/v1/auth/status');
            if (!authRes.ok) { window.location.href = '/login'; return; }
            currentUser = await authRes.json();

            const [statsRes, roomsRes, alertsRes] = await Promise.all([
                fetch('/api/v1/stats'),
                fetch('/api/v1/room_list/'),
                fetch('/api/v1/alerts'),
            ]);
            if (statsRes.ok)  stats = await statsRes.json();
            if (roomsRes.ok) {
                const data = await roomsRes.json();
                rooms = data.rooms || [];
                stats.totalRooms = rooms.length;

                // Check if a specific room was requested via ?room=N (from "View Feed" button)
                const params = new URLSearchParams(window.location.search);
                const requestedRoomId = params.get('room');
                if (requestedRoomId) {
                    selectedRoom = rooms.find(r => String(r.room_id) === String(requestedRoomId)) || null;
                }
                // If none requested (or not found), auto-select first room with a camera
                if (!selectedRoom) {
                    selectedRoom = rooms.find(r => r.ip && r.port) || rooms[0] || null;
                }
            }
            if (alertsRes.ok) {
                // alerts from API ignored — using dummy alerts for display
            }
            pollInterval = setInterval(fetchLiveData, 5000);
        } catch (e) {
            console.error('Dashboard init error', e);
            errorMessage = 'Failed to connect to server';
        } finally {
            loading = false;
        }
    });

    onDestroy(() => {
        clearInterval(clockInterval);
        clearInterval(pollInterval);
    });

    function selectRoom(room) {
        selectedRoom = room;
        redacted = true; // reset redact mode on room switch
    }

    $: cameraConnected = selectedRoom && selectedRoom.ip && selectedRoom.port;
    $: videoSrc = cameraConnected
        ? (redacted
            ? `http://127.0.0.1:5000/video/${selectedRoom.ip}/${selectedRoom.port}/`
            : `http://127.0.0.1:5000/video/${selectedRoom.ip}/${selectedRoom.port}/admin`)
        : null;

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
                    {#if isRefreshing}
                        <div style="font-size: 0.75rem; color: #50fa7b; margin-top: 6px; text-align: right; font-weight: 600;">🔄 Refreshing data...</div>
                    {/if}
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


            </div>

            <div class="dashboard-grid">

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
                        {#if cameraConnected}
                            <img
                                id="cctv-feed"
                                src={videoSrc}
                                alt="CCTV Feed"
                                class="cctv-feed"
                                on:error={(e) => e.target.src =
                                    'https://placehold.co/640x360/090b10/50fa7b?text=Searching+for+Camera+Signal...'}
                            />
                        {:else}
                            <div class="no-camera">
                                <span class="no-cam-icon">📷</span>
                                <span class="no-cam-text">Camera Not Connected</span>
                                <span class="no-cam-sub">{selectedRoom ? `Room ${selectedRoom.room_id} — no IP/port configured` : 'No room selected'}</span>
                            </div>
                        {/if}
                        <div class="stream-overlay">
                            <span class="timestamp">{timeStr}</span>
                            <span class="cam-label">{selectedRoom ? `CAM_${String(selectedRoom.room_id).padStart(2,'0')} · ROOM_${selectedRoom.room_id}` : 'NO FEED'}</span>
                        </div>
                    </div>

                    <div class="room-footer glass">
                        <div class="footer-left">
                            <span class="footer-label">Current Feed</span>
                            <span class="footer-val">{selectedRoom ? `Room ${selectedRoom.room_id}` : 'None'} {cameraConnected ? `· ${selectedRoom.ip}:${selectedRoom.port}` : '· No camera'}</span>
                        </div>
                        {#if selectedRoom && selectedRoom.p_count >=0}
                             <div class="footer-right">
                                <span class="footer-occ-tag" class:is-occupied={selectedRoom.p_count > 0}>
                                    {selectedRoom.p_count > 0 ? `👥 ${selectedRoom.p_count} OCCUPIED` : '🔘 EMPTY'}
                                </span>
                             </div>
                        {/if}
                    </div>
                </div>



                <div class="right-col">
                    <aside class="room-panel glass" id="room-overview-panel">
                        <h3>Room Overview</h3>
                        <div class="room-scroll">
                            {#if rooms.length === 0}
                                <p class="empty-hint">No room data available.</p>
                            {/if}
                            {#each rooms as room}
                                <div
                                    class="room-row"
                                    class:room-row-active={selectedRoom?.room_id === room.room_id}
                                    on:click={() => selectRoom(room)}
                                    role="button"
                                    tabindex="0"
                                    on:keypress={(e) => e.key === 'Enter' && selectRoom(room)}
                                >
                                    <span class="room-id">Room {room.room_id}</span>
                                    <div class="room-right">
                                        {#if room.p_count > 0}
                                            <span class="p-count-badge">👤 {room.p_count}</span>
                                        {/if}
                                        <span class="room-cam-badge" class:connected={room.ip && room.port}>
                                            {room.ip && room.port ? '● Live' : '○ No Cam'}
                                        </span>
                                        <span class="status-dot" style="background:{statusColor(room.status)};box-shadow:0 0 6px {statusColor(room.status)}"></span>
                                    </div>
                                </div>
                            {/each}
                        </div>
                        <a href="/rooms" class="view-all-btn" id="btn-view-all-rooms">View All Rooms →</a>
                    </aside>

                    <aside class="alerts-panel glass" id="alerts-panel">
                        <h3>⚡ Alerts</h3>
                        <div class="alerts-scroll">
                            {#each dummyAlerts as alert}
                                <div class="alert-row alert-{alert.status}">
                                    <div class="alert-left">
                                        <span class="alert-icon">
                                            {#if alert.status === 'occupied'}🟢{:else if alert.status === 'vacant'}⚫{:else}🟡{/if}
                                        </span>
                                        <div class="alert-text">
                                            <span class="alert-label">Room {alert.room_id}</span>
                                            <span class="alert-msg">{alert.message}</span>
                                        </div>
                                    </div>
                                    <span class="alert-time">{alert.time}</span>
                                </div>
                            {/each}
                        </div>
                    </aside>
                </div>


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



    .dashboard-grid {
        display: grid;
        grid-template-columns: 1fr 280px;
        grid-template-rows: 1fr;
        gap: 1.2rem;
        position: relative;
        flex: 1;
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

    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
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
        padding: 0.7rem 1.2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .footer-left { display: flex; flex-direction: column; gap: 2px; }
    .footer-label { font-size: 0.7rem; color: #64748b; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
    .footer-val   { font-size: 0.85rem; color: #e2e8f0; font-weight: 600; }

    .footer-occ-tag {
        font-size: 0.65rem;
        font-weight: 800;
        padding: 4px 10px;
        border-radius: 6px;
        background: rgba(148,163,184,0.1);
        color: #94a3b8;
        border: 1px solid rgba(148,163,184,0.15);
        letter-spacing: 0.5px;
    }
    .footer-occ-tag.is-occupied {
        background: rgba(80,250,123,0.08);
        color: #50fa7b;
        border-color: rgba(80,250,123,0.15);
    }


    .right-col {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        overflow-y: auto;
        min-height: 0;
    }

    .room-panel {
        border-radius: 20px;
        padding: 1.4rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
        overflow: hidden;
        max-height: 20vh;
    }
    .room-panel h3 { margin: 0; font-size: 1rem; color: #fff; }

    .alerts-panel {
        border-radius: 20px;
        padding: 1.4rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
        overflow: hidden;
        max-height: 45vh;
        margin-top: 0;
    }
    .alerts-panel h3 { margin: 0; font-size: 1rem; color: #fff; }

    .alerts-scroll {
        flex: 1;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .alerts-scroll::-webkit-scrollbar { width: 3px; }
    .alerts-scroll::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }

    .alert-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 9px 10px;
        border-radius: 10px;
        border-bottom: 1px solid rgba(255,255,255,0.04);
        transition: background 0.15s;
    }
    .alert-row:hover { background: rgba(255,255,255,0.03); }
    .alert-left { display: flex; align-items: flex-start; gap: 8px; }
    .alert-icon { font-size: 0.7rem; margin-top: 2px; }
    .alert-text { display: flex; flex-direction: column; gap: 2px; }
    .alert-label { font-size: 0.82rem; color: #e2e8f0; font-weight: 600; }
    .alert-msg { font-size: 0.72rem; color: #64748b; }
    .alert-time { font-size: 0.68rem; color: #475569; white-space: nowrap; margin-left: 4px; }

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
        cursor: pointer;
    }
    .room-row:hover { background: rgba(255,255,255,0.05); }
    .room-row.room-row-active {
        background: rgba(80,250,123,0.08);
        border-color: rgba(80,250,123,0.15);
    }

    .room-id  { font-size: 0.85rem; color: #e2e8f0; }
    .room-right { display: flex; align-items: center; gap: 8px; }
    .status-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }

    .room-cam-badge {
        font-size: 0.65rem;
        font-weight: 600;
        color: #475569;
        letter-spacing: 0.3px;
    }
    .room-cam-badge.connected { color: #50fa7b; }
    
    .p-count-badge {
        font-size: 0.75rem;
        background: rgba(139,233,253,0.1);
        color: #8be9fd;
        padding: 2px 6px;
        border-radius: 6px;
        font-weight: 600;
        margin-right: 4px;
    }

    /* ── No Camera placeholder ── */
    .no-camera {
        width: 100%; height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        background: rgba(9,11,16,0.85);
    }
    .no-cam-icon { font-size: 2.5rem; opacity: 0.4; }
    .no-cam-text { font-size: 1rem; font-weight: 600; color: #64748b; }
    .no-cam-sub  { font-size: 0.75rem; color: #334155; }

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



    @media (max-width: 1100px) {
        .dashboard-grid.panel-open { grid-template-columns: 1fr 260px; grid-template-rows: auto auto; }
        :global(.room-panel) { grid-column: 1 / -1; }
    }
</style>