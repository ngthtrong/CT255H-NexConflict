# /implement-task [TASK-ID]

## Mô tả
Agent Developer triển khai tính năng theo TDD Green Phase: làm cho failing tests pass, chạy coverage gate (≥80%), và performance scan (N+1, index, LIMIT).

## Cú pháp
```
/implement-task TASK-00002
```

## Quy trình thực hiện

**Agent thực hiện**: Developer (`agents/developer.md`)

### Bước 1: Branch Guard (BẮT BUỘC)
```bash
BRANCH=$(git branch --show-current)
if [[ "$BRANCH" == "main" || "$BRANCH" == "develop" ]]; then
  echo "❌ KHÔNG ĐƯỢC implement trực tiếp trên $BRANCH!"
  echo "   Lệnh này sẽ tạo feature branch từ develop."
  exit 1
fi
```

### Bước 2: Verify Task trong Git
```bash
git show develop:.github-copilot/workspace/tasks/TASK-{ID}.yaml > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "❌ TASK-{ID}.yaml chưa tồn tại trong develop!"
  exit 1
fi
```

### Bước 3: Tạo Feature Branch
```bash
git checkout develop && git pull origin develop
git checkout -b feature/TASK-{ID}-{feature-slug}
```

### Bước 4: TDD Green Phase
Implement code production chỉ đủ để failing tests pass.
Không thêm functionality chưa có test.

```bash
# Chạy tests sau mỗi lần implement một phần:
{test_command}  # → dần dần xanh hơn
```

### Bước 5: Coverage Gate
```bash
{coverage_command}
# Nếu coverage < 80%:
#   - Thêm test cases cho các branches chưa được cover
#   - Hoặc ghi Tech Debt note với lý do cụ thể
echo "Coverage: {X}%  (Gate: 80%)"
```

### Bước 6: Performance Scan (BẮT BUỘC)
```bash
echo "=== N+1 Query Scan ==="
grep -rn --include="*.{js,ts,go,py}" \
  -A2 "for \|forEach\|\.map\|\.each\|range " src/ | \
  grep -i "find\|query\|select\|fetch\|\.get\b" | head -20

echo "=== Missing Index Scan ==="
grep -rn "\.where\|WHERE\|JOIN ON" \
  migrations/ schema/ db/ 2>/dev/null | head -20

echo "=== Missing LIMIT Scan ==="
grep -rn "findAll\|\.find(\|SELECT \*" src/ | \
  grep -v "LIMIT\|limit\|\.take\|\.first" | head -10
```

**Xử lý kết quả**:
- ≤ 2 files cần sửa → Sửa ngay trong PR này
- > 2 files hoặc cần refactor lớn → Ghi vào `TECH-DEBT.md`:
```markdown
## Tech Debt từ TASK-{ID}
- **Vấn đề**: {mô tả}
- **Files liên quan**: {list}
- **Priority**: {HIGH/MEDIUM/LOW}
- **Ước tính**: {effort}
```

### Bước 7: Commit và Push
```bash
git add .
git commit -m "feat(TASK-{ID}): {mô tả tính năng}

- Implement: {feature name}
- Tests: {X} passing, coverage {Y}%
- N+1 scan: {clean / {N} issues fixed / {N} issues deferred to TASK-DEBT-xxx}
- Index: {ok / added index on {column}}
- Tech debt: {none / xem TECH-DEBT.md}"
git push origin feature/TASK-{ID}-{slug}
```

## Output
```
🟢 TDD Green Phase Complete — TASK-{ID}

Branch: feature/TASK-{ID}-{slug}
Tests: {X} passing
Coverage: {Y}%
Performance scan: {status}

Bước tiếp theo:
  /create-pr TASK-{ID}    → Tạo Pull Request
```

## Agent sử dụng
**Agent Developer**
