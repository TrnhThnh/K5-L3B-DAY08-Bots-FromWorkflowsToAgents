# Ghi chú shape D (swarm): baseline và nháp cho ADR / research card

Tài liệu làm việc của người phụ trách D. Số liệu lấy từ bộ public, chạy trong `src/`.
Khi A, B, C xong, chép các đoạn cần thiết sang `decision_adr.md`, `research_card.md`, `group_report.md`.

## 1. Lệnh đã chạy

```text
python -m lab8.benchmark --shapes swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/swarm_baseline.json
python -m lab8.crash_test --count 20 --out reports/crash.json
python -m pytest -q tests/test_swarm_analysis.py
```

`reports/swarm_baseline.json` chỉ là baseline của D. File nộp bắt buộc vẫn là `reports/benchmark.json` gồm đủ 4 shape, chạy ở CP5.

## 2. Baseline swarm (14 claim × 5 seed = 70 trial)

| Metric | Giá trị |
| --- | --- |
| Pass rate | 69/70 = 0.986 |
| Pass^5 | 13/14 = 0.929 |
| Pass theo seed | 11, 22, 33, 44: 1.000 · 55: 0.929 |
| Seed variance (chia N) / min / max | 0.000816 / 0.929 / 1.000 |
| Cost per success (mô phỏng) | 49.57 VND (tổng 3420.12 VND / 69 trial pass) |
| Mean / p95 steps | 2.80 / 3 |
| Mean model calls / tool calls | 3.0 / 4.66 |
| Crash safety | 20/20 (`reports/crash.json`) |
| Lỗi duy nhất | `R-swarm-C-002-s55`: `status resolved != denied` |

Cost một trial ở seed 11: khoảng 52.2–52.4 VND với claim có đơn hợp lệ, 42.2 với `escalated` (C-005), 12.28 với `needs_info` (C-004). Trial lỗi C-002 seed 55 tốn 62.22 VND: thêm một tool call vì phải tính lại quote. Tức là **trial sai còn đắt hơn trial đúng**.

## 3. Vì sao swarm fail C-002 ở seed 55

- Ticket ghi "trễ 5 ngày", cột `delay_days` của đơn O-202 ghi 2 ngày. Theo luật, trễ dưới 3 ngày thì không hoàn, nên đáp án là `denied`, 0 VND.
- Khối `REFERENCE_WEAKNESS` trong `swarm_reference.py`: khi `seed % 5 == 0` và số ngày parse từ ticket khác DB, swarm ghi đè `delay_days` bằng số trong ticket, rồi tính lại quote. Kết quả: `resolved`, trả 20.000 VND.
- Host **không chặn được** lỗi này: approval hợp lệ, đúng chủ đơn, chưa hoàn lần nào. Cổng của host chỉ kiểm quyền và idempotency, không kiểm dữ liệu đầu vào của quote. Lỗi nằm ở tầng quyết định của shape.
- Trace có ghi event `model_override` ở đúng trial đó, nên lỗi được phát hiện bằng trace mà không cần đọc lại code.

Bài học cho A, B, C: số tiền phải lấy từ `compute_compensation` trên **order row trong DB**. Chữ trong ticket là dữ liệu người dùng, không phải sự thật.

## 4. Test đã thêm: `src/tests/test_swarm_analysis.py` (14 test, chạy trong cổng host)

| Test | Chứng minh |
| --- | --- |
| `test_weakness_fires_only_on_seed_divisible_by_5` | C-002 chỉ fail ở seed 55 (trả 20.000), seed khác `denied`. `model_override` chỉ xuất hiện ở seed 55 |
| `test_weakness_only_hits_t02_on_public_set` | Trên 12 claim × 5 seed, override và trial fail đều chỉ là `(C-002, 55)` |
| `test_swarm_is_deterministic_per_seed` | Cùng seed thì cùng kết quả và cost: variance đến từ seed, không phải nhiễu |
| `test_swarm_pays_peer_overhead_on_every_claim_with_order` | Swarm luôn gọi model 3 lần (peer, parse, draft), kể cả claim đơn giản |
| `test_swarm_never_leaks_parent_secret` | Ở 5 seed, kết quả và trace không có `CANARY_SECRET` hay `Bearer` |
| `test_swarm_crash_then_resume_keeps_one_refund` | Crash ở cả 3 điểm rồi resume vẫn còn đúng một dòng refund. Crash suite gốc chỉ thử swarm ở một điểm |

Sau khi thêm, `python -m pytest -q` ra `68 passed, 248 deselected` (54 + 14).

## 5. Nháp cho `decision_adr.md` (phần so sánh với swarm)

> Swarm (D) đạt pass 0.986 nhưng pass^5 chỉ 0.929 và có variance khác 0 vì một trial trên năm seed tin số ngày trong ticket. Lỗi này không phải nhiễu ngẫu nhiên mà là lỗi quyết định có hệ thống, lặp lại đúng ở seed 55, và host không chặn được vì approval vẫn hợp lệ. Chi phí: swarm tốn 3 model call mỗi trial (49.57 VND/success). Shape được chọn phải [điền số của shape nhóm chọn: pass, pass^5, variance, cost/success] trên cùng 14 claim × 5 seed. Nếu shape ít tự chủ hơn đạt pass^5 = 1.0 với cost thấp hơn, thì không có lý do để trả thêm cost cho multi-agent. Quyết định chỉ đảo lại nếu bộ hidden có loại claim mà chỉ investigator song song mới xử lý được, và swarm vẫn giữ 0 leak, 0 bypass.

## 6. Nháp cho `research_card.md` (đề xuất R2, nhóm chốt lại)

| Field | Nháp |
| --- | --- |
| CÂU | R2 |
| SOURCE | Cemri và cộng sự, *Why Do Multi-Agent LLM Systems Fail?* (MAST), NeurIPS 2025, arXiv 2503.13657. Loại bằng chứng: phân tích và gán nhãn trace của nhiều framework multi-agent mã nguồn mở |
| CLAIM | Lỗi của hệ multi-agent gom được thành 3 nhóm: lỗi đặc tả / thiết kế hệ thống, lệch giữa các agent, và lỗi kiểm chứng / kết thúc task. Một phần lớn lỗi đến từ thiết kế hệ thống, không chỉ từ năng lực model |
| BOUNDARY | Kết luận rút từ trace của các framework và model mà paper khảo sát, task chủ yếu là lập trình và giải toán. Không phải task hoàn tiền có ledger, cũng không dùng MockLLM |
| HYPOTHESIS | Lỗi C-002 seed 55 của swarm thuộc nhóm **kiểm chứng**: swarm nhận số ngày trong ticket mà không đối chiếu với order row. Đổi D → A (workflow luôn lấy `delay_days` từ DB) thì pass^5 tăng 0.929 → 1.0, variance về 0, cost/success giảm vì ít model call hơn |
| METHOD | Cố định: MockLLM, tool, seed `11,22,33,44,55`, 14 claim public, `config/pricing.yaml`, evaluator `lab8.metrics`. Biến duy nhất thay đổi: shape (swarm → workflow) |
| FAILURE / METRIC | Lỗi dự kiến: tin dữ liệu ticket thay cho DB. Đo bằng pass^5, seed variance, số trial có `model_override` trong trace, cost/success |

Phần "Kết quả ablation" điền sau khi workflow chạy được, bằng lệnh benchmark 4 shape ở CP5. Trước khi nộp, đối chiếu lại tên paper và nội dung CLAIM với bản gốc.

## 7. Giới hạn

MockLLM không phải model sản xuất. Latency là `unavailable`. Cost là giá mô phỏng, không phải hóa đơn API.
