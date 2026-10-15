"""Run IV adapter v2 (fixes A and B, preview mode) on the full base set.

Tasks: the 408 base-set tasks plus tasks 83 and 110, whose control IV fails. Only the fixed adapter is used
(iv_adapter.py next to this file, imported read-only; only adapt() and reverse_shape() are called), and only in preview
mode, because saved plans exist only for the pilot. No Pulumi or Terraform command is run.

All paths are relative to this file (see README.md), and the environment variable RUNS can point to the run folders.
The two hashes below are those of the adapter file in my working folder (v1 and v2), which has other paths and
comments than iv_adapter.py here, so the first log line reports DIFFERENT for both hashes.

The adapter reads its inputs from the module-level constant PILOT (load_preview(), program_path()). For each task, this
driver points that attribute of the imported module to the task's run folder. This happens in memory only; the adapter
file is not changed.

IV check, unchanged from the original study (intent.rego from the original package, pass function from analyzer.py in
the original code):
    opa.exe eval -i <plan.json> -d <dataset>/<task>/intent.rego data
    pass = extract_validation_status(json.loads(out)['result'][0]['expressions'][0]['value'])

Run folder per task: pilot tasks use runs/pilot-aligned; ext tasks use the ext-w1-{a,b,c,d} folder whose
results_tf.csv holds the task. results_<lang>.csv is read from the same folder.
Base set: the rows of supervisor_opa_recheck.csv with listed_pass == "True" and recheck_lenient == "True".
Run set per language: the base tasks with preview_ok == "True" (eligible if also tf_opa == "pass"), plus 83 and 110
when their preview passed (not eligible, because their control IV fails).

Rows (full_results.csv / full_results_detail.csv)
  lang terraform,  variant CTRL / EMPTY             : every task (410). CTRL is the unchanged control plan file.
  lang terraform,  variant R-P1 / R-P2 / R-P3       : every task (410): the control plan cut to the variant's shape.
  lang typescript / python, variant P1/P2/P3id/P3src : adapter output in preview mode, for the run set.
  lang typescript / python, variant R-P1/R-P2/R-P3  : the same reverse-shape result as in the terraform rows, repeated
                                                     for each (task, lang) in the run set so that counts per language
                                                     can be read off directly.
verdict          = pass/fail of our OPA run on that input.
control_verdict  = tf_opa in results_tf.csv (our CTRL OPA run is checked against it, see "Run and sanity" in SUMMARY.md).
rule_vector_equal= the boolean rule leaves of the OPA value (path: true/false, absent = undefined) are the same as in
                   our CTRL run on the full control plan, and neither run had an OPA error.
false_rules      = leaves that are true in CTRL and false here; undefined_rules = leaves of CTRL that are absent here.

Outputs (all in results/full408_v2): full_results.csv, full_results_detail.csv, rule_vectors.json, run_meta.json,
run_log.txt, out/<task>-<lang>-preview-<variant>.json, out/<task>-tf-<shape>.json, out/<task>-EMPTY.json.
"""
import csv, hashlib, importlib.util, json, os, subprocess, sys, time, traceback
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool

sys.dont_write_bytecode = True   # importing the adapter should not leave a __pycache__ folder next to it
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

STUDY = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')     # iv-adapter/
ROOT = os.path.dirname(STUDY)                                              # repository root
PKG = ROOT + '/original-package/iac-research-without-agent'
sys.path.insert(0, PKG)
from iac_research.validation.analyzer import extract_validation_status  # pass function from the original code (unchanged)

DATASET = PKG + '/ground_truth/dataset'
OPA = ROOT + '/tools/opa-1.1.0/opa.exe'
RECHECK = ROOT + '/results/supervisor_opa_recheck.csv'
RUNS = os.environ.get('RUNS', ROOT + '/pipeline/runs').replace('\\', '/')
FOLDERS = ('pilot-aligned', 'ext-w1-a', 'ext-w1-b', 'ext-w1-c', 'ext-w1-d')
ADAPTER = STUDY + '/iv_adapter.py'
ADAPTER_SHA_PILOT = '98a53d94c75c931670efcb1d81474dd650a7dbc6cbd39ab54316cbcc4bfcd8b4'   # v1, used for the pilot and full408
ADAPTER_SHA_V2 = '1d9f6f26e0316ecc9303c4b73af4c18d5a2176e6c298afeabfbfed657c0044d2'      # v2, see "v2" in CHANGES.md
HERE = STUDY + '/results/full408_v2'
OUT = HERE + '/out'
VARIANTS = ('P1', 'P2', 'P3id', 'P3src')
SHAPES = ('R-P1', 'R-P2', 'R-P3')
LANGS = ('typescript', 'python')
EXTRA = ('83', '110')
MODE = 'preview'
N_PROC = 16
N_OPA = 16

