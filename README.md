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
├── e2e/              # Playwright E2E tests (to be added by Mario)
│   ├── playwright.config.js
│   └── tests/
├── .github/
│   └── workflows/    # GitHub Actions (de adăugat de Adi)
└── docker-compose.yml
```
