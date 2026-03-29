# /discover-codebase

## Mô tả
Chạy phân tích brownfield discovery 10 giai đoạn trên codebase hiện có. Tạo 7 tài liệu phân tích sống và PROJECT-PROFILE.md.

## Khi nào dùng
- Lần đầu làm việc với repo existing
- Sau khi có thay đổi kiến trúc lớn
- Khi onboard developer mới vào team

## Quy trình thực hiện

**Agent thực hiện**: Codebase Analyst (`agents/analyst.md`)

Đọc và thực hiện đầy đủ 10 giai đoạn theo định nghĩa trong `agents/analyst.md`:

1. **Stack Detection** → `analysis/01-stack.md`
2. **Module Map** → `analysis/02-module-map.md`
3. **Business Logic Extraction** → `analysis/03-business-logic.md`
4. **Fragile Zone Detection** → `analysis/04-fragile-zones.md`
5. **Test Coverage Map** → `analysis/05-test-coverage.md`
6. **API Surface Documentation** → `analysis/06-api-surface.md`
7. **Database Schema Analysis** → (trong `06-api-surface.md`)
8. **External Dependencies Audit** → (trong `01-stack.md`)
9. **Documentation Drift Detection** → `analysis/07-drift-report.md`
10. **PROJECT-PROFILE.md** → `.claude/PROJECT-PROFILE.md`

### Sau khi hoàn thành:
```bash
git add .claude/workspace/analysis/ .claude/PROJECT-PROFILE.md
git commit -m "docs: brownfield discovery — {project} codebase analysis"
git push origin develop
```

## Output
```
📊 Codebase Analysis Complete!

Files tạo ra:
  .claude/workspace/analysis/01-stack.md
  .claude/workspace/analysis/02-module-map.md
  .claude/workspace/analysis/03-business-logic.md
  .claude/workspace/analysis/04-fragile-zones.md
  .claude/workspace/analysis/05-test-coverage.md
  .claude/workspace/analysis/06-api-surface.md
  .claude/workspace/analysis/07-drift-report.md
  .claude/PROJECT-PROFILE.md

⚠️ Các Fragile Zones cần chú ý:
  {list HIGH RISK zones}

Bước tiếp theo:
  /update-agents    → Cập nhật guardrails với commands thực tế
  /analyze-requirements BRIEF-xxxxx → Bắt đầu sprint mới
```

## Human Checkpoint
Không bắt buộc, nhưng nên review `04-fragile-zones.md` để nắm rủi ro.

## Agent sử dụng
**Agent Analyst** (Codebase Analyst)
