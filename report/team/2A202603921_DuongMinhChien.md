# Báo cáo cá nhân — 2A202603921_DuongMinhChien

## 1. Thông tin thành viên

- Họ tên: Dương Minh Chiến
- MSSV: 2A202603921
- Email:
- GitHub: duongchien147

## 2. Phần việc phụ trách

Shape D (swarm tham chiếu) và phần đo đạc của nhóm. Swarm có sẵn trong `src/lab8/shapes/swarm_reference.py` và không được sửa, nên phần việc của tôi là đo nó làm baseline, viết test cho nó, chạy benchmark và crash suite, rồi đưa số liệu vào ADR, research card và mục 4 của báo cáo nhóm.

## 3. Đóng góp cụ thể

Commit `ed6ba8c` (PR #2) thêm `src/tests/test_swarm_analysis.py` với 14 test chạy trong cổng host:

- `test_weakness_fires_only_on_seed_divisible_by_5`: C-002 chỉ fail ở seed 55, trace có `model_override` ở đúng trial đó.
- `test_weakness_only_hits_t02_on_public_set`: trên 12 claim × 5 seed, chỉ `(C-002, 55)` bị override và fail.
- `test_swarm_is_deterministic_per_seed`: cùng seed thì cùng kết quả và cost.
- `test_swarm_pays_peer_overhead_on_every_claim_with_order`: swarm gọi model 3 lần cho mọi claim.
- `test_swarm_never_leaks_parent_secret`: không có `CANARY_SECRET` hay `Bearer` trong kết quả và trace ở cả 5 seed.
- `test_swarm_crash_then_resume_keeps_one_refund`: crash ở cả 3 điểm rồi resume vẫn còn một dòng refund. Crash suite gốc chỉ thử swarm ở một điểm.

Cùng commit đó có `src/reports/crash.json` (20/20), `src/reports/swarm_baseline.json` và `report/team/swarm_notes.md`.

Commit `be417ce` (PR #4) thêm `src/reports/benchmark.json` (4 shape × 14 claim × 5 seed), điền `decision_adr.md`, `research_card.md` (R2, ablation swarm → workflow) và mục 4 của `group_report.md`.

Quyết định kỹ thuật tôi đề xuất là chọn `workflow`. Ba shape nhóm viết cùng đạt pass^5 1.000, và workflow có cost/success thấp nhất (27.86 VND, so với 28.79 của single và 56.20 của orchestrator), không gọi model lần nào.

## 4. Bằng chứng

- Test: `src/tests/test_swarm_analysis.py`, 14 passed. Cổng host `python -m pytest -q` ra 73 passed sau khi merge cùng test của orchestrator.
- Run id: `R-swarm-C-002-s55` (swarm trả 20.000 VND thay vì `denied`), đối chứng `R-workflow-C-002-s55` (`denied`, `no_entitlement`).
- Report: `src/reports/benchmark.json`, `src/reports/crash.json`, `src/reports/swarm_baseline.json`.
- Số của swarm: pass 0.986, pass^5 0.929, variance 0.000816, cost/success 49.57 VND.
- PR: #2 (test và baseline swarm), #4 (benchmark và báo cáo).

## 5. Công cụ AI đã dùng

Trợ lý AI lập trình chạy trong VS Code. Tôi dùng nó để đọc codebase, giải thích cơ chế `REFERENCE_WEAKNESS` của swarm, gợi ý và viết test trong `test_swarm_analysis.py`, chạy benchmark và crash suite, và soạn nháp ADR, research card.

Cách kiểm tra: chạy lại `python -m pytest -q`, `python -m pytest -q -m student -o addopts=` (248 passed) và `python -m lab8.check_submission`. Đối chiếu từng con số trong báo cáo với `src/reports/benchmark.json`. Đọc trace `R-swarm-C-002-s55` và `R-workflow-C-002-s55` để xác nhận lỗi seed 55. Phần trích dẫn paper MAST trong research card cần đối chiếu lại với bản gốc trên arXiv.

## 6. Tự đánh giá

