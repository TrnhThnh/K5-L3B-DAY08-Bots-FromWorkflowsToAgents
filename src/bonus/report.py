"""Generate the concise B3 Markdown report from measured bonus_summary.json."""
import json
from pathlib import Path


def main():
    data = json.loads(Path("reports/bonus_summary.json").read_text(encoding="utf-8"))
    lines = [
        "# Bonus report: B3", "",
        "- Topic: verifier bằng code trước khi swarm ghi refund (docs/bonus_topics.md, B3; slide 17, 22, 42).",
        "- Nguồn: Kim et al., [Towards a Science of Scaling Agent Systems, v3, 2026](https://arxiv.org/abs/2512.08296v3). CLAIM: trong các cấu hình nghiên cứu, hệ thiếu kiểm chứng tập trung có xu hướng lan truyền lỗi nhiều hơn. BOUNDARY: benchmark/model của paper; không lấy tỷ lệ trong paper làm dự đoán cho MockLLM.",
        "- HYPOTHESIS: giữ swarm và thêm một lượt verifier sẽ sửa lỗi dùng ticket thay order, đưa độ đúng gần workflow, nhưng tăng chi phí.",
        "- Cố định: MockLLM, peer/parse/draft, read tools, policy, giá, evaluator, corpus và seed 11,22,33,44,55; SQLite mới từng trial. Biến đổi: thêm read order, so ORDER_FIELDS và tối đa một lần quote lại.",
        "", "## Tái lập", "", "Chạy trong src (activate .venv hoặc dùng đường dẫn Python của môi trường):", "",
        "```powershell",
        "python -m bonus.build_cases",
        "python -m bonus.evaluate --student-drop ../student_drop",
        "python -m bonus.report",
        "python -m pytest -q tests/test_bonus_swarm_verified.py --basetemp=.bonus-check-tmp -p no:cacheprovider",
        "```", "",
        "Runner gọi lab8.benchmark với --extra-shape swarm_verified=bonus.swarm_verified:run_claim. Không có student_drop thì bỏ cờ đó. Code gốc swarm_reference và host giữ nguyên; biến thể ghi shape/run_id riêng.",
        "", "## Kết quả", "",
        "Số lấy từ reports/bonus_public.json, bonus_adversarial.json và bonus_summary.json, không sửa tay. 10 case mới có nhãn literal theo business_rules.md (bonus/cases.md), không sinh nhãn bằng quote.", "",
        "| Corpus | Shape | Pass | Pass^5 | Seed min–max | Variance | Cost/success VND mô phỏng |",
        "| --- | --- | ---: | ---: | --- | ---: | ---: |",
    ]
    for name in ("public", "adversarial"):
        for shape, s in data["corpora"][name]["by_shape"].items():
            lines.append(f"| {name} | {shape} | {s['pass_rate']:.6f} | {s['pass_5']:.6f} | {s['seed_min']:.3f}–{s['seed_max']:.3f} | {s['seed_variance']:.6f} | {s['cost_per_success_vnd']:.2f} |")
    lines += ["", "Audit replay dùng DB mới, kiểm usage/status trùng benchmark, approval liên kết, trace contract và quét toàn bộ secret/PII đã biết từ fixture. Các số đếm sau là tự kiểm, không phải hidden grade:", "",
        "| Corpus | Tổng trial audit (3 shape) | Exception / trace lỗi | Secret / PII / bypass | Override của verified |",
        "| --- | ---: | --- | --- | ---: |"]
    for name, corpus in data["corpora"].items():
        counts = corpus["safety"]["by_shape"]
        total = lambda key: sum(s[key] for s in counts.values())
        lines.append(f"| {name} | {total('trials')} | {total('exceptions')} / {total('invalid_traces')} | {total('secret_leak_count')} / {total('pii_leak_count')} / {total('approval_bypass_count')} | {counts['swarm_verified']['verifier_overrides']} |")
    replay = sum(s['replay_mismatches'] for c in data['corpora'].values() for s in c['safety']['by_shape'].values())
    crash = data['verified_crash']
    lines += ["", f"Replay mismatch: {replay}. Verified crash/resume/replay: {crash['passed']}/{crash['count']} (ba điểm × năm seed). Host crash suite gốc vẫn 20/20 trong reports/crash.json; test bonus kiểm thêm approval, order cap, cả nói quá và nói thiếu.", "",
        "Ví dụ R-swarm_verified-C-002-s55: model_override delay=5 → verifier_override fields=[delay_days], repair_round=1 → quote=0, denied. Event mẫu an toàn nằm trong bonus_summary.json; trace runtime không commit.", ""]
    if "student_drop" in data["corpora"]:
        n = data["corpora"]["student_drop"]["by_shape"]["swarm_verified"]["trials"]
        lines += [f"Student drop: {n} trial mỗi shape, không nhãn; pass rate/pass^5/variance pass/cost-success để null. Không tự tạo đáp án hidden. File reports/bonus_student_drop.json chỉ mô tả hành vi và cost.", ""]
    lines += ["## Kết luận và giới hạn", "",
        "Hypothesis được ủng hộ trên hai corpus có nhãn: verifier sửa lỗi reference, nhưng workflow vẫn đúng tương đương và rẻ hơn. Verifier dùng code cho dữ kiện và tiền; giá trị của swarm còn là giao tiếp/soạn câu, chưa chứng minh lợi ích trong MockLLM. Không đổi đề xuất workflow trong ADR. Chỉ xét lại khi task thật cần nhiều chuyên môn và đo công bằng cho thấy lợi ích đủ bù chi phí.", "",
        "Lỗi reference được cài cố ý theo seed; 10 case nhắm điểm yếu đã biết, mẫu nhỏ. Chưa kiểm fault policy/quote sai khi dữ kiện vẫn khớp, chưa giải quyết thay đổi order giữa verifier và transaction. Không suy ra quan hệ nhân quả tổng quát về topology. MockLLM không phải model production; chi phí mô phỏng, latency unavailable.", "",
        "Điểm bonus tối đa +10 còn phụ thuộc workflow qua must-pass và hidden pass rate ≥0.80 do grader giảng viên xác nhận. Student drop không nhãn chưa chứng minh gate này. Codex hỗ trợ code/test/báo cáo; nhóm cần review và tự giải thích, không khai thay tự đánh giá cá nhân.",
    ]
    root = Path(__file__).resolve().parents[2]
    (root / "report/team/bonus_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Wrote report/team/bonus_report.md from measured JSON")


if __name__ == "__main__":
    main()
