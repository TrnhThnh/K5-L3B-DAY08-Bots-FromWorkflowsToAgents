# Bonus B3 — Code verifier cho swarm

Chỉ một topic B3, theo docs/bonus_topics.md. Không sửa reference, host, metrics, policy, config hay public fixtures. swarm_verified.py dẫn xuất từ swarm_reference.py trong starter, giữ peer/parse/draft và lỗi override của baseline để đo tác động riêng của verifier.

## Chạy trong src

```powershell
.\.venv\Scripts\python.exe -m bonus.build_cases
.\.venv\Scripts\python.exe -m pytest -q tests/test_bonus_swarm_verified.py --basetemp=.bonus-tests-tmp -p no:cacheprovider
.\.venv\Scripts\python.exe -m bonus.evaluate --student-drop ../student_drop
.\.venv\Scripts\python.exe -m bonus.report
```

Trên máy không có student_drop, bỏ cờ --student-drop; public và đối kháng vẫn chạy offline. Có thể dùng python thay đường dẫn .venv nếu đã activate môi trường.

Runner gọi lab8.benchmark qua --extra-shape cho từng corpus, sau đó replay từng trial trên SQLite mới để audit safety, kiểm tra usage/status trùng benchmark, đếm verifier_override và lưu một ví dụ trace sạch. Chỉ counts và field-name events đi vào summary, không dump secret/PII.

## Kiến trúc

1. Giữ cách swarm đọc claim, handoff, investigator và peer/parse calls.
2. Giữ candidate order và quote của swarm, gồm override delay có chủ ý.
3. Đọc lại order bằng lookup_order có principal scope, tính chi phí read tool.
4. So tất cả ORDER_FIELDS, gồm delay_days, status, damage_verified, shipping_fee_vnd, paid_vnd, order_id và carrier. Nếu lệch, quote lại từ bản authoritative đúng một lần; không sửa candidate hoặc lặp repair.
5. Kiểm trước cả nhánh quote=0, tránh mất quyền lợi do ticket nói thiếu ngày.
6. Host vẫn là writer duy nhất, nhận quote đầy đủ; approval/idempotency không đổi.
7. RunResult dùng shape và run_id swarm_verified riêng, trace có verifier_check/verifier_override.

## Dữ liệu

cases.jsonl có 10 claim tự tạo với nhãn viết tay trong build_cases.py; world.json lấy bản sao policy public và các order/approval giả riêng. Không dùng quote để sinh nhãn, không lấy nhãn từ hidden. Các case phủ nói quá/nói thiếu, damage giả/đã xác minh, trạng thái hủy, cộng ship+damage, thiếu/mượn approval, nhiều con số và top-up sau refund lịch sử.

## Bằng chứng

- reports/bonus_public.json: workflow/swarm/swarm_verified trên public.
- reports/bonus_adversarial.json: cùng ba shape trên 10 case mới.
- reports/bonus_student_drop.json: tự kiểm không nhãn khi có dữ liệu; không tính pass rate.
- reports/bonus_summary.json: metric từ benchmark, audit safety, số lần override, ví dụ trace và 15 case crash/resume/replay của biến thể.
- report/team/bonus_report.md ở root repo: báo cáo tối đa hai trang nội dung chính.

Không sửa JSON bằng tay. Không commit student_drop/, traces/ hay SQLite. Topic bonus chỉ được tính điểm khi workflow (shape nhóm chọn) qua must-pass và hidden pass rate >=0.80 do grader giảng viên xác nhận; selfcheck không chứng minh gate này.
