#!/usr/bin/env python3
"""Scrie in Job Summary un raport combinat cu starea celor doua pipeline-uri:
GitHub Actions (outer) si Jenkins (inner) -- unul sub altul, direct pe pagina
de rezultate a rularii (vizibil instant, fara artefacte de descarcat).

Date comune (fetch din GitHub/Jenkins) sunt in pipeline_data.py.

Variabile de mediu suplimentare folosite aici:
  JENKINS_JOB         - numele jobului Jenkins (doar pentru afisare)
  GITHUB_STEP_SUMMARY - (setat automat de GitHub Actions) fisierul Markdown
                        care devine rezumatul vizibil al jobului
"""

import os

from pipeline_data import github_jobs, jenkins_stages, ICONS


# Doar emoji de status -- numele nodului e randat separat ca "code span"
# (apare ca o cutie gri monospace in Markdown), ca sa semene cu un nod de pipeline.
#
# Markdown-ul din Job Summary nu accepta CSS/HTML custom (GitHub il elimina din
# motive de securitate), deci nu putem desena cutii colorate cu borduri ca in
# interfata GitHub/Jenkins. In schimb recream aceeasi senzatie -- un lant de
# noduri distincte, conectate prin sageti, fiecare cu indicator de status --
# folosind doar elemente garantate sa se afiseze: code-span-uri + emoji + sageti.
ARROW = '&nbsp;&nbsp;➜&nbsp;&nbsp;'


def chain(nodes):
    if not nodes:
        return '_(informatie indisponibila)_'
    parts = [f"`{node['name']}` {ICONS.get(node['status'], '❔ ' + node['status'])}" for node in nodes]
    return ARROW.join(parts)


def main():
    jenkins_job = os.environ.get('JENKINS_JOB', 'proiect-mdssc')
    sections = [
        '## 🔀 Pipeline Dashboard — GreenCart MDSSC',
        '',
        '**GitHub Actions** — _outer pipeline_',
        '',
        chain(github_jobs()),
        '',
        f'**↳ Jenkins `{jenkins_job}`** — _inner pipeline, ruleaza in interiorul nodului "Jenkins (MDSSC + Build + Deploy)"_',
        '',
        chain(jenkins_stages()),
        '',
        f'`Build Jenkins:` {os.environ.get("BUILD_URL", "-")}',
    ]
    with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as handle:
        handle.write('\n'.join(sections) + '\n')
    print('Dashboard combinat scris in Job Summary.')


if __name__ == '__main__':
    main()
