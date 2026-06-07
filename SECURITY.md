# Security Policy

## Overview
This pipeline integrates OPSWAT MDSSC Scanner, npm audit, and ESLint
to automatically detect vulnerabilities on every push.

## How It Works
Every push triggers:
1. **npm audit** — scans Node.js dependencies for known vulnerabilities
2. **ESLint** — checks code quality and potential security issues 
3. **MDSSC Scan** — scans source code for CVEs, malware, and secrets

## Configuring Security Threshold
In Jenkins, set these parameters before running the pipeline:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `MDSSC_VULNERABILITY_THRESHOLD` | Severity level that fails the build | `critical` |
| `MDSSC_FAIL_ON_VULNERABILITIES` | Stop pipeline if vulnerabilities found | `false` |

Options: `critical`, `high`, `medium`, `low`

## How to Read Reports
After each build, go to **Jenkins → Your Build → Artifacts**:

- `backend-audit.json` — vulnerabilities found in backend dependencies
- `frontend-audit.json` — vulnerabilities found in frontend dependencies  
- `eslint-report.json` — code quality issues found in frontend

Each report contains:
- Severity level (critical/high/moderate/low)
- Package name and version affected
- CVE identifier
- Recommended fix

## How to Fix Vulnerabilities
```bash
# Fix automatically where possible
npm audit fix

# Force fix (may include breaking changes)
npm audit fix --force
```

## Security Contacts
Report security issues to your DevSecOps team.