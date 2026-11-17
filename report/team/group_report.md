# Báo cáo nhóm — Lab 8 LogiX-VN

## 1. Thông tin nhóm

- Tên nhóm: BOTS
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): 166907f

| Thành viên | MSSV | Phần việc |
| --- | --- | --- |
| Trần Đức Trung | 2A202603938 | Shape A (workflow), crash recovery, 10 test workflow |
| Đỗ Anh Thư | 2A202603815 | Shape B (single agent ReAct), crash recovery CP3, 8 test single |
| Trịnh Hưng Thịnh | 2A202603907 | Shape C (orchestrator, investigator chỉ đọc), handoff, trace an toàn, test orchestrator, tự kiểm `student_drop/` |
| Dương Minh Chiến | 2A202603921 | Shape D (swarm tham chiếu), 14 test swarm, benchmark, crash suite, ADR, research card |

## 2. Mục tiêu và cách tiếp cận

Bài toán là xử lý claim hoàn phí ship cho đơn giao trễ hoặc hàng hỏng của LogiX-VN. Mỗi claim có ticket do khách viết, một order row trong SQLite, có thể có approval, và một policy hiện hành. Nhóm đọc đề theo ba ý chính. Ticket là dữ liệu người dùng nhập, không dùng để tính tiền. Số tiền do `compute_compensation` tính trên order row và policy. Chỉ host (`durability.issue_refund`) được kiểm approval, áp trần theo đơn và ghi ledger.

Nhóm có 4 người, mỗi người nhận một shape. A, B, C là ba shape nhóm phải viết. D là swarm có sẵn trong `swarm_reference.py`, không được sửa, nên người nhận D làm baseline, viết test cho nó và lo phần đo đạc chung.

