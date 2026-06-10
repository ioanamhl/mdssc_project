#!/usr/bin/env python3
"""Genereaza o pagina HTML statica -- cu noduri si sageti colorate, in stilul
graficelor din GitHub Actions / Jenkins Blue Ocean -- care prezinta starea
celor doua pipeline-uri (GitHub Actions = outer, Jenkins = inner).

Pagina e (re)publicata pe GitHub Pages dupa fiecare rulare pe `main`, asa ca
link-ul ramane mereu acelasi si arata mereu ULTIMA stare cunoscuta -- un
"dashboard live" fara cost de hosting propriu.

Important pentru securitate: tokenurile NU ajung niciodata in browser. Datele
sunt preluate aici, server-side, in interiorul rularii (cu secretele din
Actions); pagina publicata contine doar rezultatul -- nume + status, oricum
vizibile public in Actions.

Date comune (fetch din GitHub/Jenkins) sunt in pipeline_data.py.

Variabile de mediu suplimentare folosite aici:
  JENKINS_JOB    - numele jobului Jenkins (doar pentru afisare)
  SITE_DIR       - folderul in care se scrie index.html (implicit "_site")
  GITHUB_SERVER_URL / GITHUB_REPOSITORY / GITHUB_RUN_ID - link spre rularea curenta
"""

import datetime
import os
from html import escape

from pipeline_data import github_jobs, jenkins_stages, ICONS


STATUS_CLASS = {
    'SUCCESS':      'ok',
    'FAILURE':      'fail',
    'FAILED':       'fail',
    'CANCELLED':    'fail',
    'IN_PROGRESS':  'running',
    'NOT_EXECUTED': 'pending',
    'QUEUED':       'pending',
    'SKIPPED':      'skip',
}


def node_html(name, status, extra_attrs=''):
    css_class = STATUS_CLASS.get(status, 'pending')
    icon = ICONS.get(status, '❔')
    return (f'<div class="node {css_class}"{extra_attrs}>'
            f'<span class="icon">{icon}</span>'
            f'<span class="label">{escape(name)}</span>'
            f'</div>')


def chain_html(nodes, anchor_predicate=None):
    """Randeaza un lant de noduri conectate cu sageti.

    anchor_predicate -- functie optionala(node_dict -> bool); nodul care
    returneaza True primeste data-anchor="true", folosit de JS-ul de pe pagina
    ca punct de ancorare pentru conectorul vertical catre inner pipeline.
    """
    if not nodes:
        return '<p class="muted"><em>(informatie indisponibila)</em></p>'
    pieces = []
    for index, item in enumerate(nodes):
        if index:
            pieces.append('<div class="arrow">&#10148;</div>')
        extra = ' data-anchor="true"' if (anchor_predicate and anchor_predicate(item)) else ''
        pieces.append(node_html(item['name'], item['status'], extra_attrs=extra))
    return '<div class="chain">' + ''.join(pieces) + '</div>'


CSS = """
:root {
  color-scheme: dark;
  --bg: #0d1117;
  --panel: #161b22;
  --border: #30363d;
  --text: #c9d1d9;
  --muted: #8b949e;
  --ok: #2ea043;
  --fail: #f85149;
  --running: #d29922;
  --pending: #6e7681;
  --link: #58a6ff;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font: 15px/1.55 -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}
main { max-width: 980px; margin: 0 auto; padding: 32px 20px 60px; }
h1 { font-size: 22px; margin: 0 0 4px; }
h2 { font-size: 16px; margin: 0 0 10px; display: flex; align-items: center; gap: 8px; }
h3 { font-size: 14px; margin: 0 0 4px; display: flex; flex-wrap: wrap; align-items: center; gap: 8px; font-weight: 600; }
.muted { color: var(--muted); font-size: 13px; }
p.muted { margin: 6px 0 0; }
code {
  background: #0d1117;
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 1px 6px;
  font-size: 13px;
}
.tag {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: .04em;
  text-transform: uppercase;
  color: var(--muted);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 1px 9px;
}
/* === Layout pipeline combinat === */
.pipeline-combined {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px 18px 20px;
  margin-top: 14px;
  position: relative;
}
.chain {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
}
/* Linia verticala care conecteaza nodul Jenkins exterior cu inner pipeline.
   Pozitia sa orizontala (margin-left) e setata dinamic de JS la incarcarea
   paginii, astfel incat sa porneasca exact din centrul nodului Jenkins. */
.v-conn {
  width: 0;
  height: 22px;
  border-left: 2px dashed var(--border);
  margin-top: 6px;
  margin-bottom: -12px;
  position: relative;
  z-index: 1;
}
/* Sectiunea inner Jenkins -- border dashed ca sa o diferentieze vizual de
   sectiunea exterioara (border solid) si sa sugereze ca e "in interiorul"
   unui nod din lantul de deasupra. */
.inner-section {
  border: 1px dashed var(--border);
  border-radius: 10px;
  padding: 14px 16px 16px;
  position: relative;
  z-index: 0;
}
/* === Noduri === */
.node {
  display: flex;
  align-items: center;
  gap: 7px;
  border: 1px solid var(--border);
  border-left: 4px solid var(--pending);
  border-radius: 8px;
  padding: 8px 14px;
  background: #0d1117;
  font-size: 13px;
  white-space: nowrap;
}
.node .label { font-family: ui-monospace, "Cascadia Code", Consolas, monospace; }
.node.ok      { border-left-color: var(--ok); }
.node.fail    { border-left-color: var(--fail); }
.node.skip    { border-left-color: var(--muted); opacity: .6; }
.node.pending { border-left-color: var(--pending); opacity: .75; }
.node.running {
  border-left-color: var(--running);
  animation: pulse 1.6s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(210, 153, 34, .35); }
  50%      { box-shadow: 0 0 0 5px rgba(210, 153, 34, 0); }
}
.arrow { color: var(--muted); font-size: 16px; }
/* === Footer === */
footer {
  margin-top: 28px;
  color: var(--muted);
  font-size: 12px;
  border-top: 1px solid var(--border);
  padding-top: 14px;
}
footer a { color: var(--link); }
"""

