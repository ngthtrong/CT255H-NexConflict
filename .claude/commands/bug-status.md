# /bug-status

## Mô tả
Hiển thị tổng quan trạng thái tất cả bugs đang được track — open, in-progress, fixed, verified.

## Cú pháp
```
/bug-status
/bug-status P1      ← Chỉ hiện P1 bugs
```

## Quy trình thực hiện

**Agent thực hiện**: PM

```bash
echo "=== BUG STATUS REPORT — $(date +%Y-%m-%d) ==="

for BUG_FILE in .claude/workspace/bugs/BUG-*.md; do
  BUG_ID=$(basename $BUG_FILE .md)
  STATUS=$(grep "^status:" $BUG_FILE | awk '{print $2}')
  PRIORITY=$(grep "^priority:" $BUG_FILE | awk '{print $2}')
  TITLE=$(grep "^title:" $BUG_FILE | cut -d: -f2-)
  ASSIGNEE=$(grep "^assignee:" $BUG_FILE | awk '{print $2}')
  echo "$BUG_ID | $PRIORITY | $STATUS | $ASSIGNEE | $TITLE"
done | sort -k2,2

echo ""
echo "=== Tóm tắt ==="
echo "P1 Open: $(grep -l "priority: P1" .claude/workspace/bugs/*.md 2>/dev/null | xargs grep -l "status: open" 2>/dev/null | wc -l)"
echo "P2 Open: $(grep -l "priority: P2" .claude/workspace/bugs/*.md 2>/dev/null | xargs grep -l "status: open" 2>/dev/null | wc -l)"
echo "P3 Open: $(grep -l "priority: P3" .claude/workspace/bugs/*.md 2>/dev/null | xargs grep -l "status: open" 2>/dev/null | wc -l)"
echo "Fixed (chờ verify): $(grep -rl "status: fixed" .claude/workspace/bugs/ 2>/dev/null | wc -l)"
echo "Verified: $(grep -rl "status: verified" .claude/workspace/bugs/ 2>/dev/null | wc -l)"
```

## Output mẫu
```
=== BUG STATUS REPORT — 2025-03-26 ===
BUG-00001 | P1 | open       | Developer | Login button không phản hồi
BUG-00002 | P2 | in-progress| Developer | Email validation warning
BUG-00003 | P3 | verified   | —         | Typo trong success message

=== Tóm tắt ===
P1 Open: 1
P2 Open: 0  
P3 Open: 0
Fixed (chờ verify): 0
Verified: 1
```

## Agent sử dụng
**Agent PM**
