# Báo cáo cá nhân — 2A202603938_TranDucTrung

## 1. Thông tin thành viên

- Họ tên: Trần Đức Trung
- MSSV: 2A202603938
- Email: kientrungtd135@gmail.com
- GitHub: [kientrungtd135](https://github.com/kientrungtd135)

## 2. Phần việc phụ trách

Phụ trách **Shape A — Deterministic Workflow** trong Lab 8 LogiX-VN.

- Xây dựng luồng xử lý yêu cầu hoàn phí vận chuyển.
- Hoàn thiện các checkpoint CP2, CP3 và CP4.
- Kiểm thử chức năng, approval safety, idempotency và crash recovery.
- Bổ sung 10 test cho Shape A.

## 3. Đóng góp cụ thể

### Triển khai Workflow

Hoàn thiện `src/lab8/shapes/workflow.py` với quy trình:

1. Đọc thông tin claim qua `get_claim_view()`.
2. Kiểm tra `order_id` và tra cứu đơn hàng qua `lookup_order()`.
3. Tính khoản hoàn phí bằng `compute_compensation()`.
4. Gọi `issue_refund()` để host xử lý approval, idempotency và ghi nhận refund.
5. Trả kết quả và ghi trace bằng `finish()`.

Workflow sử dụng logic Python cố định, không gọi LLM. Các quyết định liên quan đến số tiền hoàn phí dựa trên dữ liệu và chính sách đáng tin cậy, không dựa vào nội dung ticket.

### Crash recovery

Bổ sung truyền tham số `crash_at` tới durability layer, giữ nguyên cơ chế xử lý `InjectedCrash` để kiểm tra khả năng phục hồi sau lỗi.

### Kiểm thử

Tạo file `src/tests/test_workflow_approval_guard.py` gồm 10 test, kiểm tra:

- Approval hết hạn và ticket giả mạo.
- Refund hợp lệ.
- Thiếu thông tin đơn hàng.
- Truy cập đơn hàng không hợp lệ.
- Dữ liệu giao trễ giả trong ticket.
- Chính sách không còn hiệu lực.
- Giới hạn approval.
- Khoản refund đã chi trả trước đó.
- Idempotency khi retry.
- Crash recovery không tạo refund trùng.

### Commit chính

- `b885626`: Triển khai Deterministic Workflow.
- `15b8dd8`: Hoàn thiện crash recovery.
- `838ece2`: Bổ sung kết quả kiểm thử crash safety.
- `c5e3942`: Thêm 10 Workflow tests.

## 4. Bằng chứng

### Mã nguồn và kiểm thử

- Workflow: `src/lab8/shapes/workflow.py`
- Test cá nhân: `src/tests/test_workflow_approval_guard.py`
- Crash report: `src/reports/crash.json`

### Kết quả kiểm thử

- Workflow public student tests tại CP4: **62/62 passed**.
- Crash safety suite: **20/20 passed**.
- Bộ 10 test cá nhân: **10/10 passed (0.64s)**.

Lệnh chạy bộ test cá nhân:

`python -m pytest -q -o addopts= tests/test_workflow_approval_guard.py --tb=short`

### Liên kết bằng chứng

- Repository: https://github.com/TrnhThnh/K5-L3B-DAY08-Bots-FromWorkflowsToAgents
- Commit test: https://github.com/TrnhThnh/K5-L3B-DAY08-Bots-FromWorkflowsToAgents/commit/c5e3942

## 5. Công cụ AI đã dùng

**Công cụ:** ChatGPT.

**Mục đích sử dụng:**

- Hỗ trợ phân tích yêu cầu của Shape A và các checkpoint.
- Gợi ý cách triển khai Workflow và xử lý crash recovery.
- Hỗ trợ viết test, kiểm tra các tình huống biên và soạn báo cáo.

**Cách tự kiểm tra kết quả:**

- Đối chiếu mã nguồn với API, fixture và yêu cầu của lab.
- Chạy pytest để kiểm tra các nhánh xử lý Workflow.
- Chạy crash safety suite để kiểm tra khả năng phục hồi.
- Chạy trực tiếp 10 test bổ sung, xác nhận kết quả `10 passed`.
- Kiểm tra Git diff và commit trước khi đưa thay đổi lên repository.

Các gợi ý từ AI được kiểm tra lại bằng mã nguồn và kết quả chạy thực tế, không sử dụng đầu ra AI làm bằng chứng kiểm thử.

## 6. Tự đánh giá

Đã hoàn thành phần Shape A — Deterministic Workflow, bao gồm triển khai chức năng, crash recovery và kiểm thử bổ sung.

**Điểm đạt được:**

- Workflow xử lý claim theo luồng xác định, không phụ thuộc LLM.
- Phân tách quyết định nghiệp vụ và thao tác hoàn tiền của host.
- Đạt toàn bộ public Workflow tests đã chạy tại CP4.
- Vượt qua crash safety suite và 10 test bổ sung.

**Hạn chế:**

- Kiểm thử chủ yếu thực hiện trên môi trường mô phỏng của lab.
- Chưa đánh giá với hệ thống hoàn tiền và dữ liệu sản xuất thực tế.

**Hướng cải thiện:**

- Bổ sung thêm các tình huống lỗi và dữ liệu đầu vào bất thường.
- Tích hợp kiểm thử tự động vào CI để phát hiện lỗi khi thay đổi code.