# Pozitioneaza linia verticala exact sub centrul nodului Jenkins din lantul
# GitHub Actions (data-anchor="true"). Ruleaza la load si la resize.
CONNECTOR_SCRIPT = """<script>
(function () {
  function align() {
    var anchor = document.querySelector('[data-anchor]');
    var conn   = document.getElementById('v-conn');
    if (!anchor || !conn) return;
    var ar = anchor.getBoundingClientRect();
    var pr = conn.parentElement.getBoundingClientRect();
    var cx = Math.round(ar.left - pr.left + ar.width / 2 - 1);
    conn.style.marginLeft = Math.max(16, cx) + 'px';
  }
  align();
  window.addEventListener('resize', align);
})();
</script>"""

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="120">
<title>Pipeline Dashboard — @@PROJECT_NAME@@</title>
<style>@@CSS@@</style>
</head>
<body>
  <main>
    <h1>&#128256; Pipeline Dashboard <span class="muted">&#8212; @@PROJECT_NAME@@</span></h1>
    <p class="muted">
      Actualizata automat dupa fiecare rulare CI/CD pe <code>main</code>
      &middot; se reincarca singura la 2 minute.
    </p>

    <section class="pipeline-combined">
      <h2>GitHub Actions <span class="tag">outer pipeline</span></h2>
      @@GITHUB_CHAIN@@

      <div id="v-conn" class="v-conn"></div>

      <div class="inner-section">
        <h3>&#8627; Jenkins <code>@@JENKINS_JOB@@</code> <span class="tag">inner pipeline</span></h3>
        <p class="muted">Ruleaza in interiorul nodului &bdquo;Jenkins (MDSSC + Build + Deploy)&rdquo;.</p>
        @@JENKINS_CHAIN@@
        <p class="muted">Build: <a href="@@BUILD_URL@@">@@BUILD_URL@@</a></p>
      </div>
    </section>

    <footer>
      Ultima actualizare: @@TIMESTAMP@@ UTC &middot;
      <a href="@@RUN_URL@@">vezi rularea completa pe GitHub Actions</a>
    </footer>
  </main>
@@CONNECTOR_SCRIPT@@
</body>
</html>
"""


def render(jenkins_job, build_url, run_url, timestamp, project_name):
    return (PAGE_TEMPLATE
            .replace('@@CSS@@', CSS)
            .replace('@@PROJECT_NAME@@', escape(project_name))
            .replace('@@GITHUB_CHAIN@@', chain_html(
                github_jobs(),
                anchor_predicate=lambda n: 'jenkins' in n['name'].lower(),
            ))
            .replace('@@JENKINS_CHAIN@@', chain_html(jenkins_stages()))
            .replace('@@JENKINS_JOB@@', escape(jenkins_job))
            .replace('@@BUILD_URL@@', escape(build_url))
            .replace('@@RUN_URL@@', escape(run_url))
            .replace('@@TIMESTAMP@@', timestamp)
            .replace('@@CONNECTOR_SCRIPT@@', CONNECTOR_SCRIPT))


def main():
    server = os.environ.get('GITHUB_SERVER_URL', 'https://github.com')
    repo = os.environ.get('GITHUB_REPOSITORY', '')
    run_id = os.environ.get('GITHUB_RUN_ID', '')

    html = render(
        project_name=os.environ.get('PROJECT_NAME', 'GreenCart MDSSC'),
        jenkins_job=os.environ.get('JENKINS_JOB', 'proiect-mdssc'),
        build_url=os.environ.get('BUILD_URL', '-'),
        run_url=f'{server}/{repo}/actions/runs/{run_id}',
        timestamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M'),
    )

    site_dir = os.environ.get('SITE_DIR', '_site')
    os.makedirs(site_dir, exist_ok=True)
    with open(os.path.join(site_dir, 'index.html'), 'w', encoding='utf-8') as handle:
        handle.write(html)
    print(f'Pagina live generata in {site_dir}/index.html')


if __name__ == '__main__':
    main()
