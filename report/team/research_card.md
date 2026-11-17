# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R2 |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Cemri và cộng sự, *Why Do Multi-Agent LLM Systems Fail?* (MAST), NeurIPS 2025, https://arxiv.org/abs/2503.13657. Bằng chứng: phân tích và gán nhãn trace chạy thật của nhiều framework multi-agent mã nguồn mở |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Lỗi của hệ multi-agent xếp được vào 3 nhóm: lỗi đặc tả và thiết kế hệ thống, lệch giữa các agent, và lỗi kiểm chứng hoặc kết thúc task. Nhiều lỗi đến từ cách thiết kế hệ thống chứ không chỉ do model yếu |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Paper rút kết luận từ trace của các framework và model mà nó khảo sát, task chủ yếu là lập trình và giải toán. Không có task hoàn tiền có ledger, không dùng MockLLM, nên ở lab này chỉ dùng taxonomy để phân loại lỗi, không dùng tỷ lệ lỗi của paper |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Lỗi C-002 seed 55 của swarm thuộc nhóm kiểm chứng: swarm nhận số ngày trễ trong ticket mà không đối chiếu order row. Đổi swarm (D) sang workflow (A), luôn lấy `delay_days` từ DB, thì pass^5 tăng từ 0.929 lên 1.0, variance về 0, cost/success giảm vì không có peer call |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Cố định: MockLLM, tool trong `config/tools.manifest.v1.1.yaml`, seed 11,22,33,44,55, 14 claim public, `config/pricing.yaml`, evaluator `lab8.metrics`, `as_of` 2026-11-15, mỗi trial một SQLite mới. Biến duy nhất thay đổi: shape (swarm → workflow) |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: tin dữ liệu trong ticket thay cho DB. Đo bằng pass^5, seed variance, cost/success, và số trial có event `model_override` trong trace |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Run id / file report: `src/reports/benchmark.json`; trial lỗi `R-swarm-C-002-s55`, đối chứng `R-workflow-C-002-s55`
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: Đúng. Swarm → workflow: pass 0.986 → 1.000, pass^5 0.929 → 1.000, variance 0.000816 → 0, cost/success 49.57 → 27.86 VND, model call trung bình 3.0 → 0.0. Swarm có đúng 1 trial ghi `model_override` (C-002 seed 55, trả 20.000 VND thay vì `denied`), workflow không có trial nào. Test `tests/test_swarm_analysis.py::test_weakness_only_hits_t02_on_public_set` kiểm lại điều này
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`. Lỗi của swarm ở đây được cài sẵn (`REFERENCE_WEAKNESS`, chỉ bật khi seed chia hết cho 5), không phát sinh tự nhiên như trong paper. Corpus chỉ có 14 claim public

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
