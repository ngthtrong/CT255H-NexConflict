# /branch-status

## Mô tả
Hiển thị toàn bộ branches, trạng thái của chúng, và task nào đang nằm trên branch nào.

## Quy trình thực hiện

**Agent thực hiện**: PM

```bash
echo "=== BRANCH STATUS — $(date +%Y-%m-%d) ==="

echo "--- Protected Branches ---"
git log main --oneline -1 2>/dev/null && echo "main: $(git log main --format='%h %s' -1)"
git log develop --oneline -1 2>/dev/null && echo "develop: $(git log develop --format='%h %s' -1)"

echo ""
echo "--- Feature Branches ---"
git branch -a | grep "feature/" | while read BRANCH; do
  COMMITS_AHEAD=$(git rev-list develop...$BRANCH --count 2>/dev/null)
  LAST_COMMIT=$(git log $BRANCH --format='%h %s' -1 2>/dev/null)
  echo "$BRANCH (+$COMMITS_AHEAD commits) | $LAST_COMMIT"
done

echo ""
echo "--- Test Branches ---"
git branch -a | grep "test/" | while read BRANCH; do
  echo "$BRANCH | $(git log $BRANCH --format='%h %s' -1 2>/dev/null)"
done

echo ""
echo "--- Fix Branches ---"
git branch -a | grep "fix/" | while read BRANCH; do
  echo "$BRANCH | $(git log $BRANCH --format='%h %s' -1 2>/dev/null)"
done

echo ""
echo "--- Stale Branches (>14 ngày chưa có commit) ---"
git branch | while read BRANCH; do
  LAST_DATE=$(git log -1 --format="%ct" $BRANCH)
  AGE_DAYS=$(( ($(date +%s) - $LAST_DATE) / 86400 ))
  [ $AGE_DAYS -gt 14 ] && echo "$BRANCH — $AGE_DAYS ngày"
done
```

## Agent sử dụng
**Agent PM**
