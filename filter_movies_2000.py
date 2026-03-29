"""
Script lọc MovieLens data - chỉ giữ phim từ năm 2000 đến nay.

Xử lý:
- movie.csv: parse năm từ title (format: "Movie Name (YYYY)")
- link.csv: filter theo movieId
- rating.csv: filter theo movieId (file lớn 690MB, xử lý theo chunks)
- genome-scores.csv: filter theo movieId (file lớn 214MB, xử lý theo chunks)
- tag.csv: filter theo movieId (optional)

Chạy: python filter_movies_2000.py
"""

import pandas as pd
import os
import re
import shutil
from datetime import datetime

# Cấu hình
DATA_DIR = 'data'
BACKUP_DIR = 'data_backup'
MIN_YEAR = 2000
CHUNK_SIZE = 100000  # Số dòng đọc mỗi lần cho file lớn

def backup_data():
    """Backup data files gốc"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{BACKUP_DIR}_{timestamp}"
    
    if not os.path.exists(DATA_DIR):
        print(f"❌ Không tìm thấy thư mục {DATA_DIR}")
        return False
    
    print(f"📦 Đang backup data vào {backup_path}...")
    shutil.copytree(DATA_DIR, backup_path)
    print(f"✅ Backup hoàn tất: {backup_path}")
    return True

def extract_year(title):
    """
    Trích xuất năm từ title.
    Format: "Movie Name (YYYY)" hoặc "Movie Name (YYYY-YYYY)"
    
    Returns: int năm, hoặc None nếu không parse được
    """
    if pd.isna(title):
        return None
    
    # Regex: tìm 4 chữ số trong ngoặc đơn ở cuối title
    match = re.search(r'\((\d{4})\)', str(title))
    if match:
        try:
            year = int(match.group(1))
            # Validate năm hợp lý (1900-2030)
            if 1900 <= year <= 2030:
                return year
        except ValueError:
            pass
    return None

def filter_movies():
    """Lọc movies.csv - chỉ giữ phim >= MIN_YEAR"""
    # Thử cả 2 tên file: movies.csv (gốc) và movie.csv (đã filter)
    movie_path = os.path.join(DATA_DIR, 'movies.csv')
    if not os.path.exists(movie_path):
        movie_path = os.path.join(DATA_DIR, 'movie.csv')
    
    if not os.path.exists(movie_path):
        print(f"❌ Không tìm thấy movies.csv hoặc movie.csv")
        return None
    
    print(f"\n📊 Đang xử lý {os.path.basename(movie_path)}...")
    movies_df = pd.read_csv(movie_path)
    
    print(f"  - Tổng số phim ban đầu: {len(movies_df):,}")
    
    # Parse năm
    movies_df['year'] = movies_df['title'].apply(extract_year)
    
    # Thống kê phim không parse được năm
    no_year = movies_df['year'].isna().sum()
    if no_year > 0:
        print(f"  - ⚠️ {no_year:,} phim không parse được năm (sẽ bị loại bỏ)")
    
    # Filter năm >= MIN_YEAR
    filtered_df = movies_df[movies_df['year'] >= MIN_YEAR].copy()
    
    print(f"  - Số phim từ {MIN_YEAR} trở đi: {len(filtered_df):,}")
    print(f"  - Tỷ lệ giữ lại: {len(filtered_df)/len(movies_df)*100:.1f}%")
    
    # Lưu file mới (không cần cột year)
    filtered_df = filtered_df.drop(columns=['year'])
    output_path = os.path.join(DATA_DIR, 'movies.csv')
    filtered_df.to_csv(output_path, index=False)
    print(f"  ✅ Đã lưu: {output_path}")
    
    # Return set movieIds để filter các file khác
    valid_movie_ids = set(filtered_df['movieId'].values)
    return valid_movie_ids

def filter_links(valid_movie_ids):
    """Lọc links.csv theo movieId"""
    # Thử cả 2 tên file
    link_path = os.path.join(DATA_DIR, 'links.csv')
    if not os.path.exists(link_path):
        link_path = os.path.join(DATA_DIR, 'link.csv')
    
    if not os.path.exists(link_path):
        print(f"❌ Không tìm thấy links.csv hoặc link.csv")
        return
    
    print(f"\n📊 Đang xử lý {os.path.basename(link_path)}...")
    links_df = pd.read_csv(link_path)
    
    print(f"  - Tổng số links ban đầu: {len(links_df):,}")
    
    # Filter
    filtered_df = links_df[links_df['movieId'].isin(valid_movie_ids)]
    
    print(f"  - Số links còn lại: {len(filtered_df):,}")
    print(f"  - Tỷ lệ giữ lại: {len(filtered_df)/len(links_df)*100:.1f}%")
    
    # Lưu
    output_path = os.path.join(DATA_DIR, 'links.csv')
    filtered_df.to_csv(output_path, index=False)
    print(f"  ✅ Đã lưu: {output_path}")

def filter_ratings(valid_movie_ids):
    """Lọc ratings.csv theo movieId (xử lý theo chunks vì file lớn)"""
    # Thử cả 2 tên file
    rating_path = os.path.join(DATA_DIR, 'ratings.csv')
    if not os.path.exists(rating_path):
        rating_path = os.path.join(DATA_DIR, 'rating.csv')
    
    if not os.path.exists(rating_path):
        print(f"❌ Không tìm thấy ratings.csv hoặc rating.csv")
        return
    
    print(f"\n📊 Đang xử lý {os.path.basename(rating_path)} (file lớn, xử lý theo chunks)...")
    
    # Output path tạm
    output_path = os.path.join(DATA_DIR, 'ratings_filtered.csv')
    
    total_rows = 0
    filtered_rows = 0
    first_chunk = True
    
    # Đọc và filter theo chunks
    for chunk in pd.read_csv(rating_path, chunksize=CHUNK_SIZE):
        total_rows += len(chunk)
        
        # Filter
        filtered_chunk = chunk[chunk['movieId'].isin(valid_movie_ids)]
        filtered_rows += len(filtered_chunk)
        
        # Ghi vào file output
        if first_chunk:
            filtered_chunk.to_csv(output_path, mode='w', index=False)
            first_chunk = False
        else:
            filtered_chunk.to_csv(output_path, mode='a', index=False, header=False)
        
        print(f"  - Đã xử lý {total_rows:,} rows...", end='\r')
    
    print(f"\n  - Tổng số ratings ban đầu: {total_rows:,}")
    print(f"  - Số ratings còn lại: {filtered_rows:,}")
    print(f"  - Tỷ lệ giữ lại: {filtered_rows/total_rows*100:.1f}%")
    
    # Replace file gốc - luôn dùng tên ratings.csv
    final_path = os.path.join(DATA_DIR, 'ratings.csv')
    os.replace(output_path, final_path)
    print(f"  ✅ Đã lưu: {final_path}")

def filter_genome_scores(valid_movie_ids):
    """Lọc genome-scores.csv theo movieId (xử lý theo chunks)"""
    genome_path = os.path.join(DATA_DIR, 'genome-scores.csv')
    
    if not os.path.exists(genome_path):
        print(f"⚠️ Không tìm thấy {genome_path} - bỏ qua")
        return
    
    print(f"\n📊 Đang xử lý genome-scores.csv (file lớn, xử lý theo chunks)...")
    
    output_path = os.path.join(DATA_DIR, 'genome-scores_filtered.csv')
    
    total_rows = 0
    filtered_rows = 0
    first_chunk = True
    
    for chunk in pd.read_csv(genome_path, chunksize=CHUNK_SIZE):
        total_rows += len(chunk)
        
        filtered_chunk = chunk[chunk['movieId'].isin(valid_movie_ids)]
        filtered_rows += len(filtered_chunk)
        
        if first_chunk:
            filtered_chunk.to_csv(output_path, mode='w', index=False)
            first_chunk = False
        else:
            filtered_chunk.to_csv(output_path, mode='a', index=False, header=False)
        
        print(f"  - Đã xử lý {total_rows:,} rows...", end='\r')
    
    print(f"\n  - Tổng số genome scores ban đầu: {total_rows:,}")
    print(f"  - Số genome scores còn lại: {filtered_rows:,}")
    print(f"  - Tỷ lệ giữ lại: {filtered_rows/total_rows*100:.1f}%")
    
    os.replace(output_path, genome_path)
    print(f"  ✅ Đã lưu: {genome_path}")

def filter_tags(valid_movie_ids):
    """Lọc tag.csv theo movieId (optional)"""
    tag_path = os.path.join(DATA_DIR, 'tag.csv')
    
    if not os.path.exists(tag_path):
        print(f"⚠️ Không tìm thấy {tag_path} - bỏ qua")
        return
    
    print(f"\n📊 Đang xử lý tag.csv...")
    tags_df = pd.read_csv(tag_path)
    
    print(f"  - Tổng số tags ban đầu: {len(tags_df):,}")
    
    filtered_df = tags_df[tags_df['movieId'].isin(valid_movie_ids)]
    
    print(f"  - Số tags còn lại: {len(filtered_df):,}")
    print(f"  - Tỷ lệ giữ lại: {len(filtered_df)/len(tags_df)*100:.1f}%")
    
    output_path = os.path.join(DATA_DIR, 'tag.csv')
    filtered_df.to_csv(output_path, index=False)
    print(f"  ✅ Đã lưu: {output_path}")

def cleanup_old_models():
    """Xóa pre-trained models để force retrain"""
    model_dir = os.path.join('ai-service', 'models')
    
    if not os.path.exists(model_dir):
        print(f"\n⚠️ Không tìm thấy {model_dir}")
        return
    
    print(f"\n🧹 Đang xóa pre-trained models...")
    
    pkl_files = [f for f in os.listdir(model_dir) if f.endswith('.pkl')]
    
    if not pkl_files:
        print("  - Không có file .pkl nào để xóa")
        return
    
    for pkl_file in pkl_files:
        file_path = os.path.join(model_dir, pkl_file)
        os.remove(file_path)
        print(f"  - Đã xóa: {pkl_file}")
    
    print(f"  ✅ Đã xóa {len(pkl_files)} model files")

def main():
    print("=" * 60)
    print(f"  FILTER MOVIELENS DATA - GIỮ PHIM TỪ NĂM {MIN_YEAR}")
    print("=" * 60)
    
    # 1. Backup
    if not backup_data():
        return
    
    # 2. Filter movies và lấy danh sách movieId hợp lệ
    valid_movie_ids = filter_movies()
    if valid_movie_ids is None:
        print("\n❌ Filter thất bại!")
        return
    
    # 3. Filter các file liên quan
    filter_links(valid_movie_ids)
    filter_ratings(valid_movie_ids)
    filter_genome_scores(valid_movie_ids)
    filter_tags(valid_movie_ids)
    
    # 4. Cleanup models
    cleanup_old_models()
    
    print("\n" + "=" * 60)
    print("  ✅ HOÀN TẤT!")
    print("=" * 60)
    print(f"\n📝 Tóm tắt:")
    print(f"  - Đã giữ lại: {len(valid_movie_ids):,} phim (từ {MIN_YEAR} trở đi)")
    print(f"  - Backup: {[d for d in os.listdir('.') if d.startswith('data_backup_')]}")
    print(f"\n🔄 Bước tiếp theo:")
    print(f"  1. Verify data: python -c \"import pandas as pd; print(pd.read_csv('data/movies.csv').shape)\"")
    print(f"  2. Retrain models: cd ai-service && python train.py")
    print(f"  3. Restart services: docker-compose down && docker-compose up --build")

if __name__ == "__main__":
    main()
