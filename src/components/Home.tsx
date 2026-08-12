import { useEffect, useRef, useState } from 'react'
import { Sparkles, ChevronLeft, ChevronRight, Play, Send, X, Mic, Info } from 'lucide-react'
import { MOVIES, type Movie } from '../data'
import { getRecommendedMovies, getTrendingMovies } from '../services/movies'
import PosterImage from './PosterImage'

const HERO_CHIPS = ["What's trending?", 'Movie for tonight', 'Something under 2 hours', 'Book 2 seats']

function HeroPrompt({ onOpenChat }: { onOpenChat: (seed?: string) => void }) {
  const [val, setVal] = useState('')
  const ref = useRef<HTMLTextAreaElement>(null)

  const submit = () => {
    const clean = val.trim()
    if (!clean) return
    onOpenChat(clean)
    setVal('')
  }

  return (
    <div>
      <div
        onClick={() => ref.current?.focus()}
        className="glass group flex cursor-text items-start gap-3 rounded-3xl border p-3 pl-4 transition focus-within:shadow-[0_0_0_2px_transparent] focus-within:[border-image:var(--grad)_1]"
        style={{ borderColor: 'var(--hairline)' }}
      >
        <span className="grad-bg mt-1 grid h-9 w-9 shrink-0 place-items-center rounded-full text-white">
          <Sparkles size={16} className="sparkle" />
        </span>
        <textarea
          ref={ref}
          value={val}
          onChange={(e) => setVal(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submit() }
          }}
          rows={1}
          placeholder="Tell Nia what you want to watch…"
          aria-label="Ask Nia"
          className="min-h-[40px] flex-1 resize-none bg-transparent pt-1.5 text-sm outline-none placeholder:opacity-70 sm:text-base"
          style={{ caretColor: 'var(--red)' }}
        />
        {val && (
          <button onClick={() => { setVal(''); ref.current?.focus() }} aria-label="Clear" className="mt-1 rounded-full p-2 hover:bg-white/10" style={{ color: 'var(--muted)' }}>
            <X size={16} />
          </button>
        )}
        <button type="button" aria-label="Voice input" className="mt-1 hidden rounded-full p-2 hover:bg-white/10 sm:block" style={{ color: 'var(--muted)' }}>
          <Mic size={18} />
        </button>
        <button onClick={submit} disabled={!val.trim()} aria-label="Send" className="grad-bg mt-0.5 grid h-10 w-10 shrink-0 place-items-center rounded-full text-white transition disabled:opacity-40">
          <Send size={16} />
        </button>
      </div>
      <p className="mt-2 pl-2 text-xs" style={{ color: 'var(--muted)' }}>
        Try: Find a funny movie tonight, recommend a thriller, or book 2 seats.
      </p>
      <div className="mt-3 flex flex-wrap gap-2">
        {HERO_CHIPS.map((c) => (
          <button key={c} onClick={() => onOpenChat(c)} className="rounded-full border px-3.5 py-1.5 text-xs font-medium transition hover:bg-white/5 focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--red)]" style={{ borderColor: 'var(--hairline)' }}>
            {c}
          </button>
        ))}
      </div>
    </div>
  )
}

