# IV adapter: Pulumi preview to Terraform plan JSON

## What it is

In the original study, the IV (intent validation) step runs a task's `intent.rego` with OPA 1.1.0 on the Terraform plan JSON
(`terraform show -json`) and reads the verdict with `extract_validation_status()`. A Pulumi translation has no
Terraform plan. The adapter fills that gap. It reads what Pulumi produces for the translated program
(`pulumi preview --json`, and the converted program text for one variant) and writes a JSON file in the shape of a
Terraform 1.5.7 plan. Then the unchanged IV runs on that file:

```
opa eval -i <adapted.json> -d <dataset>/<task>/intent.rego data
pass = extract_validation_status(result[0].expressions[0].value)
```

Nothing in the original package is changed: not the rules, not the OPA command, not the pass function. The adapter does not
run Pulumi or Terraform. It only reads files that the pipeline (`../pipeline/`) already wrote.

## How it was written and checked

I wrote the adapter with the help of an LLM (Claude). It started as a quick prototype on 6 Oct 2026. On 15 Oct,
again with Claude's help, it was checked rule by rule against the source code of the tools:

1. **Two specs from the source code.** Both cite file and line ranges at fixed tags, and both were checked against
   real data.
   - `specs/terraform-plan-json.md` (42 rules, R-TF-n): what Terraform v1.5.7 writes into the plan JSON
     (`jsonplan`, `jsonconfig`, `jsonstate`, address ordering), plus HCL v2.16.2 and go-cty v1.12.2. Checked against
     the 426 `tfplan.json` files in the original dataset.
   - `specs/pulumi-side.md` (33 rules, R-PU-n): what the adapter gets from Pulumi v3.267.0, pulumi-aws v6.72.0,
     pulumi-terraform-bridge v3.104.0 (names, MaxItemsOne, defaults) and pulumi-converter-terraform v1.4.0.
     Checked against the 60 pilot previews.
2. **Review against the specs.** `CHANGES.md` lists every rule: what the prototype did, what the spec says (with its
   source), and what was changed. 40 points were fixed and 25 were left open, each with a reason. No change was chosen
   by looking at which rules pass or fail.
3. **Independent check.** `VERIFY.md` re-reads the cited source for each row of `CHANGES.md`, re-runs the pilot and
   checks the output files against the structural rules of the spec. This was done on v1.
4. **v2.** The full run on the base set found two adapter bugs (`results/full408/REPORT.md`, section 4). v2 fixes
   them, based on the converter source code (`CHANGES.md`, section "v2 (fixes A, B)"):
   - A: the converter turns each `local-exec` provisioner into a separate `command:local:Command` resource. v2 folds
     these back into the `provisioners` list of the parent resource.
   - B: a block-typed argument that the preview hides as a whole (a secret) is no longer written as one flat
     expression. P3src rebuilds the blocks from the program text.

## Variants

Each variant emits more of the Terraform plan. This shows which parts of the plan the rules need.

| variant | what the adapter writes |
|---|---|
| P1 | `planned_values` and `resource_changes` (values only) |
| P2 | P1 + `configuration` with constant values only (no references) |
| P3id | P2 + references between resources, taken from Pulumi's `propertyDependencies`. The attribute part of a reference is guessed as `.id`. |
| P3src | P2 + references with the real attribute and nesting, read from the converted program text. Also, an argument that is not a literal in the program text gets no constant value. |

Reference rows (no adapter involved):

| row | what it is |
|---|---|
| CTRL | the unchanged Terraform control plan of the task |
| R-P1, R-P2, R-P3 | the control plan cut down to the shape of P1, P2 and P3. It shows what a variant of that shape can reach with a perfect translation. |
| EMPTY | the input `{}`. It must fail every task (it does). |

All numbers here use **preview mode**: values come from the preview. The adapter also has a plan mode that reads saved
plans from `pulumi preview --save-plan`. It was used only on the 30 pilot tasks, and the saved plans are not included.

## Results (adapter v2, preview mode, 408 base tasks)

Base tasks are the 408 tasks that the original package lists as OPA successes and that also pass when we re-run the
original `tfplan.json` with OPA 1.1.0 (`../results/supervisor_opa_recheck.csv`, `listed_pass` and `recheck_lenient` both
True). An **eligible pair** is a base task and a language (TS = TypeScript, Py = Python) where the Pulumi preview
succeeded and the control plan passes IV: TS 326, Py 346. The control passes on every eligible pair, so "pass" here
means "agrees with the control".

| variant | TS pass / 326 | Py pass / 346 |
|---|---|---|
| P1 | 118 (36.2%) | 124 (35.8%) |
| P2 | 187 (57.4%) | 198 (57.2%) |
| P3id | 304 (93.3%) | 320 (92.5%) |
| **P3src** | **314 (96.3%)** | **331 (95.7%)** |
| R-P1 / R-P2 / R-P3 | 123 / 193 / 321 | 129 / 204 / 338 |

