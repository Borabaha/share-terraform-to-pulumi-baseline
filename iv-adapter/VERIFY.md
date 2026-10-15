# Independent check of the adapter review and the pilot re-run (15 Oct 2026)

> **Note for this repository.** This check was made on adapter **v1** (sha256 `98a53d94…`) and the 30-task pilot, before the full base-set runs in `results/`. It checks every row of `CHANGES.md` against its cited source. Paths are those of my working folder (`E-prototype/` = the adapter folder, `results/` = the pilot run, `verify/` = the check scripts, `lab/` = the pipeline folder). The scripts in `verify/` and the pilot outputs are not included in this repository. In this file, `RESULTS.md`, `results/RESULTS.md`, `results/run_pilot.py` and `results/pilot_results_detail.csv` mean the adapter's pilot report and pilot files in my working folder. They are not included, and that `RESULTS.md` is not the same document as this repository's `results/RESULTS.md`. Apart from this note, section 3 (and the short-version item and the section 5 row that refer to it) was shortened to its findings, without the details of my own machine, and one word in section 2 was changed (now "the original `extract_validation_status`").

**Short version.**

- **(1) Sources.** I checked all 65 rows of `E-prototype/CHANGES.md` (40 fixed, 25 not fixed) against what they cite. Where a row cites code on the web, I opened that file at the cited tag and read the cited lines. Where a row cites a spec rule (R-TF-n / R-PU-n), I checked the spec text, and also the spec's own web source wherever the row depends on it.
  - No row says the opposite of its source.
  - Three counts or claims were wrong in the text. I corrected them in `CHANGES.md` (rows 7 and 20, row N5). I also fixed one inconsistent sentence in `RESULTS.md`.
  - Two rows rely on behaviour their cited spec rule does not state. Row 5 is backed by a provider-SDK source that `CHANGES.md` does not cite. Row 12 has no source. Neither changes any pilot result.
  - One spec file has a wording error (`specs/pulumi-side.md` R-PU-27). The adapter follows the code, not that wording. I did not edit the spec, because only `RESULTS.md`/`CHANGES.md` were in scope.
  - None of the structural spec rules is violated by the fixed adapter's 328 output files (`verify/invariants.py`).
- **(2) Re-run.** I wrote my own driver and re-ran the fixed adapter's P3src variant in both languages and both modes. The results equal `results/RESULTS.md`:
  - **TS 16/17** (fails task 3) and **Py 18/20** (fails tasks 3 and 90), in preview and plan mode.
  - Task 83 passes outside the eligible set; task 110 fails.
  - CTRL agrees with `results_tf.csv` on 30/30. There were 0 OPA errors.
  - All 82 output files are identical, field for field except `timestamp`, to the ones the earlier runs saved.
- **(3) Outside iv-study, no pilot, dataset or tool file changed, and no secrets.**
  - Nothing under `lab/runs/pilot-aligned` has an mtime later than 2026-10-11 20:47:51.
  - Outside `iv-study`, 9 entries changed on 15 Oct. None is a pilot, dataset or tool file. The only writes there by the review's LLM agents were two `__pycache__` folders in the original package's code, created by accident and then removed (section 3).
  - The secret scan of `iv-study` found only documentation placeholders and the LocalStack dummy credentials `test`.

The adapter code was not changed: `iv_adapter.py` still has sha256 `98a53d94…cd8b4`, and the baseline still has `5f2c594c…e4c0`.

---

## 1. CHANGES.md rows against their sources

**Method.**
- **Web files.** Each one was read at the exact tag from `raw.githubusercontent.com`, printed to the terminal and not saved. The tags:
  - `hashicorp/terraform@v1.5.7`
  - `zclconf/go-cty@v1.12.2`
  - `hashicorp/hcl@v2.16.2`
  - `hashicorp/terraform-provider-aws@v5.90.0`
  - `hashicorp/terraform-plugin-sdk@v2.36.1`
  - `pulumi/pulumi@v3.267.0`
  - `pulumi/pulumi-terraform-bridge@v3.104.0`
  - `pulumi/pulumi-converter-terraform@v1.4.0`
- **Data claims.** I checked them against `runs/pilot-aligned`, the dataset and `E-prototype/tables/` with small read-only scripts in `verify/`.

