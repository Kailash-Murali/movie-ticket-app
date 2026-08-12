export type Showtime = { time: string; format: string; price: number }

export type Movie = {
  id: string
  tmdbId: number
  title: string
  originalTitle: string
  cert: string // certificate
  genres: string[]
  languages: string[]
  runtime: string
  year: string
  releaseDate: string
  rating: string
  voteCount: number
  poster: string // posterUrl (built by the movies service, never from title)
  backdrop: string // backdropUrl
  synopsis: string // overview
  reason: string
  tags: string[] // for filters: New, IMAX, 3D
  cast: { name: string; role: string; photo: string }[]
  showtimes: Showtime[]
}

const u = (id: string, w = 600, h = 900) =>
  `https://images.unsplash.com/photo-${id}?w=${w}&h=${h}&fit=crop&auto=format`

// A neutral, on-brand SVG poster used when no image is available. Never a broken icon.
export const POSTER_PLACEHOLDER =
  'data:image/svg+xml;utf8,' +
  encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="300" height="450" viewBox="0 0 300 450"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#212129"/><stop offset="1" stop-color="#1a1a1f"/></linearGradient></defs><rect width="300" height="450" fill="url(#g)"/><g fill="none" stroke="#e63946" stroke-width="2" opacity="0.7"><path d="M150 190v70M115 225h70" stroke-linecap="round"/></g><text x="150" y="300" fill="#9a9aa6" font-family="sans-serif" font-size="14" text-anchor="middle">Poster unavailable</text></svg>`,
  )

const defaultShowtimes = (): Showtime[] => [
  { time: '09:45 AM', format: '2D', price: 190 },
  { time: '11:45 AM', format: 'IMAX', price: 470 },
  { time: '1:20 PM', format: '2D', price: 220 },
  { time: '4:45 PM', format: '3D', price: 290 },
  { time: '7:30 PM', format: 'IMAX', price: 470 },
  { time: '10:20 PM', format: '2D', price: 250 },
]

