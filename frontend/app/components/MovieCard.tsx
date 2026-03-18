import Link from 'next/link';

interface Movie {
  id: number;
  title: string;
  genres: string;
  posterUrl: string | null;
  tmdbId?: number;
}

// Generate a consistent color based on movie id
function getGradientColor(id: number): string {
  const colors = [
    'from-red-900 to-red-700',
    'from-blue-900 to-blue-700',
    'from-green-900 to-green-700',
    'from-purple-900 to-purple-700',
    'from-orange-900 to-orange-700',
    'from-pink-900 to-pink-700',
    'from-teal-900 to-teal-700',
    'from-indigo-900 to-indigo-700',
  ];
  return colors[id % colors.length];
}

// Extract year from title like "Toy Story (1995)"
function extractYear(title: string): string | null {
  const match = title.match(/\((\d{4})\)/);
  return match ? match[1] : null;
}

// Get clean title without year
function getCleanTitle(title: string): string {
  return title.replace(/\s*\(\d{4}\)\s*$/, '').trim();
}

export default function MovieCard({ movie }: { movie: Movie }) {
  const year = extractYear(movie.title);
  const cleanTitle = getCleanTitle(movie.title);
  const gradientClass = getGradientColor(movie.id);
  const firstGenre = movie.genres?.split('|')[0] || '';

  return (
    <Link href={`/movies/${movie.id}`} className="group block overflow-hidden rounded-lg bg-zinc-900 shadow-md transition-transform hover:scale-105 hover:shadow-xl">
      <div className="aspect-[2/3] w-full bg-zinc-800 relative overflow-hidden">
        {movie.posterUrl ? (
          <img
            src={movie.posterUrl}
            alt={movie.title}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        ) : (
          <div className={`flex flex-col h-full items-center justify-center bg-gradient-to-br ${gradientClass} p-4 text-center`}>
            <div className="text-4xl mb-2 opacity-80">🎬</div>
            <div className="text-white font-bold text-sm leading-tight line-clamp-3 mb-2">
              {cleanTitle}
            </div>
            {year && (
              <div className="text-white/60 text-xs">{year}</div>
            )}
            {firstGenre && (
              <div className="mt-2 px-2 py-1 bg-black/30 rounded text-xs text-white/70">
                {firstGenre}
              </div>
            )}
          </div>
        )}
        {/* Hover overlay */}
        <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
          <span className="text-white font-semibold text-sm">View Details</span>
        </div>
      </div>
      <div className="p-3">
        <h3 className="truncate font-medium text-white group-hover:text-red-500 text-sm">{movie.title}</h3>
        <p className="mt-1 text-xs text-zinc-400 truncate">{movie.genres?.replace(/\|/g, ' • ')}</p>
      </div>
    </Link>
  );
}
