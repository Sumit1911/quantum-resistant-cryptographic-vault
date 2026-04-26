import { Link, Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { useEffect, useState } from 'react'

import AttackLab from './pages/AttackLab'
import Arena from './pages/Arena'
import Vault from './pages/Vault'

function TopNav({
  theme,
  onToggleTheme,
}: {
  theme: 'current' | 'light'
  onToggleTheme: () => void
}) {
  const location = useLocation()

  const links = [
    { to: '/arena', label: 'Arena' },
    { to: '/attack', label: 'Attack Lab' },
    { to: '/vault', label: 'Vault Lens' },
  ]

  return (
    <header className="topnav">
      <div className="brand-wrap">
        <p className="brand-kicker">Research Platform</p>
        <h1 className="brand">Post Quantum Cryptographic Vault</h1>
      </div>
      <nav className="topnav-links">
        {links.map((link) => (
          <Link key={link.to} to={link.to} className={location.pathname === link.to ? 'active' : ''}>
            {link.label}
          </Link>
        ))}
        <button className="theme-toggle" onClick={onToggleTheme} type="button">
          {theme === 'current' ? 'Light Mode' : 'Crypto Mode'}
        </button>
      </nav>
    </header>
  )
}

function App() {
  const [theme, setTheme] = useState<'current' | 'light'>(() => {
    const stored = localStorage.getItem('cryptoarena-theme')
    return stored === 'light' ? 'light' : 'current'
  })

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('cryptoarena-theme', theme)
  }, [theme])

  return (
    <div className="app-shell">
      <TopNav
        theme={theme}
        onToggleTheme={() => setTheme((prev) => (prev === 'current' ? 'light' : 'current'))}
      />
      <main>
        <Routes>
          <Route path="/" element={<Navigate to="/arena" replace />} />
          <Route path="/arena" element={<Arena />} />
          <Route path="/attack" element={<AttackLab />} />
          <Route path="/vault" element={<Vault />} />
          <Route path="*" element={<Navigate to="/arena" replace />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
