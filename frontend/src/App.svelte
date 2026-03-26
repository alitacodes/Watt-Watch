<script>
    import Router from 'svelte-spa-router';
    
    // Configurable routes passed into the app
    export let routes = {};
</script>

<main>
    <Router {routes} />
</main>

<style>
    main {
        font-family: sans-serif;
        text-align: center;
    }
</style>