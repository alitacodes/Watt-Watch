<script>
    import { onMount } from 'svelte';

    async function handleLogout() {
        try {
            const response = await fetch('/api/v1/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                // Redirect to login page after successful logout
                window.location.href = '/login';
            } else {
                const data = await response.json();
                console.error('Logout failed:', data.error);
                window.location.href = '/login';
            }
        } catch (error) {
            console.error('Logout error:', error);
            window.location.href = '/login';
        }
    }

    onMount(() => {
        // Automatically logout when this component mounts
        handleLogout();
    });
</script>

<main class="logout-container">
    <div class="card">
        <h1>Watt-Watch</h1>
        <p>Logging you out...</p>
        <div class="spinner"></div>
    </div>
</main>

<style>
    :global(body) {
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: #0f111a;
        color: white;
    }

    .logout-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
    }

    .card {
        background: #1a1d27;
        padding: 40px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
        width: 100%;
        max-width: 380px;
    }

    h1 {
        margin-top: 0;
        color: #50fa7b;
        margin-bottom: 10px;
    }

    p {
        color: #a8a8b3;
        margin-bottom: 30px;
    }

    .spinner {
        border: 4px solid #333;
        border-top: 4px solid #50fa7b;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 0 auto;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>
