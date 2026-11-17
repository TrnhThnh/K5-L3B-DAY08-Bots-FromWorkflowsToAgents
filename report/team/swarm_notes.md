# Ghi chú shape D (swarm)

Phân tích của người phụ trách D trên bộ public. Mọi lệnh chạy trong `src/`. Kết luận đã được đưa vào `decision_adr.md`, `research_card.md` và mục 4 của `group_report.md`.

## 1. Lệnh đã chạy

```text
python -m lab8.benchmark --shapes swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/swarm_baseline.json
python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
python -m lab8.crash_test --count 20 --out reports/crash.json
python -m pytest -q tests/test_swarm_analysis.py
```

`reports/swarm_baseline.json` là số đo swarm chạy riêng, lấy trước khi ba shape còn lại xong. File nộp chính thức là `reports/benchmark.json`. Số của swarm trong hai file trùng nhau.

## 2. Baseline swarm (14 claim × 5 seed = 70 trial)

| Metric | Giá trị |
| --- | --- |
| Pass rate | 69/70 = 0.986 |
| Pass^5 | 13/14 = 0.929 |
| Pass theo seed | seed 11, 22, 33, 44: 1.000; seed 55: 0.929 |
| Seed variance (chia N) / min / max | 0.000816 / 0.929 / 1.000 |
| Cost per success (mô phỏng) | 49.57 VND (tổng 3420.12 VND / 69 trial pass) |
| Mean / p95 steps | 2.80 / 3 |
| Model calls / tool calls trung bình | 3.0 / 4.66 |
| Crash safety | 20/20 (`reports/crash.json`) |
| Trial lỗi | `R-swarm-C-002-s55`: `status resolved != denied` |

Ở seed 11, một trial swarm có đơn hợp lệ tốn khoảng 52.2 đến 52.4 VND. C-005 (`escalated`) tốn 42.2, C-004 (`needs_info`) tốn 12.28. Trial lỗi C-002 seed 55 tốn 62.22 VND vì thêm một tool call để tính lại quote, nên trial sai lại đắt hơn trial đúng.

## 3. Vì sao swarm fail C-002 ở seed 55

Ticket của C-002 ghi "trễ 5 ngày", còn cột `delay_days` của đơn O-202 ghi 2 ngày. Theo luật, trễ dưới 3 ngày thì không được hoàn, nên đáp án là `denied` với 0 VND.

Trong `swarm_reference.py`, khối `REFERENCE_WEAKNESS` chạy khi `seed % 5 == 0` và số ngày parse từ ticket khác số trong DB. Khi đó swarm ghi đè `delay_days` bằng số trong ticket rồi tính lại quote, ra `resolved` và trả 20.000 VND.

Host không chặn được lỗi này. Approval hợp lệ, principal đúng chủ đơn, đơn chưa được hoàn lần nào. Cổng của host kiểm quyền và idempotency chứ không kiểm dữ liệu dùng để tính quote, nên lỗi nằm ở tầng quyết định của shape.

Trace ghi event `model_override` ở đúng trial này. Đọc trace là thấy lỗi, không cần mở code.

Với ba shape còn lại, số tiền phải tính bằng `compute_compensation` trên order row trong DB. Chữ trong ticket là dữ liệu người dùng nhập. Workflow, single và orchestrator đều làm như vậy và cùng trả `denied` cho C-002 ở seed 55.

## 4. So với ba shape nhóm viết

| Shape | pass^5 | variance | cost/success (VND) | model calls TB |
| --- | --- | --- | --- | --- |
| workflow | 1.000 | 0 | 27.86 | 0.0 |
| single | 1.000 | 0 | 28.79 | 1.0 |
| orchestrator | 1.000 | 0 | 56.20 | 0.93 |
| swarm | 0.929 | 0.000816 | 49.57 | 3.0 |

Swarm là shape duy nhất có variance khác 0. Nó tốn gần gấp đôi workflow cho mỗi trial pass, và 3 model call mỗi claim (peer, parse, draft) không giúp pass thêm claim nào.

## 5. Test đã thêm: `src/tests/test_swarm_analysis.py`

14 test, chạy trong cổng host (không có marker `student`).

| Test | Kiểm điều gì |
| --- | --- |
| `test_weakness_fires_only_on_seed_divisible_by_5` | C-002 chỉ fail ở seed 55 (trả 20.000), các seed khác ra `denied`. `model_override` chỉ có ở seed 55 |
| `test_weakness_only_hits_t02_on_public_set` | Trên 12 claim × 5 seed, override và trial fail đều chỉ là `(C-002, 55)` |
| `test_swarm_is_deterministic_per_seed` | Cùng seed thì cùng kết quả và cost. Variance đến từ seed, không phải nhiễu |
| `test_swarm_pays_peer_overhead_on_every_claim_with_order` | Swarm gọi model 3 lần cho mọi claim, kể cả claim đơn giản |
| `test_swarm_never_leaks_parent_secret` | Ở cả 5 seed, kết quả và trace không có `CANARY_SECRET` hay `Bearer` |
| `test_swarm_crash_then_resume_keeps_one_refund` | Crash ở cả 3 điểm rồi resume vẫn còn một dòng refund. Crash suite gốc chỉ thử swarm ở `after_effect_before_checkpoint` |

Sau khi merge cùng test của orchestrator, `python -m pytest -q` ra 73 passed, 248 deselected.

## 6. Giới hạn

MockLLM không phải model sản xuất. Latency là `unavailable`. Cost là giá mô phỏng, không phải hóa đơn API. Lỗi của swarm được cài sẵn để tạo variance, không tự phát sinh như lỗi của một model thật.
