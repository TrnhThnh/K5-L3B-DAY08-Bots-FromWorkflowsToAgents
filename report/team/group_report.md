# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`):

## 2. Mục tiêu và cách tiếp cận

Nhóm hiểu bài toán thế nào, chia việc ra sao, thứ tự làm bốn shape.

...

## 3. Giải pháp

Mô tả ba shape nhóm viết (workflow, single, orchestrator): mỗi shape đọc gì, quyết định gì, gọi host ra sao. Chỉ rõ ranh giới code / model (tham khảo [docs/architecture.md](../../docs/architecture.md)), cách handoff được sanitize và trace ghi những event nào.

### Shape A — Deterministic Workflow

Shape A sử dụng quy trình Python cố định để xử lý yêu cầu hoàn phí vận chuyển mà không cần gọi LLM. Việc điều hướng được thực hiện bằng các điều kiện trong `run_claim()`.

Quy trình gồm: đọc claim bằng `get_claim_view()`, kiểm tra `order_id`, xác minh quyền truy cập với `lookup_order()`, tính mức hoàn bằng `compute_compensation()` và chuyển yêu cầu hoàn tiền cho `durability.issue_refund()`.

Các quyết định về số tiền, approval và ghi refund được thực hiện bằng code và host, không phụ thuộc nội dung ticket. Workflow sử dụng `finish()` để trả về `RunResult` và ghi trace theo contract.

Đối với khả năng phục hồi, Shape A truyền `crash_at` cho durability layer. Khi chương trình gặp crash, cơ chế idempotency ngăn việc hoàn tiền trùng trong lần chạy lại.

**Kết quả:** Workflow đạt 62/62 public student tests. Trong benchmark nhóm trên 70 trials, Workflow đạt pass rate 100%, pass⁵ 100%, seed variance bằng 0 và cost per success mô phỏng là 27,86 VND.

## 4. Kết quả

Bảng so sánh 4 shape trên bộ public (từ `src/reports/benchmark.json`): pass rate, pass^5, seed min–max, variance, cost/success, mean/p95 steps. Kèm crash safety (`src/reports/crash.json`) và, nếu có, kết quả tự kiểm trên `student_drop/`.

Số liệu lấy từ `src/reports/benchmark.json`: 14 claim public × seed 11, 22, 33, 44, 55, mỗi shape 70 trial, chạy trên commit `166907f`.

| Shape | pass | pass^5 | seed min-max | variance | cost/success (VND) | mean / p95 steps |
| --- | --- | --- | --- | --- | --- | --- |
| workflow | 1.000 | 1.000 | 1.000-1.000 | 0 | 27.86 | 4.43 / 5 |
| single | 1.000 | 1.000 | 1.000-1.000 | 0 | 28.79 | 2.79 / 3 |
| orchestrator | 1.000 | 1.000 | 1.000-1.000 | 0 | 56.20 | 5.36 / 6 |
| swarm | 0.986 | 0.929 | 0.929-1.000 | 0.000816 | 49.57 | 2.80 / 3 |

Crash safety là 20/20 (`src/reports/crash.json`). Ma trận student ra 248 passed, 0 failed (4 shape × 62 test). Cổng host `python -m pytest -q` ra 73 passed.

Ba shape nhóm viết pass hết 70 trial. Swarm sai một trial, `R-swarm-C-002-s55`: ở seed 55 nó lấy số ngày trễ trong ticket (5 ngày) thay cho order row (2 ngày) và trả 20.000 VND thay vì từ chối. Trial này tốn 62.22 VND, cao hơn trial đúng của swarm (khoảng 52.3) vì phải tính lại quote. Phân tích chi tiết ở `report/team/swarm_notes.md`.

Đã tự kiểm `student_drop/` không nhãn: xem `src/reports/hidden_selfcheck.json`; không suy ra pass rate hidden từ kết quả này. Phần mở rộng B3 (verifier cho swarm), benchmark public/đối kháng và tự kiểm student drop của biến thể được trình bày riêng trong [bonus_report.md](bonus_report.md).

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Lỗi gặp phải (kèm lệnh, output hoặc ảnh chụp) và cách nhóm xử lý.

...

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`. Nêu thêm giới hạn của nhóm và điều kiện làm kết luận thay đổi.

...

## 8. Tài liệu tham khảo

...
