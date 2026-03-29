# /cleanup-branches

## Mô tả
Xóa các feature/test/fix branch đã được merge vào develop, giữ git history clean.

## Cú pháp
```
/cleanup-branches
```

## Quy trình thực hiện

**Agent thực hiện**: Developer (`agents/developer.md`)

### Bước 1: Fetch Latest
```bash
git fetch --all --prune
git checkout develop
git pull origin develop
```

### Bước 2: Find Merged Branches
```bash
# Branches đã merge vào develop
MERGED_LOCAL=$(git branch --merged develop | grep -v "main\|develop" | grep -E "feature/|test/|fix/")
MERGED_REMOTE=$(git branch -r --merged develop | grep -v "main\|develop" | grep -E "feature/|test/|fix/")
```

### Bước 3: Confirm Before Delete
```markdown
## Branches to be deleted

### Local branches (merged into develop)
{list}

### Remote branches (merged into develop)
{list}

⚠️ These branches will be PERMANENTLY DELETED.
```

### Bước 4: Delete Merged Branches
```bash
# Local
for branch in $MERGED_LOCAL; do
  git branch -d $branch
done

# Remote
for branch in $MERGED_REMOTE; do
  git push origin --delete ${branch#origin/}
done
```

### Bước 5: Prune Remote References
```bash
git remote prune origin
```

## Output
```
🧹 Branch Cleanup Complete

Deleted:
- Local: {N} branches
- Remote: {M} branches

Kept:
- main
- develop
- {active branches}

Git history is now clean! ✨
```

## Human Checkpoint
Không bắt buộc — chỉ xóa branches đã merge.

## Agent sử dụng
**Agent Developer**
