"""Reproduces the OPA results of the original package with the pass function from the original code.

For every task, the plan from the original package (tfplan.json) and its intent.rego are evaluated with
`opa eval ... data`, the same command as in the original code, and the result is passed to extract_validation_status().
The outcome is compared with the 'Successful Directories' list in the package. A stricter criterion (every boolean
in the OPA result is true) is reported as well.

Output: results/supervisor_opa_recheck.csv
"""
import csv, glob, json, os, subprocess, sys, winreg

LAB = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(LAB, '..', 'original-package', 'iac-research-without-agent')
sys.path.insert(0, PKG)
from iac_research.validation.analyzer import extract_validation_status  # pass function from the original code

paths = []
for root, key in [(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'),
                  (winreg.HKEY_CURRENT_USER, 'Environment')]:
    with winreg.OpenKey(root, key) as k:
        paths.append(os.path.expandvars(winreg.QueryValueEx(k, 'Path')[0]))
env = dict(os.environ, PATH=';'.join(paths))
# By default OPA 1.1.0, the version of the original study. To compare with another OPA binary, pass it as the
# first argument, e.g. python recheck_supervisor_opa.py opa (output then: results/supervisor_opa_recheck_opa.csv)
OPA = sys.argv[1] if len(sys.argv) > 1 else os.path.join(LAB, '..', 'tools', 'opa-1.1.0', 'opa.exe')
OUT = 'supervisor_opa_recheck.csv' if len(sys.argv) <= 1 else 'supervisor_opa_recheck_' + os.path.basename(OPA).replace('.exe', '') + '.csv'

listed, section = set(), None
for line in open(os.path.join(PKG, 'ground_truth', 'tracking', 'opa_rego_fixes', 'opa_results_summary_improved.txt'), encoding='utf-8'):
    line = line.strip()
    if line.endswith(':'): section = line[:-1]
    elif line.startswith('- ') and section == 'Successful Directories': listed.add(line[2:])


def all_bools(v):
    if isinstance(v, bool): yield v
    elif isinstance(v, dict):
        for x in v.values(): yield from all_bools(x)


rows = []
for d in sorted(glob.glob(os.path.join(PKG, 'ground_truth', 'dataset', '*')), key=lambda p: int(os.path.basename(p))):
    t = os.path.basename(d)
    if not os.path.exists(os.path.join(d, 'tfplan.json')):
        rows.append({'task': t, 'listed_pass': t in listed, 'recheck_lenient': '', 'recheck_strict': '', 'note': 'no tfplan.json'}); continue
    p = subprocess.run([OPA, 'eval', '-i', 'tfplan.json', '-d', 'intent.rego', 'data'], cwd=d, env=env,
                       capture_output=True, text=True)
    try:
        val = json.loads(p.stdout)['result'][0]['expressions'][0]['value']
    except Exception:
        rows.append({'task': t, 'listed_pass': t in listed, 'recheck_lenient': False, 'recheck_strict': False, 'note': p.stderr[:150]}); continue
    b = list(all_bools(val))
    rows.append({'task': t, 'listed_pass': t in listed, 'recheck_lenient': extract_validation_status(val),
                 'recheck_strict': bool(b) and all(b), 'note': ''})

with open(os.path.join(LAB, '..', 'results', OUT), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

n = len(rows)
lp = sum(r['listed_pass'] for r in rows)
len_ = sum(r['recheck_lenient'] is True for r in rows)
st = sum(r['recheck_strict'] is True for r in rows)
mismatch = [r['task'] for r in rows if r['listed_pass'] and r['recheck_lenient'] is not True]
print(f'{n} tasks | listed as passing in the package: {lp} | recheck (their function): {len_} | recheck (strict): {st}')
print(f'listed as passing but not passing now with their function: {len(mismatch)} ->', ' '.join(mismatch[:40]))
lenient_not_strict = [r['task'] for r in rows if r['recheck_lenient'] is True and r['recheck_strict'] is not True]
print(f'passing with their criterion but not with the strict one: {len(lenient_not_strict)} ->', ' '.join(lenient_not_strict[:40]))
