"""IV adapter, reviewed against the two specs. The baseline is the first prototype.

It turns Pulumi preview artefacts into Terraform-plan-shaped JSON, so that the checks of the original package run on
it unchanged (each task's intent.rego, the same OPA 1.1.0 command and the pass function extract_validation_status):

    opa eval -i <adapted.json> -d intent.rego data   ->  result[0].expressions[0].value  ->  extract_validation_status

Rule IDs point to specs/terraform-plan-json.md (R-TF-n) and specs/pulumi-side.md (R-PU-n).
CHANGES.md lists, rule by rule, what the prototype did, what the spec says and what was changed here.

Inputs (all read-only):
  * the pilot `pulumi preview --json` digests and converted programs (<RUNS>/pilot-aligned)
  * plan mode: saved plans of `pulumi preview --save-plan` (<RUNS>/saved-plans/<task>-<lang>/plan.json, not included)
  * the official TF<->Pulumi mappings (`pulumi package get-mapping terraform ...`, R-PU-26) for aws, null, random and
    archive, in tables/ (build_mappings.py makes the null/random/archive ones)
  * Terraform provider schemas at the original study's provider versions (tables/tf_schema.json, build_tf_schema.py):
    schema_version, attribute or block, block nesting, sensitivity, computed flags (R-TF-8/9/11/18/24/29/30)
  * tables/pulumi_only_defaults.json (R-PU-14, build_pulumi_defaults.py; Terraform defaults cited from provider source)

Value modes (where planned_values and resource_changes.after come from):
  preview : newState.inputs of the preview JSON (program values plus provider-filled defaults), no computed attributes.
  plan    : resourcePlans[urn].state of the saved plan (the provider's advisory planned state, R-PU-33).

Variants (which Terraform sections are written; the same as in the prototype, so results stay comparable):
  P1     : format_version, terraform_version, timestamp, planned_values, resource_changes
  P2     : P1 + configuration: provider_config, managed resources, expressions with constant_value only
  P3id   : P2 + references from propertyDependencies, with the attribute part guessed as "id"; depends_on
  P3src  : P2 + references whose attribute and nesting are read from the converted program text; depends_on;
           also no constant_value where the program text of a top-level argument is not a literal (R-TF-32/33)

Reverse shapes (sanity check: our Terraform control plan cut down to the same shapes):
  R-P1 / R-P2 / R-P3 as in the prototype. provider_config keeps every provider entry (R-TF-21), because the
  adapter writes them too. CTRL = the full control plan, EMPTY = {}.

v2 (see CHANGES.md, section "v2 (fixes A, B)"):
  A  The `command:local:Command` resources that converter v1.4.0 makes for `local-exec` provisioners are folded back
     into the `provisioners` list of their parent's configuration resource (P2/P3id/P3src; R-TF-24, R-TF-32..36).
  B  A block-typed argument whose preview value is hidden as a whole ("[secret]" or unknown) is never written as one
     attribute expression (R-TF-29). P3src rebuilds the blocks from the program text; P2 and P3id write {}.

Run:  python iv_adapter.py   (paths are relative to this file; env var RUNS = run folders; see README.md)
Outputs (next to this script): results_fixed.csv, out_fixed/<task>-<lang>-<mode>-<variant>.json
"""
import copy, csv, datetime, functools, json, os, re, subprocess, sys
from collections import defaultdict, OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace('\\', '/')    # repository root
PKG = ROOT + '/original-package/iac-research-without-agent'
sys.path.insert(0, PKG)
from iac_research.validation.analyzer import extract_validation_status  # pass function of the original code, unchanged
DATASET = PKG + '/ground_truth/dataset'
OPA = ROOT + '/tools/opa-1.1.0/opa.exe'
RUNS = os.environ.get('RUNS', ROOT + '/pipeline/runs').replace('\\', '/')   # run folders (pilot-aligned, ext-w1-*)
PILOT = RUNS + '/pilot-aligned'
TASKS_FILE = ROOT + '/pipeline/tasks/pilot_tasks.txt'
HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
RERUN = RUNS + '/saved-plans'          # plan mode only; not part of the repository
TABLES = HERE + '/tables'
MAPPING_FILES = {'aws': TABLES + '/aws-6.72.0-terraform-mapping.json',      # get-mapping terraform aws@6.72.0
                 'null': TABLES + '/null-0.0.10-terraform-mapping.json',
                 'random': TABLES + '/random-4.18.0-terraform-mapping.json',
                 'archive': TABLES + '/archive-0.3.2-terraform-mapping.json'}
OUT = HERE + '/out_fixed'
RESULTS = HERE + '/results_fixed.csv'

# R-PU-9: all 7 unknown sentinels (the serialized one, plus the 6 typed gRPC ones as a precaution)
UNKNOWN = '04da6b54-80e4-46f7-96ec-b56ff0331ba9'
UNKNOWNS = {UNKNOWN, '1c4a061d-8072-4f0a-a4cb-0ff528b18fe7', '3eeb2bf0-c639-47a8-9e75-3b44932eb421',
            '6a19a0b0-7e62-4c92-b797-7f8e31da9cc2', '030794c1-ac77-496b-92df-f27374a8bd58',
            'e48ece36-62e2-4504-bad9-02848725956a', 'dd056dcd-154b-4c76-9bd3-c8f88648b5ff'}
# R-PU-11: signatures of Pulumi special values
SIG = '4dabf18193072939515e22adb298388d'
SIG_SECRET, SIG_ASSET, SIG_ARCHIVE = '1b47061264138c4ac30d75fd1eb44270', 'c44067f5952c0a294b673a41bacd8c17', '0def7320c3a5731c473e5ecbe6d01bc7'
SIG_RESREF, SIG_OUTPUT, SIG_BYTES = '5cf8f73096256a8f31e491e813e4eb8e', 'd0e6a833031e9bbcd3f4e8bde6ca49a4', '803fd3297a5875dc03ca845dda5d2a98'
SIG_FLOAT = '8ad145fe-0d11-4827-bfd7-1abcbf086f5c'
SECRET_MASK = '[secret]'     # R-PU-10
# Marker for a Pulumi secret: the program set the value, but the adapter cannot see it (R-PU-10). It is treated like
# an unknown in planned values and carried as a value mark into sensitive_values/after_sensitive (R-TF-11/18).
HIDDEN = '<pulumi-secret>'
UNKNOWNS.add(HIDDEN)
META = ('__defaults', '__meta')   # R-PU-12

# ablation switches kept from the prototype (all False = full adapter)
ABL = {'no_autoname': False, 'no_sort': False, 'no_maxitemsone': False, 'no_nullfill': False, 'no_coerce': False}

MAPS = {k: json.load(open(p, encoding='utf-8')) for k, p in MAPPING_FILES.items() if os.path.exists(p)}
TFS = json.load(open(TABLES + '/tf_schema.json', encoding='utf-8'))
PU_DEFAULTS = defaultdict(list)       # tf_type -> [(TF path list, pulumi default, terraform default)]
for _e in json.load(open(TABLES + '/pulumi_only_defaults.json', encoding='utf-8'))['entries']:
    PU_DEFAULTS[_e['tf_type']].append((_e['path'], _e['pulumi_default'], _e['tf_default']))

# R-PU-24: Pulumi token -> (provider, TF type), from the official mappings only (no fallback guessed from the name)
TOK2TF = {}
for _prov, _m in MAPS.items():
    for _tf, _r in _m['resources'].items():
        TOK2TF.setdefault(_r['tok'], (_prov, _tf))


# ============================================================================================ naming (R-PU-27)
# Port of Pluralize (pulumi/inflector v0.1.1) and terraformToPulumiName (terraform-bridge v3.104.0 names.go), taken
# from validate_reversal.py (not included here). Checked there: 52,261 of 52,264 names match the real package schema.
_PLURAL_RULES = [
    (r"(?i)(s)tatus$", r"${1}${2}tatuses"), (r"(?i)(quiz)$", r"${1}zes"), (r"(?i)^(ox)$", r"${1}${2}en"),
    (r"(?i)([m|l])ouse$", r"${1}ice"), (r"(?i)(matr|vert|ind)(ix|ex)$", r"${1}ices"),
    (r"(?i)(x|ch|ss|sh)$", r"${1}es"), (r"(?i)([^aeiouy]|qu)y$", r"${1}ies"), (r"(?i)(hive)$", r"$1s"),
    (r"(?i)(?:([^f])fe|([lre])f)$", r"${1}${2}ves"), (r"(?i)sis$", r"ses"), (r"(?i)([ti])um$", r"${1}a"),
    (r"(?i)(p)erson$", r"${1}eople"), (r"(?i)(m)an$", r"${1}en"), (r"(?i)(c)hild$", r"${1}hildren"),
    (r"(?i)(buffal|tomat)o$", r"${1}${2}oes"),
    (r"(?i)(alumn|bacill|cact|foc|fung|nucle|radi|stimul|syllab|termin|vir)us$", r"${1}i"),
    (r"(?i)us$", r"uses"), (r"(?i)(alias)$", r"${1}es"), (r"(?i)(ax|cris|test)is$", r"${1}es"),
    (r"s$", r"s"), (r"^$", r""), (r"$", r"s"),
]
_IRREGULAR = {"atlas": "atlases", "beef": "beefs", "brother": "brothers", "cafe": "cafes", "child": "children",
              "cookie": "cookies", "corpus": "corpuses", "cow": "cows", "ganglion": "ganglions", "genie": "genies",
              "genus": "genera", "graffito": "graffiti", "hoof": "hoofs", "loaf": "loaves", "man": "men",
              "money": "monies", "mongoose": "mongooses", "move": "moves", "mythos": "mythoi", "niche": "niches",
              "numen": "numina", "occiput": "occiputs", "octopus": "octopuses", "opus": "opuses", "ox": "oxen",
              "penis": "penises", "person": "people", "sex": "sexes", "soliloquy": "soliloquies",
              "testis": "testes", "trilby": "trilbys", "turf": "turfs", "potato": "potatoes", "hero": "heroes",
              "tooth": "teeth", "goose": "geese", "foot": "feet"}
_UNINFLECTED = ["Amoyese", "bison", "Borghese", "bream", "breeches", "britches", "buffalo", "cantus", "carp",
                "chassis", "clippers", "cod", "coitus", "Congoese", "contretemps", "corps", "debris", "diabetes",
                "djinn", "eland", "elk", "equipment", "Faroese", "flounder", "Foochowese", "gallows", "Genevese",
                "Genoese", "Gilbertese", "graffiti", "headquarters", "herpes", "hijinks", "Hottentotese",
                "information", "innings", "jackanapes", "Kiplingese", "Kongoese", "Lucchese", "mackerel",
                "Maltese", ".*?media", "mews", "moose", "mumps", "Nankingese", "news", "nexus", "Niasese",
                "Pekingese", "Piedmontese", "pincers", "Pistoiese", "pliers", "Portuguese", "proceedings",
                "rabies", "rice", "rhinoceros", "salmon", "Sarawakese", "scissors", "sea[- ]bass", "series",
                "Shavese", "shears", "siemens", "species", "swine", "testes", "trousers", "trout", "tuna",
                "Vermontese", "Wenchowese", "whiting", "wildebeest", "Yengeese",
                ".*[nrlm]ese", ".*deer", ".*fish", ".*measles", ".*ois", ".*pox", ".*sheep", "people"]
_UNINF_RE = re.compile(r"(?i)(^(?:%s))$" % "|".join(_UNINFLECTED))
_IRR_RE = re.compile(r"(?i)(.*)\b((?:%s))$" % "|".join(_IRREGULAR))


def _go_repl(repl, ngroups):
    def sub(m):
        g = int(m.group(1) or m.group(2))
        return "\\g<%d>" % g if g <= ngroups else ""
    return re.sub(r"\$\{(\d+)\}|\$(\d+)", sub, repl)


_COMPILED = [(re.compile(p), None) for p, _ in _PLURAL_RULES]
_COMPILED = [(rx, _go_repl(rep, rx.groups)) for (rx, _), (_, rep) in zip(_COMPILED, _PLURAL_RULES)]


def pluralize(s):
    m = _IRR_RE.match(s)
    if m:
        return m.group(1) + s[0:1] + _IRREGULAR[m.group(2).lower()][1:]
    if _UNINF_RE.match(s):
        return s
    for rx, rep in _COMPILED:
        if rx.search(s):
            return rx.sub(rep, s, count=1)
    return s


