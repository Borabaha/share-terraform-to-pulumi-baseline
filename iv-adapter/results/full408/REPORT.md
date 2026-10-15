# IV adapter on the full base set: final report (15 Oct 2026)

> **Note: this report describes adapter v1.** Adapter v2 then fixed bugs A and B from section 4 (`CHANGES.md`, section "v2 (fixes A, B)"), and the full run was repeated (`results/full408_v2/SUMMARY.md`, `full_results.csv`). With v2, on the eligible pairs (TS 326, Py 346):
>
> | variant | TS v1 → v2 | Py v1 → v2 |
> |---|---|---|
> | P1 | 118 → 118 | 124 → 124 |
> | P2 | 187 → 187 | 198 → 198 |
> | P3id | 302 → 304 (93.3%) | 318 → 320 (92.5%) |
> | P3src | 312 → **314 (96.3%)** | 328 → **331 (95.7%)** |
>
> Exactly 9 rows changed, all from fail to pass: tasks 87 and 89 (TS and Py, P3id and P3src) and task 15 (Py, P3src). This is the projection in section 4 for P3src. The R-shapes and CTRL did not change. The P3src disagreements with the control went from 34 to 29, and no adapter-bug rows are left (clusters C3 and C4b are gone). The rest of this report is the v1 text. Only a duplicate short summary and a local path at the end were removed, and the wording of the C5 row in section 3 was changed (now "the original plan"). Paths such as `E-prototype/iv_adapter.py` refer to my working folder; the adapter is `iv_adapter.py` in this repository.

The fixed adapter (`E-prototype/iv_adapter.py`, sha256 `98a53d94…`, unchanged) was run in preview mode on the 408 base tasks, with the unchanged IV method (`intent.rego`, OPA 1.1.0, `extract_validation_status`). Eligible pairs: TS 326, Py 346. The control passes on every eligible pair, so "agrees with control" means "passes".

## 1. Final numbers (eligible pairs)

| variant | TS / 326 | Py / 346 |
|---|---|---|
| P1 | 118 (36.2%) | 124 (35.8%) |
| P2 | 187 (57.4%) | 198 (57.2%) |
| P3id | 302 (92.6%) | 318 (91.9%) |
| **P3src** | **312 (95.7%)** | **328 (94.8%)** |
| R-P1 / R-P2 / R-P3 | 123 / 193 / 321 | 129 / 204 / 338 |

- **Same rule vector as the control:** P3src TS 311, Py 327. The one exception is task 365: it passes, but the adapter writes `public_key ""` where Terraform leaves the key out.
- **P3src vs R-P3, same rule vector:** TS 316/326, Py 335/346.
- **P3id fails where P3src passes:** 10 pairs per language, because P3id guesses `.id` as the attribute. The reverse never happens.
- **R-shapes over all 408 base tasks:** R-P1 137, R-P2 222, R-P3 374.
  - Of the 34 R-P3 failures, the rule reads module.* references in 25, data sources in 7, root outputs in 1 and local.* references in 1.
  - 26 of the 34 have no passing preview in either language.
- **Whole run set, including the non-eligible tasks 83 and 110:** P3src agrees with the control in TS 313/328 and Py 329/348.
- **Sanity checks:** CTRL agrees with `results_tf.csv` on 410/410. The empty input passes 0. There were 0 errors in 4754 OPA calls.

## 2. Independent check

- Recount: all numbers above match, and the disagreement set is identical (cluster sizes C1–C5 = 13/2/4/11/4).
- Re-run of 25 pairs: 200/200 identical in verdict, rule vector and adapter JSON.
- Spot check of 2 rows per cluster: 10/10 confirmed.

## 3. Why P3src disagrees with the control (34 rows)