- The passing P3src pairs usually match the control rule for rule, not just in the verdict: every boolean rule leaf
  has the same value as in the control run in TS 313 and Py 330 pairs. The exception is task 365 (one pair per
  language), which passes with a different leaf.
- The control plan cut to the P3 shape (R-P3) passes 374 of the 408 base tasks. The rules of the other 34 tasks read
  something the P3 shape does not carry: `module.*` references (25), data sources (7), root outputs (1) and
  `local.*` references (1).
- Sanity: our OPA run on the control plans agrees with the pipeline's result on 410/410 tasks (408 base plus 83 and
  110). The empty input passes 0. There were 0 errors in 4754 OPA calls.

**Why P3src disagrees with the control (29 rows).** 27 rows are eligible pairs where the adapter fails (TS 12,
Py 15). 2 rows are task 83, where the control fails and the adapter passes.

| cause | rows | tasks |
|---|---|---|
| shape limit: the rule reads data sources or root outputs | 13 | 90 Py, 94 Py, 99 Py, 117, 124, 149, 187, 309 |
| shape limit: the preview shows the password as `[secret]` | 10 | 366-370 |
| HCL literal type lost in conversion (`-1` vs `"-1"`, `120` vs `"120"`) | 4 | 455; 83 (not eligible) |
| real translation defect: the converter dropped the provider aliases | 2 | 3 |

Task 3 is worth a note: TV says the translation is equivalent, but IV catches the dropped aliases.

Details: `results/full408_v2/SUMMARY.md` (v2 run, with a row-by-row comparison to v1) and
`results/full408/REPORT.md` (v1 run, failure clusters and the fixes that became v2).

`results/full408_v2/full_results.csv` has one row per (task, language, variant):

| column | meaning |
|---|---|
| `task` | task id in the original dataset |
| `lang` | `terraform` for CTRL, EMPTY and R-shape rows of the control plan; `typescript` or `python` for adapter rows. The R-shape result is repeated under each language, so counts per language can be read off directly. |
| `variant` | P1, P2, P3id, P3src, R-P1, R-P2, R-P3, CTRL or EMPTY |
| `verdict` | pass or fail of our OPA run on this input |
| `control_verdict` | the control plan's IV result from the pipeline (`tf_opa` in `results_tf.csv`) |
| `rule_vector_equal` | True if every boolean rule leaf of the OPA output equals the leaf of the CTRL run |
| `false_rules` | rule leaves that are true in CTRL and false here |
| `undefined_rules` | rule leaves of CTRL that are missing here |
| `error` | build or OPA error (empty in this run) |

To count eligible pairs: take the rows of one language and variant, keep the base tasks, and keep
`control_verdict == pass` (this drops tasks 83 and 110).

## Limitations

- **Only false fails are measured.** The control passes on every eligible pair, so these numbers say how often the
  adapter fails a translation that should pass. They do not say how often it passes a broken translation. A
  false-pass test (deliberately broken translations) is not part of this repository.
- **Not a test on unseen tasks.** Fixes A and B were made after looking at the base-set disagreements, so the v2
  numbers come from the same tasks that were used to find the bugs.
- **What a preview cannot show.** Data sources, root outputs and `local.*`/`var.*` references are not in a Pulumi
  preview, and the adapter does not rebuild Terraform modules (R-PU-20, R-PU-7; `CHANGES.md` N2-N5, N16). Secrets
  are masked (R-PU-10, N24). Values that only the provider computes are missing in preview mode (N6). HCL literal
  types are lost in conversion (N7).
- **Program-text reading is regex based.** P3src reads the converted TypeScript or Python with a small reader, not a
  full parser. The literal check covers top-level arguments, and nested ones only where a whole block is hidden
  (N15).
- **One provider schema.** The adapter uses the aws 5.90.0 schema for every task. Task 432 was planned with aws
  4.67.0 (N22).
- **Converter coverage.** Only `local-exec` provisioners are rebuilt. `remote-exec` and `file` provisioners would get
  a note (none occur in the base set).
- `CHANGES.md` lists all 25 open points (N1-N25) with their sources.

## How to run

Requirements:

- Python 3 (only the standard library; the runs used 3.13.3).
- The original package in `../original-package/iac-research-without-agent` (included in this repository; only
  `iac_research/validation` and `ground_truth/dataset` are used).
- OPA 1.1.0 at `../tools/opa-1.1.0/opa.exe`. On Linux or macOS, change the `OPA` constant in `run_full.py` and
  `iv_adapter.py` to the `opa` binary.