function Hero({ movies, onSelect, onBook }: { movies: Movie[]; onSelect: (m: Movie) => void; onBook: (m: Movie) => void }) {
  const [i, setI] = useState(0)
  const featured = movies.slice(0, 3)
  useEffect(() => {
    if (!featured.length) return
    const t = setInterval(() => setI((v) => (v + 1) % featured.length), 6000)
    return () => clearInterval(t)
  }, [featured.length])
  if (!featured.length) return <div className="h-[440px] animate-pulse rounded-3xl" style={{ background: 'var(--surface)' }} />
  const m = featured[i]

  return (
    <div className="relative overflow-hidden rounded-3xl border" style={{ borderColor: 'var(--hairline)' }}>
      <PosterImage key={m.id + 'bg'} src={m.backdrop} alt="" className="fade-up absolute inset-0 h-full w-full opacity-40" />
      <div className="absolute inset-0" style={{ background: 'linear-gradient(90deg, var(--bg) 12%, transparent 60%), linear-gradient(0deg, var(--bg), transparent 55%)' }} />

      <div className="relative grid gap-6 p-6 sm:p-10 md:grid-cols-[1.1fr_0.9fr] md:items-center">
        <div className="fade-up order-2 md:order-1">
          <h2 onClick={() => onSelect(m)} className="font-display cursor-pointer text-5xl font-extrabold leading-[0.95] transition-colors hover:text-[var(--red)] sm:text-7xl">{m.title}</h2>
          <p className="mt-3 flex flex-wrap items-center gap-2 text-sm font-medium" style={{ color: 'var(--muted)' }}>
            <span className="rounded border px-1.5 py-0.5" style={{ borderColor: 'var(--hairline)' }}>{m.cert}</span>
            <span>{m.languages.join(', ')}</span>
            <span>·</span>
            <span>{m.runtime}</span>
            <span>·</span>
            <span>{m.genres.join(', ')}</span>
          </p>
          <p className="mt-4 line-clamp-3 max-w-lg text-sm leading-relaxed sm:text-base" style={{ color: 'var(--muted)' }}>{m.synopsis}</p>
          <p className="mt-2 text-xs" style={{ color: 'var(--muted)' }}>In cinemas {new Date(m.releaseDate).toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}</p>
          <div className="mt-6 flex flex-wrap items-center gap-3">
            <button onClick={() => onBook(m)} className="grad-bg rounded-full px-7 py-3 text-sm font-semibold text-white">Book Tickets</button>
            <button onClick={() => onSelect(m)} className="flex items-center gap-2 rounded-full border px-5 py-3 text-sm font-semibold" style={{ borderColor: 'var(--hairline)' }}>
              <Play size={15} /> Watch Trailer
            </button>
          </div>
        </div>
        <div className="order-1 hidden justify-end md:order-2 md:flex">
          <button onClick={() => onSelect(m)} aria-label={`View ${m.title}`} className="cursor-pointer transition-transform duration-300 hover:scale-[1.02]">
            <PosterImage key={m.poster} src={m.poster} alt={m.title} className="fade-up h-[380px] w-[260px] rounded-2xl shadow-2xl" />
          </button>
        </div>
      </div>

      <button onClick={() => setI((v) => (v - 1 + featured.length) % featured.length)} aria-label="Previous" className="glass absolute left-4 top-1/2 hidden -translate-y-1/2 rounded-full p-2 md:block" style={{ border: '1px solid var(--hairline)' }}><ChevronLeft size={18} /></button>
      <button onClick={() => setI((v) => (v + 1) % featured.length)} aria-label="Next" className="glass absolute right-4 top-1/2 hidden -translate-y-1/2 rounded-full p-2 md:block" style={{ border: '1px solid var(--hairline)' }}><ChevronRight size={18} /></button>
      <div className="absolute bottom-5 left-1/2 flex -translate-x-1/2 gap-2">
        {featured.map((_, d) => (
          <button key={d} onClick={() => setI(d)} aria-label={`Slide ${d + 1}`} className="h-1.5 rounded-full transition-all" style={{ width: d === i ? 28 : 8, background: d === i ? 'transparent' : 'var(--muted)' }}>
            {d === i && <span className="grad-bg block h-full w-full rounded-full" />}
          </button>
        ))}
      </div>
    </div>
  )
}

function PosterCard({ m, onSelect, onBook, reason }: { m: Movie; onSelect: (m: Movie) => void; onBook: (m: Movie) => void; reason?: boolean }) {
  const [why, setWhy] = useState(false)
  return (
    <div className="group relative shrink-0">
      <div onClick={() => onSelect(m)} className="relative cursor-pointer overflow-hidden rounded-2xl transition-all duration-300 group-hover:-translate-y-1.5 group-hover:shadow-[0_16px_32px_-12px_rgba(23,23,23,0.25)]">
        <PosterImage src={m.poster} alt={m.title} className="aspect-[2/3] w-full" />
        <div className="absolute inset-0 flex items-end gap-2 bg-gradient-to-t from-black/70 via-transparent p-3 opacity-0 transition group-hover:opacity-100">
          <button onClick={(e) => { e.stopPropagation(); onSelect(m) }} className="flex-1 rounded-full border border-white/40 py-2 text-xs font-semibold text-white backdrop-blur">Details</button>
          <button onClick={(e) => { e.stopPropagation(); onBook(m) }} className="grad-bg flex-1 rounded-full py-2 text-xs font-semibold text-white">Book now</button>
        </div>
        <span className="absolute right-2 top-2 rounded-md bg-black/60 px-1.5 py-0.5 text-[11px] font-semibold text-white backdrop-blur">{m.rating} ★</span>
      </div>
      <p className="font-display mt-2 text-base font-bold leading-tight">{m.title}</p>
      <p className="text-[11px]" style={{ color: 'var(--muted)' }}>{m.year} · {m.languages[0]} · {m.genres[0]} · {m.runtime}</p>
      {reason && (
        <div className="mt-0.5 flex items-center gap-1">
          <p className="line-clamp-2 text-xs italic leading-snug" style={{ color: 'var(--muted)' }}>{m.reason}</p>
          <button onClick={() => setWhy((v) => !v)} aria-label="Why this pick?" className="relative shrink-0" style={{ color: 'var(--muted)' }}>
            <Info size={13} />
            {why && (
              <span className="glass fade-up absolute bottom-5 left-1/2 z-20 w-48 -translate-x-1/2 rounded-xl border p-2.5 text-left text-[11px] font-normal not-italic shadow-xl" style={{ borderColor: 'var(--hairline)', color: 'var(--text)' }}>
                Nia matched this to your watch history — {m.genres.join('/')} fans in {m.languages[0]} rated it {m.rating}★ across {m.voteCount.toLocaleString('en-IN')} votes.
              </span>
            )}
          </button>
        </div>
      )}
    </div>
  )
}

