/**
 * Movies service — the single integration boundary for movie data.
 *
 * In production this layer would call the TMDB API:
 *   - search:      GET /search/movie?query=...
 *   - details:     GET /movie/{tmdbId}
 *   - poster URLs: `${IMAGE_BASE}/w500${poster_path}` (built from the returned
 *     path, NEVER from the movie title)
 *
 * When no TMDB key is configured (as in this prototype) we fall back to a local
 * dataset that already exposes the same shape, so components never change.
 * Components must import from here, not hardcode poster URLs.
 */
import { MOVIES, POSTER_PLACEHOLDER, type Movie, type Showtime } from '../data'
import { apiFetchMovies, apiFetchMovie, apiFetchShows, toFrontendMovie } from './api'

// Would be: import.meta.env.VITE_TMDB_KEY
const TMDB_KEY: string | undefined = undefined
export const TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p'
export const usingLiveApi = Boolean(TMDB_KEY)

/** Build a TMDB poster URL from a path. Returns the placeholder if absent. */
export function buildPosterUrl(path: string | null | undefined, size = 'w500') {
  if (!path) return POSTER_PLACEHOLDER
  return `${TMDB_IMAGE_BASE}/${size}${path}`
}

export async function searchMovies(query: string): Promise<Movie[]> {
  const q = query.trim().toLowerCase()
  if (!q) return []
  try {
    const all = await apiFetchMovies()
    const hits = all.filter(
      (m) =>
        m.title.toLowerCase().includes(q) ||
        m.genres.some((g) => g.toLowerCase().includes(q)) ||
        m.languages.some((l) => l.toLowerCase().includes(q)),
    )
    return hits.length ? hits : all.slice(0, 3)
  } catch {
    const hits = MOVIES.filter(
      (m) =>
        m.title.toLowerCase().includes(q) ||
        m.genres.some((g) => g.toLowerCase().includes(q)) ||
        m.languages.some((l) => l.toLowerCase().includes(q)),
    )
    return hits.length ? hits : MOVIES.slice(0, 3)
  }
}

export async function getMovieDetails(id: string): Promise<Movie | undefined> {
  return apiFetchMovie(id)
}

export async function getTrendingMovies(): Promise<Movie[]> {
  try {
    const all = await apiFetchMovies()
    return [...all].sort((a, b) => b.voteCount - a.voteCount)
  } catch {
    return [...MOVIES].sort((a, b) => b.voteCount - a.voteCount)
  }
}

export async function getRecommendedMovies(_preferences?: { genres?: string[]; city?: string }): Promise<Movie[]> {
  return apiFetchMovies()
}

export async function getMovieShowtimes(
  movieId: string,
  _date?: string,
  _city?: string,
): Promise<Showtime[]> {
  try {
    const shows = await apiFetchShows(movieId, _date)
    if (shows.length) {
      return shows.map((s) => ({
        time: s.time,
        format: s.format,
        price: s.price,
      }))
    }
  } catch {
    // fall through
  }
  const movie = MOVIES.find((m) => m.id === movieId)
  return movie?.showtimes ?? []
}