Verdicts:
- **OK**: the source says what the row says.
- **OK, data**: a pilot or dataset fact, re-checked here.
- **Spec only**: the row matches the spec rule, and I did not re-open that rule's own web source.
- **Gap**: the row is right, but its cited source does not state everything the change does.
- **Fixed**: the text was wrong and I corrected it.

### Fixed rows (1-40)

| # | What I checked | Verdict |
|---|---|---|
| 1 | `jsonplan/plan.go` L49-L66: the plan struct has `timestamp` (L65, omitempty). | OK. The adapter's value is the preview file's mtime, not a plan time. That is harmless. |
| 2 | `jsonplan/resource.go` L34: `schema_version` has no omitempty. `jsonconfig/config.go` L99: the same in `configuration`. Control plans: `aws_db_instance` is 2 in all 11 cases. | OK; OK, data |
| 3 | `jsonplan/values.go` L182: `provider_name` is the provider's full address. | OK. The adapter hard-codes `registry.terraform.io/hashicorp/<pkg>`, which is right for the 4 providers used. |
| 4 | `jsonplan/resource.go` L40: `values` is omitempty, and it is a map, so an empty map is dropped. In task 296, `aws_iam_role_policy_attachment.lambda_policy_attach` has no `values` in the control plan. | OK; OK, data |
| 5 | R-TF-9 says `values` holds every schema attribute, and R-PU-31 asks for the 5.90.0 schema. Neither spec says that an unset computed attribute becomes unknown. That behaviour is in terraform-plugin-sdk v2.36.1 `helper/schema/unknown.go` L14-L56 (`SetUnknowns`: computed attributes that are null become unknown, recursively in blocks). It is called for creates at `grpc_provider.go` L964-L968, and aws v5.90.0 pins that SDK (`go.mod` L293). | **Gap.** The change is supported, but by a source `CHANGES.md` does not cite. The `[]` for unset list/set blocks and unknown for Optional+Computed blocks are checked only against the control plans (conformance), not against a cited rule. |
| 6 | R-TF-9 (task 283 shows `timeouts: null`). In `tables/tf_schema.json`, `timeouts` has nesting `single` in 584 aws resources. | OK, data |
| 7 | `jsonconfig/expression.go` L136-L138: single/group blocks become one nested object. I recounted in `tf_schema.json`: there are **5 top-level** single/group blocks in managed resources, and **14 at any depth** (both without `timeouts`). | OK. **Fixed** the count wording in `CHANGES.md`. |
| 8 | go-cty v1.12.2 `cty/set_internals.go` L85-L135 (`Less`) and L144-L260 (`appendSetHashBytes`). I also checked `cty/set/ops.go` L117-L138: `Values()` sorts with `Less`, so this really is the iteration order. Nulls and unknowns sort last, strings compare bytewise, numbers numerically, false before true, and anything else by hash bytes. | OK. One small gap in the port: Go's `%q` also escapes non-printable non-ASCII runes, while `_go_quote` escapes ASCII control characters only. This can only matter for strings with such characters inside set elements of complex type. |
| 9 | `jsonstate/state.go` L486-L556 (`SensitiveAsBool`). `jsonplan/values.go` L212-L213 and L230: `sensitive_values` uses the marked after-value, with no `schema.ValueMarks` call. | OK |
| 10 | `jsonplan/values.go` L240-L242: sorted by `Address` string. | OK |
| 11 | `plan.go` L363-L368 sorts with `Addr.Less`. `addrs/resource.go` L38-L52 (data before managed, then type, then name), L122-L132 and L353-L363. `addrs/instance_key.go` L92-L117 (int keys compare numerically). | OK |
| 12 | R-TF-15 lists the 7 action lists (spec text). No spec rule maps Pulumi op names to them. Mapping `replace` to `["create","delete"]` assumes Pulumi's create-before-delete default, and no source is given for it. | **Gap.** The mapping has no source. It has no effect on the pilot, which has only creates (R-PU-4). |
| 13 | `plan.go` L423-L441: a wholly known after-value gives `{}`, otherwise `unknownAsBool`. L737-L800 is `unknownAsBool`. | OK |
| 14 | `plan.go` L442-L450: `after_sensitive` adds `schema.ValueMarks`. | OK |
| 15 | R-TF-21 and R-TF-42.3 (spec text). 12 of the 60 pilot previews have no `aws:region`. | Spec only; OK, data |
| 16 | `sdk/go/common/providers/reference.go` L27-L32 (the reference is URN `::` ID, and the ID is unknown in preview), L48-L51 (a provider is default when its name starts with `default`), L94-L101. In task 3 all 8 resources use `default_6_72_0` in both languages. | OK; OK, data |
| 17 | `jsonconfig/config.go` L516-L519: sorted by `Address`. | OK |
| 18 | `jsonconfig/config.go` L95: `expressions` is omitempty. | OK |
| 19 | R-PU-8 and R-PU-18 (spec). `expression.go` L111 uses `PartialContent`, so only written arguments appear (R-TF-28). | OK |
| 20 | `expression.go` L103-L104 calls `FixUpBlockAttrs`, and `blocktoattr/fixup.go` L15-L22 confirms it is schema-driven. I recounted in `tf_schema.json`: there are **20 top-level** configurable list/set(object) attributes in managed resources, and **21 at any depth** (the extra one is `aws_securitylake_data_lake` `configuration.encryption_configuration`). The old 5 entries in `attr_blocks.json` are all among them. | OK. **Fixed** the count wording in `CHANGES.md`. |
| 21 | R-TF-30. Task 343 `tfplan.json`, `ingress.constant_value[0]`: all 9 element attributes are present, 4 of them null. | OK, data |
| 22 | R-TF-38 and the HCL v2.16.2 `hclsyntax/variables.go` L14-L56 walker (only root scope traversals are collected). | OK. The `count.index` reference is an approximation when the real expression also names `var.`/`local.`. |
| 23 | `expression.go` L44-L48: constant only if evaluation with a nil context gives a value. HCL `hclsyntax/expression.go` L240-L251: with no functions, a call gives `DynamicVal`. | OK |
| 24 | `expression.go` L50-L81: full traversal, then shorter ones, then the bare subject, plus the un-keyed resource. R-PU-28 is the spec. | OK |
| 25 | `config.go` L500-L512: `depends_on` keeps the order written. Node `sdk/nodejs/runtime/resource.ts` L1003-L1006 and L1088-L1100, plus `dependsOn.ts` L23-L54 and L110-L118: arrays, Sets and `Promise.all` keep insertion order. Python `sdk/python/lib/pulumi/runtime/resource.py` L276-L282: `dependencies` is a `set`. | OK |
| 26 | R-PU-3 (spec). The adapter only adds a note. | Spec only |
| 27 | R-PU-6 and R-PU-24 (spec). | Spec only |
| 28 | `sdk/go/common/resource/sig/sig.go` L44-L78: exactly 7 unknown sentinels. They are identical to the adapter's `UNKNOWNS`. | OK |
| 29 | R-PU-9 granularity caveat (spec). Task 428 `route` stays element-wise in the control plan. | Spec only; OK, data |
| 30 | `pkg/backend/display/json.go` L45-L71 and L85-L98: every secret becomes the string `[secret]`, and show-secrets is hard-wired off. | OK |
| 31 | `sig.go` L17-L42 has the signature key, secret, resource reference, **output value** (L29-L30), byte string, asset and archive. `pkg/resource/stack/deployment.go` L70 has the float signature, with NaN/Inf handling at L903-L904. All are equal to the adapter's constants. | OK |
| 32 | R-PU-13 (spec). | Spec only |
| 33 | All 16 `tf_source` links in `tables/pulumi_only_defaults.json`, opened at v5.90.0: each cited range declares the argument as Optional with the default "Managed by Terraform". The exception is `parameter.apply_method`, whose default is `types.ApplyMethodImmediate`. I also recounted get-mapping aws 6.72.0: exactly 16 fields have a literal `default.value`, so the table is complete for aws. | OK; OK, data |
| 34 | R-PU-21 (spec). | Spec only |
| 35 | R-PU-23 (spec). | Spec only |
| 36 | Bridge v3.104.0 `pkg/tfbridge/schema.go` L1386-L1399 (`IsMaxItemsOne`: list or set, then the override if set, else `MaxItems() == 1`). | OK |
| 37 | Bridge `pkg/tfbridge/names.go` L137-L232. The adapter's `tf_to_pulumi` pluralizes when the override is false, or when there is no override and `maxItems != 1`. That matches L153-L173. | OK. **Spec wording error, not fixed (out of scope):** `specs/pulumi-side.md` R-PU-27 step 2 calls the `maxItems != 1` case "MaxItemsOne". The code (and R-PU-28) say that this case is the one that is *not* MaxItemsOne. |
| 38 | `expression.go` L44-L47: the constant is marshalled with its own cty type, with no conversion to the schema type. | OK |
| 39 | Reverse-shape design choice (no external source needed). | n/a |
| 40 | Docstring only. | n/a |

