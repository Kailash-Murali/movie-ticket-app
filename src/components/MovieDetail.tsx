import { useState } from 'react'
import { Play, Sparkles, Send, ChevronLeft, Clock, Calendar, Star } from 'lucide-react'
import type { Movie } from '../data'
import PosterImage from './PosterImage'

function AskBox({ title, onOpenChat }: { title: string; onOpenChat: (seed?: string) => void }) {
  const [q, setQ] = useState('')
  // Submitting hands the question straight to the side-bar chatbot: it opens the
  // drawer, seeds the typed text as the first user message, then focuses the chat.
  const handoff = () => {
    const clean = q.trim()
    onOpenChat(clean ? `About ${title}: ${clean}` : `Tell me about ${title}`)
    setQ('')
  }
  return (
    <div className="rounded-2xl border p-5" style={{ borderColor: 'var(--hairline)', background: 'var(--surface)' }}>
      <div className="mb-3 flex items-center gap-2">
        <span className="grad-bg grid h-7 w-7 place-items-center rounded-full text-white"><Sparkles size={14} /></span>
        <p className="font-display text-lg font-bold">Ask Nia about {title}</p>
        <span className="ml-auto rounded-full px-2 py-0.5 text-[10px] font-semibold" style={{ background: 'var(--surface-2)', color: 'var(--muted)' }}>spoiler-safe</span>
      </div>
      <form onSubmit={(e) => { e.preventDefault(); handoff() }} className="flex gap-2">
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Is it scary? Worth watching? Good for kids?" className="flex-1 rounded-full px-4 py-2.5 text-sm outline-none" style={{ background: 'var(--surface-2)' }} />
        <button aria-label="Ask Nia" className="grad-bg grid h-10 w-10 shrink-0 place-items-center rounded-full text-white"><Send size={15} /></button>
      </form>
    </div>
  )
}

const TABS = ['Synopsis', 'Trailers & Videos', 'Cast & Crew']

export default function MovieDetail({ m, onBack, onBook, onOpenChat }: { m: Movie; onBack: () => void; onBook: (m: Movie) => void; onOpenChat: (seed?: string) => void }) {
  const [tab, setTab] = useState('Synopsis')

  return (
    <div className="pb-28">
      {/* Banner */}
      <div className="relative h-[46vh] min-h-[340px] w-full overflow-hidden">
        <PosterImage src={m.backdrop} alt="" className="h-full w-full" />
        <div className="absolute inset-0" style={{ background: 'linear-gradient(0deg, var(--bg) 5%, transparent 70%), linear-gradient(90deg, var(--bg) 0%, transparent 50%)' }} />
        <button onClick={onBack} className="glass absolute left-4 top-4 flex items-center gap-1 rounded-full px-3 py-2 text-sm sm:left-8" style={{ border: '1px solid var(--hairline)' }}><ChevronLeft size={16} /> Back</button>
      </div>

      <div className="mx-auto -mt-40 max-w-[1280px] px-4 sm:px-8">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-end">
          <div className="relative shrink-0">
            <PosterImage src={m.poster} alt={m.title} className="h-[300px] w-[200px] rounded-2xl shadow-2xl" />
            <button className="glass absolute inset-0 m-auto grid h-16 w-16 place-items-center rounded-full text-white" style={{ border: '1px solid rgba(255,255,255,0.3)' }}>
              <Play size={26} fill="currentColor" />
            </button>
          </div>
          <div className="pb-2">
            <h1 className="font-display text-5xl font-extrabold sm:text-6xl">{m.title}</h1>
            <div className="mt-2 flex flex-wrap items-center gap-3 text-sm" style={{ color: 'var(--muted)' }}>
              <span className="flex items-center gap-1 font-semibold" style={{ color: 'var(--text)' }}><Star size={14} className="grad-text" fill="currentColor" /> {m.rating}/10</span>
              <span className="rounded border px-1.5 py-0.5" style={{ borderColor: 'var(--hairline)' }}>{m.cert}</span>
              <span className="flex items-center gap-1"><Clock size={13} /> {m.runtime}</span>
              <span className="flex items-center gap-1"><Calendar size={13} /> {new Date(m.releaseDate).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}</span>
              <span>{m.genres.join(' · ')}</span>
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {m.languages.map((l) => (
                <span key={l} className="rounded-full px-3 py-1 text-xs font-medium" style={{ background: 'var(--surface-2)' }}>{l}</span>
              ))}
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="mt-8 flex gap-6 border-b" style={{ borderColor: 'var(--hairline)' }}>
          {TABS.map((t) => (
            <button key={t} onClick={() => setTab(t)} className="relative pb-3 text-sm font-semibold transition" style={{ color: t === tab ? 'var(--text)' : 'var(--muted)' }}>
              {t}
              {t === tab && <span className="grad-bg absolute inset-x-0 bottom-0 h-[3px] rounded-full" />}
            </button>
          ))}
        </div>

        <div className="grid gap-8 py-8 lg:grid-cols-[1.5fr_1fr]">
          <div className="space-y-8">
            {tab === 'Synopsis' && <p className="max-w-2xl text-base leading-relaxed" style={{ color: 'var(--muted)' }}>{m.synopsis}</p>}
            {tab === 'Trailers & Videos' && (
              <div className="grid grid-cols-2 gap-3">
                {[m.backdrop, m.poster].map((src, i) => (
                  <div key={i} className="relative aspect-video overflow-hidden rounded-xl">
                    <img src={src} alt="" className="h-full w-full object-cover" />
                    <span className="glass absolute inset-0 m-auto grid h-12 w-12 place-items-center rounded-full text-white"><Play size={18} fill="currentColor" /></span>
                  </div>
                ))}
              </div>
            )}
            {(tab === 'Cast & Crew' || tab === 'Synopsis') && (
              <div>
                <h3 className="font-display mb-4 text-2xl font-bold">Cast & Crew</h3>
                <div className="flex flex-wrap gap-6">
                  {m.cast.map((c) => (
                    <div key={c.name} className="w-20 text-center">
                      <img src={c.photo} alt={c.name} className="h-20 w-20 rounded-full object-cover" style={{ background: 'var(--surface-2)' }} />
                      <p className="mt-1.5 text-xs font-semibold leading-tight">{c.name}</p>
                      <p className="text-[11px]" style={{ color: 'var(--muted)' }}>{c.role}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
          <AskBox title={m.title} onOpenChat={onOpenChat} />
        </div>
      </div>

      {/* Sticky book bar */}
      <div className="glass fixed inset-x-0 bottom-0 z-30 border-t" style={{ borderColor: 'var(--hairline)' }}>
        <div className="mx-auto flex max-w-[1280px] items-center gap-4 px-4 py-3 sm:px-8">
          <div className="hidden sm:block">
            <p className="font-display text-lg font-bold leading-none">{m.title}</p>
            <p className="text-xs" style={{ color: 'var(--muted)' }}>from ₹190 · {m.languages.join(', ')}</p>
          </div>
          <button onClick={() => onBook(m)} className="grad-bg ml-auto rounded-full px-8 py-3 text-sm font-semibold text-white">Book Tickets</button>
        </div>
      </div>
    </div>
  )
}
