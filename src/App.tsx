import { useEffect, useState } from 'react'
import { Sparkles } from 'lucide-react'
import Navbar from './components/Navbar'
import Home from './components/Home'
import MovieDetail from './components/MovieDetail'
import SeatSelection from './components/SeatSelection'
import Confirmation, { type Booking } from './components/Confirmation'
import ChatPanel from './components/ChatPanel'
import { MOVIES, type Movie } from './data'

type View = 'home' | 'detail' | 'seats' | 'confirm'

export default function App() {
  const [view, setView] = useState<View>('home')
  const [movie, setMovie] = useState<Movie>(MOVIES[0])
  const [booking, setBooking] = useState<Booking | null>(null)
  const [city, setCity] = useState('Chennai, Tamil Nadu')
  const [dark, setDark] = useState(false)

  const [chatOpen, setChatOpen] = useState(false)
  const [chatSeed, setChatSeed] = useState<string | undefined>(undefined)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
  }, [dark])

  const go = (v: View) => { setView(v); window.scrollTo(0, 0) }

  const openChat = (seed?: string) => { setChatSeed(seed); setChatOpen(true) }

  const selectMovie = (m: Movie) => { setMovie(m); go('detail') }
  const bookMovie = (m: Movie) => { setMovie(m); go('seats') }

  // Smooth-scroll the home page to a section; return home first if elsewhere.
  const navigate = (tab: string) => {
    const scroll = () => {
      if (tab === 'Movies') { window.scrollTo({ top: 0, behavior: 'smooth' }); return }
      const id = tab === 'For You' ? 'for-you' : 'upcoming'
      document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
    if (view !== 'home') { setView('home'); setTimeout(scroll, 80) } else scroll()
  }

  return (
    <div className="min-h-screen">
      <Navbar city={city} setCity={setCity} dark={dark} toggleTheme={() => setDark((d) => !d)} onHome={() => go('home')} onNavigate={navigate} />

      {view === 'home' && <Home city={city} onOpenChat={openChat} onSelect={selectMovie} onBook={bookMovie} />}
      {view === 'detail' && <MovieDetail m={movie} onBack={() => go('home')} onBook={bookMovie} onOpenChat={openChat} />}
      {view === 'seats' && (
        <SeatSelection
          m={movie}
          onBack={() => go('detail')}
          onConfirm={(data) => { setBooking(data); go('confirm') }}
        />
      )}
      {view === 'confirm' && booking && <Confirmation m={movie} booking={booking} onHome={() => go('home')} />}

      {view === 'home' && (
        <footer className="mx-auto max-w-[1280px] border-t px-4 py-8 text-xs sm:px-8" style={{ borderColor: 'var(--hairline)', color: 'var(--muted)' }}>
          <div className="flex flex-wrap items-center justify-between gap-4">
            <p className="font-display text-lg font-bold" style={{ color: 'var(--text)' }}>Fabula<span className="grad-text">.</span></p>
            <nav className="flex flex-wrap gap-5">
              {['Movies', 'For You', 'Upcoming', 'Help', 'Privacy', 'Terms'].map((l) => (
                <a key={l} href="#" className="font-medium transition-colors hover:text-[var(--red)]">{l}</a>
              ))}
            </nav>
          </div>
          <p className="mt-4 max-w-xl leading-relaxed">
            This product uses the TMDB API but is not endorsed or certified by TMDB. Showtimes, pricing, and availability are illustrative.
          </p>
        </footer>
      )}

      {/* Floating AI button — single circle with a tight halo, no adjacent pill/text.
          Hidden on the seat view so it never overlaps the sticky booking summary/CTA. */}
      {!chatOpen && view !== 'seats' && (
        <button
          onClick={() => openChat()}
          title="Ask Nia"
          className="pulse-ring grad-bg fixed bottom-6 right-6 z-40 grid h-14 w-14 place-items-center rounded-full text-white shadow-xl transition hover:scale-105"
          aria-label="Ask Nia, your movie concierge"
        >
          <Sparkles size={24} />
        </button>
      )}

      <ChatPanel
        open={chatOpen}
        onClose={() => setChatOpen(false)}
        seed={chatSeed}
        onView={selectMovie}
        onShowtimes={bookMovie}
        onBook={bookMovie}
      />
    </div>
  )
}