def camel(name):
    """names.go L208-L231: after the first non-'_' char, '_' upper-cases the next a-z letter; a trailing '_' is kept."""
    out, next_cap, active, prev = [], False, False, ''
    for c in name:
        if c == '_' and active:
            next_cap = True
        else:
            if c != '_' and not active:
                active = True
            out.append(c.upper() if next_cap and 'a' <= c <= 'z' else c)
            next_cap = False
        prev = c
    if prev == '_':
        out.append('_')
    return ''.join(out)


def snake(s):
    """Undo camelCase only. Like the bridge fallback, it never singularizes (R-PU-27)."""
    return re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '_', s).lower()


def is_mio(sch, info):
    """R-PU-28: MaxItemsOne means list/set and (the maxItemsOne override if set, else TF maxItems == 1)."""
    if (sch or {}).get('type') not in (5, 7):
        return False
    if info and info.get('maxItemsOne') is not None:
        return bool(info['maxItemsOne'])
    return (sch or {}).get('maxItems', 0) == 1


def tf_to_pulumi(name, schema_map, infos):
    info = (infos or {}).get(name) or {}
    if info.get('name'):
        return info['name']
    sch = schema_map.get(name)
    n = name
    if sch is not None and sch.get('type') in (5, 7):
        plural = (not info['maxItemsOne']) if info.get('maxItemsOne') is not None else sch.get('maxItems', 0) != 1
        if plural:
            cand = pluralize(name)
            ci = (infos or {}).get(cand) or {}
            conflict_safe = bool(ci.get('name')) and ci.get('name') != cand
            if cand not in schema_map or conflict_safe:
                n = cand
    return camel(n)


def sub_infos(info):
    if not info:
        return {}
    return (info.get('element') or {}).get('fields') or info.get('fields') or {}


UNRESOLVED = set()


class Names:
    """Pulumi <-> TF names at one object level. Runs the bridge's forward naming over the get-mapping shim schema
    and inverts it (R-PU-26/27). Also gives the per-field get-mapping info (defaults, MaxItemsOne, computed)."""
    _cache = {}

    def __init__(self, shim, infos, where=''):
        self.shim, self.infos, self.where = shim or {}, infos or {}, where
        self.fwd = {a: tf_to_pulumi(a, self.shim, self.infos) for a in self.shim}
        self.rev = {}
        for a in sorted(self.fwd):
            self.rev.setdefault(self.fwd[a], a)
        self._children = {}

    @classmethod
    def root(cls, prov, tf_type):
        key = (prov, tf_type)
        if key not in cls._cache:
            m = MAPS.get(prov) or {}
            cls._cache[key] = Names((m.get('provider') or {}).get('resources', {}).get(tf_type) or {},
                                    ((m.get('resources') or {}).get(tf_type) or {}).get('fields') or {}, tf_type)
        return cls._cache[key]

    @classmethod
    def provider_config(cls, prov):
        key = (prov, '<provider>')
        if key not in cls._cache:
            m = MAPS.get(prov) or {}
            cls._cache[key] = Names((m.get('provider') or {}).get('schema') or {}, m.get('config') or {}, prov)
        return cls._cache[key]

    def tf_key(self, pk):
        tk = self.rev.get(pk)
        if tk is None:
            if pk == 'id' and '.' not in self.where:      # the resource id (not part of the shim attribute map)
                return 'id'
            UNRESOLVED.add(f'{self.where}:{pk}')
            return snake(pk)
        return tk

    def pulumi_key(self, tk):
        return self.fwd.get(tk) or camel(tk)

    def child(self, tk):
        if tk not in self._children:
            sch = self.shim.get(tk) or {}
            elem = sch.get('element') or {}
            self._children[tk] = Names(elem.get('resource') or {}, sub_infos(self.infos.get(tk) or {}), f'{self.where}.{tk}')
        return self._children[tk]

    def is_mio(self, tk):
        return is_mio(self.shim.get(tk), self.infos.get(tk))

    def default_info(self, tk):
        return (self.infos.get(tk) or {}).get('default') or {}

    def shim_computed(self, tk):
        return bool((self.shim.get(tk) or {}).get('computed'))


# ============================================================================================ TF schema helpers
def tf_resource_schema(prov, tf_type):
    return (TFS.get(prov) or {}).get(tf_type)


def fqn(prov):
    """R-TF-8: fully qualified provider name. All providers of the original study are hashicorp/* (tf_schema.json)."""
    return 'registry.terraform.io/hashicorp/' + prov


def is_primitive(ty):
    return isinstance(ty, str)


def block_cty_type(blk):
    """cty object type of a block value (attributes and nested block types), used for set ordering (R-TF-10)."""
    attrs = {n: a.get('type', 'dynamic') for n, a in blk['attributes'].items()}
    for n, bt in blk['block_types'].items():
        ot = block_cty_type(bt['block'])
        nm = bt['nesting_mode']
        attrs[n] = ['list', ot] if nm == 'list' else ['set', ot] if nm == 'set' else ['map', ot] if nm == 'map' else ot
    return ['object', attrs]


# ============================================================================================ value helpers
def is_unknown(v):
    return isinstance(v, str) and v in UNKNOWNS


def is_secret(v):
    return v == SECRET_MASK or (isinstance(v, dict) and v.get(SIG) == SIG_SECRET)


def has_unknown(v):
    if is_unknown(v):
        return True
    if isinstance(v, dict):
        return any(has_unknown(x) for k, x in v.items() if k not in META)
    if isinstance(v, list):
        return any(has_unknown(x) for x in v)
    return False


def has_hidden(v):
    """True if any part is unknown (R-PU-9) or secret (R-PU-10), i.e. the adapter cannot see the value."""
    if is_unknown(v) or is_secret(v):
        return True
    if isinstance(v, dict) and SIG not in v:
        return any(has_hidden(x) for k, x in v.items() if k not in META)
    if isinstance(v, list):
        return any(has_hidden(x) for x in v)
    return False


def norm_pulumi(v):
    """R-PU-9/10/11: turn Pulumi special values into plain values. Anything the adapter cannot see becomes UNKNOWN
    (HIDDEN for secrets)."""
    if is_secret(v) or v == HIDDEN:
        return HIDDEN
    if is_unknown(v):
        return UNKNOWN
    if isinstance(v, dict) and SIG in v:
        s = v[SIG]
        if s in (SIG_ASSET, SIG_ARCHIVE):            # the TF field name comes from the asset translation in get-mapping (key mapping)
            return v.get('path') or v.get('text') or v.get('uri') or UNKNOWN
        if s == SIG_RESREF:
            return v['id'] if isinstance(v.get('id'), str) and v['id'] and not is_unknown(v['id']) else UNKNOWN
        if s == SIG_OUTPUT:
            if 'value' not in v or v.get('secret'):
                return UNKNOWN
            return norm_pulumi(v['value'])
        if s == SIG_BYTES:
            import base64
            return base64.b64decode(v.get('value') or '').decode('utf-8', 'replace')
        if s == SIG_FLOAT:
            return UNKNOWN                            # NaN/Inf cannot be written in a TF JSON plan
        return UNKNOWN
    return v


def coerce(v, ty):
    """Coerce a planned value to its TF schema type (Terraform types planned values by the schema, R-TF-9)."""
    if v is None or is_unknown(v) or isinstance(v, (dict, list)) or ABL['no_coerce']:
        return v
    try:
        if ty == 'string' and not isinstance(v, str):
            if isinstance(v, bool):
                return 'true' if v else 'false'
            if isinstance(v, float) and v.is_integer():
                return str(int(v))
            return str(v)
        if ty == 'number':
            if isinstance(v, str) and re.fullmatch(r'-?\d+', v.strip()):
                return int(v)
            if isinstance(v, str):
                return float(v)
            if isinstance(v, float) and v.is_integer():
                return int(v)          # cty writes whole numbers without a decimal point
        if ty == 'bool' and isinstance(v, str) and v.lower() in ('true', 'false'):
            return v.lower() == 'true'
    except Exception:
        pass
    return v


# ------------------------------------------------------------------ cty set order (R-TF-10; go-cty v1.12.2)
# https://github.com/zclconf/go-cty/blob/v1.12.2/cty/set_internals.go, Less (L85-L135): strings by bytes, numbers
# numerically, false before true, null and unknown last, the rest by bytes.Compare of makeSetHashBytes (L144-L260).
def _go_quote(s):
    out = ['"']
    esc = {'"': '\\"', '\\': '\\\\', '\a': '\\a', '\b': '\\b', '\f': '\\f', '\n': '\\n', '\r': '\\r', '\t': '\\t',
           '\v': '\\v'}
    for ch in s:
        if ch in esc:
            out.append(esc[ch])
        elif ord(ch) < 0x20 or ord(ch) == 0x7f:
            out.append('\\x%02x' % ord(ch))
        else:
            out.append(ch)
    out.append('"')
    return ''.join(out)


def _hash_bytes(v, ty):
    if is_unknown(v):
        return '?'
    if v is None:
        return '~'
    if ty == 'number':
        return format(v, '.10g') if isinstance(v, (int, float)) else str(v)   # big.Float.String() is Text('g', 10)
    if ty == 'bool':
        return 'T' if v else 'F'
    if ty == 'string':
        return _go_quote(v if isinstance(v, str) else str(v))
    if not isinstance(ty, list):
        return json.dumps(v, sort_keys=True)
    k = ty[0]
    if k == 'map' and isinstance(v, dict):
        return '{' + ''.join(_go_quote(x) + ':' + _hash_bytes(v[x], ty[1]) + ';' for x in sorted(v)) + '}'
    if k in ('list', 'set') and isinstance(v, list):
        return '[' + ''.join(_hash_bytes(e, ty[1]) + ';' for e in v) + ']'
    if k == 'object' and isinstance(v, dict):
        return '<' + ''.join(_hash_bytes(v.get(a), ty[1][a]) + ';' for a in sorted(ty[1])) + '>'
    if k == 'tuple' and isinstance(v, list):
        return '<' + ''.join(_hash_bytes(e, t) + ';' for e, t in zip(v, ty[1])) + '>'
    return json.dumps(v, sort_keys=True)


def _cty_less(a, b, ty):
    if json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True):
        return False
    if b is None and a is not None:
        return True
    if a is None:
        return False
    if not is_unknown(a) and is_unknown(b):
        return True
    if is_unknown(a):
        return False
    if ty == 'string' and isinstance(a, str) and isinstance(b, str):
        return a.encode('utf-8') < b.encode('utf-8')
    if ty == 'bool':
        return b is True
    if ty == 'number' and isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a < b
    return _hash_bytes(a, ty).encode('utf-8') < _hash_bytes(b, ty).encode('utf-8')


def cty_set(elems, ety):
    """Finish a TF set value: an unknown primitive element makes the whole set unknown (R-PU-9 granularity caveat),
    equal known elements collapse, and elements come out in cty set order (R-TF-10)."""
    if is_primitive(ety) and any(is_unknown(e) for e in elems):
        return UNKNOWN
    if ABL['no_sort']:
        return elems
    seen, out = set(), []
    for e in elems:
        k = json.dumps(e, sort_keys=True)
        if is_unknown(e) or k not in seen:
            seen.add(k)
            out.append(e)
    cmp = lambda a, b: -1 if _cty_less(a, b, ety) else (1 if _cty_less(b, a, ety) else 0)
    return sorted(out, key=functools.cmp_to_key(cmp))


# ============================================================================================ Pulumi -> TF values
DROPPED = set()


def pv_attr(v, ty, names, mio):
    """Convert one Pulumi value to a TF value of cty type `ty` (planned values). `names` is the naming context of
    the value's own object level, i.e. the attribute's child context."""
    v = norm_pulumi(v)
    if is_unknown(v):
        return UNKNOWN
    if v is None:
        return None
    if is_primitive(ty):
        if ty == 'dynamic':
            return strip_meta(v)
        return coerce(v, ty)
    kind = ty[0]
    if kind in ('list', 'set'):
        if not isinstance(v, list):
            if mio and not ABL['no_maxitemsone']:
                v = [v]                    # R-PU-28: a flattened MaxItemsOne value becomes a one-element list
            else:
                return strip_meta(v)
        out = [pv_attr(e, ty[1], names, False) for e in v]
        return cty_set(out, ty[1]) if kind == 'set' else out
    if kind == 'map':
        if not isinstance(v, dict):
            return v
        return {k: pv_attr(x, ty[1], names, False) for k, x in v.items() if k not in META}   # R-PU-29: map keys kept
    if kind == 'object':
        if not isinstance(v, dict):
            return v
        out = {}
        for pk, x in v.items():
            if pk in META:
                continue
            tk = names.tf_key(pk)
            if tk not in ty[1]:
                DROPPED.add(f'{names.where}.{tk}')
                continue
            out[tk] = pv_attr(x, ty[1][tk], names.child(tk), names.is_mio(tk))
        for a in ty[1]:
            out.setdefault(a, None)           # a cty object value always carries every attribute of its type
        return out
    if kind == 'tuple':
        return [pv_attr(e, t, names, False) for e, t in zip(v, ty[1])] if isinstance(v, list) else v
    return strip_meta(v)


