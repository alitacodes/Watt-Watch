<script>
    import { onMount, onDestroy } from 'svelte';
    import Sidebar from '../components/Sidebar.svelte';

    let currentUser = null;
    let rooms = [];
    let loading = true;
    let pollInterval;
    let isRefreshing = false;

    async function fetchRoomsConfig() {
        try {
            isRefreshing = true;
            const roomsRes = await fetch('/api/v1/rooms');
            if (roomsRes.ok) {
                const data = await roomsRes.json();
                rooms = (data.rooms || []).map(r => ({ ...r }));
            }
        } catch (e) {
            console.error('Poll error', e);
        } finally {
            setTimeout(() => { isRefreshing = false; }, 1000);
        }
    }

    onMount(async () => {
        try {
            const authRes = await fetch('/api/v1/auth/status');
            if (!authRes.ok) { window.location.href = '/login'; return; }
            currentUser = await authRes.json();

            const roomsRes = await fetch('/api/v1/rooms');
            if (roomsRes.ok) {
                const data = await roomsRes.json();
                rooms = (data.rooms || []).map(r => ({ ...r }));
            }
            pollInterval = setInterval(fetchRoomsConfig, 5000);
        } catch (e) {
            console.error('Rooms init error', e);
        } finally {
            loading = false;
        }
    });

    onDestroy(() => {
        clearInterval(pollInterval);
    });

    function statusColor(s = '') {
        const v = s.toLowerCase();
        if (v === 'occupied') return '#50fa7b';
        if (v === 'vacant')   return '#6272a4';
        return '#ffb86c';
    }

    function statusBg(s = '') {
        const v = s.toLowerCase();
        if (v === 'occupied') return 'rgba(80,250,123,0.08)';
        if (v === 'vacant')   return 'rgba(98,114,164,0.08)';
        return 'rgba(255,184,108,0.08)';
    }
</script>

