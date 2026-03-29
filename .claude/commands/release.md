# /release [version]

## Mô tả
Merge `develop` vào `main`, gắn git tag, và tạo release. Đây là lệnh cuối cùng trong pipeline — có NHIỀU cổng bảo vệ trước khi được phép chạy.

## Cú pháp
```
/release v1.0.0
/release v1.2.3
```

## Điều kiện tiên quyết (TẤT CẢ phải thỏa mãn)
1. Đang ở branch `develop`
2. Smoke test report tồn tại và được PO ký duyệt (APPROVED)
3. Commit hash trong report KHỚP với HEAD hiện tại của develop
4. Không có file untracked quan trọng chưa commit

## Quy trình thực hiện

**Agent thực hiện**: Tech Lead xác nhận cổng, Developer thực hiện merge.

### Bước 1: Branch Guard (BẮT BUỘC — không tự động chuyển)
```bash
BRANCH=$(git branch --show-current)
if [ "$BRANCH" != "develop" ]; then
  echo "❌ /release PHẢI chạy từ branch develop"
  echo "   Current: $BRANCH"
  echo "   Lệnh này sẽ KHÔNG tự động chuyển branch."
  exit 1
fi
```

### Bước 2: Verify Smoke Test Approval
```bash
SMOKE_FILE=$(ls .claude/workspace/smoke-{version}-*.md 2>/dev/null | tail -1)
if [ -z "$SMOKE_FILE" ]; then
  echo "❌ Không tìm thấy smoke test report cho {version}"
  echo "   Chạy /smoke-test {version} trước."
  exit 1
fi

if ! grep -q "APPROVED" "$SMOKE_FILE"; then
  echo "❌ PO chưa ký duyệt smoke test report!"
  echo "   File: $SMOKE_FILE"
  exit 1
fi
```

### Bước 3: Cross-check Commit Hash (BẮT BUỘC)
```bash
CURRENT_HEAD=$(git rev-parse HEAD)
SMOKE_HASH=$(grep "Commit Hash" "$SMOKE_FILE" | awk '{print $NF}' | tr -d '`')

if [ "$CURRENT_HEAD" != "$SMOKE_HASH" ]; then
  echo "❌ CẢNH BÁO: Code đã thay đổi kể từ smoke test!"
  echo "   Smoke tested: $SMOKE_HASH"
  echo "   Current HEAD: $CURRENT_HEAD"
  echo "   Cần chạy lại /smoke-test {version} và PO ký lại."
  exit 1
fi
echo "✅ Commit hash khớp: $CURRENT_HEAD"
```

### Bước 4: Chạy Regression Tests
```bash
echo "Chạy full test suite..."
{test_command}
if [ $? -ne 0 ]; then
  echo "❌ Tests fail! Không thể release."
  exit 1
fi
echo "✅ All tests passing"
```

### Bước 5: Confirmation Gate (BẮT BUỘC — Human Input)
```
🚀 RELEASE CONFIRMATION — {version}

Branch: develop → main
Commit: {hash}
Smoke test: APPROVED by PO ✅
Tests: All passing ✅

⚠️  Hành động này sẽ merge develop vào main và gắn tag {version}.
    KHÔNG THỂ HOÀN TÁC tự động sau khi push.

    Gõ YES để xác nhận, hoặc bất kỳ thứ gì khác để hủy:
```

### Bước 6: Merge vào main (SAU KHI nhận YES)
```bash
git checkout main
git pull origin main
git merge --no-ff develop -m "release: {version}

Smoke test: APPROVED ({date})
Commit hash: {hash}"
git tag -a {version} -m "Release {version} — {date}"
git push origin main
git push origin {version}
git checkout develop
```

### Bước 7: Báo cáo Release
```
🎉 RELEASED — {version}

main ← develop (merged)
Tag: {version}

Changelog highlights:
  {list tasks merged in this release}

Bước tiếp theo:
  /doc-sync    → Đồng bộ tài liệu sau release
```

## Human Checkpoint ⚠️ ⚠️ ⚠️
**Release Confirmation**: Phải gõ `YES` — đây không phải auto-approve.

## Agent sử dụng
**Agent Tech Lead** (verification) + **Agent Developer** (merge)
