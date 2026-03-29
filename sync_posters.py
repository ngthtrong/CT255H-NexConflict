#!/usr/bin/env python3
"""
Sync movie posters from TMDB API to PostgreSQL database.
Run this script to update posterUrl for movies with tmdbId but no poster.
"""

import os
import sys
import time
import requests
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_API_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

# Database connection
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'database': os.getenv('POSTGRES_DB', 'nexconflict_db'),
    'user': os.getenv('POSTGRES_USER', 'nexconflict'),
    'password': os.getenv('POSTGRES_PASSWORD', 'nexconflict123')
}

# Rate limiting
REQUESTS_PER_SECOND = 40  # TMDB allows ~40 requests/second
DELAY_BETWEEN_REQUESTS = 1.0 / REQUESTS_PER_SECOND


def get_poster_url(tmdb_id: int) -> str | None:
    """Fetch poster URL from TMDB API."""
    if not TMDB_API_KEY:
        print("Error: TMDB_API_KEY not set in environment")
        return None
    
    try:
        url = f"{TMDB_API_URL}/movie/{tmdb_id}?api_key={TMDB_API_KEY}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            poster_path = data.get('poster_path')
            if poster_path:
                return f"{TMDB_IMAGE_URL}{poster_path}"
        elif response.status_code == 404:
            return None  # Movie not found on TMDB
        else:
            print(f"  TMDB API error for {tmdb_id}: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"  Request failed for {tmdb_id}: {e}")
    
    return None


def sync_posters(batch_size: int = 100, max_movies: int | None = None):
    """Sync missing posters from TMDB to database."""
    
    print(f"\n{'='*60}")
    print("TMDB Poster Sync")
    print(f"{'='*60}")
    
    if not TMDB_API_KEY:
        print("❌ Error: TMDB_API_KEY not configured in .env file")
        return
    
    print(f"✓ TMDB API Key: {TMDB_API_KEY[:8]}...")
    print(f"✓ Database: {DB_CONFIG['database']}@{DB_CONFIG['host']}")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Count movies needing poster sync
        cursor.execute("""
            SELECT COUNT(*) FROM movie 
            WHERE tmdb_id IS NOT NULL AND poster_url IS NULL
        """)
        total_candidates = cursor.fetchone()[0]
        print(f"\n📊 Movies needing poster sync: {total_candidates}")
        
        if total_candidates == 0:
            print("✅ All movies already have posters!")
            return
        
        # Fetch movies in batches
        limit = max_movies if max_movies else total_candidates
        print(f"🎯 Will process up to: {limit} movies")
        print(f"{'='*60}\n")
        
        cursor.execute("""
            SELECT id, tmdb_id, title FROM movie 
            WHERE tmdb_id IS NOT NULL AND poster_url IS NULL
            ORDER BY id
            LIMIT %s
        """, (limit,))
        
        movies = cursor.fetchall()
        
        updated = 0
        failed = 0
        no_poster = 0
        start_time = time.time()
        
        for i, (movie_id, tmdb_id, title) in enumerate(movies, 1):
            # Rate limiting
            time.sleep(DELAY_BETWEEN_REQUESTS)
            
            poster_url = get_poster_url(tmdb_id)
            
            if poster_url:
                cursor.execute("""
                    UPDATE movie SET poster_url = %s WHERE id = %s
                """, (poster_url, movie_id))
                conn.commit()
                updated += 1
                status = "✓"
            else:
                no_poster += 1
                status = "✗"
            
            # Progress
            elapsed = time.time() - start_time
            rate = i / elapsed if elapsed > 0 else 0
            eta = (len(movies) - i) / rate if rate > 0 else 0
            
            print(f"[{i:4d}/{len(movies)}] {status} {title[:40]:<40} (TMDB: {tmdb_id}) | {rate:.1f}/s ETA: {eta:.0f}s")
        
        # Final stats
        elapsed_total = time.time() - start_time
        
        print(f"\n{'='*60}")
        print("📊 Sync Complete!")
        print(f"{'='*60}")
        print(f"  ⏱️  Duration: {elapsed_total:.1f}s")
        print(f"  ✅ Updated: {updated}")
        print(f"  ⚠️  No poster on TMDB: {no_poster}")
        print(f"  ❌ Failed: {failed}")
        
        # Check remaining
        cursor.execute("""
            SELECT COUNT(*) FROM movie 
            WHERE tmdb_id IS NOT NULL AND poster_url IS NULL
        """)
        remaining = cursor.fetchone()[0]
        print(f"  📋 Remaining: {remaining}")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Sync movie posters from TMDB')
    parser.add_argument('--max', type=int, default=None, help='Max movies to sync (default: all)')
    parser.add_argument('--batch', type=int, default=100, help='Batch size (default: 100)')
    
    args = parser.parse_args()
    
    sync_posters(batch_size=args.batch, max_movies=args.max)
