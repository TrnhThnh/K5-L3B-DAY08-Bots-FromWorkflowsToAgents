# Báo cáo cá nhân — Trịnh Hưng Thịnh

## 1. Thông tin thành viên

- Họ tên: Trịnh Hưng Thịnh.
- MSSV: 2A202603907
- Email: hungthinh05112002@gmail.com
- GitHub: [TrnhThnh](https://github.com/TrnhThnh)
- Phần việc: Shape C — orchestrator và investigator chỉ đọc.
- Báo cáo hiện dùng tên `2A202603907_TrinhHungThinh.md` theo tên đã cung cấp; đổi phần HoTen thành họ tên đầy đủ không dấu khi có thông tin.

## 2. Phần việc phụ trách

Triển khai `src/lab8/shapes/orchestrator.py` với chữ ký run_claim của đề. Orchestrator đọc claim bằng get_claim_view; thiếu order_id trả needs_info, claim không tồn tại trả failed. Sau đó tạo handoff.v1 bằng make_handoff với facts rỗng, nhiệm vụ cố định và danh sách tool chỉ đọc.

Investigator đọc order theo principal, policy hiện hành, lịch sử refund và compute_compensation. Không nhìn thấy đơn thì orchestrator trả escalated. Quote bằng 0 thì denied; quote dương chuyển đầy đủ vào durability.issue_refund. Host quyết định approval, trần theo đơn và ghi ledger; investigator không có quyền ghi refund.

## 3. Đóng góp cụ thể

Commit [c93c6c3](https://github.com/TrnhThnh/K5-L3B-DAY08-Bots-FromWorkflowsToAgents/commit/c93c6c3ca15248f7404fb5ac52fb71b68a5ea683), tác giả Thịnh, chứa code C, test riêng và bản nháp báo cáo; đã merge vào main qua PR #1. Các thay đổi được thực hiện với hỗ trợ Codex, không khai là code tự viết không dùng AI.

Các quyết định kỹ thuật:

- Dùng make_handoff và allowlist bằng code; không dùng tóm tắt model để che secret.
- Không đưa ticket, parent_secret, raw headers hay parent context vào trace/handoff.
- Truyền quote đầy đủ cho host, không tự trừ tiền lịch sử để tránh trừ hai lần.
- Dùng finish để lấy refund_effects và committed_audit_count từ ledger thực.
- Truyền crash_at xuống host; không bắt InjectedCrash. finally ghi trace và đóng SQLite connection.
- Bước plan dùng MockLLM có budget; danh sách nhiệm vụ/tool được giới hạn bằng code, không phải model thật tự lập kế hoạch.

Test trong `src/tests/test_thinh_orchestrator.py`:

- test_unknown_claim_has_fresh_safe_trace: claim không tồn tại vẫn có trace đúng run_id và không refund.
- test_ticket_injection_does_not_change_order_or_leak: ticket chứa lệnh giả, số ngày sai, canary và số điện thoại không thay đổi quyết định từ order hoặc lọt vào trace; handoff không cấp issue_refund.
- test_each_shape_crashes_and_resumes_once: ba case before_effect, after_effect_before_checkpoint và after_checkpoint; resume còn đúng một refund và một audit committed.

## 4. Bằng chứng

### Public và regression

Các lệnh chạy trong src bằng Python của .venv:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp=.thinh-update-host-tmp -p no:cacheprovider
.\.venv\Scripts\python.exe -m pytest -q -m student -o addopts= -k orchestrator --basetemp=.thinh-update-student-tmp -p no:cacheprovider
```

Bộ host và test hiện tại: 73 passed, 248 deselected. Student shape C: 62 passed, 259 deselected. Test riêng C có năm trường hợp (ba trường hợp crash). basetemp trong workspace và no:cacheprovider xử lý quyền temp/cache trên Windows, không sửa thước đo.

### Tự kiểm student drop

Bộ dữ liệu được đặt ở student_drop/ tại root repo, do đó chạy từ src bằng đường dẫn ../student_drop/; không cần di chuyển dữ liệu.

```powershell
.\.venv\Scripts\python.exe -m lab8.benchmark --shapes workflow,single,orchestrator --cases ../student_drop/hidden_claims.jsonl --world ../student_drop/hidden_world_state.json --seeds 11,22,33,44,55 --out reports/hidden_selfcheck.json
```

Bằng chứng: `src/reports/hidden_selfcheck.json` được lab8.benchmark sinh, không sửa tay. Chạy trên main nền 166907f; trong lần tự kiểm này chỉ tài liệu được cập nhật, code shape giữ nguyên.

| Shape | Claim × seed | Trial | Exception/status error | Lỗi trace hoặc leak_suspect |
| --- | --- | ---: | ---: | ---: |
| workflow | 40 × 5 | 200 | 0 | 0 |
| single | 40 × 5 | 200 | 0 | 0 |
| orchestrator | 40 × 5 | 200 | 0 | 0 |

Riêng C: resolved 90, denied 95, needs_info 5, escalated 10; 200 reason đều unlabeled. Không có nhãn nên pass rate, pass^5, variance pass và cost/success để null; không suy ra đã đạt hidden ≥ 0.75. Không có leak_suspect chỉ là kết quả scanner tự kiểm, không thay thế grader chính thức hoặc chứng minh mọi dạng PII đều sạch.

Report ghi run_id cho từng trial; với biến thể dữ liệu hidden, xem các hàng shape=orchestrator trong chính JSON thay vì tự đặt run id. Không commit student_drop, trace hoặc SQLite.

## 5. Công cụ AI đã dùng

Codex hỗ trợ đọc đề, giải thích kiến trúc, triển khai C, tạo test, chạy CLI, soạn tài liệu và thao tác Git theo yêu cầu của Thịnh. Kết quả nêu trên lấy từ lệnh chạy thực tế trong phiên, không phải số liệu tự ước lượng. Việc chạy được trợ lý thực hiện; không khai thay rằng cá nhân đã tự chạy hoặc tự giải thích thành thạo. Thịnh cần đọc code và chạy lại các lệnh để xác nhận trước khi nộp.

## 6. Tự đánh giá

Về sản phẩm: C đã có luồng đầy đủ, handoff giới hạn, tiền do code/host quyết, test crash và tự kiểm student drop không báo lỗi. Giới hạn: MockLLM không đại diện model sản xuất, investigator trong cùng process, latency unavailable; hidden không có nhãn nên chưa có kết luận độ đúng.

Phần tự đánh giá năng lực và trải nghiệm cá nhân cần Thịnh tự xác nhận, bổ sung sau review; trợ lý không tự khai thay. Các điểm cần giải thích được: quyền tool đọc của investigator, quote đầy đủ và order cap, lý do ledger chống ghi trùng, dữ liệu bị loại khỏi trace.