def strip_meta(v):
    if isinstance(v, dict):
        return {k: strip_meta(x) for k, x in v.items() if k not in META}
    if isinstance(v, list):
        return [strip_meta(x) for x in v]
    return norm_pulumi(v)


def pv_nested(v, bt, names):
    v = norm_pulumi(v)
    if is_unknown(v):
        return UNKNOWN
    nm, blk = bt['nesting_mode'], bt['block']
    if nm in ('list', 'set'):
        if v is None:
            return []
        if isinstance(v, dict):
            if ABL['no_maxitemsone']:
                return pv_block(v, blk, names)
            v = [v]                           # R-PU-28: flattened MaxItemsOne block
        out = [pv_block(e, blk, names) if isinstance(e, dict) else norm_pulumi(e) for e in v]
        return cty_set(out, block_cty_type(blk)) if nm == 'set' else out
    if nm in ('single', 'group'):
        if isinstance(v, list):
            v = v[0] if v else None
        if v is None:
            return pv_block({}, blk, names) if nm == 'group' else None
        return pv_block(v, blk, names)
    if nm == 'map':
        return {k: pv_block(e, blk, names) for k, e in v.items() if k not in META} if isinstance(v, dict) else v
    return strip_meta(v)


def pv_block(pobj, blk, names):
    """Pulumi object to TF block value with every attribute of the TF provider schema (R-TF-9, R-PU-31). Unset
    computed attributes become unknown, unset optional ones null, unset list/set blocks [], unset single blocks null."""
    out = {}
    for pk, x in pobj.items():
        if pk in META:
            continue
        tk = names.tf_key(pk)
        if tk in blk['attributes']:
            out[tk] = pv_attr(x, blk['attributes'][tk].get('type', 'dynamic'), names.child(tk), names.is_mio(tk))
        elif tk in blk['block_types']:
            out[tk] = pv_nested(x, blk['block_types'][tk], names.child(tk))
        else:
            DROPPED.add(f'{names.where}.{tk}')   # not a Terraform attribute, e.g. a Pulumi-only field
    if not ABL['no_nullfill']:
        for a, s in blk['attributes'].items():
            if a not in out:
                out[a] = UNKNOWN if s.get('computed') else None
        for b, bt in blk['block_types'].items():
            if b not in out:
                nm = bt['nesting_mode']
                if names.shim_computed(b):          # SDKv2 Optional+Computed block: unknown in the plan when unset
                    out[b] = UNKNOWN
                elif nm in ('list', 'set'):
                    out[b] = []
                elif nm == 'map':
                    out[b] = {}
                elif nm == 'group':
                    out[b] = pv_block({}, bt['block'], names.child(b))
                else:
                    out[b] = None
    return out


def pv_generic(pobj, names):
    """Fallback when the TF type has no Terraform schema (e.g. aws_s3_bucket_legacy): rename keys only."""
    out = {}
    for pk, x in pobj.items():
        if pk in META:
            continue
        tk = names.tf_key(pk)
        x = norm_pulumi(x)
        out[tk] = pv_generic(x, names.child(tk)) if isinstance(x, dict) else (
            [pv_generic(e, names.child(tk)) if isinstance(e, dict) else norm_pulumi(e) for e in x] if isinstance(x, list) else x)
    return out


# ------------------------------------------------------------------ plan JSON encodings (R-TF-9/11/16/17/18)
_OMIT = object()


def omit_unknowns(v):
    """Port of jsonplan omitUnknowns: unknown object attributes are dropped, unknown list/set elements become null."""
    if is_unknown(v):
        return _OMIT
    if isinstance(v, dict):
        return {k: o for k, x in v.items() for o in [omit_unknowns(x)] if o is not _OMIT}
    if isinstance(v, list):
        return [None if o is _OMIT else o for o in (omit_unknowns(x) for x in v)]
    return v


def unknown_as_bool(v):
    """Port of jsonplan unknownAsBool: unknown is true, objects drop known leaves, lists keep one entry per element."""
    if v is None:
        return False
    if is_unknown(v):
        return True
    if isinstance(v, list):
        return [unknown_as_bool(x) for x in v]
    if isinstance(v, dict):
        return {k: b for k, x in v.items() for b in [unknown_as_bool(x)] if b is not False}
    return False


def sensitive_as_bool(v, desc, marks, schema_sensitive=False):
    """Port of jsonstate SensitiveAsBool. desc is ('block', blk), ('nested', bt) or ('attr', cty type).
    marks=True adds the schema's sensitive attributes (after_sensitive, R-TF-18); marks=False gives sensitive_values
    (R-TF-11). A Pulumi secret (HIDDEN) counts as a value mark, except on a schema-sensitive attribute: there the
    secret comes from the schema itself (R-PU-10), and Terraform marks it only in after_sensitive."""
    if v == HIDDEN:
        return not schema_sensitive
    kind = desc[0]
    if kind == 'block':
        blk = desc[1]
        if v is None:
            return False
        if is_unknown(v) or not isinstance(v, dict):
            return {}
        out = {}
        for n, a in blk['attributes'].items():
            if marks and a.get('sensitive'):
                out[n] = True
                continue
            if n in v:
                s = sensitive_as_bool(v[n], ('attr', a.get('type', 'dynamic')), marks, bool(a.get('sensitive')))
                if s is not False:
                    out[n] = s
        for n, bt in blk['block_types'].items():
            if n in v:
                s = sensitive_as_bool(v[n], ('nested', bt), marks)
                if s is not False:
                    out[n] = s
        return out
    if kind == 'nested':
        bt = desc[1]
        nm = bt['nesting_mode']
        if v is None:
            return False
        if nm in ('list', 'set'):
            if is_unknown(v) or not isinstance(v, list) or not v:
                return []
            return [sensitive_as_bool(e, ('block', bt['block']), marks) for e in v]
        if nm == 'map':
            if is_unknown(v) or not isinstance(v, dict) or not v:
                return {}
            return {k: s for k, e in v.items() for s in [sensitive_as_bool(e, ('block', bt['block']), marks)] if s is not False}
        return sensitive_as_bool(v, ('block', bt['block']), marks)
    ty = desc[1]
    if v is None or is_primitive(ty):
        return False
    k = ty[0]
    if k in ('list', 'set', 'tuple'):
        if is_unknown(v) or not isinstance(v, list) or not v:
            return []
        if k == 'tuple':
            return [sensitive_as_bool(e, ('attr', t), marks) for e, t in zip(v, ty[1])]
        return [sensitive_as_bool(e, ('attr', ty[1]), marks) for e in v]
    if k in ('map', 'object'):
        if is_unknown(v) or not isinstance(v, dict) or not v:
            return {}
        sub = (lambda key: ty[1]) if k == 'map' else (lambda key: ty[1].get(key, 'dynamic'))
        return {kk: s for kk, e in v.items() for s in [sensitive_as_bool(e, ('attr', sub(kk)), marks)] if s is not False}
    return False


# ============================================================================================ Pulumi inputs
def load_preview(task, lang):
    d = json.load(open(f'{PILOT}/{task}/preview-{lang}.json', encoding='utf-8'))
    res, skipped, providers, notes = [], [], {}, []
    if any((x.get('severity') == 'error') for x in d.get('diagnostics') or []):
        notes.append('preview has error diagnostics (R-PU-3)')
    for s in d.get('steps', []):
        ns = s.get('newState') or {}
        urn = s['urn']
        typ = ns.get('type') or urn.split('::')[2].split('$')[-1]
        if typ.startswith('pulumi:providers:'):          # R-PU-6: not a TF resource, but read for R-PU-25
            providers[urn] = {'pkg': typ.split(':')[2], 'name': urn.rsplit('::', 1)[1], 'inputs': ns.get('inputs') or {}}
            continue
        if not ns.get('custom'):                         # R-PU-6: skip stack and component resources
            continue
        if typ not in TOK2TF:                            # R-PU-24: only types in the official mapping
            skipped.append(urn)
            notes.append(f'no TF type for {typ} (skipped)')
            continue
        prov, tft = TOK2TF[typ]
        res.append({'urn': urn, 'op': s.get('op'), 'type': typ, 'prov': prov, 'tf_type': tft,
                    'name': urn.rsplit('::', 1)[1], 'inputs': ns.get('inputs') or {},
                    'propdeps': ns.get('propertyDependencies') or {}, 'deps': ns.get('dependencies') or [],
                    'parent': ns.get('parent'), 'provider_ref': ns.get('provider') or s.get('provider') or ''})
    mtime = os.path.getmtime(f'{PILOT}/{task}/preview-{lang}.json')
    return res, d.get('config') or {}, providers, skipped, notes, mtime


def load_commands(task, lang):
    """v2 fix A: the `command:*` custom resources of the preview. They have no TF type (R-PU-24) and load_preview
    skips them; they are read only to rebuild Terraform `provisioners` (see provisioner_blocks)."""
    d = json.load(open(f'{PILOT}/{task}/preview-{lang}.json', encoding='utf-8'))
    out = []
    for s in d.get('steps', []):
        ns = s.get('newState') or {}
        urn = s['urn']
        typ = ns.get('type') or urn.split('::')[2].split('$')[-1]
        if typ.startswith('command:') and ns.get('custom'):
            out.append({'urn': urn, 'type': typ, 'name': urn.rsplit('::', 1)[1], 'inputs': ns.get('inputs') or {},
                        'propdeps': ns.get('propertyDependencies') or {}, 'deps': ns.get('dependencies') or []})
    return out


def load_saved_state(task, lang):
    p = f'{RERUN}/{task}-{lang}/plan.json'
    if not os.path.exists(p):
        return {}
    d = json.load(open(p, encoding='utf-8'))
    return {urn: (rp.get('state') or {}) for urn, rp in d.get('resourcePlans', {}).items()}


def program_path(task, lang):
    return f'{PILOT}/{task}/pulumi-ts/index.ts' if lang == 'typescript' else f'{PILOT}/{task}/pulumi-py/__main__.py'


def provider_key(r, providers):
    """R-PU-25: "<pkg>" for the default provider, "<pkg>.N" for an explicit `pulumi:providers:<pkg>` resource N."""
    ref = r['provider_ref']
    purn = ref.rsplit('::', 1)[0] if ref.count('::') >= 4 else ref
    if not purn:
        return r['prov']
    pname = purn.rsplit('::', 1)[1]
    if pname.startswith('default'):
        return r['prov']
    return f"{r['prov']}.{pname}"


# ============================================================================================ program-text parser
KEY_RE = re.compile(r'(?:^|(?<=[{(,\n]))\s*(["\']?)([A-Za-z_]\w*)\1\s*(?::(?!:)|=(?![=>]))')
STEP_RE = re.compile(r'\.(\w+)|\[\s*(\d+|"[^"\]]*"|\'[^\'\]]*\')\s*\]')


def code_mask(src):
    """Per character: True if it is code, False if it is inside a string literal."""
    mask = [True] * len(src)
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if c in '"\'`':
            q = c
            triple = src[i:i + 3] == q * 3
            j = i + (3 if triple else 1)
            while j < n:
                if src[j] == '\\':
                    j += 2
                    continue
                if triple and src[j:j + 3] == q * 3:
                    j += 3
                    break
                if not triple and src[j] == q:
                    j += 1
                    break
                j += 1
            for k in range((i + 3 if triple else i + 1), min((j - 3 if triple else j - 1), n)):
                mask[k] = False
            i = j
            continue
        i += 1
    return mask