Thứ tự làm bám theo checkpoint. Ba shape A, B, C viết song song trên nhánh riêng. Trong lúc đó D đo swarm trước để có baseline. Code vào `main` qua PR: shape C (PR #1), test swarm (PR #2), shape A (PR #3); shape B gộp từ nhánh `DoAnhThu`. Khi đủ bốn shape, nhóm chạy benchmark 4 shape × 14 claim × 5 seed và crash suite trên commit `166907f`, rồi chọn shape trong ADR. Cuối cùng là tự kiểm trên `student_drop/` và viết báo cáo.

## 3. Giải pháp

Cả ba shape dùng chung một ranh giới (theo `docs/architecture.md`): code lọc theo principal, chọn policy hiệu lực và tính tiền; host kiểm approval, idempotency, trần theo đơn và ghi refund trong một transaction. Model (MockLLM) chỉ được soạn câu chữ hoặc lập kế hoạch trong phạm vi code cho phép. Ba shape đều truyền quote đầy đủ vào `durability.issue_refund`. Host đã tự trừ phần mà các claim trước của cùng đơn đã nhận, nên nếu shape trừ trước thì tiền sẽ bị trừ hai lần.

### Shape A — Deterministic Workflow

`src/lab8/shapes/workflow.py` là một chuỗi bước Python cố định trong `run_claim()`, không gọi model (model calls trung bình 0.0):

1. `get_claim_view()` đọc claim. Không có claim thì trả `failed`, thiếu `order_id` thì trả `needs_info`.
2. `lookup_order()` đọc đơn theo principal. Không thấy đơn thì trả `escalated`.
3. `compute_compensation()` tính quote. Quote bằng 0 thì trả `denied` và không gọi host.
4. Quote dương thì gọi `issue_refund()` với quote đầy đủ và `crash_at`. Host trả ok thì `resolved`, bị chặn thì `denied` hoặc `failed`.

Mọi nhánh return đi qua `finish()` để trả `RunResult` và ghi trace. Trace của workflow có 5 loại event: `claim_lookup` (`found`), `order_lookup` (`visible`, `reason`), `quote` (`amount_vnd`, `reason`, `clause_ids`), `refund_result` (`ok`, `reason`) và `decision` (`status`, `reason`). Workflow không bắt `InjectedCrash`. Crash đi ra ngoài, lần chạy lại dựa vào ledger để không hoàn trùng.

### Shape B — Single Agent ReAct

`src/lab8/shapes/single.py` chạy một vòng `run_react` tối đa 8 bước. Hàm `decide` chọn tool tiếp theo dựa trên kết quả bước trước: thiếu `order_id` thì dừng với `needs_info`; sau `lookup_order` nếu đơn không thấy thì `escalated`, thấy thì gọi `compute_compensation`; quote bằng 0 thì `denied`, dương thì `ready_to_refund`. Agent chỉ có tool đọc, không gọi `issue_refund` trong vòng lặp. Sau vòng lặp, code mới gọi host với quote đầy đủ. MockLLM được gọi một lần ở bước `draft` để soạn câu trả lời (model calls trung bình 1.0), không quyết định số tiền.

Trace của single có các event `react_step` (tool, `visible`), `quote`, `decision` và `error` khi claim không tồn tại. Khi gặp `InjectedCrash`, single ghi event `crash` rồi ném lỗi ra ngoài.

### Shape C — Orchestrator và investigator chỉ đọc

`src/lab8/shapes/orchestrator.py` đọc claim, trả `failed` hoặc `needs_info` như A. Sau đó gọi MockLLM một lần ở bước `plan`, rồi tạo `handoff.v1` bằng `make_handoff` với `facts` rỗng, nhiệm vụ cố định `check_applicable_policy` và bốn tool đọc: `lookup_order`, `lookup_policy`, `lookup_refund_history`, `compute_compensation`. Investigator chạy qua `run_readonly_investigators` và không có registry ghi, nên không thể gọi `issue_refund`. Orchestrator nhận kết quả, trả `escalated` nếu không thấy đơn, `denied` nếu quote bằng 0, còn quote dương thì tự gọi host.

Handoff được sanitize bằng code, không dùng tóm tắt của model. `handoff.py` bỏ mọi field ngoài `ALLOWED_FIELDS`, rồi từ chối nếu còn sót canary. Ticket, `parent_secret`, raw header và parent context không vào handoff. Tool đọc trong `tools.py` chỉ trả các field allowlist của đơn (`order_id`, `status`, `delay_days`, `shipping_fee_vnd`, `paid_vnd`, `damage_verified`, `carrier`...), nên số điện thoại, địa chỉ, tên hàng và ghi chú nội bộ không đi ra khỏi tầng tool.

Trace của orchestrator có `claim` (`found`), `handoff`, `investigator` (kết quả `lookup_order` và lịch sử refund đã lọc), `quote`, `refund` (`ok`, `reason`) và `decision`. Khối `finally` ghi trace và đóng kết nối SQLite cả khi crash, rồi để `InjectedCrash` đi ra ngoài.

### Những gì trace cố ý không ghi

Cả ba shape không ghi claim row đầy đủ, nội dung ticket, `parent_secret`, header `Authorization`, số điện thoại, địa chỉ, tên hàng và ghi chú nội bộ. Claim row chứa secret của parent, order row đầy đủ chứa PII. Trace chỉ giữ cờ, lý do và số tiền, đủ để biết shape đã quyết định gì.

## 4. Kết quả

Số liệu lấy từ `src/reports/benchmark.json`: 14 claim public × seed 11, 22, 33, 44, 55, mỗi shape 70 trial, chạy trên commit `166907f`.

| Shape | pass | pass^5 | seed min-max | variance | cost/success (VND) | mean / p95 steps |
| --- | --- | --- | --- | --- | --- | --- |
| workflow | 1.000 | 1.000 | 1.000-1.000 | 0 | 27.86 | 4.43 / 5 |
| single | 1.000 | 1.000 | 1.000-1.000 | 0 | 28.79 | 2.79 / 3 |
| orchestrator | 1.000 | 1.000 | 1.000-1.000 | 0 | 56.20 | 5.36 / 6 |
| swarm | 0.986 | 0.929 | 0.929-1.000 | 0.000816 | 49.57 | 2.80 / 3 |

Crash safety là 20/20 (`src/reports/crash.json`). Trên `main` hiện tại, ma trận student (`python -m pytest -q -m student -o addopts=`) ra 258 passed, 0 failed, và cổng host `python -m pytest -q` ra 81 passed. `python -m lab8.check_submission` ra 0 FAIL, 0 WARN.

Ba shape nhóm viết pass hết 70 trial. Swarm sai một trial, `R-swarm-C-002-s55`: ở seed 55 nó lấy số ngày trễ trong ticket (5 ngày) thay cho order row (2 ngày) và trả 20.000 VND thay vì từ chối. Trial này tốn 62.22 VND, cao hơn trial đúng của swarm (khoảng 52.3) vì phải tính lại quote. Đối chứng `R-workflow-C-002-s55` ra `denied`, `no_entitlement`. Phân tích chi tiết ở `report/team/swarm_notes.md`.

### Tự kiểm trên `student_drop/`

Lệnh (chạy trong `src/`, dữ liệu đặt ở `student_drop/` tại gốc repo):

```text
python -m lab8.benchmark --shapes workflow,single,orchestrator --cases ../student_drop/hidden_claims.jsonl --world ../student_drop/hidden_world_state.json --seeds 11,22,33,44,55 --out reports/hidden_selfcheck.json
```

Kết quả ở `src/reports/hidden_selfcheck.json`, 40 claim × 5 seed = 200 trial mỗi shape:

| Shape | denied | resolved | escalated | needs_info | leak_suspect | lỗi chạy |
| --- | --- | --- | --- | --- | --- | --- |
| workflow | 95 | 90 | 10 | 5 | 0 | 0 |
| single | 95 | 90 | 10 | 5 | 0 | 0 |
| orchestrator | 95 | 90 | 10 | 5 | 0 | 0 |

Bộ này không có nhãn, nên pass rate, pass^5 và cost/success để null, và nhóm không kết luận đã đạt ngưỡng hidden 0.75. Hai điều đọc được từ file: ở cả 40 claim, ba shape cho cùng trạng thái và cùng số tiền quote ở cả 5 seed; và không trace hidden nào chứa `CANARY_SECRET` hay `Bearer`. Chiến chạy lại riêng cùng bộ dữ liệu và được 600 trial trùng khớp với file đã commit.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Pytest trên Windows lỗi quyền ghi thư mục temp và cache. Thịnh chạy với thư mục temp trong workspace và tắt cache plugin, không sửa file thước đo:

```text
.\.venv\Scripts\python.exe -m pytest -q --basetemp=.thinh-update-host-tmp -p no:cacheprovider
```

Git chặn pull vì file untracked ở máy trùng tên với file vừa được commit trên `main`. Lỗi này gặp hai lần: lúc Thư kéo code về, và lúc kéo `src/reports/hidden_selfcheck.json` mà Thịnh đã commit trong khi máy của Chiến có bản tự chạy. Lần sau, Chiến chuyển file của mình ra ngoài repo, pull, rồi so hai file: 600 trial trùng nhau nên giữ bản đã commit.

```text
error: The following untracked working tree files would be overwritten by merge:
	src/reports/hidden_selfcheck.json
```

File zip `student_drop` nén trên macOS. Lần giải nén đầu chỉ lấy ra `._hidden_claims.jsonl` và `._hidden_world_state.json` (163 byte, metadata `com.apple.provenance` trong `__MACOSX`), không có claim nào. Nhóm lấy lại đúng hai file `hidden_claims.jsonl` (40 claim) và `hidden_world_state.json` từ thư mục `student_drop/` trong zip.

Crash suite gốc chỉ thử swarm ở điểm `after_effect_before_checkpoint`. Để chắc phần resume, single, orchestrator và swarm có thêm test crash ở cả ba điểm `before_effect`, `after_effect_before_checkpoint`, `after_checkpoint` (`test_single_agent.py`, `test_thinh_orchestrator.py`, `test_swarm_analysis.py`). Test của workflow (`test_workflow_approval_guard.py`) thử crash ở `after_effect_before_checkpoint`. Sau mỗi lần resume vẫn chỉ có một dòng refund.

Swarm pass 0.986 trên bộ public mà lúc đầu chưa rõ vì sao. Đọc trace thấy event `model_override` ở đúng trial `R-swarm-C-002-s55`, rồi lần ra khối `REFERENCE_WEAKNESS` trong `swarm_reference.py` (chỉ bật khi `seed % 5 == 0` và số ngày trong ticket khác DB). Test `test_weakness_only_hits_t02_on_public_set` khóa lại kết luận này trên 12 claim × 5 seed.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`. Cost là giá mô phỏng trong `config/pricing.yaml`, không phải hóa đơn API.

Số pass chỉ đo trên 14 claim public. Bộ hidden 40 claim không có nhãn ở phía nhóm, nên chưa biết pass thật trên hidden. Ba shape cho kết quả giống nhau trên hidden là dấu hiệu tốt nhưng không chứng minh là đúng, vì cả ba dùng chung `compute_compensation`, `policy.py` và host; nếu một luật nghiệp vụ bị hiểu sai ở tầng chung thì ba shape sẽ sai giống nhau.

Lỗi của swarm được cài sẵn (`REFERENCE_WEAKNESS`), không phát sinh tự nhiên như với model thật. Vì vậy kết luận "swarm kém hơn workflow" ở đây chỉ đúng cho swarm tham chiếu này. Investigator của orchestrator chạy cùng process với orchestrator, nên bài chưa thử trường hợp agent con bị tách ra hoặc chạy song song.

Nhóm sẽ xét lại lựa chọn workflow nếu bộ hidden có loại claim mà luật cố định không xử lý được, ví dụ phải đọc nhiều nguồn mới ra quyết định, và một shape multi-agent pass thêm ở đó mà vẫn giữ 0 leak, 0 bypass. Khi đó phải so lại bằng pass^5 và cost/success trên cùng 40 claim × 5 seed. Hướng cải thiện khác: chạy test và benchmark trong CI cho mỗi PR, thêm test crash ở đủ ba điểm cho workflow, và thêm test cho các dạng claim hidden nhắm tới (homoglyph, principal lẫn, approval mượn của claim khác) vào bộ test của nhóm.

## 8. Tài liệu tham khảo

- Cemri và cộng sự, *Why Do Multi-Agent LLM Systems Fail?* (MAST), NeurIPS 2025 Datasets and Benchmarks Track, https://arxiv.org/abs/2503.13657. Dùng trong `research_card.md` để phân loại lỗi của swarm.
- `docs/architecture.md`: bốn shape, ranh giới code / model, handoff.
- `docs/business_rules.md`: luật hoàn phí, approval, trần theo đơn.
- `docs/contracts.md`: trace contract v1.
- `docs/metrics.md`: định nghĩa pass rate, pass^5, variance, cost/success.
