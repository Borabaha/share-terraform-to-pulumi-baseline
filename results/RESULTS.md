# Results

All numbers on this page are computed from the CSV files in this folder.

## Files

| File | Rows | Content |
|---|---|---|
| `control_group.csv` | 410 | The original Terraform of each task, run the way of the original study: `tflocal init` + `plan` against LocalStack, then the task's Rego rule with OPA 1.1.0. |
| `pulumi_typescript.csv` | 410 | `pulumi convert` to TypeScript, then compile, `pulumi preview` against the same LocalStack (TV) and the resource check (EQ). |
| `pulumi_python.csv` | 410 | The same for Python. |
| `supervisor_opa_recheck.csv` | 458 | The original `tfplan.json` files checked again with the original rules and pass function. Defines the base set. |
| `tasks.csv` | 458 | Features of every task in the package (difficulty, size, modules, ...) and the results recorded in the package. |

IV results (the Rego rules applied to the Pulumi preview through the adapter) are in `../iv-adapter/`.

TV for Pulumi is `pulumi preview` against LocalStack. It plays the role of `terraform plan` in the original method. Nothing is deployed in either case.

## How the files were made

- The runs were split over five run folders: `pilot-aligned` (the 30 pilot tasks) and `ext-w1-a` to `ext-w1-d` (95 tasks each). Each task ran in exactly one folder. The three run CSVs are the `results_tf.csv`, `results_typescript.csv` and `results_python.csv` files of these folders, stacked into one row per task and sorted by task id. The `run` column names the source folder.
- Some tasks ran more than once: six wave-1 tasks were repeated in wave 2, and runs that broke while the machine was asleep were repeated (19 tasks on 8 October, tasks 214, 216 and 254 on 14 October; see step 6 of "How to reproduce" in the main README). The files contain the last run of each task.
- Values are copied unchanged, with one exception: in 48 `preview_error` cells of `pulumi_typescript.csv`, the local absolute path in front of `runs\` was removed (for example `'runs\ext-w1-c\9\pulumi-ts/'`).
- No column held only local paths, so no column was dropped.
- Columns added for this repository: `run` and `in_base_set` (all three run CSVs), `failure_cause` and `failure_detail` (the two Pulumi CSVs). See section 4.
- `supervisor_opa_recheck.csv` is the output of `pipeline/recheck_supervisor_opa.py`, and `tasks.csv` the output of `pipeline/build_task_table.py`, both unchanged.
- Dates: the Pulumi stage ran on 6 October 2026 (pilot) and 6 to 8 October 2026 (the other 380 tasks). The Terraform stage was run again on 11 to 14 October 2026 after pinning python-hcl2 7.3.1, because with python-hcl2 8.x `tflocal` ignored the provider region in `main.tf`. The Pulumi stage does not use `tflocal`. EQ compares resource types and counts, not regions.

## Task sets

- The package has 458 tasks.
- 422 are listed as passing in the package (`ground_truth/tracking/opa_rego_fixes/opa_results_summary_improved.txt`).
- 409 pass today when the packaged rules are run on the original `tfplan.json` with OPA 1.1.0 and the original `extract_validation_status()`. 32 tasks have no `tfplan.json`.
- **Base set: listed and passing today, 408 tasks** (also in `../pipeline/tasks/base_tasks.txt`).
  - 14 listed tasks fail today: 0, 18, 81, 83, 110, 112, 116, 118, 122, 125, 182, 194, 232, 244.
  - Task 129 passes today but is not listed.
- **Run set: 410 tasks** = the 408 base tasks + 83 and 110. These two were in the 30-task pilot, which was drawn before the base set was fixed. They stay in the CSVs with `in_base_set = False` and are left out of every base-set number below.

## 1. Control group (original Terraform, 410 tasks)

| Check | Result |
|---|---|
| `tflocal init` | 410/410 |
| `tflocal plan` + `tflocal show -json` | 410/410 |
| Rego rule passes (original pass function) | 408/410 (fail: 83, 110) |
| Rego rule, strict reading (every boolean true) | 406/410 (also fail: 115, 365) |
| Plan identical to the original `tfplan.json` (resource addresses and actions, endpoint set, provider regions) | 410/410 |

- On the 408 base tasks, plan and rule both pass 408/408. So all 408 base tasks are the denominator for the Pulumi side.
- AWS provider: 5.90.0 in 388 tasks, 4.67.0 in 22 tasks (the `~> 4.16` tasks, all between 430 and 457).
- 26 of the 410 tasks use the `terraform-aws-modules/vpc` module (326 to 357). For them `input_patched = True`: `version = "5.19.0"` was added to the module block in the working copy. The package files are not changed.

## 2. `pulumi convert` (base set, 408 tasks)

| Step | TypeScript | Python |
|---|---|---|
| Convert (L0) | 407 | 405 |
| Compile (L1, for diagnosis only) | 369 | 382 |
| **TV: `pulumi preview` passes** | **326 (79.9%)** | **346 (84.8%)** |
| EQ, among TV passes | 324/326 | 344/346 |
| Tasks with a `not_implemented` call in the generated code | 1 (task 16) | 1 (task 16) |

On all 410 tasks TV is 328 (TypeScript) and 348 (Python). Tasks 83 and 110 pass TV and EQ in both languages.

Notes:

- **The convert failures are network timeouts.** All four (TypeScript: 327; Python: 333, 339, 355) timed out while the converter fetched the VPC module from `registry.terraform.io`. They are not converter errors, and they were not re-run. All four are VPC module tasks. In the other language each of them converted and then failed on the generated module code, like every other VPC module task. So a re-run would very likely not change TV.
- **The two EQ "failures" are empty plans.** Tasks 124 and 187 only read a data source (`aws_ami`). The Terraform plan creates no resource and the preview creates none either. EQ requires at least one resource (`tf_n > 0`), so these two count as not equivalent. No TV pass has a missing or an extra resource.
- **Compile results cannot be compared between the languages.** `tsc` checks types, `py_compile` only checks syntax. TV is the step to compare. TypeScript task 160 has `compile_ok = False` only because `tsc` hit the 600 s timeout; its preview passed.

## 3. TypeScript compared with Python (base set)

| | Tasks |
|---|---|
| TV passes in both | 326 |
| TV passes in Python only | 20 |
| TV passes in TypeScript only | 0 |
| TV fails in both | 62 |

- Python-only passes: 74 to 77, 88, 90 to 95, 97 to 99, 101 to 103, 156, 166 (TypeScript heredoc JSON escaping) and 15 (TypeScript type error).
- The convert step gives the same result in both languages. For the 404 tasks converted in both, the warnings, dropped provider settings and `not_implemented` counts are identical.
- Where both pass TV, the number of Pulumi resources is identical (326/326).

## 4. Why TV failed (base set)

`failure_cause` is set for every row whose `preview_ok` is not `True`. It names the first blocking error. It was assigned by text patterns on `convert_error`, `preview_error` and the error diagnostics in the saved preview JSON of the task (the raw run folders, which are not part of this repository). Python's `preview_error` often says only "Program failed with an unhandled exception", so for Python the cause comes from the preview JSON. `failure_detail` is the error line the cause is based on, shortened to 220 characters.

| `failure_cause` | Meaning | TS | Py |
|---|---|---|---|
| `vpc_module_codegen` | The generated VPC module code does not work. TypeScript: type error in `vpc_5.19.0.ts`. Python: `from vpc_5.19.0 import Vpc5190` is a syntax error (a module name cannot contain dots). | 25 | 23 |
| `pulumi_auto_naming` | Pulumi creates a name for an unnamed resource and the AWS provider rejects it: a security group name may not start with `sg-`, an RDS identifier may not contain `_`. | 14 | 21 |
| `ts_heredoc_json_escaping` | TypeScript writes the JSON of a heredoc as `\"` inside a template string, so the policy, event pattern or item is invalid JSON. | 19 | 0 |
| `ts_type_error` | `tsc` type error in `index.ts`. | 12 | 0 |
| `missing_file_in_package` | `main.tf` points to a file that is not in the package. The Terraform plan does not open the file, the Pulumi preview does. A package issue, not a translation error. | 10 | 13 |
| `convert_network_timeout` | The convert step timed out while fetching the VPC module (see section 2). | 1 | 3 |
| `other` | Task 450 (both): `allocation_id is not supported with connectivity_type = "private"` (NAT gateway). Task 381 (Python): DLM `resource_types` must be a list. | 1 | 2 |
| **Total TV failures** | | **82** | **62** |

