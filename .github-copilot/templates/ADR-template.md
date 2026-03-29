# ADR-{ID}: {Tên quyết định kiến trúc}

## Metadata
- **Ngày**: {YYYY-MM-DD}
- **Trạng thái**: PROPOSED | ACCEPTED | DEPRECATED | SUPERSEDED
- **Author**: Tech Lead Agent
- **Supersedes**: {ADR-ID cũ nếu có}
- **Liên quan đến**: {TASK-ID hoặc REQ-ID}

## Bối cảnh & Vấn đề

<!-- Mô tả ngữ cảnh và vấn đề dẫn đến quyết định kiến trúc này -->

## Các lựa chọn đã xem xét

### Lựa chọn A: {Tên}
**Mô tả**: {chi tiết}
**Pros**:
- {ưu điểm 1}
- {ưu điểm 2}
**Cons**:
- {nhược điểm 1}
- {nhược điểm 2}

### Lựa chọn B: {Tên}
**Mô tả**: {chi tiết}
**Pros**: ...
**Cons**: ...

### Lựa chọn C: {Tên}
*(nếu có)*

## Quyết định

**→ Chọn Lựa chọn {A/B/C}** vì {lý do chính}.

## Hậu quả (Consequences)

### Hậu quả tích cực
- {benefit 1}
- {benefit 2}

### Hậu quả tiêu cực / Trade-offs
- {trade-off 1}
- {trade-off 2}

## NFR Impact (BẮT BUỘC — không được bỏ)

| Thuộc tính | Ảnh hưởng | Chi tiết |
|-----------|----------|---------|
| **Performance** | Tích cực / Tiêu cực / Neutral | {ví dụ: latency tăng 5ms do encryption} |
| **Scalability** | Tích cực / Tiêu cực / Neutral | {ví dụ: horizontal scaling dễ dàng hơn} |
| **Security** | Tích cực / Tiêu cực / Neutral | {ví dụ: attack surface tăng do thêm endpoint} |
| **Reliability** | Tích cực / Tiêu cực / Neutral | {ví dụ: single point of failure ở message queue} |
| **Observability** | Tích cực / Tiêu cực / Neutral | {ví dụ: cần thêm metrics cho distributed tracing} |

## Implementation Notes
<!-- Hướng dẫn cụ thể cho Developer khi implement theo ADR này -->

---
> **Human Review Required**: Tech Lead đề nghị team đọc và đồng ý với ADR này trước khi code bắt đầu.
