# Team

## Thông tin nhóm

- Tên nhóm:
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-TenNhom-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 |        |      |       |        |         |
|   2 |        |      |       |        |         |
|   3 | Thịnh | 2A202603907 | hungthinh05112002@gmail.com | [TrnhThnh](https://github.com/TrnhThnh) | Shape C: orchestrator, handoff chỉ đọc, trace an toàn và crash recovery |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| | | | |
| Thịnh | Shape C: orchestrator và investigator chỉ đọc | [c93c6c3](https://github.com/TrnhThnh/K5-L3B-DAY08-Bots-FromWorkflowsToAgents/commit/c93c6c3ca15248f7404fb5ac52fb71b68a5ea683) | `src/tests/test_thinh_orchestrator.py`: unknown claim, ticket injection/handoff, crash và resume tại ba điểm |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## MSSV_HoTen

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-

## 2A202603907_Thinh

### Phần việc phụ trách

- Shape C trong `src/lab8/shapes/orchestrator.py`: orchestrator giao việc bằng `make_handoff`; investigator chỉ dùng tool đọc; host kiểm approval và ghi refund.

### Đóng góp cụ thể

- Commit `c93c6c3` triển khai C và thêm năm test regression riêng; đã merge vào `main` qua PR #1.
- Dùng quote đầy đủ, không tự trừ refund lịch sử; ghi trace có allowlist, để `InjectedCrash` truyền ra và đóng connection trong `finally`.
- Codex hỗ trợ triển khai, kiểm thử và báo cáo; báo cáo cá nhân ghi rõ phạm vi hỗ trợ AI.

### Bằng chứng

- Báo cáo: [2A202603907_Thinh.md](report/team/2A202603907_Thinh.md).
- Tự kiểm student drop: `src/reports/hidden_selfcheck.json` (không có nhãn, không suy ra pass rate).
- Tên hiện dùng là Thịnh theo thông tin đã cung cấp; bổ sung họ tên đầy đủ và đổi tên báo cáo tương ứng trước khi nộp.