class Program:
    """Small regex-based reader of the `pulumi convert` output (TS or Python). Only P3src uses it."""
    _CALL = r'(\w+)\.(?:(\w+)\.)?([A-Z]\w*)\(\s*'
    CTOR_TS = re.compile(r'new\s+' + _CALL + r'(["\'`])([^"\'`$]*)')
    CTOR_PY = re.compile(r'(?<![\w.])' + _CALL + r'(?:resource_name=)?f?(["\'])([^"\'{]*)')
    VAR_TS = [re.compile(r'(?:const|let|var)\s+(\w+)\s*(?::[^=]+)?=\s*new\s+' + _CALL + r'["\'`]([^"\'`$]*)'),
              re.compile(r'(\w+)\.push\(\s*new\s+' + _CALL + r'["\'`]([^"\'`$]*)')]
    VAR_PY = [re.compile(r'^(\w+)\s*(?::[^=\n]+)?=\s*' + _CALL + r'(?:resource_name=)?f?["\']([^"\'{]*)', re.M),
              re.compile(r'(\w+)\.append\(\s*' + _CALL + r'(?:resource_name=)?f?["\']([^"\'{]*)')]

    def __init__(self, path, lang):
        self.ok = os.path.exists(path)
        self.src = open(path, encoding='utf-8').read() if self.ok else ''
        self.lang = lang
        self.mask = code_mask(self.src)
        self.vars = {}   # var name -> (module, Class, logical base)
        for rx in (self.VAR_TS if lang == 'typescript' else self.VAR_PY):
            for m in rx.finditer(self.src):
                base = m.group(5).rstrip('-')
                self.vars.setdefault(m.group(1), ((m.group(3) or 'index').lower().rstrip('_'), m.group(4), base))
        self.ctors = []  # (open paren, close paren, module, Class, logical base)
        rx = self.CTOR_TS if lang == 'typescript' else self.CTOR_PY
        for m in rx.finditer(self.src):
            if not self.mask[m.start()]:
                continue
            op = self.src.index('(', m.start())
            end = self.match_paren(op)
            self.ctors.append((op, end, (m.group(2) or 'index').lower().rstrip('_'), m.group(3), m.group(5).rstrip('-')))

    def match_paren(self, i):
        depth, n = 0, len(self.src)
        for j in range(i, n):
            if not self.mask[j]:
                continue
            c = self.src[j]
            if c in '([{':
                depth += 1
            elif c in ')]}':
                depth -= 1
                if depth == 0:
                    return j
        return n

    def find_ctor(self, typ, name):
        mod = typ.split(':')[1].split('/')[0].lower()
        cls = typ.split(':')[2]
        base = re.sub(r'-\d+$', '', name)
        for c in self.ctors:
            if c[2] == mod and c[3] == cls and c[4] in (name, base):
                return c
        return None

    # ---------------------------------------------------------- references (as in the prototype, plus index steps)
    def occurrences(self, typ, name):
        """References inside the constructor of resource (typ, name), as dicts {var, target, steps, index, keys, pos}.
        steps is the attribute/index chain after the variable, e.g. [('attr','certificateAuthority'),('attr','data')]."""
        c = self.find_ctor(typ, name)
        if not c:
            return None
        start, end = c[0], c[1]
        seg = self.src[start:end + 1]
        keys_at, depth = {}, 0
        key_positions = {m.start(2): m.group(2) for m in KEY_RE.finditer(seg)
                         if self.mask[start + (m.start(1) if m.group(1) else m.start(2))]}
        step = r'(?:\.\w+(?![\w(]|\s*\()|\[\s*(?:\d+|"[^"\]]*"|\'[^\'\]]*\')\s*\])'
        var_rx = re.compile(r'(?<![\w.])(' + '|'.join(map(re.escape, sorted(self.vars, key=len, reverse=True))) +
                            r')((?:\[(?:[^\[\]]|\[[^\]]*\])*\])?)((?:\.\w+(?![\w(]|\s*\())' + step + r'*)') if self.vars else None
        occ_positions = {}
        if var_rx:
            for m in var_rx.finditer(seg):
                g = start + m.start()
                if self.mask[g] or (m.start() > 0 and seg[m.start() - 1] == '{'):
                    occ_positions[m.start()] = m
        out, i = [], 0
        while i < len(seg):
            gi = start + i
            if i in key_positions:
                keys_at[depth] = key_positions[i]
                for d in [d for d in keys_at if d > depth]:
                    del keys_at[d]
            if i in occ_positions:
                m = occ_positions[i]
                chain = [keys_at[d] for d in sorted(keys_at) if d <= depth]
                steps = [('attr', a) if a else ('index', ix) for a, ix in STEP_RE.findall(m.group(3))]
                out.append({'var': m.group(1), 'target': self.vars[m.group(1)], 'steps': steps,
                            'index': m.group(2), 'keys': chain, 'pos': gi})
            if self.mask[gi]:
                ch = seg[i]
                if ch in '([{':
                    depth += 1
                elif ch in ')]}':
                    for d in [d for d in keys_at if d >= depth]:
                        del keys_at[d]
                    depth -= 1
            i += 1
        return out

    # ---------------------------------------------------------- top-level argument texts (R-TF-32/33 in P3src)
    def _split_items(self, a, b):
        """Split src[a:b] at commas on depth 0, ignoring strings. Returns a list of (start, end)."""
        items, depth, s = [], 0, a
        for j in range(a, b):
            if not self.mask[j]:
                continue
            ch = self.src[j]
            if ch in '([{':
                depth += 1
            elif ch in ')]}':
                depth -= 1
            elif ch == ',' and depth == 0:
                items.append((s, j))
                s = j + 1
        if self.src[s:b].strip():
            items.append((s, b))
        return items

    def top_level_args(self, typ, name):
        """{Pulumi property name: (value start, value end)} of the resource's argument object (TS) or kwargs (Python)."""
        c = self.find_ctor(typ, name)
        if not c:
            return None
        op, end = c[0], c[1]
        items = self._split_items(op + 1, end)
        out = {}
        if self.lang == 'typescript':
            if len(items) < 2:
                return out
            a, b = items[1]
            ob = self.src.find('{', a, b)
            if ob < 0 or not self.mask[ob]:
                return out
            cb = self.match_paren(ob)
            for s, e in self._split_items(ob + 1, cb):
                m = re.match(r'\s*(["\']?)([A-Za-z_]\w*)\1\s*:', self.src[s:e])
                if m:
                    out[m.group(2)] = (s + m.end(), e)
        else:
            for s, e in items[1:]:
                m = re.match(r'\s*([A-Za-z_]\w*)\s*=(?!=)', self.src[s:e])
                if m and m.group(1) not in ('opts', 'resource_name'):
                    out[camel(m.group(1))] = (s + m.end(), e)
        return out

    def is_literal(self, a, b):
        """True if src[a:b] is a literal in Terraform's sense (no variable, reference, function call or
        interpolation): strings without interpolation, numbers, bools, null, lists/objects of literals, enum members."""
        parts, j = [], a
        while j < b:
            if self.mask[j]:
                parts.append(self.src[j])
                j += 1
                continue
            k = j
            while k < b and not self.mask[k]:
                k += 1
            content = self.src[j:k]
            q = self.src[j - 1] if j > 0 else ''
            pre = self.src[max(0, j - 4):j]
            if q == '`' and '${' in content:
                return False                                   # TS template with interpolation
            if self.lang == 'python' and re.search(r'(?<![\w])[rR]?[fF][rR]?("""|\'\'\'|"|\')$', pre) and '{' in content:
                return False                                   # Python f-string with a placeholder
            parts.append('S')
            j = k
        code = ''.join(parts)
        code = re.sub(r'[rRbBuUfF]{0,2}(?:""""""|\'\'\'\'\'\'|"S"|\'S\'|`S`|""|\'\'|``)', 'S', code)
        code = code.replace('"""S"""', 'S').replace("'''S'''", 'S')
        code = re.sub(r'\b[a-z_]\w*\.\w+\.[A-Z]\w*\.[A-Za-z_]\w*\b(?!\s*\()', 'S', code)      # enum members
        code = re.sub(r'\b[a-z_]\w*\.\w+\.[A-Z]\w*Args\s*\(', '(', code)                   # Python *Args classes
        # type conversions the converter puts around literals, e.g. float(80) for HCL "80" given to a number
        code = re.sub(r'(?<![\w.])(?:float|int|str|bool|Number|String|Boolean)\s*\(', '(', code)
        if self.lang == 'python':
            code = re.sub(r'\b[A-Za-z_]\w*\s*=(?!=)', ':', code)                            # kwargs inside them
        code = re.sub(r'(?:\bS|\b[A-Za-z_]\w*)\s*:', ':', code)                               # object keys
        code = re.sub(r'-?\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b|\b(?:true|false|null|undefined|True|False|None)\b', 'S', code)
        code = re.sub(r'[\s\[\]{}(),:S]', '', code)
        return code == ''

    # ---------------------------------------------------------- nested literal structure (v2 fix B; lifts N15 there)
    def _skip_ws(self, i, b):
        """First index >= i (and < b) that is neither whitespace nor in a line comment; b if there is none."""
        while i < b:
            if self.src[i].isspace():
                i += 1
            elif self.mask[i] and (self.src.startswith('//', i) or (self.lang == 'python' and self.src[i] == '#')):
                j = self.src.find('\n', i, b)
                i = b if j < 0 else j
            else:
                break
        return i

    def object_fields(self, a, b):
        """{key: (value start, value end)} in source order if src[a:b] is one object literal: TS `{k: v}`, Python
        dict `{"k": v}` or Python `...Args(k=v)`. None otherwise."""
        i = self._skip_ws(a, b)
        if i >= b or not self.mask[i]:
            return None
        kw = False
        if self.src[i] == '{':
            op = i
        else:
            m = re.compile(r'[A-Za-z_][\w.]*Args\s*\(').match(self.src, i) if self.lang == 'python' else None
            if not m:
                return None
            op, kw = m.end() - 1, True
        close = self.match_paren(op)
        if close >= b or self._skip_ws(close + 1, b) < b:
            return None
        rx = re.compile(r'([A-Za-z_]\w*)\s*=(?!=)' if kw else r'(["\']?)([A-Za-z_]\w*)\1\s*:(?!:)')
        out = OrderedDict()
        for s, e in self._split_items(op + 1, close):
            k = self._skip_ws(s, e)
            if k >= e:
                continue
            m = rx.match(self.src, k, e)
            if not m:
                return None                     # spread, computed key and the like: not a plain object literal
            out[m.group(1) if kw else m.group(2)] = (m.end(), e)
        return out

    def literal_items(self, a, b):
        """Element spans, in source order, of the list literal in src[a:b]. A single object literal (single block or
        flattened MaxItemsOne block, R-PU-28) counts as one element. None if src[a:b] is neither, e.g. a computed
        list such as `[...].map(...)` or a variable."""
        i = self._skip_ws(a, b)
        if i >= b or not self.mask[i]:
            return None
        if self.src[i] == '[':
            close = self.match_paren(i)
            if close >= b or self._skip_ws(close + 1, b) < b:
                return None
            return [(s, e) for s, e in self._split_items(i + 1, close) if self._skip_ws(s, e) < e]
        return [(i, b)] if self.object_fields(i, b) is not None else None

    def literal_value(self, a, b):
        """Value of the literal src[a:b]; call it only where is_literal is True. _NOLIT if the value cannot be
        found without running code (enum members, type conversions)."""
        text = self.src[a:b].strip()
        try:
            if self.lang == 'python':
                import ast
                return ast.literal_eval(text)
            return _ts_literal(text)
        except Exception:
            return _NOLIT


_NOLIT = object()


def _ts_literal(text):
    """Value of a TypeScript literal: strings without interpolation, numbers, true/false/null, array and object
    literals of these. Raises ValueError for anything else."""
    s, pos = text, [0]
    esc = {'n': '\n', 't': '\t', 'r': '\r', 'b': '\b', 'f': '\f', 'v': '\v', '0': '\0'}
    num_rx = re.compile(r'-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?(?![\w$.])')
    kw_rx = re.compile(r'(true|false|null)(?![\w$.])')
    key_rx = re.compile(r'[A-Za-z_$][\w$]*|\d+')

    def peek():
        return s[pos[0]:pos[0] + 1]

    def ws():
        while pos[0] < len(s):
            if s[pos[0]].isspace():
                pos[0] += 1
            elif s.startswith('//', pos[0]):
                j = s.find('\n', pos[0])
                pos[0] = len(s) if j < 0 else j
            elif s.startswith('/*', pos[0]):
                j = s.find('*/', pos[0] + 2)
                if j < 0:
                    raise ValueError('comment')
                pos[0] = j + 2
            else:
                return

    def string():
        q = s[pos[0]]
        j, out = pos[0] + 1, []
        while j < len(s):
            ch = s[j]
            if ch == '\\':
                n = s[j + 1:j + 2]
                if n == 'u' and s[j + 2:j + 3] == '{':
                    k = s.index('}', j)
                    out.append(chr(int(s[j + 3:k], 16)))
                    j = k + 1
                elif n == 'u':
                    out.append(chr(int(s[j + 2:j + 6], 16)))
                    j += 6
                elif n == 'x':
                    out.append(chr(int(s[j + 2:j + 4], 16)))
                    j += 4
                elif n in ('\n', '\r'):                       # line continuation
                    j += 3 if s[j + 1:j + 3] == '\r\n' else 2
                else:
                    out.append(esc.get(n, n))
                    j += 2
                continue
            if ch == q:
                pos[0] = j + 1
                return ''.join(out)
            if q == '`' and s.startswith('${', j):
                raise ValueError('interpolation')
            if q != '`' and ch == '\n':
                raise ValueError('newline in string')
            out.append(ch)
            j += 1
        raise ValueError('unterminated string')

    def value():
        ws()
        c = peek()
        if c in ('"', "'", '`'):
            return string()
        if c in ('[', '{'):
            pos[0] += 1
            out = [] if c == '[' else {}
            end = ']' if c == '[' else '}'
            while True:
                ws()
                if peek() == end:
                    pos[0] += 1
                    return out
                if c == '[':
                    out.append(value())
                else:
                    if peek() in ('"', "'"):
                        k = string()
                    else:
                        m = key_rx.match(s, pos[0])
                        if not m:
                            raise ValueError('key')
                        k, pos[0] = m.group(0), m.end()
                    ws()
                    if peek() != ':':
                        raise ValueError('colon')
                    pos[0] += 1
                    out[k] = value()
                ws()
                if peek() == ',':
                    pos[0] += 1
                elif peek() != end:
                    raise ValueError('separator')
        m = num_rx.match(s, pos[0])
        if m:
            pos[0] = m.end()
            return int(m.group(0)) if re.fullmatch(r'-?\d+', m.group(0)) else float(m.group(0))
        m = kw_rx.match(s, pos[0])
        if m:
            pos[0] = m.end()
            return {'true': True, 'false': False, 'null': None}[m.group(1)]
        raise ValueError('not a literal')

    v = value()
    ws()
    if pos[0] != len(s):
        raise ValueError('trailing text')
    return v


