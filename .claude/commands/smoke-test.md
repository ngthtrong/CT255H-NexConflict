# /smoke-test [version]

## Mô tả
Chạy smoke test trên môi trường live thực tế (không dùng mock). Tạo báo cáo có chữ ký để PO ký duyệt trước khi `/release` được phép chạy.

## Cú pháp
```
/smoke-test v1.0.0
/smoke-test v1.2.3
```

## Quy trình thực hiện

**Agent thực hiện**: Tester (`agents/tester.md`)

### Bước 1: Phải đang ở develop
```bash
BRANCH=$(git branch --show-current)
if [ "$BRANCH" != "develop" ]; then
  echo "❌ /smoke-test phải chạy từ branch develop"
  exit 1
fi
```

### Bước 2: Record Commit Hash (BẮT BUỘC)
```bash
COMMIT_HASH=$(git rev-parse HEAD)
echo "🔒 Smoke test hash: $COMMIT_HASH"
# Hash này sẽ được cross-check khi /release chạy
```

### Bước 3: Khởi động Môi trường Live
```bash
# Theo PROJECT-PROFILE.md "Start" command
{start_command}  # ví dụ: docker-compose up -d

# Chờ health check
RETRIES=10
while [ $RETRIES -gt 0 ]; do
  curl -sf {health_check_url} && break
  echo "Chờ service khởi động... ($RETRIES lần còn lại)"
  sleep 3
  RETRIES=$((RETRIES-1))
done
[ $RETRIES -eq 0 ] && echo "❌ Service không khởi động được" && exit 1
```

### Bước 4: Chạy Smoke Test Scenarios (≤ 10)
Dùng scenarios từ `PROJECT-PROFILE.md`. **KHÔNG DÙNG MOCK** — test trực tiếp trên service đang chạy.

```bash
# Ví dụ scenarios (tùy theo project):
# 1. Health check
curl -sf {url}/health

# 2. Authentication flow
curl -sf -X POST {url}/auth/login -d '{...}'

# 3. Critical read operation
curl -sf -H "Authorization: Bearer $TOKEN" {url}/api/resource

# ... tối đa 10 scenarios
```

### Bước 5: Tear Down Môi trường
```bash
{stop_command}  # ví dụ: docker-compose down
# Dọn dẹp test data nếu cần
```

### Bước 6: Tạo Smoke Test Report

Tạo `.claude/workspace/smoke-{version}-{date}.md`:

```markdown
# Smoke Test Report — {version}

**Ngày/giờ**: {datetime}
**Commit Hash**: {hash}
**Branch**: develop
**Môi trường**: {local docker / staging / ...}
**Tester**: Agent Tester

## Kết quả

| # | Kịch bản | Kết quả | Thời gian | Ghi chú |
|---|----------|---------|-----------|---------|
| 1 | Health check | ✅ PASS | 45ms | |
| 2 | Login flow | ✅ PASS | 120ms | |
| 3 | {scenario} | ❌ FAIL | — | {error detail} |

## Tổng kết
- **Tổng scenarios**: {N}
- **Pass**: {X}
- **Fail**: {Y}
- **Kết luận**: {✅ PASS / ❌ FAIL}

{Nếu FAIL}: Chi tiết lỗi:
{error logs}

---
## Ký duyệt PO

> Commit hash được test: `{hash}`
> Tôi xác nhận đã review báo cáo smoke test tại version {version}.
>
> ☐ **APPROVED** — Cho phép chạy `/release {version}`
>
> Chữ ký PO: _________________________ Ngày: __________

> ⚠️ LƯU Ý: Nếu có bất kỳ commit nào được push lên develop SAU khi báo cáo này được ký,
> chữ ký ký sẽ bị vô hiệu và cần chạy lại /smoke-test.
```

### Bước 7: Commit Report
```bash
git add .claude/workspace/smoke-{version}-{date}.md
git commit -m "test: smoke test report v{version} — {PASS/FAIL}"
git push origin develop
```

### Bước 8: Chờ PO Ký Duyệt
```
📋 Smoke Test Report đã tạo!

File: .claude/workspace/smoke-{version}-{date}.md
Kết quả: {X}/{N} PASS

⚠️  CHỜ PO KÝ DUYỆT trước khi chạy /release
    PO mở file report và đánh dấu APPROVED rồi save.
    Sau đó commit và chạy: /release {version}
```

## Human Checkpoint ⚠️ ⚠️
**Smoke Test Sign-off**: PO PHẢI ký vào báo cáo. `/release` sẽ từ chối chạy nếu chưa có approval.

## Agent sử dụng
**Agent Tester**
