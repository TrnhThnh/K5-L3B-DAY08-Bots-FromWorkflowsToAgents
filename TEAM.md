# Team

## Thông tin nhóm

- Tên nhóm:
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY08-Bots-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:

## Thành viên

| STT | Họ tên           | MSSV        | Email                       | GitHub        | Vai trò                                                                    |
| --: | ---------------- | ----------- | --------------------------- | ------------- | -------------------------------------------------------------------------- |
|   1 | Dương Minh Chiến | 2A202603921 | duongchien1472005@gmail.com | duongchien147 | D swarm (baseline, test swarm), benchmark, crash suite, ADR, research card |
|   3 Trần Đức Trung | 2A202603938 | kientrungtd135@gmail.com | kientrungtd135 | Shape A — Workflow, crash recovery, testing |
|   2 |                  |             |                             |               |                                                                            |
|   2 | Đỗ Anh Thư       | 2A202603815 | adugarux4@gmail.com         | DoAnhThu832004| B single (Single agent ReAct, crash recovery CP3, test single)             |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người            | Vai                         | Commit           | Test đã thêm hoặc sửa                      |
| ---------------- | --------------------------- | ---------------- | ------------------------------------------ |
| Dương Minh Chiến | D swarm, benchmark, báo cáo | ed6ba8c, be417ce | src/tests/test_swarm_analysis.py (14 test) |
| Trần Đức Trung | Shape A — Workflow, testing | b885626, 15b8dd8, 838ece2, c5e3942 | src/tests/test_workflow_approval_guard.py (10 tests) |
| Đỗ Anh Thư       | B single                    | 8f8368f, 523138f | src/tests/test_single_agent.py (8 test)    |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603921_DuongMinhChien

### Phần việc phụ trách

- Shape D swarm baseline, test swarm, benchmark 4 shape, crash suite, ADR, research card.

### Đóng góp cụ thể

- Commit ed6ba8c, be417ce: src/tests/test_swarm_analysis.py (14 test), benchmark.json, điền ADR và research card.

### Bằng chứng

- src/tests/test_swarm_analysis.py, src/reports/benchmark.json, report/team/2A202603921_DuongMinhChien.md.

## 2A202603815_DoAnhThu

### Phần việc phụ trách

- Shape B: Single Agent ReAct (`src/lab8/shapes/single.py`), xử lý crash recovery CP3, viết unit test kiểm thử.

### Đóng góp cụ thể

- Commit 8f8368f: Cài đặt hoàn chỉnh Shape B `single.py`.
- Thêm file test `src/tests/test_single_agent.py` (8 unit tests passed).

### Bằng chứng

- `src/tests/test_single_agent.py` (8 passed), ma trận test `tests/test_public_matrix.py` (62 passed cho shape single), báo cáo cá nhân `report/team/2A202603815_DoAnhThu.md`.

### Bằng chứng

-
