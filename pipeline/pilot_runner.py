"""Baseline runner: Terraform (control group) and `pulumi convert` (deterministic baseline), run against the AWS
emulator on localhost:4566. All runs used LocalStack.

Stages for each task:
  tf       Control group, as in the paper: tflocal init and plan on the original main.tf, save plan.json and
           check it with OPA against the intent.rego of the original package.
  convert  L0: pulumi convert --from terraform --language <lang>; records exit code, warnings and notImplemented calls.
  compile  L1: compile or syntax check (TypeScript: tsc --noEmit, Python: py_compile).
  preview  L2: pulumi preview --json against the emulator, with emulator-stack-config.yaml (the settings pulumilocal writes).
  equiv    L3: compares the managed resources in the Terraform plan with the resources in the Pulumi preview (type and count).

Usage:
  python pilot_runner.py tf      --run pilot
  python pilot_runner.py setup   --run pilot --lang typescript      # installs the shared dependencies once
  python pilot_runner.py pulumi  --run pilot --lang typescript      # convert + compile + preview + equiv
Task list: --tasks tasks/pilot_tasks.txt (default) or --tasks all
"""
import argparse, csv, glob, json, os, re, shutil, subprocess, sys, time, urllib.request, winreg
from collections import Counter

LAB = os.path.dirname(os.path.abspath(__file__))
DATASET = os.path.join(LAB, '..', 'original-package', 'iac-research-without-agent', 'ground_truth', 'dataset')
VENV = os.path.join(os.environ['USERPROFILE'], 'venvs', 'iac', 'Scripts')
PULUMI = r'C:\Program Files (x86)\Pulumi\pulumi.exe'
EMU = 'http://localhost:4566'
# OPA 1.1.0, the version used in the paper. It lives under tools/ and is not in git.
OPA = os.path.join(LAB, '..', 'tools', 'opa-1.1.0', 'opa.exe')
TIMEOUT = 600


def build_env():
    """Build the environment for all subprocesses.

    PATH is read from the registry, so tools installed after this process started are still found.
    """
    paths = []
    for root, key in [(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'),
                      (winreg.HKEY_CURRENT_USER, 'Environment')]:
        with winreg.OpenKey(root, key) as k:
            paths.append(os.path.expandvars(winreg.QueryValueEx(k, 'Path')[0]))
    env = dict(os.environ)
    env['PATH'] = ';'.join(paths + [VENV, os.path.dirname(PULUMI)])
    env.update({
        'AWS_ACCESS_KEY_ID': 'test', 'AWS_SECRET_ACCESS_KEY': 'test', 'AWS_DEFAULT_REGION': 'us-east-1',
        # S3_HOSTNAME is left unset, so tflocal uses its default (s3.localhost.localstack.cloud), as in the original study.
        'AWS_ENDPOINT_URL': EMU,
        # In parallel runs each shard needs its own cache, set with THESIS_TF_PLUGIN_CACHE_DIR. With one shared cache a shard
        # can rewrite a plugin while another shard runs it; the plugin is then half-written and fails with
        # "%1 is not a valid Win32 application".
        'TF_PLUGIN_CACHE_DIR': os.environ.get('THESIS_TF_PLUGIN_CACHE_DIR') or os.path.join(os.environ['USERPROFILE'], '.terraform.d', 'plugin-cache'),
        'TF_IN_AUTOMATION': '1', 'CHECKPOINT_DISABLE': '1',
        # 203 tasks set profile = "admin-1" in the provider block, a local AWS profile from the original study.
        # We provide a profile with that name and fake credentials, so main.tf stays unchanged.
        'AWS_SHARED_CREDENTIALS_FILE': os.path.join(LAB, 'config', 'emu-aws-credentials'),
        'AWS_CONFIG_FILE': os.path.join(LAB, 'config', 'emu-aws-config'),
        # Provider versions of the original study (aws 5.90.0 / 4.67.0, archive 2.7.0, kubernetes 2.36.0),
        # pinned in config/terraform-pinned.tfrc.
        'TF_CLI_CONFIG_FILE': os.path.join(LAB, 'config', 'terraform-pinned.tfrc'),
        'PULUMI_CONFIG_PASSPHRASE': 'thesis-local', 'PULUMI_SKIP_UPDATE_CHECK': 'true',
        # Stay on the pinned versions: a missing plugin makes the run fail instead of downloading the newest version.
        'PULUMI_DISABLE_AUTOMATIC_PLUGIN_ACQUISITION': 'true',
    })
    return env


ENV = build_env()


def run(cmd, cwd, log=None, timeout=TIMEOUT, env=None):
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=cwd, env=env or ENV, capture_output=True, text=True,
                           encoding='utf-8', errors='replace', timeout=timeout)
        rc, out, err = p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        rc, out, err = 'timeout', e.stdout or '', (e.stderr or '') + f'\nTIMEOUT after {timeout}s'
    dt = round(time.time() - t0, 1)
    if log:
        with open(log, 'a', encoding='utf-8') as f:
            f.write(f'$ {" ".join(map(str, cmd))}\n[rc={rc}, {dt}s]\n--- stdout ---\n{out}\n--- stderr ---\n{err}\n\n')
    return rc, out, err, dt


