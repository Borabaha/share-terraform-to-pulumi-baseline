# Terraform to Pulumi: control group, `pulumi convert` baseline and IV adapter

This repository has the code, results and notes of my MSc thesis work so far (state of 15 October 2026). The thesis
is about translating Terraform programs to Pulumi: first with `pulumi convert`, later with LLMs. The translations are
judged with the method of Nekrasov, Fossati, Kumara, Tamburri and van den Heuvel ("IaC Generation with LLMs: An Error
Taxonomy and A Study on Configuration Knowledge Injection", arXiv:2512.14792), on the corrected IaC-Eval dataset from
their replication package. In that method, TV (technical validation) asks whether the program plans without errors
against LocalStack, and IV (intent validation) runs the task's Rego rule with OPA on the plan.

The repository covers three parts:

1. A check of the original package: its results, re-run with its own files and code.
2. A control group: the original Terraform of each task, run through the original chain in my setup.
3. The `pulumi convert` baseline in TypeScript and Python, checked with TV, a resource comparison (EQ), and IV through
   an adapter.

The LLM translations are not part of this repository yet.

## The original package

`original-package/iac-research-without-agent/` holds the part of the original replication package that the scripts
use, copied unchanged from the Zenodo release (DOI [10.5281/zenodo.20272829](https://doi.org/10.5281/zenodo.20272829),
file `iac-research-code-replication-package.zip`, MD5 `0A0568F4C9906DC8C46A1F8241A5AF61`). It is under the original
MIT license (`original-package/iac-research-without-agent/LICENSE`). It contains:

- `ground_truth/`: the 458 tasks (`main.tf`, `intent.rego`, `tfplan.json`, ...) and the tracking files of the rule
  and plan fixes;
- `iac_research/validation/analyzer.py`: the pass function `extract_validation_status()`;
- `iac_research/analysis/`: the error analyzer and its pattern files;
- `validation/runs/`: the result files and reports of the six experiment runs that the error analyzer reads;
- `LICENSE`, `README.md` and `requirements.txt` of the package.

The rest of the package (generation pipelines, RAG data, notebooks, scripts) is not needed here and is left out. The
scripts import the original functions from this folder and read its files; they never change them. To check that
every file is identical to the Zenodo zip:

```powershell
python pipeline\check_original_package.py <path to iac-research-code-replication-package.zip>
```

## What is not included

| What | Where to get it | Where it goes |
|---|---|---|
| Tools: the OPA 1.1.0 binary, the Terraform provider mirror, `bridge-metadata.json` of pulumi-aws 6.72.0 | See "Tools" below | `tools/` |
| Raw run folders (per task: plans, previews, generated Pulumi code, logs) | Rebuilt by running the pipeline | `pipeline/runs/` |
| A LocalStack auth token | Free account at app.localstack.cloud | `%USERPROFILE%\.localstack\auth_token.txt`, never in the repository |

`tools/` and `pipeline/runs/` are in `.gitignore`. The scripts copy what they need into the run folders.

### Tools

| File in `tools/` | Source |
|---|---|
| `opa-1.1.0/opa.exe` | https://github.com/open-policy-agent/opa/releases/tag/v1.1.0 (`opa_windows_amd64.exe`) |
| `tf-mirror/registry.terraform.io/hashicorp/<name>/terraform-provider-<name>_<version>_windows_amd64.zip` for aws 5.90.0 and 4.67.0, archive 2.7.0, kubernetes 2.36.0, random 3.7.1, null 3.2.3 | https://releases.hashicorp.com/terraform-provider-<name>/<version>/ (check against the `SHA256SUMS` file there) |
| `pulumi-aws-6.72.0/bridge-metadata.json` | https://raw.githubusercontent.com/pulumi/pulumi-aws/v6.72.0/provider/cmd/pulumi-resource-aws/bridge-metadata.json |

`pipeline/config/terraform-pinned.tfrc` points Terraform to the mirror. The Pulumi plugins are installed with
`pulumi plugin install` (converter terraform 1.4.0; resource aws 6.72.0, archive 0.3.2, null 0.0.10, random 4.18.0,
std 2.3.2, command 1.2.1), and `tflocal` comes from `pipeline/config/requirements-tflocal.txt`.

## Folders

```
original-package/                     the part of the original replication package that the scripts use, unchanged
pipeline/                             the code that ran the original chain and the Pulumi baseline
  pilot_runner.py                     main runner. Stages: setup, tf (control group), pulumi (convert, compile, preview, EQ)
  recheck_supervisor_opa.py           the packaged rules on the original tfplan.json files
  rerun_supervisor_error_analyzer.py  the original error analyzer on the 6 runs of the package, compared with its reports
  check_original_package.py           checks original-package/ byte for byte against the Zenodo zip
  build_task_table.py                 task table (results/tasks.csv) and the 30-task pilot sample
  opa_pass.py                         runs one task's rule on one plan file and prints PASS or FAIL
  run_shards.sh, run_waves.sh,
  run_tf_refresh.sh, run_rerun.sh     the full run in 4 parallel shards (Git Bash)
  config/                             version pinning, emulator settings, npm and pip lock files
  tasks/                              pilot list, the 408 base tasks, the shard and re-run lists of the full run
results/                              one row per task, all runs combined. RESULTS.md: numbers and column descriptions
iv-adapter/                           the adapter that lets the Rego rules run on a Pulumi preview: code, specs, checks, results
```

## Pinned versions

My rule was to use the versions of the original study wherever they are known, and to pin everything else.

| Tool | Version | Why this version |
|---|---|---|
| Terraform | 1.5.7 | All 426 `tfplan.json` files in the package say `terraform_version: 1.5.7`. |
| AWS provider | 5.90.0, and 4.67.0 for the 22 tasks with `~> 4.16` | The logs in the original package and the `.terraform.lock.hcl` inside its binary `tfplan` files. Served from a local mirror, so no `main.tf` is changed. |
| archive / random / null / kubernetes providers | 2.7.0 / 3.7.1 / 3.2.3 / 2.36.0 | Same source as the AWS provider. |
| terraform-local (`tflocal`) | 0.24.1 | With localstack-client 2.7 it writes exactly the 93 endpoint services of the original plans. |
| localstack-client | 2.7 | See above. A newer client wrote 107 services and broke the `~> 4.16` tasks. |
| python-hcl2 | 7.3.1 | With 8.x, `tflocal` ignores the region in `main.tf`. 7.3.1 was current when terraform-local 0.24.1 came out. |
| OPA | 1.1.0 | The version named in the paper. |
| LocalStack | 2026.9.0, image `localstack/localstack-pro@sha256:801a3dff7f6a23857e7310b7602e67d52a29dfdcb03e09f7c608d5c57d24b792` | The version of the original study is unknown. I used the current one and pinned it by digest. |
| Pulumi CLI | 3.267.0 | Pulumi is not part of the original study. This was the current stable version when I started. |
| Pulumi Terraform converter | 1.4.0 | |
| pulumi-aws | 6.72.0 | Built on Terraform AWS 5.90.1, the closest release to 5.90.0. Its `bridge-metadata.json` is the type map for EQ. |
| pulumi archive / null / random | 0.3.2 / 0.0.10 / 4.18.0 | Built from the same Terraform providers as above (archive 2.7.0, null 3.2.3, random 3.7.1). |
| pulumi std / command | 2.3.2 / 1.2.1 | Used by the generated code (Terraform functions, provisioners). |

Automatic plugin download is off, and exactly one version of each Pulumi plugin is installed. With a missing plugin
the converter does not fail; it silently writes wrong code.

Other versions I used, not chosen for a specific reason: Windows 11, Python 3.13.3, Node 22.14.0, TypeScript 5.9.3,
Docker Desktop 4.40.0, lstk 1.3.0 (to start LocalStack). The npm and pip versions of the Pulumi programs are in
`pipeline/config/package-lock.json` and `pipeline/config/requirements-lock-py.txt`. For Python, `pilot_runner.py setup`
pins the provider packages but installs the Pulumi SDK as `pulumi>=3.200,<4`; the lock file records the version that
was used (3.267.0).

## Main results

All numbers below are computed from the CSV files in this repository. Details: [results/RESULTS.md](results/RESULTS.md)
and [iv-adapter/README.md](iv-adapter/README.md).

**The package.** The package lists 422 tasks as passing IV. When I run the packaged rules on the original
`tfplan.json` files with OPA 1.1.0 and the original `extract_validation_status()`, 408 of the 422 still pass. I use
these 408 as the base set. The original error analyzer, re-run on the 6 experiment runs of the package, gives
identical reports for 6 of 6.

**Control group** (original Terraform, 410 tasks: the 408 base tasks plus tasks 83 and 110 from the pilot):

| Check | Result |
|---|---|
| `tflocal init` + `plan` | 410/410 |
| Rego rule passes | 408/410 (83 and 110 fail, as they do on the original plans) |
| Plan identical to the original `tfplan.json` (resource addresses and actions, endpoint set, provider regions) | 410/410 |

**`pulumi convert` baseline** (408 base tasks):

| | TypeScript | Python |
|---|---|---|
| Convert | 407 | 405 |
| TV: `pulumi preview` passes against LocalStack | 326 (79.9%) | 346 (84.8%) |
| EQ: same resources as the Terraform plan, among TV passes | 324/326 | 344/346 |

- Main causes of TV failures (TypeScript / Python): the generated VPC module code (25 / 23), resource names that
  Pulumi generates and AWS rejects (14 / 21), heredoc JSON escaped wrongly in TypeScript (19 / 0), other TypeScript
  type errors (12 / 0), helper files that are not in the dataset (10 / 13).
- The 4 convert failures were network timeouts while fetching the VPC module, not converter errors.
- The EQ misses are tasks 124 and 187 in both languages. Their plans contain no resources at all.

**IV through the adapter** (v2, variant P3src). 304 of the 458 rules read the `configuration` section of the Terraform
plan, which Pulumi does not produce. The adapter writes the Pulumi preview, plus the converted program text, as a
Terraform-style plan. The rules, the OPA command and the pass function run unchanged on it. Counted on the pairs where
TV passed and the control plan passes IV:

| | TypeScript | Python |
|---|---|---|
| IV passes (agrees with the control) | 314/326 (96.3%) | 331/346 (95.7%) |

In the 27 pairs where the adapter fails, 23 come from things a preview cannot show (data sources, root outputs,
masked passwords). 2 are task 3: the converter really dropped the provider aliases. TV did not notice this, IV did.
The last 2 are task 455, where a literal type is lost in conversion (`-1` vs `"-1"`). These numbers measure false
fails only, not false passes. The other variants and the limits are in
[iv-adapter/README.md](iv-adapter/README.md).

Two choices still wait for the supervisors' confirmation: the 408-task base set (instead of the 422 listed), and the
adapter as the IV method.

## How to reproduce

Everything ran on Windows 11, with PowerShell and Git Bash. `pilot_runner.py` and `recheck_supervisor_opa.py` use
`winreg`, so they only run on Windows. In short:

1. Install the pinned tools listed above. LocalStack needs your own auth token.
2. Optionally, check `original-package/` against the Zenodo zip with `pipeline\check_original_package.py`.
3. Re-check the results of the original package. No LocalStack is needed (the error analyzer needs pandas and numpy):
   ```powershell
   cd <repo>\pipeline
   python recheck_supervisor_opa.py
   python rerun_supervisor_error_analyzer.py initial_4o_Baseline
   ```
   The other five runs are checked the same way, with their folder name from
   `original-package/iac-research-without-agent/validation/runs/` (for example `naive_rag_4o`).
4. After every reboot, start Docker Desktop and LocalStack, and check LocalStack before any run.
5. Run the 30-task pilot: the control group, then the Pulumi baseline in both languages, and compare with
   `results/`. Use the run name `pilot-aligned`: `run_tf_refresh.sh` and `iv-adapter/run_full.py` read the pilot from
   that folder.
   ```powershell
   python pilot_runner.py tf --run pilot-aligned
   Copy-Item config\package-lock.json runs\pilot-aligned\
   python pilot_runner.py setup  --run pilot-aligned --lang typescript
   python pilot_runner.py setup  --run pilot-aligned --lang python
   python pilot_runner.py pulumi --run pilot-aligned --lang typescript
   python pilot_runner.py pulumi --run pilot-aligned --lang python
   ```
6. The rest of the base set in 4 parallel shards, from Git Bash:
   - `run_shards.sh` (wave 1). Its 4 shards still shared one Terraform plugin cache. In this wave the Terraform plan of
     tasks 16, 49, 98, 146, 304 and 440 failed with a provider error ("failed to read schema"), most likely because of
     the shared cache. They were run again in wave 2, so they appear in two shard lists.
   - `run_waves.sh` (the remaining waves) and `run_tf_refresh.sh` (the control group again, after pinning python-hcl2
     7.3.1). Here each shard has its own plugin cache (`THESIS_TF_PLUGIN_CACHE_DIR`).
   - Runs that broke while the machine was asleep were repeated with the same commands: 19 tasks on 8 October with
     `run_rerun.sh` (all stages, lists `tasks/shards/rerun-*.txt`), and tasks 214, 216 and 254 on 14 October (control
     group only: `python pilot_runner.py tf --run ext-w1-<shard> --tasks tasks/shards/rerun-tf-<shard>.txt`, with the
     shard's plugin cache). The committed results contain these repeated runs.

   The original code resets LocalStack after every task (`/_localstack/state/reset`). This endpoint was not available
   in my setup, so the reset call failed and no reset happened. Plan and preview create no resources, so nothing is
   carried over from one task to the next.
7. The IV adapter on all tasks. It needs the run folders from step 6, but no LocalStack:
   ```powershell
   cd <repo>\iv-adapter
   python -B run_full.py
   ```

Scripts that write a file in `results/` or `iv-adapter/results/` overwrite the committed copy, so `git diff` shows
any difference.

## About the code

The scripts in `pipeline/` and `iv-adapter/` are the ones that produced the results. Their paths are relative to the
script and follow this folder layout. Apart from the paths, they differ from the copies in my working folder only in
comments, a few printed messages and two local names (the plugin-cache variable `THESIS_TF_PLUGIN_CACHE_DIR` and the
Pulumi passphrase `thesis-local`); none of these affects the results.

Run from this repository, `recheck_supervisor_opa.py` and `build_task_table.py` write the same files that are committed
in `results/`, `iv-adapter/run_full.py` writes the same `iv-adapter/results/full408_v2/full_results.csv`, and
`rerun_supervisor_error_analyzer.py` gives the same report as the package for each of the six runs. The stages that need
LocalStack were not run again from here.

The line numbers that `iv-adapter/CHANGES.md` cites in `iv_adapter.py` point to the code in this repository.

## Use of an LLM

I used an LLM (Claude) during this work, but not to the same degree everywhere. The IV adapter was written mostly with
the LLM. Because of that, I checked it rule by rule against the source code of Terraform v1.5.7, Pulumi v3.267.0,
pulumi-terraform-bridge v3.104.0 and pulumi-converter-terraform v1.4.0. The two specs in `iv-adapter/specs/` were
written from that source code and cite files and line ranges at fixed tags. `iv-adapter/CHANGES.md` goes through every
rule: what the prototype did, what the source says and what was changed (40 fixes, 25 open points with reasons).
`iv-adapter/VERIFY.md` is an independent re-check of it and of the pilot re-run. The run on all base tasks then found
two more bugs, which version 2 fixes.

For the rest of the code, the LLM helped me write the pipeline scripts and the shell scripts, and it wrote most of the
comments and the documentation. I also used it for brainstorming. I decided the setup, the versions and the checks, ran
everything, and compared the results with the original package (see "About the code").
