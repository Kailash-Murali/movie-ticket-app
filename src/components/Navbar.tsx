import { useState } from 'react'
import { MapPin, Search, Bell, Sun, Moon, ChevronDown, Menu, X } from 'lucide-react'
import { CITIES } from '../data'

const TABS = ['Movies', 'For You', 'Upcoming']

export default function Navbar({
  city,
  setCity,
  dark,
  toggleTheme,
  onHome,
  onNavigate,
}: {
  city: string
  setCity: (c: string) => void
  dark: boolean
  toggleTheme: () => void
  onHome: () => void
  onNavigate: (tab: string) => void
}) {
  const [tab, setTab] = useState('Movies')
  const [cityOpen, setCityOpen] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <header className="glass sticky top-0 z-40 border-b" style={{ borderColor: 'var(--hairline)' }}>
      <div className="mx-auto flex h-16 max-w-[1280px] items-center gap-4 px-4 sm:px-8">
        {/* Mobile menu toggle */}
        <button onClick={() => setMenuOpen((v) => !v)} aria-label="Menu" aria-expanded={menuOpen} className="rounded-full p-2 hover:bg-white/5 lg:hidden" style={{ color: 'var(--muted)' }}>
          {menuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>

        {/* Logo + city */}
        <button onClick={onHome} className="font-display text-2xl font-extrabold tracking-tight">
          Fabula<span className="grad-text">.</span>
        </button>

        <div className="relative hidden sm:block">
          <button
            onClick={() => setCityOpen((v) => !v)}
            className="flex items-center gap-1.5 border-l pl-4 text-sm"
            style={{ borderColor: 'var(--hairline)' }}
          >
            <MapPin size={15} className="grad-text" />
            <span className="font-medium">{city}</span>
            <ChevronDown size={14} style={{ color: 'var(--muted)' }} />
          </button>
          {cityOpen && (
            <div className="glass fade-up absolute left-4 top-10 z-50 w-56 rounded-2xl border p-1.5 shadow-2xl" style={{ borderColor: 'var(--hairline)' }}>
              {CITIES.map((c) => (
                <button
                  key={c}
                  onClick={() => { setCity(c); setCityOpen(false) }}
                  className={`block w-full rounded-xl px-3 py-2 text-left text-sm hover:bg-white/5 ${c === city ? 'grad-text font-semibold' : ''}`}
                >
                  {c}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Center tabs */}
        <nav className="mx-auto hidden items-center gap-8 lg:flex">
          {TABS.map((t) => (
            <button key={t} onClick={() => { setTab(t); onNavigate(t) }} className="relative py-5 text-sm font-medium transition-colors hover:text-[var(--red)]" style={{ color: t === tab ? 'var(--red)' : 'var(--muted)' }}>
              {t}
              {t === tab && <span className="grad-bg absolute inset-x-0 bottom-0 h-[3px] rounded-full" />}
            </button>
          ))}
        </nav>

        {/* Right actions */}
        <div className="ml-auto flex items-center gap-1 lg:ml-0">
          <button className="rounded-full p-2.5 hover:bg-white/5" style={{ color: 'var(--muted)' }}><Search size={18} /></button>
          <button onClick={toggleTheme} className="rounded-full p-2.5 hover:bg-white/5" style={{ color: 'var(--muted)' }}>
            {dark ? <Sun size={18} /> : <Moon size={18} />}
          </button>
          <button className="relative rounded-full p-2.5 hover:bg-white/5" style={{ color: 'var(--muted)' }}>
            <Bell size={18} />
            <span className="grad-bg absolute right-2 top-2 h-2 w-2 rounded-full" />
          </button>
          <button className="grad-bg ml-1 grid h-9 w-9 place-items-center rounded-full font-display text-sm font-bold text-white">K</button>
        </div>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="fade-up border-t px-4 py-4 lg:hidden" style={{ borderColor: 'var(--hairline)' }}>
          <button className="mb-3 flex items-center gap-1.5 text-sm font-medium">
            <MapPin size={15} className="grad-text" /> {city}
          </button>
          <nav className="flex flex-col">
            {TABS.map((t) => (
              <button
                key={t}
                onClick={() => { setTab(t); setMenuOpen(false); onNavigate(t) }}
                className="rounded-xl px-3 py-2.5 text-left text-sm font-medium"
                style={{ color: t === tab ? 'var(--red)' : 'var(--muted)', background: t === tab ? 'var(--red-tint)' : 'transparent' }}
              >
                {t}
              </button>
            ))}
          </nav>
          <div className="mt-3 flex flex-wrap gap-1.5">
            {CITIES.map((c) => (
              <button
                key={c}
                onClick={() => { setCity(c); setMenuOpen(false) }}
                className="rounded-full border px-3 py-1.5 text-xs"
                style={c === city ? { borderColor: 'transparent', background: 'var(--grad)', color: '#fff' } : { borderColor: 'var(--hairline)', color: 'var(--muted)' }}
              >
                {c.split(',')[0]}
              </button>
            ))}
          </div>
        </div>
      )}
    </header>
  )
}