def ministack_reset():
    """Reset the emulator state before a task.

    For LocalStack this is the same reset call as executor.py in the original code; MiniStack has its own endpoint.
    """
    for path in ('/_localstack/state/reset', '/_ministack/reset'):
        try:
            urllib.request.urlopen(urllib.request.Request(f'{EMU}{path}', method='POST'), timeout=30).read()
            return path
        except Exception:
            continue
    print('  ! emulator reset failed')


def tasks_from(arg):
    if arg == 'all':
        return sorted((os.path.basename(p) for p in glob.glob(os.path.join(DATASET, '*'))), key=int)
    return [t.strip() for t in open(os.path.join(LAB, arg)) if t.strip()]


# VPC module version of the original study: in terraform_results_1.csv all 47 module tasks show
# "Downloading registry.terraform.io/terraform-aws-modules/vpc/aws 5.19.0", and the plan trace also shows 5.19.0.
MODULE_PIN = '5.19.0'
# As in copy_structure of the original code, the whole task folder is copied. Only old plan outputs are left out
# (run_validation in the original code also deletes tfplan / tfplan.json before a run).
SKIP_FILES = {'tfplan', 'tfplan.json', '.terraform.lock.hcl'}


def write_input(task, dest_dir):
    """Copy the task folder to dest_dir as the original code does. The only input change is the VPC module pin.

    47 tasks call the terraform-aws-modules/vpc module without a version. Its latest version today needs aws >= 6.28,
    which conflicts with the tasks' `~> 5.75` constraint. In the working copy we pin it to MODULE_PIN.
    main.tf is written as bytes so that Windows does not turn LF into CRLF. Returns True when main.tf was changed.
    """
    src = os.path.join(DATASET, task)
    for name in os.listdir(src):
        if name in SKIP_FILES or name == '.terraform':
            continue
        s, d = os.path.join(src, name), os.path.join(dest_dir, name)
        if os.path.isdir(s):
            shutil.rmtree(d, ignore_errors=True)
            shutil.copytree(s, d)
        elif name != 'main.tf':
            shutil.copyfile(s, d)
    raw = open(os.path.join(src, 'main.tf'), 'rb').read()
    # No module block in the dataset has a version, so the version line goes directly below the source line.
    patched = re.sub(rb'(module\s+"[^"]+"\s*\{\s*\n([ \t]*)source\s*=\s*"terraform-aws-modules/vpc/aws"[^\n]*\n)',
                     lambda m: m.group(1) + m.group(2) + f'version = "{MODULE_PIN}"\n'.encode(), raw)
    open(os.path.join(dest_dir, 'main.tf'), 'wb').write(patched)
    return patched != raw


def first_error(text):
    for line in text.splitlines():
        s = line.strip().lstrip('│').strip()
        if s.startswith('Error') or s.startswith('error:') or 'error TS' in s:
            return s[:300]
    return ''


