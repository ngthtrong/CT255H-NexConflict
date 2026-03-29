---
name: agentic-brownfield
description: 'Discover and document existing systems with 10-phase brownfield analysis and drift detection workflows.'
argument-hint: 'analysis scope (full/module/api/database)'
user-invocable: true
---
# Agentic Brownfield Skill

## When to Use
- Mới tiếp quản một codebase có sẵn.
- Cần cập nhật phân tích và drift report sau nhiều thay đổi.
- Muốn hiểu rõ kiến trúc và các vùng rủi ro của hệ thống.

## Procedure
1. **Detect Stack** — Chạy `/detect-stack` để xác định công nghệ sử dụng.
2. **10-Phase Discovery** — Chạy `/discover-codebase` theo thứ tự:
   - Phase 1: Module Mapping
   - Phase 2: Dependency Graph
   - Phase 3: Entry Points Analysis
   - Phase 4: Business Logic Extraction
   - Phase 5: Data Model Documentation
   - Phase 6: API Surface Mapping
   - Phase 7: Test Coverage Assessment
   - Phase 8: Fragile Zones Detection
   - Phase 9: Technical Debt Inventory
   - Phase 10: Security Hotspots
3. **Generate Analysis Documents** — Tạo/cập nhật 7 tài liệu phân tích.
4. **Drift Detection** — Đối chiếu tài liệu hiện tại và code để phát hiện drift.
5. **Risk Prioritization** — Đề xuất ưu tiên khắc phục theo risk level.
6. **Update PROJECT-PROFILE.md** — Cập nhật profile với thông tin mới.

## Human Checkpoints
- ✅ **Stack Review** — Xác minh cấu hình công nghệ phát hiện được là chính xác
- ✅ **Drift Report Review** — Review các điểm drift được phát hiện

## Required References
- `.claude/commands/detect-stack.md`
- `.claude/commands/discover-codebase.md`
- `.claude/commands/doc-sync.md`
- `.claude/agents/analyst.md`
- `.claude/agents/docsync.md`

## Output Artifacts
- `STACK.md` trong `.claude/`
- `PROJECT-PROFILE.md` trong `.claude/`
- Các tài liệu phân tích trong `workspace/analysis/`:
  - `MODULE-MAP.md`
  - `DEPENDENCY-GRAPH.md`
  - `API-SURFACE.md`
  - `DATA-MODEL.md`
  - `FRAGILE-ZONES.md`
  - `TECH-DEBT.md`
  - `SECURITY-HOTSPOTS.md`
- `DRIFT-REPORT.md` trong `workspace/analysis/`
