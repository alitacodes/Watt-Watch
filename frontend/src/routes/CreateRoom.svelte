<script>
    import { onMount } from 'svelte';
    import Sidebar from '../components/Sidebar.svelte';

    let currentUser = null;
    let loading = false;
    let errorMsg = '';

    let ip = '';
    let port = '';
    let zone_count = 1;
    let appliances = [
        { type: '', wattage: '', zone: '1' }
    ];

    onMount(async () => {
        try {
            const authRes = await fetch('/api/v1/auth/status');
            if (!authRes.ok) { window.location.href = '/login'; return; }
            currentUser = await authRes.json();
        } catch (e) {
            console.error('Auth check error', e);
        }
    });

    function addAppliance() {
        appliances = [...appliances, { type: '', wattage: '', zone: '1' }];
    }

    function removeAppliance(index) {
        if (appliances.length > 1) {
            appliances = appliances.filter((_, i) => i !== index);
        }
    }

    async function createRoom(e) {
        e.preventDefault();
        loading = true;
        errorMsg = '';

        if (!zone_count || zone_count < 1) {
            errorMsg = "Zone count must be at least 1.";
            loading = false;
            return;
        }

        for (let i = 0; i < appliances.length; i++) {
            const a = appliances[i];
            if (!a.type || !a.wattage || !a.zone) {
                errorMsg = `Please fill out all fields for appliance ${i + 1}.`;
                loading = false;
                return;
            }
        }

        const payload = {
            no_of_appl: appliances.length,
            zone_count: Number(zone_count),
            appl: appliances.map(a => ({
                type: a.type,
                wattage: Number(a.wattage),
                zone: a.zone
            })),
            ip: ip.trim() || null,
            port: port ? Number(port) : null
        };

        try {
            const res = await fetch('/api/v1/add_room', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (res.ok) {
                window.location.href = '/rooms';
            } else {
                const data = await res.json();
                errorMsg = data.error || 'Failed to create room';
            }
        } catch (err) {
            console.error(err);
            errorMsg = 'Network error while creating room.';
        } finally {
            loading = false;
        }
    }
</script>

<div class="page-wrapper">
    <Sidebar active="rooms" {currentUser} />

    <div class="main-content">
        <header class="page-header">
            <div>
                <h1>Create New Room</h1>
                <p class="subtitle">Set up configuration and appliances for a new room.</p>
            </div>
            <a href="/rooms" class="btn-back">⬅ Back to Rooms</a>
        </header>

        <div class="glass form-container">
            <form on:submit={createRoom}>
                
                {#if errorMsg}
                    <div class="error-banner">{errorMsg}</div>
                {/if}

                <div class="form-row">
                    <div class="form-group flex-1">
                        <label for="ip">Camera IP (Optional)</label>
                        <input type="text" id="ip" bind:value={ip} placeholder="e.g. 192.168.0.10" />
                    </div>
                    <div class="form-group flex-1">
                        <label for="port">Camera Port (Optional)</label>
                        <input type="number" id="port" bind:value={port} placeholder="e.g. 5000" />
                    </div>
                </div>

                <div class="form-group" style="max-width: 250px;">
                    <label for="zone_count">Total Zones</label>
                    <input type="number" id="zone_count" bind:value={zone_count} min="1" required />
                </div>

                <div class="appliances-section">
                    <div class="section-header">
                        <h3>Appliances ({appliances.length})</h3>
                        <button type="button" class="btn-add" on:click={addAppliance}>+ Add Appliance</button>
                    </div>

                    <div class="appliances-list">
                        {#each appliances as app, i}
                            <div class="appliance-row">
                                <span class="app-num">{i + 1}.</span>
                                <div class="form-group inline">
                                    <label>Type</label>
                                    <input type="text" bind:value={app.type} placeholder="e.g. AC, Light" required />
                                </div>
                                <div class="form-group inline">
                                    <label>Wattage (W)</label>
                                    <input type="number" bind:value={app.wattage} placeholder="e.g. 1500" required />
                                </div>
                                <div class="form-group inline sm">
                                    <label>Zone</label>
                                    <input type="text" bind:value={app.zone} placeholder="e.g. 1" required />
                                </div>
                                {#if appliances.length > 1}
                                    <button type="button" class="btn-remove" on:click={() => removeAppliance(i)}>✕</button>
                                {/if}
                            </div>
                        {/each}
                    </div>
                </div>

                <div class="form-actions">
                    <button type="submit" class="btn-submit" disabled={loading}>
                        {loading ? 'Creating...' : 'Create Room'}
                    </button>
                </div>
            </form>
        </div>
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
        gap: 2rem;
        background: radial-gradient(circle at 20% 80%, rgba(189,147,249,0.04), transparent 50%);
    }

    .main-content::-webkit-scrollbar { width: 5px; }
    .main-content::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 4px; }

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

    .btn-back {
        background: rgba(98,114,164,0.1);
        color: #8be9fd;
        border: 1px solid rgba(98,114,164,0.3);
        padding: 9px 18px;
        border-radius: 12px;
        text-decoration: none;
        font-size: 0.85rem;
        font-weight: 600;
        transition: all 0.2s;
    }
    .btn-back:hover { background: rgba(98,114,164,0.2); transform: translateY(-1px); }

    .glass {
        background: rgba(18,21,32,0.55);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255,255,255,0.05);
    }

    .form-container {
        padding: 2.5rem;
        border-radius: 18px;
        max-width: 800px;
    }

    .error-banner {
        background: rgba(255, 85, 85, 0.1);
        color: #ff5555;
        border: 1px solid rgba(255, 85, 85, 0.3);
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        font-size: 0.9rem;
        font-weight: 600;
        text-align: center;
    }

    .form-row {
        display: flex;
        gap: 1.5rem;
        flex-wrap: wrap;
    }
    .flex-1 { flex: 1; min-width: 200px; }

    .form-group {
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin-bottom: 1.5rem;
    }
    
    .form-group.inline { margin-bottom: 0; flex: 1; }
    .form-group.inline.sm { flex: 0.5; }
    
    label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #94a3b8;
    }

    input[type="text"], input[type="number"] {
        padding: 12px 16px;
        border-radius: 10px;
        background: rgba(15,23,42,0.6);
        border: 1px solid rgba(255,255,255,0.1);
        color: #f8fafc;
        font-family: inherit;
        font-size: 0.95rem;
        transition: border-color 0.2s;
    }
    input[type="text"]:focus, input[type="number"]:focus {
        outline: none;
        border-color: #50fa7b;
    }

    .appliances-section {
        margin-top: 2rem;
        border-top: 1px solid rgba(255,255,255,0.06);
        padding-top: 1.5rem;
    }

    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    }

    .section-header h3 { margin: 0; font-size: 1.2rem; color: #f8fafc; }

    .btn-add {
        background: rgba(139, 233, 253, 0.1);
        color: #8be9fd;
        border: 1px solid rgba(139, 233, 253, 0.2);
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        font-family: inherit;
    }
    .btn-add:hover { background: rgba(139, 233, 253, 0.2); transform: translateY(-1px); }

    .appliances-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }

    .appliance-row {
        display: flex;
        align-items: flex-end;
        gap: 12px;
        background: rgba(255,255,255,0.02);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.04);
        position: relative;
    }

    .app-num {
        color: #64748b;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 12px;
    }

    .btn-remove {
        background: rgba(255, 85, 85, 0.1);
        color: #ff5555;
        border: 1px solid rgba(255, 85, 85, 0.2);
        width: 38px;
        height: 38px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    .btn-remove:hover { background: rgba(255, 85, 85, 0.2); transform: scale(1.05); }

    .form-actions {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 1rem;
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(255,255,255,0.06);
    }

    .btn-submit {
        background: #50fa7b;
        color: #0f172a;
        border: none;
        padding: 10px 24px;
        border-radius: 10px;
        font-weight: 700;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.2s;
        font-family: inherit;
    }
    .btn-submit:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(80,250,123,0.3);
    }
    .btn-submit:disabled {
        background: #334155;
        color: #94a3b8;
        cursor: not-allowed;
        transform: none;
        box-shadow: none;
    }
</style>
