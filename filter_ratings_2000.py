"""
Script tối ưu để lọc ratings.csv - chỉ giữ ratings của phim từ năm 2000 trở đi.

Xử lý file lớn (>20 triệu dòng) bằng cách:
1. Đọc danh sách movieId hợp lệ từ movies.csv (đã được lọc)
2. Xử lý ratings.csv theo chunks để tiết kiệm RAM
3. Chỉ giữ ratings có movieId trong danh sách hợp lệ

Chạy: python filter_ratings_2000.py
"""

import pandas as pd
import os
from datetime import datetime
import sys

# Cấu hình
DATA_DIR = 'data'
CHUNK_SIZE = 500000  # Tăng chunk size để xử lý nhanh hơn (500k rows/chunk)

def load_valid_movie_ids():
    """Đọc danh sách movieId hợp lệ từ movies.csv đã được lọc"""
    movies_path = os.path.join(DATA_DIR, 'movies.csv')
    
    if not os.path.exists(movies_path):
        print(f"❌ Không tìm thấy {movies_path}")
        print("   Vui lòng chạy filter_movies_2000.py trước để lọc movies.csv")
        return None
    
    print(f"📖 Đang đọc {movies_path}...")
    movies_df = pd.read_csv(movies_path)
    valid_movie_ids = set(movies_df['movieId'].values)
    
    print(f"  ✅ Đã load {len(valid_movie_ids):,} movieId hợp lệ (phim từ 2000 trở đi)")
    return valid_movie_ids

def filter_ratings(valid_movie_ids):
    """Lọc ratings.csv theo movieId (xử lý theo chunks)"""
    ratings_path = os.path.join(DATA_DIR, 'ratings.csv')
    
    if not os.path.exists(ratings_path):
        print(f"❌ Không tìm thấy {ratings_path}")
        return False
    
    # Lấy kích thước file
    file_size_mb = os.path.getsize(ratings_path) / (1024 * 1024)
    print(f"\n📊 Đang xử lý {ratings_path} ({file_size_mb:.1f} MB)...")
    print(f"  - Chunk size: {CHUNK_SIZE:,} rows")
    
    # Output path tạm
    output_path = os.path.join(DATA_DIR, 'ratings_filtered_temp.csv')
    
    total_rows = 0
    filtered_rows = 0
    first_chunk = True
    chunk_count = 0
    start_time = datetime.now()
    
    try:
        # Đọc và filter theo chunks
        for chunk in pd.read_csv(ratings_path, chunksize=CHUNK_SIZE):
            chunk_count += 1
            total_rows += len(chunk)
            
            # Filter: chỉ giữ ratings có movieId hợp lệ
            filtered_chunk = chunk[chunk['movieId'].isin(valid_movie_ids)]
            filtered_rows += len(filtered_chunk)
            
            # Ghi vào file output
            if first_chunk:
                filtered_chunk.to_csv(output_path, mode='w', index=False)
                first_chunk = False
            else:
                filtered_chunk.to_csv(output_path, mode='a', index=False, header=False)
            
            # Progress update
            elapsed = (datetime.now() - start_time).total_seconds()
            speed = total_rows / elapsed if elapsed > 0 else 0
            print(f"  - Chunk {chunk_count}: Đã xử lý {total_rows:,} rows | "
                  f"Giữ lại {filtered_rows:,} | "
                  f"Tốc độ {speed:,.0f} rows/s", end='\r')
        
        print()  # Xuống dòng sau progress
        
        # Thống kê
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"\n📈 Kết quả:")
        print(f"  - Tổng số ratings ban đầu: {total_rows:,}")
        print(f"  - Số ratings còn lại: {filtered_rows:,}")
        print(f"  - Số ratings bị loại: {total_rows - filtered_rows:,}")
        print(f"  - Tỷ lệ giữ lại: {filtered_rows/total_rows*100:.1f}%")
        print(f"  - Thời gian xử lý: {elapsed:.1f} giây ({elapsed/60:.1f} phút)")
        
        # Backup file gốc
        backup_path = os.path.join(DATA_DIR, f'ratings_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
        print(f"\n📦 Đang backup file gốc...")
        os.rename(ratings_path, backup_path)
        print(f"  ✅ Backup: {backup_path}")
        
        # Rename file filtered thành ratings.csv
        os.rename(output_path, ratings_path)
        print(f"  ✅ Đã lưu file mới: {ratings_path}")
        
        # Kích thước file mới
        new_file_size_mb = os.path.getsize(ratings_path) / (1024 * 1024)
        print(f"\n💾 Kích thước:")
        print(f"  - File gốc: {file_size_mb:.1f} MB")
        print(f"  - File mới: {new_file_size_mb:.1f} MB")
        print(f"  - Tiết kiệm: {file_size_mb - new_file_size_mb:.1f} MB ({(1 - new_file_size_mb/file_size_mb)*100:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Lỗi khi xử lý: {e}")
        # Xóa file tạm nếu có lỗi
        if os.path.exists(output_path):
            os.remove(output_path)
        return False

def verify_result():
    """Kiểm tra kết quả sau khi filter"""
    print(f"\n🔍 Đang kiểm tra kết quả...")
    
    ratings_path = os.path.join(DATA_DIR, 'ratings.csv')
    movies_path = os.path.join(DATA_DIR, 'movies.csv')
    
    # Sample ratings
    print(f"  - Đọc sample từ {ratings_path}...")
    ratings_sample = pd.read_csv(ratings_path, nrows=10000)
    
    # Load all movieIds
    movies_df = pd.read_csv(movies_path)
    valid_movie_ids = set(movies_df['movieId'].values)
    
    # Kiểm tra có movieId nào không hợp lệ
    invalid_ratings = ratings_sample[~ratings_sample['movieId'].isin(valid_movie_ids)]
    
    if len(invalid_ratings) > 0:
        print(f"  ⚠️ Phát hiện {len(invalid_ratings)} ratings không hợp lệ trong sample!")
        print(f"     (Có thể cần chạy lại script)")
    else:
        print(f"  ✅ Tất cả ratings trong sample đều hợp lệ!")
    
    # Thống kê ratings per user
    print(f"\n📊 Thống kê (sample):")
    print(f"  - Số user: {ratings_sample['userId'].nunique():,}")
    print(f"  - Số movie: {ratings_sample['movieId'].nunique():,}")
    print(f"  - Rating trung bình: {ratings_sample['rating'].mean():.2f}")

def main():
    print("=" * 70)
    print("  FILTER RATINGS.CSV - CHỈ GIỮ RATINGS CỦA PHIM TỪ NĂM 2000")
    print("=" * 70)
    
    # 1. Load danh sách movieId hợp lệ
    valid_movie_ids = load_valid_movie_ids()
    if valid_movie_ids is None:
        return
    
    # 2. Filter ratings
    success = filter_ratings(valid_movie_ids)
    if not success:
        print("\n❌ Filter thất bại!")
        return
    
    # 3. Verify kết quả
    verify_result()
    
    print("\n" + "=" * 70)
    print("  ✅ HOÀN TẤT!")
    print("=" * 70)
    print(f"\n🔄 Bước tiếp theo:")
    print(f"  1. Kiểm tra file: data/ratings.csv")
    print(f"  2. File backup: data/ratings_backup_*.csv (có thể xóa sau khi verify)")
    print(f"  3. Cập nhật models: cd ai-service && python train.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Đã hủy bởi người dùng!")
        sys.exit(1)