PKG_ROOT = os.path.join(LAB, '..', 'original-package', 'iac-research-without-agent')
sys.path.insert(0, PKG_ROOT)
from iac_research.validation.analyzer import extract_validation_status  # pass function from the original code


def opa_valid(plan_json, rego):
    """Check a plan against intent.rego the same way as the original code.

    Runs `opa eval -i <plan> -d intent.rego data` and passes the result to extract_validation_status().
    The second return value is a stricter check (every boolean in the package is true), used only for comparison.
    """
    rc, out, err, _ = run([OPA, 'eval', '-i', plan_json, '-d', rego, 'data'], cwd=LAB)
    if rc != 0:
        return 'error', 'error'
    try:
        val = json.loads(out)['result'][0]['expressions'][0]['value']
    except Exception:
        return 'undefined', 'undefined'

    def bools(v):
        if isinstance(v, bool): yield v
        elif isinstance(v, dict):
            for x in v.values(): yield from bools(x)
    b = list(bools(val))
    strict = 'pass' if b and all(b) else 'fail'
    return ('pass' if extract_validation_status(val) else 'fail'), strict


# ---------------------------------------------------------------- Terraform (control group)
def stage_tf(run_dir, tasks):
    """Control group: run the original chain (tflocal init, plan, OPA) on the reference main.tf, as in the paper."""
    work = os.path.join(run_dir, '_tfwork')          # one shared working folder, so the AWS provider (~800 MB) is unpacked once
    os.makedirs(work, exist_ok=True)
    rows = []
    for i, t in enumerate(tasks, 1):
        src = os.path.join(DATASET, t)
        out = os.path.join(run_dir, t, 'terraform'); os.makedirs(out, exist_ok=True)
        log = os.path.join(out, 'log.txt'); open(log, 'w').close()
        # Clear everything except .terraform (downloaded plugins), so that a helper file left by the previous task
        # cannot stand in for a missing file of the next task.
        for name in os.listdir(work):
            if name == '.terraform':
                continue
            pth = os.path.join(work, name)
            shutil.rmtree(pth) if os.path.isdir(pth) else os.remove(pth)
        patched = write_input(t, work)
        ministack_reset()
        tfl = [os.path.join(VENV, 'python.exe'), os.path.join(VENV, 'tflocal')]
        # init gets 3 attempts in case of network timeouts during provider installation.
        for attempt in range(3):
            rc_i, o_i, e_i, d_i = run(tfl + ['init', '-input=false', '-no-color'], work, log)
            if rc_i == 0 or 'Failed to install provider' not in (e_i + o_i):
                break
            time.sleep(10)
        rc_p, o_p, e_p, d_p = ('skip', '', '', 0)
        plan_ok, opa, opa_strict = False, 'skip', 'skip'
        if rc_i == 0:
            rc_p, o_p, e_p, d_p = run(tfl + ['plan', '-input=false', '-no-color', '-out', 'tf.tfplan'], work, log)
            if rc_p == 0:
                rc_s, o_s, e_s, _ = run(tfl + ['show', '-json', 'tf.tfplan'], work, log)
                if rc_s == 0:
                    pj = os.path.join(out, 'plan.json')
                    open(pj, 'w', encoding='utf-8').write(o_s)
                    plan_ok = True
                    opa, opa_strict = opa_valid(pj, os.path.join(src, 'intent.rego'))
        aws_ver = (re.search(r'Installed hashicorp/aws v([0-9.]+)', o_i) or
                   re.search(r'Using previously-installed hashicorp/aws v([0-9.]+)', o_i))
        row = {'task': t, 'input_patched': patched, 'tf_init': rc_i == 0, 'tf_plan': plan_ok, 'tf_opa': opa,
               'tf_opa_strict': opa_strict,
               'aws_provider': aws_ver.group(1) if aws_ver else '',
               'vs_supervisor_plan': compare_with_supervisor_plan(os.path.join(out, 'plan.json'), t) if plan_ok else '',
               'tf_error': '' if plan_ok else first_error(e_i + e_p + o_p), 'tf_seconds': round(d_i + d_p, 1)}
        json.dump(row, open(os.path.join(out, 'result.json'), 'w'), indent=1)
        rows.append(row)
        print(f'[{i}/{len(tasks)}] {t}: init={row["tf_init"]} plan={row["tf_plan"]} opa={opa} {row["tf_error"][:90]}', flush=True)
    write_csv(os.path.join(run_dir, 'results_tf.csv'), rows)