export const MOVIES: Movie[] = [
  {
    id: 'devadas',
    tmdbId: 1041613,
    title: 'Devadas & Chandra',
    originalTitle: 'தேவதாஸ் & சந்திரா',
    cert: 'A',
    genres: ['Crime', 'Romance', 'Drama'],
    languages: ['Tamil', 'Telugu'],
    runtime: '2h 38m',
    year: '2026',
    releaseDate: '2026-08-07',
    rating: '8.4',
    voteCount: 2140,
    poster: u('1557701472-b7ea9af8aa9a'),
    backdrop: u('1557701472-b7ea9af8aa9a', 1600, 900),
    synopsis:
      'In a gritty world of passion and peril, the rugged rebel Devadas teams up with Chandra. In their volatile journey, blood is shed for love, and unwavering loyalty becomes the ultimate price of survival.',
    reason: 'Because you like action thrillers',
    tags: ['New', 'IMAX'],
    cast: [
      { name: 'Arjun Kapadia', role: 'Devadas', photo: u('1637059880830-59a90102de77', 200, 200) },
      { name: 'Meera Rao', role: 'Chandra', photo: u('1628070436462-1fb43bceecf7', 200, 200) },
      { name: 'Ravi Sekhar', role: 'Director', photo: u('1694877286935-0e7decac9bb1', 200, 200) },
      { name: 'Nila Menon', role: 'Aunt Kamala', photo: u('1628070436055-bccbecab1a1f', 200, 200) },
    ],
    showtimes: defaultShowtimes(),
  },
  {
    id: 'oakstreet',
    tmdbId: 872585,
    title: 'The End of Oak Street',
    originalTitle: 'The End of Oak Street',
    cert: 'UA16+',
    genres: ['Adventure', 'Sci-Fi'],
    languages: ['English', 'Tamil'],
    runtime: '2h 11m',
    year: '2026',
    releaseDate: '2026-08-01',
    rating: '7.9',
    voteCount: 1560,
    poster: u('1707181599307-5c7e50368521'),
    backdrop: u('1707181599307-5c7e50368521', 1600, 900),
    synopsis:
      'Two siblings uncover a fracture in time beneath their childhood home, unleashing a prehistoric storm that only their bond can outrun.',
    reason: 'Popular near Chennai this weekend',
    tags: ['New', '3D'],
    cast: [
      { name: 'Dev Anand', role: 'Sam', photo: u('1734656913620-7dc20c2fc2ac', 200, 200) },
      { name: 'Priya Nair', role: 'Ela', photo: u('1773592606902-6e0a0cc9fc47', 200, 200) },
    ],
    showtimes: defaultShowtimes(),
  },
  {
    id: 'magudam',
    tmdbId: 693134,
    title: 'Magudam',
    originalTitle: 'மகுடம்',
    cert: 'UA16+',
    genres: ['Action', 'Thriller'],
    languages: ['Tamil'],
    runtime: '2h 24m',
    year: '2026',
    releaseDate: '2026-07-25',
    rating: '8.1',
    voteCount: 1890,
    poster: u('1678918549313-cbaf32e5a1c5'),
    backdrop: u('1678918549313-cbaf32e5a1c5', 1600, 900),
    synopsis:
      'A retired con artist is pulled back for one last heist across the neon underbelly of the city, where every ally wears two faces.',
    reason: 'Top rated by viewers like you',
    tags: ['IMAX'],
    cast: [
      { name: 'Karthik V', role: 'Guru', photo: u('1678918561191-197742cb9271', 200, 200) },
      { name: 'Anjali Das', role: 'Reva', photo: u('1773592612185-bd985ac2bfe2', 200, 200) },
    ],
    showtimes: defaultShowtimes(),
  },
  {
    id: 'agadha',
    tmdbId: 558449,
    title: 'Agadha',
    originalTitle: 'అగధ',
    cert: 'A',
    genres: ['Horror', 'Mystery'],
    languages: ['Telugu'],
    runtime: '1h 58m',
    year: '2026',
    releaseDate: '2026-08-08',
    rating: '7.6',
    voteCount: 980,
    poster: u('1637059880830-59a90102de77'),
    backdrop: u('1637059880830-59a90102de77', 1600, 900),
    synopsis:
      'A pilgrimage to a forgotten temple awakens something that has waited centuries in the dark. Faith becomes the only exit.',
    reason: 'A good fit for a 2-hour plan',
    tags: ['New'],
    cast: [
      { name: 'Suraj M', role: 'The Pilgrim', photo: u('1734656913620-7dc20c2fc2ac', 200, 200) },
    ],
    showtimes: defaultShowtimes(),
  },
  {
    id: 'odyssey',
    tmdbId: 315011,
    title: 'The Odyssey',
    originalTitle: 'The Odyssey',
    cert: 'A',
    genres: ['Epic', 'Adventure'],
    languages: ['English'],
    runtime: '2h 52m',
    year: '2026',
    releaseDate: '2026-07-17',
    rating: '8.8',
    voteCount: 4210,
    poster: u('1628070437212-2f2073cae44e'),
    backdrop: u('1628070437212-2f2073cae44e', 1600, 900),
    synopsis:
      'A warrior-king battles gods and monsters across an unforgiving sea to return to the throne — and the family — he left behind.',
    reason: 'Because you rated epics highly',
    tags: ['IMAX', '3D'],
    cast: [
      { name: 'Leo Marsh', role: 'Odysseus', photo: u('1694877286935-0e7decac9bb1', 200, 200) },
    ],
    showtimes: defaultShowtimes(),
  },
  {
    id: 'awarapan',
    tmdbId: 447365,
    title: 'Awarapan 2',
    originalTitle: 'आवारापन 2',
    cert: 'UA16+',
    genres: ['Drama', 'Romance'],
    languages: ['Hindi'],
    runtime: '2h 16m',
    year: '2026',
    releaseDate: '2026-08-05',
    rating: '7.4',
    voteCount: 720,
    poster: u('1678918561191-197742cb9271'),
    backdrop: u('1678918561191-197742cb9271', 1600, 900),
    synopsis:
      'A brooding enforcer finds unexpected redemption in a chance encounter, forcing him to choose between the life he owes and the one he wants.',
    reason: 'A slow-burn romance you may love',
    tags: ['New'],
    cast: [
      { name: 'Imran K', role: 'Shivam', photo: u('1637059880830-59a90102de77', 200, 200) },
    ],
    showtimes: defaultShowtimes(),
  },
]

export const CITIES = [
  'Chennai, Tamil Nadu',
  'Bengaluru, Karnataka',
  'Mumbai, Maharashtra',
  'Hyderabad, Telangana',
  'Delhi NCR',
  'Kochi, Kerala',
]

export const SHOWTIMES = ['09:45 AM', '11:45 AM', '1:20 PM', '4:45 PM', '7:30 PM', '10:20 PM']

export const THEATRES = [
  'Fabula Luxe · Phoenix Marketcity',
  'Fabula IMAX · Express Avenue',
  'Fabula RSL · ECR',
]

export function nextDays(n: number) {
  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
  const out: { day: string; date: number; key: string }[] = []
  const base = new Date(2026, 7, 12)
  for (let i = 0; i < n; i++) {
    const d = new Date(base)
    d.setDate(base.getDate() + i)
    out.push({ day: days[d.getDay()], date: d.getDate(), key: d.toISOString().slice(0, 10) })
  }
  return out
}
