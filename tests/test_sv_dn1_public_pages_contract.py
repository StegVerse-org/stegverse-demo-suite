from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class SvDn1PublicPagesContractTests(unittest.TestCase):
    def test_placeholder_is_explicitly_non_live(self):
        page = (ROOT / "public" / "sv-dn1" / "index.html").read_text()
        self.assertIn("WITHHELD", page)
        self.assertIn("NONE_YET", page)
        self.assertIn("NOT ANALYZED", page)
        self.assertIn("No fixture or parsed-web preflight is being presented as live evidence.", page)
        self.assertIn("StegVerse production pipeline under observation", page)
        self.assertNotIn("<script", page.lower())

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
