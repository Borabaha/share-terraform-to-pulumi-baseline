"""Builds the task table and picks the pilot sample.

Collects a few features for each of the 458 IaC-Eval tasks in the original package: difficulty, line count, use of
module/data/count, and whether the Terraform plan and the OPA check passed on LocalStack in the original study.
Then it picks a stratified pilot sample of 30 tasks.

Outputs: results/tasks.csv, pipeline/tasks/pilot_tasks.txt
"""
import csv, glob, os, random, re

LAB = os.path.dirname(os.path.abspath(__file__))
GT = os.path.join(LAB, '..', 'original-package', 'iac-research-without-agent', 'ground_truth')
csv.field_size_limit(10**9)

# Terraform init and plan results from the original package. The fix rounds are read in order, so the last
# result for a task is the one that counts.
tf_pass = {}
for i in range(1, 5):
    with open(os.path.join(GT, 'tracking', 'terraform_init_plan_fixes', f'terraform_results_{i}.csv'), encoding='utf-8') as f:
        for r in csv.DictReader(f):
            tf_pass[r['Directory']] = r['Init Success'] == 'True' and r['Plan Success'] == 'True'

# OPA results from the original package, with the corrected Rego rules
opa_pass, section = set(), None
for line in open(os.path.join(GT, 'tracking', 'opa_rego_fixes', 'opa_results_summary_improved.txt'), encoding='utf-8'):
    line = line.strip()
    if line.endswith(':'):
        section = line[:-1]
    elif line.startswith('- ') and section == 'Successful Directories':
        opa_pass.add(line[2:])

rows = []
for d in sorted(glob.glob(os.path.join(GT, 'dataset', '*')), key=lambda p: int(os.path.basename(p))):
    tid = os.path.basename(d)
    tf = open(os.path.join(d, 'main.tf'), encoding='utf-8').read()
    readme = open(os.path.join(d, 'README.md'), encoding='utf-8').read()
    m = re.search(r'## Difficulty\s+(\d+)', readme)
    rows.append({
        'task': tid,
        'difficulty': int(m.group(1)) if m else '',
        'loc': tf.count('\n') + 1,
        'n_resources': len(re.findall(r'^\s*resource\s+"', tf, re.M)),
        'has_module': int(bool(re.search(r'^\s*module\s+"', tf, re.M))),
        'has_data': int(bool(re.search(r'^\s*data\s+"', tf, re.M))),
        'has_count': int(bool(re.search(r'\bcount\s*=', tf))),
        'has_provider_block': int(bool(re.search(r'^\s*provider\s+"', tf, re.M))),
        'supervisors_tf_plan_pass': int(tf_pass.get(tid, False)),
        'supervisors_opa_pass': int(tid in opa_pass),
    })

with open(os.path.join(LAB, '..', 'results', 'tasks.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)

ok = [r for r in rows if r['supervisors_tf_plan_pass'] and r['supervisors_opa_pass']]
print(f"{len(rows)} tasks; plan passed for the supervisors {sum(r['supervisors_tf_plan_pass'] for r in rows)}, "
      f"OPA passed {len(opa_pass)}, both {len(ok)}")

# Stratified pilot from the tasks that passed both checks in the original study: 4 tasks without modules per
# difficulty level, 5 tasks with modules and 1 task with count. The seed is fixed, so the sample can be repeated.
rng = random.Random(20261005)
pilot = []
for lvl in sorted({r['difficulty'] for r in ok}):
    pool = [r for r in ok if r['difficulty'] == lvl and not r['has_module']]
    pilot += rng.sample(pool, min(4, len(pool)))
pilot += rng.sample([r for r in ok if r['has_module'] and r not in pilot], 5)
pilot += rng.sample([r for r in ok if r['has_count'] and not r['has_module'] and r not in pilot], 1)
pilot.sort(key=lambda r: int(r['task']))
open(os.path.join(LAB, 'tasks', 'pilot_tasks.txt'), 'w').write('\n'.join(r['task'] for r in pilot) + '\n')
print('pilot:', len(pilot), 'tasks ->', ' '.join(r['task'] for r in pilot))
print('difficulty distribution:', {l: sum(1 for r in pilot if r['difficulty'] == l) for l in range(1, 7)},
      '| module', sum(r['has_module'] for r in pilot), '| data', sum(r['has_data'] for r in pilot),
      '| count', sum(r['has_count'] for r in pilot))
