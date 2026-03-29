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
Đọc `.claude/workspace/bugs/BUG-{ID}.md` — đặc biệt là "Steps to Reproduce" và "Expected Behavior".

### Bước 2: Chạy lại Steps to Reproduce
Thực hiện chính xác các bước được ghi trong bug report.

### Bước 3: Kiểm tra Expected Behavior
Xác nhận behavior hiện tại có khớp với Expected không.

### Bước 4: Kiểm tra Regression
```bash
# Chạy test suite liên quan đến component bị bug
{test_command} --grep "{component}"
```

### Bước 5: Kết luận và Update

**FIXED**:
```bash
# Cập nhật BUG-{ID}.md:
# - status: FIXED
# - verified-by: Agent Tester
# - verified-date: {date}
git add .claude/workspace/bugs/BUG-{ID}.md
git commit -m "bug(verified): BUG-{ID} FIXED ✅ — verified by Tester"
```

**NOT FIXED**:
```bash
# Thêm note vào bug report về lý do chưa fix
# Assign lại cho Developer
git add .claude/workspace/bugs/BUG-{ID}.md
git commit -m "bug(reopen): BUG-{ID} — vẫn còn lỗi sau fix attempt"
```

### Bước 6: Thông báo
```
{✅ VERIFIED FIXED / ❌ NOT FIXED} — BUG-{ID}

{Nếu FIXED}:
  Bug đã được sửa và verified.
  Cập nhật bug status trong backlog.

{Nếu NOT FIXED}:
  Bug vẫn còn. Cần Developer xem lại.
  Chi tiết: {lý do}
```

## Agent sử dụng
**Agent Tester**