LOG = []


def log(*a):
    s = ' '.join(str(x) for x in a)
    print(s, flush=True)
    LOG.append(s)


def sha256(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def read_rows(p):
    return list(csv.DictReader(open(p, encoding='utf-8')))


def dump(obj, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=1)


# ------------------------------------------------------------------------------------------- index
def build_index():
    base = [r['task'] for r in read_rows(RECHECK)
            if r['listed_pass'] == 'True' and r['recheck_lenient'] == 'True']
    tf, holders = {}, {}
    for f in FOLDERS:
        for r in read_rows(f'{RUNS}/{f}/results_tf.csv'):
            holders.setdefault(r['task'], []).append(f)
    for t, fs in holders.items():
        f = 'pilot-aligned' if 'pilot-aligned' in fs else sorted(fs)[0]
        if len(fs) > 1:
            log(f'task {t} in several results_tf.csv: {fs} -> {f}')
        tf[t] = dict(next(r for r in read_rows(f'{RUNS}/{f}/results_tf.csv') if r['task'] == t), folder=f)
    pu = {lang: {} for lang in LANGS}
    for lang in LANGS:
        for f in FOLDERS:
            for r in read_rows(f'{RUNS}/{f}/results_{lang}.csv'):
                if tf.get(r['task'], {}).get('folder') == f:
                    pu[lang][r['task']] = r
    return base, tf, pu


# ------------------------------------------------------------------------------------------- build (worker processes)
_MOD = None


def _init_worker():
    global _MOD
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('ivad_fixed', ADAPTER)
    _MOD = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(_MOD)


def build_adapter_job(job):
    """job = (task, folder, lang). Write the four preview-mode variants and return (path, notes, error) per variant."""
    task, folder, lang = job
    _MOD.PILOT = f'{RUNS}/{folder}'          # in memory only, see the module docstring
    out = {}
    for variant in VARIANTS:
        path = f'{OUT}/{task}-{lang}-{MODE}-{variant}.json'
        try:
            plan, notes = _MOD.adapt(task, lang, MODE, variant)
            dump(plan, path)
            out[variant] = (path, ';'.join(dict.fromkeys(notes)), '')
        except Exception as e:
            out[variant] = (None, '', 'adapter: ' + ''.join(traceback.format_exception_only(type(e), e)).strip()[:300])
    return (task, lang, out, sorted(_MOD.UNRESOLVED), sorted(_MOD.DROPPED))


def build_shape_job(job):
    """job = (task, folder). Write the R-P1/R-P2/R-P3 shapes of the control plan and the EMPTY input."""
    task, folder = job
    cp = f'{RUNS}/{folder}/{task}/terraform/plan.json'
    ctrl = json.load(open(cp, encoding='utf-8'))
    out = {}
    for shape in SHAPES:
        path = f'{OUT}/{task}-tf-{shape}.json'
        try:
            dump(_MOD.reverse_shape(ctrl, shape), path)
            out[shape] = (path, '')
        except Exception as e:
            out[shape] = (None, 'reverse_shape: ' + repr(e)[:300])
    ep = f'{OUT}/{task}-EMPTY.json'
    dump({}, ep)
    out['EMPTY'] = (ep, '')
    out['CTRL'] = (cp, '')
    return task, out


# ------------------------------------------------------------------------------------------- OPA
def bool_leaves(v, path=''):
    if isinstance(v, bool):
        yield path, v
    elif isinstance(v, dict):
        for k, x in v.items():
            yield from bool_leaves(x, path + '/' + str(k))


def opa(job):
    task, path = job
    p = subprocess.run([OPA, 'eval', '-i', path, '-d', f'{DATASET}/{task}/intent.rego', 'data'],
                       capture_output=True, text=True)
    try:
        val = json.loads(p.stdout)['result'][0]['expressions'][0]['value']
    except Exception:
        return {'pass': False, 'error': 'opa: ' + (p.stderr or p.stdout)[:300].replace('\n', ' '), 'bools': {}}
    return {'pass': bool(extract_validation_status(val)), 'error': '', 'bools': dict(bool_leaves(val))}


def rule_diff(ctrl_b, b):
    out = []
    for k in sorted(set(ctrl_b) | set(b)):
        c, a = ctrl_b.get(k, 'u'), b.get(k, 'u')
        if c != a:
            out.append(f"{k.rsplit('/', 1)[-1]}:{str(c)[0]}->{str(a)[0]}")
    return ';'.join(out)


# ------------------------------------------------------------------------------------------- main
def main():
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    sha0 = sha256(ADAPTER)
    log(f'adapter: {ADAPTER} sha256={sha0} (v2 {ADAPTER_SHA_V2}: {"same" if sha0 == ADAPTER_SHA_V2 else "DIFFERENT"}; '
        f'v1 {ADAPTER_SHA_PILOT}: {"same" if sha0 == ADAPTER_SHA_PILOT else "DIFFERENT"})')
    base, tf, pu = build_index()
    tasks = [t for t in base] + [t for t in EXTRA if t in tf and t not in base]
    log(f'base tasks {len(base)}; all tasks run (CTRL/EMPTY/R-shapes) {len(tasks)}')
    missing_plan = [t for t in tasks if not os.path.exists(f"{RUNS}/{tf[t]['folder']}/{t}/terraform/plan.json")]
    log('tasks without terraform/plan.json:', missing_plan)
    tasks = [t for t in tasks if t not in missing_plan]
    run_set, eligible = {}, {}
    for lang in LANGS:
        run_set[lang] = [t for t in tasks if pu[lang].get(t, {}).get('preview_ok') == 'True'
                         and os.path.exists(f"{RUNS}/{tf[t]['folder']}/{t}/preview-{lang}.json")]
        eligible[lang] = [t for t in run_set[lang] if t in base and tf[t]['tf_opa'] == 'pass']
        skipped = [t for t in base if t not in run_set[lang]]
        log(f'{lang}: run set {len(run_set[lang])} (eligible {len(eligible[lang])}, non-eligible '
            f'{[t for t in run_set[lang] if t not in eligible[lang]]}); base tasks skipped (preview failed) {len(skipped)}')

    # ---------------------------------------------------------------- 1. build every input file
    adapter_jobs = [(t, tf[t]['folder'], lang) for lang in LANGS for t in run_set[lang]]
    shape_jobs = [(t, tf[t]['folder']) for t in tasks]
    with Pool(N_PROC, initializer=_init_worker) as pool:
        shape_res = pool.map(build_shape_job, shape_jobs, chunksize=4)
        adapter_res = pool.map(build_adapter_job, adapter_jobs, chunksize=2)
    t_build = time.time() - t0
    log(f'built inputs: {len(shape_jobs)} tasks x (3 shapes + EMPTY), {len(adapter_jobs)} (task, lang) x 4 variants '
        f'({t_build:.0f}s)')
    unresolved, dropped = set(), set()
    files = {}      # key -> (task, path, notes, build_error)
    for task, out in shape_res:
        for k, (path, err) in out.items():
            files[(k, task)] = (task, path, '', err)
    for task, lang, out, unr, drp in adapter_res:
        unresolved.update(unr)
        dropped.update(drp)
        for variant, (path, notes, err) in out.items():
            files[(lang, task, variant)] = (task, path, notes, err)
    build_errors = {k: v[3] for k, v in files.items() if v[3]}
    log('build errors:', len(build_errors), list(build_errors.items())[:20])

    # ---------------------------------------------------------------- 2. OPA on every file
    keys = [k for k, v in files.items() if v[1]]
    t1 = time.time()
    with ThreadPoolExecutor(max_workers=N_OPA) as ex:
        res = list(ex.map(opa, [(files[k][0], files[k][1]) for k in keys]))
    t_opa = time.time() - t1
    R = dict(zip(keys, res))
    for k, v in files.items():
        if not v[1]:
            R[k] = {'pass': False, 'error': v[3], 'bools': {}}
    log(f'OPA runs: {len(keys)} ({t_opa:.0f}s, {N_OPA} threads)')

    # ---------------------------------------------------------------- 3. rows
    rows, detail, vectors = [], [], {}

    def add(task, lang, variant, key, elig):
        r, c = R[key], R[('CTRL', task)]
        if variant == 'CTRL':
            rve = not r['error']
        else:
            rve = r['bools'] == c['bools'] and not r['error'] and not c['error']
        row = {'task': task, 'lang': lang, 'variant': variant,
               'verdict': 'pass' if r['pass'] else 'fail', 'control_verdict': tf[task]['tf_opa'],
               'rule_vector_equal': rve,
               'false_rules': ';'.join(k for k, v in r['bools'].items() if v is False and c['bools'].get(k) is True),
               'undefined_rules': ';'.join(k for k in c['bools'] if k not in r['bools']),
               'error': r['error']}
        rows.append(row)
        path, notes = files[key][1], files[key][2]
        detail.append(dict(row, mode=(MODE if lang in LANGS and variant in VARIANTS else 'control'),
                           eligible=elig, base=task in base, folder=tf[task]['folder'],
                           rule_diff=rule_diff(c['bools'], r['bools']), notes=notes or '',
                           out_file=(path or '').replace(STUDY + '/', '')))
        vectors['|'.join([task, lang, variant])] = r['bools']

    for t in tasks:
        for v in ('CTRL', 'EMPTY') + SHAPES:
            add(t, 'terraform', v, (v, t), '')
    for lang in LANGS:
        for t in run_set[lang]:
            elig = t in eligible[lang]
            for v in VARIANTS:
                add(t, lang, v, (lang, t, v), elig)
            for s in SHAPES:
                add(t, lang, s, (s, t), elig)

    cols = ['task', 'lang', 'variant', 'verdict', 'control_verdict', 'rule_vector_equal', 'false_rules',
            'undefined_rules', 'error']
    with open(HERE + '/full_results.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    with open(HERE + '/full_results_detail.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(detail[0].keys()))
        w.writeheader()
        w.writerows(detail)
    json.dump(vectors, open(HERE + '/rule_vectors.json', 'w', encoding='utf-8'), indent=0, sort_keys=True)

    # ---------------------------------------------------------------- 4. sanity lines
    ctrl_ok = [t for t in tasks if R[('CTRL', t)]['pass'] == (tf[t]['tf_opa'] == 'pass')]
    opa_errors = {'|'.join(k): R[k]['error'] for k in R if R[k]['error']}
    sha1 = sha256(ADAPTER)
    total = time.time() - t0
    log(f'CTRL (our OPA run) agrees with results_tf.csv tf_opa: {len(ctrl_ok)}/{len(tasks)}; '
        f'disagree: {[t for t in tasks if t not in ctrl_ok]}')
    log('EMPTY input passes (vacuous):', [t for t in tasks if R[('EMPTY', t)]['pass']])
    log('errors (build or OPA):', len(opa_errors), list(opa_errors.items())[:20])
    log('rows', len(rows), f'(total {total:.0f}s)')
    log(f'unresolved Pulumi names: {sorted(unresolved)}')
    log(f'Pulumi keys without a Terraform attribute: {sorted(dropped)}')
    log(f'adapter sha256 after run: {sha1} ({"unchanged" if sha1 == sha0 else "CHANGED"})')
    meta = {'adapter': ADAPTER, 'adapter_sha256_before': sha0, 'adapter_sha256_after': sha1,
            'adapter_sha256_pilot': ADAPTER_SHA_PILOT, 'adapter_sha256_v2_expected': ADAPTER_SHA_V2, 'mode': MODE,
            'n_tasks': len(tasks), 'n_base': len(base), 'run_set': {l: len(run_set[l]) for l in LANGS},
            'eligible': {l: len(eligible[l]) for l in LANGS},
            'non_eligible_run': {l: [t for t in run_set[l] if t not in eligible[l]] for l in LANGS},
            'skipped_preview_failed': {l: len([t for t in base if t not in run_set[l]]) for l in LANGS},
            'opa_calls': len(keys), 'build_seconds': round(t_build, 1), 'opa_seconds': round(t_opa, 1),
            'total_seconds': round(total, 1), 'n_proc': N_PROC, 'n_opa_threads': N_OPA,
            'ctrl_agree': len(ctrl_ok), 'ctrl_disagree': [t for t in tasks if t not in ctrl_ok],
            'empty_pass': [t for t in tasks if R[('EMPTY', t)]['pass']], 'errors': opa_errors,
            'build_errors': {'|'.join(k): v for k, v in build_errors.items()},
            'unresolved': sorted(unresolved), 'dropped': sorted(dropped), 'rows': len(rows)}
    json.dump(meta, open(HERE + '/run_meta.json', 'w', encoding='utf-8'), indent=1)
    open(HERE + '/run_log.txt', 'w', encoding='utf-8').write('\n'.join(LOG) + '\n')


if __name__ == '__main__':
    main()
