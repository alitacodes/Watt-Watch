<script>
    import { onMount } from 'svelte';
    
    let currentUser = null;
    let users = [];
    let errorMessage = '';
    let loading = true;

    onMount(async () => {
        // Get current user info from auth status
        const authRes = await fetch('/api/v1/auth/status');
        if (authRes.ok) {
            const data = await authRes.json();
            currentUser = data;
            console.log('Current user:', currentUser);
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
            } else if (usersRes.status === 403) {
                errorMessage = 'You do not have permission to view users';
            }
        }

        loading = false;
    });

    function handleLogout() {
        window.location.href = '/logout';
    }

    async function deleteUser(userid) {
        if (!confirm(`Are you sure you want to delete user ${userid}?`)) {
            return;
        }

        const res = await fetch(`/api/v1/delete_user/${userid}`, {
            method: 'POST'
        });

        if (res.ok) {
            users = users.filter(u => u.userid !== userid);
            alert('User deleted successfully');
        } else {
            const data = await res.json();
            errorMessage = data.error || 'Failed to delete user';
        }
    }
</script>

<main class="dashboard-container">
    <nav class="navbar">
        <div class="nav-content">
            <h1>Watt-Watch Dashboard</h1>
            <div class="nav-right">
                {#if currentUser}
                    <span class="user-info">
                        {currentUser.userid}
                        <span class="badge" class:admin={currentUser.type === 'admin'} class:mod={currentUser.type === 'mod'}>
                            {currentUser.type.toUpperCase()}
                        </span>
                    </span>
                {/if}
                <button on:click={handleLogout} class="logout-btn">Logout</button>
            </div>
        </div>
    </nav>

    <div class="content">
        {#if loading}
            <div class="loading">Loading...</div>
        {:else}
            <div class="welcome">
                <h2>Welcome, {currentUser?.userid}!</h2>
                <p>User Type: <strong>{currentUser?.type}</strong></p>
            </div>

            {#if errorMessage}
                <div class="error-message">{errorMessage}</div>
            {/if}

            <!-- Admin-Only Section -->
            {#if currentUser?.type === 'admin'}
                <section class="admin-section">
                    <h3>Admin Panel</h3>
                    <div class="users-list">
                        <h4>All Users</h4>
                        {#if users.length > 0}
                            <table>
                                <thead>
                                    <tr>
                                        <th>User ID</th>
                                        <th>Type</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {#each users as user}
                                        <tr>
                                            <td>{user.userid}</td>
                                            <td>
                                                <span class="badge" class:admin={user.type === 'admin'} class:mod={user.type === 'mod'}>
                                                    {user.type.toUpperCase()}
                                                </span>
                                            </td>
                                            <td>
                                                {#if user.userid !== currentUser.userid}
                                                    <button on:click={() => deleteUser(user.userid)} class="delete-btn">Delete</button>
                                                {/if}
                                            </td>
                                        </tr>
                                    {/each}
                                </tbody>
                            </table>
                        {:else}
                            <p>No users found</p>
                        {/if}
                    </div>
                </section>
            {/if}

            <!-- Mod & Admin Section -->
            {#if currentUser?.type === 'admin' || currentUser?.type === 'mod'}
                <section class="mod-section">
                    <h3>Activity Dashboard</h3>
                    <p>View and manage recent activities here.</p>
                </section>
            {/if}

            <!-- General Section -->
            <section class="general-section">
                <h3>General Information</h3>
                <p>Your session is active. You can navigate through the application.</p>
            </section>
        {/if}
    </div>
</main>

<style>
    :global(body) {
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: #0f111a;
        color: white;
    }

    .dashboard-container {
        display: flex;
        flex-direction: column;
        height: 100vh;
    }

    .navbar {
        background: #1a1d27;
        border-bottom: 2px solid #50fa7b;
        padding: 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }

    .nav-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.5rem 2rem;
        max-width: 1400px;
        margin: 0 auto;
        width: 100%;
    }

    .navbar h1 {
        margin: 0;
        color: #50fa7b;
        font-size: 1.8rem;
    }

    .nav-right {
        display: flex;
        align-items: center;
        gap: 20px;
    }

    .user-info {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 0.95rem;
    }

    .badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: bold;
    }

    .badge.admin {
        background-color: #ff5555;
        color: white;
    }

    .badge.mod {
        background-color: #ffaa00;
        color: white;
    }

    .logout-btn {
        background: #50fa7b;
        color: #0f111a;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: bold;
        cursor: pointer;
        transition: opacity 0.2s;
    }

    .logout-btn:hover {
        opacity: 0.8;
    }

    .content {
        flex: 1;
        padding: 2rem;
        max-width: 1400px;
        margin: 0 auto;
        width: 100%;
        overflow-y: auto;
    }

    .loading {
        text-align: center;
        padding: 2rem;
        font-size: 1.2rem;
    }

    .welcome {
        background: #1a1d27;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        border-left: 4px solid #50fa7b;
    }

    .welcome h2 {
        margin: 0 0 0.5rem 0;
    }

    .welcome p {
        margin: 0;
        color: #a8a8b3;
    }

    .error-message {
        background-color: rgba(255, 85, 85, 0.1);
        color: #ff5555;
        border: 1px solid #ff5555;
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 1.5rem;
    }

    section {
        background: #1a1d27;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 2rem;
    }

    section h3 {
        margin-top: 0;
        color: #50fa7b;
    }

    .admin-section {
        border-left: 4px solid #ff5555;
    }

    .mod-section {
        border-left: 4px solid #ffaa00;
    }

    .general-section {
        border-left: 4px solid #50fa7b;
    }

    .users-list h4 {
        margin-top: 0;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
    }

    thead {
        background: #333;
    }

    th, td {
        padding: 0.75rem 1rem;
        text-align: left;
        border-bottom: 1px solid #333;
    }

    th {
        font-weight: bold;
        color: #50fa7b;
    }

    tbody tr:hover {
        background: #222;
    }

    .delete-btn {
        background: #ff5555;
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.85rem;
        transition: opacity 0.2s;
    }

    .delete-btn:hover {
        opacity: 0.8;
    }
</style>