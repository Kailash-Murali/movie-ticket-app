import { useMemo, useState } from 'react'
import { ChevronLeft, Play } from 'lucide-react'
import { SHOWTIMES, THEATRES, nextDays, type Movie } from '../data'
import PosterImage from './PosterImage'

const ROWS = ['H', 'G', 'F', 'E', 'D', 'C', 'B', 'A'] // back to front
const COLS = 14
const PREMIUM_ROWS = ['A', 'B'] // closest to screen recliners
const BOOKED = new Set(['G5', 'G6', 'F8', 'E3', 'C11', 'C12', 'D7', 'H2'])

function price(row: string) {
  return PREMIUM_ROWS.includes(row) ? 470 : 190
}

export default function SeatSelection({ m, onBack, onConfirm }: {
  m: Movie
  onBack: () => void
  onConfirm: (data: { seats: string[]; total: number; time: string; theatre: string; day: string }) => void
}) {
  const days = useMemo(() => nextDays(7), [])
  const [dayIdx, setDayIdx] = useState(0)
  const [time, setTime] = useState(SHOWTIMES[3])
  const [theatre, setTheatre] = useState(THEATRES[0])
  const [selected, setSelected] = useState<string[]>([])

  const toggle = (id: string) => {
    if (BOOKED.has(id)) return
    setSelected((s) => (s.includes(id) ? s.filter((x) => x !== id) : s.length < 8 ? [...s, id] : s))
  }

  const total = selected.reduce((sum, id) => sum + price(id[0]), 0)

  const legend = [
    { label: 'Available', style: { border: '1px solid var(--hairline)', background: '#ffffff' } },
    { label: 'Selected', style: { background: 'var(--grad)' } },
    { label: 'Premium', style: { border: '1.5px solid var(--red-hover)', background: 'var(--red-tint)' } },
    { label: 'Booked', style: { background: '#9ca3af' } },
  ]

  return (
    <div className="mx-auto grid max-w-[1280px] gap-8 px-4 py-6 sm:px-8 lg:grid-cols-[380px_1fr]">
      {/* Left: movie + selectors */}
      <div className="space-y-6">
        <button onClick={onBack} className="flex items-center gap-1 text-sm" style={{ color: 'var(--muted)' }}><ChevronLeft size={16} /> Back</button>

        <div className="flex gap-4">
          <div className="relative shrink-0">
            <PosterImage src={m.poster} alt={m.title} className="h-40 w-28 rounded-xl" />
            <span className="glass absolute inset-0 m-auto grid h-10 w-10 place-items-center rounded-full text-white"><Play size={16} fill="currentColor" /></span>
          </div>
          <div>
            <h1 className="font-display text-2xl font-extrabold leading-tight">{m.title}</h1>
            <p className="text-sm" style={{ color: 'var(--muted)' }}>{m.cert} · {m.runtime}</p>
            <p className="mt-1 text-xs" style={{ color: 'var(--muted)' }}>{m.genres.join(' · ')}</p>
            <p className="mt-2 text-sm font-semibold grad-text">{m.rating} ★ · {m.year}</p>
          </div>
        </div>

        {/* Theatre */}
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--muted)' }}>Theatre</p>
          <div className="space-y-2">
            {THEATRES.map((t) => (
              <button key={t} onClick={() => setTheatre(t)} className="block w-full rounded-xl border px-3 py-2.5 text-left text-sm transition" style={t === theatre ? { borderColor: 'transparent', background: 'var(--red-tint)', boxShadow: 'inset 0 0 0 1.5px var(--red)' } : { borderColor: 'var(--hairline)' }}>{t}</button>
            ))}
          </div>
        </div>

        {/* Date */}
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--muted)' }}>Date</p>
          <div className="no-scrollbar flex gap-2 overflow-x-auto pb-1">
            {days.map((d, i) => (
              <button key={d.key} onClick={() => setDayIdx(i)} className="flex w-14 shrink-0 flex-col items-center rounded-xl border py-2 text-sm transition" style={i === dayIdx ? { borderColor: 'transparent', background: 'var(--grad)', color: '#fff' } : { borderColor: 'var(--hairline)' }}>
                <span className="text-[11px] opacity-80">{d.day}</span>
                <span className="font-display text-lg font-bold">{d.date}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Time */}
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--muted)' }}>Showtime</p>
          <div className="flex flex-wrap gap-2">
            {SHOWTIMES.map((t) => (
              <button key={t} onClick={() => setTime(t)} className="rounded-full border px-3.5 py-2 text-xs font-semibold transition" style={t === time ? { borderColor: 'transparent', background: 'var(--grad)', color: '#fff' } : { borderColor: 'var(--hairline)', color: 'var(--muted)' }}>{t}</button>
            ))}
          </div>
        </div>
      </div>

      {/* Right: seat map */}
      <div className="rounded-3xl border p-5 sm:p-8" style={{ borderColor: 'var(--hairline)', background: 'var(--surface)' }}>
        {/* Screen */}
        <div className="mx-auto mb-2 max-w-xl">
          <div className="h-2.5 rounded-t-[50%]" style={{ background: 'var(--grad)', filter: 'blur(1px)' }} />
          <p className="mt-1 text-center text-xs font-semibold uppercase tracking-[0.4em]" style={{ color: 'var(--muted)' }}>Screen</p>
        </div>

        {/* Seats */}
        <div className="no-scrollbar overflow-x-auto py-4">
          <div className="mx-auto w-max space-y-1.5">
            {ROWS.map((r) => (
              <div key={r} className="flex items-center gap-1.5">
                <span className="w-4 text-center text-[11px] font-semibold" style={{ color: 'var(--muted)' }}>{r}</span>
                <div className="flex gap-1.5">
                  {Array.from({ length: COLS }, (_, c) => {
                    const id = `${r}${c + 1}`
                    const isBooked = BOOKED.has(id)
                    const isSel = selected.includes(id)
                    const isPrem = PREMIUM_ROWS.includes(r)
                    let style: React.CSSProperties = { border: '1px solid var(--hairline)', background: '#ffffff' }
                    if (isPrem && !isSel && !isBooked) style = { border: '1.5px solid var(--red-hover)', background: 'var(--red-tint)' }
                    if (isSel) style = { background: 'var(--grad)', transform: 'scale(1.12)' }
                    if (isBooked) style = { background: '#9ca3af', cursor: 'not-allowed' }
                    return (
                      <button key={id} onClick={() => toggle(id)} disabled={isBooked} title={id} className={`h-6 w-6 rounded-md text-[9px] font-semibold text-white/70 transition-transform duration-150 hover:scale-110 ${c === COLS / 2 ? 'ml-7' : ''}`} style={style} />
                    )
                  })}
                </div>
                <span className="w-4 text-center text-[11px] font-semibold" style={{ color: 'var(--muted)' }}>{r}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Legend */}
        <div className="mt-4 flex flex-wrap justify-center gap-4">
          {legend.map((l) => (
            <span key={l.label} className="flex items-center gap-1.5 text-xs" style={{ color: 'var(--muted)' }}>
              <span className="h-4 w-4 rounded" style={l.style} /> {l.label}
            </span>
          ))}
        </div>

        {/* Summary — sticky at the bottom on mobile, inline on desktop */}
        <div className="glass sticky bottom-0 z-10 -mx-5 mt-6 border-t px-5 pb-5 pt-4 sm:-mx-8 sm:px-8 lg:static lg:mx-0 lg:bg-transparent lg:px-0 lg:pb-0" style={{ borderColor: 'var(--hairline)' }}>
          {selected.length ? (
            <div className="mb-3 flex flex-wrap gap-2">
              {selected.map((id) => (
                <button key={id} onClick={() => toggle(id)} className="rounded-full px-3 py-1 text-xs font-semibold text-white" style={{ background: 'var(--grad)' }}>{id} ✕</button>
              ))}
            </div>
          ) : (
            <p className="mb-3 text-sm" style={{ color: 'var(--muted)' }}>Select your seats — premium recliners are outlined in red.</p>
          )}
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs" style={{ color: 'var(--muted)' }}>{selected.length} {selected.length === 1 ? 'seat' : 'seats'} · {time}</p>
              <p className="font-display text-3xl font-extrabold">₹{total}</p>
            </div>
            <button
              disabled={!selected.length}
              onClick={() => onConfirm({ seats: selected, total, time, theatre, day: `${days[dayIdx].day} ${days[dayIdx].date}` })}
              className="grad-bg rounded-full px-8 py-3.5 text-sm font-semibold text-white transition disabled:opacity-40"
            >
              Confirm & Pay
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
