import Link from 'next/link';
import Image from 'next/image';

interface Movie {
  id: number;
  title: string;
  genres: string;
  posterUrl: string | null;
}

export default function MovieCard({ movie }: { movie: Movie }) {
  return (
    <Link href={`/movies/${movie.id}`} className="group block overflow-hidden rounded-lg bg-zinc-900 shadow-md transition-transform hover:scale-105">
      <div className="aspect-[2/3] w-full bg-zinc-800 relative">
        {movie.posterUrl ? (
          <Image src={movie.posterUrl} alt={movie.title} fill className="object-cover" />
        ) : (
          <div className="flex h-full items-center justify-center text-zinc-500">
            No Poster
          </div>
        )}
      </div>
      <div className="p-4">
        <h3 className="truncate font-medium text-white group-hover:text-red-500">{movie.title}</h3>
        <p className="mt-1 text-xs text-zinc-400 truncate">{movie.genres}</p>
      </div>
    </Link>
  );
}