### Not-fixed rows (N1-N25)

| # | What I checked | Verdict |
|---|---|---|
| N1-N4 | The counts quoted (329/426; 0/458 and 1/458; about 3/458 and pilot 0; about 1/458) are the ones in R-TF-2/7/3/4/5. | Spec only |
| N5 | The text said that no pilot task has modules. **That is wrong.** Tasks 330, 334, 335, 337 and 338 have `module "vpc"` in `main.tf`, and their control plans have `child_modules`/`module_calls` (`verify/module_check.py`). All 10 of their Pulumi previews failed (`preview_ok` False), so no adapter input contains a module. None of these 5 rules reads `module_calls`/`child_modules`. | **Fixed** in `CHANGES.md` |
| N6-N9 | Consistent with R-TF-9/10/21 and R-PU-20. | Spec only |
| N10 | Converter v1.4.0 `pkg/convert/tf.go` L4643-L4652, inside `translateModuleSourceCode` (which starts at L4153): a provider block with an alias gets a warning and is skipped with `continue`. | OK. The line numbers now match online too, not only the local copy. |
| N11 | `tf.go` L2653 `convertLocalExecProvisioner`; L2663 creates a `command:local:Command` resource. | OK |
| N12-N21 | Consistent with R-TF-26/31/32/35/39/40 and R-PU-16/18/21. | Spec only |
| N22 | `runs/pilot-aligned/432/terraform/log.txt` shows aws v4.67.0 installed for `~> 4.16`. | OK, data |
| N23-N25 | Consistent with R-PU-33, R-PU-10 and R-PU-11. | Spec only |