| cause | eligible rows (adapter fails) | non-eligible rows (adapter passes) | where it comes from |
|---|---|---|---|
| shape limitation | 23 (TS 10, Py 13) | 0 | **C1, 13 rows:** the rule reads data sources, prior_state or root outputs (R-PU-20, R-PU-7). Tasks 90 Py, 94 Py, 99 Py, 117, 124, 149, 187, 309. **C4a, 10 rows:** the preview shows master_password as `"[secret]"` (R-PU-10). Tasks 366–370. |
| adapter bug | 5 (TS 2, Py 3) | 0 | **C3, 4 rows:** provisioners are skipped (N11). Tasks 87, 89. **C4b, 1 row:** a secret list of blocks is written flat (R-TF-29). Task 15 Py. |
| translation defect | 2 (TS 1, Py 1) | 0 | **C2:** the converter dropped the provider aliases. Task 3. TV still says equivalent=True. |
| rule fragility | 2 (TS 1, Py 1) | 2 | **C5:** the rule checks the JSON type of an HCL literal. Task 455: `-1` vs `"-1"`. Task 83: `"120"` vs `120`; the original plan fails this rule too. |
| other | 0 | 0 | |
| **total** | **32** | **2** | **34** |

- **C4a is a shape limit that R-P3 does not model.** R-P3 copies secrets from the Terraform plan. With the preview's masking applied (R-P3m), all 10 rows fail with the adapter's vector. The adapter leaves the literal password out of its output on purpose (N24), so this is not a bug.
- **Task 90 Py** is in C1, but it also has the C3 provisioner gap.

## 4. Adapter bugs and suggested fixes

| # | bug | rows | fix | spec rules | effect (counterfactual) |
|---|---|---|---|---|---|
| A | `command:local:Command` resources are skipped, so `provisioners` is never written (N11) | 87, 89 TS+Py | New R-PU entry that inverts `tf.go` L2582-L2717:<br>1. Find the parent through the `dependsOn` chain.<br>2. Order the provisioners by `<i>`.<br>3. Emit `local-exec` with a `command` expression on the parent.<br>4. Take the command from `delete` when create and update are `"true"`, otherwise from `create`.<br>5. In P3, write references to the parent as `self`. | R-TF-24, R-TF-32..35; consistent with R-PU-24 and N16 | 4/4 pass with the control vector |
| B | A block-typed input that is wholly `"[secret]"` becomes one flat `references` expression | 15 Py | Never write a schema block type as an attribute expression. In P3src, build one block per element from the program text; in P3id, write `{}`. | R-TF-29, R-PU-10, R-PU-18; lifts N15 | 1/1 passes with the control vector |
| (C) | Design option, not a bug: recover secret literals from the program text | 366–370 | Put the literal into `values` and keep `after_sensitive`. | R-PU-10, R-TF-9/18; reverses N24 | 10/10 pass |
| (D) | Evaluation fix, not an adapter bug: R-P3m | — | Mask secrets in `reverse_shape()` in preview mode. | R-PU-10 | The 10 lightsail rows become shape failures in the baseline too |

Projected pass counts (arithmetic from the counterfactuals, not a run of a modified adapter; side effects of the fixes on other rows are untested):
- With A and B: TS 314/326 (96.3%), Py 331/346 (95.7%).
- Adding C: TS 319/326 (97.9%), Py 336/346 (97.1%).

## 5. What this means for using the adapter as the IV mechanism

- **P3src in preview mode is usable.** It agrees with the control on 95.7% (TS) and 94.8% (Py) of eligible pairs, and usually reproduces the full rule vector, not just the verdict.
- **The ceiling under preview masking** is R-P3 minus the 5 lightsail tasks per language: TS 316, Py 333. P3src sits 4 (TS) and 5 (Py) rows below it:
  - 1 per language is a real translation defect that IV catches and TV misses (task 3);
  - TS 2 and Py 3 are the adapter bugs A and B;
  - 1 per language is rule fragility (task 455).
- **Some rules can never be decided from a preview.** 34 of 408 base tasks (8.3%) fail even for R-P3, because the rule reads data sources, outputs, module.* or local.* references, or secret values. These should be reported as "not decidable from the preview", not as translation failures.
- **References are essential.** P1 (about 36%) and P2 (about 57%) are not usable as IV.
- **Only false fails are measured here**, because the control passes on every eligible pair. False passes need negative cases, such as the pilot's mutation test or the hold-out set.
- **Fix A and B before the hold-out run.**

The independent-check files (`full408/indep_check/` in my working folder) are not included in this repository:
- `recount.py`, `recount_out.txt`, `recount.json`
- `rerun_sample.py`, `rerun_sample.csv`, `rerun_sample_out.txt`, `sample_out/`
- `spot_check.py`, `spot_check_out.txt`, `spot_check.json`, `spot_out/`
