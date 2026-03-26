<script>
    import { push } from 'svelte-spa-router';

    let username = '';
    let password = '';

    function handleLogin(event) {
        event.preventDefault();
        // In a real app, you would validate credentials here
        console.log('Logging in with', username);
        push('/dashboard');
    }
</script>

<main class="login-container">
    <div class="card">
        <h1>Watt-Watch</h1>
        <p>Please log in to your account.</p>
        
        <form on:submit={handleLogin}>
            <div class="input-group">
                <label for="username">Username</label>
                <input 
                    type="text" 
                    id="username" 
                    bind:value={username} 
                    placeholder="Enter your username" 
                    required 
                />
            </div>
            
            <div class="input-group">
                <label for="password">Password</label>
                <input 
                    type="password" 
                    id="password" 
                    bind:value={password} 
                    placeholder="Enter your password" 
                    required 
                />
            </div>

            <button type="submit">Sign In</button>
        </form>
    </div>
</main>

<style>
    :global(body) {
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: #0f111a;
        color: white;
    }

    .login-container {
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

    form {
        display: flex;
        flex-direction: column;
        text-align: left;
    }

    .input-group {
        margin-bottom: 20px;
    }

    label {
        display: block;
        margin-bottom: 8px;
        font-size: 14px;
        color: #e6e6e6;
        font-weight: 500;
    }

    input {
        width: 100%;
        padding: 12px;
        border-radius: 6px;
        border: 1px solid #333;
        background-color: #0f111a;
        color: white;
        font-size: 16px;
        box-sizing: border-box;
        transition: border-color 0.2s, box-shadow 0.2s;
    }

    input::placeholder {
        color: #4a4a55;
    }

    input:focus {
        border-color: #50fa7b;
        outline: none;
        box-shadow: 0 0 0 2px rgba(80, 250, 123, 0.2);
    }

    button {
        background: #50fa7b;
        color: #0f111a;
        border: none;
        padding: 14px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 16px;
        cursor: pointer;
        transition: opacity 0.2s, transform 0.1s;
        margin-top: 10px;
    }

    button:hover {
        opacity: 0.9;
    }

    button:active {
        transform: translateY(1px);
    }
</style>
