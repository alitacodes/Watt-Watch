<script>
    import { onMount } from 'svelte';
    import Sidebar from '../components/Sidebar.svelte';

    let currentUser = null;
    let rooms = [];
    let loading = true;
    let selectedRoomIdx = null;

    // Per-room expanded tab state: null | 'daily' | 'monthly'
    function toggleTab(idx, tab) {
        if (selectedRoomIdx === idx && rooms[idx]._tab === tab) {
            rooms[idx]._tab = null;
            selectedRoomIdx = null;
        } else {
            rooms = rooms.map((r, i) => ({ ...r, _tab: i === idx ? tab : null }));
            selectedRoomIdx = idx;
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
                rooms = (data.rooms || []).map(r => ({ ...r, _tab: null }));
            }
        } catch (e) {
            console.error('Rooms init error', e);
        } finally {
            loading = false;
        }
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
                </div>
                <a href="/report" class="btn-report" id="btn-go-report">📄 Generate Report</a>
            </header>

            <div class="rooms-layout">
                <!-- ── Left: Room Cards Stack ── -->
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
                            class:expanded={room._tab !== null}
                            id="room-card-{room.room_id}"
                        >
                            <div class="room-card-top">
                                <div class="room-id-block">
                                    <span class="room-num">Room {room.room_id}</span>
                                    <span
                                        class="status-badge"
                                        style="color:{statusColor(room.status)};background:{statusBg(room.status)}"
                                    >
                                        {room.status}
                                    </span>
                                </div>

                                <div class="room-meta">
                                    <div class="meta-item">
                                        <span class="meta-label">Current Load</span>
                                        <span class="meta-val">{room.current_usage_kw ?? '—'} <small>kW</small></span>
                                    </div>
                                    <div class="meta-divider"></div>
                                    <div class="meta-item">
                                        <span class="meta-label">Floor</span>
                                        <span class="meta-val">{room.floor ?? '—'}</span>
                                    </div>
                                </div>

                                <div class="btn-group">
                                    <button
                                        class="tab-btn"
                                        class:tab-active={room._tab === 'daily'}
                                        on:click={() => toggleTab(i, 'daily')}
                                        id="btn-daily-{room.room_id}"
                                    >
                                        📅 Daily
                                    </button>
                                    <button
                                        class="tab-btn"
                                        class:tab-active={room._tab === 'monthly'}
                                        on:click={() => toggleTab(i, 'monthly')}
                                        id="btn-monthly-{room.room_id}"
                                    >
                                        📆 Monthly
                                    </button>
                                </div>
                            </div>

                            {#if room._tab}
                                <div class="usage-panel">
                                    <div class="usage-header">
                                        <span class="usage-title">
                                            {room._tab === 'daily' ? 'Daily Usage' : 'Monthly Usage'}
                                        </span>
                                        <span class="usage-val">
                                            {room._tab === 'daily'
                                                ? (room.daily_usage_kwh ?? '—')
                                                : (room.monthly_usage_kwh ?? '—')} kWh
                                        </span>
                                    </div>

                                    <!-- Mini bar chart -->
                                    <div class="mini-chart">
                                        {#if room._tab === 'daily'}
                                            {#each (room.daily_bars || [4,6,5,8,7,9,6]) as val, bi}
                                                <div class="bar-col">
                                                    <div
                                                        class="bar"
                                                        style="height:{(val/10)*100}%;background:linear-gradient(to top,#50fa7b,#8be9fd)"
                                                    ></div>
                                                    <span class="bar-label">{['M','T','W','T','F','S','S'][bi]}</span>
                                                </div>
                                            {/each}
                                        {:else}
                                            {#each (room.monthly_bars || [60,75,55,90,80,70,85,65,78,88,72,68]) as val, bi}
                                                <div class="bar-col">
                                                    <div
                                                        class="bar"
                                                        style="height:{(val/100)*100}%;background:linear-gradient(to top,#bd93f9,#ff79c6)"
                                                    ></div>
                                                    <span class="bar-label">{['J','F','M','A','M','J','J','A','S','O','N','D'][bi]}</span>
                                                </div>
                                            {/each}
                                        {/if}
                                    </div>
                                </div>
                            {/if}
                        </div>
                    {/each}
                </div>

                <!-- ── Right: Room List Sidebar ── -->
                <aside class="room-list glass" id="rooms-list-sidebar">
                    <h3>All Rooms</h3>
                    <div class="list-scroll">
                        {#each rooms as room}
                            <div
                                class="list-row"
                                class:list-row-active={room._tab !== null}
                            >
                                <div class="list-left">
                                    <span
                                        class="list-dot"
                                        style="background:{statusColor(room.status)};box-shadow:0 0 6px {statusColor(room.status)}"
                                    ></span>
                                    <span class="list-name">Room {room.room_id}</span>
                                </div>
                                <div class="list-right">
                                    <span class="list-status">{room.status}</span>
                                    <span class="list-kw">{room.current_usage_kw ?? '—'} kW</span>
                                </div>
                            </div>
                        {/each}
                        {#if rooms.length === 0}
                            <p class="empty-hint">No rooms found.</p>
                        {/if}
                    </div>

                    <!-- Summary -->
                    <div class="list-summary">
                        <div class="summary-item">
                            <span class="s-label">Occupied</span>
                            <span class="s-val" style="color:#50fa7b">
                                {rooms.filter(r => r.status?.toLowerCase() === 'occupied').length}
                            </span>
                        </div>
                        <div class="summary-item">
                            <span class="s-label">Active</span>
                            <span class="s-val" style="color:#ffb86c">
                                {rooms.filter(r => r.status?.toLowerCase() === 'active').length}
                            </span>
                        </div>
                        <div class="summary-item">
                            <span class="s-label">Vacant</span>
                            <span class="s-val" style="color:#6272a4">
                                {rooms.filter(r => r.status?.toLowerCase() === 'vacant').length}
                            </span>
                        </div>
                    </div>
                </aside>
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

    /* ── Header ── */
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

    /* ── Layout ── */
    .rooms-layout {
        display: grid;
        grid-template-columns: 1fr 280px;
        gap: 1.5rem;
        flex: 1;
        min-height: 0;
    }

    /* ── Rooms Stack ── */
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

    /* ── Room Card ── */
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

    .room-card.expanded {
        border-color: rgba(80,250,123,0.25);
        transform: scale(1.005);
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
    .meta-divider { width: 1px; height: 30px; background: rgba(255,255,255,0.06); }

    .btn-group { display: flex; gap: 8px; margin-left: auto; }

    .tab-btn {
        background: rgba(255,255,255,0.04);
        color: #64748b;
        border: 1px solid rgba(255,255,255,0.06);
        padding: 7px 14px;
        border-radius: 10px;
        font-size: 0.8rem;
        font-weight: 500;
        cursor: pointer;
        font-family: inherit;
        transition: all 0.2s;
    }

    .tab-btn:hover { background: rgba(255,255,255,0.08); color: #e2e8f0; }

    .tab-btn.tab-active {
        background: rgba(80,250,123,0.12);
        color: #50fa7b;
        border-color: rgba(80,250,123,0.2);
    }

    /* ── Usage Panel ── */
    .usage-panel {
        background: rgba(255,255,255,0.02);
        border-radius: 14px;
        padding: 1rem 1.2rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
        border: 1px solid rgba(255,255,255,0.04);
        animation: fadeDown 0.2s ease;
    }

    @keyframes fadeDown { from { opacity:0; transform:translateY(-6px); } to { opacity:1; transform:none; } }

    .usage-header { display: flex; justify-content: space-between; align-items: center; }
    .usage-title { font-size: 0.85rem; color: #94a3b8; font-weight: 500; }
    .usage-val { font-size: 1.4rem; font-weight: 700; color: #f8fafc; }

    .mini-chart {
        display: flex;
        align-items: flex-end;
        gap: 6px;
        height: 80px;
    }

    .bar-col {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;
        height: 100%;
        justify-content: flex-end;
    }

    .bar {
        width: 100%;
        border-radius: 4px 4px 0 0;
        transition: height 0.5s ease;
        min-height: 4px;
    }

    .bar-label { font-size: 0.6rem; color: #475569; }

    /* ── Room List Sidebar ── */
    .room-list {
        border-radius: 20px;
        padding: 1.4rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
        overflow: hidden;
    }

    .room-list h3 { margin: 0; font-size: 1rem; color: #fff; }

    .list-scroll {
        flex: 1;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 2px;
    }

    .list-scroll::-webkit-scrollbar { width: 3px; }
    .list-scroll::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); }

    .list-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 10px;
        border-radius: 10px;
        transition: background 0.15s;
        cursor: default;
    }

    .list-row:hover { background: rgba(255,255,255,0.03); }
    .list-row.list-row-active { background: rgba(80,250,123,0.06); }

    .list-left { display: flex; align-items: center; gap: 8px; }
    .list-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
    .list-name { font-size: 0.85rem; color: #e2e8f0; }

    .list-right { display: flex; flex-direction: column; align-items: flex-end; gap: 1px; }
    .list-status { font-size: 0.7rem; color: #64748b; }
    .list-kw { font-size: 0.75rem; color: #94a3b8; font-weight: 500; }

    .empty-hint { color: #475569; font-size: 0.85rem; text-align: center; padding: 2rem 0; }

    /* ── Summary ── */
    .list-summary {
        display: flex;
        gap: 0.5rem;
        padding-top: 0.5rem;
        border-top: 1px solid rgba(255,255,255,0.05);
    }

    .summary-item {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 2px;
        background: rgba(255,255,255,0.02);
        border-radius: 10px;
        padding: 8px 4px;
    }

    .s-label { font-size: 0.65rem; color: #64748b; }
    .s-val   { font-size: 1rem; font-weight: 700; }
</style>
