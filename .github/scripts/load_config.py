#!/usr/bin/env python3
"""Citeste .github/config.yml si exporta valorile in GITHUB_ENV, astfel incat
toti pasii urmatori din workflow sa le poata folosi ca variabile de mediu.

Apelat ca primul pas (dupa checkout) in job-urile care au nevoie de config.
PyYAML este pre-instalat pe runner-ii ubuntu-latest din GitHub Actions.
"""

import os
import sys

try:
    import yaml
except ImportError:
    print("PyYAML nu este instalat. Ruleaza: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yml')

try:
    with open(config_path, encoding='utf-8') as f:
        cfg = yaml.safe_load(f) or {}
except FileNotFoundError:
    print(f"ATENTIE: {config_path} nu a fost gasit — se folosesc valori implicite.", file=sys.stderr)
    cfg = {}

env_file = os.environ.get('GITHUB_ENV')
if not env_file:
    print("GITHUB_ENV nu este setat — acest script este destinat rularii in GitHub Actions.", file=sys.stderr)
    sys.exit(1)


def write_env(name, value):
    with open(env_file, 'a', encoding='utf-8') as f:
        f.write(f'{name}={value}\n')
    print(f'  {name} = {value}')


print('=== Incarcare .github/config.yml ===')

project = cfg.get('project', {})
write_env('PROJECT_NAME', project.get('name', 'Pipeline Dashboard'))

jenkins = cfg.get('jenkins', {})
write_env('JENKINS_JOB',          jenkins.get('job_name', 'my-jenkins-job'))
write_env('JENKINS_APP_NAME',     jenkins.get('app_name', 'myapp'))

# JENKINS_TIMEOUT_MIN: inputul workflow_dispatch suprascrie config-ul cand e furnizat.
# Daca inputul nu a fost furnizat (variabila e goala), folosim valoarea din config.
existing_timeout = os.environ.get('JENKINS_TIMEOUT_MIN', '').strip()
if not existing_timeout:
    write_env('JENKINS_TIMEOUT_MIN', str(jenkins.get('timeout_minutes', 30)))
else:
    print(f'  JENKINS_TIMEOUT_MIN = {existing_timeout} (din workflow input, suprascrie config)')

gh = cfg.get('github_actions', {})
job_names = gh.get('job_names', [])
write_env('GITHUB_JOB_NAMES', '|'.join(job_names))

app = cfg.get('app', {})
write_env('FRONTEND_PORT', str(app.get('frontend_port', 3001)))

e2e_cfg = cfg.get('e2e', {})
write_env('E2E_BASE_URL_FALLBACK', e2e_cfg.get('base_url_fallback', 'http://localhost:3000'))

print('=== Config incarcat cu succes ===')