- The pipeline's run folders `pilot-aligned`, `ext-w1-a`, `ext-w1-b`, `ext-w1-c` and `ext-w1-d` in
  `../pipeline/runs/`, or in a folder named by the environment variable `RUNS`. Each holds `results_tf.csv`,
  `results_typescript.csv`, `results_python.csv` and, per task, `terraform/plan.json`, `preview-<lang>.json`,
  `pulumi-ts/index.ts` and `pulumi-py/__main__.py`. The run folders are not in the repository; they are rebuilt by
  running the pipeline (see the main README).

Full run (no Pulumi, Terraform or LocalStack needed; 1 to 3 minutes with 16 processes):

```
python -B run_full.py
```

It writes `results/full408_v2/full_results.csv` again, so `git diff` shows any difference from the committed run.
The other outputs (`full_results_detail.csv`, `rule_vectors.json`, `run_meta.json`, `run_log.txt` and `out/` with
4,344 adapter and shape files) are ignored by git. The first log line reports the adapter hash as DIFFERENT from
both stored hashes. That is expected: the stored hashes are those of the adapter file in my working folder, which has
other paths and comments.

Run from this repository on my run folders (through `RUNS`), it gives a byte-identical
`full_results.csv` and `rule_vectors.json`, the same values in every column of `full_results_detail.csv` except the
file paths, and byte-identical files for all 4,344 inputs in `out/`.

One task by hand, here pilot task 428 in Python, variant P3src (run from this folder; it takes a few seconds):

```
python -B -c "import json, iv_adapter as ad; plan, notes = ad.adapt('428', 'python', 'preview', 'P3src'); json.dump(plan, open('428-py-P3src.json', 'w'), indent=1)"
python -B ../pipeline/opa_pass.py 428-py-P3src.json ../original-package/iac-research-without-agent/ground_truth/dataset/428/intent.rego
```

The second command runs OPA and the original `extract_validation_status()` and prints PASS or FAIL (here PASS). The JSON file
is byte-identical to the one the full run wrote for this pair. `adapt()` reads the task from `RUNS/pilot-aligned`. For
a task of an `ext-w1-*` folder, set `ad.PILOT` to that folder first, as `run_full.py` does.

`python iv_adapter.py` on its own runs the 30 pilot tasks in both modes and writes `results_fixed.csv` and
`out_fixed/` (a few minutes; OPA runs one call at a time). The preview-mode and control rows give the same verdicts
as my original pilot run. Without the saved plans, plan mode has no values: its rows get the note "no saved plan"
and should be ignored.

## Files

| file | what it is |
|---|---|
| `iv_adapter.py` | the adapter (v2). Main entry points: `adapt(task, lang, mode, variant)` and `reverse_shape(plan, shape)`. |
| `run_full.py` | driver for the full base-set run (writes `results/full408_v2/`) |
| `CHANGES.md` | rule-by-rule review of the prototype, the open points, and the v2 fixes |
| `VERIFY.md` | independent check of `CHANGES.md` and of the pilot re-run (on v1) |
| `specs/terraform-plan-json.md` | R-TF rules: Terraform 1.5.7 plan JSON |
| `specs/pulumi-side.md` | R-PU rules: what Pulumi gives the adapter |
| `tables/tf_schema.json`, `tf_schema.lock.hcl` | Terraform provider schemas (aws 5.90.0, null 3.2.3, archive 2.7.0, random 3.7.1), from `build_tf_schema.py` |
| `tables/*-terraform-mapping.json` | official Pulumi-to-Terraform name mappings (`pulumi package get-mapping terraform`): null, random and archive from `build_mappings.py`; aws 6.72.0 made once, outside that script, with `pulumi package get-mapping terraform aws@6.72.0` |
| `tables/pulumi_only_defaults.json` | defaults that exist only on the Pulumi side, with the Terraform default cited from the provider source (`build_pulumi_defaults.py`) |
| `results/full408_v2/` | v2 run: `full_results.csv`, `SUMMARY.md` |
| `results/full408/REPORT.md` | v1 run: report with the failure clusters (a note at the top gives the v2 numbers) |

The tables are already built. Rebuilding them needs Terraform 1.5.7 with the provider mirror
(`../pipeline/config/terraform-pinned.tfrc`), the Pulumi CLI with the provider plugins, and, for
`build_pulumi_defaults.py`, the aws package schema (`pulumi package get-schema aws@6.72.0`, 35 MB, not included).
The mirror path in that `.tfrc` is relative to `pipeline/runs/<run>/_tfwork`. `build_tf_schema.py` runs Terraform in
`tables/_tfwork`, where that path does not resolve, so first set `path` in the `.tfrc` to the absolute path of
`tools/tf-mirror` (forward slashes), as its comment says, and undo the change afterwards.

The docs mention helper scripts and outputs from my working folder (the prototype, `conformance.py`, `v2_check.py`,
the `verify/` scripts, local copies of the cited source files). They are not included. The public sources are cited
by URL at fixed tags.
