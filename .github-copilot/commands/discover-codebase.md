# /discover-codebase

## Mô tả
Chạy phân tích brownfield discovery 10 giai đoạn trên codebase hiện có. Tạo 7 tài liệu phân tích sống và PROJECT-PROFILE.md.

## Khi nào dùng
- Lần đầu làm việc với repo existing
- Sau khi có thay đổi kiến trúc lớn

## Quy trình thực hiện

**Agent thực hiện**: Codebase Analyst (`agents/analyst.md`)

### 10 Giai đoạn Phân tích

#### Giai đoạn 1: Stack Detection
Xác định ngôn ngữ, framework, toolchain → `01-stack.md`

#### Giai đoạn 2: Module Map
Vẽ sơ đồ module và dependencies → `02-module-map.md`

#### Giai đoạn 3: Business Logic Extraction
Tìm và ghi chép business logic bị chôn vùi → `03-business-logic.md`

#### Giai đoạn 4: Fragile Zone Detection
Phát hiện vùng rủi ro cao → `04-fragile-zones.md`

#### Giai đoạn 5: Test Coverage Map
Đo test coverage và gaps → `05-test-coverage.md`

#### Giai đoạn 6: API Surface Documentation
Ghi chép API endpoints → `06-api-surface.md`

#### Giai đoạn 7: Database Schema Analysis
Phân tích schema, indexes, N+1 patterns

#### Giai đoạn 8: External Dependencies Audit
Kiểm tra third-party libs và APIs

#### Giai đoạn 9: Documentation Drift Detection
So sánh docs với code thực tế → `07-drift-report.md`

#### Giai đoạn 10: PROJECT-PROFILE.md Generation
Tổng hợp thành file config cho agents

## Output Files

Tạo 7 files trong `.github-copilot/workspace/analysis/`:
1. `01-stack.md`
2. `02-module-map.md`
3. `03-business-logic.md`
4. `04-fragile-zones.md`
5. `05-test-coverage.md`
6. `06-api-surface.md`
7. `07-drift-report.md`

Plus: `.github-copilot/PROJECT-PROFILE.md`

## Output
```
🔍 Brownfield Discovery Complete

10 giai đoạn hoàn thành ✅

Files tạo:
- 7 tài liệu phân tích trong .github-copilot/workspace/analysis/
- PROJECT-PROFILE.md đã được cập nhật

Fragile Zones phát hiện:
- 🔴 HIGH: {N} zones
- 🟡 MEDIUM: {M} zones  
- 🟢 LOW: {K} zones

Test Coverage: {X}%
Documentation Drift: {Y} issues

Bước tiếp theo:
1. Review PROJECT-PROFILE.md
2. Chạy /update-agents để cập nhật guardrails
```

## Human Checkpoint
**Khuyến nghị**: Review Fragile Zones và plan addressing tech debt.

## Agent sử dụng
**Agent Codebase Analyst**
