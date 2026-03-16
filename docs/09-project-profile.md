# Project Profile - Movie Recommendation Web App

## Thông tin chung
- **Đề tài**: Xây dựng Web App gợi ý phim sử dụng MovieLens 20M Dataset
- **Môn học**: Ứng dụng và Máy học
- **Nhóm**: 2 sinh viên
- **Thời gian**: 3 tuần
- **Trình độ nhóm**: Khá - Giỏi (quen pandas, scikit-learn, đã làm project web + ML)
- **Hình thức làm việc**: Vibe coding (cả nhóm cùng code), phân chia công việc ở báo cáo

## Quyết định đã chọn

### Thuật toán
| Quyết định | Lựa chọn |
|---|---|
| Hướng tiếp cận chính | Collaborative Filtering |
| KNN | Item-based KNN (cosine similarity) |
| Matrix Factorization | SVD (sử dụng thư viện Surprise) |
| Deep Learning | Không sử dụng (không cần CNN/NCF) |
| Cold-start | Onboarding quiz (chọn genre + đánh giá 5-10 phim) |

### Tech Stack
| Thành phần | Công nghệ |
|---|---|
| Frontend | Gradio (Python-based UI) |
| Backend | FastAPI |
| ML Libraries | Surprise (SVD), scikit-learn (KNN), pandas, numpy |
| Deployment | Local only (localhost) |

### Tính năng
| Tính năng | Có/Không |
|---|---|
| Gợi ý phim (core) | ✅ |
| Onboarding quiz | ✅ |
| Giải thích gợi ý (XAI) | ✅ |
| Search & Filter | ✅ |
| Poster & thông tin phim | ❌ |
| Deploy cloud | ❌ |

### Đánh giá Model
- **Mức độ**: Đầy đủ
- **Metrics**: RMSE, MAE, Precision@K, Recall@K, NDCG@K, Coverage, Diversity
- **So sánh**: Popularity baseline vs Item-KNN vs SVD vs Hybrid
- **Biểu đồ**: So sánh trực quan giữa các model

### Data
- **Quy mô phát triển**: Sample nhỏ (~1M ratings, ~10K movies)
- **Dataset gốc**: MovieLens 20M (6 CSV files)
- **Lý do sample**: Nhanh hơn để phát triển, test, và iterate

## Ưu tiên
- Cân bằng tất cả: Model tốt + UI chấp nhận được + Giải thích cơ bản
- Không over-engineer, tập trung MVP hoàn chỉnh trong 3 tuần

## Thay đổi so với docs ban đầu
1. **Frontend**: React → **Gradio** (đơn giản hơn, tập trung vào ML)
2. **ANN index**: Bỏ Faiss/Annoy (không cần thiết với sample nhỏ, dùng exact KNN)
3. **Deploy**: Chỉ local, không Docker
4. **Phân công**: Không phân chia backend/frontend riêng, cùng vibe coding