Tasks per cause:

| `failure_cause` | TypeScript | Python |
|---|---|---|
| `vpc_module_codegen` | 326, 328 to 342, 346 to 349, 353 to 357 | 326 to 332, 334 to 338, 340 to 342, 346 to 349, 353, 354, 356, 357 |
| `pulumi_auto_naming` | 25, 200 to 212 | 16, 17, 19, 24, 25, 26, 200 to 214 |
| `ts_heredoc_json_escaping` | 74 to 77, 88, 90 to 95, 97 to 99, 101 to 103, 156, 166 | none |
| `ts_type_error` | 9 to 12, 14 to 17, 19, 24, 26, 381 | none |
| `missing_file_in_package` | 13, 115, 154, 213, 214, 277, 278, 316, 317, 319 | 9 to 14, 115, 154, 277, 278, 316, 317, 319 |
| `convert_network_timeout` | 327 | 333, 339, 355 |
| `other` | 450 | 381, 450 |

Each task has one cause, but some tasks have more than one problem:

- 15 base tasks point to a file that is missing from the package: 9 to 14, 115, 154, 213, 214, 277, 278, 316, 317, 319. None of them passes TV in either language. In TypeScript, 9 to 12 and 14 stop earlier at a type error. In Python, 213 and 214 stop earlier at the security group name error. This is why the counts differ (10 and 13).
- In TypeScript, 213 and 214 show both the security group name error and the missing file in the same preview. They are counted as `missing_file_in_package`.
- In TypeScript, the RDS tasks 16, 17, 19, 24 and 26 stop at a type error before the RDS name is checked.
- Task 16 also has the only `not_implemented` call (`formatdate`).
- Task 381 fails in both languages for the same reason: the converter writes `resource_types = ["VOLUME"]` as the string `"VOLUME"`. It shows as `ts_type_error` in TypeScript and as `other` in Python.

