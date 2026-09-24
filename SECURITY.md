# Security Policy

## Scope

CyberSentinel is a **defensive** analysis tool for portfolio and learning purposes. It analyses uploaded flow data and packet captures. It does not send traffic, scan networks, exploit systems, or execute uploaded content. Requests to add offensive functionality will be declined.

## Supported versions

Only the latest commit on `main` is supported. There are no maintained release branches yet.

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security problems.

Use GitHub's private vulnerability reporting for this repository (Security tab, "Report a vulnerability"). Include:

- what is affected (file, endpoint, component) and the commit you tested
- steps to reproduce, and what you expected instead
- impact as you understand it

You should get an acknowledgement within 7 days. This is a one-person student project, so fixes are best-effort. Reporters are credited in the changelog unless they prefer not to be.

## Security practices in this repository

Implemented now:

- No secrets in the repository. Configuration comes from environment variables; `.env` is gitignored and `.env.example` holds dummy values only.
- Secret scanning (gitleaks) and large-file checks in pre-commit.
- YAML is loaded with `yaml.safe_load` only. Config models reject unknown keys.
- Datasets and model artifacts are never committed.

Planned (tracked in `docs/PROJECT_PLAN.md`, Section 7):

- Upload validation (type allow-list, magic bytes, size limits enforced twice), random storage names, no archive extraction
- PCAP parsing isolated in a container with no network, read-only filesystem, non-root user and resource limits
- Argon2id password hashing, server-side sessions in HttpOnly/SameSite cookies, CSRF protection, role-based access control
- Model artifacts loaded only from a trusted, read-only location after SHA-256 verification. No model upload feature (pickle-style formats can execute code)
- Dependency and container scanning in CI (pip-audit, npm audit, Trivy, CodeQL, Dependabot)
- STRIDE threat model in `docs/THREAT_MODEL.md`

## Data handling

Do not upload real production traffic or personal data to a demo instance. Public research datasets are the intended input.
