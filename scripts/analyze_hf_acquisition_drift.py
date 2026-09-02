#!/usr/bin/env python3
"""Deterministic longitudinal classifier for HF acquisition-drift observations."""

ALLOWED_EVIDENCE = {
    "DIRECT_PUBLIC_OBSERVATION",
    "RECEIPT_BOUND_SV_DN1_OBSERVATION",
    "OFFICIAL_ANNOUNCEMENT",
    "THIRD_PARTY_REPORT",
    "INFERENCE",
    "UNKNOWN",
}
DIRECT = {
    "DIRECT_PUBLIC_OBSERVATION",
    "RECEIPT_BOUND_SV_DN1_OBSERVATION",
    "OFFICIAL_ANNOUNCEMENT",
}
ALLOWED_DIRECTION = {"NEGATIVE", "POSITIVE", "NEUTRAL", "UNKNOWN"}


def classify(observations):
    if not isinstance(observations, list):
        raise ValueError("observations must be a list")
    scored = []
    for row in observations:
        if not isinstance(row, dict):
            raise ValueError("observation must be an object")
        evidence_class = row.get("evidence_class")
        direction = row.get("direction")
        if evidence_class not in ALLOWED_EVIDENCE:
            raise ValueError("invalid evidence_class")
        if direction not in ALLOWED_DIRECTION:
            raise ValueError("invalid direction")
        if evidence_class in {"INFERENCE", "UNKNOWN"}:
            continue
        confidence = row.get("confidence", 0)
        if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        weight = float(confidence) * (1.0 if evidence_class in DIRECT else 0.5)
        score = {"NEGATIVE": -1, "POSITIVE": 1, "NEUTRAL": 0, "UNKNOWN": 0}[direction] * weight
        scored.append((score, row))

    if not scored:
        state = "INSUFFICIENT_EVIDENCE"
        net = 0.0
    else:
        net = sum(x[0] for x in scored)
        has_neg = any(x[0] < 0 for x in scored)
        has_pos = any(x[0] > 0 for x in scored)
        if has_neg and has_pos:
            state = "MIXED_DRIFT"
        elif net < -0.5:
            state = "COMMUNITY_NEGATIVE_DRIFT"
        elif net > 0.5:
            state = "COMMUNITY_POSITIVE_DRIFT"
        else:
            state = "NO_MATERIAL_DRIFT_OBSERVED"

    return {
        "schema": "stegverse.hf-acquisition-drift-result/v1",
        "state": state,
        "net_direction_score": round(net, 6),
        "admissible_observation_count": len(scored),
        "inference_promoted_to_observation": False,
        "authority_effect": "NONE",
    }