# ============================================================================================ adapter core
def tf_address(tf_type, name, idx_names):
    """(address, config address, TF name, index) for a Pulumi logical name. R-PU-23: '<base>-<i>' is read as an
    index only when the (TF type, base) pair was detected as a contiguous count group."""
    m = re.match(r'^(.*)-(\d+)$', name)
    if m and (tf_type, m.group(1)) in idx_names:
        base, idx = m.group(1), int(m.group(2))
        return f'{tf_type}.{base}[{idx}]', f'{tf_type}.{base}', base, idx
    return f'{tf_type}.{name}', f'{tf_type}.{name}', name, None


def rc_sort_key(r):
    """R-TF-13: AbsResourceInstance.Less in the root module: data before managed, then type, name, numeric key."""
    return (0 if r.get('mode') == 'data' else 1, r['type'], r['name'],
            (0, r['index'], '') if isinstance(r.get('index'), int) else (1, 0, str(r.get('index') or '')))


def at_path(obj, path, fn):
    """Apply fn(container, key) at a TF path, descending through lists of objects."""
    if not path or obj is None:
        return
    if isinstance(obj, list):
        for e in obj:
            at_path(e, path, fn)
        return
    if not isinstance(obj, dict) or path[0] not in obj:
        return
    if len(path) == 1:
        fn(obj, path[0])
    else:
        at_path(obj[path[0]], path[1:], fn)


def replace_contained(v, needles):
    """R-PU-13/21: a string that contains a Pulumi-generated name is unknown in Terraform."""
    if isinstance(v, str) and not is_unknown(v) and any(n in v for n in needles):
        return UNKNOWN
    if isinstance(v, dict):
        return {k: (x if k in META else replace_contained(x, needles)) for k, x in v.items()}
    if isinstance(v, list):
        return [replace_contained(x, needles) for x in v]
    return v


def autoname_keys(r, raw):
    """R-PU-13: keys in __defaults whose get-mapping default is autonamed or isFunc, at every object level."""
    found = {}

    def walk(obj, names, path):
        if not isinstance(obj, dict):
            return
        for pk in obj.get('__defaults') or []:
            tk = names.tf_key(pk)
            d = names.default_info(tk)
            if d.get('autonamed') or d.get('isFunc'):
                found[tuple(path + [pk])] = obj.get(pk)
        for pk, x in obj.items():
            tk = names.rev.get(pk)
            if pk in META or tk is None or 'resource' not in ((names.shim.get(tk) or {}).get('element') or {}):
                continue                     # go into nested blocks and objects only, not maps (R-PU-29)
            sub = names.child(tk)
            if isinstance(x, dict) and SIG not in x:
                walk(x, sub, path + [pk])
            elif isinstance(x, list):
                for e in x:
                    walk(e, sub, path + [pk])
    walk(raw, Names.root(r['prov'], r['tf_type']), [])
    return found


def overlay_secrets(raw, inputs):
    """Plan mode: where the preview input is a secret and the saved-plan value is unknown, keep the secret mark."""
    if isinstance(raw, dict) and isinstance(inputs, dict):
        for k, x in inputs.items():
            if k in META or k not in raw:
                continue
            if is_secret(x) and is_unknown(raw[k]):
                raw[k] = HIDDEN
            else:
                overlay_secrets(raw[k], x)
    elif isinstance(raw, list) and isinstance(inputs, list) and len(raw) == len(inputs):
        for i, x in enumerate(inputs):
            if is_secret(x) and is_unknown(raw[i]):
                raw[i] = HIDDEN
            else:
                overlay_secrets(raw[i], x)


def set_pulumi_path(obj, path, value):
    if not path or not isinstance(obj, (dict, list)):
        return
    if isinstance(obj, list):
        for e in obj:
            set_pulumi_path(e, path, value)
        return
    if path[0] not in obj:
        return
    if len(path) == 1:
        obj[path[0]] = value
    else:
        set_pulumi_path(obj[path[0]], path[1:], value)


def adapt(task, lang, mode, variant, drop_caddr=None):
    res, config, providers, skipped, notes, mtime = load_preview(task, lang)
    state = load_saved_state(task, lang) if mode == 'plan' else {}
    if mode == 'plan' and not state:
        notes.append('no saved plan')
    # --- count groups (R-PU-23): names base-0 .. base-k with no gap, keyed by (TF type, base)
    by_base = defaultdict(list)
    for r in res:
        m = re.match(r'^(.*)-(\d+)$', r['name'])
        if m:
            by_base[(r['tf_type'], m.group(1))].append(int(m.group(2)))
    idx_names = {tb for tb, ids in by_base.items() if sorted(ids) == list(range(len(ids)))}
    for r in res:
        addr, caddr, base, idx = tf_address(r['tf_type'], r['name'], idx_names)
        r.update(address=addr, caddr=caddr, base=base, index=idx, pkey=provider_key(r, providers))
        if r['parent'] and not r['parent'].split('::')[2].startswith('pulumi:pulumi:Stack'):
            notes.append(f'{addr}: parent is a component (module placement R-TF-41 not reproduced)')
    if drop_caddr:   # mutation test: delete one resource block from the Pulumi side
        res = [r for r in res if r['caddr'] != drop_caddr]
    urn2res = {r['urn']: r for r in res}
    # --- R-PU-13 generated names: per resource, Pulumi path -> value; the values are carried over to dependants
    gen_vals = {}
    for r in res:
        raw = (state.get(r['urn']) if mode == 'plan' else r['inputs']) or {}
        raw = copy.deepcopy(raw)
        if mode == 'plan':
            for pk in [k for k, x in raw.items() if is_secret(x) and k not in r['inputs']]:
                del raw[pk]          # additionalSecretOutputs wrapped an attribute the program never set
            overlay_secrets(raw, r['inputs'])
        r['raw'] = raw
        r['autoname'] = autoname_keys(r, r['inputs'])          # the keys come from the preview's __defaults
        vals = set()
        for path in r['autoname']:
            cur = r['raw']
            for p in path:
                cur = cur.get(p) if isinstance(cur, dict) else None
            if isinstance(cur, str) and len(cur) >= 8 and not is_unknown(cur):
                vals.add(cur)
        gen_vals[r['urn']] = vals
    # --- planned values / resource changes
    pv_resources, rc = [], []
    for r in res:
        tschema = tf_resource_schema(r['prov'], r['tf_type'])
        names = Names.root(r['prov'], r['tf_type'])
        raw = r['raw']
        if not ABL['no_autoname']:
            for path in r['autoname']:
                set_pulumi_path(raw, list(path), UNKNOWN)
            for pk, urns in r['propdeps'].items():
                needles = set().union(*[gen_vals.get(u, set()) for u in urns]) if urns else set()
                if needles and pk in raw:
                    raw[pk] = replace_contained(raw[pk], needles)
        if tschema:
            after = pv_block(raw, tschema['block'], names)
            version = tschema.get('version', 0)
        else:
            notes.append(f'{r["tf_type"]} not in the Terraform provider schema')
            after, version = pv_generic(raw, names), 0
        for path, pdef, tdef in PU_DEFAULTS.get(r['tf_type'], []):      # R-PU-14
            at_path(after, path, lambda o, k, pdef=pdef, tdef=tdef: o.__setitem__(k, tdef) if o[k] == pdef else None)
        r['after'] = after
        values = omit_unknowns(after)
        values = OrderedDict(sorted(values.items()))
        au = {} if not has_unknown(after) else unknown_as_bool(after)
        desc = ('block', tschema['block']) if tschema else ('block', {'attributes': {}, 'block_types': {}})
        sv = sensitive_as_bool(after, desc, False)
        asens = sensitive_as_bool(after, desc, True)
        base = OrderedDict([('address', r['address']), ('mode', 'managed'), ('type', r['tf_type']), ('name', r['base'])])
        if r['index'] is not None:
            base['index'] = r['index']
        base['provider_name'] = fqn(r['prov'])
        pvr = dict(base, schema_version=version)
        if values:
            pvr['values'] = values                              # `values` is omitempty (jsonplan resource.go L40)
        pvr['sensitive_values'] = sv
        pv_resources.append(pvr)
        actions = OP2ACTIONS.get(r['op'], [r['op']])
        if actions != ['create']:
            notes.append(f'{r["address"]}: op {r["op"]} (before state not reconstructed)')
        rc.append(dict(base, change={'actions': actions, 'before': None, 'after': copy.deepcopy(values),
                                     'after_unknown': au, 'before_sensitive': False, 'after_sensitive': asens}))
    if not ABL['no_sort']:
        pv_resources.sort(key=lambda x: x['address'])          # R-TF-12: plain address string order
        rc.sort(key=rc_sort_key)                               # R-TF-13
    plan = OrderedDict([('format_version', '1.2'), ('terraform_version', '1.5.7'),
                        ('planned_values', {'root_module': {'resources': pv_resources}}),
                        ('resource_changes', rc),
                        ('timestamp', datetime.datetime.fromtimestamp(mtime, datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))])
    if variant == 'P1':
        return plan, notes
    # --- configuration
    prog = Program(program_path(task, lang), lang) if variant == 'P3src' else None
    provs = provisioner_blocks(load_commands(task, lang), urn2res, variant, prog, lang, notes)   # v2 fix A
    groups = defaultdict(list)
    for r in res:
        groups[r['caddr']].append(r)
    conf_res = []
    for caddr in (list(groups) if ABL['no_sort'] else sorted(groups)):     # R-TF-23: managed, by address string
        insts = sorted(groups[caddr], key=lambda r: (r['index'] or 0))
        r0 = insts[0]
        tschema = tf_resource_schema(r0['prov'], r0['tf_type'])
        exprs = build_exprs(r0, insts, tschema, variant, urn2res, prog, notes, skipped)
        cr = OrderedDict([('address', caddr), ('mode', 'managed'), ('type', r0['tf_type']), ('name', r0['base']),
                          ('provider_config_key', r0['pkey'])])
        if provs.get(caddr):
            cr['provisioners'] = provs[caddr]                   # R-TF-24; jsonconfig field order (config.go L71-L108)
        if exprs:
            cr['expressions'] = exprs                           # R-TF-24: omitted when empty
        cr['schema_version'] = (tschema or {}).get('version', 0)
        if r0['index'] is not None:
            cr['count_expression'] = {'constant_value': len(insts)}
        if variant.startswith('P3'):
            prop_urns = {u for v in r0['propdeps'].values() for u in v}
            dep = []
            for u in r0['deps']:                                 # R-PU-19
                if u in prop_urns or u not in urn2res:
                    continue
                a = urn2res[u]['caddr']
                if a not in dep:
                    dep.append(a)
            if lang == 'python':     # the Python SDK keeps `dependencies` in a set (resource.py L276): no source order
                dep.sort()           # the Node SDK keeps dependsOn order (resource.ts L1003-L1006, L1088-L1100)
            if dep:
                cr['depends_on'] = dep
        conf_res.append(cr)
    plan['configuration'] = {'provider_config': provider_config(res, config, providers),
                             'root_module': {'resources': conf_res}}
    return plan, notes


