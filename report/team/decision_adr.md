# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: 166907f
- Run id dẫn chứng: R-workflow-C-002-s55 (đối chứng R-swarm-C-002-s55), src/reports/benchmark.json
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000-1.000 / 0.000000 (14 claim public × seed 11,22,33,44,55 = 70 trial)
- Cost per success (mô phỏng, VND): 27.86
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0 trên 70 trial public

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Cả bốn shape chạy trên cùng 14 claim public, cùng 5 seed, cùng MockLLM và bảng giá (`src/reports/benchmark.json`). Workflow, single và orchestrator đều đạt pass 1.000, pass^5 1.000, variance 0. Swarm đạt pass 0.986, pass^5 0.929, variance 0.000816, vì sai đúng một trial là C-002 ở seed 55. Giữa ba shape cùng điểm, workflow rẻ nhất: 27.86 VND mỗi trial pass, so với 28.79 của single và 56.20 của orchestrator. Workflow không gọi model lần nào (mean model calls 0.0), tiền do `compute_compensation` tính trên order row, nên ticket không thể đổi số tiền. Bài yêu cầu chọn shape ít tự chủ nhất mà vẫn làm được việc, và trên bộ public đó là workflow.

| Shape | pass | pass^5 | seed min-max | variance | cost/success (VND) | mean / p95 steps | model calls TB |
| --- | --- | --- | --- | --- | --- | --- | --- |
| workflow | 1.000 | 1.000 | 1.000-1.000 | 0 | 27.86 | 4.43 / 5 | 0.0 |
| single | 1.000 | 1.000 | 1.000-1.000 | 0 | 28.79 | 2.79 / 3 | 1.0 |
| orchestrator | 1.000 | 1.000 | 1.000-1.000 | 0 | 56.20 | 5.36 / 6 | 0.93 |
| swarm | 0.986 | 0.929 | 0.929-1.000 | 0.000816 | 49.57 | 2.80 / 3 | 3.0 |

## Có đáng đổi lấy multi-agent không

Trên bộ public thì không. Orchestrator không pass thêm trial nào so với workflow mà tốn gấp khoảng 2 lần (56.20 so với 27.86). Swarm vừa tốn hơn (49.57) vừa kém hơn: ở seed 55 nó lấy số ngày trễ trong ticket ("trễ 5 ngày") thay cho cột `delay_days` (2 ngày) và trả 20.000 VND cho claim lẽ ra bị từ chối. Host không chặn lỗi này vì approval vẫn hợp lệ. Trial sai còn đắt hơn trial đúng: 62.22 VND so với khoảng 52.3, vì swarm phải tính lại quote.

Nhóm sẽ xét lại nếu bộ hidden có loại claim mà workflow không xử lý được bằng luật cố định, ví dụ cần đọc nhiều nguồn mới ra quyết định, và multi-agent pass thêm ở đó mà vẫn giữ 0 leak, 0 bypass. Khi đó phải so lại bằng pass^5 và cost/success trên cùng 40 claim × 5 seed, không so một lần chạy lẻ.

## Trace và bằng chứng

Trace của workflow ghi 5 loại event: `claim_lookup` (chỉ có `found`), `order_lookup` (`visible`, `reason`), `quote` (`amount_vnd`, `reason`, `clause_ids`), `refund_result` (`ok`, `reason`), và `decision` (`status`, `reason`) ở mọi nhánh return. Ví dụ `R-workflow-C-002-s55` có 4 event và kết thúc bằng `denied`, `no_entitlement`.

Trace cố ý không ghi claim row, order row, nội dung ticket, `parent_secret`, header, số điện thoại, địa chỉ, tên hàng và ghi chú nội bộ. Claim row chứa secret của parent, order row chứa PII. Trace chỉ giữ cờ và số tiền, đủ để biết shape đã quyết định gì.

Trace nằm trong `src/traces/<run_id>.json`, đúng chỗ grader quét. Quét 70 trace workflow và các trace còn lại của benchmark không thấy `CANARY_SECRET` hay `Bearer`. Test `tests/test_swarm_analysis.py::test_swarm_never_leaks_parent_secret` kiểm điều này cho swarm ở cả 5 seed.

## Giới hạn

MockLLM không phải model sản xuất. Latency để `unavailable`. Cost là giá mô phỏng trong `config/pricing.yaml`, không phải hóa đơn API. Các số trên chỉ đo trên 14 claim public. Ngưỡng 0.75 được chấm trên bộ hidden 40 claim × 5 seed. Không sửa JSON cho đủ 0.75.