const FILTERS = ['All', 'Tamil', 'English', 'Hindi', 'Telugu', 'New Releases', 'IMAX', '3D']

function Row({ id, title, movies, onSelect, onBook, reason }: { id?: string; title: string; movies: Movie[]; onSelect: (m: Movie) => void; onBook: (m: Movie) => void; reason?: boolean }) {
  return (
    <section id={id} className="scroll-mt-24">
      <h3 className="font-display mb-4 text-3xl font-extrabold">{title}</h3>
      <div className="no-scrollbar -mx-4 flex gap-4 overflow-x-auto px-4 pb-2 sm:mx-0 sm:px-0">
        {movies.map((m) => (
          <div key={m.id} className="w-40 sm:w-44"><PosterCard m={m} onSelect={onSelect} onBook={onBook} reason={reason} /></div>
        ))}
      </div>
    </section>
  )
}

export default function Home({ city, onOpenChat, onSelect, onBook }: {
  city: string
  onOpenChat: (seed?: string) => void
  onSelect: (m: Movie) => void
  onBook: (m: Movie) => void
}) {
  const [recommended, setRecommended] = useState<Movie[]>([])
  const [trending, setTrending] = useState<Movie[]>([])
  const [active, setActive] = useState('All')

  useEffect(() => {
    getRecommendedMovies({ city }).then(setRecommended)
    getTrendingMovies().then(setTrending)
  }, [city])

  const allMovies = recommended.length ? recommended : MOVIES
  const heroMovies = trending.length ? trending : allMovies

  const matches = (m: Movie) => {
    if (active === 'All') return true
    if (active === 'New Releases') return m.tags.includes('New')
    if (['IMAX', '3D'].includes(active)) return m.tags.includes(active)
    return m.languages.some((l) => l.toLowerCase() === active.toLowerCase())
  }
  const filtered = allMovies.filter(matches)

  const loading = !recommended.length && !MOVIES.length

  const upcomingMovies = allMovies.filter((m) => m.tags.includes('New')).length
    ? allMovies.filter((m) => m.tags.includes('New'))
    : allMovies.slice(0, 6)

  return (
    <div className="mx-auto max-w-[1280px] space-y-14 px-4 pb-24 pt-6 sm:px-8">
      <HeroPrompt onOpenChat={onOpenChat} />
      <Hero movies={heroMovies} onSelect={onSelect} onBook={onBook} />

      {/* Recommended */}
      <section id="for-you" className="scroll-mt-24">
        <div className="mb-4 flex items-center gap-3">
          <h3 className="font-display text-3xl font-extrabold">Recommended for You</h3>
          <span className="grad-bg flex items-center gap-1 rounded-full px-2.5 py-1 text-[11px] font-semibold text-white">
            <Sparkles size={11} /> Curated by Nia
          </span>
        </div>
        {loading ? (
          <div className="flex gap-4 overflow-hidden">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="aspect-[2/3] w-40 shrink-0 animate-pulse rounded-2xl sm:w-44" style={{ background: 'var(--surface)' }} />
            ))}
          </div>
        ) : (
          <div className="no-scrollbar -mx-4 flex gap-4 overflow-x-auto px-4 pb-2 sm:mx-0 sm:px-0">
            {allMovies.map((m) => (
              <div key={m.id} className="w-40 sm:w-44"><PosterCard m={m} onSelect={onSelect} onBook={onBook} reason /></div>
            ))}
          </div>
        )}
      </section>

      {/* This Week's Releases */}
      <Row id="upcoming" title="This Week's Releases" movies={upcomingMovies} onSelect={onSelect} onBook={onBook} />

      {/* Only in Theatres + filters */}
      <section>
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <h3 className="font-display text-3xl font-extrabold">Only in Theatres · {city.split(',')[0]}</h3>
          <div className="flex flex-wrap gap-2">
            {FILTERS.map((f) => (
              <button
                key={f}
                onClick={() => setActive(f)}
                className="rounded-full border px-3.5 py-1.5 text-xs font-semibold transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--red)]"
                style={active === f
                  ? { background: 'var(--grad)', color: '#fff', borderColor: 'transparent' }
                  : { borderColor: 'var(--hairline)', color: 'var(--muted)' }}
              >
                {f}
              </button>
            ))}
          </div>
        </div>
        {filtered.length ? (
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-5">
            {filtered.map((m) => (
              <PosterCard key={m.id} m={m} onSelect={onSelect} onBook={onBook} />
            ))}
          </div>
        ) : (
          <p className="py-8 text-center text-sm" style={{ color: 'var(--muted)' }}>No movies match this filter right now.</p>
        )}
      </section>
    </div>
  )
}
