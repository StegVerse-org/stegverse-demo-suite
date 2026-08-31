from __future__ import annotations

import base64
import hashlib
import io
import json
from pathlib import Path
import unittest

from scripts import verify_sv_dn1_public_publication as observer


def package_fixture() -> dict:
    rows = []
    for name in observer.EXPECTED_FILES:
        raw = ("authentic-" + name + "\n").encode()
        rows.append({
            "path": "public/sv-dn1/" + name,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "size": len(raw),
            "content_base64": base64.b64encode(raw).decode("ascii"),
        })
    body = {
        "schema": observer.PACKAGE_SCHEMA,
        "state": "READY_FOR_ADMITTED_REPOSITORY_MUTATION",
        "target_repository": "StegVerse-org/stegverse-demo-suite",
        "target_ref": "main",
        "target_root": "public/sv-dn1",
        "exchange_id": "sha256:" + "a" * 64,
        "manifest_receipt_id": "MR-EXAMPLE",
        "publication_state": "PUBLIC_OBSERVED",
        "observation_class": "LIVE",
        "files": rows,
        "exact_bytes_preserved": True,
        "semantic_rewrite_performed": False,
        "network_fetch_performed": False,
        "credential_used": False,
        "repository_writeback_performed": False,
        "deployment_performed": False,
        "authority_effect": "NONE_PERSISTENCE_PACKAGE_ONLY",
    }
    value = dict(body)
    value["package_sha256"] = observer.sha256_bytes(observer.stable_bytes(body))
    return value


class FakeResponse(io.BytesIO):
    def __init__(self, raw: bytes, url: str, status: int = 200):
        super().__init__(raw)
        self.status = status
        self._url = url

    def getcode(self):
        return self.status

    def geturl(self):
        return self._url

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class FakeOpener:
    def __init__(self, package: dict, *, mutate: str | None = None, redirect_host: str | None = None):
        self.rows = {Path(row["path"]).name: row for row in package["files"]}
        self.mutate = mutate
        self.redirect_host = redirect_host

    def open(self, request, timeout=30):
        name = Path(request.full_url).name
        row = self.rows[name]
        raw = base64.b64decode(row["content_base64"])
        if name == self.mutate:
            raw += b"tampered"
        url = request.full_url
        if self.redirect_host:
            url = url.replace("stegverse-org.github.io", self.redirect_host)
        return FakeResponse(raw, url)


class SvDn1PublicationObserverTests(unittest.TestCase):
    def test_exact_public_bytes_complete_observation(self):
        package = package_fixture()
        result = observer.observe_publication(package, opener=FakeOpener(package))
        self.assertEqual(result["transition_id"], "SV_DN1_AUTHENTIC_PUBLICATION_OBSERVED")
        self.assertTrue(result["all_public_artifacts_observed"])
        self.assertTrue(result["exact_bytes_preserved"])
        self.assertFalse(result["credential_used"])
        self.assertFalse(result["repository_writeback_performed"])
        self.assertFalse(result["deployment_performed"])
        self.assertEqual(set(result["artifacts"]), set(observer.EXPECTED_FILES))
        self.assertTrue(all(row["exact_bytes_match"] for row in result["artifacts"].values()))

    def test_tampered_public_artifact_fails_closed(self):
        package = package_fixture()
        with self.assertRaisesRegex(observer.PublicationObservationError, "do not match governed package"):
            observer.observe_publication(package, opener=FakeOpener(package, mutate="index.html"))

    def test_redirect_outside_admitted_public_host_fails_closed(self):
        package = package_fixture()
        with self.assertRaisesRegex(observer.PublicationObservationError, "escaped admitted host"):
            observer.observe_publication(package, opener=FakeOpener(package, redirect_host="example.com"))

    def test_package_hash_tamper_fails_before_network(self):
        package = package_fixture()
        package["package_sha256"] = "0" * 64
        with self.assertRaisesRegex(observer.PublicationObservationError, "package_sha256 mismatch"):
            observer.observe_publication(package, opener=FakeOpener(package))

    def test_non_https_or_wrong_path_is_rejected(self):
        package = package_fixture()
        with self.assertRaisesRegex(observer.PublicationObservationError, "HTTPS"):
            observer.observe_publication(package, base_url="http://stegverse-org.github.io/stegverse-demo-suite/sv-dn1/", opener=FakeOpener(package))
        with self.assertRaisesRegex(observer.PublicationObservationError, "path mismatch"):
            observer.observe_publication(package, base_url="https://stegverse-org.github.io/other/", opener=FakeOpener(package))


if __name__ == "__main__":
    unittest.main()
