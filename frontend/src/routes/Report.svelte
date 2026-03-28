<script>
    import { onMount } from 'svelte';
    import Sidebar from '../components/Sidebar.svelte';

    let currentUser = null;
    let rooms = [];
    let loading = true;
    let searchQuery = '';
    let selectedRoom = null;

    let weeklyData = [];

    $: filteredRooms = rooms.filter(r =>
        String(r.room_id).toLowerCase().includes(searchQuery.toLowerCase()) ||
        (r.room_name || '').toLowerCase().includes(searchQuery.toLowerCase())
    );

    $: if (filteredRooms.length === 1 && searchQuery) {
        selectedRoom = filteredRooms[0];
    }

    onMount(async () => {
        try {
            const authRes = await fetch('/api/v1/auth/status');
            if (!authRes.ok) { window.location.href = '/login'; return; }
            currentUser = await authRes.json();

            const [roomsRes, weeklyRes] = await Promise.all([
                fetch('/api/v1/rooms'),
                fetch('/api/v1/wastage/weekly'),
            ]);
            if (roomsRes.ok) {
                const data = await roomsRes.json();
                rooms = data.rooms || [];
            }
            if (weeklyRes.ok) {
                const data = await weeklyRes.json();
                weeklyData = data.weekly || [];
            }
        } catch (e) {
            console.error('Report init error', e);
        } finally {
            loading = false;
        }
    });

    function selectRoom(room) {
        selectedRoom = room;
        searchQuery = String(room.room_id);
    }

    function statusColor(s = '') {
        const v = s.toLowerCase();
        if (v === 'occupied') return '#50fa7b';
        if (v === 'vacant')   return '#6272a4';
        return '#ffb86c';
    }

    function buildPolyline(data, width = 380, height = 120) {
        if (!data.length) return { line: '', area: '', points: [] };
        const vals = data.map(d => d.wastage_wh);
        const max = Math.max(...vals, 0.001);
        const pts = vals.map((v, i) => {
            const x = data.length > 1 ? (i / (data.length - 1)) * width : width / 2;
            const y = height - (v / max) * (height - 20) - 10;
            return { x: +x.toFixed(1), y: +y.toFixed(1), val: v };
        });
        const line = pts.map(p => `${p.x},${p.y}`).join(' ');
        const area = `0,${height} ${line} ${width},${height}`;
        return { line, area, points: pts };
    }

    $: chartData = buildPolyline(weeklyData);
    $: chartLabels = weeklyData.map(d => d.label);

    function downloadCSV() {
        if (!selectedRoom) return;
        window.location.href = `/api/v1/wastage/csv/${selectedRoom.room_id}`;
    }
</script>

