# GreenCart Grocery — MDSSC CI/CD Project

Proiect universitar ce demonstrează un pipeline CI/CD securizat pentru o aplicație de tip grocery shop (GreenCart), integrând scanare MDSSC (OPSWAT MetaDefender Supply Chain Security) atât pe codul sursă, cât și pe artefactele de build.

## Aplicația

**GreenCart** este un magazin online de produse alimentare cu arhitectură full-stack:

- **Backend** — Node.js + Express + MongoDB (Mongoose), autentificare JWT, upload imagini via Cloudinary, plăți Stripe
- **Frontend** — React + Vite (SPA, served static)
- **Infrastructură** — Docker, PM2, Nginx, DigitalOcean Droplet ($6/lună)

## Arhitectura Pipeline-ului

Pipline-ul este structurat pe două niveluri — **GitHub Actions** (orchestrator exterior) și **Jenkins** (pipeline interior), conform schemei de mai jos:

```
PUSH ──> GITHUB ACTIONS (outer)
              |
              |── Scan Code          (CodeQL)
              |
              |── TRIGGER JENKINS ──────────> JENKINS (inner)
              |    ^ așteaptă                 |── scan sursă MDSSC
              |    |                          |── build artefact
              |    |                          |── scan artefact MDSSC
              |    |                          └── deploy pe VPS
              |    └──────────────────────── întoarce verde/roșu
              |
              |── E2E Test           (Playwright pe VPS-ul tocmai deployat)
              |
              └── Release            (tag + GitHub Release dacă tot e verde)
```

GitHub Actions orchestrează tot fluxul; Jenkins este chemat ca o etapă internă, execută scanările MDSSC + build + deploy, după care returnează rezultatul (verde/roșu) înapoi în Actions.

## Stagiile Jenkins (pipeline interior)

| # | Stagiu | Descriere |
|---|--------|-----------|
| 1 | **Checkout** | Clonare repo, verificare tool-uri, creare arhivă sursă `.tar.gz` |
| 2 | **Check Health** | Verificare server MDSSC + fetch metadate workflow (StorageId, RepositoryId) |
| 3 | **Source Code Scan** | Upload direct arhivă sursă → MDSSC; scan indirect prin referință de branch |
| 4 | **Build** | `npm ci` backend + frontend în paralel, `vite build`, packaging, Docker images |
| 5 | **Artifact Scan** | Scanare MDSSC pe toate artefactele de build (frontend bundle, backend archive, Docker images) |
| 6 | **Deploy** | PM2 restart/start backend (Node.js) + PM2 serve frontend (SPA static, port 3001) |

## MDSSC API — metode folosite

| Metodă | Endpoint | Rol |
|--------|----------|-----|
| GET | `/api/v1/health` | Health check server MDSSC |
| GET | `/api/v1/workflows/{workflowId}` | Fetch metadate workflow |
| POST | `/api/v1/scans/direct` | Upload fișier + inițiere scanare |
| GET | `/api/v1/scans/{id}/overview` | Polling status scanare |
| GET | `/api/v1/scans/{id}` | Rezultat final scanare |
| POST | `/api/v1/scans` | Scanare indirectă prin referință repo/branch |

## Infrastructură

- **Jenkins** rulează pe un **DigitalOcean Droplet** ($6/lună)
- **Stack pe VPS**: Node.js, MongoDB, Nginx, PM2, Docker
- **Jenkins polling SCM**: la fiecare 2 minute (`H/2 * * * *`)
- **Vulnerability threshold**: configurabil (critical / high / medium / low)

## Roadmap — Responsabilități echipă

### Vera — Infrastructură & Jenkins
-  Creare VM în cloud (DigitalOcean Droplet)
-  Instalare Jenkins pe VM
-  Configurare Jenkins (pluginuri, credențiale)
-  Instalare Node.js, MongoDB, Nginx pe VM
-  Configurare PM2 pentru rularea aplicației
-  Documentație infrastructură

### Ioana — GitHub & Pipeline
-  Creare repo GitHub + invitare echipă
-  Clone cod sursă și upload pe repo-ul echipei
-  Scriere Jenkinsfile cu stagiile: Install → Scan → Test → Deploy
-  Configurare webhook GitHub → Jenkins

### Adi — GitHub Actions Workflows
-  Creare `.github/workflows/ci.yml` (Scan Code + validare YAML)
-  Creare `.github/workflows/release.yml` (build + deploy automat)
-  Configurare E2E tests în workflow
-  Testare că Actions pornesc la fiecare push/PR
-  Adăugare badge de status în README

### Mario — End-to-End Tests & Scanare Cod
-  Configurare `npm audit` pentru scanare dependențe
-  Integrare ESLint pentru calitatea codului
-  Integrare Snyk sau OWASP pentru vulnerabilități
-  Configurare rapoarte de scanare (output JSON/HTML)
-  Testare că scanarea detectează probleme reale
-  Documentare cum se citesc rapoartele

## Structura Repo

```
mdssc_project/
├── backend/          # Node.js + Express API
├── frontend/         # React + Vite SPA
├── ci/
│   ├── Jenkinsfile           # Pipeline Jenkins complet
│   └── mdsscAdvanced.groovy  # Biblioteca MDSSC helper
├── e2e/              # Playwright E2E tests (de adăugat de Mario)
│   ├── playwright.config.js
│   └── tests/
├── .github/
│   └── workflows/    # GitHub Actions (de adăugat de Adi)
└── docker-compose.yml
```
