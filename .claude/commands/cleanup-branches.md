# /cleanup-branches

## Mô tả
Xóa các feature/test/fix branch đã được merge vào develop, giữ git history clean.

## Quy trình thực hiện

**Agent thực hiện**: Developer

### Bước 1: Liệt kê branches đã merged
```bash
git fetch --prune
MERGED_BRANCHES=$(git branch --merged develop | \
  grep -E "feature/|test/|fix/" | \
  grep -v "^\*")

echo "Các branches đã merged vào develop:"
echo "$MERGED_BRANCHES"
```

### Bước 2: Xóa local branches đã merged
```bash
echo "$MERGED_BRANCHES" | xargs git branch -d
```

### Bước 3: Xóa remote tracking branches đã merged
```bash
git branch -r --merged develop | \
  grep -E "origin/(feature|test|fix)/" | \
  sed 's/origin\///' | \
  xargs -I{} git push origin --delete {}
```

### Bước 4: Xóa stale remote tracking refs
```bash
git remote prune origin
```

### Bước 5: Báo cáo
```
🧹 Branch Cleanup Complete

Branches đã xóa local: {N}
Branches đã xóa remote: {N}
Stale refs pruned: {N}

Branches còn lại:
  main, develop, {active feature branches}
```

## Ghi chú
- **KHÔNG** xóa `main` hay `develop`
- **KHÔNG** xóa branch chưa merged
- Chạy lệnh này sau mỗi sprint hoặc sau series của `/merge-pr`

## Agent sử dụng
**Agent Developer**
