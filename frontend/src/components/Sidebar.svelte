<script>
    export let active = 'dashboard';
    export let currentUser = null;

    function handleLogout() {
        window.location.href = '/logout';
    }

    const navItems = [
        { id: 'dashboard', label: 'Dashboard', icon: '📊', href: '/dashboard' },
        { id: 'rooms',     label: 'Rooms',     icon: '🏠', href: '/rooms'     },
        { id: 'report',    label: 'Report',    icon: '📄', href: '/report'    },
    ];
</script>

<nav class="sidebar">
    <div class="logo">
        <span class="bolt">⚡</span>
        <span class="logo-text">Watt-Watch</span>
    </div>

    <div class="nav-links">
        {#each navItems as item}
            <a
                href={item.href}
                class="nav-item"
                class:active={active === item.id}
                id="nav-{item.id}"
            >
                <span class="nav-icon">{item.icon}</span>
                <span class="nav-label">{item.label}</span>
                {#if active === item.id}
                    <span class="active-pip"></span>
                {/if}
            </a>
        {/each}
    </div>

    <div class="spacer"></div>

    <button class="nav-item logout-btn" on:click={handleLogout} id="nav-logout">
        <span class="nav-icon">🚪</span>
        <span class="nav-label">Logout</span>
    </button>

    {#if currentUser}
        <div class="user-profile">
            <div class="avatar">{currentUser.userid[0].toUpperCase()}</div>
            <div class="user-meta">
                <span class="username">{currentUser.userid}</span>
                <span class="role">{currentUser.type.toUpperCase()}</span>
            </div>
        </div>
    {/if}
</nav>

<style>
    .sidebar {
        width: 240px;
        min-width: 240px;
        background: rgba(10, 12, 20, 0.97);
        border-right: 1px solid rgba(255, 255, 255, 0.04);
        display: flex;
        flex-direction: column;
        padding: 1.8rem 1.2rem;
        gap: 0.3rem;
        height: 100vh;
        box-sizing: border-box;
    }

    .logo {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 2.5rem;
        padding-left: 0.4rem;
    }

    .bolt {
        font-size: 1.4rem;
        background: linear-gradient(135deg, #50fa7b, #8be9fd);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .logo-text {
        font-size: 1.25rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #f8fafc;
    }

    .nav-links {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }

    .nav-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 11px 14px;
        text-decoration: none;
        color: #64748b;
        border-radius: 12px;
        transition: all 0.2s ease;
        position: relative;
        font-size: 0.92rem;
        font-weight: 500;
        cursor: pointer;
        border: none;
        background: transparent;
        font-family: inherit;
        width: 100%;
        text-align: left;
    }

    .nav-item:hover {
        background: rgba(80, 250, 123, 0.07);
        color: #e2e8f0;
    }

    .nav-item.active {
        background: rgba(80, 250, 123, 0.12);
        color: #50fa7b;
    }

    .nav-icon {
        font-size: 1rem;
        width: 20px;
        text-align: center;
    }

    .active-pip {
        width: 5px;
        height: 5px;
        border-radius: 50%;
        background: #50fa7b;
        box-shadow: 0 0 8px #50fa7b;
        margin-left: auto;
    }

    .logout-btn {
        color: #64748b;
        margin-bottom: 0.5rem;
    }

    .logout-btn:hover {
        background: rgba(255, 85, 85, 0.1);
        color: #ff5555;
    }

    .spacer { flex: 1; }

    .user-profile {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.04);
        padding: 0.9rem 1rem;
        border-radius: 14px;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 0.5rem;
    }

    .avatar {
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, #bd93f9, #ff79c6);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.9rem;
        color: #fff;
        flex-shrink: 0;
    }

    .user-meta {
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }

    .username {
        font-weight: 600;
        font-size: 0.85rem;
        color: #e2e8f0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .role {
        font-size: 0.65rem;
        color: #50fa7b;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
</style>
