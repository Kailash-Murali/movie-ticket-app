import { useMemo } from 'react'
import { QRCodeSVG } from 'qrcode.react'
import { Check, CalendarPlus, Download, MapPin, Clock } from 'lucide-react'
import type { Movie } from '../data'
import PosterImage from './PosterImage'

export type Booking = {
  seats: string[]
  total: number
  time: string
  theatre: string
  day: string
}

export default function Confirmation({ m, booking, onHome }: { m: Movie; booking: Booking; onHome: () => void }) {
  const bookingId = useMemo(() => 'FAB-' + Math.random().toString(36).slice(2, 8).toUpperCase(), [])
  return (
    <div className="mx-auto flex max-w-lg flex-col items-center px-4 py-12">
      <div className="grad-bg pulse-ring relative mb-5 grid h-16 w-16 place-items-center rounded-full text-white">
        <Check size={30} strokeWidth={3} />
      </div>
      <h1 className="font-display text-4xl font-extrabold">Booking Confirmed</h1>
      <p className="mt-1 text-sm" style={{ color: 'var(--muted)' }}>See you at the movies. Your ticket is ready.</p>

      <div className="fade-up mt-8 w-full overflow-hidden rounded-3xl border" style={{ borderColor: 'var(--hairline)', background: 'var(--surface)' }}>
        <div className="flex gap-4 p-5">
          <PosterImage src={m.poster} alt={m.title} className="h-32 w-24 shrink-0 rounded-xl" />
          <div className="min-w-0 flex-1">
            <h2 className="font-display text-2xl font-extrabold leading-tight">{m.title}</h2>
            <p className="text-xs" style={{ color: 'var(--muted)' }}>{m.cert} · {m.languages[0]}</p>
            <p className="mt-2 flex items-center gap-1.5 text-sm"><MapPin size={14} className="grad-text" /> {booking.theatre}</p>
            <p className="mt-1 flex items-center gap-1.5 text-sm"><Clock size={14} className="grad-text" /> {booking.day} · {booking.time}</p>
            <div className="mt-2 flex items-center gap-2">
              <span className="text-xs" style={{ color: 'var(--muted)' }}>Booking ID</span>
              <span className="font-display text-sm font-bold tracking-wide" style={{ color: 'var(--red)' }}>{bookingId}</span>
              <span className="ml-auto flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-semibold" style={{ background: 'var(--surface-2)', color: 'var(--muted)' }}>
                <Check size={11} /> Paid
              </span>
            </div>
          </div>
        </div>

        {/* Torn divider */}
        <div className="relative flex items-center">
          <span className="h-5 w-5 rounded-full" style={{ background: 'var(--bg)' }} />
          <span className="flex-1 border-t border-dashed" style={{ borderColor: 'var(--hairline)' }} />
          <span className="h-5 w-5 rounded-full" style={{ background: 'var(--bg)' }} />
        </div>

        <div className="flex items-center gap-5 p-5">
          <div className="rounded-2xl bg-white p-2.5">
            <QRCodeSVG value={`FABULA|${m.id}|${booking.seats.join(',')}|${booking.time}`} size={92} bgColor="#ffffff" fgColor="#0f0f12" />
          </div>
          <div className="flex-1">
            <p className="text-xs uppercase tracking-wider" style={{ color: 'var(--muted)' }}>Seats</p>
            <p className="font-display text-2xl font-extrabold grad-text">{booking.seats.join(', ')}</p>
            <div className="mt-2 flex items-center justify-between">
              <span className="text-xs uppercase tracking-wider" style={{ color: 'var(--muted)' }}>Total paid</span>
              <span className="font-display text-xl font-bold">₹{booking.total}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-5 grid w-full grid-cols-2 gap-3">
        <button className="grad-bg flex items-center justify-center gap-2 rounded-full py-3 text-sm font-semibold text-white"><CalendarPlus size={16} /> Add to Calendar</button>
        <button className="flex items-center justify-center gap-2 rounded-full border py-3 text-sm font-semibold" style={{ borderColor: 'var(--hairline)' }}><Download size={16} /> Download Ticket</button>
      </div>
      <button onClick={onHome} className="mt-5 text-sm font-medium" style={{ color: 'var(--muted)' }}>Back to home</button>
    </div>
  )
}
