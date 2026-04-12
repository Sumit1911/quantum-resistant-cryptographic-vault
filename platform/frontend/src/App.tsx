import { Link, Navigate, Route, Routes, useLocation } from 'react-router-dom'

import AttackLab from './pages/AttackLab'
import Arena from './pages/Arena'
import Dashboard from './pages/Dashboard'
import Vault from './pages/Vault'

function TopNav() {
  const location = useLocation()

  const links = [
    { to: '/', label: 'Overview' },
    { to: '/arena', label: 'Arena' },
    { to: '/attack', label: 'Attack Lab' },
    { to: '/vault', label: 'Vault Lens' },
  ]

  return (
    <header className="topnav">
      <div className="brand-wrap">
        <p className="brand-kicker">Post-Quantum Research Platform</p>
        <h1 className="brand">CryptoArena</h1>
      </div>
      <nav className="topnav-links">
        {links.map((link) => (
          <Link key={link.to} to={link.to} className={location.pathname === link.to ? 'active' : ''}>
            {link.label}
          </Link>
        ))}
      </nav>
    </header>
  )
}

function App() {
  return (
    <div className="app-shell">
      <div className="bg-orb orb-a" />
      <div className="bg-orb orb-b" />
      <TopNav />
      <main>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/arena" element={<Arena />} />
          <Route path="/attack" element={<AttackLab />} />
          <Route path="/vault" element={<Vault />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
