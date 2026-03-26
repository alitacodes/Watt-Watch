<script>
  let rooms = [
    { id: '101', people: 0, status: 'AC On', result: 'WASTE DETECTED', color: '#ff5f5f' },
    { id: '102', people: 3, status: 'AC On', result: 'OPERATIONAL OK', color: '#50fa7b' },
    { id: 'Conf A', people: 12, status: 'Full Load', result: 'OPERATIONAL OK', color: '#50fa7b' },
    { id: '204', people: 1, status: 'Lights Standby', result: 'PENDING LOGIC', color: '#ffb86c' }
  ];
</script>

<main class="dashboard">
  <aside class="sidebar">
    <h2 class="logo">WATT-WATCH</h2>
    <nav>
      <div class="nav-item active">Dashboard</div>
      <div class="nav-item">Rooms</div>
      <div class="nav-item">History</div>
      <div class="nav-item">Settings</div>
    </nav>
    <div class="efficiency-card">
      <p>EFFICIENCY RATING</p>
      <h1>92% <span class="trend">+2.4%</span></h1>
    </div>
  </aside>

  <section class="content">
    <header class="stats-row">
      <div class="stat-card">TOTAL ROOMS <h3>24</h3></div>
      <div class="stat-card">WASTE DETECTED <h3 class="danger">5</h3></div>
      <div class="stat-card">ENERGY WASTE <h3>124.5 kWh</h3></div>
    </header>

    <div class="grid-layout">
      <div class="video-feed">
        <div class="video-header">LIVE VIDEO FEED - PRIVACY MODE</div>
        <div class="video-placeholder">
          <div class="privacy-mask">PRIVACY MASK ACTIVE</div>
        </div>
      </div>

      <div class="room-status">
        <div class="table-header">
          <span>ROOM</span><span>PPL</span><span>STATUS</span><span>FINAL</span>
        </div>
        {#each rooms as room}
          <div class="table-row">
            <span>Room {room.id}</span>
            <span>{room.people}</span>
            <span>{room.status}</span>
            <span class="badge" style="color: {room.color}">{room.result}</span>
          </div>
        {/each}
      </div>
    </div>
  </section>

  <aside class="alerts">
    <div class="total-savings">
      <p>TOTAL SAVINGS TODAY</p>
      <h2>$42.80 <small>USD</small></h2>
    </div>
  </aside>
</main>

<style>
  :global(body) {
    background-color: #0f111a;
    color: #e6e6e6;
    font-family: sans-serif;
    margin: 0;
  }

  .dashboard {
    display: grid;
    grid-template-columns: 200px 1fr 300px;
    height: 100vh;
    gap: 20px;
    padding: 20px;
  }

  .stat-card, .video-feed, .room-status, .efficiency-card, .total-savings {
    background: #1a1d27;
    border-radius: 12px;
    padding: 20px;
  }

  .stats-row {
    display: flex;
    gap: 15px;
    margin-bottom: 20px;
  }

  .stats-row div { flex: 1; }

  .grid-layout {
    display: grid;
    grid-template-rows: 2fr 1fr;
    gap: 20px;
  }

  .video-placeholder {
    height: 300px;
    background: #090b10;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid #333;
  }

  .table-row {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1.5fr;
    padding: 12px 0;
    border-bottom: 1px solid #2a2d3a;
    font-size: 0.9rem;
  }

  .badge {
    font-weight: bold;
    font-size: 0.75rem;
  }

  .nav-item {
    padding: 10px;
    cursor: pointer;
    opacity: 0.6;
  }

  .nav-item.active {
    background: #232734;
    opacity: 1;
    border-radius: 4px;
  }

  .danger { color: #ff5f5f; }
  .trend { color: #50fa7b; font-size: 0.8rem; }
</style>