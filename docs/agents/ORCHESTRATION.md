# Agent Orchestration Guide
# Hướng dẫn điều phối các AI Agent

## TỔNG QUAN

Dự án được chia thành **5 agents**, mỗi agent chịu trách nhiệm 1 phần cụ thể.
Mỗi agent nhận 1 file hướng dẫn riêng trong `docs/agents/` để có đủ context hoạt động độc lập.

---

## DANH SÁCH AGENTS

| Agent | File hướng dẫn | Vai trò | Output |
|---|---|---|---|
| **Agent 5A** | AGENT-5-SETUP-INTEGRATION.md (Phase A) | Project Setup: thư mục, requirements, gitignore | Cấu trúc thư mục + config files |
| **Agent 1** | AGENT-1-DATA-PIPELINE.md | Data loading, sampling, preprocessing | `src/data/` (3 files) |
| **Agent 2** | AGENT-2-ML-MODELS.md | KNN, SVD, Hybrid models | `src/models/` (4 files) |
| **Agent 3** | AGENT-3-SERVICES-UI.md | Services + Gradio UI | `src/services/` (4 files) + `src/app.py` |
| **Agent 4** | AGENT-4-EVALUATION.md | Metrics + Evaluation pipeline | `src/evaluation/` (3 files) |
| **Agent 5B** | AGENT-5-SETUP-INTEGRATION.md (Phase B) | Training script + Smoke tests | `src/scripts/` + `tests/` |

---

## DEPENDENCY GRAPH

```
          Agent 5A (Setup)
               │
               ▼
          Agent 1 (Data)
               │
         ┌─────┴─────┐
         ▼            ▼
    Agent 2        (wait)
    (Models)          │
         │            │
    ┌────┴────┐       │
    ▼         ▼       │
 Agent 3   Agent 4    │
 (Services  (Eval)    │
  + UI)       │       │
    │         │       │
    └────┬────┘       │
         ▼            │
     Agent 5B ◄───────┘
   (Integration)
```

### Thứ tự thực hiện chi tiết:

```
ROUND 1: Agent 5A (Setup)
  → Tạo thư mục, requirements.txt, .gitignore, README.md
  → Tiên quyết: không có
  → Output: project skeleton

ROUND 2: Agent 1 (Data Pipeline)
  → Tạo src/data/loader.py, preprocessor.py
  → Tiên quyết: Agent 5A hoàn thành
  → Output: data layer hoàn chỉnh

ROUND 3: Agent 2 (ML Models)
  → Tạo src/models/knn_model.py, svd_model.py, hybrid.py
  → Tiên quyết: Agent 1 hoàn thành (cần biết data interface)
  → Output: model layer hoàn chỉnh

ROUND 4: Agent 3 + Agent 4 (CHẠY SONG SONG)
  → Agent 3: src/services/ + src/app.py
  → Agent 4: src/evaluation/
  → Tiên quyết: Agent 2 hoàn thành
  → Có thể chạy SONG SONG vì không phụ thuộc nhau

ROUND 5: Agent 5B (Integration)
  → Tạo src/scripts/train.py, tests/test_smoke.py
  → Tiên quyết: Tất cả agents khác hoàn thành
  → Output: training script + tests
```

---

## CÁCH SỬ DỤNG

### Cho mỗi agent, cung cấp:
1. File hướng dẫn tương ứng (e.g., `docs/agents/AGENT-1-DATA-PIPELINE.md`)
2. File kiến trúc tổng thể: `docs/ARCHITECTURE.md`
3. Các file docs gốc nếu cần thêm context:
   - `docs/10-algorithm-detail.md` (cho Agent 2, 4)
   - `docs/11-tech-stack.md` (cho Agent 3, 5)

### Prompt mẫu cho mỗi agent:

**Agent 5A:**
```
Đọc file docs/agents/AGENT-5-SETUP-INTEGRATION.md và thực hiện Phase A:
Tạo cấu trúc thư mục, requirements.txt, .gitignore, và cập nhật README.md.
```

**Agent 1:**
```
Đọc file docs/agents/AGENT-1-DATA-PIPELINE.md và docs/ARCHITECTURE.md.
Tạo src/data/__init__.py, src/data/loader.py, src/data/preprocessor.py.
```

