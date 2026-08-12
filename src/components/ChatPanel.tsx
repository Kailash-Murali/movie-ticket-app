import { useEffect, useRef, useState } from 'react'
import { Sparkles, X, Send, Ticket, Check, Mic } from 'lucide-react'
import { MOVIES, type Movie } from '../data'
import { getRecommendedMovies } from '../services/movies'
import PosterImage from './PosterImage'

type RichCard =
  | { kind: 'movies'; movies: Movie[] }
  | { kind: 'seats'; seats: string; screen: string }
  | { kind: 'confirmation'; movie: string; seats: string; total: number }

type Msg = {
  id: number
  role: 'nia' | 'user'
  text?: string
  card?: RichCard
}

const QUICK_REPLIES = [
  'Find a movie for tonight',
  "What's popular near me?",
  'Recommend something like an action thriller',
  'Help me choose seats',
]

let idc = 100

async function reply(text: string): Promise<Msg[]> {
  const t = text.toLowerCase()
  if (t.includes('seat') || t.includes('back') || t.includes('together') || t.includes('cheap') || t.includes('row')) {
    return [
      { id: idc++, role: 'nia', text: 'Found 2 seats together near the back with a clean sightline. Want me to hold them?' },
      { id: idc++, role: 'nia', card: { kind: 'seats', seats: 'H10, H11', screen: 'Screen 3 · Fabula Luxe' } },
    ]
  }
  if (t.includes('book') && (t.includes('tonight') || t.includes('2') || t.includes('seat'))) {
    return [
      { id: idc++, role: 'nia', text: 'Locked in for tonight. Here is your confirmation.' },
      { id: idc++, role: 'nia', card: { kind: 'confirmation', movie: 'The Odyssey', seats: 'H10, H11', total: 940 } },
    ]
  }
  const movies = await getRecommendedMovies()
  return [
    { id: idc++, role: 'nia', text: 'I found these options near you. Would you like the earliest show, the best-rated option, or seats together?' },
    { id: idc++, role: 'nia', card: { kind: 'movies', movies: movies.slice(0, 3) } },
  ]
}

function MovieRichCard({ m, onView, onShowtimes, onBook }: {
  m: Movie
  onView: (m: Movie) => void
  onShowtimes: (m: Movie) => void
  onBook: (m: Movie) => void
}) {
  return (
    <div className="flex gap-3 rounded-xl border p-2.5" style={{ borderColor: 'var(--hairline)', background: 'var(--surface)' }}>
      <PosterImage src={m.poster} alt={m.title} className="h-24 w-16 shrink-0 rounded-lg" />
      <div className="min-w-0 flex-1">
        <p className="font-display text-sm font-bold leading-tight">{m.title}</p>
        <p className="text-[11px]" style={{ color: 'var(--muted)' }}>{m.rating} ★ · {m.runtime} · {m.languages[0]}</p>
        <div className="mt-1.5 flex flex-wrap gap-1">
          <button onClick={() => onView(m)} className="rounded-full border px-2 py-1 text-[10px] font-semibold" style={{ borderColor: 'var(--hairline)' }}>View</button>
          <button onClick={() => onShowtimes(m)} className="rounded-full border px-2 py-1 text-[10px] font-semibold" style={{ borderColor: 'var(--hairline)' }}>Showtimes</button>
          <button onClick={() => onBook(m)} className="grad-bg rounded-full px-2.5 py-1 text-[10px] font-semibold text-white">Book now</button>
        </div>
      </div>
    </div>
  )
}