# ---------------------------------------------------------------- Pulumi (baseline)
LANG_DIR = {'typescript': 'pulumi-ts', 'python': 'pulumi-py', 'yaml': 'pulumi-yaml', 'go': 'pulumi-go'}


def stage_setup(run_dir, lang):
    """Install the shared dependencies once per run: one node_modules in the run folder for TypeScript, one venv for Python."""
    if lang == 'typescript':
        # Our own choice: @pulumi/aws 6.72.0 is built on Terraform AWS 5.90.1, the closest published match to
        # aws 5.90.0 in the original study. For the other providers we also chose the Pulumi packages built from
        # the Terraform versions of the original study:
        #   archive 0.3.2 = TF archive 2.7.0, null 0.0.10 = TF null 3.2.3, random 4.18.0 = TF random 3.7.1
        pkg = {'name': 'shared', 'private': True,
               'dependencies': {'@pulumi/pulumi': '^3.200.0', '@pulumi/aws': '6.72.0', '@pulumi/std': '2.3.2',
                                '@pulumi/command': '1.2.1', '@pulumi/random': '4.18.0', '@pulumi/archive': '0.3.2',
                                '@pulumi/null': '0.0.10', 'typescript': '^5.6.0', '@types/node': '^20.0.0'}}
        json.dump(pkg, open(os.path.join(run_dir, 'package.json'), 'w'), indent=1)
        rc, out, err, dt = run(['npm.cmd', 'install', '--no-audit', '--no-fund'], run_dir, os.path.join(run_dir, 'setup.log'))
        print('npm install rc', rc, f'{dt}s', err[-500:])
    elif lang == 'python':
        venv = os.path.join(run_dir, '.venv-py')
        run([sys.executable, '-m', 'venv', venv], run_dir)
        rc, out, err, dt = run([os.path.join(venv, 'Scripts', 'python.exe'), '-m', 'pip', 'install', '-q',
                                'pulumi>=3.200,<4', 'pulumi-aws==6.72.0', 'pulumi-std==2.3.2', 'pulumi-command==1.2.1',
                                'pulumi-random==4.18.0', 'pulumi-archive==0.3.2', 'pulumi-null==0.0.10'], run_dir, os.path.join(run_dir, 'setup.log'))
        print('pip install rc', rc, f'{dt}s', err[-500:])


def count_not_implemented(folder):
    n = 0
    for f in glob.glob(os.path.join(folder, '**', '*.*'), recursive=True):
        if 'node_modules' in f or not f.endswith(('.ts', '.py', '.yaml', '.go')):
            continue
        text = open(f, encoding='utf-8', errors='replace').read()
        # Count calls only, not the definition of the helper function the converter adds (function/def/func ...).
        n += len(re.findall(r'(?<!function )(?<!def )(?<!func )not[_]?[iI]mplemented\(', text))
    return n


def prepare_project(proj, lang, run_dir, task):
    """Add the emulator stack config and point the project to the shared dependencies."""
    py = os.path.join(proj, 'Pulumi.yaml')
    text = open(py, encoding='utf-8').read()
    text = re.sub(r'^name:.*$', f'name: task-{task}', text, count=1, flags=re.M)
    if lang == 'python':
        venv = os.path.join(run_dir, '.venv-py').replace('\\', '/')
        text = re.sub(r'^runtime:.*(\n  .*)*', f'runtime:\n  name: python\n  options:\n    virtualenv: {venv}', text, count=1, flags=re.M)
    open(py, 'w', encoding='utf-8').write(text)
    shutil.copy(os.path.join(LAB, 'config', 'emulator-stack-config.yaml'), os.path.join(proj, 'Pulumi.emu.yaml'))