**Agent 2:**
```
Đọc file docs/agents/AGENT-2-ML-MODELS.md và docs/10-algorithm-detail.md.
Tạo src/models/__init__.py, knn_model.py, svd_model.py, hybrid.py.
```

**Agent 3:**
```
Đọc file docs/agents/AGENT-3-SERVICES-UI.md và docs/11-tech-stack.md.
Tạo src/services/ (recommender.py, explainer.py, search.py) và src/app.py.
```

**Agent 4:**
```
Đọc file docs/agents/AGENT-4-EVALUATION.md và docs/10-algorithm-detail.md.
Tạo src/evaluation/__init__.py, metrics.py, evaluate.py.
```

**Agent 5B:**
```
Đọc file docs/agents/AGENT-5-SETUP-INTEGRATION.md Phase B.
Tạo src/scripts/train.py và tests/test_smoke.py.
Đảm bảo tất cả imports hoạt động đúng.
```

---

## KIỂM TRA SAU KHI HOÀN THÀNH

### Checklist tổng hợp:
- [ ] `pip install -r requirements.txt` thành công
- [ ] `python -c "from src.data import load_ratings, load_movies"` không lỗi
- [ ] `python -c "from src.models import ItemKNN, SVDModel, HybridRecommender"` không lỗi
- [ ] `python -c "from src.services import RecommenderService"` không lỗi
- [ ] `python -c "from src.evaluation import EvaluationPipeline"` không lỗi
- [ ] Data CSV files có trong `data/` (phải download riêng)
- [ ] `python -m src.scripts.train --n-users 500` chạy thành công
- [ ] `python -m src.app` khởi động Gradio ở localhost:7860
- [ ] `python -m pytest tests/test_smoke.py -v` pass tất cả tests

---

## FILE TREE HOÀN CHỈNH (Sau khi tất cả agents xong)

```
CT255H-NexConflict/
├── .gitignore
├── README.md
├── requirements.txt
├── data/
│   ├── rating.csv              ← Download riêng
│   └── movie.csv               ← Download riêng
├── docs/
│   ├── 09-project-profile.md
│   ├── 10-algorithm-detail.md
│   ├── 11-tech-stack.md
│   ├── 12-implementation-guide.md
│   ├── ARCHITECTURE.md
│   └── agents/
│       ├── AGENT-1-DATA-PIPELINE.md
│       ├── AGENT-2-ML-MODELS.md
│       ├── AGENT-3-SERVICES-UI.md
│       ├── AGENT-4-EVALUATION.md
│       ├── AGENT-5-SETUP-INTEGRATION.md
│       └── ORCHESTRATION.md
├── src/
│   ├── __init__.py
│   ├── app.py                  ← Agent 3
│   ├── data/
│   │   ├── __init__.py         ← Agent 1
│   │   ├── loader.py           ← Agent 1
│   │   └── preprocessor.py     ← Agent 1
│   ├── models/
│   │   ├── __init__.py         ← Agent 2
│   │   ├── knn_model.py        ← Agent 2
│   │   ├── svd_model.py        ← Agent 2
│   │   └── hybrid.py           ← Agent 2
│   ├── services/
│   │   ├── __init__.py         ← Agent 3
│   │   ├── recommender.py      ← Agent 3
│   │   ├── explainer.py        ← Agent 3
│   │   └── search.py           ← Agent 3
│   ├── evaluation/
│   │   ├── __init__.py         ← Agent 4
│   │   ├── metrics.py          ← Agent 4
│   │   └── evaluate.py         ← Agent 4
│   └── scripts/
│       ├── __init__.py         ← Agent 5B
│       └── train.py            ← Agent 5B
├── tests/
│   └── test_smoke.py           ← Agent 5B
├── artifacts/                   ← Generated after training
│   ├── knn_model.pkl
│   ├── svd_model.pkl
│   ├── hybrid_model.pkl
│   ├── movies_info.pkl
│   ├── popular_movies.pkl
│   ├── trainset.pkl
│   ├── testset.pkl
│   ├── evaluation_results.json
│   └── plots/
│       ├── rmse_comparison.png
│       ├── precision_comparison.png
│       ├── ndcg_comparison.png
│       └── overview_comparison.png
└── notebooks/                   ← Optional EDA
```
