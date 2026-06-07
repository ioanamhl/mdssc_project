#!/usr/bin/env python3
"""Date comune despre starea celor doua pipeline-uri (GitHub Actions + Jenkins).

Folosit atat de write_pipeline_summary.py (raport in Job Summary), cat si de
generate_pages_site.py (pagina live publicata pe GitHub Pages) -- ca sa nu
existe doua surse diferite pentru aceleasi date.

Variabile de mediu necesare:
  JOBS_API_URL      - URL-ul GitHub "list jobs for a workflow run"
  GH_API_TOKEN      - token pentru autentificare la API-ul GitHub
  BUILD_URL         - URL-ul build-ului Jenkins curent (cu "/" la final)
  JENKINS_USER      - utilizator Jenkins
  JENKINS_API_TOKEN - token API Jenkins
"""

import json
import os
import urllib.request
from base64 import b64encode


def fetch_json(url, auth_header):
    request = urllib.request.Request(url, headers={'Authorization': auth_header})
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode())


def github_jobs():
    try:
        data = fetch_json(os.environ['JOBS_API_URL'], 'Bearer ' + os.environ['GH_API_TOKEN'])
        return [
            {'name': job['name'], 'status': (job.get('conclusion') or job.get('status') or 'queued').upper()}
            for job in data.get('jobs', [])
        ]
    except Exception as exc:
        print(f'Avertisment: nu am putut citi joburile GitHub Actions ({exc})')
        return []


def jenkins_stages():
    try:
        auth = 'Basic ' + b64encode(
            f"{os.environ['JENKINS_USER']}:{os.environ['JENKINS_API_TOKEN']}".encode()
        ).decode()
        data = fetch_json(os.environ['BUILD_URL'] + 'wfapi/describe', auth)
        return [{'name': s.get('name', '?'), 'status': s.get('status', '?')} for s in data.get('stages', [])]
    except Exception as exc:
        print(f'Avertisment: nu am putut citi etapele Jenkins ({exc})')
        return []


ICONS = {
    'SUCCESS':      '✅',
    'FAILURE':      '❌',
    'FAILED':       '❌',
    'IN_PROGRESS':  '🔄',
    'NOT_EXECUTED': '⏳',
    'CANCELLED':    '🚫',
    'QUEUED':       '⏳',
    'SKIPPED':      '⏭️',
}