### Spec rules that no row names

None of these is ignored in a way that matters:
- **R-TF-1, 14, 16, 20, 34, 42.** `verify/invariants.py` checks them on all 328 fixed-adapter files in `results/out/fixed/` (82 per variant), and finds **0 violations**.
- **Further checks in the same script, all 0 violations:**
  - R-TF-2/8/9/11/12/13/15/17/18/21/23/24/26/28/29/35/40;
  - every schema attribute is either in `values` or unknown;
  - every reference subject is a config address;
  - an attribute reference is always followed by its bare subject.
- **Negative control.** The same script on `results/out/baseline/` reports 6 violation classes, the ones the fixes target: no `timestamp` (328), a `provider_config_key` without an entry (186), `schema_version` (424), the schema fill (288), keys not in the schema (16), and empty `values` (16). So the check does detect problems.
- **R-TF-19** (replace/import fields) does not apply to creates.
- **R-TF-27** (`module_calls`) is covered in substance by N5, which does not name it.
- **R-PU-1/2/5/22** concern how the preview is obtained and parsed. The adapter's URN parsing (last `$` segment, name after the last `::`) follows R-PU-22.
- **R-PU-32** lists limits, not adapter rules.

## 2. Independent re-run of the fixed adapter, P3src

**Script.** `verify/rerun_p3src.py` is new, and it does not reuse `results/run_pilot.py`. It imports `E-prototype/iv_adapter.py` read-only, with `sys.dont_write_bytecode` set and run with `python -B`, and calls only `adapt(task, lang, mode, 'P3src')`.
- **OPA.** It runs OPA itself: `opa.exe eval -i <plan> -d <dataset>/<task>/intent.rego data` (OPA 1.1.0).
- **Pass.** It calls the original `extract_validation_status` on `result[0].expressions[0].value`.
- **Eligibility.** Eligible means `preview_ok == True` in `results_<lang>.csv` and `tf_opa == pass` in `results_tf.csv`.

| lang | mode | P3src pass / eligible | failing eligible tasks | non-eligible tasks run | of those, passing |
|---|---|---|---|---|---|
| TS | preview | **16/17** | 3 | 83, 110 | 83 |
| TS | plan | **16/17** | 3 | 83, 110 | 83 |
| Py | preview | **18/20** | 3, 90 | 83, 110 | 83 |
| Py | plan | **18/20** | 3, 90 | 83, 110 | 83 |

