from __future__ import annotations
import json
from pathlib import Path

class ReportsGate:
    def __init__(self, repo_root:Path):
        self.repo_root=Path(repo_root).resolve(); self.manifest_path=self.repo_root/'docs'/'reports_manifest.json'; self.manifest=json.loads(self.manifest_path.read_text(encoding='utf-8'))
    def list_reports(self): return self.manifest['reports']
    def get_report_entry(self, report_id):
        reports=self.manifest['reports']
        if report_id not in reports: raise KeyError(f'Unknown report: {report_id}')
        return reports[report_id]
    def get_report_message(self, report_id):
        entry=self.get_report_entry(report_id)
        if entry['status']=='available': return f"Report available: {entry['title']}\nPath: {entry['path']}"
        if entry['status']=='reserved': return f"Report: {entry['title']}\nStatus: reserved\nRelease state: causally withheld\nPlaceholder report available at: {entry['path']}"
        return f"Report: {entry['title']}\nStatus: unavailable\nRelease state: not yet admissible\nPlaceholder report available at: {entry['path']}"
