import App from './App.svelte';
import Login from './routes/Login.svelte';
import Dashboard from './routes/Dashboard.svelte';

const routes = {
    '/': Login,
    '/login': Login,
    '/dashboard': Dashboard,
    '*': Login
};

const app = new App({
	target: document.body,
	props: {
		routes
	}
});

export default app;