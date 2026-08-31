#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any, Mapping
from urllib.parse import urljoin, urlparse
from urllib.request import Request, build_opener
from urllib.error import HTTPError, URLError

PACKAGE_SCHEMA = "stegverse.sv-dn1.repository-persistence-package/v1"
OBSERVATION_SCHEMA = "stegverse.sv-dn1.publication-observation/v1"
EXPECTED_FILES = (
    "first-round-analysis.json",
    "production-pipeline-observation.json",
    "result-receipt.json",
    "report.md",
    "index.html",
)
DEFAULT_PUBLIC_BASE = "https://stegverse-org.github.io/stegverse-demo-suite/sv-dn1/"
ALLOWED_HOSTS = {"stegverse-org.github.io"}


class PublicationObservationError(RuntimeError):
    pass


def stable_bytes(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(dict(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PublicationObservationError(f"expected JSON object: {path}")
    return value


def validate_package(package: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    if package.get("schema") != PACKAGE_SCHEMA:
        raise PublicationObservationError("wrong persistence package schema")
    if package.get("state") != "READY_FOR_ADMITTED_REPOSITORY_MUTATION":
        raise PublicationObservationError("persistence package is not mutation-ready")
    if package.get("target_repository") != "StegVerse-org/stegverse-demo-suite":
        raise PublicationObservationError("wrong target repository")
    if package.get("target_ref") != "main" or package.get("target_root") != "public/sv-dn1":
        raise PublicationObservationError("wrong target ref/root")
    if package.get("publication_state") not in {"PUBLIC_OBSERVED", "PUBLIC_WITH_LIMITATIONS"}:
        raise PublicationObservationError("publication state is not public-observable")
    if package.get("observation_class") != "LIVE":
        raise PublicationObservationError("package observation class is not LIVE")
    for field, expected in {
        "exact_bytes_preserved": True,
        "semantic_rewrite_performed": False,
        "network_fetch_performed": False,
        "credential_used": False,
        "repository_writeback_performed": False,
        "deployment_performed": False,
        "authority_effect": "NONE_PERSISTENCE_PACKAGE_ONLY",
    }.items():
        if package.get(field) != expected:
            raise PublicationObservationError(f"package field mismatch: {field}")

    claimed = package.get("package_sha256")
    body = dict(package)
    body.pop("package_sha256", None)
    if not isinstance(claimed, str) or claimed != sha256_bytes(stable_bytes(body)):
        raise PublicationObservationError("package_sha256 mismatch")

    rows = package.get("files")
    if not isinstance(rows, list) or len(rows) != len(EXPECTED_FILES):
        raise PublicationObservationError("package must contain exactly five public files")

    by_name: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            raise PublicationObservationError("invalid package file entry")
        path = str(row.get("path") or "")
        pure = PurePosixPath(path)
        if pure.parts[:2] != ("public", "sv-dn1") or len(pure.parts) != 3:
            raise PublicationObservationError(f"unexpected package target path: {path}")
        name = pure.name
        if name not in EXPECTED_FILES or name in by_name:
            raise PublicationObservationError(f"unexpected or duplicate package file: {name}")
        encoded = row.get("content_base64")
        if not isinstance(encoded, str):
            raise PublicationObservationError(f"missing base64 content: {name}")
        try:
            raw = base64.b64decode(encoded.encode("ascii"), validate=True)
        except Exception as exc:
            raise PublicationObservationError(f"invalid base64 content: {name}") from exc
        digest = sha256_bytes(raw)
        if row.get("sha256") != digest:
            raise PublicationObservationError(f"package file hash mismatch: {name}")
        if row.get("size") != len(raw):
            raise PublicationObservationError(f"package file size mismatch: {name}")
        by_name[name] = {"bytes": raw, "sha256": digest, "size": len(raw), "path": path}

    if set(by_name) != set(EXPECTED_FILES):
        raise PublicationObservationError("package public file set mismatch")
    return by_name


def _validate_base_url(base_url: str) -> str:
    parsed = urlparse(base_url)
    if parsed.scheme != "https":
        raise PublicationObservationError("public base URL must use HTTPS")
    if parsed.hostname not in ALLOWED_HOSTS:
        raise PublicationObservationError("public base hostname is not admitted")
    path = parsed.path if parsed.path.endswith("/") else parsed.path + "/"
    if path != "/stegverse-demo-suite/sv-dn1/":
        raise PublicationObservationError("public base path mismatch")
    if parsed.query or parsed.fragment or parsed.username or parsed.password or parsed.port:
        raise PublicationObservationError("public base URL contains unsupported components")
    return parsed._replace(path=path).geturl()


def observe_publication(
    package: Mapping[str, Any],
    *,
    base_url: str = DEFAULT_PUBLIC_BASE,
    opener: Any | None = None,
) -> dict[str, Any]:
    expected = validate_package(package)
    base = _validate_base_url(base_url)
    client = opener or build_opener()

    observed: dict[str, dict[str, Any]] = {}
    for name in EXPECTED_FILES:
        url = urljoin(base, name)
        request = Request(
            url,
            method="GET",
            headers={
                "Accept": "*/*",
                "User-Agent": "stegverse-sv-dn1-publication-observer",
            },
        )
        try:
            response = client.open(request, timeout=30)
        except (HTTPError, URLError, OSError) as exc:
            raise PublicationObservationError(f"public fetch failed: {name}: {exc}") from exc
        with response:
            status = int(getattr(response, "status", response.getcode()))
            final_url = response.geturl()
            if status != 200:
                raise PublicationObservationError(f"public status is not 200: {name}: {status}")
            final = urlparse(final_url)
            if final.scheme != "https" or final.hostname not in ALLOWED_HOSTS:
                raise PublicationObservationError(f"public redirect escaped admitted host: {name}")
            if final.path != urlparse(url).path:
                raise PublicationObservationError(f"public redirect changed artifact path: {name}")
            raw = response.read()

        digest = sha256_bytes(raw)
        if digest != expected[name]["sha256"] or raw != expected[name]["bytes"]:
            raise PublicationObservationError(f"public artifact bytes do not match governed package: {name}")
        observed[name] = {
            "url": final_url,
            "status": 200,
            "sha256": digest,
            "size": len(raw),
            "exact_bytes_match": True,
        }

    return {
        "schema": OBSERVATION_SCHEMA,
        "state": "COMPLETE",
        "transition_id": "SV_DN1_AUTHENTIC_PUBLICATION_OBSERVED",
        "target_repository": package["target_repository"],
        "target_ref": package["target_ref"],
        "target_root": package["target_root"],
        "exchange_id": package.get("exchange_id"),
        "manifest_receipt_id": package.get("manifest_receipt_id"),
        "publication_state": package["publication_state"],
        "observation_class": "LIVE_PUBLIC_HTTPS_EXACT_BYTE_OBSERVATION",
        "public_base_url": base,
        "artifacts": observed,
        "exact_bytes_preserved": True,
        "all_public_artifacts_observed": True,
        "credential_used": False,
        "authorization_header_sent": False,
        "repository_writeback_performed": False,
        "deployment_performed": False,
        "governance_executed": False,
        "sdk_execution_performed": False,
        "authority_effect": "NONE_PUBLICATION_OBSERVATION_ONLY",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify exact governed SV-DN-1 bytes on the public HTTPS surface.")
    parser.add_argument("--persistence-package", required=True, type=Path)
    parser.add_argument("--public-base-url", default=DEFAULT_PUBLIC_BASE)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    result = observe_publication(load_json(args.persistence_package), base_url=args.public_base_url)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(payload, encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