OP2ACTIONS = {'create': ['create'], 'same': ['no-op'], 'update': ['update'], 'replace': ['create', 'delete'],
              'create-replacement': ['create', 'delete'], 'delete-replaced': ['create', 'delete'],
              'delete': ['delete'], 'read': ['read'], 'refresh': ['no-op']}    # R-TF-15


# ------------------------------------------------------------------ provider_config (R-TF-21/22/42.3, R-PU-25)
def provider_config(res, config, providers):
    pc = OrderedDict()
    for key in sorted({r['pkey'] for r in res}):
        pkg, _, alias = key.partition('.')
        e = OrderedDict([('name', pkg), ('full_name', fqn(pkg))])
        if alias:
            e['alias'] = alias
            src = next((p['inputs'] for p in providers.values() if p['pkg'] == pkg and p['name'] == alias), {})
        else:
            src = {k.split(':', 1)[1]: v for k, v in config.items() if k.startswith(pkg + ':')}
        ex = provider_exprs(pkg, src)
        if ex:
            e['expressions'] = ex
        pc[key] = e
    return pc


def provider_exprs(pkg, cfg):
    """Provider block expressions from the stack config, or from the inputs of an explicit provider resource."""
    blk = ((TFS.get(pkg) or {}).get('_provider_config')) or {'attributes': {}, 'block_types': {}}
    names = Names.provider_config(pkg)
    out = OrderedDict()
    for pk, v in sorted(cfg.items()):
        if pk in META or pk == 'version':
            continue
        tk = names.tf_key(pk)
        if is_secret(v) or is_unknown(v):
            if tk in blk['attributes'] or tk in blk['block_types']:
                out[tk] = {}
            continue
        if isinstance(v, str) and (tk in blk['block_types'] or not is_primitive((blk['attributes'].get(tk) or {}).get('type', 'string'))):
            try:
                v = json.loads(v)
            except Exception:
                pass
        if tk in blk['attributes']:
            ty = blk['attributes'][tk].get('type', 'string')
            out[tk] = {'constant_value': coerce(v, ty) if is_primitive(ty) else v}
        elif tk in blk['block_types']:
            items = v if isinstance(v, list) else [v]
            sub = names.child(tk)
            bb = blk['block_types'][tk]['block']
            out[tk] = [OrderedDict((sub.tf_key(k), {'constant_value': coerce(x, (bb['attributes'].get(sub.tf_key(k)) or {}).get('type', 'string'))})
                                   for k, x in sorted(it.items())) for it in items if isinstance(it, dict)]
    return out


# ------------------------------------------------------------------ configuration expressions
def program_value(v):
    """The part of a Pulumi value the program wrote: drop the keys in each level's __defaults (R-PU-12)."""
    if isinstance(v, dict) and SIG not in v:
        d = set(v.get('__defaults') or [])
        return {k: program_value(x) for k, x in v.items() if k not in META and k not in d}
    if isinstance(v, list):
        return [program_value(x) for x in v]
    return v


def cfg_value(v, ty, names, mio, fill_objects=False):
    """Value of a constant expression: TF names, but no type coercion (constant_value is the HCL value, R-TF-10/32).
    fill_objects: attribute-as-block elements get every element attribute, null where missing (R-TF-30)."""
    v = norm_pulumi(v)
    if v is None or is_primitive(ty):
        return strip_meta(v)
    kind = ty[0]
    if kind in ('list', 'set'):
        if not isinstance(v, list):
            if not mio:
                return strip_meta(v)
            v = [v]
        return [cfg_value(e, ty[1], names, False, fill_objects) for e in v]
    if kind == 'map':
        return {k: cfg_value(x, ty[1], names, False) for k, x in v.items() if k not in META} if isinstance(v, dict) else v
    if kind == 'object':
        if not isinstance(v, dict):
            return v
        out = {}
        for pk, x in v.items():
            if pk in META:
                continue
            tk = names.tf_key(pk)
            out[tk] = cfg_value(x, ty[1].get(tk, 'dynamic'), names.child(tk), names.is_mio(tk), fill_objects)
        if fill_objects:
            for a in ty[1]:
                out.setdefault(a, None)
        return OrderedDict(sorted(out.items()))
    return strip_meta(v)


def is_attr_as_block(ty):
    return isinstance(ty, list) and ty[0] in ('list', 'set') and isinstance(ty[1], list) and ty[1][0] == 'object'


def const_expr(val, ty, names, mio, derived):
    """Expression of a TF attribute whose value has no references (R-TF-32/33, R-PU-9/10/13/21)."""
    if has_hidden(val) or (derived and replace_contained(val, derived) != val):
        return {}
    return {'constant_value': cfg_value(val, ty, names, mio, fill_objects=is_attr_as_block(ty))}


def block_exprs(val, bt, names, ctx, leaf_fn=None, path=None):
    """Block expressions of a nested block, shaped by the schema nesting (R-TF-29): an array for list/set, an object
    for single/group, a keyed object for map. leaf_fn(path, value) may return a references expression (P3)."""
    nm, blk = bt['nesting_mode'], bt['block']

    def one(it, p):
        d = OrderedDict()
        pv = program_value(it)
        for pk in sorted(pv):
            x = pv[pk]
            ctk = names.tf_key(pk)
            if (ctx['tf_type'], ctx['tf_path'] + [ctk]) in ctx['pu_defaults'] and x == ctx['pu_defaults'][(ctx['tf_type'], ctx['tf_path'] + [ctk])]:
                continue                                       # R-PU-14: nested Pulumi-only default
            pp = (p or []) + [pk]
            if ctk in blk['block_types']:
                if isinstance(x, (dict, list)):
                    sub_ctx = dict(ctx, tf_path=ctx['tf_path'] + [ctk])
                    d[ctk] = block_exprs(x, blk['block_types'][ctk], names.child(ctk), sub_ctx, leaf_fn, pp)
                continue
            if leaf_fn is not None:
                e = leaf_fn(pp, x)
                if e is not None:
                    d[ctk] = e
                    continue
            ty = (blk['attributes'].get(ctk) or {}).get('type', 'dynamic')
            d[ctk] = const_expr(x, ty, names.child(ctk), names.is_mio(ctk), ctx['derived'])
        return d

    if nm in ('list', 'set'):
        items = val if isinstance(val, list) else [val]
        return [one(it, path) for it in items if isinstance(it, dict)]
    if nm == 'map':
        return {k: one(it, path) for k, it in val.items() if isinstance(it, dict)} if isinstance(val, dict) else {}
    if isinstance(val, list):
        val = val[0] if val else {}
    return one(val, path) if isinstance(val, dict) else {}


def target_key(t):
    """(module, Class, logical base) of a resource record, comparable with Program var targets."""
    return (t['type'].split(':')[1].split('/')[0].lower(), t['type'].split(':')[2], t['base'])


def tf_traversal(target_r, steps, lang):
    """TF traversal segments for a Pulumi access chain on the target (names as in R-PU-27). '[0]' is inserted after
    an attribute that Pulumi flattened (MaxItemsOne, R-PU-28) when the program reads a field below it."""
    names = Names.root(target_r['prov'], target_r['tf_type'])
    segs = []
    for i, (kind, s) in enumerate(steps):
        if kind == 'index':
            segs.append(f'[{s}]' if s.isdigit() else '[%s]' % json.dumps(s.strip('\'"')))
            continue
        if s in ('id', 'urn') and i == 0:
            segs.append('.id')
            break
        pk = camel(s) if (lang == 'python' or '_' in s) else s
        tk = names.tf_key(pk)
        segs.append('.' + tk)
        nxt = steps[i + 1] if i + 1 < len(steps) else None
        if nxt is not None and nxt[0] == 'attr' and names.is_mio(tk):
            segs.append('[0]')
        names = names.child(tk)
    return segs


def same_index_pattern(t, pk, insts, urn2res):
    """True if every instance i of a counted source refers to instance i of target t in property pk. Terraform
    writes aws_x.y[count.index] as the references ["aws_x.y", "count.index"] (R-TF-38)."""
    if t['index'] is None or len(insts) < 2 or insts[0]['index'] is None:
        return False
    for i in insts:
        us = i['propdeps'].get(pk) or []
        if not any(u in urn2res and urn2res[u]['caddr'] == t['caddr'] and urn2res[u]['index'] == i['index'] for u in us):
            return False
    return True


def ref_strings(t, segs, pk, insts, urn2res, dynamic_index=False):
    """Terraform references for one traversal (R-TF-35): the full path, then shorter prefixes, then the subject,
    then the containing resource if the subject is an indexed instance. No de-duplication (R-TF-37)."""
    if same_index_pattern(t, pk, insts, urn2res):
        return [t['caddr'], 'count.index']
    if dynamic_index:
        return [t['caddr']]                                   # R-TF-38: a dynamic index ends the traversal
    subject = t['address']
    out = [subject + ''.join(segs[:k]) for k in range(len(segs), 0, -1)]
    out.append(subject)
    if t['index'] is not None:
        out.append(t['caddr'])
    return out


def norm_key(k, lang):
    return camel(k) if (lang == 'python' or '_' in k) else k


def refs_from_occurrences(occs, deps, pk, insts, urn2res, variant, lang):
    """P3src: one traversal per program-text occurrence (in source order), then a guessed '.id' traversal for each
    mapped propertyDependencies target that has no text evidence. P3src_textonly: occurrences only (nested leaves).
    P3id: one '.id' traversal per mapped target, in address order."""
    deps = list(dict.fromkeys(u for u in deps if u in urn2res))
    out, used = [], set()
    if variant.startswith('P3src'):
        for o in sorted(occs, key=lambda o: o['pos']):
            cands = [u for u in deps if target_key(urn2res[u]) == o['target']]
            if not cands:
                continue
            ix = (o['index'] or '').strip('[] ')
            if ix.isdigit():
                cands = [u for u in cands if urn2res[u]['index'] == int(ix)] or cands
            u = cands[0]
            used.add(u)
            dyn = bool(ix) and not ix.isdigit()
            out += ref_strings(urn2res[u], tf_traversal(urn2res[u], o['steps'], lang), pk, insts, urn2res, dyn)
    if variant != 'P3src_textonly':
        for u in sorted([u for u in deps if u not in used], key=lambda u: urn2res[u]['address']):
            out += ref_strings(urn2res[u], ['.id'], pk, insts, urn2res)
    return out


def text_const(v, ty, names, mio, lang):
    """constant_value of a literal read from program text (v2 fix B): TF names at object levels (Python dict keys
    are snake_case Pulumi names), map keys as written (R-PU-29), no type coercion (R-TF-10/32)."""
    if v is None or is_primitive(ty):
        return v
    kind = ty[0]
    if kind in ('list', 'set'):
        if not isinstance(v, list):
            if not mio:
                return v
            v = [v]
        return [text_const(e, ty[1], names, False, lang) for e in v]
    if kind == 'map':
        return {k: text_const(x, ty[1], names, False, lang) for k, x in v.items()} if isinstance(v, dict) else v
    if kind == 'object' and isinstance(v, dict):
        out = {}
        for k, x in v.items():
            tk = names.tf_key(norm_key(k, lang))
            out[tk] = text_const(x, ty[1].get(tk, 'dynamic'), names.child(tk), names.is_mio(tk), lang)
        return OrderedDict(sorted(out.items()))
    return v


