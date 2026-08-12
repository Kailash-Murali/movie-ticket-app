/**
 * API client for Backend1 (CineMate AI).
 *
 * All calls go through the Vite proxy: /api/* → http://localhost:8000/*
 * Each function maps to a Backend1 endpoint and transforms the response
 * into the shape the frontend components expect.
 */

import { MOVIES, POSTER_PLACEHOLDER, type Movie, type Showtime } from '../data'

const BASE = '/api'

// ─── Low-level fetch helper ───────────────────────────────────────────────

async function fetchApi<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  })
  if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`)
  return res.json()
}

// ─── Backend1 response types ──────────────────────────────────────────────

export type BackendMovie = {
  id: string
  title: string
  genre: string[]
  language: string
  runtime: number
  rating: number
  mood_tags: string[]
  age_rating: string
  description: string
  formats: string[]
}

export type BackendShow = {
  id: string
  movie_id: string
  theater_id: string
  date: string
  time: string
  format: string
  price: number
  movie?: BackendMovie
  theater?: { id: string; name: string; location: string; distance_km: number; formats: string[]; amenities: string[] }
}

export type BackendSeat = {
  id: string
  show_id: string
  row: string
  number: number
  seat_code: string
  type: string
  status: string
  price: number
}

export type BackendBookingResponse = {
  booking_id: string
  status: string
  show_id: string
  movie: string
  theater: string
  show_date: string
  show_time: string
  seats: string[]
  total_price: number
  user_name: string
  created_at: string
  qr_data: string | null
}

export type ChatResponse = {
  session_id: string
  intent: string
  reply: string
  data: Record<string, unknown>
}

export type SeatRecommendation = {
  show_id: string
  recommended_seats: string[]
  recommended_seat_ids: string[]
  score: number
  total_price: number
  reason: string
}

// ─── Adapter: BackendMovie → frontend Movie ──────────────────────────────

const unsplashIds = [
  '1557701472-b7ea9af8aa9a',
  '1707181599307-5c7e50368521',
  '1678918549313-cbaf32e5a1c5',
  '1637059880830-59a90102de77',
  '1628070437212-2f2073cae44e',
  '1678918561191-197742cb9271',
  '1734656913620-7dc20c2fc2ac',
  '1773592606902-6e0a0cc9fc47',
  '1694877286935-0e7decac9bb1',
  '1628070436462-1fb43bceecf7',
]

function stableImageId(id: string): string {
  // Hash the movie ID string to pick a stable unsplash image
  let hash = 0
  for (let i = 0; i < id.length; i++) hash = ((hash << 5) - hash + id.charCodeAt(i)) | 0
  return unsplashIds[Math.abs(hash) % unsplashIds.length]
}

function runtimeToString(mins: number): string {
  const h = Math.floor(mins / 60)
  const m = mins % 60
  return m > 0 ? `${h}h ${m}m` : `${h}h`
}

export function toFrontendMovie(b: BackendMovie): Movie {
  const imgId = stableImageId(b.id)
  const poster = `https://images.unsplash.com/photo-${imgId}?w=600&h=900&fit=crop&auto=format`
  const backdrop = `https://images.unsplash.com/photo-${imgId}?w=1600&h=900&fit=crop&auto=format`

  return {
    id: b.id,
    tmdbId: Math.abs(b.id.split('').reduce((acc, ch) => ((acc << 5) - acc + ch.charCodeAt(0)) | 0, 0)),
    title: b.title,
    originalTitle: b.title,
    cert: b.age_rating || 'UA',
    genres: b.genre,
    languages: [b.language],
    runtime: runtimeToString(b.runtime),
    year: '2026',
    releaseDate: '2026-08-12',
    rating: String(b.rating),
    voteCount: Math.floor(b.rating * 250),
    poster,
    backdrop,
    synopsis: b.description,
    reason: b.mood_tags?.[0] ? `Mood: ${b.mood_tags.join(', ')}` : 'Recommended for you',
    tags: b.formats?.includes('IMAX') ? ['IMAX'] : [],
    cast: [],
    showtimes: [],
  }
}