def compare_with_supervisor_plan(our_plan_json, task):
    """Compare our plan with the plan in the original package (tfplan.json).

    Compared: resource addresses and actions, the set of endpoints and the provider regions.
    """
    sup = os.path.join(DATASET, task, 'tfplan.json')
    if not os.path.exists(sup):
        return 'no_supervisor_plan'

    def sig(path):
        p = json.load(open(path, encoding='utf-8'))
        res = sorted((r['address'], ','.join(r['change']['actions'])) for r in p.get('resource_changes', []))
        eps, regions = set(), {}
        for key, v in p.get('configuration', {}).get('provider_config', {}).items():
            if v.get('name') != 'aws':
                continue
            if v.get('expressions', {}).get('endpoints'):
                eps |= set(v['expressions']['endpoints'][0])
            # The region is compared too: with python-hcl2 8.x, tflocal could not read the region in main.tf.
            regions[key] = v.get('expressions', {}).get('region', {}).get('constant_value')
        return res, eps, regions
    (r1, e1, g1), (r2, e2, g2) = sig(our_plan_json), sig(sup)
    if r1 != r2:
        return 'resources_differ'
    if e1 != e2:
        return 'same_resources_endpoints_differ'
    return 'same' if g1 == g2 else 'same_resources_region_differs'


def tf_resources(plan_json):
    plan = json.load(open(plan_json, encoding='utf-8'))
    return Counter(rc['type'] for rc in plan.get('resource_changes', [])
                   if rc.get('mode') == 'managed' and 'create' in rc['change']['actions'])


def pulumi_resources(preview):
    """Count the real (custom) resources in the preview, for all providers and not only AWS, as on the Terraform side.

    Left out: Pulumi's own entries (pulumi:...), components (custom=False, e.g. a ComponentResource made from a module)
    and command:... resources. The converter turns Terraform provisioner blocks into command resources, but provisioners
    are not separate resources in the Terraform plan, so they are not counted in EQ. They are reported as provisioner_n.
    """
    c = Counter()
    for s in preview.get('steps', []):
        ns = s.get('newState') or {}
        typ = ns.get('type') or s.get('type', '')
        if s.get('op') in ('create', 'same') and ns.get('custom') and not typ.startswith(('pulumi:', 'command:')):
            c[typ] += 1
    return c


def provisioner_count(preview):
    return sum(1 for s in preview.get('steps', [])
               if s.get('op') in ('create', 'same') and ((s.get('newState') or {}).get('type') or '').startswith('command:'))


def norm_tf(t):     # aws_s3_bucket_metric -> s3bucketmetric
    return t.removeprefix('aws_').replace('_', '').lower()


def norm_pulumi(tok):   # aws:s3/bucketMetric:BucketMetric -> (s3, bucketmetric)
    mod_part, name = tok.split(':')[1], tok.split(':')[2]
    return mod_part.split('/')[0].lower(), name.lower()


BRIDGE = os.path.join(LAB, '..', 'tools', 'pulumi-aws-6.72.0', 'bridge-metadata.json')
_TOKENS = None


def tf_to_tokens(tf_type):
    """Map a Terraform type to its Pulumi type tokens, using bridge-metadata.json of pulumi-aws 6.72.0.

    Both 'current' and 'past' (old) names are included. For aws_s3_bucket, 6.x has two Pulumi resources:
    BucketV2 (current) and the old Bucket.
    """
    global _TOKENS
    if _TOKENS is None:
        res = json.load(open(BRIDGE, encoding='utf-8'))['auto-aliasing']['resources']
        _TOKENS = {k: {v['current']} | {p['name'] for p in v.get('past', [])} for k, v in res.items()}
        _TOKENS.setdefault('aws_s3_bucket', set()).add('aws:s3/bucket:Bucket')
    return _TOKENS.get(tf_type)


def type_match(tf_type, tok):
    """Use the exact mapping first, and a name heuristic when the Terraform type is not in the mapping file (non-AWS)."""
    toks = tf_to_tokens(tf_type)
    if toks is not None:
        return tok in toks
    # Non-AWS (random, null, ...), e.g. random_id -> random:index/randomId:RandomId, null_resource -> null:index/resource:Resource
    if tf_type.split('_', 1)[0] != tok.split(':', 1)[0]:
        return False
    mod, name = norm_pulumi(tok)
    full = tf_type.replace('_', '').lower()                       # randomid / nullresource
    short = tf_type.split('_', 1)[-1].replace('_', '').lower()    # id / resource
    return bool({full, short} & {name, mod + name})


