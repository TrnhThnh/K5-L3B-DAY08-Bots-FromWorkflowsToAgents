"""Shape C — orchestrator plus read-only investigators. Student work.

1. Build a handoff with `lab8.handoff.make_handoff`. Allowed tools are read-only.
   Never put parent_secret, raw headers, or the full claim row into facts.
2. `lab8.runtime.run_readonly_investigators` runs those tools.
3. The orchestrator quotes from the investigator's order view and calls
   `durability.issue_refund`. Investigators have no write registry.
   Pass the full quote; the host subtracts earlier refunds on the same order.
   `lookup_refund_history` is a read-only tool you may hand to an investigator.
4. Trace the sanitized handoff, not the parent context.

An LLM summary of the parent context is not a sanitizer. Use the allowlist.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

from lab8.db import connect
from lab8.durability import issue_refund
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import get_claim_view, lookup_order, compute_compensation, tool_cost
from lab8.trace import Trace
from lab8.handoff import make_handoff
from lab8.runtime import run_readonly_investigators
from lab8.mock_llm import complete


def run_claim(claim_id: str, *, seed: int, store_path: str,
              crash_at: str | None = None) -> RunResult:
    conn = connect(store_path)
    budget = Budget()
    trace = Trace(make_run_id("orchestrator", claim_id, seed))

    def done(status, proposal=0, reason=None):
        trace.add("decision", {"status": status, "proposal_amount": proposal,
                               "reason": reason})
        return finish(conn, shape="orchestrator", claim_id=claim_id, seed=seed,
                      status=status, proposal_amount=proposal, budget=budget,
                      trace=trace, error_reason=reason)

    try:
        budget.add_tool(tool_cost())
        claim = get_claim_view(conn, claim_id)
        # Ticket text is untrusted and is never copied into traces or handoffs.
        trace.add("claim", {"found": claim["found"]})
        if not claim["found"]:
            return done("failed", reason="unknown_claim")
        if not claim.get("order_id"):
            return done("needs_info", reason="missing_order_id")
        complete(budget, seed=seed, purpose="plan", prompt="Investigate owner order and current policy")
        handoff = make_handoff(
            request_id=trace.run_id, claim_id=claim_id,
            task="check_applicable_policy", facts={},
            allowed_tools=["lookup_order", "lookup_policy", "lookup_refund_history",
                           "compute_compensation"])
        trace.add("handoff", handoff)
        investigated = run_readonly_investigators(
            conn, budget, handoff, principal_id=claim["principal_id"])
        order_view = investigated["tools"].get("lookup_order", {})
        trace.add("investigator", {"lookup_order": order_view,
                  "refund_history": investigated["tools"].get("lookup_refund_history")})
        if not order_view.get("visible"):
            return done("escalated", reason=order_view.get("reason"))
        quote = investigated["tools"]["compute_compensation"]
        proposal = int(quote["amount_vnd"])
        trace.add("quote", quote)
        if proposal <= 0:
            return done("denied", reason=quote.get("reason"))
        # Full entitlement goes to the host; it alone applies approval and order cap.
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
        trace.add("refund", {"ok": outcome["ok"], "reason": outcome["reason"]})
        if not outcome["ok"]:
            return done("failed" if outcome["conflict"] else "denied",
                        proposal, outcome["reason"])
        return done("resolved", proposal)
    finally:
        # Flush safe events even on InjectedCrash, and let the crash propagate.
        try:
            trace.write()
        finally:
            conn.close()
