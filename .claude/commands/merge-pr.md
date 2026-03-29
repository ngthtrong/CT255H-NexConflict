# /merge-pr [TASK-ID]

## Mô tả
Merge Pull Request đã được Tech Lead approve vào `develop`. Dùng squash merge để giữ lịch sử clean, sau đó tự động chạy Doc Sync.

## Cú pháp
```
/merge-pr TASK-00002
```

## Điều kiện tiên quyết
- PR phải có trạng thái **APPROVED** từ `/techlead-review`
- Tất cả tests phải pass
- Coverage ≥ 80%

## Quy trình thực hiện

**Agent thực hiện**: Tech Lead (`agents/techlead.md`) xác nhận điều kiện, Developer thực hiện merge.

### Bước 1: Verify Approval
```bash
# Kiểm tra review report tồn tại và APPROVED
if ! grep -q "APPROVED" .claude/workspace/reviews/REVIEW-TASK-{ID}.md 2>/dev/null; then
  echo "❌ PR chưa được Tech Lead approve!"
  echo "   Chạy /techlead-review TASK-{ID} trước."
  exit 1
fi
```

### Bước 2: Squash Merge vào develop
```bash
git checkout develop
git pull origin develop
git merge --squash feature/TASK-{ID}-{slug}
git commit -m "feat(TASK-{ID}): {feature name}

{Tóm tắt từ PR description}
Coverage: {X}% | Tests: {N} passing
Reviewed-by: Tech Lead Agent"
git push origin develop
```

### Bước 3: Xóa Feature Branch
```bash
git branch -d feature/TASK-{ID}-{slug}
git push origin --delete feature/TASK-{ID}-{slug}
```

### Bước 4: Cập nhật Task Status
```bash
# Cập nhật TASK-{ID}.yaml: status: merged
sed -i 's/status: in-progress/status: merged/' \
  .claude/workspace/tasks/TASK-{ID}.yaml
git add .claude/workspace/tasks/TASK-{ID}.yaml
git commit -m "chore: TASK-{ID} → merged"
```

### Bước 5: Trigger Doc Sync
Chạy `/doc-sync` tự động sau merge.

### Bước 6: Báo cáo
```
✅ Merged — TASK-{ID}

feature/TASK-{ID}-{slug} → develop (squash merge)
Branch đã xoá: ✅
Doc sync: ✅

Nếu sprint hoàn thành:
  /smoke-test v{version}  → Chuẩn bị release
```

## Agent sử dụng
**Agent Developer** + **Agent Tech Lead** (verification)
