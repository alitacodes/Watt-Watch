import { useState } from 'react'
import WattWatchDashboard from './dashboard'
import Login from './login'

function App() {
  const [page, setPage] = useState('dashboard') // 'dashboard' | 'login'

  return page === 'login'
    ? <Login onNavigateToDashboard={() => setPage('dashboard')} />
    : <WattWatchDashboard onNavigateToLogin={() => setPage('login')} />
}

export default App