- **Sanity.** CTRL (my OPA run on the unchanged control plans) agrees with `results_tf.csv` on 30/30. There were 0 OPA errors. The adapter hash at run time was `98a53d94c75c931670efcb1d81474dd650a7dbc6cbd39ab54316cbcc4bfcd8b4`.
- **Determinism.** All 82 P3src files I produced are identical, ignoring `timestamp`, to those in `results/out/fixed/` and `E-prototype/out_fixed/`.
- **The other `RESULTS.md` numbers.** I recomputed them from `results/pilot_results_detail.csv`, and all of them hold:
  - every pass/eligible cell and fail list in both language tables;
  - 0 of 451 verdict changes and 0 of 451 rule-diff changes from baseline to fixed;
  - `rule_vector_equal` true on 292 of 407 eligible fixed rows, which are exactly the 292 passing rows.
- **Task-level claims.** These also hold:
  - Task 3 fails on `is_valid_r53_zone`, `is_valid_db_instance_main` and the 3 replica rules, and the 3 `has_required_db_replica*_arguments` are undefined.
  - Task 90 fails on `has_aws_eks_cluster_auth` and `has_null_resource_k8s_patcher`, with `valid_configuration` undefined. That is the same for P3src and R-P3.
  - Task 83 P3src passes while CTRL fails.
- **File counts.** These also match: 478 files in `out_fixed/`, and 418/418/30 in `results/out/{baseline,fixed,control}`.

## 3. Writes outside iv-study, and secrets

**Writes** (`verify/mtime_scan.py`, stat only, 230,090 entries in my thesis folder outside `iv-study`):

- The newest mtime under the pilot run folder `lab/runs/pilot-aligned` is **2026-10-11 20:47:51** (`results_tf.csv`). Nothing there was modified on 15 Oct.
- 9 entries outside `iv-study` have an mtime on 15 Oct. None is a pilot, dataset or tool file. Apart from the two folders below, they are the folder in which `iv-study` was created and entries of my own notes and repository metadata.
- The only writes of the review's LLM agents outside `iv-study` (`verify/transcript_writes.py`, over the session logs of all 77 agents) concern two `__pycache__` folders that the re-run created by accident in the original package's code (`iac_research` and `iac_research/validation`) and then removed. The files in both folders still have their 2026-10-05 mtimes, and no `__pycache__` is left there. My own runs used `python -B` with `PYTHONDONTWRITEBYTECODE=1` and created none.

