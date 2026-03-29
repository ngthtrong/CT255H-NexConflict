# /report-bug [mô tả ngắn]

## Mô tả
Tạo bug report có cấu trúc. Agent Tester ghi chép đầy đủ thông tin tái hiện lỗi, severity, và commit vào develop để tracking.

## Cú pháp
```
/report-bug "Login button không phản hồi trên mobile"
/report-bug "API /users trả về 500 khi email có ký tự đặc biệt"
```

## Quy trình thực hiện

**Agent thực hiện**: Tester (`agents/tester.md`)

### Bước 1: Lấy Bug ID tiếp theo
```bash
LAST_ID=$(ls .claude/workspace/bugs/BUG-*.md 2>/dev/null | \
  sed 's/.*BUG-//' | sed 's/.md//' | sort -n | tail -1)
NEXT_ID=$(printf "%05d" $((${LAST_ID:-0} + 1)))
```

### Bước 2: Thu thập thông tin từ Claude conversation context
- Mô tả hiện tượng
- Steps to reproduce (từ context)
- Expected vs Actual behavior
- Severity assessment

### Bước 3: Tạo Bug Report file

Tạo `.claude/workspace/bugs/BUG-{ID}.md` theo template tại `.claude/templates/BUG-template.md`.

### Bước 4: Commit
```bash
git add .claude/workspace/bugs/BUG-{ID}.md
git commit -m "bug: BUG-{ID} — {mô tả ngắn}"
git push origin develop
```

### Bước 5: Thông báo
```
🐛 Bug Report tạo: BUG-{ID}
Severity: {P1/P2/P3}

{Nếu P1}:
  ⚠️  BUG P1 — Human Decision Required!
  PO phải quyết định:
    A) Hotfix ngay (pause sprint hiện tại)
    B) Đưa vào sprint tiếp theo
  Chạy: /triage-bug BUG-{ID}

{Nếu P2/P3}:
  Bước tiếp theo: /triage-bug BUG-{ID}
```

## Agent sử dụng
**Agent Tester**