def text_block_exprs(prog, r0, pk, bt, names, deps, insts, urn2res, occ, lang):
    """v2 fix B (P3src): block expressions of a block-typed argument whose preview value is hidden as a whole
    ("[secret]", R-PU-10, or unknown, R-PU-9). propertyDependencies has no nested path (R-PU-18), so the blocks are
    rebuilt from the program text: one block-expressions object per element of the argument's list literal, in
    source order (R-TF-29). For each leaf: references from the program-text occurrences inside it (R-TF-35); else
    constant_value if its text is a literal (R-TF-32); else {} (R-TF-33). Schema-sensitive leaves also get {}, so no
    secret value is taken from program text (row 30, N24). None if the argument is not a list or object literal."""
    lits = prog.top_level_args(r0['type'], r0['name']) or {}
    if pk not in lits:
        return None
    occ = occ or []

    def blocks(a, b, bt, names):
        items = prog.literal_items(a, b)
        if items is None:
            return None
        objs = [one(s, e, bt['block'], names) for s, e in items]
        if any(o is None for o in objs):
            return None
        if bt['nesting_mode'] in ('list', 'set'):
            return objs
        if bt['nesting_mode'] in ('single', 'group') and len(objs) == 1:
            return objs[0]
        return None                                            # map nesting (keyed blocks): not handled, no such case

    def one(a, b, blk, names):
        fields = prog.object_fields(a, b)
        if fields is None:
            return None
        d = {}
        for key, (s, e) in fields.items():
            tk = names.tf_key(norm_key(key, lang))
            if tk in blk['block_types']:
                sub = blocks(s, e, blk['block_types'][tk], names.child(tk))
                d[tk] = {} if sub is None else sub
                continue
            attr = blk['attributes'].get(tk)
            if attr is None:
                DROPPED.add(f'{names.where}.{tk}')
                continue
            c_occ = [o for o in occ if s <= o['pos'] < e]
            if c_occ:
                refs = refs_from_occurrences(c_occ, deps, pk, insts, urn2res, 'P3src_textonly', lang)
                d[tk] = {'references': refs} if refs else {}
            elif attr.get('sensitive') or not prog.is_literal(s, e):
                d[tk] = {}
            else:
                v = prog.literal_value(s, e)
                d[tk] = {} if v is _NOLIT else {
                    'constant_value': text_const(v, attr.get('type', 'dynamic'), names.child(tk), names.is_mio(tk), lang)}
        return OrderedDict(sorted(d.items()))

    return blocks(lits[pk][0], lits[pk][1], bt, names)


def ref_expr(r0, insts, bt, names, pk, val, deps, variant, urn2res, occ, ctx, lang, prog=None):
    """Expression of a property that depends on other resources (P3 variants)."""
    tocc = []
    if variant == 'P3src' and occ:
        tocc = [o for o in occ if o['keys'] and norm_key(o['keys'][0], lang) == pk]
    if bt is not None and isinstance(val, (dict, list)):
        # put the references on nested leaves (propertyDependencies is top-level only)
        if variant == 'P3src' and tocc:
            def leaf_fn(path, v):
                c_occ = [o for o in tocc if [norm_key(k, lang) for k in o['keys'][:len(path)]] == path]
                if c_occ:
                    refs = refs_from_occurrences(c_occ, deps, pk, insts, urn2res, 'P3src_textonly', lang)
                    return {'references': refs} if refs else {}
                return None
        else:
            def leaf_fn(path, v):
                if has_hidden(v):          # no text evidence: every mapped target on each hidden leaf, as ".id"
                    refs = refs_from_occurrences([], deps, pk, insts, urn2res, 'P3id', lang)
                    return {'references': refs} if refs else {}
                return None
        return block_exprs(val, bt, names, ctx, leaf_fn, [pk])
    if bt is not None:
        # v2 fix B: the value is hidden as a whole; a block type is never one attribute expression (R-TF-29)
        if variant == 'P3src' and prog is not None and prog.ok:
            b = text_block_exprs(prog, r0, pk, bt, names, deps, insts, urn2res, occ, lang)
            if b is not None:
                return b
        return {}
    refs = refs_from_occurrences(tocc, deps, pk, insts, urn2res, variant, lang)
    return {'references': refs} if refs else {}


def build_exprs(r0, insts, tschema, variant, urn2res, prog, notes, skipped):
    lang = 'python' if (prog and prog.lang == 'python') else 'typescript'
    names = Names.root(r0['prov'], r0['tf_type'])
    blk = (tschema or {}).get('block') or {'attributes': {}, 'block_types': {}}
    inputs = r0['inputs']
    # R-PU-8/18: the top-level keys the program (or SDK) wrote are the propertyDependencies keys
    written = list(r0['propdeps']) if r0['propdeps'] else [k for k in inputs if k not in META and k not in set(inputs.get('__defaults') or [])]
    written = [k for k in written if k != 'tagsAll']                      # R-PU-15
    gen = set()
    for i in insts:                                                    # generated names of targets (R-PU-13/21)
        for urns in i['propdeps'].values():
            for u in urns:
                if u in urn2res:
                    for path in urn2res[u]['autoname']:
                        cur = urn2res[u]['inputs']
                        for p in path:
                            cur = cur.get(p) if isinstance(cur, dict) else None
                        if isinstance(cur, str) and len(cur) >= 8:
                            gen.add(cur)
    ctx = {'tf_type': r0['tf_type'], 'tf_path': [], 'derived': gen,
           'pu_defaults': _PathDict({(r0['tf_type'], tuple(p)): pdef for p, pdef, _ in PU_DEFAULTS.get(r0['tf_type'], [])})}
    occ, lits = None, None
    if prog is not None and prog.ok:
        occ = prog.occurrences(r0['type'], r0['name'])
        lits = prog.top_level_args(r0['type'], r0['name'])
        if occ is None:
            notes.append(f'ctor not found {r0["name"]}')
    exprs = OrderedDict()
    for pk in sorted(set(written)):
        tk = names.tf_key(pk)
        if tk not in blk['attributes'] and tk not in blk['block_types']:
            notes.append(f'{r0["caddr"]}.{tk}: not a Terraform argument (dropped)')
            continue
        attr = blk['attributes'].get(tk)
        if attr is not None and attr.get('computed') and not attr.get('optional') and not attr.get('required'):
            continue                                                   # computed-only: cannot be set in configuration
        has_val = pk in inputs
        val = program_value(inputs.get(pk))
        if has_val and ctx['pu_defaults'].get((r0['tf_type'], (tk,))) is not None and val == ctx['pu_defaults'][(r0['tf_type'], (tk,))]:
            continue                                                   # R-PU-14: Pulumi-only default, not written
        raw_deps = r0['propdeps'].get(pk) or []
        bt = blk['block_types'].get(tk)
        ty = (attr or {}).get('type', 'dynamic')
        sub = names.child(tk)
        kctx = dict(ctx, tf_path=[tk])
        if not raw_deps:
            if not has_val:
                continue
            if bt is not None:
                if isinstance(val, (dict, list)):
                    exprs[tk] = block_exprs(val, bt, sub, kctx)
                else:                                          # hidden as a whole: v2 fix B (P3src), else {}
                    b = (text_block_exprs(prog, r0, pk, bt, sub, [], insts, urn2res, occ, lang)
                         if variant == 'P3src' and prog is not None and prog.ok else None)
                    exprs[tk] = {} if b is None else b
                continue
            # counted resource whose instances differ: no literal can do that (R-TF-32); TF uses count.index (R-TF-38)
            if len(insts) > 1 and any(json.dumps(program_value(i['inputs'].get(pk)), sort_keys=True) !=
                                      json.dumps(val, sort_keys=True) for i in insts[1:]):
                exprs[tk] = {'references': ['count.index']} if variant.startswith('P3') else {}
                continue
            if variant == 'P3src' and lits and pk in lits and not prog.is_literal(*lits[pk]):
                exprs[tk] = {}                                         # R-TF-32/33: call, variable or interpolation
                continue
            exprs[tk] = const_expr(val, ty, sub, names.is_mio(tk), gen)
            continue
        # the value comes from other resources: never a constant (R-PU-21)
        if not variant.startswith('P3'):
            if bt is not None and isinstance(val, (dict, list)):
                exprs[tk] = block_exprs(val, bt, sub, kctx)            # nested constants kept, hidden leaves give {}
            else:
                exprs[tk] = {}
            continue
        exprs[tk] = ref_expr(r0, insts, bt, sub, pk, val, raw_deps, variant, urn2res, occ, kctx, lang, prog)
    return OrderedDict(sorted(exprs.items()))


class _PathDict(dict):
    """{(tf_type, tuple path): value} that also answers list-path lookups."""
    def _k(self, k):
        return (k[0], tuple(k[1]))

    def __contains__(self, k):
        return dict.__contains__(self, self._k(k))

    def __getitem__(self, k):
        return dict.__getitem__(self, self._k(k))

    def get(self, k, default=None):
        return dict.get(self, self._k(k), default)


# ============================================================================================ provisioners (v2 fix A)
# How pulumi-converter-terraform v1.4.0 converts provisioners, from pkg/convert/tf.go
# (https://github.com/pulumi/pulumi-converter-terraform/blob/v1.4.0/pkg/convert/tf.go):
#   * each `provisioner` block of a managed resource becomes its own resource, in block order (loop L3796-L3800);
#     `local-exec` gives a `command:local:Command` named `<parent PCL name>Provisioner<i>` (L2582-L2618, L2653-L2663);
#   * options.dependsOn is [parent] for i == 0, else [<parent>Provisioner<i-1>]; a for_each parent gives
#     [for _r in <target>: _r] (provisionerDependsOn, L2620-L2651);
#   * `self.<attr>` is rewritten to `<parent>.<attr>` (scopes.self L2679-L2681; rewrite L1625-L1628);
#   * `command` goes to `create`; with `when = destroy`, create = update = "true" and delete = command (L2697-L2706);
#     `interpreter` and `environment` are copied (L2683-L2696, L2708-L2714); `working_dir`, `quiet` and
#     `on_failure` are not converted.
# Terraform v1.5.7 writes them on the configuration resource as `provisioners: [{type, expressions}]` in block order,
# with expressions = marshalExpressions(p.Config, provisioner schema); `when`, `on_failure` and `connection` are not
# included (internal/command/jsonconfig/config.go L89-L91, L117-L120, L486-L498). The local-exec schema is command
# string (required), interpreter list(string), environment map(string) (internal/builtin/provisioners/local-exec/
# resource_provisioner.go L44-L66). `self.x` gives ["self.x", "self"] (R-TF-35/36; internal/addrs/parse_ref.go
# L261-L266, addrs.Self).
LOCAL_EXEC = OrderedDict([('command', 'string'), ('interpreter', ['list', 'string']), ('environment', ['map', 'string'])])
PROV_RE = re.compile(r'^(.*)Provisioner(\d+)(?:-.*)?$')
_PROV_NAMES = Names({}, {}, 'local-exec')


def provisioner_parents(cmds, urn2res, notes):
    """{parent config address: {i: command record}}, the inverse of tf.go L2620-L2663. Follows the dependsOn chain
    <p>Provisioner<i> -> <p>Provisioner<i-1> down to i == 0, whose dependsOn target is the parent. dependsOn is
    `dependencies` minus all `propertyDependencies` (R-PU-19). When the parent is also referenced in a property
    (`self.x`), that difference is empty, so the mapped dependencies are used, with the PCL name prefix as tie-break."""
    pos = {c['urn']: (m.group(1), int(m.group(2))) for c in cmds for m in [PROV_RE.match(c['name'])] if m}
    out = defaultdict(dict)
    for c in cmds:
        if c['type'] != 'command:local:Command':
            notes.append(f'{c["name"]}: {c["type"]} is not a local-exec provisioner (not reproduced)')
            continue
        if c['urn'] not in pos:
            notes.append(f'{c["name"]}: command:local:Command not named <resource>Provisioner<i> (skipped)')
            continue
        prefix, i = pos[c['urn']]
        cur, k = c, i
        while k > 0:
            prev = next((x for x in cmds if x['urn'] in cur['deps'] and pos.get(x['urn']) == (prefix, k - 1)), None)
            if prev is None:
                break
            cur, k = prev, k - 1
        if k:
            notes.append(f'{c["name"]}: dependsOn chain to {prefix}Provisioner0 not found (skipped)')
            continue
        pd = {u for v in cur['propdeps'].values() for u in v}
        cands = [u for u in cur['deps'] if u in urn2res and u not in pd] or [u for u in cur['deps'] if u in urn2res]
        caddrs = list(dict.fromkeys(urn2res[u]['caddr'] for u in cands))
        if len(caddrs) > 1:
            pre = {urn2res[u]['caddr']: len(camel(urn2res[u]['base'])) for u in cands
                   if prefix.startswith(camel(urn2res[u]['base']))}
            caddrs = [a for a, n in pre.items() if n == max(pre.values())] if pre else []
        if len(caddrs) != 1:
            notes.append(f'{c["name"]}: parent resource not determined (skipped)')
            continue
        out[caddrs[0]].setdefault(i, c)          # a for_each parent has one command per instance and provisioner
    return out


def self_refs(segs):
    """R-TF-35 with the subject `self`: the full traversal, then shorter ones, then `self` (no keyed form)."""
    return ['self' + ''.join(segs[:k]) for k in range(len(segs), 0, -1)] + ['self']


