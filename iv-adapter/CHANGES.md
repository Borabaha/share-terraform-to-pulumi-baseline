# Review of the IV adapter prototype against the two specs (15 Oct 2026)

> **Note for this repository.** This file was written in my working folder and is copied here unchanged apart from this note, one word in row 20 (now "the original plans"), and the git remarks in section "v2 (fixes A, B)", which now say that v1 (commit c447213) is in my working repository and not in this one. Paths are relative to that folder, where the adapter lived in `E-prototype/`. In this repository, `../specs/` is `specs/`, `tables/` is `tables/`, and `../full408/REPORT.md` is `results/full408/REPORT.md`. `../results` means the adapter's pilot outputs in my working folder, which are not included. The v1 and v2 sha256 values are those of the adapter file in my working folder; `iv_adapter.py` here has other paths and comments, so its hash differs. The line numbers (Lnnn) still match `iv_adapter.py` here. The helper scripts and outputs named below are not included: the prototype (`iv_adapter_proto*.py`), `conformance.py`, `compare_results.py`, `ablation.py`, `mutation.py`, `fidelity.py`, `final_tables.py`, `v2_check.py` with `v2_check/`, the pilot outputs `results_fixed.csv` and `out_fixed/`, `../full408/clusters/` and `../specs/src/`. The public sources are cited by URL at fixed tags.

**Baseline:** `iv_adapter_proto.recovered.py`, a byte-identical copy of the recovered `iv_adapter_proto.py` (sha256 `5f2c594c…`). It is kept unchanged.
**Reviewed version:** `iv_adapter.py`.

The review checked the code rule by rule against two specs:
- `../specs/terraform-plan-json.md` (R-TF-n): what Terraform 1.5.7 writes.
- `../specs/pulumi-side.md` (R-PU-n): what Pulumi gives the adapter.

The variant structure is unchanged (P1, P2, P3id, P3src, plus R-P1/R-P2/R-P3, CTRL and EMPTY). The OPA command and `extract_validation_status` are also unchanged.

No change was chosen or tuned by looking at which pilot rules pass or fail. To check that the code behaves as the specs say, I used `conformance.py`. It compares the adapter output with our Terraform control plan cut to the same shape (R-P3), field by field. It never runs OPA or `intent.rego`. OPA ran only at the end (`iv_adapter.py` → `results_fixed.csv`), twice. The first run's log showed that the generated-name walk (row 32) was descending into map values (`tags`, `triggers`), which showed up as unresolved names. I fixed that walk and ran again. No pass/fail result was looked at before the second run finished.

## Result

**Pass counts did not change.** Both preview mode and plan mode give TS P1/P2/P3id/P3src 8/10/16/16 of 17 and Py 10/12/18/18 of 20. That is the same as the prototype, with the same failing tasks: 3 in both languages, plus 90 in Python. R-P1/R-P2/R-P3 are also unchanged: TS 8/10/17, Py 10/12/19. CTRL still agrees with `results_tf.csv` on 30/30. Comparing `results.csv` with `results_fixed.csv`, 0 of 448 rows change verdict, and 0 rows change their rule-leaf diff (`compare_results.py`, `compare_results_out.txt`).

**The output is now much closer to a real Terraform plan.** The table below compares the output with our Terraform control plan in R-P3 shape, from `conformance.py` / `conformance.csv`. Each cell is old → new, and "/ n" is the total. Rows cover variants P2 and P3src. P3id has the same plan sections as P3src, except references.

| lang | mode | variant | values identical (per resource) | sensitive_values identical | after_unknown identical | after_sensitive identical | schema_version identical | expression kind agrees | references exact | every provider_config_key has an entry |
|---|---|---|---|---|---|---|---|---|---|---|
| TS | preview | P2 | 19→41 / 58 | 7→56 | 33→53 | 7→56 | 36→58 | 170→168 / 225 | – | 13→19 / 19 |
| TS | preview | P3src | 19→41 / 58 | 7→56 | 33→53 | 7→56 | 36→58 | 214→223 / 225 | 44→46 / 46 | 13→19 / 19 |
| TS | plan | P3src | 50→54 / 58 | 7→58 | 33→55 | 7→58 | 36→58 | 214→223 / 225 | 44→46 / 46 | 13→19 / 19 |
| Py | preview | P2 | 29→59 / 82 | 14→79 | 49→77 | 14→79 | 51→82 | 204→202 / 290 | – | 15→22 / 22 |
| Py | preview | P3src | 29→59 / 82 | 14→79 | 49→77 | 14→79 | 51→82 | 273→288 / 290 | 69→71 / 71 | 15→22 / 22 |
| Py | plan | P3src | 73→79 / 82 | 14→81 | 49→79 | 14→81 | 51→82 | 273→288 / 290 | 69→71 / 71 | 15→22 / 22 |

The expression-kind counts that went down in P2 (170→168 and 204→202) are the two RDS `password` constants, in tasks 3 and 408. The prototype emitted `{"constant_value": "[secret]"}`. That matched Terraform's kind but carried an invented value. R-PU-10 rules this out (row 30).

What is left in P3src:
- The two passwords (R-PU-10).
- The aliases dropped in task 3 (R-PU-25).
- In preview mode only: provider-side zero values and defaults (row N6).
- JSON formatting of policy documents (row N20).
- HCL literal types (row N7).
- Schema drift in task 432 (row N22).

`conformance.py detail <task> <lang> <mode>` prints the remaining differences field by field.

## How to run

```
cd iv-study/E-prototype
python tables/build_tf_schema.py      # Terraform 1.5.7 `providers schema -json` (aws 5.90.0, null 3.2.3, archive 2.7.0, random 3.7.1) from the local mirror
python tables/build_mappings.py       # `pulumi package get-mapping terraform` for null@0.0.10, random@4.18.0, archive@0.3.2
python tables/build_pulumi_defaults.py
python conformance.py                 # rule-independent comparison, old vs new (no OPA)
python iv_adapter.py                  # OPA run -> results_fixed.csv, out_fixed/
python compare_results.py             # pass counts, old vs new
```