def compare(tf_c, pu_c):
    """EQ: match Terraform and Pulumi resources type by type.

    Equivalent when the Terraform plan has at least one resource and nothing is left over on either side.
    """
    tf_left, pu_left = Counter(tf_c), Counter(pu_c)
    for tt in list(tf_left):
        for pt in list(pu_left):
            if tf_left[tt] and pu_left[pt] and type_match(tt, pt):
                k = min(tf_left[tt], pu_left[pt]); tf_left[tt] -= k; pu_left[pt] -= k
    tf_left, pu_left = +tf_left, +pu_left
    total = sum(tf_c.values())
    matched = total - sum(tf_left.values())
    return {'tf_n': total, 'pulumi_n': sum(pu_c.values()), 'matched': matched,
            'missing_in_pulumi': dict(tf_left), 'extra_in_pulumi': dict(pu_left),
            'equivalent': total > 0 and not tf_left and not pu_left}


def stage_pulumi(run_dir, tasks, lang):
    """Pulumi baseline for one language: convert (L0), compile (L1), preview (L2) and compare with the Terraform plan (L3)."""
    ld = LANG_DIR[lang]
    state = os.path.join(run_dir, f'_state-{lang}'); os.makedirs(state, exist_ok=True)
    env = dict(ENV, PULUMI_BACKEND_URL='file://' + state.replace('\\', '/'))
    rows = []
    for i, t in enumerate(tasks, 1):
        src = os.path.join(DATASET, t)
        tdir = os.path.join(run_dir, t)
        clean = os.path.join(tdir, '_tfsrc'); proj = os.path.join(tdir, ld)
        for d in (clean, proj):
            shutil.rmtree(d, ignore_errors=True)
        os.makedirs(clean); write_input(t, clean)
        log = os.path.join(tdir, f'log-{lang}.txt'); open(log, 'w').close()
        row = {'task': t, 'lang': lang}

        # L0 convert
        rc, out, err, dt = run([PULUMI, 'convert', '--from', 'terraform', '--language', lang, '--out', proj,
                                '--generate-only'], clean, log, env=env)
        row['convert_ok'] = rc == 0 and os.path.exists(os.path.join(proj, 'Pulumi.yaml'))
        row['convert_seconds'] = dt
        row['convert_warnings'] = len(re.findall(r'^warning', err, re.M | re.I))
        # Descriptive only, not part of success: provider settings and aliases the converter dropped without an error,
        # and functions it could not convert.
        row['provider_config_dropped'] = ';'.join(sorted(set(re.findall(r'ignoring aws:(\w+)', err))))
        row['provider_alias_dropped'] = ';'.join(sorted(set(re.findall(r'ignoring aws=([\w-]+)', err))))
        row['unimplemented_functions'] = ';'.join(sorted(set(re.findall(r'Function (\w+) not yet implemented', err))))
        # Warning kinds such as "Provider alias not supported" or "create_before_destroy ...", from lines of the form
        # main.tf:<line>: <kind>; <detail>
        row['convert_warning_kinds'] = ';'.join(sorted(set(re.findall(r'main\.tf:\d+,[\d-]+: ([^;\n]+);', err))))
        row['not_implemented'] = count_not_implemented(proj) if row['convert_ok'] else ''
        row['convert_error'] = '' if row['convert_ok'] else (first_error(err) or err.strip()[-300:])
        row.update(compile_ok='skip', preview_ok='skip', preview_error='', **{k: '' for k in
                   ('tf_n', 'pulumi_n', 'matched', 'equivalent', 'missing_in_pulumi', 'extra_in_pulumi')})

        if row['convert_ok']:
            # Copy helper files (supplement/, lambda.js, ...) into the Pulumi project too, because the program refers
            # to them relative to the project folder, e.g. FileAsset("./supplement/index.html").
            for name in os.listdir(clean):
                if name in ('main.tf', 'intent.rego', 'README.md'):
                    continue
                s_, d_ = os.path.join(clean, name), os.path.join(proj, name)
                if os.path.isdir(s_):
                    shutil.rmtree(d_, ignore_errors=True); shutil.copytree(s_, d_)
                elif not os.path.exists(d_):
                    shutil.copyfile(s_, d_)
            # L1 compile
            if lang == 'typescript':
                tsc = os.path.join(run_dir, 'node_modules', '.bin', 'tsc.cmd')
                rc, out, err, _ = run([tsc, '--noEmit', '-p', proj], proj, log, env=env)
                row['compile_ok'] = rc == 0
                if rc != 0: row['preview_error'] = 'compile: ' + first_error(out + err)
            elif lang == 'python':
                files = glob.glob(os.path.join(proj, '**', '*.py'), recursive=True)
                rc, out, err, _ = run([sys.executable, '-m', 'py_compile'] + files, proj, log, env=env)
                row['compile_ok'] = rc == 0
            else:
                row['compile_ok'] = 'n/a'

            # L2 preview
            prepare_project(proj, lang, run_dir, t)
            ministack_reset()
            run([PULUMI, 'stack', 'init', 'emu', '--non-interactive'], proj, log, env=env)
            rc, out, err, dt = run([PULUMI, 'preview', '--json', '--non-interactive', '-s', 'emu'], proj, log, env=env)
            row['preview_seconds'] = dt
            preview = None
            try:
                preview = json.loads(out)
                open(os.path.join(tdir, f'preview-{lang}.json'), 'w', encoding='utf-8').write(out)
            except Exception:
                pass
            row['preview_ok'] = rc == 0
            if rc != 0:
                diag = ' | '.join(d.get('message', '').strip().splitlines()[0][:200]
                                  for d in (preview or {}).get('diagnostics', []) if d.get('severity') == 'error')
                row['preview_error'] = (row['preview_error'] + ' ' + (diag or first_error(err) or err.strip()[-300:])).strip()

            # L3 equivalence
            pj = os.path.join(tdir, 'terraform', 'plan.json')
            if row['preview_ok'] and preview and os.path.exists(pj):
                row.update(compare(tf_resources(pj), pulumi_resources(preview)))
                row['provisioner_n'] = provisioner_count(preview)
        json.dump(row, open(os.path.join(tdir, f'result-{lang}.json'), 'w'), indent=1)
        rows.append(row)
        print(f"[{i}/{len(tasks)}] {t}: convert={row['convert_ok']} notImpl={row['not_implemented']} "
              f"compile={row['compile_ok']} preview={row['preview_ok']} equiv={row['equivalent']} "
              f"{(row['convert_error'] or row['preview_error'])[:80]}", flush=True)
    write_csv(os.path.join(run_dir, f'results_{lang}.csv'), rows)


def write_csv(path, rows):
    """Write the result CSV, merged task by task with an existing file, so rerunning some tasks keeps the others."""
    if os.path.exists(path):
        merged = {r['task']: r for r in csv.DictReader(open(path, encoding='utf-8'))}
        merged.update({str(r['task']): r for r in rows})
        rows = sorted(merged.values(), key=lambda r: int(r['task']))
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields, restval=''); w.writeheader(); w.writerows(rows)
    print('->', path)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('stage', choices=['tf', 'setup', 'pulumi'])
    ap.add_argument('--run', default='pilot')
    ap.add_argument('--lang', default='typescript', choices=list(LANG_DIR))
    ap.add_argument('--tasks', default='tasks/pilot_tasks.txt')
    a = ap.parse_args()
    run_dir = os.path.join(LAB, 'runs', a.run); os.makedirs(run_dir, exist_ok=True)
    tasks = tasks_from(a.tasks)
    {'tf': lambda: stage_tf(run_dir, tasks),
     'setup': lambda: stage_setup(run_dir, a.lang),
     'pulumi': lambda: stage_pulumi(run_dir, tasks, a.lang)}[a.stage]()
