"""Phân tích shape D (swarm tham chiếu): điểm yếu theo seed, chi phí, secret, crash.

Bổ sung cho tests/test_swarm_reference.py và ma trận student. Chạy trong cổng host
(không có marker `student`). Không sửa swarm_reference.py: các test này chỉ đo nó,
làm baseline để so với workflow, single, orchestrator ở CP5.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lab8.db import connect, init_store
from lab8.durability import InjectedCrash
from lab8.metrics import artifact_blob, trial_pass
from lab8.shapes.swarm_reference import run_claim
from tests.conftest import BY_ID, CLAIMS, WORLD

PUBLIC_SEEDS = (11, 22, 33, 44, 55)
SINGLE_RUN_CLAIMS = [f"C-{i:03d}" for i in range(1, 11)] + ["C-013", "C-014"]
CRASH_POINTS = ("before_effect", "after_effect_before_checkpoint", "after_checkpoint")


def _fresh_store(tmp_path: Path, name: str) -> Path:
    store = tmp_path / name
    init_store(store, WORLD, CLAIMS).close()
    return store


def _trace_kinds(result) -> list[str]:
    body = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    return [event["kind"] for event in body["events"]]


def _grade(store: Path, result, claim_id: str) -> tuple[bool, str]:
    conn = connect(store)
    try:
        return trial_pass(result.as_dict(), BY_ID[claim_id]["expected"], conn)
    finally:
        conn.close()


def test_weakness_fires_only_on_seed_divisible_by_5(tmp_path):
    """T02 chỉ fail ở seed 55. Trace ghi `model_override` đúng ở trial đó, và chỉ ở trial đó."""
    outcomes = {}
    for seed in PUBLIC_SEEDS:
        store = _fresh_store(tmp_path, f"c002-{seed}.sqlite")
        result = run_claim("C-002", seed=seed, store_path=str(store))
        passed, _ = _grade(store, result, "C-002")
        outcomes[seed] = (passed, result.status, result.proposal_amount, "model_override" in _trace_kinds(result))
    assert outcomes[55] == (False, "resolved", 20000, True)
    for seed in (11, 22, 33, 44):
        assert outcomes[seed] == (True, "denied", 0, False)


def test_weakness_only_hits_t02_on_public_set(tmp_path):
    """Trên 12 claim chạy một lần × 5 seed, override chỉ xảy ra ở (C-002, 55): ticket và DB lệch nhau."""
    overrides = []
    misses = []
    for claim_id in SINGLE_RUN_CLAIMS:
        for seed in PUBLIC_SEEDS:
            store = _fresh_store(tmp_path, f"{claim_id}-{seed}.sqlite")
            result = run_claim(claim_id, seed=seed, store_path=str(store))
            if "model_override" in _trace_kinds(result):
                overrides.append((claim_id, seed))
            if not _grade(store, result, claim_id)[0]:
                misses.append((claim_id, seed))
    assert overrides == [("C-002", 55)]
    assert misses == [("C-002", 55)]


@pytest.mark.parametrize("claim_id", ["C-001", "C-002", "C-008"])
def test_swarm_is_deterministic_per_seed(tmp_path, claim_id):
    """Cùng claim, cùng seed, DB mới: kết quả và cost y hệt. Variance của swarm đến từ seed, không phải nhiễu."""
    runs = []
    for attempt in range(2):
        store = _fresh_store(tmp_path, f"{claim_id}-det-{attempt}.sqlite")
        r = run_claim(claim_id, seed=55, store_path=str(store))
        runs.append((r.status, r.proposal_amount, r.model_calls, r.tool_calls, r.cost_estimate))
    assert runs[0] == runs[1]


def test_swarm_pays_peer_overhead_on_every_claim_with_order(tmp_path):
    """Swarm gọi model 3 lần (peer, parse, draft) kể cả claim đơn giản. Đây là phần cost để so với workflow."""
    for claim_id in SINGLE_RUN_CLAIMS:
        store = _fresh_store(tmp_path, f"{claim_id}-cost.sqlite")
        result = run_claim(claim_id, seed=11, store_path=str(store))
        assert result.model_calls == 3, (claim_id, result.model_calls)
        assert result.cost_estimate > 0


@pytest.mark.parametrize("seed", PUBLIC_SEEDS)
def test_swarm_never_leaks_parent_secret(tmp_path, seed):
    """Kết quả và trace không chứa secret hay header của parent, kể cả ở seed 55 khi swarm trả sai."""
    for claim_id in SINGLE_RUN_CLAIMS:
        store = _fresh_store(tmp_path, f"{claim_id}-{seed}-leak.sqlite")
        result = run_claim(claim_id, seed=seed, store_path=str(store))
        blob = artifact_blob(result.as_dict())
        assert "CANARY_SECRET" not in blob, (claim_id, seed)
        assert "Bearer" not in blob, (claim_id, seed)


@pytest.mark.parametrize("point", CRASH_POINTS)
def test_swarm_crash_then_resume_keeps_one_refund(tmp_path, point):
    """Crash suite chỉ thử swarm ở after_effect_before_checkpoint. Ở đây thử cả 3 điểm crash."""
    store = _fresh_store(tmp_path, f"crash-{point}.sqlite")
    with pytest.raises(InjectedCrash):
        run_claim("C-012", seed=11, store_path=str(store), crash_at=point)
    result = run_claim("C-012", seed=11, store_path=str(store))
    passed, reason = _grade(store, result, "C-012")
    assert passed, reason
    conn = connect(store)
    try:
        count = conn.execute("SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-012'").fetchone()["n"]
    finally:
        conn.close()
    assert count == 1
