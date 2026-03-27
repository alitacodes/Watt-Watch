<script>
    import Login     from './routes/Login.svelte';
    import Dashboard from './routes/Dashboard.svelte';
    import Rooms     from './routes/Rooms.svelte';
    import Report    from './routes/Report.svelte';
    import Logout    from './routes/Logout.svelte';
    import CreateRoom from './routes/CreateRoom.svelte';

    const routes = {
        '/':          Login,
        '/login':     Login,
        '/dashboard': Dashboard,
        '/rooms':     Rooms,
        '/report':    Report,
        '/logout':    Logout,
        '/create-room': CreateRoom,
    };

    const path = window.location.pathname;
    let page = routes[path] || Login;
</script>

<svelte:component this={page} />