## 5. Settings the converter drops (logged only, not part of success)

Base set, from the convert warnings:

| Dropped with a warning | TS | Py |
|---|---|---|
| `assume_role` in the provider block | 164 | 162 |
| Provider aliases (tasks 3, 13, 25, 145, 167) | 5 | 5 |
| `create_before_destroy` lifecycle setting (all in VPC module tasks) | 25 | 23 |
| Function not implemented (`formatdate`, task 16) | 1 | 1 |

The TS/Py differences in this table come only from the convert timeouts: a task that did not convert has no warnings.

Terraform provisioners become `command:` resources in Pulumi. They are not counted in EQ and are reported in `provisioner_n`: tasks 87 and 89 (4 each) in both languages, and task 90 (1) in Python. In TypeScript, task 90 fails TV, so it has no value.

## Column descriptions

Empty cells mean the step was not reached. `skip` means the step was skipped because an earlier step failed.

### `control_group.csv`

| Column | Meaning |
|---|---|
| `task` | Task id (folder name in `ground_truth/dataset/` of the package). |
| `input_patched` | `True` if `version = "5.19.0"` was added to the VPC module block in the working copy of `main.tf`. |
| `tf_init` | `tflocal init` exited with 0. |
| `tf_plan` | `tflocal plan` and `tflocal show -json` both succeeded. |
| `tf_opa` | Rule result: `opa eval -i plan.json -d intent.rego data` (OPA 1.1.0), then the original `extract_validation_status()`. `pass` / `fail`; `error` if OPA failed, `undefined` if OPA returned no value, `skip` if there was no plan. |
| `tf_opa_strict` | Stricter reading of the same OPA output: `pass` only if every boolean in it is true. For comparison only. |
| `aws_provider` | `hashicorp/aws` version installed by `init`. |
| `vs_supervisor_plan` | Our plan compared with the original `tfplan.json`. `same`: same resource addresses and actions, same endpoint set, same provider regions. Other possible values: `resources_differ`, `same_resources_endpoints_differ`, `same_resources_region_differs`, `no_supervisor_plan`. |
| `tf_error` | First error line if `init` or `plan` failed (empty in all 410 rows). |
| `tf_seconds` | Time of `init` + `plan`, in seconds. |
| `run` | Run folder the row came from (added). |
| `in_base_set` | `True` if the task is in the 408-task base set (added). |

### `pulumi_typescript.csv` and `pulumi_python.csv`

