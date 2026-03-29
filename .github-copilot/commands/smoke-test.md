# /smoke-test [version]

## Mô tả
Chạy smoke test trên môi trường live thực tế (không dùng mock). Tạo báo cáo có chữ ký để PO ký duyệt trước khi `/release` được phép chạy.

## Cú pháp
```
/smoke-test v1.0.0
```

## Quy trình thực hiện

**Agent thực hiện**: Tester (`agents/tester.md`)

### Bước 1: Đọc PROJECT-PROFILE.md
```bash
# Lấy thông tin từ PROJECT-PROFILE.md:
# - start command
# - stop command
# - health_check_url
# - smoke test scenarios
```

### Bước 2: Record Commit Hash
```bash
COMMIT_HASH=$(git rev-parse HEAD)
BRANCH=$(git branch --show-current)
echo "📍 Smoke test tại commit: $COMMIT_HASH trên branch: $BRANCH"
```

### Bước 3: Khởi động Môi trường
```bash
# Chạy start command từ PROJECT-PROFILE.md
{start_command}

# Chờ health check
for i in {1..30}; do
  curl -sf {health_check_url} && break
  sleep 2
done
```

### Bước 4: Chạy Smoke Test Scenarios (≤ 10)

Chỉ test critical user flows:
1. Happy path chính
2. Authentication (nếu có)
3. Core data operations
4. Critical error states

**KHÔNG dùng mock** — chạy trên ứng dụng thật!

### Bước 5: Tear Down
```bash
{stop_command}
# Dọn dẹp test data nếu cần
```

### Bước 6: Tạo Smoke Test Report

Tạo `.github-copilot/workspace/smoke-{version}-{date}.md`:

```markdown
# Smoke Test Report — v{version}

**Ngày**: {date}
**Commit Hash**: {hash}
**Branch**: {branch}
**Môi trường**: {docker/local/staging}
**Tester**: Agent Tester

## Kết quả

| # | Kịch bản | Kết quả | Ghi chú |
|---|----------|---------|---------|
| 1 | {scenario} | ✅ PASS / ❌ FAIL | {detail} |
| 2 | {scenario} | ✅ PASS / ❌ FAIL | {detail} |
...

## Tổng kết
- **Tổng**: {N} kịch bản
- **Pass**: {X}
- **Fail**: {Y}
- **Kết luận**: {PASS / FAIL}

---

## Ký duyệt PO

> Tôi xác nhận đã review báo cáo smoke test này.
> Commit hash được test: `{hash}`
>
> [ ] APPROVED — cho phép chạy `/release v{version}`
>
> Chữ ký: _______________________ Ngày: _______
```

### Bước 7: Commit Report
```bash
git add .github-copilot/workspace/smoke-*.md
git commit -m "test: smoke test report v{version}"
git push origin develop
```

## Output
```
🧪 Smoke Test Complete — v{version}

Kết quả: {PASS / FAIL}
- Pass: {X}/{N}
- Fail: {Y}/{N}

Report: .github-copilot/workspace/smoke-{version}-{date}.md

⚠️ YÊU CẦU PO KÝ DUYỆT:
1. Mở file smoke test report
2. Đánh dấu [x] APPROVED
3. Điền chữ ký và ngày
4. Commit thay đổi

Sau khi PO ký duyệt:
  /release v{version}    → Release lên main
```

## Human Checkpoint
**BẮT BUỘC**: PO phải ký duyệt trong báo cáo trước khi `/release` được phép chạy.

## Agent sử dụng
**Agent Tester**
