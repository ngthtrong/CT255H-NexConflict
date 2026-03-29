# /doc-sync

## Mô tả
Chạy Doc Sync Agent để phát hiện drift giữa tài liệu và code, cập nhật analysis documents. Nên chạy sau mỗi sprint hoặc sau mỗi PR được merge.

## Khi nào dùng
- Sau `/merge-pr` (tự động được trigger)
- Sau mỗi sprint kết thúc
- Trước khi onboard member mới

## Quy trình thực hiện

**Agent thực hiện**: Doc Sync (`agents/docsync.md`)

Thực hiện đầy đủ theo `agents/docsync.md`:

1. Xác định scope thay đổi từ lần sync trước
2. Kiểm tra API surface drift
3. Kiểm tra module map drift
4. Kiểm tra stack/commands drift
5. Kiểm tra PROJECT-PROFILE.md còn chính xác
6. Tạo Drift Report
7. Cập nhật tài liệu (tự động những gì có thể)
8. Cập nhật `.last-sync-date`
9. Commit tất cả thay đổi

## Output
```
📄 Doc Sync Complete — {date}

Files checked: {N}
Drift HIGH (cần xử lý ngay): {X}
Drift MEDIUM (sprint này): {Y}
Drift LOW (có thể đợi): {Z}

Files cập nhật tự động: {N}
Files cần review thủ công: {M}

Xem chi tiết: .claude/workspace/drift-{date}.md
```

## Agent sử dụng
**Agent Doc Sync**