def prov_refs(occs, deps, parent, variant, urn2res, lang):
    """References of one provisioner argument, built as in refs_from_occurrences (P3src: one traversal per program
    text occurrence, then a guessed '.id' per mapped target without text evidence; P3id: '.id' per mapped target).
    The difference is that the parent resource is written as `self`, since the converter rewrote `self.x` to `<parent>.x`."""
    deps = list(dict.fromkeys(u for u in deps if u in urn2res))
    out, used, self_done = [], set(), False

    def refs(u, segs, dyn=False):
        t = urn2res[u]
        return self_refs(segs) if t['caddr'] == parent else ref_strings(t, segs, None, [], urn2res, dyn)

    if variant == 'P3src':
        for o in sorted(occs, key=lambda o: o['pos']):
            cands = [u for u in deps if target_key(urn2res[u]) == o['target']]
            if not cands:
                continue
            ix = (o['index'] or '').strip('[] ')
            if ix.isdigit():
                cands = [u for u in cands if urn2res[u]['index'] == int(ix)] or cands
            u = cands[0]
            used.add(u)
            self_done = self_done or urn2res[u]['caddr'] == parent
            out += refs(u, tf_traversal(urn2res[u], o['steps'], lang), bool(ix) and not ix.isdigit())
    for u in sorted([u for u in deps if u not in used], key=lambda u: urn2res[u]['address']):
        if urn2res[u]['caddr'] == parent:
            if self_done:
                continue                          # all instances of a counted parent share the one subject `self`
            self_done = True
        out += refs(u, ['.id'])
    return out


def provisioner_blocks(cmds, urn2res, variant, prog, lang, notes):
    """v2 fix A: {parent config address: [{"type": "local-exec", "expressions": {...}}, ...]}, ordered by <i>, for
    the configuration variants (P2/P3id/P3src). Expressions follow the variant's rules for resource arguments: no
    constant_value when propertyDependencies is non-empty (R-PU-21) or the value is a secret (R-PU-10). There P2
    writes {} and P3 writes references (R-TF-35). P3src also applies the literal check (R-TF-32/33)."""
    if variant == 'P1' or not cmds:
        return {}
    out = {}
    for parent, by_i in provisioner_parents(cmds, urn2res, notes).items():
        if sorted(by_i) != list(range(len(by_i))):
            notes.append(f'{parent}: provisioner positions {sorted(by_i)} (others are not local-exec)')
        blocks = []
        for i in sorted(by_i):
            c = by_i[i]
            ins = c['inputs']
            destroy = ins.get('create') == 'true' and ins.get('update') == 'true' and 'delete' in ins   # L2697-L2706
            src = {'command': 'delete' if destroy else 'create', 'interpreter': 'interpreter',
                   'environment': 'environment'}
            written = list(c['propdeps']) if c['propdeps'] else [k for k in ins if k not in META and
                                                                   k not in set(ins.get('__defaults') or [])]
            occ, lits = [], {}
            if prog is not None and prog.ok:
                occ = prog.occurrences(c['type'], c['name']) or []
                lits = prog.top_level_args(c['type'], c['name']) or {}
            ex = OrderedDict()
            for tk, ty in LOCAL_EXEC.items():
                pk = src[tk]
                if pk not in written:
                    continue
                raw_deps = c['propdeps'].get(pk) or []
                if raw_deps:
                    if variant.startswith('P3'):
                        tocc = [o for o in occ if o['keys'] and norm_key(o['keys'][0], lang) == pk]
                        refs = prov_refs(tocc, raw_deps, parent, variant, urn2res, lang)
                        ex[tk] = {'references': refs} if refs else {}
                    else:
                        ex[tk] = {}
                elif pk not in ins:
                    continue
                elif variant == 'P3src' and pk in lits and not prog.is_literal(*lits[pk]):
                    ex[tk] = {}
                else:
                    ex[tk] = const_expr(program_value(ins[pk]), ty, _PROV_NAMES, False, set())
            blk = OrderedDict([('type', 'local-exec')])
            if ex:
                blk['expressions'] = OrderedDict(sorted(ex.items()))     # omitempty (config.go L117-L120)
            blocks.append(blk)
        out[parent] = blocks
        notes.append(f'{parent}: {len(blocks)} local-exec provisioner(s) rebuilt from command:local:Command (v2 fix A)')
    return out


# ============================================================================================ reverse shapes
NON_MANAGED = ('var.', 'local.', 'each.', 'path.', 'self.', 'terraform.', 'data.', 'module.')   # count.index kept


def strip_refs(o):
    """R-P2: drop every `references` list, keep the rest."""
    if isinstance(o, dict):
        return {k: strip_refs(v) for k, v in o.items() if k != 'references'}
    if isinstance(o, list):
        return [strip_refs(v) for v in o]
    return o


def filter_refs(o):
    """R-P3: keep only references to managed resources (and count.index); drop a list that ends up empty."""
    if isinstance(o, dict):
        out = {}
        for k, v in o.items():
            if k == 'references' and isinstance(v, list):
                keep = [s for s in v if not s.startswith(NON_MANAGED)]
                if keep:
                    out[k] = keep
            else:
                out[k] = filter_refs(v)
        return out
    if isinstance(o, list):
        return [filter_refs(v) for v in o]
    return o


def reverse_shape(tfplan, shape):
    """Sanity check of the shapes: our Terraform control plan cut down to what a variant can carry. R-P1 has the
    P1 sections, R-P2 adds the configuration without references, R-P3 keeps references to managed resources only."""
    pv = copy.deepcopy(tfplan.get('planned_values') or {})
    rm = pv.get('root_module') or {}
    rm['resources'] = [r for r in rm.get('resources', []) if r.get('mode') == 'managed']   # the adapter has no data sources (N2)
    p = OrderedDict([('format_version', tfplan.get('format_version')),
                     ('terraform_version', tfplan.get('terraform_version')),
                     ('planned_values', pv),
                     ('resource_changes', [r for r in tfplan.get('resource_changes', []) if r.get('mode') == 'managed']),
                     ('timestamp', tfplan.get('timestamp'))])
    if shape == 'R-P1':
        return p
    conf = tfplan.get('configuration') or {}
    pc = OrderedDict()
    for key, e in (conf.get('provider_config') or {}).items():        # every entry (R-TF-21), no version_constraint
        ne = OrderedDict((k, e[k]) for k in ('name', 'full_name', 'alias') if k in e)
        if 'expressions' in e:
            ne['expressions'] = strip_refs(e['expressions']) if shape == 'R-P2' else filter_refs(e['expressions'])
        pc[key] = ne
    resources = []
    for r in (conf.get('root_module') or {}).get('resources', []):
        if r.get('mode') != 'managed':
            continue
        r = copy.deepcopy(r)
        if shape == 'R-P2':
            r['expressions'] = strip_refs(r.get('expressions') or {})
            r.pop('depends_on', None)
            if 'count_expression' in r:
                r['count_expression'] = strip_refs(r['count_expression'])
            if 'for_each_expression' in r:
                r['for_each_expression'] = strip_refs(r['for_each_expression'])
        else:
            r['expressions'] = filter_refs(r.get('expressions') or {})
            if 'depends_on' in r:
                r['depends_on'] = [s for s in r['depends_on'] if not s.startswith(NON_MANAGED)]
                if not r['depends_on']:
                    r.pop('depends_on')
            for k in ('count_expression', 'for_each_expression'):
                if k in r:
                    r[k] = filter_refs(r[k])
        resources.append(r)
    p['configuration'] = {'provider_config': pc, 'root_module': {'resources': resources}}
    return p


# ============================================================================================ OPA
def bool_leaves(v, path=''):
    """(path, value) of every boolean in the OPA result, i.e. the boolean rules of intent.rego."""
    if isinstance(v, bool):
        yield path, v
    elif isinstance(v, dict):
        for k, x in v.items():
            yield from bool_leaves(x, path + '/' + str(k))


def run_opa(plan, task, tag):
    """Check one plan as the original code does: write it to out_fixed/, run the same OPA 1.1.0 command on the
    task's unchanged intent.rego and pass the result to extract_validation_status from the original code.
    Returns the pass flag, the OPA error text (if any) and the boolean rule values."""
    os.makedirs(OUT, exist_ok=True)
    path = f'{OUT}/{task}-{tag}.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=1)
    rego = f'{DATASET}/{task}/intent.rego'
    p = subprocess.run([OPA, 'eval', '-i', path, '-d', rego, 'data'], capture_output=True, text=True)
    try:
        val = json.loads(p.stdout)['result'][0]['expressions'][0]['value']
    except Exception:
        return {'pass': False, 'error': (p.stderr or p.stdout)[:300].replace('\n', ' '), 'bools': {}}
    return {'pass': bool(extract_validation_status(val)), 'error': '', 'bools': dict(bool_leaves(val))}


# ============================================================================================ main
def rule_diff(ctrl_b, b):
    """All boolean rule leaves whose value differs from the control run (both directions, 'u' = undefined)."""
    out = []
    for k in sorted(set(ctrl_b) | set(b)):
        c, a = ctrl_b.get(k, 'u'), b.get(k, 'u')
        if c != a:
            out.append(f"{k.rsplit('/', 1)[-1]}:{str(c)[0]}->{str(a)[0]}")
    return ';'.join(out)


def read_csv(p):
    return {r['task']: r for r in csv.DictReader(open(p, encoding='utf-8'))}


def main():
    """Pilot run. Control group first: the original check on our Terraform plan of each task's reference main.tf
    (CTRL), on {} (EMPTY) and on the three reverse shapes. Then every adapter variant in both value modes, for
    each task and language where both the Pulumi preview and the Terraform plan succeeded. Writes results_fixed.csv."""
    tasks = [t.strip() for t in open(TASKS_FILE) if t.strip()]
    tf = read_csv(f'{PILOT}/results_tf.csv')
    rows, ctrl_cache = [], {}
    for t in tasks:
        cp = f'{PILOT}/{t}/terraform/plan.json'
        if not os.path.exists(cp):
            continue
        tfplan = json.load(open(cp, encoding='utf-8'))
        ctrl = run_opa(tfplan, t, 'CTRL')
        ctrl_cache[t] = (tfplan, ctrl)
        empty = run_opa({}, t, 'EMPTY')
        for shape in ('R-P1', 'R-P2', 'R-P3'):
            r = run_opa(reverse_shape(tfplan, shape), t, 'tf-' + shape)
            rows.append({'task': t, 'lang': 'terraform', 'mode': 'control', 'variant': shape, 'pass': r['pass'],
                         'control_pass': ctrl['pass'], 'control_tf_opa_csv': tf[t]['tf_opa'],
                         'empty_pass': empty['pass'], 'eligible': '', 'error': r['error'],
                         'false_rules': ';'.join(k for k, v in r['bools'].items() if not v and ctrl['bools'].get(k) is True),
                         'rule_diff': rule_diff(ctrl['bools'], r['bools']), 'notes': ''})
        rows.append({'task': t, 'lang': 'terraform', 'mode': 'control', 'variant': 'CTRL', 'pass': ctrl['pass'],
                     'control_pass': ctrl['pass'], 'control_tf_opa_csv': tf[t]['tf_opa'], 'empty_pass': empty['pass'],
                     'eligible': '', 'error': ctrl['error'], 'false_rules': '', 'rule_diff': '', 'notes': ''})
    for lang in ('typescript', 'python'):
        pu = read_csv(f'{PILOT}/results_{lang}.csv')
        for t in tasks:
            if pu[t]['preview_ok'] != 'True' or tf[t]['tf_plan'] != 'True':
                continue
            tfplan, ctrl = ctrl_cache[t]
            elig = ctrl['pass']
            empty_pass = [r for r in rows if r['task'] == t and r['variant'] == 'CTRL'][0]['empty_pass']
            for mode in ('preview', 'plan'):
                for variant in ('P1', 'P2', 'P3id', 'P3src'):
                    plan, notes = adapt(t, lang, mode, variant)
                    r = run_opa(plan, t, f'{lang}-{mode}-{variant}')
                    false_rules = [k for k, v in r['bools'].items() if not v and ctrl['bools'].get(k) is True]
                    missing_rules = [k for k, v in ctrl['bools'].items() if v is True and k not in r['bools']]
                    rows.append({'task': t, 'lang': lang, 'mode': mode, 'variant': variant, 'pass': r['pass'],
                                 'control_pass': ctrl['pass'], 'control_tf_opa_csv': tf[t]['tf_opa'],
                                 'empty_pass': empty_pass, 'eligible': elig, 'error': r['error'],
                                 'false_rules': ';'.join(false_rules + ['undef:' + m for m in missing_rules]),
                                 'rule_diff': rule_diff(ctrl['bools'], r['bools']),
                                 'notes': ';'.join(dict.fromkeys(notes))})
    with open(RESULTS, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print('rows', len(rows))
    print('unresolved Pulumi names:', sorted(UNRESOLVED))
    print('Pulumi keys without a Terraform attribute (dropped from values):', sorted(DROPPED))


if __name__ == '__main__':
    main()
