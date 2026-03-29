# /triage-bug [BUG-ID]

## Mô tả
PM và Tech Lead cùng đánh giá bug, xác định priority thực sự, và quyết định hướng xử lý — hotfix ngay hay schedule vào sprint tiếp theo.

## Cú pháp
```
/triage-bug BUG-00001
```

## Quy trình thực hiện

**Agent thực hiện**: PM + Tech Lead

### Bước 1: Đọc Bug Report
Đọc `.claude/workspace/bugs/BUG-{ID}.md` để hiểu đầy đủ.

### Bước 2: Phân tích Impact

PM đánh giá:
- User impact (bao nhiêu users bị ảnh hưởng?)
- Business impact (revenue, reputation, SLA?)
- Workaround có không?

Tech Lead đánh giá:
- Root cause (có thể xác định từ bug report không?)
- Fix complexity (đơn giản hay cần refactor lớn?)
- Risk của hotfix (có thể break gì khác không?)

### Bước 3: Kết luận Priority

| Tiêu chí | P1 | P2 | P3 |
|---------|----|----|-----|
| System down / data loss | ✅ | | |
| Core feature broken, no workaround | ✅ | | |
| Core feature broken, has workaround | | ✅ | |
| Minor bug, cosmetic | | | ✅ |

### Bước 4: Quyết định Hành động

**P1 — Hotfix Ngay**:
```
⚠️  BUG P1 — Human Decision Required!
PM khuyến nghị: Hotfix ngay / Pause sprint hiện tại

PO quyết định:
  A) HOTFIX: Developer tạo hotfix branch ngay bây giờ
  B) SCHEDULE: Đưa vào sprint tiếp theo (accept risk)
```

**P2** — Tạo task mới cho sprint tiếp theo

**P3** — Thêm vào backlog

### Bước 5: Cập nhật Bug Report & Commit
```bash
# Update BUG-{ID}.md với priority và decision
git add .claude/workspace/bugs/BUG-{ID}.md
git commit -m "bug(triage): BUG-{ID} → P{X}, {action}"
```

## Human Checkpoint ⚠️
**P1 Bugs**: PO PHẢI quyết định trước khi team làm bất cứ điều gì.

## Agent sử dụng
**Agent PM** + **Agent Tech Lead**
