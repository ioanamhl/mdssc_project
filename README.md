# GreenCart Grocery — MDSSC CI/CD Project

[![CI/CD](https://github.com/ioanamhl/mdssc_project/actions/workflows/cicd.yml/badge.svg)](https://github.com/ioanamhl/mdssc_project/actions/workflows/cicd.yml)

A university project demonstrating a secure CI/CD pipeline for a grocery shop application (GreenCart), integrating MDSSC (OPSWAT MetaDefender Supply Chain Security) scanning on both source code and build artifacts.

## The Application

**GreenCart** is a full-stack online grocery store:

- **Backend** — Node.js + Express + MongoDB (Mongoose), JWT authentication, image upload via Cloudinary, Stripe payments
- **Frontend** — React + Vite (SPA, served static)
- **Infrastructure** — Docker, PM2, Nginx, DigitalOcean Droplet ($6/month)

## Pipeline Architecture

The pipeline is structured on two levels — **GitHub Actions** (outer orchestrator) and **Jenkins** (inner pipeline), as shown below:

```
PUSH ──> GITHUB ACTIONS (outer)
              |
              |── MDSSC Scan         (OPSWAT, sursă)
              |
              |── TRIGGER JENKINS ──────────> JENKINS (inner)
              |    ^ waits                    |── MDSSC source scan
              |    |                          |── build artifact
              |    |                          |── MDSSC artifact scan
              |    |                          └── deploy to VPS
              |    └──────────────────────── returns green/red
              |
              |── E2E Test           (Playwright on the freshly deployed VPS)
              |
              └── Release            (tag + GitHub Release if everything is green)
```

GitHub Actions orchestrates the entire flow; Jenkins is called as an inner stage, runs the MDSSC scans + build + deploy, then returns the result (green/red) back to Actions.

## Jenkins Stages (inner pipeline)

| # | Stage | Description |
|---|-------|-------------|
| 1 | **Checkout** | Clone repo, verify tools, create source archive `.tar.gz` |
| 2 | **Check Health** | Verify MDSSC server + fetch workflow metadata (StorageId, RepositoryId) |
| 3 | **Source Code Scan** | Direct upload of source archive → MDSSC; indirect scan via branch reference |
| 4 | **Build** | `npm ci` backend + frontend in parallel, `vite build`, packaging, Docker images |
| 5 | **Artifact Scan** | MDSSC scan on all build artifacts (frontend bundle, backend archive, Docker images) |
| 6 | **Deploy** | PM2 restart/start backend (Node.js) + PM2 serve frontend (static SPA, port 3001) |

## MDSSC API — Methods Used

| Method | Endpoint | Role |
|--------|----------|------|
| GET | `/api/v1/health` | MDSSC server health check |
| GET | `/api/v1/workflows/{workflowId}` | Fetch workflow metadata |
| POST | `/api/v1/scans/direct` | File upload + scan initiation |
| GET | `/api/v1/scans/{id}/overview` | Scan status polling |
| GET | `/api/v1/scans/{id}` | Final scan result |
| POST | `/api/v1/scans` | Indirect scan via repo/branch reference |

## Infrastructure

- **Jenkins** runs on a **DigitalOcean Droplet** ($6/month)
- **VPS stack**: Node.js, MongoDB, Nginx, PM2, Docker
- **Jenkins SCM polling**: every 2 minutes (`H/2 * * * *`)
- **Vulnerability threshold**: configurable (critical / high / medium / low)

## Roadmap — Team Responsibilities

### Vera — Infrastructure & Jenkins
-  Create VM in the cloud (DigitalOcean Droplet)
-  Install Jenkins on VM
-  Configure Jenkins (plugins, credentials)
-  Install Node.js, MongoDB, Nginx on VM
-  Configure PM2 for running the application
-  Infrastructure documentation

### Ioana — GitHub & Pipeline
-  Create GitHub repo + invite team
-  Clone source code and push to team repo
-  Write Jenkinsfile with stages: Install → Scan → Test → Deploy
-  Configure GitHub → Jenkins webhook

### Adi — GitHub Actions Workflows
-  Create `.github/workflows/ci.yml` (Scan Code + YAML validation)
-  Create `.github/workflows/release.yml` (automated build + deploy)
-  Configure E2E tests in workflow
-  Test that Actions trigger on every push/PR
-  Add status badge to README

### Mario — End-to-End Tests & Code Scanning
-  Configure `npm audit` for dependency scanning
-  Integrate ESLint for code quality
-  Integrate Snyk or OWASP for vulnerabilities
-  Configure scan reports (JSON/HTML output)
-  Test that scanning detects real issues
-  Document how to read the reports

## Repository Structure

```
mdssc_project/
├── backend/          # Node.js + Express API
├── frontend/         # React + Vite SPA
├── ci/
│   ├── Jenkinsfile           # Full Jenkins pipeline
│   └── mdsscAdvanced.groovy  # MDSSC helper library
├── e2e/              # Playwright E2E tests
│   ├── playwright.config.js
│   └── tests/
├── .github/
│   ├── config.yml            # ← Configuratie pipeline (editeaza asta)
│   ├── scripts/              # Python scripts CI/CD
│   └── workflows/
│       └── cicd.yml          # GitHub Actions workflow
└── docker-compose.yml
```

---

## Adapting This Pipeline to Your Own Project

Copy `.github/`, `ci/`, and `e2e/` into your repository, then follow the steps below. You do **not** need to touch the Python scripts or the workflow YAML for a basic setup.

### Step 1 — Fill in `.github/config.yml`

This is the single source of truth for all project-specific values read by GitHub Actions at runtime.

```yaml
project:
  name: "My App"               # shown in the Pages dashboard title

jenkins:
  job_name: "my-jenkins-job"   # must match the Jenkins job name exactly
  timeout_minutes: 30
  app_name: "myapp"            # used for pm2 process names (myapp-backend, myapp-frontend)

github_actions:
  job_names:                   # must match the `name:` fields in cicd.yml exactly
    - "MDSSC Scan (OPSWAT)"
    - "Jenkins (MDSSC + Build + Deploy)"
    - "E2E Tests (Playwright)"
    - "Auto Release (semver)"

app:
  backend_dir: "backend"
  frontend_dir: "frontend"
  frontend_port: 3001          # keep in sync with VPS firewall rules

e2e:
  base_url_fallback: "http://localhost:3000"   # used locally; secret overrides in CI
```

> **Note:** `scan_cron` in `config.yml` is documentation only — also update the `on: schedule: cron:` value in `.github/workflows/cicd.yml` manually, as GitHub evaluates that field before any steps run.

### Step 2 — Set GitHub Secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Description |
|--------|-------------|
| `JENKINS_VPS_URL` | Jenkins base URL, e.g. `http://your-vps-ip:8080` |
| `JENKINS_USER` | Jenkins username |
| `MDSSC_JENKINS_API_TOKEN` | Jenkins API token (generate in Jenkins → User → Configure → API Token) |
| `MDSSC_SERVER` | MDSSC server base URL, e.g. `http://your-mdssc-ip` |
| `MDSSC_JENKINS_API_TOKEN` | MDSSC API key (also used by the GitHub Actions MDSSC scanner) |
| `VPS_BASE_URL` | Deployed app URL for E2E tests, e.g. `http://your-vps-ip:3001` |
| `DOCKERHUB_USERNAME` | _(optional)_ Docker Hub username — avoids anonymous pull rate limits |
| `DOCKERHUB_TOKEN` | _(optional)_ Docker Hub access token |

### Step 3 — Update `ci/Jenkinsfile`

Change the single `APP_NAME` value at the top of the `environment {}` block. Everything else derives from it automatically (Docker image names, PM2 process names, scan labels):

```groovy
environment {
    APP_NAME = 'myapp'    // ← change only this
    ...
}
```

Also update the MDSSC parameter defaults (optional — they can be left as-is and overridden per-run from the Jenkins UI):

```groovy
string(name: 'MDSSC_SERVER', defaultValue: 'http://your-mdssc-ip', ...)
string(name: 'MDSSC_CREDENTIALS_ID', defaultValue: 'mdssc-api-key', ...)
```

### Step 4 — Enable GitHub Pages

In your repo: **Settings → Pages → Source: "GitHub Actions"**.

The pipeline dashboard will be published automatically at `https://<your-username>.github.io/<repo-name>/` after the first successful run on `main`.

### Step 5 — Install the Jenkins Plugin

The pipeline stage monitoring requires the **Pipeline: REST API** plugin in Jenkins.

Install it from: **Jenkins → Manage Jenkins → Plugins → Available → "Pipeline: REST API"**

### What Each File Does at Runtime

| File | When it runs | What it does |
|------|-------------|--------------|
| `.github/config.yml` | — | Single config file; read by the step below |
| `.github/scripts/load_config.py` | First step of `deploy` and `publish-dashboard` jobs | Reads `config.yml`, exports values as env vars via `$GITHUB_ENV` |
| `.github/scripts/pipeline_data.py` | During `publish-dashboard` | Fetches GitHub Actions job statuses + Jenkins stage statuses from APIs |
| `.github/scripts/generate_pages_site.py` | During `publish-dashboard` | Generates the styled HTML dashboard page |
| `ci/Jenkinsfile` | On Jenkins | Full inner pipeline: scan → build → artifact scan → deploy |
| `ci/mdsscAdvanced.groovy` | On Jenkins (loaded by Jenkinsfile) | MDSSC API helper library |
