"""Extract the Terraform provider schemas that the IV adapter needs (R-TF-8/9/11/18/24/29/30, R-PU-31).

Runs `terraform providers schema -json` (Terraform 1.5.7) on an empty configuration that only pins the provider
versions of the original study (aws 5.90.0, null 3.2.3, archive 2.7.0, random 3.7.1). The CLI configuration
pipeline/config/terraform-pinned.tfrc is only read, not changed.
There is no plan, no apply and no cloud access: `init -backend=false` only unpacks the providers from the local
filesystem mirror. The large unpacked binaries are deleted at the end; the compact table tf_schema.json and the lock
file tf_schema.lock.hcl are kept.

tf_schema.json = {provider: {resource_type: {"version": int, "block": <block>}}} with
  <block> = {"attributes": {name: {"type": <cty type JSON>, "optional"?, "required"?, "computed"?, "sensitive"?}},
             "block_types": {name: {"nesting_mode": "single|list|set|map|group", "max_items"?, "min_items"?,
                                    "block": <block>}}}
"""
import json, os, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
WORK = HERE + '/_tfwork'
CACHE = HERE + '/_tfcache'          # separate plugin cache; parallel runs must not share one
TFRC = HERE + '/../../pipeline/config/terraform-pinned.tfrc'
OUT = HERE + '/tf_schema.json'

MAIN_TF = '''terraform {
  required_providers {
    aws     = { source = "hashicorp/aws", version = "5.90.0" }
    null    = { source = "hashicorp/null", version = "3.2.3" }
    archive = { source = "hashicorp/archive", version = "2.7.0" }
    random  = { source = "hashicorp/random", version = "3.7.1" }
  }
}
'''

KEEP_ATTR = ('type', 'optional', 'required', 'computed', 'sensitive', 'nested_type')


def compact_block(b):
    out = {'attributes': {}, 'block_types': {}}
    for n, a in (b.get('attributes') or {}).items():
        out['attributes'][n] = {k: a[k] for k in KEEP_ATTR if k in a}
    for n, bt in (b.get('block_types') or {}).items():
        d = {'nesting_mode': bt['nesting_mode'], 'block': compact_block(bt.get('block') or {})}
        for k in ('max_items', 'min_items'):
            if k in bt:
                d[k] = bt[k]
        out['block_types'][n] = d
    return out


def main():
    shutil.rmtree(WORK, ignore_errors=True)
    os.makedirs(WORK)
    os.makedirs(CACHE, exist_ok=True)
    open(WORK + '/main.tf', 'w', encoding='utf-8').write(MAIN_TF)
    env = dict(os.environ, TF_CLI_CONFIG_FILE=TFRC, TF_PLUGIN_CACHE_DIR=CACHE, TF_IN_AUTOMATION='1',
               CHECKPOINT_DISABLE='1')
    p = subprocess.run(['terraform', 'init', '-backend=false', '-input=false', '-no-color'], cwd=WORK, env=env,
                       capture_output=True, text=True, timeout=900)
    print('init rc', p.returncode, p.stdout[-1500:], p.stderr[-1500:])
    if p.returncode:
        raise SystemExit(1)
    p = subprocess.run(['terraform', 'providers', 'schema', '-json'], cwd=WORK, env=env, capture_output=True,
                       text=True, encoding='utf-8', timeout=900)
    print('schema rc', p.returncode, len(p.stdout), p.stderr[-800:])
    raw = json.loads(p.stdout)
    out = {'_source': 'terraform 1.5.7 providers schema -json; ' + ', '.join(
        l.strip() for l in MAIN_TF.splitlines() if 'version' in l and 'source' in l)}
    for addr, ps in raw['provider_schemas'].items():
        prov = addr.split('/')[-1]
        out[prov] = {'_provider_config': compact_block((ps.get('provider') or {}).get('block') or {})}
        for kind in ('resource_schemas', 'data_source_schemas'):
            for t, s in (ps.get(kind) or {}).items():
                key = t if kind == 'resource_schemas' else 'data.' + t
                out[prov][key] = {'version': s.get('version', 0), 'block': compact_block(s.get('block') or {})}
        print(prov, 'resources', len(ps.get('resource_schemas') or {}), 'data', len(ps.get('data_source_schemas') or {}))
    json.dump(out, open(OUT, 'w', encoding='utf-8'), separators=(',', ':'), sort_keys=True)
    print('wrote', OUT, os.path.getsize(OUT))
    # the lock file records the exact provider builds
    shutil.copy(WORK + '/.terraform.lock.hcl', HERE + '/tf_schema.lock.hcl')
    shutil.rmtree(WORK + '/.terraform', ignore_errors=True)
    shutil.rmtree(CACHE, ignore_errors=True)


if __name__ == '__main__':
    main()