**Secrets** (`verify/secret_scan.py`: 2,730 text files in `iv-study`, the adapter's working folder; output masked). The patterns covered LocalStack token names and values, Pulumi/GitHub/Anthropic-style tokens, AWS key IDs and secrets, private-key blocks, bearer headers and generic token assignments.
- No LocalStack token and no Pulumi access token was found.
- The only matches are documentation examples (AWS's published example key, private-key header strings in schema descriptions, two placeholder API keys in a Pulumi docs page) and LocalStack's dummy credentials `test`/`test`.
- The 41 copied `Pulumi.emu.yaml` files contain an `encryptionsalt` and **no** `secure:` values.
- The fixed `PULUMI_CONFIG_PASSPHRASE` in `tables/build_mappings.py` is the harness's passphrase for its local Pulumi file backend, the same literal as in the pipeline's `pilot_runner.py` (`thesis-local` in this repository). It is not a secret and does not change the mapping output.

## 4. Documentation fixes made (adapter code unchanged)

1. `CHANGES.md` row 7: "5 such blocks" now says top level of managed resources (14 at any depth, without `timeouts`).
2. `CHANGES.md` row 20: "20 such attributes" now says top level (21 at any depth, with the extra one named).
3. `CHANGES.md` row N5: "No pilot task has modules or components" was wrong. It now says that 5 pilot tasks use `module "vpc"`, but their previews failed, so no adapter input has modules.
4. `RESULTS.md` short version, cause (c): it said the provisioner is something "P3 cannot carry". Section (c) of the same file shows that R-P3 carries it and only the adapter lacks it (N11). The sentence now says so.

Not changed, but worth knowing:
- Row 5's missing SDK citation and row 12's unsourced op mapping (section 1).
- The R-PU-27 wording error in `specs/pulumi-side.md`.
- `RESULTS.md` says it gave no line numbers for Pulumi `pkg/codegen/pcl/rewrite_convert.go`. They are: `convertPrimitiveValues` is at L310, and the int/number case is at L323-L327. That case turns a string literal into a number when the target type is a number.

## 5. Files in `verify/`

| file | what it does |
|---|---|
| `rerun_p3src.py` → `rerun_p3src.csv`, `rerun_p3src_out.txt`, `out/` (82 files) | Independent P3src re-run (section 2) |
| `invariants.py` → `invariants_out.txt`, `invariants_out_baseline.txt` | Structural spec checks on adapter output (fixed version, plus baseline as negative control) |
| `module_check.py` | Which pilot tasks use modules, and their preview status |
| `mtime_scan.py` → `mtime_scan_out.txt` | mtime scan outside `iv-study` |
| `transcript_writes.py` → `transcript_writes_out.txt` | File-changing tool calls of the review's LLM agents on 15 Oct, read from their session logs. Its regex is broad, so most hits are read-only commands with `2>/dev/null`; the only real write outside `iv-study` is the `__pycache__` removal. |
| `secret_scan.py` → `secret_scan_out.txt` | Masked secret scan of `iv-study` |

## Web sources opened for this check (15 Oct 2026)

All are read at the tag in the URL. Each entry gives the lines read and a paraphrase.

- **Terraform v1.5.7**, https://github.com/hashicorp/terraform/blob/v1.5.7/internal/…
  - `command/jsonplan/resource.go` L34, L40: `schema_version` is always written; `values` is omitempty.
  - `command/jsonplan/plan.go`:
    - L49-L66: the top-level plan keys;
    - L356-L384: sort resource changes by address `Less`, and drop data-source deletes;
    - L400-L452: before, after, after_unknown and after_sensitive;
    - L671-L800: `omitUnknowns` and `unknownAsBool`.
  - `command/jsonplan/values.go`:
    - L33-L46: every attribute of the value is marshalled;
    - L176-L245: schema version, the marked value for sensitivity, sort by address.
  - `command/jsonstate/state.go` L486-L556: `SensitiveAsBool`.
  - `command/jsonconfig/config.go` L70-L108 and L444-L520: the resource struct, the order of `depends_on`, sort by address.
  - `command/jsonconfig/expression.go` L20-L156: constant only if evaluation with a nil context gives a value; the order references are expanded in; nesting of block expressions; the `FixUpBlockAttrs` call.
  - `addrs/resource.go` L38-L52, L122-L132, L353-L363 and `addrs/instance_key.go` L92-L117: address ordering.
  - `lang/blocktoattr/fixup.go` L15-L30: block syntax is allowed for list/set attributes, and is driven by the schema.
- **go-cty v1.12.2**: https://github.com/zclconf/go-cty/blob/v1.12.2/cty/set_internals.go L60-L270 (ordering and hash bytes), `cty/set/ops.go` L117-L138 (`Values()` sorts with `Less`), and `cty/element_iterator.go` (set iteration).
- **HCL v2.16.2**: `hclsyntax/expression.go` L236-L252 (without a function table, a call gives an unknown value) and `hclsyntax/variables.go` L14-L60 (only root scope traversals are collected).
- **terraform-provider-aws v5.90.0**: the 16 `tf_source` ranges listed in `E-prototype/tables/pulumi_only_defaults.json`, and `go.mod` L285-L293 (plugin-sdk v2.36.1, framework v1.14.1).
- **terraform-plugin-sdk v2.36.1**: `helper/schema/unknown.go` L14-L80 (computed nulls become unknown) and `helper/schema/grpc_provider.go` L955-L970 (applied on create).
- **Pulumi v3.267.0**:
  - `sdk/go/common/resource/sig/sig.go` L15-L78;
  - `pkg/resource/stack/deployment.go` L70, L903-L904;
  - `sdk/nodejs/runtime/resource.ts` L995-L1010, L1080-L1105;
  - `sdk/nodejs/runtime/dependsOn.ts` L14-L172;
  - `sdk/python/lib/pulumi/runtime/resource.py` L262-L292;
  - `pkg/backend/display/json.go` L45-L98;
  - `sdk/go/common/providers/reference.go` L25-L102;
  - `pkg/codegen/pcl/rewrite_convert.go` L306-L345.
- **pulumi-terraform-bridge v3.104.0**: `pkg/tfbridge/names.go` L137-L232 and `pkg/tfbridge/schema.go` L1383-L1400.
- **pulumi-converter-terraform v1.4.0**: `pkg/convert/tf.go` L2494-L2541, L2651-L2665, L4153 (function start) and L4638-L4655.