export default function ChatPanel({
  open,
  onClose,
  seed,
  onView,
  onShowtimes,
  onBook,
}: {
  open: boolean
  onClose: () => void
  seed?: string
  onView: (m: Movie) => void
  onShowtimes: (m: Movie) => void
  onBook: (m: Movie) => void
}) {
  const [messages, setMessages] = useState<Msg[]>([
    { id: 1, role: 'nia', text: "Hi, I'm Nia. Tell me your mood, preferred language, location, or how many seats you need." },
  ])
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const seededRef = useRef<string | undefined>(undefined)

  const push = (text: string) => {
    const clean = text.trim()
    if (!clean) return
    setMessages((m) => [...m, { id: idc++, role: 'user', text: clean }])
    setInput('')
    setTyping(true)
    reply(clean).then((msgs) => {
      setTyping(false)
      setMessages((m) => [...m, ...msgs])
      inputRef.current?.focus()
    })
  }

  // A seeded prompt (from the hero prompt) becomes the first user message.
  useEffect(() => {
    if (open && seed && seed !== seededRef.current) {
      seededRef.current = seed
      push(seed)
    } else if (open) {
      setTimeout(() => inputRef.current?.focus(), 120)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, seed])

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, typing])

  // Close on Escape.
  useEffect(() => {
    if (!open) return
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open, onClose])

  if (!open) return null

  const book = (m: Movie) => { onBook(m); onClose() }
  const view = (m: Movie) => { onView(m); onClose() }
  const showtimes = (m: Movie) => { onShowtimes(m); onClose() }

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <button aria-label="Close chat" onClick={onClose} className="absolute inset-0 bg-black/50" />
      <aside
        className="slide-in glass relative flex h-full w-full flex-col border-l sm:w-[360px] lg:w-[400px]"
        style={{ borderColor: 'var(--hairline)', borderTopLeftRadius: 24 }}
      >
        <header className="flex items-center gap-3 border-b p-4" style={{ borderColor: 'var(--hairline)' }}>
          <div className="grad-bg grid h-10 w-10 place-items-center rounded-full text-white">
            <Sparkles size={18} />
          </div>
          <div className="flex-1">
            <p className="font-display text-lg font-bold leading-none">Nia</p>
            <p className="text-xs" style={{ color: 'var(--muted)' }}>Your movie concierge · online</p>
          </div>
          <button onClick={onClose} aria-label="Close" className="rounded-full p-2 hover:bg-white/10" style={{ color: 'var(--muted)' }}>
            <X size={18} />
          </button>
        </header>

        <div ref={scrollRef} className="no-scrollbar flex-1 space-y-3 overflow-y-auto p-4">
          {messages.map((m) => (
            <div key={m.id} className={`fade-up flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`max-w-[88%] rounded-2xl px-3.5 py-2.5 text-sm ${m.role === 'user' ? 'text-white' : ''}`}
                style={
                  m.role === 'user'
                    ? { background: 'var(--red)', borderBottomRightRadius: 6 }
                    : { background: 'var(--red-tint)', color: 'var(--text)', borderBottomLeftRadius: 6 }
                }
              >
                {m.text && <p className="leading-snug">{m.text}</p>}
                {m.card?.kind === 'movies' && (
                  <div className="mt-2 space-y-2">
                    {m.card.movies.map((mv) => (
                      <MovieRichCard key={mv.id} m={mv} onView={view} onShowtimes={showtimes} onBook={book} />
                    ))}
                  </div>
                )}
                {m.card?.kind === 'seats' && (
                  <div className="mt-2 rounded-xl border p-3" style={{ borderColor: 'var(--hairline)', background: 'var(--surface)' }}>
                    <p className="text-xs" style={{ color: 'var(--muted)' }}>{m.card.screen}</p>
                    <p className="font-display text-2xl font-bold grad-text">{m.card.seats}</p>
                    <button className="grad-bg mt-2 w-full rounded-full py-1.5 text-xs font-semibold text-white">Hold these seats</button>
                  </div>
                )}
                {m.card?.kind === 'confirmation' && (
                  <div className="mt-2 rounded-xl border p-3" style={{ borderColor: 'var(--hairline)', background: 'var(--surface)' }}>
                    <div className="flex items-center gap-2">
                      <div className="grad-bg grid h-8 w-8 place-items-center rounded-full text-white"><Check size={16} /></div>
                      <div>
                        <p className="font-display text-base font-bold leading-none">{m.card.movie}</p>
                        <p className="text-[11px]" style={{ color: 'var(--muted)' }}>Seats {m.card.seats}</p>
                      </div>
                    </div>
                    <div className="mt-2 flex items-center justify-between text-xs">
                      <span style={{ color: 'var(--muted)' }}>Paid</span>
                      <span className="font-semibold">₹{m.card.total}</span>
                    </div>
                    <button className="mt-2 flex w-full items-center justify-center gap-1.5 rounded-full border py-1.5 text-xs font-semibold" style={{ borderColor: 'var(--hairline)' }}><Ticket size={13} /> Download ticket</button>
                  </div>
                )}
              </div>
            </div>
          ))}
          {typing && (
            <div className="fade-up flex items-center gap-2 justify-start">
              <div className="flex gap-1 rounded-2xl px-4 py-3" style={{ background: 'var(--surface-2)' }}>
                {[0, 1, 2].map((i) => (
                  <span key={i} className="sparkle h-1.5 w-1.5 rounded-full" style={{ background: 'var(--muted)', animationDelay: `${i * 0.2}s` }} />
                ))}
              </div>
              <span className="text-xs" style={{ color: 'var(--muted)' }}>Nia is finding the best options…</span>
            </div>
          )}
        </div>

        <div className="no-scrollbar flex gap-2 overflow-x-auto px-4 pb-2">
          {QUICK_REPLIES.map((q) => (
            <button
              key={q}
              onClick={() => push(q)}
              className="shrink-0 rounded-full border px-3 py-1.5 text-xs font-medium transition hover:bg-white/5 focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--red)]"
              style={{ borderColor: 'var(--hairline)' }}
            >
              {q}
            </button>
          ))}
        </div>

        <form
          onSubmit={(e) => { e.preventDefault(); push(input) }}
          className="flex items-center gap-2 border-t p-3"
          style={{ borderColor: 'var(--hairline)' }}
        >
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask Nia anything…"
            className="flex-1 rounded-full px-4 py-2.5 text-sm outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--red)]"
            style={{ background: 'var(--surface-2)' }}
          />
          <button type="button" aria-label="Voice input" className="grid h-10 w-10 shrink-0 place-items-center rounded-full border" style={{ borderColor: 'var(--hairline)', color: 'var(--muted)' }}>
            <Mic size={16} />
          </button>
          <button type="submit" disabled={!input.trim()} aria-label="Send" className="grad-bg grid h-10 w-10 shrink-0 place-items-center rounded-full text-white transition disabled:opacity-40">
            <Send size={16} />
          </button>
        </form>
      </aside>
    </div>
  )
}