<div class="page-wrapper">
    <Sidebar active="rooms" {currentUser} />

    <div class="main-content">
        {#if loading}
            <div class="loader-wrap">
                <div class="loader"></div>
                <p>Loading room data…</p>
            </div>
        {:else}
            <header class="page-header">
                <div>
                    <h1>Room Details</h1>
                    <p class="subtitle">{rooms.length} rooms monitored — click a card to view usage</p>
                    {#if isRefreshing}
                        <p class="subtitle" style="color: #50fa7b; font-weight: bold; margin-top: 8px;">🔄 Refreshing data...</p>
                    {/if}
                </div>
                <a href="/create-room" class="btn-report" id="btn-go-create-room">➕ Create Room</a>
            </header>

            <div class="rooms-layout">
                <div class="rooms-stack">
                    {#if rooms.length === 0}
                        <div class="empty-state glass">
                            <span>🏠</span>
                            <p>No rooms configured yet.</p>
                        </div>
                    {/if}

                    {#each rooms as room, i}
                        <div
                            class="room-card glass"
                            id="room-card-{room.room_id}"
                        >
                            <div class="room-card-top">
                                <div class="room-id-block">
                                    <span class="room-num">Room {room.room_id}</span>
                                    <div class="status-stack">
                                        <span
                                            class="status-badge"
                                            style="color:{statusColor(room.status)};background:{statusBg(room.status)}"
                                        >
                                            {room.status}
                                        </span>
                                        {#if room.p_count > 0}
                                            <span class="p-count-mini">👤 {room.p_count} <small>persons</small></span>
                                        {/if}
                                    </div>
                                </div>

                                <div class="room-meta">
                                    <div class="meta-item">
                                        <span class="meta-label">Daily Wastage</span>
                                        <span class="meta-val">{room.daily_usage_kwh ?? '—'} <small>kWh</small></span>
                                    </div>
                                    <div class="meta-divider"></div>
                                    <div class="meta-item">
                                        <span class="meta-label">Monthly Wastage</span>
                                        <span class="meta-val">{room.monthly_usage_kwh ?? '—'} <small>kWh</small></span>
                                    </div>
                                    <div class="meta-divider"></div>
                                    <div class="meta-item">
                                        <span class="meta-label">Total Appliances</span>
                                        <span class="meta-val">{room.no_of_appl ?? '—'}</span>
                                    </div>
                                    <div class="meta-divider"></div>
                                    <div class="meta-item">
                                        <span class="meta-label">Running</span>
                                        <span class="meta-val meta-running">6</span>
                                    </div>
                                    <div class="meta-divider"></div>
                                    <div class="meta-item">
                                        <span class="meta-label">Waste Detected</span>
                                        <span class="meta-val meta-waste-{(room.status === 'empty' || room.status === 'vacant') && room.current_usage_kw > 0.02 ? 'yes' : 'no'}">
                                            {(room.status === 'empty' || room.status === 'vacant') && room.current_usage_kw > 0.02 ? 'TRUE' : 'FALSE'}
                                        </span>
                                    </div>
                                </div>

                                <div class="room-actions">
                                    <span class="cam-indicator" class:cam-live={room.ip && room.port}>
                                        {room.ip && room.port ? '● Camera Live' : '○ No Camera'}
                                    </span>
                                    <a
                                        href="/dashboard?room={room.room_id}"
                                        class="btn-view-feed"
                                        id="btn-feed-{room.room_id}"
                                    >
                                        🎥 View Feed
                                    </a>
                                </div>

                            </div>
                        </div>
                    {/each}
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

    .page-wrapper {
        display: flex;
        height: 100vh;
        width: 100vw;
        overflow: hidden;
    }

    .main-content {
        flex: 1;
        padding: 2rem 2.5rem;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        background: radial-gradient(circle at 20% 80%, rgba(189,147,249,0.04), transparent 50%);
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

    .subtitle { margin: 4px 0 0; color: #64748b; font-size: 0.88rem; }

    .btn-report {
        background: rgba(80,250,123,0.1);
        color: #50fa7b;
        border: 1px solid rgba(80,250,123,0.2);
        padding: 9px 18px;
        border-radius: 12px;
        text-decoration: none;
        font-size: 0.85rem;
        font-weight: 600;
        transition: all 0.2s;
    }

    .btn-report:hover { background: rgba(80,250,123,0.18); transform: translateY(-1px); }

    .rooms-layout {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        flex: 1;
        min-height: 0;
    }

    .rooms-stack {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        overflow-y: auto;
    }

    .rooms-stack::-webkit-scrollbar { width: 3px; }
    .rooms-stack::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); }

    .empty-state {
        border-radius: 20px;
        padding: 3rem;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;
        color: #475569;
        font-size: 2rem;
    }

    .empty-state p { font-size: 0.9rem; margin: 0; }

    .glass {
        background: rgba(18,21,32,0.55);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255,255,255,0.05);
    }

    .room-card {
        padding: 1.3rem 1.5rem;
        border-radius: 18px;
        display: flex;
        flex-direction: column;
        gap: 1rem;
        transition: border-color 0.3s, transform 0.2s;
    }

    .room-card-top {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        flex-wrap: wrap;
    }

    .room-id-block { display: flex; flex-direction: column; gap: 5px; min-width: 100px; }

    .room-num { font-size: 1.1rem; font-weight: 700; color: #f8fafc; }

    .status-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 8px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    .room-meta {
        display: flex;
        align-items: center;
        gap: 1rem;
        flex: 1;
    }

    .meta-item { display: flex; flex-direction: column; gap: 2px; }
    .meta-label { font-size: 0.7rem; color: #64748b; }
    .meta-val { font-size: 1rem; font-weight: 600; color: #e2e8f0; }
    .meta-val small { font-size: 0.7rem; color: #94a3b8; }
    .meta-running { color: #50fa7b; }
    .meta-waste-yes { color: #ff5555; }
    .meta-waste-no  { color: #50fa7b; }
    .meta-divider { width: 1px; height: 30px; background: rgba(255,255,255,0.06); }

    .room-actions {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-left: auto;
    }

    .cam-indicator {
        font-size: 0.68rem;
        font-weight: 600;
        color: #475569;
        letter-spacing: 0.3px;
        white-space: nowrap;
    }
    .cam-indicator.cam-live { color: #50fa7b; }

    .status-stack { display: flex; flex-direction: column; gap: 4px; }
    .p-count-mini {
        font-size: 0.65rem;
        font-weight: 700;
        color: #8be9fd;
        background: rgba(139,233,253,0.06);
        padding: 2px 6px;
        border-radius: 4px;
        width: fit-content;
    }
    .p-count-mini small { font-weight: 400; opacity: 0.7; }

    .btn-view-feed {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 7px 14px;
        border-radius: 10px;
        background: rgba(80,250,123,0.08);
        color: #50fa7b;
        border: 1px solid rgba(80,250,123,0.15);
        font-size: 0.78rem;
        font-weight: 600;
        text-decoration: none;
        transition: all 0.2s;
        font-family: inherit;
        white-space: nowrap;
    }
    .btn-view-feed:hover {
        background: rgba(80,250,123,0.16);
        border-color: rgba(80,250,123,0.3);
        transform: translateY(-1px);
    }
</style>
