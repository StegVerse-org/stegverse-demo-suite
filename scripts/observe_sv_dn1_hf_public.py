#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable

MAX_BYTES = 5 * 1024 * 1024


def raw_digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def canonical_digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def allowed_hf_url(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https":
        return False
    host = (parsed.hostname or "").lower()
    return host == "huggingface.co" or host.endswith(".huggingface.co")


def capture_public_json(
    url: str,
    observed_at: str,
    *,
    timeout: float = 20.0,
    opener: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    if not allowed_hf_url(url):
        raise ValueError("only HTTPS huggingface.co public sources are admitted")
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "StegVerse-SV-DN-1/1.0 public-evidence-observer",
            "Accept": "application/json",
        },
        method="GET",
    )
    open_fn = opener or urllib.request.urlopen
    with open_fn(request, timeout=timeout) as response:
        status = int(getattr(response, "status", 200))
        final_url = response.geturl()
        if not allowed_hf_url(final_url):
            raise ValueError("redirect left admitted Hugging Face boundary")
        content_type = response.headers.get("Content-Type", "")
        raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("response exceeds source-capture size limit")
        if status < 200 or status >= 300:
            raise ValueError(f"unexpected HTTP status: {status}")
        if "json" not in content_type.lower():
            raise ValueError("public source did not return JSON")
    parsed = json.loads(raw.decode("utf-8"))
    raw_sha = raw_digest(raw)
    basis = {
        "source_system": "huggingface",
        "requested_url": url,
        "final_url": final_url,
        "observed_at": observed_at,
        "http_status": status,
        "content_type": content_type,
        "raw_sha256": raw_sha,
        "raw_size": len(raw),
    }
    return {
        "schema_version": "stegverse.sv-dn1.source-capture/v1",
        "capture_id": canonical_digest(basis),
        "source_system": "huggingface",
        "requested_url": url,
        "final_url": final_url,
        "observed_at": observed_at,
        "http_status": status,
        "content_type": content_type,
        "raw_sha256": raw_sha,
        "raw_size": len(raw),
        "parsed_json": parsed,
        "claims": {
            "public_source_only": True,
            "credential_used": False,
            "hugging_face_endorsement_claimed": False,
            "live_interlock_traversal_claimed": False,
        },
        "authority_effect": "NONE",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--observed-at", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--timeout", type=float, default=20.0)
    args = ap.parse_args()
    capture = capture_public_json(args.url, args.observed_at, timeout=args.timeout)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(capture, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "state": "SV_DN1_PUBLIC_SOURCE_CAPTURED",
        "capture_id": capture["capture_id"],
        "raw_sha256": capture["raw_sha256"],
        "credential_used": False,
        "authority_effect": "NONE",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
