from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SvDn1PublicPagesContractTests(unittest.TestCase):
    def test_public_projection_is_fail_closed_before_activation_or_receipt_derived_after_activation(self):
        page = (ROOT / "public" / "sv-dn1" / "index.html").read_text()

        withheld = (
            "WITHHELD" in page
            and "NONE_YET" in page
            and "NOT ANALYZED" in page
            and "No fixture or parsed-web preflight is being presented as live evidence." in page
        )
        activated = (
            "Admission state:</strong> SDK_ADMITTED" in page
            and "Observation class:</strong> LIVE" in page
            and (
                "Publication state:</strong> PUBLIC_OBSERVED" in page
                or "Publication state:</strong> PUBLIC_WITH_LIMITATIONS" in page
            )
            and "Receipt chain" in page
            and "StegVerse production pipeline under observation" in page
        )

        self.assertTrue(
            withheld or activated,
            "public projection must be either the explicit fail-closed placeholder "
            "or an authentic receipt-derived SDK_ADMITTED live result",
        )
        self.assertNotEqual(
            withheld,
            activated,
            "placeholder and activated public-result semantics must not be conflated",
        )
        self.assertNotIn("<script", page.lower())

        if activated:
            self.assertNotIn("FIXTURE / NOT LIVE-ADMITTED", page)
            self.assertIn("Transparency boundary:", page)
            self.assertIn("Production perfection claimed:</strong> false", page)

    def test_static_hosting_workflow_cannot_run_evaluation(self):
        workflow = (ROOT / ".github" / "workflows" / "deploy-sv-dn1-pages.yml").read_text()
        for token in (
            "observe_sv_dn1_hf_public.py",
            "run_sv_dn1.py",
            "build_sv_dn1_sdk_ingress_manifest.py",
            "stegverse governance",
            "curl ",
            "wget ",
            "huggingface.co/api/",
        ):
            self.assertNotIn(token, workflow)
        self.assertIn("path: public", workflow)
        self.assertIn("persist-credentials: false", workflow)


if __name__ == "__main__":
    unittest.main()
