# /release [version]

## Mô tả
Merge `develop` vào `main`, gắn git tag, và tạo release. Đây là lệnh cuối cùng trong pipeline — có NHIỀU cổng bảo vệ trước khi được phép chạy.

## Cú pháp
```
/release v1.0.0
```

## Điều kiện tiên quyết (TẤT CẢ bắt buộc)
1. ✅ Smoke test report tồn tại cho version này
2. ✅ PO đã ký duyệt smoke test report
3. ✅ Commit hash trong report = HEAD của develop
4. ✅ Tất cả tests pass trên develop
5. ✅ Không có task BLOCKED

## Quy trình thực hiện

**Agent thực hiện**: PM với confirm từ PO

### Bước 1: Verify Smoke Test Report
```bash
REPORT=".github-copilot/workspace/smoke-v{version}-*.md"
if [ ! -f $REPORT ]; then
  echo "❌ Chưa có smoke test report cho v{version}!"
  echo "   Chạy /smoke-test v{version} trước."
  exit 1
fi

# Kiểm tra PO đã ký duyệt
if ! grep -q "\[x\] APPROVED" $REPORT; then
  echo "❌ PO chưa ký duyệt smoke test report!"
  exit 1
fi
```

### Bước 2: Cross-check Commit Hash
```bash
CURRENT_HEAD=$(git rev-parse HEAD)
SMOKE_HASH=$(grep "Commit Hash" $REPORT | awk '{print $3}')

if [ "$CURRENT_HEAD" != "$SMOKE_HASH" ]; then
  echo "❌ CẢNH BÁO: Code đã thay đổi sau smoke test!"
  echo "   Smoke tested: $SMOKE_HASH"
  echo "   Current HEAD: $CURRENT_HEAD"
  echo ""
  echo "   Cần chạy lại /smoke-test v{version} trước khi release!"
  exit 1
fi
```

### Bước 3: Chạy Regression Tests
```bash
echo "🧪 Chạy regression tests trước release..."
{test_command}
if [ $? -ne 0 ]; then
  echo "❌ Regression tests fail! Không thể release."
  exit 1
fi
echo "✅ Regression tests pass"
```

### Bước 4: Xác nhận Release (Human Checkpoint)
```bash
echo ""
echo "⚠️  RELEASE CONFIRMATION"
echo "========================"
echo "Version: v{version}"
echo "Branch: develop → main"
echo "Commit: $CURRENT_HEAD"
echo ""
echo "Gõ 'YES' để xác nhận release: "
read CONFIRM
if [ "$CONFIRM" != "YES" ]; then
  echo "❌ Release cancelled."
  exit 1
fi
```

### Bước 5: Merge develop → main
```bash
git checkout main
git pull origin main
git merge develop --no-ff -m "release: v{version}

Smoke test: PASSED ✅
PO sign-off: ✅
Regression tests: ✅"
git push origin main
```

### Bước 6: Tag Release
```bash
git tag -a v{version} -m "Release v{version}

Changes:
- {list features from sprint}

Tested: {smoke test date}
Approved by: PO"
git push origin v{version}
```

### Bước 7: Update Develop
```bash
git checkout develop
git merge main --ff-only
git push origin develop
```

## Output
```
🎉 RELEASE COMPLETE — v{version}

Tag: v{version}
Main: {commit_hash}
Time: {datetime}

✅ All gates passed:
  - Smoke test: PASS
  - PO sign-off: ✅
  - Regression: PASS
  - Human confirm: YES

GitHub Release URL: {url nếu dùng gh CLI}

---
🚀 v{version} is now live!
```

## Human Checkpoint
**BẮT BUỘC**: Phải gõ `YES` để xác nhận release.

## Agent sử dụng
**Agent PM** (với orchestration từ tất cả agents để verify gates)