// ─── API functions ────────────────────────────────────────────────────────

/** Fetch all movies, with optional filters. Falls back to local data. */
export async function apiFetchMovies(filters?: {
  genre?: string; language?: string; max_runtime?: number; min_rating?: number
}): Promise<Movie[]> {
  try {
    const params = new URLSearchParams()
    if (filters?.genre) params.set('genre', filters.genre)
    if (filters?.language) params.set('language', filters.language)
    if (filters?.max_runtime) params.set('max_runtime', String(filters.max_runtime))
    if (filters?.min_rating) params.set('min_rating', String(filters.min_rating))
    const qs = params.toString()
    const data = await fetchApi<BackendMovie[]>(`/movies${qs ? `?${qs}` : ''}`)
    return data.map(toFrontendMovie)
  } catch {
    return MOVIES
  }
}

/** Fetch a single movie by backend ID. */
export async function apiFetchMovie(movieId: string): Promise<Movie | undefined> {
  try {
    const data = await fetchApi<BackendMovie>(`/movies/${movieId}`)
    return toFrontendMovie(data)
  } catch {
    return MOVIES.find((m) => m.id === movieId)
  }
}

/** Fetch shows for a movie. Returns BackendShow[] for SeatSelection to use. */
export async function apiFetchShows(movieId: string, date?: string): Promise<BackendShow[]> {
  try {
    const params = new URLSearchParams()
    if (date) params.set('date', date)
    const qs = params.toString()
    return await fetchApi<BackendShow[]>(`/movies/${movieId}/shows${qs ? `?${qs}` : ''}`)
  } catch {
    return []
  }
}

/** Fetch seat map for a show. */
export async function apiFetchSeats(showId: string): Promise<BackendSeat[]> {
  try {
    return await fetchApi<BackendSeat[]>(`/shows/${showId}/seats`)
  } catch {
    return []
  }
}

/** Create a booking. */
export async function apiCreateBooking(showId: string, seatIds: string[], userName?: string): Promise<BackendBookingResponse> {
  return fetchApi<BackendBookingResponse>('/bookings', {
    method: 'POST',
    body: JSON.stringify({ show_id: showId, seat_ids: seatIds, user_name: userName || 'Guest' }),
  })
}

/** Fetch a booking by ID. */
export async function apiFetchBooking(bookingId: string): Promise<BackendBookingResponse> {
  return fetchApi<BackendBookingResponse>(`/bookings/${bookingId}`)
}

/** Send a chat message. */
export async function apiChat(message: string, sessionId?: string): Promise<ChatResponse> {
  return fetchApi<ChatResponse>('/chat', {
    method: 'POST',
    body: JSON.stringify({ message, session_id: sessionId }),
  })
}

/** Get AI movie recommendation. */
export async function apiRecommend(message: string) {
  return fetchApi<{
    intent: Record<string, unknown>
    recommendations: { movie_id: string; movie: BackendMovie; match_score: number; reasons: string[] }[]
    explanation: string
  }>('/ai/recommend', {
    method: 'POST',
    body: JSON.stringify({ message }),
  })
}

/** Get AI seat recommendation. */
export async function apiSeatRecommend(showId: string, groupSize: number): Promise<SeatRecommendation> {
  return fetchApi<SeatRecommendation>('/ai/seat-recommendation', {
    method: 'POST',
    body: JSON.stringify({ show_id: showId, group_size: groupSize }),
  })
}

/** Mock payment. */
export async function apiMockPayment(bookingId: string) {
  return fetchApi<{ status: string; transaction_id: string; booking_id: string; message: string }>('/payments/mock', {
    method: 'POST',
    body: JSON.stringify({ booking_id: bookingId }),
  })
}

/** Health check — useful to determine if backend is available. */
export async function apiHealthCheck(): Promise<boolean> {
  try {
    await fetchApi<{ status: string }>('/health')
    return true
  } catch {
    return false
  }
}