The three table builders are already run, and their outputs are in `tables/`. None of them touch LocalStack, a stack or any state. `build_tf_schema.py` only runs `terraform init -backend=false` and `terraform providers schema -json`. It then deletes the unpacked provider binaries and keeps `tf_schema.json` and `tf_schema.lock.hcl`.

`ablation.py`, `mutation.py`, `fidelity.py` and `final_tables.py` are left as recovered, and they still read the prototype and its outputs.

## Rule-by-rule table

"Fixed" means the change is made in `iv_adapter.py`. "Not fixed" means the reason is given in the last column.

### Fixed (40)

| # | rule id | what the old code did | what the spec says (source) | change made |
|---|---|---|---|---|
| 1 | R-TF-2 | No `timestamp`. | All 426 plans have `timestamp` (R-TF-2; PLAN L49-66). | Added. It is the preview file's mtime in RFC 3339 (UTC), so it is deterministic. |
| 2 | R-TF-8, R-TF-24 | `schema_version` was always 0. | It is always present and equals the provider's resource schema version (R-TF-8, RES L34). For example, `aws_db_instance` is 2 in the control plans. | Taken from the Terraform provider schema (`tables/tf_schema.json`, aws 5.90.0), in both `planned_values` and `configuration`. Agreement went from 36→58/58 (TS) and 51→82/82 (Py). |
| 3 | R-TF-8 | `provider_name` was built from the prefix of the TF type. | It is the fully qualified provider of the resource (R-TF-8, D8). | Built from the provider package of the mapped token (`registry.terraform.io/hashicorp/<pkg>`). Pilot output is the same. |
| 4 | R-TF-8 | `values` was always written, even as `{}`. | `values` is `omitempty`. Terraform v1.5.7 `internal/command/jsonplan/resource.go` L40 (https://github.com/hashicorp/terraform/blob/v1.5.7/internal/command/jsonplan/resource.go#L40). Seen in task 296: when every attribute is unknown, `values` is missing. | `values` is left out when it is empty. `change.after` stays `{}`. |
| 5 | R-TF-9, R-PU-31 | `null_fill` used the Pulumi shim schema (upstream 5.90.1). It forced `id` to unknown on every resource. It forced `tags_all` to unknown. It kept Pulumi keys that have no Terraform attribute, renamed by snake-casing. | `values` holds every attribute of the **provider schema** (R-TF-9). Schema differences should be checked against `terraform providers schema -json` of 5.90.0 (R-PU-31, which says this "was not done"). | The 5.90.0 schema now drives every level. Unset computed attributes become unknown. Unset optional attributes become null. Unset list/set blocks become `[]`. Unset single blocks become null. Blocks the shim marks computed become unknown. `id` appears only where the schema has it. Keys not in the Terraform schema are dropped and logged (on the pilot: `aws_eks_cluster.certificate_authorities` and `default_addons_to_remove`). |
| 6 | R-TF-9 | `"timeouts": null` was added only in plan mode, through the timeouts key in Pulumi `__meta`. | `timeouts` is a single-nesting block in the schema, so it is null when unset (R-TF-9; task 283). | This now follows from row 5 in both modes. The `__meta` workaround was removed. |
| 7 | R-TF-9, R-TF-29, R-PU-28 | Every value whose shim element is `resource` was wrapped in a list. That included Plugin-Framework single nested blocks (shim type 6). | Single blocks are an object in `values` (R-TF-9) and in `expressions` (R-TF-29). R-PU-28 left the Terraform side "not checked". The 5.90.0 schema has 5 such blocks with `nesting_mode: single` at the top level of managed resources (14 at any depth, not counting `timeouts`; count corrected in VERIFY.md). | The nesting mode comes from the Terraform schema: list/set give an array, single/group give an object, map gives a keyed object. This applies to values and to block expressions. |
| 8 | R-TF-10, R-PU-17 | Set values kept Pulumi program order. | Sets come out in cty order: strings bytewise, numbers numerically, false before true, other types by comparing their hash bytes. Source: go-cty v1.12.2 `cty/set_internals.go` `Less` L85-L135 and `appendSetHashBytes` L144-L260 (https://github.com/zclconf/go-cty/blob/v1.12.2/cty/set_internals.go#L85-L135). | `cty_set()` ports that order. It applies to every set attribute and set block at any depth, and equal elements collapse. In `configuration`, `constant_value` keeps source order (R-TF-10). |
| 9 | R-TF-11 | `sensitive_values` was always `{}`. | Same shape as `values`: true for sensitive leaves, one entry per list element, `[]`/`{}` for empty or unknown collections. Terraform `jsonstate/state.go` L486 `SensitiveAsBool`; `jsonplan/values.go` L230 uses the marked after-value without schema marks. | `sensitive_as_bool(..., marks=False)`. Agreement went from 7→56/58 (TS preview) and 14→79/82 (Py preview). |
| 10 | R-TF-12 | Resources were sorted naturally (`addr_sort_key`, so `x[2]` came before `x[10]`). | Sorted by the plain address string (VAL L240-242). | Plain string sort. |
| 11 | R-TF-13 | `resource_changes` used the same natural order. | `AbsResourceInstance.Less` sorts by mode (data before managed), then type, name and numeric key (RADDR). | `rc_sort_key()`. |
| 12 | R-TF-15, R-PU-4 | `actions` was `[op]` with the raw Pulumi op name (for example `["same"]`). | Terraform action lists (R-TF-15). | `OP2ACTIONS`: create, no-op, update, `[create, delete]` for replacements (Pulumi's default is create-before-delete), delete and read. Any op other than create also gets a note. The pilot has only creates (R-PU-4). |
| 13 | R-TF-17 | `after_unknown` kept only the unknown markers. Known lists and maps were dropped. | `unknownAsBool`: lists keep one entry per element, empty collections stay as `[]`/`{}`, and a wholly known after-value gives `{}`. Terraform `jsonplan/plan.go` L424-L440 and L737 (https://github.com/hashicorp/terraform/blob/v1.5.7/internal/command/jsonplan/plan.go#L424-L440). | `unknown_as_bool()`, with the wholly-known case handled. |
| 14 | R-TF-18 | `after_sensitive` was always `{}`. | Like R-TF-11, plus the schema's sensitive attributes (plan.go L442-L446). | `sensitive_as_bool(..., marks=True)`. Sensitive flags come from the Terraform schema. For example, `password` and `password_wo` are true, as in the control plans. |
| 15 | R-TF-21, R-TF-42.3 | `provider_config` held only `aws` with `region`, and only when the stack config had `aws:region`. 12 of the 60 pilot previews have no `aws:region`, so `provider_config` was `{}` while resources pointed at `"aws"`. Task 90 Py had no `null` entry. | Each provider key gets an entry with `name`, `full_name`, `alias` and `expressions`, and every `provider_config_key` must be a key of `provider_config` (R-TF-21, R-TF-42.3). | One entry per provider key the resources use. Its `expressions` come from every `<pkg>:*` stack config key, reverse-named through the get-mapping provider config schema and typed by the Terraform provider schema. For explicit provider resources (none in the pilot), they come from that resource's inputs. Coverage went from 13→19/19 (TS) and 15→22/22 (Py). As on the Terraform side (R-TF-21 observation), this includes the harness's LocalStack settings. |
| 16 | R-TF-22, R-PU-25 | `provider_config_key` was the prefix of the TF type. | It comes from the provider reference in `newState.provider`: a default provider gives `"<pkg>"`, and an explicit provider resource named N gives `"<pkg>.N"` (R-PU-25). | Implemented in `provider_key()`. |
| 17 | R-TF-23 | Configuration resources were sorted naturally. | Managed resources sorted by address string (CFG L516-519). | Plain string sort. |
| 18 | R-TF-24 | `expressions` was always written, even as `{}`. | `expressions` is left out when the block has no arguments (R-TF-24; 36/426 plans). | Left out when empty. |
| 19 | R-TF-28, R-PU-8, R-PU-18 | The set of written keys was the inputs minus `__defaults`, plus special cases for `tags_all` and the value "Managed by Pulumi". | The keys the program wrote are the `propertyDependencies` keys (R-PU-8, R-PU-18). `tagsAll` is never in `configuration` (R-PU-15). Only written arguments appear (R-TF-28). | `propertyDependencies` keys (falling back to inputs minus `__defaults` if missing), minus `tagsAll`, minus R-PU-14 defaults (row 33), minus computed-only Terraform attributes. Keys with no Terraform argument are dropped with a note. Nested levels still drop their own `__defaults` (R-PU-12). |
| 20 | R-TF-29, R-TF-30 | Block or attribute was decided from the shim (`element.resource`) plus `attr_blocks.json`. That table has 5 entries scanned from the original plans, and it misses `aws_default_security_group`. | Whether a field is an attribute depends on the provider **schema**, not on the syntax (R-TF-30). Attributes give one expression; blocks give nested block expressions (R-TF-29). | Decided from the Terraform schema. `block_types` give nested expressions. A configurable attribute of type list/set(object) gives one expression. There are 20 such top-level attributes in aws 5.90.0 managed resources (21 at any depth; the extra one is `aws_securitylake_data_lake` `configuration.encryption_configuration`; count corrected in VERIFY.md), including `aws_default_security_group.ingress/egress`, `aws_default_route_table.route` and `aws_emr_cluster.step`. The old 5 entries are a subset (checked). `attr_blocks.json` is no longer read. |
| 21 | R-TF-30 | In the all-constant attribute-as-block case, missing element attributes were filled with `[]` for nested blocks and null otherwise. | `constant_value` is a list of objects with every element attribute, missing ones null (R-TF-30). | Filled from the attribute's object type, with null for each missing attribute. |
| 22 | R-TF-32, R-TF-38 | In a counted group, instance 0's value became `constant_value` even when the instances had different values. | A literal gives the same value for every instance, so a per-instance value cannot be a `constant_value` (R-TF-32). Index-dependent expressions list `count.index` (R-TF-38; task 428 `cidr_block` gives `["count.index"]`). | If a top-level value with no dependencies differs between instances, P2 gives `{}` and P3 gives `{"references": ["count.index"]}`. On the pilot this fixes task 428 `aws_subnet.public` `cidr_block` and `availability_zone` in both languages, so exact P3src reference lists went from 44→46/46 (TS) and 69→71/71 (Py). |
| 23 | R-TF-32, R-TF-33 | Any known value with no dependencies got `constant_value`, including results of function calls (`JSON.stringify`/`json.dumps` for `jsonencode`), variables and template interpolation. | No `constant_value` for function calls, references or interpolation, and `{}` is legal. The adapter must not invent constants (R-TF-32/33). | **P3src only**, because P3src is the only variant that reads the program: `Program.is_literal()` classifies each top-level argument. Literals are strings without interpolation, numbers, bools, null, lists and objects of literals, enum members, and type conversions the converter puts around literals (`float(80)`, `Number("3")`). Anything else gives `{}`. Mismatches where Terraform had `{}` and the adapter a constant went from 9→0 (TS) and 15→0 (Py). |
| 24 | R-TF-35, R-TF-38, R-PU-28 | (P3src) The access-chain regex stopped at index steps. A literal index such as `x[1].id` still picked instance 0. A dynamic index was only handled by the same-index check. `[0]` was inserted after any list/set attribute. | References list the full traversal and then shorter ones, with keyed subjects such as `type.name[1]` (R-TF-35). A dynamic index ends the traversal (R-TF-38). Only attributes Pulumi flattened (MaxItemsOne) lose their `[0]` (R-PU-28). | Index steps are parsed. A literal index picks the matching instance. A dynamic index gives `[type.name]` unless the `count.index` pattern applies. `[0]` is inserted only after flattened MaxItemsOne attributes. No pilot reference list changes through this row: the pilot has no literal-index or index-chain references to resources. It matters for the hold-out set. |
| 25 | R-TF-25, R-PU-19 | `depends_on` was a natural sort of addresses. | It is `dependencies` minus all `propertyDependencies` (R-PU-19), as written in source order (R-TF-25). The Node SDK keeps `dependsOn` insertion order (`sdk/nodejs/runtime/resource.ts` L1003-L1006, L1088-L1100). The Python SDK builds a `set` (`sdk/python/lib/pulumi/runtime/resource.py` L276-L282; local copies in `specs/src/pulumi`). | TS keeps the order of `dependencies`. Python sorts by address, because a set has no source order. |
| 26 | R-PU-3 | Error diagnostics were not looked at. | A failed preview still writes a digest with partial steps. Eligibility comes from the exit code or the diagnostics (R-PU-3). | A note is added when a diagnostic has severity error. Eligibility still comes from `results_<lang>.csv`. |
| 27 | R-PU-6, R-PU-24 | Tokens were mapped through bridge-metadata `current`/`past`, with a `<pkg>_<snake(name)>` fallback, a special case for `null` and a forced `aws:s3/bucket:Bucket → aws_s3_bucket` default. | Token ↔ TF type comes only from the mapping (R-PU-24). Only custom resources are TF resources, and provider resources are read for R-PU-25 (R-PU-6). | Only get-mapping tokens (aws 6.72.0, null 0.0.10, random 4.18.0, archive 0.3.2). An unmapped custom resource (`command:local:Command`) is skipped with a note, and its URN still counts for R-PU-21. Provider resources are collected for R-PU-25. |
| 28 | R-PU-9 | Only the sentinel `04da6b54-…` counted as unknown. | Accept all 7 unknown sentinels, as a defensive measure (R-PU-9; `sdk/go/common/resource/sig/sig.go` L44-L78). | `UNKNOWNS` holds all 7. |
| 29 | R-PU-9 | A set with an unknown element became wholly unknown only at the top level. | When a TF **set** holds an unknown element, the whole attribute is unknown (R-PU-9 granularity caveat; 11 pilot cases). Set blocks stay element-wise (R-TF-17, task 428 `route`). | Applied to primitive-element sets at any depth (`cty_set`). |
| 30 | R-PU-10 | Secrets became `{"constant_value": "[secret]"}` in `configuration` and the string `"[secret]"` in `planned_values`. | The key exists but has no `constant_value`, and its value must never be compared or used (R-PU-10). | `configuration` gives `{}`. In `planned_values` the value is treated as not visible: it is left out and `after_unknown` is true. It is also carried as a value mark into `sensitive_values`/`after_sensitive`, except on schema-sensitive attributes, which Terraform marks only in `after_sensitive` (R-TF-11/18). In plan mode, a secret wrapper around an attribute the program never set (`additionalSecretOutputs`) is dropped, so row 5 decides its value. Example: RDS replica `password`, which is null in Terraform. |
| 31 | R-PU-11 | Only asset and archive signatures were handled. | Signature objects for resource references, byte strings and float NaN/Inf (R-PU-11), plus output values (`sig.go`). | `norm_pulumi()` handles all of them. A resource reference gives its `id`, or unknown. An output value gives its value, or unknown/hidden. A byte string is base64-decoded. NaN/Inf give unknown. |
| 32 | R-PU-13 | Generated names were found from get-mapping `autonamed` **or** a regex guess (`looks_autoname`: logical name, optional `-`, 7 hex characters), and only at the top level. They were propagated by matching equal strings in every resource. | Every `__defaults` key whose get-mapping default is `autonamed` or `isFunc` is "not configured, unknown in plan". Downstream values whose `propertyDependencies` point at the generating resource are references, never constants (R-PU-13, R-PU-21). | `autonamed` or `isFunc` at every object level, with no regex. In `planned_values`, a generated name becomes unknown only in keys whose `propertyDependencies` point at the generating resource (strings that contain it). In `configuration`, such values never become constants. |
| 33 | R-PU-14 | Every string equal to "Managed by Pulumi" became "Managed by Terraform" in all values, and any configuration key with that value was skipped. | Keep a list of the Pulumi-only defaults from the package schema and get-mapping `default.value`. Treat them as defaults (no expression), and do not take their value as the TF value (R-PU-14). | `tables/pulumi_only_defaults.json`: the 16 fields, cross-checked between get-mapping and the package schema. Their Terraform defaults are cited from terraform-provider-aws v5.90.0 source (URL and lines in the file; for example `route53/zone.go#L50-L53`). 15 are "Managed by Terraform". `aws_db_parameter_group` `parameter.apply_method` is "immediate" on both sides. Applied per (type, path) in `planned_values`, and skipped in `configuration`. |
| 34 | R-PU-21 | Whether to emit a constant was decided from `propertyDependencies` already filtered to mapped targets. A dependency on a skipped resource therefore produced a constant. | Never emit `constant_value` for a key whose `propertyDependencies` is non-empty (R-PU-21). | The raw list decides. References are made only for mapped targets. If none is mapped, the result is `{}`. |
| 35 | R-PU-23 | Count groups were detected by base name only, without the type. | Pairing must include the TF type (R-PU-23; task 428 has `public` and `public-<i>`). | Detection keys on (TF type, base). |
| 36 | R-PU-26, R-PU-28, R-PU-30 | MaxItemsOne came from `bridge-metadata.json`. | get-mapping is authoritative. MaxItemsOne = list/set and (override `maxItemsOne` if set, else `maxItems == 1`). bridge-metadata is a build-time record (R-PU-26/28/30). | get-mapping rule (`is_mio`). bridge-metadata is no longer read. The two sources agree on every field (R-PU-30), so values stay the same. |
| 37 | R-PU-27 | Reverse names were guessed: camelCase plus `s`/`es`/`ies` candidates, with a snake-case fallback. | Invert the bridge's forward algorithm (override, pluralize unless MaxItemsOne, camelCase) and never singularize heuristically (R-PU-27). The heuristic is wrong on 23 of 115,455 names. | Port of inflector v0.1.1 and `terraformToPulumiName`, from `specs/validate_reversal.py` (52,261 of 52,264 names correct there), inverted per object level. Unresolved names are logged: 0 on the pilot. |
| 38 | R-TF-10, R-TF-32 | `constant_value` was coerced to the TF schema type (`conv_value`). | `constant_value` is the HCL value, not the provider-typed value (R-TF-10, R-TF-32). | No coercion in `configuration`. The Pulumi program value is used, renamed and wrapped for MaxItemsOne. Coercion stays in `planned_values`, which the schema types (R-TF-9). |
| 39 | R-TF-21 (reverse shapes) | R-P2/R-P3 kept only `provider_config.aws.expressions.region`. | The reverse shapes cut the control plan down to what each variant can carry. The adapter now writes every provider entry (row 15). | R-P2/R-P3 keep every control `provider_config` entry: `name`, `full_name`, `alias`, and `expressions` with references stripped (R-P2) or filtered (R-P3). `version_constraint` is dropped because the adapter cannot know it (N8). R-shape pass counts are unchanged. |
| 40 | (docs) | The docstring listed `rule_diffs.csv` and `attr_recovery.csv`, which the code never writes. | – | The docstring now matches the outputs (`results_fixed.csv`, `out_fixed/`). |

### Not fixed (25)

| # | rule id | what the old code did (and still does) | what the spec says (source) | why not fixed |
|---|---|---|---|---|
| N1 | R-TF-2 | No `relevant_attributes`. | It is present in 329/426 plans (R-TF-2). | It is derived from the references, including data sources the adapter cannot see (R-PU-20). The spec lists no rule that uses it. |
| N2 | R-TF-3, R-TF-7, R-TF-13 | No data sources: no `prior_state`, and no data entries in `planned_values` or `resource_changes`. | Data sources read at plan time go to `prior_state`. Deferred reads appear with action `read`. | Data sources become invokes, which have no step, URN or state (R-PU-20). The spec lists 0/458 rules for `mode == "data"` in `planned_values` and 1/458 for `prior_state`. |
| N3 | R-TF-4 | No `variables`. | Caller values plus declared defaults (R-TF-4). | Converted variables become config reads. The digest's `config` holds only values set in the stack, and defaults live in program text. The spec lists about 3/458 rules and 0 in the pilot. |
| N4 | R-TF-5 | No outputs. | Root outputs (R-TF-5). | A preview has no outputs (R-PU-7). The spec lists about 1/458 rules. |
| N5 | R-TF-6, R-TF-41, R-PU-23 | Everything is placed in the root module. The `${name}-` prefix of component children is not removed. | Child modules, module addresses and module-relative configuration addresses. | No adapter input in the pilot has modules or components. Five pilot tasks (330, 334, 335, 337, 338) do use `module "vpc"`, but their Pulumi previews failed in both languages (`preview_ok` False), so the adapter never sees them (corrected in VERIFY.md; the earlier text said no pilot task has modules). The converter emits components. A note is now written when a resource's parent is not the stack. The spec lists 0/458 rules for `child_modules`. This should be revisited for the hold-out set (26/426 plans have modules). |
| N6 | R-TF-9 | In **preview** mode, nested elements of SDKv2 resources get null where Terraform shows zero values (`""`, `[]`), for example in `route`, `cors_rule` and lex `slot`. Provider-side defaults that are missing from the preview inputs (for example `aws_vpc.instance_tenancy = "default"`) are null too. | `values` holds the provider's planned value (R-TF-9). | The provider computes these values, and they are not in the preview inputs. Neither spec states a rule for them, and the control plans mix `""` and null (`cors_rule.id` is `""`, `max_age_seconds` is null). Plan mode has the provider's real values (saved-plan state, R-PU-33): `values` identical 54/58 (TS) and 79/82 (Py). |
| N7 | R-TF-10, R-TF-32 | `constant_value` has the type of the Pulumi program value, for example `60` where HCL wrote `"60"` (task 3 `ttl`, task 83). | `constant_value` is the HCL literal value. | The converter writes typed SDK values, so the HCL literal type is gone. `const_equal_coerced` stays at 6 in both languages. |
| N8 | R-TF-21 | No `version_constraint`. | The resolved constraint (R-TF-21). | It is not in any Pulumi artefact. No rule uses it. |
| N9 | R-TF-21 | No entry for providers used only by data sources (for example `archive` in task 156 Py). | Required providers get an entry. | Data sources are invisible (R-PU-20). |
| N10 | R-TF-22, R-PU-25 | Task 3 resources get `provider_config_key` `"aws"`. | `aws.<alias>`. | Converter v1.4.0 drops aliased provider blocks (R-PU-25, CV `tf.go` L4643-L4652). This is a translation defect, not an adapter defect. The adapter would emit `aws.N` for an explicit provider resource. |
| N11 | R-TF-24 | No `provisioners`. The `command:local:Command` resource is skipped. | `provisioners` is optional on configuration resources. | Neither spec has a rule for mapping the converter's provisioner resources back to `provisioners`. A sound mapping would need its own spec entry (converter `tf.go`). |
| N12 | R-TF-26 | `count_expression` is `{"constant_value": N}`, with N = number of instances. | `constant_value` only for a literal `count`; otherwise references such as `local.subnet_count`. | The preview cannot show where the count came from. In P3src it could be read from the loop bound, but local/var references are outside the R-P3 shape (N16). The spec lists 0/458 rules. |
| N13 | R-TF-31 | Blocks that the converter expanded from `dynamic` blocks appear as normal blocks. | `dynamic` blocks are not represented. | They cannot be told apart in the preview. Rare. |
| N14 | R-TF-32, R-TF-33 | In P2 and P3id, a known value with no dependencies still becomes a constant even when Terraform used a function call or variable. | No constants for function calls or references. | By definition these variants use preview data only. In the preview, a `jsonencode` result looks the same as a heredoc literal. Row 23 fixes this where program text is available (P3src). |
| N15 | R-TF-32, R-TF-33 | In P3src, the literal check covers top-level arguments only. | It applies to arguments inside nested blocks too. | Nested argument spans would need a fuller parser. No nested mismatch of this kind is left in the pilot conformance check. |
| N16 | R-TF-35, R-TF-36, R-PU-20 | No `data.*`, `var.*` or `local.*` reference strings. | References use the full subject grammar. | Keeping variant P3 means keeping references to managed resources only. R-P3 filters these prefixes out (`NON_MANAGED`). Data references would also need data blocks in `configuration`, so a separate variant would be the place for it. |
| N17 | R-TF-35, R-TF-37, R-PU-18 | P3id writes one `.id` traversal per target, so attribute names are guessed and repeats are missing. | The real attribute, with no deduplication. | This is the design of P3id (attribute guessed as `id`). P3src recovers both. |
| N18 | R-TF-39 | `for` expressions and splats over counted resources are not detected. They give per-instance `.id` guesses. | Only the collection `type.name` is listed. | No pilot case. It would need loop and map detection in the program text. |
| N19 | R-TF-40, R-PU-23 | `for_each` instances (`<base>-<key>`) are not detected. | String keys `type.name["k"]`. | The pattern cannot be told apart from TF names that contain `-` without program text, and there is no pilot case (26/426 plans use `for_each`). |
| N20 | R-PU-16 | Policy and JSON strings keep the formatting the Pulumi program wrote. | R-PU-16 compares them semantically. It is pilot evidence, "not a cited rule". | Terraform's value depends on whether the source used `jsonencode` or a heredoc, which the preview cannot tell. |
| N21 | R-PU-21 | Under a key that has dependencies, known leaves of nested blocks stay constants. Only leaves derived from generated names are dropped. | Never a constant for a key whose `propertyDependencies` is non-empty. | `propertyDependencies` records the top-level key only (R-PU-18c), while Terraform splits nested blocks into one expression per argument (R-TF-29). Read strictly, the rule would drop literal nested arguments that Terraform does keep. |
| N22 | R-PU-31 | The adapter uses the aws 5.90.0 schema for every task. | Align versions (R-PU-31). | That is the provider line Pulumi uses (upstream 5.90.1). Task 432 (`~> 4.16`) was planned with aws 4.67.0, so `instance_id` and `enable_classiclink*` differ. The adapter does not see `main.tf`'s version constraint. |
| N23 | R-PU-33 | Plan mode uses the advisory `state` of the saved plan. | The format is experimental ([PREVIEW]). | The mode is kept so results stay comparable. Preview mode is the main mode. |
| N24 | R-PU-10 | Secret values are not recovered, even in P3src. | "Otherwise the value can only be recovered from program text." | P3src adds references and the literal check only. Taking values from program text would mix value recovery into a references variant. As a result, Terraform knows the `password` value but the adapter marks it unknown. |
| N25 | R-PU-11 | The bridge-filled asset hash field (`source_code_hash`) is not reproduced. | Assets map to the TF field via get-mapping `asset`. | The field name is mapped. The hash comes from a bridge computation that is not visible in the preview. One pilot archive (task 156 Py). |

## Files added in `E-prototype/`

- `iv_adapter_proto.recovered.py`: baseline, unchanged copy.
- `iv_adapter.py`: reviewed adapter. It writes `results_fixed.csv` and `out_fixed/` (478 JSON files) and leaves `results.csv` and `out/` untouched.
- `tables/build_tf_schema.py` → `tables/tf_schema.json` and `tables/tf_schema.lock.hcl`: Terraform provider schemas.
- `tables/build_mappings.py` → `tables/{null-0.0.10,random-4.18.0,archive-0.3.2}-terraform-mapping.json`.
- `tables/build_pulumi_defaults.py` → `tables/pulumi_only_defaults.json`: the R-PU-14 table with web citations.
- `conformance.py` → `conformance.csv` and `conformance_out.txt`: rule-independent comparison, old vs new.
- `compare_results.py` → `compare_results_out.txt`: pass counts and verdict changes, old vs new.
- `CHANGES.md`: this file.

## Web sources consulted for this review (15 Oct 2026)

These are in addition to the sources already cited in the two spec files.

- go-cty v1.12.2 set ordering: https://github.com/zclconf/go-cty/blob/v1.12.2/cty/set_internals.go#L85-L135 (`Less`) and #L144-L260 (`appendSetHashBytes`). Paraphrase: primitive types have a defined order, and every other type is ordered by comparing its serialized hash bytes.
- Terraform v1.5.7:
  - `internal/command/jsonplan/resource.go` L34 (`schema_version` is always written) and L40 (`values` is `omitempty`).
  - `plan.go` L424-L446: a wholly known after-value gives an empty `after_unknown`; otherwise `unknownAsBool`; `after_sensitive` adds the schema's marks.
  - `plan.go` L678 `omitUnknowns` and L737 `unknownAsBool`.
  - `values.go` L222-L230: planned values use the marked after-value without schema marks.
  - `jsonstate/state.go` L486 `SensitiveAsBool`.
- terraform-provider-aws v5.90.0 schema defaults for the 16 Pulumi-only defaults: the exact files and lines are in `tables/pulumi_only_defaults.json`, for example https://github.com/hashicorp/terraform-provider-aws/blob/v5.90.0/internal/service/route53/zone.go#L50-L53. Paraphrase: these optional description/comment arguments default to the text "Managed by Terraform".

## v2 (fixes A, B)

Date: 15 Oct 2026.

- **v1:** `iv_adapter.py` sha256 `98a53d94c75c931670efcb1d81474dd650a7dbc6cbd39ab54316cbcc4bfcd8b4` (commit c447213 in my working repository). This is the version every earlier number in this file and in `../full408/REPORT.md` comes from.
- **v2:** `iv_adapter.py` sha256 **`1d9f6f26e0316ecc9303c4b73af4c18d5a2176e6c298afeabfbfed657c0044d2`**. Like the v1 hash, this is the hash of the working-copy bytes (CRLF line ends). In that repository, git stores LF, because `core.autocrlf` is true.

The file was edited in place; v1 is kept in my working repository only, not in this one. Only fixes A and B were made, as proposed in `../full408/REPORT.md` §4. Nothing else changes behaviour; the regression diff below shows this. The only signature change is an optional `prog=None` argument on `ref_expr`. `load_preview()`, `reverse_shape()`, the OPA call and `extract_validation_status` are unchanged.

### Fix A: provisioners rebuilt from `command:local:Command` (lifts N11)

**What v1 did.** `command:local:Command` has no Terraform type (R-PU-24), so v1 skipped it with a note. `provisioners` was never written (N11). N11 said a sound mapping would need its own spec entry; the entry is the source analysis below.

**What v2 does.** Three new functions build the field: `load_commands()` (L706), `provisioner_parents()` (L1824) and `provisioner_blocks()` (L1899), with `prov_refs()` and `self_refs()` as helpers. `adapt()` (L1336, L1349) writes `provisioners` on the parent's configuration resource in variants P2, P3id and P3src. The field comes right after `provider_config_key`, which is where Terraform puts it.

1. **Parent.** The adapter follows the `dependsOn` chain `<p>Provisioner<i>` → `<p>Provisioner<i-1>` down to `i = 0`. The `dependsOn` target of provisioner 0 is the parent.
   - `dependsOn` is `dependencies` minus every `propertyDependencies` URN (R-PU-19).
   - If the parent is also referenced in a property (`self.x`), that difference is empty. The mapped `dependencies` are used instead, with the PCL name prefix as a tie-break.
   - All instances of a counted parent collapse to its configuration address.
   - If the chain or the parent cannot be determined, the command is skipped and a note is written.
2. **Order.** Provisioners are ordered by `<i>`. A gap in the positions, for example where a provisioner was not local-exec, gets a note.
3. **Block.** Each provisioner becomes `{"type": "local-exec", "expressions": {...}}`. `expressions` is left out when it is empty.
4. **Command source.** `command` comes from `delete` when `create` and `update` are both `"true"` (a destroy-time provisioner). Otherwise it comes from `create`. `interpreter` and `environment` are copied under their own names.
5. **Expressions.** These follow the variant's existing rules for resource arguments:
   - **P2:** `{}` when the key has `propertyDependencies` (R-PU-21). Otherwise `constant_value`, or `{}` for a secret (R-PU-10).
   - **P3id:** one guessed `.id` traversal per mapped target, as in N17.
   - **P3src:** traversals from the program text inside the Command constructor. A guessed `.id` is added for each mapped target without text evidence, and the literal check (R-TF-32/33) applies to keys without dependencies.
   - **The parent in P3:** written as `self`, following R-TF-35/36: `["self.name", "self"]`, with no keyed form. P3id therefore gives `["self.id", "self"]`.
   - **Data sources:** `data.*` references are not written (N16).

**Sources** (each verified at the tag):

- **pulumi-converter-terraform v1.4.0 `pkg/convert/tf.go`.** This is the local copy `../specs/src/converter/pkg/convert/tf.go`, compared with https://github.com/pulumi/pulumi-converter-terraform/blob/v1.4.0/pkg/convert/tf.go on 15 Oct 2026 for the functions below.
  - L3796-L3800: one converted resource per provisioner block, in block order.
  - L2582-L2618: `local-exec` dispatches to `convertLocalExecProvisioner`.
  - L2661-L2663: the name is `<parent PCL name>Provisioner<i>` and the type is `command:local:Command`.
  - L2620-L2651, `provisionerDependsOn`: `[parent]` for `i == 0`, otherwise `[<parent>Provisioner<i-1>]`. A for_each parent gives `[for _r in …]`.
  - L2679-L2681 together with L1625-L1628: `self.<attr>` becomes `<parent>.<attr>`.
  - L2683-L2696: only `command`, `interpreter` and `environment` are read.
  - L2697-L2706: when `when = destroy`, `create` and `update` are set to `"true"` and `delete` holds the command. Otherwise `create` holds it.
  - L2708-L2714: `interpreter` and `environment` are copied.
- **Terraform v1.5.7 `internal/command/jsonconfig/config.go`** (https://github.com/hashicorp/terraform/blob/v1.5.7/internal/command/jsonconfig/config.go):
  - L89-L91: `provisioners` sits between `provider_config_key` and `expressions`, and is `omitempty`.
  - L117-L120: the `provisioner` struct has only `type` and `expressions`, both `omitempty`.
  - L486-L498: `Expressions = marshalExpressions(p.Config, schemas.ProvisionerConfig(p.Type))`, in block order.
  - So `when`, `on_failure` and `connection` (L90: "Connection info will not be included here") never appear in the plan JSON.
- **Terraform v1.5.7 `internal/builtin/provisioners/local-exec/resource_provisioner.go` L44-L66:** the local-exec schema is `command` (string, required), `interpreter` (list(string)), `working_dir`, `environment` (map(string)) and `quiet`. The converter drops `working_dir` and `quiet`, so the adapter cannot recover them.
- **Terraform v1.5.7 `internal/addrs/parse_ref.go` L261-L266:** the root `self` gives subject `addrs.Self`, whose `String()` is `"self"`, plus the remaining traversal. That yields `["self.<attr>", "self"]` (R-TF-35). The control plans of 87 and 89 show this form.
- **Spec rules:** R-TF-24 (`provisioners` is an optional config resource field), R-TF-28/32/33/34/35/36, R-PU-19, R-PU-21, R-PU-10. This is consistent with R-PU-24, because the Command is still not a TF resource, and with N16.

**Coverage.** A scan of all preview files in the 5 run folders found 17 `command:*` resources. All of them are `command:local:Command`, in tasks 87 (TS and Py), 89 (TS and Py) and 90 (Py). `command:remote:*` resources (remote-exec and file provisioners) are not reproduced. They get a note, and none occur in the base set.

### Fix B: block-typed arguments hidden as a whole (R-TF-29)

**What v1 did.** If the preview value of a schema block type was not an object or list, `ref_expr` fell through to one attribute-style `{"references": [...]}` for the whole block (CHANGES row 20 conflict; `../full408/clusters/C4-pulumi-secret-masking.md`). The value can be wholly `"[secret]"` (R-PU-10) or unknown (R-PU-9). On the base set this happened only for task 15 Py `setting`.

**What v2 does.** A schema block type is never written as one attribute expression:
- **P3id:** writes `{}` (L1700). P2 already wrote `{}`.
- **P3src:** rebuilds the blocks from the program text, through `text_block_exprs()` (L1623), `text_const()` (L1600) and new `Program` methods: `object_fields`, `literal_items` and `literal_value` (L958-L1027), plus a small TypeScript literal reader, `_ts_literal` (L1029). It builds one block-expressions object per element of the argument's list literal, in source order (R-TF-29). A single object literal counts as one block (single or flattened MaxItemsOne, R-PU-28).
- **Leaves in P3src:**
  - **References:** taken from the program-text occurrences inside the leaf's text, filtered to the key's `propertyDependencies` targets (R-PU-18; R-TF-35).
  - **Literals:** otherwise, a literal leaf (`Program.is_literal`) gets `constant_value`, evaluated from the text. That uses `ast.literal_eval` for Python and `_ts_literal` for TS.
  - **`{}`:** everything else, including enum members, type conversions, calls and interpolation (R-TF-32/33).
  - **Schema-sensitive leaves:** also `{}`, so no secret value is taken from program text (consistent with row 30 and N24).
  - **Nested blocks:** handled by recursion. Map nesting gives `{}`.
  - **Fallback:** if the argument text is not a list or object literal (for example a computed list), the result is `{}`.
- **No-dependency branch:** P3src uses the same rebuild when the hidden key has no `propertyDependencies`. v1 wrote `{}` there. On the base set this branch changes no output: the regression diff shows no change outside the listed rows.

**Sources:** R-TF-29 (NestingList/Set gives an array of block-expressions objects in source order; EXPR L125-153), R-PU-10 (a secret's value can only come from program text), R-PU-18 (`propertyDependencies` has no nested path) and R-TF-32/33. This lifts N15 for this case only: nested argument spans are now parsed, but only where a block value is hidden as a whole. It follows the recipe in `../full408/clusters/C4-pulumi-secret-masking.md` "Suggested follow-up" 1.

### Effect

The checks are in `v2_check.py`, with outputs in `v2_check/`. The script ran OPA 1.1.0 with the unchanged `intent.rego` and `extract_validation_status`, in preview mode. No Pulumi or Terraform command was run.

**Unit check** (`v2_check/unit_check.csv`; the rule vector is compared with our CTRL run on the control plan):

| task | lang | P3src output vs control | P3src v1 → v2 | P3src rule vector == CTRL | P3id v1 → v2 | P2 v1 → v2 |
|---|---|---|---|---|---|---|
| 87 | TS | 4 `local-exec` provisioners on `aws_eks_cluster.example`, equal to the control's minus `data.*` references (N16) | fail → **pass** | False → **True** | fail → pass (vector == CTRL) | fail → fail |
| 87 | Py | same | fail → **pass** | False → **True** | fail → pass (vector == CTRL) | fail → fail |
| 89 | TS | same | fail → **pass** | False → **True** | fail → pass (vector == CTRL) | fail → fail |
| 89 | Py | same | fail → **pass** | False → **True** | fail → pass (vector == CTRL) | fail → fail |
| 15 | Py | `setting` is 4 block objects per environment, **identical** to the control (constants for `name` and `namespace`, references for `value`) | fail → **pass** | False → **True** | fail → fail (`{}`) | fail → fail |

**Regression diff over the whole base-set run** (`v2_check/regression.csv`, `v2_check/v2_check_out.txt`):
- All 2704 adapter inputs of `../full408` (TS 328 + Py 348 pairs × P1/P2/P3id/P3src) were rebuilt with v2. The JSON changed in **17** of them, and the other 2687 are identical to v1:
  - 87 and 89, TS and Py, in P2, P3id and P3src (12 inputs);
  - 15 Py, in P3id and P3src (2 inputs);
  - 90 Py, in P2, P3id and P3src (3 inputs).
- OPA was re-run on the changed inputs, with 0 errors. Unchanged inputs keep their v1 result.
- **90 Py** now carries `null_resource.k8s_patcher.provisioners`. In P3src it equals the control minus the data-source reference. The verdict stays fail with the same rule vector as v1: the rule needs the data-source reference in `triggers` (C1, a shape limit).

| variant | TS pass v1 → v2 (/ 326) | TS vector == CTRL | Py pass v1 → v2 (/ 346) | Py vector == CTRL |
|---|---|---|---|---|
| P1 | 118 → 118 | 117 → 117 | 124 → 124 | 123 → 123 |
| P2 | 187 → 187 | 186 → 186 | 198 → 198 | 197 → 197 |
| P3id | 302 → **304** | 301 → 303 | 318 → **320** | 317 → 319 |
| **P3src** | 312 → **314** | 311 → 313 | 328 → **331** | 327 → 330 |

- **P3src** reaches TS 314/326 (96.3%) and Py 331/346 (95.7%). That is exactly the projection in `../full408/REPORT.md` §4.
- **P3id** gains 87 and 89 in both languages. The REPORT did not project this.
- The R-shapes and CTRL do not depend on the adapter's `adapt()`, so they are unchanged.

### Left as it was (observations)

- **`reverse_shape()` copies the control's `provisioners` unchanged.** R-P2 does not strip their references and R-P3 does not filter them; only `expressions`, `count_expression`, `for_each_expression` and `depends_on` are processed. This is outside fixes A and B and was not changed. It does not affect 87 or 89, whose rule only tests `expressions.command != null`.
- **`load_preview()` still writes the note "no TF type for command:local:Command (skipped)".** The Command is still not a Terraform resource. A second note says that it was rebuilt into `provisioners`.
- **Earlier outputs were not regenerated with v2:** `results_fixed.csv` and `out_fixed/` (pilot), the `../results` files, and the `../full408` outputs and numbers. `ablation.py`, `mutation.py`, `fidelity.py` and `final_tables.py` still read the prototype.
- **Only false fails are measured.** The control passes on every eligible pair, so the false-pass direction still needs negative cases.

### Files added for v2

- `v2_check.py`: the unit check plus the regression diff described above.
- `v2_check/`: `unit_check.csv`, `regression.csv`, `v2_check.json`, `v2_check_out.txt` and `out/`, which holds 23 adapter JSON files: the 17 changed inputs plus the unchanged ones of the unit pairs.
