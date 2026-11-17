"""B3 regression tests: hand labels, all quote inputs, safety and durability."""
from copy import deepcopy
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from bonus.swarm_verified import run_claim, verify_quote
from lab8.config_loader import repo_path
from lab8.db import connect, init_store, load_json, load_jsonl
from lab8.durability import InjectedCrash
from lab8.metrics import trial_pass
from lab8.schemas import Budget
from lab8.tools import compute_compensation, lookup_order
from lab8.trace import Trace
from tests.conftest import CLAIMS, WORLD

BONUS = repo_path("bonus")
CASES = load_jsonl(BONUS / "cases.jsonl")
BONUS_WORLD = load_json(BONUS / "world.json")


@pytest.mark.parametrize("seed", [11, 22, 33, 44, 55])
@pytest.mark.parametrize("claim", CLAIMS, ids=lambda c: c["claim_id"])
def test_verified_passes_public_with_distinct_identity(tmp_path, claim, seed):
    store = tmp_path / "case.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    result = run_claim(claim["claim_id"], seed=seed, store_path=str(store))
    conn = connect(store)
    try:
        ok, reason = trial_pass(result.as_dict(), claim["expected"], conn)
    finally:
        conn.close()
    assert ok, reason
    assert result.shape == "swarm_verified"
    assert result.run_id.startswith("R-swarm_verified-")


@pytest.mark.parametrize("seed", [11, 22, 33, 44, 55])
@pytest.mark.parametrize("claim", CASES, ids=lambda c: c["claim_id"])
def test_verified_matches_hand_labeled_adversarial_cases(tmp_path, claim, seed):
    store = tmp_path / "adversarial.sqlite"
    init_store(store, BONUS_WORLD, CASES).close()
    result = run_claim(claim["claim_id"], seed=seed, store_path=str(store))
    conn = connect(store)
    try:
        ok, reason = trial_pass(result.as_dict(), claim["expected"], conn)
    finally:
        conn.close()
    assert ok, reason
    trace = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    overrides = [e for e in trace["events"] if e["kind"] == "verifier_override"]
    assert len(overrides) <= 1


@pytest.mark.parametrize("field,value", [
    ("delay_days", 99), ("status", "cancelled"), ("damage_verified", True),
    ("shipping_fee_vnd", 999999), ("paid_vnd", 1), ("carrier", "OTHER"),
    ("order_id", "OTHER-ORDER"), ("damage_verified", "false"),
])
def test_verifier_repairs_each_order_field_once(public_db, field, value):
    conn = connect(public_db)
    try:
        trusted = lookup_order(conn, "O-107", "P-100")["order"]
        candidate = deepcopy(trusted)
        candidate[field] = value
        trace, budget = Trace("R-verifier-unit"), Budget()
        with patch("bonus.swarm_verified.compute_compensation", wraps=compute_compensation) as quote:
            result = verify_quote(conn, budget, trace, candidate, trusted, {"amount_vnd": 999999})
            assert quote.call_count == 1
        assert result["amount_vnd"] == 35000
        assert budget.tool_calls == 1
        assert trace.events[-1] == {"kind": "verifier_override", "payload": {
            "fields": [field], "repair_round": 1}}
        assert candidate[field] == value  # never silently mutate peer evidence
    finally:
        conn.close()


def test_unchanged_order_reuses_quote_without_repair(public_db):
    conn = connect(public_db)
    try:
        trusted = lookup_order(conn, "O-107", "P-100")["order"]
        quote = compute_compensation(conn, trusted)
        budget, trace = Budget(), Trace("R-verifier-matched")
        with patch("bonus.swarm_verified.compute_compensation") as recompute:
            assert verify_quote(conn, budget, trace, dict(trusted), trusted, quote) is quote
            recompute.assert_not_called()
        assert budget.tool_calls == 0
        assert trace.events[-1]["payload"]["matched"]
    finally:
        conn.close()


@pytest.mark.parametrize("point", ["before_effect", "after_effect_before_checkpoint", "after_checkpoint"])
def test_verified_crash_resume_and_replay_keep_one_effect(public_db, point):
    with pytest.raises(InjectedCrash):
        run_claim("C-001", seed=55, store_path=str(public_db), crash_at=point)
    first = run_claim("C-001", seed=55, store_path=str(public_db))
    replay = run_claim("C-001", seed=55, store_path=str(public_db))
    assert first.status == replay.status == "resolved"
    assert len(replay.refund_effects) == 1
    assert replay.refund_effects[0]["amount_vnd"] == 35000
    assert replay.committed_audit_count == 1


def test_understated_ticket_is_repaired_before_zero_quote_return(tmp_path):
    store = tmp_path / "understatement.sqlite"
    init_store(store, BONUS_WORLD, CASES).close()
    result = run_claim("B3-002", seed=55, store_path=str(store))
    assert result.status == "resolved"
    assert result.proposal_amount == 35000
    trace = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    assert sum(e["kind"] == "verifier_override" for e in trace["events"]) == 1
    assert result.model_calls == 3  # reference peer/parse/draft retained