<div class="page-wrapper">
    <Sidebar active="report" {currentUser} />

    <div class="main-content">
        {#if loading}
            <div class="loader-wrap">
                <div class="loader"></div>
                <p>Loading report data…</p>
            </div>
        {:else}
            <header class="page-header">
                <div>
                    <h1>Report Generator</h1>
                    <p class="subtitle">Search a room and export its energy wastage report</p>
                </div>
            </header>

            <div class="report-grid">
                <div class="report-main">

                    <div class="search-card glass" id="search-card">
                        <div class="search-inner">
                            <span class="search-icon">🔍</span>
                            <input
                                id="room-search"
                                type="text"
                                placeholder="Search by room number…"
                                bind:value={searchQuery}
                                autocomplete="off"
                            />
                            {#if searchQuery}
                                <button class="clear-btn" on:click={() => { searchQuery = ''; selectedRoom = null; }}>✕</button>
                            {/if}
                        </div>
                        {#if searchQuery && filteredRooms.length > 1}
                            <div class="search-dropdown">
                                {#each filteredRooms.slice(0,6) as room}
                                    <button class="dropdown-item" on:click={() => selectRoom(room)}>
                                        <span class="dd-id">Room {room.room_id}</span>
                                        <span
                                            class="dd-status"
                                            style="color:{statusColor(room.status)}"
                                        >{room.status}</span>
                                    </button>
                                {/each}
                            </div>
                        {/if}
                    </div>

                    <div class="preview-card glass" id="preview-card">
                        {#if selectedRoom}
                            <div class="preview-header">
                                <div>
                                    <span class="preview-room-id">Room {selectedRoom.room_id}</span>
                                    <span
                                        class="preview-status"
                                        style="color:{statusColor(selectedRoom.status)}"
                                    >{selectedRoom.status}</span>
                                </div>
                                <button class="btn-csv" id="btn-download-csv" on:click={downloadCSV}>
                                    ⬇ Download CSV
                                </button>
                            </div>

                            <div class="preview-metrics">
                                <div class="prev-metric">
                                    <span class="pm-label">Daily Wastage</span>
                                    <span class="pm-val">{selectedRoom.daily_wastage_kwh ?? selectedRoom.daily_usage_kwh ?? '—'} <small>Wh</small></span>
                                </div>
                                <div class="prev-metric">
                                    <span class="pm-label">Monthly Wastage</span>
                                    <span class="pm-val">{selectedRoom.monthly_wastage_kwh ?? selectedRoom.monthly_usage_kwh ?? '—'} <small>Wh</small></span>
                                </div>
                                <div class="prev-metric">
                                    <span class="pm-label">Appliances</span>
                                    <span class="pm-val">{selectedRoom.no_of_appl ?? '—'}</span>
                                </div>
                            </div>
                        {:else}
                            <div class="preview-empty">
                                <span class="empty-icon">📋</span>
                                <p>Search and select a room to preview its details</p>
                            </div>
                        {/if}
                    </div>

                    <div class="graph-card glass" id="graph-card">
                        <div class="graph-header">
                            <h3>Wastage Graph — Last 7 Days (All Rooms)</h3>
                        </div>

                        <div class="svg-wrap">
                            {#if weeklyData.length > 0}
                                <svg viewBox="0 0 380 130" preserveAspectRatio="none">
                                    {#each [0,1,2,3] as g}
                                        <line
                                            x1="0" y1="{10 + g*30}"
                                            x2="380" y2="{10 + g*30}"
                                            stroke="rgba(255,255,255,0.04)" stroke-width="1"
                                        />
                                    {/each}

                                    <defs>
                                        <linearGradient id="grad-wastage" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="0%" stop-color="#ffb86c" stop-opacity="0.3"/>
                                            <stop offset="100%" stop-color="#ffb86c" stop-opacity="0"/>
                                        </linearGradient>
                                    </defs>
                                    <polygon
                                        points={chartData.area}
                                        fill="url(#grad-wastage)"
                                    />
                                    <polyline
                                        points={chartData.line}
                                        fill="none"
                                        stroke="#ffb86c"
                                        stroke-width="2"
                                        stroke-linecap="round"
                                        stroke-linejoin="round"
                                    />

                                    {#each chartData.points as pt}
                                        <circle cx={pt.x} cy={pt.y} r="3.5" fill="#ffb86c" stroke="#090b10" stroke-width="1.5"/>
                                    {/each}
                                </svg>

                                <div class="x-labels">
                                    {#each chartLabels as lbl}
                                        <span>{lbl}</span>
                                    {/each}
                                </div>
                            {:else}
                                <div class="no-data-chart">
                                    <span>📊</span>
                                    <p>No wastage data available for the past week</p>
                                </div>
                            {/if}
                        </div>

                        <div class="graph-legend">
                            <span class="legend-item">
                                <span class="legend-dot" style="background:#ffb86c"></span>
                                Daily Wastage (Wh)
                            </span>
                        </div>
                    </div>
                </div>

                <aside class="room-overview glass" id="report-room-overview">
                    <h3>Room Overview</h3>
                    <div class="overview-scroll">
                        {#each rooms as room}
                            <button
                                class="ov-row"
                                class:ov-selected={selectedRoom?.room_id === room.room_id}
                                on:click={() => selectRoom(room)}
                                id="ov-room-{room.room_id}"
                            >
                                <div class="ov-left">
                                    <span
                                        class="ov-dot"
                                        style="background:{statusColor(room.status)};box-shadow:0 0 6px {statusColor(room.status)}"
                                    ></span>
                                    <span class="ov-name">Room {room.room_id}</span>
                                </div>
                                <div class="ov-right">
                                    <span class="ov-kw">{room.current_usage_kw ?? '—'} kW</span>
                                </div>
                            </button>
                        {/each}
                        {#if rooms.length === 0}
                            <p class="empty-hint">No rooms found.</p>
                        {/if}
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
        background: radial-gradient(circle at 60% 90%, rgba(255,121,198,0.04), transparent 50%);
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

    .report-grid {
        display: grid;
        grid-template-columns: 1fr 260px;
        gap: 1.5rem;
        flex: 1;
        align-items: start;
    }

    .report-main { display: flex; flex-direction: column; gap: 1.2rem; }

    .glass {
        background: rgba(18,21,32,0.55);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255,255,255,0.05);
    }

    .search-card {
        border-radius: 16px;
        overflow: visible;
        position: relative;
    }

    .search-inner {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 1rem 1.3rem;
    }

    .search-icon { font-size: 1rem; opacity: 0.5; }

    .search-inner input {
        flex: 1;
        background: none;
        border: none;
        color: #f8fafc;
        font-size: 1rem;
        font-family: inherit;
        outline: none;
    }

    .search-inner input::placeholder { color: #475569; }

    .clear-btn {
        background: none;
        border: none;
        color: #64748b;
        cursor: pointer;
        font-size: 0.85rem;
        padding: 4px 6px;
        border-radius: 6px;
        transition: color 0.2s;
    }

    .clear-btn:hover { color: #ff5555; }

    .search-dropdown {
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: rgba(15,18,28,0.98);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 0 0 14px 14px;
        z-index: 100;
        backdrop-filter: blur(14px);
        overflow: hidden;
    }

    .dropdown-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 1.3rem;
        width: 100%;
        background: none;
        border: none;
        cursor: pointer;
        font-family: inherit;
        transition: background 0.15s;
    }

    .dropdown-item:hover { background: rgba(255,255,255,0.04); }

    .dd-id { font-size: 0.9rem; color: #e2e8f0; }
    .dd-status { font-size: 0.75rem; font-weight: 600; }

    .preview-card {
        border-radius: 18px;
        padding: 1.4rem;
        min-height: 120px;
    }

    .preview-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.2rem;
    }

    .preview-room-id { font-size: 1.3rem; font-weight: 700; color: #f8fafc; margin-right: 10px; }
    .preview-status  { font-size: 0.8rem; font-weight: 700; }

    .btn-csv {
        background: rgba(80,250,123,0.12);
        color: #50fa7b;
        border: 1px solid rgba(80,250,123,0.22);
        padding: 8px 18px;
        border-radius: 10px;
        font-size: 0.85rem;
        font-weight: 700;
        cursor: pointer;
        font-family: inherit;
        transition: all 0.2s;
    }

    .btn-csv:hover { background: #50fa7b; color: #090b10; transform: translateY(-1px); }

    .preview-metrics {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
    }

    .prev-metric {
        display: flex;
        flex-direction: column;
        gap: 4px;
        background: rgba(255,255,255,0.02);
        padding: 0.8rem 1rem;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.04);
    }

    .pm-label { font-size: 0.7rem; color: #64748b; }
    .pm-val   { font-size: 1.1rem; font-weight: 700; color: #f8fafc; }
    .pm-val small { font-size: 0.7rem; color: #94a3b8; font-weight: 400; }

    .preview-empty {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 0.7rem;
        padding: 2rem;
        color: #475569;
    }

    .empty-icon { font-size: 2rem; }
    .preview-empty p { margin: 0; font-size: 0.85rem; }

    .graph-card {
        border-radius: 18px;
        padding: 1.4rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .graph-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .graph-header h3 { margin: 0; font-size: 1rem; color: #fff; }

    .svg-wrap {
        display: flex;
        flex-direction: column;
        gap: 6px;
    }

    .svg-wrap svg {
        width: 100%;
        height: 130px;
        padding: 0 2px;
        border-left: 1px solid rgba(255,255,255,0.06);
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }

    .x-labels {
        display: flex;
        justify-content: space-between;
        padding: 0 2px;
    }

    .x-labels span { font-size: 0.6rem; color: #475569; }

    .no-data-chart {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        padding: 2rem;
        color: #475569;
        font-size: 0.85rem;
    }
    .no-data-chart span { font-size: 2rem; opacity: 0.4; }

    .graph-legend {
        display: flex;
        gap: 1.5rem;
    }

    .legend-item {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.78rem;
        color: #94a3b8;
    }

    .legend-dot { width: 8px; height: 8px; border-radius: 50%; }

    .room-overview {
        border-radius: 20px;
        padding: 1.4rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
        max-height: calc(100vh - 200px);
        overflow: hidden;
    }

    .room-overview h3 { margin: 0; font-size: 1rem; color: #fff; }

    .overview-scroll {
        flex: 1;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 3px;
    }

    .overview-scroll::-webkit-scrollbar { width: 3px; }
    .overview-scroll::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); }

    .ov-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 10px;
        border-radius: 10px;
        cursor: pointer;
        background: transparent;
        border: 1px solid transparent;
        width: 100%;
        font-family: inherit;
        transition: all 0.15s;
    }

    .ov-row:hover { background: rgba(255,255,255,0.03); }
    .ov-row.ov-selected { background: rgba(80,250,123,0.08); border-color: rgba(80,250,123,0.15); }

    .ov-left { display: flex; align-items: center; gap: 8px; }
    .ov-dot  { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
    .ov-name { font-size: 0.85rem; color: #e2e8f0; }
    .ov-kw   { font-size: 0.75rem; color: #64748b; }

    .empty-hint { color: #475569; font-size: 0.85rem; text-align: center; padding: 2rem 0; margin: 0; }
</style>
