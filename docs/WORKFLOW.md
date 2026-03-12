# Development Workflow

This document defines the update and release workflow for the StegVerse demo repository.

## Bundle Update Process

1. Download bundle ZIP
2. Extract bundle
3. Move files layer-by-layer into repo structure
4. Run `git status` to confirm updates
5. Commit changes
6. Push to GitHub

## Report Creation Process

1. Execute commands from [Demo Runbook](./DEMO_RUNBOOK.md)
2. Capture screenshots of runtime output
3. Assemble report using the structure defined in [REPORT_README.md](./REPORT_README.md)
4. Export PDF
5. Place report in this directory

## Release Tagging

Example:

```
git add .
git commit -m "runtime update"
git tag -a v1.1.0 -m "Mutation Governance Runtime"
git push origin main
git push origin v1.1.0
```

Refer to [Release Log](./RELEASE_LOG.md) for historical releases.