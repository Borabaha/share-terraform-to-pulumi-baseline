# Full 408 validation, IV adapter v2 (fixes A, B), 15 Oct 2026

> **Note for this repository.** The driver is `iv-adapter/run_full.py` (here with relative paths), and `full_results.csv` in this folder is its output. `rve` means that the rule vector equals the control's (column `rule_vector_equal`). The v1 driver `../full408/run_full.py`, the v1 outputs, `compare_v1_v2.py` and `E-prototype/v2_check/` named below are in my working folder and are not included, so section 2 (the comparison with v1) cannot be regenerated from this repository. The adapter hashes below are those of the adapter file in my working folder; `iv-adapter/iv_adapter.py` here has other paths and comments, so its hash differs.

The driver `full408_v2/run_full.py` is a copy of `../full408/run_full.py`. Only three things differ: the output folder, the expected adapter hash, and a log line that also names the v1 hash. Everything else is the same: preview mode, 410 tasks (408 base plus 83 and 110), the unchanged IV (`opa.exe eval ... intent.rego data` with OPA 1.1.0, then `extract_validation_status`), 16 processes and 16 OPA threads. Adapter v2 sha256 is 1d9f6f26... (v1 was 98a53d94...), and the hash was the same after the run. No Pulumi or Terraform command was run, so LocalStack was not needed.

## 1. Run and sanity (same as v1 unless noted)
- Run set: TS 328, Py 348. Eligible: TS 326, Py 346.
- 4754 OPA calls, 0 build errors, 0 OPA errors.
- CTRL agrees with results_tf.csv on 410/410. EMPTY passes 0.
- Unresolved Pulumi names / dropped keys: 0 / 0.
- full_results.csv has 6782 rows, with the same keys in the same order as v1.
- Pilot cross-check: 287/287.
- Repeat run: I ran the driver twice. full_results_detail.csv, full_results.csv and rule_vectors.json were byte-identical both times (66.6 s / 69.4 s).

## 2. Row-by-row comparison with v1 (compare_v1_v2.py)
- **All 6782 rows were compared.** 6765 OPA inputs are JSON-identical to v1 and 17 changed. 6773 rows are identical in every result column.
- **Exactly 9 rows changed.** In each of them the verdict, the rule vector and rve all changed together, always from fail to pass:
  - 87 and 89, TS and Py, in P3id and P3src (8 rows);
  - 15 Py in P3src (1 row).
- **Rows that cannot change did not change.** No result changed without an input change. No Terraform row (CTRL, EMPTY, R-P1/R-P2/R-P3) changed, and no P1 row changed. reverse_shape() is untouched in v2.
- **The set of changed inputs matches the pre-run check.** It is the same 17 inputs as E-prototype/v2_check/regression.csv. Verdict and rve agree on 17/17, and the v2_check/out files are JSON-identical to out/ (23/23).

Per changed row:

| Rows | Verdict | What changed in the input | Why |
|---|---|---|---|
| 87, 89 TS+Py, P3id and P3src | fail -> pass | `aws_eks_cluster.example` gets 4 local-exec provisioners | Fix A. Leaves has_aws_eks_cluster F->T and valid_configuration u->T. The rule needs one local-exec with `expressions.command != null` (intent.rego L25-38). P3id's `["self.id","self"]` also satisfies that, so P3id gains 87/89 too. REPORT.md did not project this, but v2_check had measured it. |
| 15 Py P3src | fail -> pass | `setting` of prod_env and staging_env changes from one flat references expression to 4 blocks | Fix B. Leaves is_valid_eb_env and is_configuration_valid F->T. The rule reads `setting[x].value.references[0]` per block (L64-71). The vector now equals CTRL. |

Inputs that changed but whose result did not (8 rows):

| Rows | Verdict | What changed in the input | Why it still fails |
|---|---|---|---|
| 87, 89 TS+Py, P2 | fail -> fail | provisioners added, with `command` `{}` | has_aws_eks_cluster also needs `count(depends_on) > 0` and non-empty subnet_ids. P2 has neither, and R-P2 fails 87/89 as well. |
| 15 Py P3id | fail -> fail | flat `.id` references -> `{}` | Fix B as designed: P3id has no program text, so it cannot rebuild the hidden blocks. Same vector as v1. |
| 90 Py, P2/P3id/P3src | fail -> fail | `null_resource.k8s_patcher` gets 1 local-exec | The rule needs `count(triggers.references) == 8`. The adapter has 6, because the 2 `data.aws_eks_cluster_auth` references are dropped (N16). It also needs the `aws_eks_cluster_auth` data source. Both are shape limits (C1), and R-P3 fails with the same vector. |

Side effects: none beyond the expected tasks. Only 87, 89 and 90 have rules that read provisioners.

## 3. Final numbers, v2 (eligible; v1 in brackets)

| variant | TS pass / 326 | TS rve | Py pass / 346 | Py rve |
|---|---|---|---|---|
| P1 | 118 [118] | 117 | 124 [124] | 123 |
| P2 | 187 [187] | 186 | 198 [198] | 197 |
| P3id | 304 (93.3%) [302] | 303 [301] | 320 (92.5%) [318] | 319 [317] |
| P3src | 314 (96.3%) [312] | 313 [311] | 331 (95.7%) [328] | 330 [327] |
| R-P1 | 123 | | 129 | |
| R-P2 | 193 | | 204 | |
| R-P3 | 321 | | 338 | |

- **R-shapes over all 408 base tasks are unchanged:** R-P1 137, R-P2 222, R-P3 374 (rve 373). The same 34 tasks fail R-P3: module.* references 25, data sources 7, root outputs 1, local.* 1.
- **Whole run set, including 83 and 110:** P3src TS 315/328 [313], Py 332/348 [329]. P3id TS 306 [304], Py 322 [320].
- **P3src vs R-P3, same rule vector:** TS 318/326 [316], Py 338/346 [335]. The remaining differences are 3, 365, 366-370 and 455.
- **P3id fails where P3src passes:** TS 10, Py 11 (15 is new in Py). The reverse happens 0 times.
- **Task 365** still passes with a vector different from CTRL.

## 4. Remaining P3src disagreements: 34 -> 29
Resolved: 87 and 89 TS+Py (v1 cluster C3) and 15 Py (C4). Nothing new. The recomputed clusters match the v1 labels on 29/29 rows:
- C1 shape limit, 13 rows: 90 Py, 94 Py, 99 Py, 117, 124, 149, 187, 309.
- C2 translation defect, 2 rows: task 3.
- C4 secret password, 10 rows: 366-370.
- C5 literal type, 4 rows: 455, and 83 where the adapter passes but 83 is not eligible.
- C3: 0 rows.

That is 27 eligible rows where the adapter fails (TS 12, Py 15) and 2 non-eligible rows where it passes.

The masked ceiling (R-P3 minus the lightsail tasks) is TS 316, Py 333. P3src now sits 2 below it per language: task 3 (a real translation defect) and task 455 (rule fragility). No adapter-bug rows remain.

## 5. Open points
- The reverse-direction test (does the adapter pass broken translations?) was not part of this run. All numbers here measure false fails only.
- reverse_shape() copies the control's provisioners unfiltered. This changes no verdict, because 87, 89 and 90 only test `command != null`.
- `results/full408/REPORT.md` describes v1. A note at its top gives the v2 numbers.
