# ADF Level 3 - launch criteria and next implementation

## Prerequisite
Merge the branch only after the four mandatory gates pass on the PR commit:
`verify`, `gate-next-fastapi`, `gate-flutter`, `gate-expo`.
The Android E2E gate uses ADB/UIAutomator to verify an installed and launched app; it does not exercise full user journeys. Keep Maestro separately as a non-blocking diagnostic until compatible infrastructure is demonstrated.

## Level 3 proposed deliverables
1. Make check-evidence artifacts tamper-evident with hashes and explicit provenance (commit, run id, timestamps).
2. Enforce least-privilege tool permissions and explicit agent action approval policies.
3. Add a PR policy gate covering threat-model, dependency and secrets scanning, and SBOM output.
4. Add reproducible acceptance suites for each stack and collect coverage information.
5. Protect main with the four required checks, requiring PRs and excluding bypasses only after all checks pass.

This is a planning handoff, not Level 3 implementation or certification.
