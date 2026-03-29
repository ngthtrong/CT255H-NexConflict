# /merge-pr [TASK-ID]

## Mô tả
Merge Pull Request đã được Tech Lead approve vào `develop`. Dùng squash merge để giữ lịch sử clean, sau đó tự động chạy Doc Sync.

## Cú pháp
```
/merge-pr TASK-00002
```

## Điều kiện tiên quyết
- PR của TASK-{ID} đã được **APPROVED** hoặc **APPROVED WITH CONDITIONS**
- Không có conflict với `develop`

## Quy trình thực hiện

**Agent thực hiện**: PM hoặc Tech Lead

### Bước 1: Verify Review Status
```bash
REVIEW_FILE=".github-copilot/workspace/reviews/REVIEW-TASK-{ID}.md"
if [ ! -f "$REVIEW_FILE" ]; then
  echo "❌ Chưa có review cho TASK-{ID}!"
  echo "   Chạy /techlead-review TASK-{ID} trước."
  exit 1
fi

VERDICT=$(grep "Verdict:" "$REVIEW_FILE" | head -1)
if [[ "$VERDICT" == *"CHANGES REQUESTED"* ]]; then
  echo "❌ Review yêu cầu thay đổi — không thể merge!"
  exit 1
fi
```

### Bước 2: Fetch và Check Conflicts
```bash
git fetch origin
git checkout develop && git pull origin develop

BRANCH=$(git branch -a | grep "feature/TASK-{ID}" | head -1 | xargs)
git merge --no-commit --no-ff origin/$BRANCH
if [ $? -ne 0 ]; then
  echo "⚠️ Có conflict! Cần resolve trước khi merge."
  git merge --abort
  exit 1
fi
git merge --abort
```

### Bước 3: Squash Merge
```bash
git checkout develop
git merge --squash origin/$BRANCH
git commit -m "feat(TASK-{ID}): {feature description}

Squash merge from $BRANCH

- Reviewed by: Tech Lead Agent
- Tests: {X} passing
- Coverage: {Y}%
- Performance scan: {clean/issues noted}

Closes TASK-{ID}"
git push origin develop
```

### Bước 4: Update Task Status
```bash
# Cập nhật TASK-{ID}.yaml
yq -i '.status = "merged"' .github-copilot/workspace/tasks/TASK-{ID}.yaml
yq -i '.review_status = "approved"' .github-copilot/workspace/tasks/TASK-{ID}.yaml
git add .github-copilot/workspace/tasks/
git commit -m "chore: update TASK-{ID} status to merged"
git push origin develop
```

### Bước 5: Cleanup Branch
```bash
git branch -d $BRANCH 2>/dev/null
git push origin --delete $BRANCH 2>/dev/null
```

### Bước 6: Trigger Doc Sync
```bash
echo "🔄 Triggering Doc Sync..."
# Tự động chạy /doc-sync
```

## Output
```
✅ PR Merged — TASK-{ID}

Merged: feature/TASK-{ID}-{slug} → develop
Commit: {hash}
Branch cleaned: ✅

Doc Sync: {running / completed}

Bước tiếp theo:
- Nếu còn task: /implement-task TASK-{next}
- Nếu hết task: /smoke-test v{version}
```

## Human Checkpoint
Không bắt buộc — merge tự động sau approval.

## Agent sử dụng
**Agent PM** hoặc **Agent Tech Lead**
