<script>
    import Login from './routes/Login.svelte';
    import Dashboard from './routes/Dashboard.svelte';
    import Logout from './routes/Logout.svelte';

    // Map paths to components
    const routes = {
        '/': Login,
        '/login': Login,
        '/dashboard': Dashboard,
        '/logout': Logout,
    };

    // Get the current path from the browser's address bar
    const path = window.location.pathname;
    
    // Pick which component to render based on the path
    let page = routes[path] || Login;
</script>

<main>
    <svelte:component this={page} />
</main>