# Checks one plan JSON against an intent.rego in the same way as the original code: opa eval (OPA 1.1.0, the version
# of the original study) and then the pass function from the original code (extract_validation_status) for PASS/FAIL.
# Usage:  python opa_pass.py <plan.json> <intent.rego>
import json, os, subprocess, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OPA = os.path.join(REPO, 'tools', 'opa-1.1.0', 'opa.exe')
PKG = os.path.join(REPO, 'original-package', 'iac-research-without-agent')
sys.path.insert(0, PKG)
from iac_research.validation.analyzer import extract_validation_status  # pass function from the original code

plan, rego = sys.argv[1], sys.argv[2]
out = subprocess.run([OPA, 'eval', '-i', plan, '-d', rego, 'data'], capture_output=True, text=True)
value = json.loads(out.stdout)['result'][0]['expressions'][0]['value']
print('OPA says:', json.dumps(value))
print('PASS' if extract_validation_status(value) else 'FAIL')
