import { useState } from 'react'
import { POSTER_PLACEHOLDER } from '../data'

/**
 * PosterImageWithFallback — shows a graceful placeholder instead of a broken
 * image icon when the source is missing or fails to load. Includes a subtle
 * skeleton shimmer until the image settles.
 */
export default function PosterImage({
  src,
  alt,
  className,
  style,
}: {
  src: string
  alt: string
  className?: string
  style?: React.CSSProperties
}) {
  const [loaded, setLoaded] = useState(false)
  const [failed, setFailed] = useState(false)
  const resolved = failed || !src ? POSTER_PLACEHOLDER : src

  return (
    <div className={`relative overflow-hidden ${className ?? ''}`} style={{ background: 'var(--surface-2)', ...style }}>
      {!loaded && <div className="absolute inset-0 animate-pulse" style={{ background: 'var(--surface-2)' }} />}
      <img
        src={resolved}
        alt={alt}
        loading="lazy"
        onLoad={() => setLoaded(true)}
        onError={() => { setFailed(true); setLoaded(true) }}
        className="h-full w-full object-cover transition-opacity duration-500"
        style={{ opacity: loaded ? 1 : 0 }}
      />
    </div>
  )
}
