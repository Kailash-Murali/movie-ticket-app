import { useEffect, useMemo, useState } from 'react'
import { ChevronLeft, Play, Sparkles } from 'lucide-react'
import { nextDays, type Movie } from '../data'
import { apiFetchShows, apiFetchSeats, apiSeatRecommend, type BackendShow, type BackendSeat } from '../services/api'
import PosterImage from './PosterImage'

const ROWS_ORDER = ['H', 'G', 'F', 'E', 'D', 'C', 'B', 'A'] // back to front
const PREMIUM_ROWS = ['A', 'B']

export default function SeatSelection({ m, onBack, onConfirm }: {
  m: Movie
  onBack: () => void
  onConfirm: (data: { seats: string[]; total: number; time: string; theatre: string; day: string; bookingShowId?: string; seatIds?: string[] }) => void
}) {
  const days = useMemo(() => nextDays(7), [])
  const [dayIdx, setDayIdx] = useState(0)

  // Shows loaded from backend
  const [shows, setShows] = useState<BackendShow[]>([])
  const [selectedShowId, setSelectedShowId] = useState<string | null>(null)
  const [loadingShows, setLoadingShows] = useState(true)

  // Seats loaded from backend
  const [seats, setSeats] = useState<BackendSeat[]>([])
  const [loadingSeats, setLoadingSeats] = useState(false)
  const [selected, setSelected] = useState<string[]>([]) // seat_codes like "D5"
  const [selectedSeatIds, setSelectedSeatIds] = useState<string[]>([]) // backend IDs

  // AI recommended seats
  const [recommended, setRecommended] = useState<Set<string>>(new Set())

  // Load shows for this movie
  useEffect(() => {
    setLoadingShows(true)
    apiFetchShows(m.id, days[dayIdx].key).then((data) => {
      setShows(data)
      if (data.length) setSelectedShowId(data[0].id)
      else setSelectedShowId(null)
      setLoadingShows(false)
    }).catch(() => setLoadingShows(false))
  }, [m.id, dayIdx, days])

  // Load seats when show changes
  useEffect(() => {
    if (!selectedShowId) { setSeats([]); return }
    setLoadingSeats(true)
    setSelected([])
    setSelectedSeatIds([])
    setRecommended(new Set())
    apiFetchSeats(selectedShowId).then((data) => {
      setSeats(data)
      setLoadingSeats(false)
    }).catch(() => setLoadingSeats(false))
  }, [selectedShowId])

  // Get AI seat recommendation
  const getAiRecommendation = () => {
    if (!selectedShowId) return
    apiSeatRecommend(selectedShowId, 2).then((rec) => {
      setRecommended(new Set(rec.recommended_seats))
    }).catch(() => { /* silent fail */ })
  }

  // Derive theatre list and show times from loaded shows
  const theaters = useMemo(() => {
    const map = new Map<string, string>()
    for (const s of shows) {
      const name = s.theater?.name || s.theater_id
      if (!map.has(s.theater_id)) map.set(s.theater_id, name)
    }
    return Array.from(map.entries()) // [id, name][]
  }, [shows])

  const [selectedTheaterId, setSelectedTheaterId] = useState<string | null>(null)
  useEffect(() => {
    if (theaters.length && !selectedTheaterId) setSelectedTheaterId(theaters[0][0])
  }, [theaters, selectedTheaterId])

  const filteredShows = useMemo(() => {
    if (!selectedTheaterId) return shows
    return shows.filter((s) => s.theater_id === selectedTheaterId)
  }, [shows, selectedTheaterId])

  const showtimes = useMemo(() => filteredShows.map((s) => ({ id: s.id, time: s.time, format: s.format, price: s.price })), [filteredShows])

  // Keep selectedShowId in sync
  useEffect(() => {
    if (showtimes.length && !showtimes.find((s) => s.id === selectedShowId)) {
      setSelectedShowId(showtimes[0].id)
    }
  }, [showtimes, selectedShowId])

  // Build seat grid from backend data
  const seatsByRow = useMemo(() => {
    const map = new Map<string, BackendSeat[]>()
    for (const s of seats) {
      if (!map.has(s.row)) map.set(s.row, [])
      map.get(s.row)!.push(s)
    }
    for (const row of map.values()) row.sort((a, b) => a.number - b.number)
    return map
  }, [seats])

  const rowLetters = useMemo(() => {
    const present = new Set(seats.map((s) => s.row))
    // Use standard ordering but only include rows that exist
    const ordered = ROWS_ORDER.filter((r) => present.has(r))
    // Add any extra rows not in ROWS_ORDER
    for (const r of present) {
      if (!ordered.includes(r)) ordered.push(r)
    }
    return ordered
  }, [seats])

  const maxCols = useMemo(() => {
    let max = 0
    for (const row of seatsByRow.values()) {
      const last = row[row.length - 1]?.number ?? 0
      if (last > max) max = last
    }
    return max || 14
  }, [seatsByRow])

  const toggle = (seatCode: string, seatId: string, status: string) => {
    if (status === 'booked') return
    if (selected.includes(seatCode)) {
      setSelected((s) => s.filter((x) => x !== seatCode))
      setSelectedSeatIds((s) => s.filter((x) => x !== seatId))
    } else if (selected.length < 8) {
      setSelected((s) => [...s, seatCode])
      setSelectedSeatIds((s) => [...s, seatId])
    }
  }

  const seatPriceMap = useMemo(() => {
    const map = new Map<string, number>()
    for (const s of seats) map.set(s.seat_code, s.price)
    return map
  }, [seats])

  const total = selected.reduce((sum, code) => sum + (seatPriceMap.get(code) || 190), 0)
  const currentShow = shows.find((s) => s.id === selectedShowId)
  const theaterName = currentShow?.theater?.name || selectedTheaterId || ''

  const legend = [
    { label: 'Available', style: { border: '1px solid var(--hairline)', background: '#ffffff' } },
    { label: 'Selected', style: { background: 'var(--grad)' } },
    { label: 'AI Pick', style: { border: '2px solid #10b981', background: '#d1fae5' } },
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
          {loadingShows ? (
            <p className="text-sm" style={{ color: 'var(--muted)' }}>Loading theatres…</p>
          ) : theaters.length === 0 ? (
            <p className="text-sm" style={{ color: 'var(--muted)' }}>No shows available for this date</p>
          ) : (
            <div className="space-y-2">
              {theaters.map(([id, name]) => (
                <button key={id} onClick={() => setSelectedTheaterId(id)} className="block w-full rounded-xl border px-3 py-2.5 text-left text-sm transition" style={id === selectedTheaterId ? { borderColor: 'transparent', background: 'var(--red-tint)', boxShadow: 'inset 0 0 0 1.5px var(--red)' } : { borderColor: 'var(--hairline)' }}>{name}</button>
              ))}
            </div>
          )}
        </div>

        {/* Date */}
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--muted)' }}>Date</p>
          <div className="no-scrollbar flex gap-2 overflow-x-auto pb-1">
            {days.map((d, i) => (
              <button key={d.key} onClick={() => { setDayIdx(i); setSelectedTheaterId(null) }} className="flex w-14 shrink-0 flex-col items-center rounded-xl border py-2 text-sm transition" style={i === dayIdx ? { borderColor: 'transparent', background: 'var(--grad)', color: '#fff' } : { borderColor: 'var(--hairline)' }}>
                <span className="text-[11px] opacity-80">{d.day}</span>
                <span className="font-display text-lg font-bold">{d.date}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Time */}
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wider" style={{ color: 'var(--muted)' }}>Showtime</p>
          {showtimes.length === 0 ? (
            <p className="text-sm" style={{ color: 'var(--muted)' }}>No showtimes available</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {showtimes.map((t) => (
                <button key={t.id} onClick={() => setSelectedShowId(t.id)} className="rounded-full border px-3.5 py-2 text-xs font-semibold transition" style={t.id === selectedShowId ? { borderColor: 'transparent', background: 'var(--grad)', color: '#fff' } : { borderColor: 'var(--hairline)', color: 'var(--muted)' }}>
                  {t.time} · {t.format} · ₹{t.price}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Right: seat map */}
      <div className="rounded-3xl border p-5 sm:p-8" style={{ borderColor: 'var(--hairline)', background: 'var(--surface)' }}>
        {/* Screen */}
        <div className="mx-auto mb-2 max-w-xl">
          <div className="h-2.5 rounded-t-[50%]" style={{ background: 'var(--grad)', filter: 'blur(1px)' }} />
          <p className="mt-1 text-center text-xs font-semibold uppercase tracking-[0.4em]" style={{ color: 'var(--muted)' }}>Screen</p>
        </div>

        {loadingSeats ? (
          <p className="py-12 text-center text-sm" style={{ color: 'var(--muted)' }}>Loading seats…</p>
        ) : seats.length === 0 ? (
          <p className="py-12 text-center text-sm" style={{ color: 'var(--muted)' }}>Select a showtime to view seats</p>
        ) : (
          <>
            {/* AI recommend button */}
            <div className="mb-3 flex justify-center">
              <button onClick={getAiRecommendation} className="flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition hover:bg-white/5" style={{ borderColor: 'var(--hairline)' }}>
                <Sparkles size={12} /> AI Seat Pick
              </button>
            </div>

            {/* Seats */}
            <div className="no-scrollbar overflow-x-auto py-4">
              <div className="mx-auto w-max space-y-1.5">
                {rowLetters.map((r) => {
                  const rowSeats = seatsByRow.get(r) || []
                  return (
                    <div key={r} className="flex items-center gap-1.5">
                      <span className="w-4 text-center text-[11px] font-semibold" style={{ color: 'var(--muted)' }}>{r}</span>
                      <div className="flex gap-1.5">
                        {Array.from({ length: maxCols }, (_, c) => {
                          const num = c + 1
                          const seat = rowSeats.find((s) => s.number === num)
                          if (!seat) return <span key={num} className="h-6 w-6" /> // empty gap
                          const code = seat.seat_code
                          const isBooked = seat.status === 'booked'
                          const isSel = selected.includes(code)
                          const isPrem = PREMIUM_ROWS.includes(r) || seat.type === 'Recliner' || seat.type === 'Premium'
                          const isRec = recommended.has(code)
                          let style: React.CSSProperties = { border: '1px solid var(--hairline)', background: '#ffffff' }
                          if (isRec && !isSel && !isBooked) style = { border: '2px solid #10b981', background: '#d1fae5' }
                          else if (isPrem && !isSel && !isBooked) style = { border: '1.5px solid var(--red-hover)', background: 'var(--red-tint)' }
                          if (isSel) style = { background: 'var(--grad)', transform: 'scale(1.12)' }
                          if (isBooked) style = { background: '#9ca3af', cursor: 'not-allowed' }
                          const halfCol = Math.ceil(maxCols / 2)
                          return (
                            <button key={code} onClick={() => toggle(code, seat.id, seat.status)} disabled={isBooked} title={`${code} · ₹${seat.price}`} className={`h-6 w-6 rounded-md text-[9px] font-semibold text-white/70 transition-transform duration-150 hover:scale-110 ${num === halfCol + 1 ? 'ml-7' : ''}`} style={style} />
                          )
                        })}
                      </div>
                      <span className="w-4 text-center text-[11px] font-semibold" style={{ color: 'var(--muted)' }}>{r}</span>
                    </div>
                  )
                })}
              </div>
            </div>
          </>
        )}

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
              {selected.map((code) => {
                const seat = seats.find((s) => s.seat_code === code)
                return (
                  <button key={code} onClick={() => seat && toggle(code, seat.id, seat.status)} className="rounded-full px-3 py-1 text-xs font-semibold text-white" style={{ background: 'var(--grad)' }}>{code} ✕</button>
                )
              })}
            </div>
          ) : (
            <p className="mb-3 text-sm" style={{ color: 'var(--muted)' }}>Select your seats — premium recliners are outlined in red.</p>
          )}
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs" style={{ color: 'var(--muted)' }}>{selected.length} {selected.length === 1 ? 'seat' : 'seats'} · {currentShow?.time || ''}</p>
              <p className="font-display text-3xl font-extrabold">₹{total}</p>
            </div>
            <button
              disabled={!selected.length}
              onClick={() => onConfirm({
                seats: selected,
                total,
                time: currentShow?.time || '',
                theatre: theaterName,
                day: `${days[dayIdx].day} ${days[dayIdx].date}`,
                bookingShowId: selectedShowId || undefined,
                seatIds: selectedSeatIds,
              })}
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
