# Dependency policy

Successful locked installation, source validation and Docker builds are sufficient evidence for eligible dependency auto-merge. All required Dependency CI Gate checks on an up-to-date branch must pass; no bypass is allowed. Every grouped dependency must qualify. Same-major minor/patch upgrades, including pre-1.0 minor/patch updates, are eligible. Numeric majors, prereleases, downgrades and unreliable version metadata remain manual. Calendar-version exceptions are not enabled in this repository.