| Column | Meaning |
|---|---|
| `task` | Task id. |
| `lang` | `typescript` or `python`. |
| `convert_ok` | `pulumi convert --from terraform --language <lang> --generate-only` exited with 0 and wrote `Pulumi.yaml`. |
| `convert_seconds` | Time of the convert step, in seconds. |
| `convert_warnings` | Number of lines in the converter's stderr that start with "warning". |
| `provider_config_dropped` | Provider settings dropped with a warning (`ignoring aws:<name>`), for example `assume_role`. `;`-separated. |
| `provider_alias_dropped` | Aliased provider blocks dropped with a warning (`ignoring aws=<alias>`). `;`-separated. |
| `unimplemented_functions` | Terraform functions the converter could not translate ("Function X not yet implemented"). |
| `convert_warning_kinds` | Distinct warning kinds from the `main.tf:<line>` warnings. `;`-separated. |
| `not_implemented` | Number of `notImplemented(...)` / `not_implemented(...)` calls in the generated code (the helper's own definition is not counted). |
| `convert_error` | First error line if the convert step failed. |
| `compile_ok` | TypeScript: `tsc --noEmit` on the project. Python: `python -m py_compile` on all `.py` files. For diagnosis only. |
| `preview_ok` | `pulumi preview --json` against LocalStack exited with 0. **This is TV.** |
| `preview_error` | TypeScript only: `compile: <first tsc error>` if `tsc` failed. Then the first line (up to 200 characters) of each error diagnostic of the preview, joined by ` \| `; if there is none, the first error line of stderr. |
| `tf_n` | Number of managed resources the Terraform plan creates (from the control group's `plan.json`). |
| `pulumi_n` | Number of real (custom) resources in the preview with `create` or `same`. Pulumi's own entries (`pulumi:`), components and `command:` resources are not counted. |
| `matched` | Terraform resources matched one-to-one to a Pulumi resource of a matching type. AWS types are matched with `bridge-metadata.json` of pulumi-aws 6.72.0 (current and past names; `aws_s3_bucket` also accepts `aws:s3/bucket:Bucket`); other providers by a name rule (`random_id` to `random:index/randomId:RandomId`). |
| `equivalent` | **EQ**: `True` if `tf_n > 0` and no resource is left unmatched on either side. |
| `missing_in_pulumi` | Terraform resource types with no Pulumi match, with counts. |
| `extra_in_pulumi` | Pulumi resource types with no Terraform match, with counts. |
| `preview_seconds` | Time of `pulumi preview`, in seconds. |
| `provisioner_n` | Number of `command:` resources in the preview (converted Terraform provisioners). |
| `run` | Run folder the row came from (added). |
| `in_base_set` | `True` if the task is in the 408-task base set (added). |
| `failure_cause` | Cause of the TV failure, see section 4 (added). Empty when TV passed. |
| `failure_detail` | The error line behind `failure_cause`, local path prefix removed (added). |

### `supervisor_opa_recheck.csv`

| Column | Meaning |
|---|---|
| `task` | Task id. |
| `listed_pass` | `True` if the task is listed under "Successful Directories" in `opa_results_summary_improved.txt` of the package. |
| `recheck_lenient` | The original `tfplan.json` + `intent.rego` of the task, `opa eval ... data` with OPA 1.1.0, then the original `extract_validation_status()`. Empty if there is no `tfplan.json`. |
| `recheck_strict` | `True` only if every boolean in the same OPA output is true. |
| `note` | `no tfplan.json` for the 32 tasks without one; empty for all other tasks. |

Base set = `listed_pass == True` and `recheck_lenient == True` (408 tasks).

### `tasks.csv`

| Column | Meaning |
|---|---|
| `task` | Task id. |
| `difficulty` | Difficulty level (1 to 6) from the task's `README.md`. |
| `loc` | Number of lines in `main.tf`. |
| `n_resources` | Number of `resource "..."` blocks in `main.tf`. |
| `has_module`, `has_data`, `has_count`, `has_provider_block` | 1 if `main.tf` has a `module` block, a `data` block, a `count =` argument, a `provider` block; else 0. |
| `supervisors_tf_plan_pass` | 1 if `init` and `plan` succeeded in the original Terraform results (`ground_truth/tracking/terraform_init_plan_fixes/terraform_results_1..4.csv`, the last listed result counts). |
| `supervisors_opa_pass` | 1 if the task is listed under "Successful Directories" (same as `listed_pass` above). |

In `tasks.csv`: 458 tasks, `supervisors_tf_plan_pass` 425, `supervisors_opa_pass` 422.
