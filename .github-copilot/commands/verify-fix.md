# /verify-fix [BUG-ID]

## Mô tả
Tester kiểm định xem bug đã được sửa đúng chưa. Chạy lại steps to reproduce, xác nhận fix, và update bug report.

## Cú pháp
```
/verify-fix BUG-00001
```

## Quy trình thực hiện

**Agent thực hiện**: Tester (`agents/tester.md`)

### Bước 1: Đọc Bug Report
```bash
cat .github-copilot/workspace/bugs/BUG-{ID}.md
# Lấy Steps to Reproduce và Expected Behavior
```

### Bước 2: Verify Fix Branch/Commit
```bash
FIX_COMMIT=$(grep "Fix Commit" .github-copilot/workspace/bugs/BUG-{ID}.md | awk '{print $3}')
git log --oneline | grep $FIX_COMMIT
```

### Bước 3: Setup Test Environment
```bash
# Checkout develop (đã có fix merged)
git checkout develop && git pull

# Start environment
{start_command}
```

### Bước 4: Execute Steps to Reproduce
```markdown
## Verification Steps — BUG-{ID}

| Step | Action | Expected | Actual | Result |
|------|--------|----------|--------|--------|
| 1 | {action} | {expected} | {actual} | ✅/❌ |
| 2 | {action} | {expected} | {actual} | ✅/❌ |
| 3 | {action} | {expected} | {actual} | ✅/❌ |
```

### Bước 5: Test Regression
```bash
# Chạy related tests để đảm bảo fix không break gì khác
{test_command}
```

### Bước 6: Update Bug Report

**Nếu FIXED:**
```markdown
## Verification
- **Verified by**: Agent Tester
- **Verified date**: {date}
- **Result**: ✅ FIXED
- **Notes**: {ghi chú nếu có}
```

**Nếu NOT FIXED:**
```markdown
## Verification
- **Verified by**: Agent Tester
- **Verified date**: {date}
- **Result**: ❌ NOT FIXED
- **Notes**: {mô tả vấn đề còn lại}
```

### Bước 7: Update Status
```bash
if [ "$RESULT" = "FIXED" ]; then
  # Update status trong frontmatter
  sed -i 's/status: fixed/status: verified/' .github-copilot/workspace/bugs/BUG-{ID}.md
else
  # Reopen bug
  sed -i 's/status: fixed/status: open/' .github-copilot/workspace/bugs/BUG-{ID}.md
fi
```

### Bước 8: Commit Verification
```bash
git add .github-copilot/workspace/bugs/
git commit -m "verify: BUG-{ID} — {FIXED / NOT FIXED}"
git push origin develop
```

## Output
```
🔍 Verification Complete — BUG-{ID}

Result: {✅ FIXED / ❌ NOT FIXED}

{If FIXED}
✅ Bug đã được xác nhận fix!
Status: verified

{If NOT FIXED}
❌ Bug chưa được fix hoàn toàn!
Remaining issues:
- {issue 1}
- {issue 2}

Bug đã được reopen.
Developer cần review lại fix.
```

## Human Checkpoint
Không bắt buộc — automated verification.

## Agent sử dụng
**Agent Tester**
