# Terraform plan JSON (`terraform show -json`, v1.5.7): what the IV adapter must emit

Status: specification checklist, written 2026-10-15 (web research plus a check against the original plans).
Purpose: the IV adapter turns a Pulumi preview into a Terraform-plan-shaped JSON, so that each task's `intent.rego` can run on it unchanged. This file lists the rules (R-TF-n) that real Terraform 1.5.7 output follows, so the adapter can be held to them.

> **Note for this repository.** The check scripts in `../scripts/` and their output files named below stay in my working folder and are not included. Every rule cites its public source by URL at the `v1.5.7` tag, and the counts refer to the original dataset (`ground_truth/dataset`).

## 0. Sources and method

All code was read from the **`v1.5.7` tag** of `hashicorp/terraform` (commit `ee58ac1851c8a433005df9863ed47796a9f6b5e7`, from the GitHub API). Raw files came from `raw.githubusercontent.com/hashicorp/terraform/v1.5.7/...`. The line numbers below are from those raw files. Links use `https://github.com/hashicorp/terraform/blob/v1.5.7/<path>#L<a>-L<b>`.

| Tag | File (at v1.5.7) |
|---|---|
| DOC | `website/docs/internals/json-format.mdx` (the docs source at the tag). The versioned page https://developer.hashicorp.com/terraform/internals/v1.5.x/json-format says the same thing (checked with WebFetch: selector "v1.5.x", format_version "1.0", `resolved_source`, `proposed_unknown`, no `timestamp`). The live page https://developer.hashicorp.com/terraform/internals/json-format (selector v1.16.x) also lists `applyable`/`complete`/`errored`, which 1.5.7 does not emit. |
| PLAN | `internal/command/jsonplan/plan.go` |
| VAL | `internal/command/jsonplan/values.go` |
| RES | `internal/command/jsonplan/resource.go` |
| MOD | `internal/command/jsonplan/module.go` |
| CFG | `internal/command/jsonconfig/config.go` |
| EXPR | `internal/command/jsonconfig/expression.go` |
| STATE | `internal/command/jsonstate/state.go` |
| REFS | `internal/lang/references.go` |
| PREF | `internal/addrs/parse_ref.go` |
| IKEY | `internal/addrs/instance_key.go`; MI = `internal/addrs/module_instance.go`; RADDR = `internal/addrs/resource.go` |
| B2A | `internal/lang/blocktoattr/fixup.go` |
| SHOW | `internal/command/show.go`; BPLAN = `internal/backend/local/backend_plan.go`; PFW = `internal/plans/planfile/writer.go` |
| HCL | `hashicorp/hcl` **v2.16.2** (the version pinned in Terraform v1.5.7's `go.mod` L46): `hclsyntax/variables.go`, `traversal.go`, `hclsyntax/expression.go` |
| CTY | `zclconf/go-cty` **v1.12.2** (`go.mod` L79): `cty/json/value.go`, `cty/json/marshal.go`, `cty/set_internals.go` |

**Checks against real plans.** Scripts in `../scripts/` read the dataset and never write to it:
- `inspect_tfplans.py`: deep look at tasks 283, 3, 428 and 57.
- `inspect_details.py`, `find_null_const.py`: targeted checks.
- `census_plan_features.py`: which format features occur in the 426 `tfplan.json` files present (458 task folders). Output in `census_output.txt`.
- `census_idioms.py`: which rule idioms occur in the 458 `intent.rego` files and the 30 pilot tasks. Output in `census_idioms_output.txt`.

All 426 plans report `format_version` "1.2" and `terraform_version` "1.5.7".

**Reading the "IaC-Eval dependence" lines.** These are counts of `intent.rego` files (comments stripped) that match a regex for the idiom, written as "ALL n/458; PILOT n/30 (task ids)". They come from regex matching only, so treat them as approximate indicators, not proofs.

---

## A. Top-level object

**R-TF-1. Versions.** Set `"format_version": "1.2"` and `"terraform_version": "1.5.7"`. The code emits the constant `FormatVersion = "1.2"`. The docs still say "1.0".
- Source: PLAN L28-32 (constant), L68-72, L221-223. DOC L18-19 and L72 say "1.0".
- Real plans: all 426 say 1.2 / 1.5.7.
- IaC-Eval dependence: no rule reads these. Emit them anyway so the output looks like a real plan.

**R-TF-2. Top-level keys.** The plan struct has these keys, all `omitempty`: `format_version`, `terraform_version`, `variables`, `planned_values`, `resource_drift`, `resource_changes`, `output_changes`, `prior_state`, `configuration`, `relevant_attributes`, `checks`, `timestamp`. There is no `proposed_unknown`, although the docs list it.
- Source: PLAN L49-66. DOC L86-89 (`proposed_unknown`, docs only).
- Real plans: every plan has `format_version`, `terraform_version`, `planned_values`, `configuration` and `timestamp`. `resource_changes` 423/426, `relevant_attributes` 329, `prior_state` 143, `output_changes` 15, `variables` 4.
- IaC-Eval dependence: `resource_changes` 156/458 (PILOT 8); `planned_values` 123/458 (PILOT 7); `configuration.root_module.resources` 298/458 (PILOT 20).

**R-TF-3. `prior_state`.** Present only when the state stored in the plan file is non-empty. That state is the refreshed prior state, so for a fresh deployment it holds **only the data sources Terraform could read during planning**. Its shape is `{format_version: "1.0", terraform_version, values: <values-representation>}`.
- Source: PLAN L280-286. SHOW L182-206 (reads the plan's embedded `tfstate`). BPLAN L152-170 (`StateFile` = PlannedStateUpdate(…, plan.PriorState)). PFW L30-35. STATE L26 (`FormatVersion = "1.0"`).
- Real plans: 143/426 have `prior_state`. All of those contain data resources, and none contain managed resources (task 57 → `data.aws_iam_policy_document.KinesisAssume`; task 428 → `data.aws_availability_zones.available`).
- IaC-Eval dependence: `prior_state` 1/458 (an `archive_file` check); PILOT 0.

**R-TF-4. `variables`.** A map `name → {"value": …}` holding the values the caller set, plus declared root-variable defaults that Terraform adds back. The key is omitted when there are no variables.
- Source: PLAN L158-164, L298-350.
- IaC-Eval dependence: about 3/458 mention `variables`; PILOT 0.

**R-TF-5. Outputs.** `output_changes` and `planned_values.outputs` cover root-module outputs only. Each output is `{sensitive, type, value}`, and `value`/`type` are omitted when the value is unknown.
- Source: PLAN L550-638. VAL L48-94.
- IaC-Eval dependence: about 1/458; PILOT 0.

## B. Values representation (`planned_values`; also `prior_state.values`)

**R-TF-6. Module tree.** `planned_values` is `{outputs?, root_module: {resources?, child_modules?}}`. The root module has no `address`. Each child module has `address` (for example `module.vpc`) and may nest further `child_modules`. Child modules are sorted by address.
- Source: VAL L22-27, L96-166, L249-285. MOD L8-19.
- Real plans: 26/426 have `child_modules` (the `terraform-aws-modules/vpc` tasks).
- IaC-Eval dependence: `child_modules` 0/458.

**R-TF-7. What appears in `planned_values`.** Every planned resource instance whose action is not delete and which is not deposed. Data sources appear here **only if their read is deferred to apply**, which gives them a planned `read` change. Data sources read during planning are absent here and appear only in `prior_state` (R-TF-3).
- Source: VAL L106-112, L172-176.
- Real plans: data resources appear in `planned_values` in 13/426 plans, and these are exactly the 13 plans with a `read` change on a data resource (set equality checked). One example is task 57's `data.aws_iam_policy_document.StreamReaderWriter`, which references an unknown ARN.
- IaC-Eval dependence: `mode == "data"` or a `"data.` literal: 0/458.

**R-TF-8. Resource object.** Each resource object has these fields:
- `address`
- `mode`: `"managed"` or `"data"`
- `type`
- `name`: the HCL block label
- `index`: only with count/for_each
- `provider_name`: the **fully qualified** provider, for example `registry.terraform.io/hashicorp/aws`. The docs example shows `"aws"`.
- `schema_version`: always present, 0 included
- `values`
- `sensitive_values`

Source: RES L13-45. VAL L178-206. DOC L261-310 (docs example uses `"provider_name": "aws"`).
Real plans: task 283 has `provider_name` `registry.terraform.io/hashicorp/aws` and `schema_version` 0.
IaC-Eval dependence: `.type == "…"` 458/458 (PILOT 30/30). `.name == "…"` about 26/458 (PILOT 3: 3, 90, 91). For example, task 3 has `resource.name == "replica_us_east"` and task 90 has `role.name == "eks-fargate-profile"`, so the adapter must reproduce the **Terraform local names**.

**R-TF-9. `values` encoding.**
- If the after-value is wholly known, `values` holds every top-level attribute of the schema type, including attributes that are null.
- Otherwise, unknown object attributes are **omitted**, and unknown list, set or tuple elements become `null` so positions stay aligned.
- Maps and objects become JSON objects. Lists, sets and tuples become JSON arrays. Nested blocks become an array (list/set) or an object (single).

Source: VAL L33-46, L221-228. PLAN L671-725 (`omitUnknowns`). DOC L292-297 only says unknowns are "omitted or set to null".
Real plans: task 283 `aws_s3_bucket.example` has 24 unknown attributes, and none of them appears in `values`. Known nulls such as `tags` and `timeouts` do appear, as `null`.
IaC-Eval dependence: `planned_values` 123/458 (PILOT 7) and `.change.after` 127/458 (PILOT 6) both use this encoding (R-TF-16). Absent and null behave differently in Rego. `not x.after.a` is true when the key is absent, but false when it is present and null. 3/458 rules use `not` on such paths.

**R-TF-10. Set ordering in values.** Set-typed attributes come out in cty set order:
- strings sorted lexicographically
- numbers sorted numerically
- false before true
- complex elements in hash order

The `constant_value` of the same attribute in `configuration` keeps **source order** (it is the HCL value, not the provider-typed value).
- Source: CTY `cty/set_internals.go` L85-135.
- Real plans: task 57 data source `statement[0].actions` is `[DescribeStream, GetRecords, GetShardIterator]` in `planned_values` and `[DescribeStream, GetShardIterator, GetRecords]` in `constant_value`.
- IaC-Eval dependence: positional `constant_value[0]` 4/458 (for example `ingress.constant_value[0].protocol`). Positional `after.x[N] ==` / `values.x[N] ==` 0/458.

**R-TF-11. `sensitive_values`.** Same shape as `values`, but sensitive leaves are `true` and non-sensitive leaves are omitted from objects. Lists keep one entry per element (`false` or `{}`), and empty collections become `[]` or `{}`.
- Source: STATE L486-556. VAL L212-235.
- Real plans: task 283 has `"cors_rule": [{"allowed_methods": [false, false], …}]`.
- IaC-Eval dependence: 0/458.

**R-TF-12. Order of resources.** `root_module.resources` is sorted by plain **address string**, so `x[10]` comes before `x[2]` and `aws_*` before `data.*`.
- Source: VAL L240-242.
- Real plans: task 57 lists `aws_*` first and then `data.aws_iam_policy_document.StreamReaderWriter`.
- IaC-Eval dependence: positional `resources[N]` 0/458. Rules iterate with `some`/`[_]`.

## C. `resource_changes`

**R-TF-13. Which entries, in which order.** There is one entry per planned resource-instance change, deposed objects included. Data-source `delete` changes are dropped. Data sources read during planning do not appear at all. The list is sorted by `AbsResourceInstance.Less`, which compares in this order:
1. module path
2. mode, with **data before managed**
3. type
4. name
5. instance key, with numeric keys compared numerically

The docs say "all resources in the configuration are included", which does not hold for data sources.
- Source: PLAN L358-384, L262-268. RADDR L38-52, L122-132, L353-363. DOC L103-106.
- Real plans: task 57 lists the deferred `data.…StreamReaderWriter` first. Task 428 does not list `data.aws_availability_zones.available`.
- IaC-Eval dependence: `resource_changes` 156/458 (PILOT 8: 17, 31, 57, 127, 156, 175, 198, 233).

**R-TF-14. Entry fields.**
- `address`
- `previous_address`: only after a `moved` block
- `module_address`: omitted in the root module
- `mode`, `type`, `name`
- `index`: JSON number for count, JSON string for for_each
- `provider_name`: FQN
- `deposed`: only for deposed objects
- `change`
- `action_reason`: omitted when there is no reason

Source: RES L47-95. PLAN L370-537.
Real plans: in the root module the keys are `address, mode, type, name, [index], provider_name, change, [action_reason]`.

**R-TF-15. `change.actions`.** One of `["no-op"]`, `["create"]`, `["read"]`, `["update"]`, `["delete","create"]`, `["create","delete"]`, `["delete"]`. For a fresh plan:
- managed resources are `["create"]`
- deferred data sources are `["read"]` with `"action_reason": "read_because_config_unknown"`

The code also knows three reasons that the docs do not list: `replace_by_triggers`, `delete_because_no_move_target` and `read_because_check_nested`.
- Source: PLAN L802-821 (mapping), L34-47 and L504-535 (reasons). DOC L152-181.
- Real plans: 423 plans contain `create` and 13 contain `read`, the latter always with `read_because_config_unknown`.
- IaC-Eval dependence: `.actions` 36/458 (the common idiom is `resource.change.actions[_] == "create"`); PILOT 1 (233).

**R-TF-16. `before` / `after`.**
- For create, `before` is JSON `null`. The key is present because the prior value is a typed cty null, not the Go zero `cty.NilVal`, so it marshals to the literal `null`. `before_sensitive` is `false`.
- `after` follows R-TF-9: wholly known means all attributes; otherwise `omitUnknowns`.
- For creates, `after` is identical to `planned_values…values`.

Source: PLAN L98-104, L404-451.
Real plans: task 283 has `before: null` and `before_sensitive: false`, and `planned_values.values == change.after` for the bucket.
IaC-Eval dependence: `.change.after` 127/458 (PILOT 6: 17, 31, 57, 127, 156, 233).

**R-TF-17. `after_unknown`.**
- An object that has only the **unknown** leaves, set to `true`. Known leaves are omitted from objects.
- Lists keep one entry per element (`true`, `false` or a nested object), and empty collections become `[]` or `{}`.
- A wholly known after-value gives `{}`.

Source: PLAN L423-441, L727-800.
Real plans: task 428 `aws_route_table.public` has `"route": [{"gateway_id": true}]`. Task 283 has `"cors_rule": [{"allowed_headers": [false], …}]`.
IaC-Eval dependence: 3/458 (`after_unknown.encryption_info[_]…`); PILOT 0.

**R-TF-18. `before_sensitive` / `after_sensitive`.** Built like R-TF-11, but they also include sensitivity from the schema.
- Source: PLAN L413-421, L442-450.
- IaC-Eval dependence: 0/458.

**R-TF-19. Optional change fields.** `replace_paths` appears only for schema-forced replacement. `importing` and `generated_config` appear only for import.
- Source: PLAN L121-150, L457-477.
- IaC-Eval dependence: 0/458.

## D. `configuration`

**R-TF-20. Shape.** `configuration` is `{provider_config: {…}, root_module: {…}}`. The key is **`provider_config`** in the code. The docs prose calls it `provider_configs`, while the docs example uses `provider_config`.
- Source: CFG L21-25. DOC L357-361.
- Real plans: all inspected plans use `provider_config`.

**R-TF-21. `provider_config` entries.**
- **Keys** are opaque provider keys:
  - `"aws"` for the default configuration
  - `"aws.<alias>"` for aliased configurations
  - `"module.x:aws"` for configurations declared in a module; these are deleted when they only inherit from the parent
- **Entry fields:** `name`, `full_name`, `alias` (only for aliased configs), `version_constraint` (the resolved constraint), `module_address` (omitted in root), and `expressions` (the provider block as block expressions, R-TF-28..31).
- Required providers that have no block still get an entry.

Source: CFG L27-39, L148-305, L539-567, L135-142.
Real plans:
- Task 3 has keys `aws, aws.ap_southeast, aws.eu_central, aws.main, aws.us_east`, each with `alias`, `version_constraint "~> 5.75"` and its own `region`.
- Task 326 has only `aws`, because `module.vpc:aws` was folded into its parent.
- Observation: the original plans carry LocalStack arguments that are not in `main.tf` (`access_key "test"`, `endpoints`, `skip_*`). Task 3 also has an extra default `aws` entry (region us-east-1) that is not in `main.tf`.

IaC-Eval dependence: `input.configuration.provider_config.aws.expressions.region.constant_value == "us-east-1"` (or "us-east-2") in 7/458 (201, 202, 208, 210, 211, 212, 214); PILOT 0.

**R-TF-22. `provider_config_key`.** Each config resource has `provider_config_key = opaqueProviderKey(ProviderConfigAddr().StringCompact(), moduleAddr)`. That gives `"aws"`, `"aws.main"`, or `"module.x:aws"`. When the module inherits the provider, the key is rewritten to the parent's key.
- Source: CFG L81-87, L447, L522-537. DOC L417-422.
- Real plans: task 3 shows `aws.main`, `aws.us_east`, …. Resources inside task 326's module show `aws`.
- IaC-Eval dependence: `provider_config_key == "aws.<alias>"` 3/458; PILOT 1 (**task 3**, `resource.provider_config_key == "aws.main"`). The pilot miss on task 3 was attributed to aliases dropped by the converter. Without alias information this rule cannot pass.

**R-TF-23. Module object.** Each configuration module object has `outputs`, `resources`, `module_calls` and `variables` (`{default?, description?, sensitive?}`), each omitted when empty. `resources` lists **managed resources sorted by address, then data resources sorted by address**. It is not one global sort.
- Source: CFG L41-48, L307-374, L444-520 (sort at L516-519).
- Real plans: in task 57, `data.…KinesisAssume` and `data.…StreamReaderWriter` come after all `aws_*` resources.

**R-TF-24. Config resource fields.**
- `address`: **module-relative**. It is `v.Addr().String()`, so a resource inside `module.vpc` has address `aws_cloudwatch_log_group.flow_log`, while the docs call it an absolute address.
- `mode`, `type`, `name`, `provider_config_key`
- `provisioners` (optional)
- `expressions`: **omitted** when the block has no arguments
- `schema_version`: always present
- `count_expression` **or** `for_each_expression`: count wins; omitted when unset
- `depends_on`

Source: CFG L70-108, L444-520. DOC L408-409.
Real plans: in task 326 the module resources have unprefixed addresses. In task 4, `data.aws_availability_zones.available` has no `expressions` key. 36/426 plans have at least one resource with no `expressions`.
IaC-Eval dependence: `X.address in Y.expressions.<attr>.references` 80/458 (PILOT 4: 283, 287, 296, 316). This idiom works only because the config `address` (`type.name`) equals the bare reference entry (R-TF-35).

**R-TF-25. `depends_on`.** A list of `ref.Subject.String()` strings, for example `"aws_iam_role_policy_attachment.eks_cluster_policy"`. The same format is used on outputs and module calls.
- Source: CFG L500-512 (resources), L332-344 (outputs), L427-439 (module calls).
- Real plans: 57/426 have it; task 90 `aws_eks_cluster.cluster` lists two attachments.
- IaC-Eval dependence: 7/458; PILOT 1 (90: `k8s_patcher.depends_on != null`).

**R-TF-26. `count_expression` / `for_each_expression`.** Expression objects (R-TF-32..39). Task 428 has `{"references": ["local.subnet_count"]}`; a literal count gives `{"constant_value": 2}`.
- Source: CFG L464-472. DOC L443-448.
- Real plans: count 32/426, for_each 26/426.
- IaC-Eval dependence: 0/458.

**R-TF-27. `module_calls`.** A map `callName → {source, expressions, count_expression | for_each_expression, module, version_constraint, depends_on}`:
- `source` is the **raw string the user wrote**. The docs instead document `resolved_source`.
- `expressions` treats module arguments as attributes named after the child variables.
- `module` is the recursive module object (R-TF-23).
- `version_constraint` is omitted when empty.

Source: CFG L50-58, L376-442. DOC L456-484.
Real plans: task 326 has `source "terraform-aws-modules/vpc/aws"` and no `version_constraint`.
IaC-Eval dependence: 0/458.

## E. Block expressions (`expressions` maps)

**R-TF-28. Only written arguments.** The map has an entry only for arguments that appear in the source. HCL `PartialContent` against the schema leaves unset arguments **absent**, not null.
- Source: EXPR L95-123.
- IaC-Eval dependence: presence-only checks such as `expressions.<attr> != null` 85/458; PILOT 8 (90, 330, 334, 335, 337, 338, 428, 432).

**R-TF-29. Nested blocks follow schema nesting.**
- NestingSingle/Group: one block-expressions **object**.
- NestingList/Set: an **array** of block-expressions objects, one per block, in source order.
- NestingMap: an object keyed by the block label.
- The recursion applies inside nested blocks too.

The docs example labels a single block `<expression-representation>`, but the prose and the code produce a nested block-expressions object.
- Source: EXPR L125-153. DOC L537-547.
- Real plans: task 283 has `cors_rule[0].allowed_methods.constant_value`. Task 57 has `inputs[0].schema[0].record_format[0].mapping_parameters[0].json[0].record_row_path`. Task 3 has `weighted_routing_policy[0].weight`.
- IaC-Eval dependence: block iteration `expressions.<blk>[_]`, `[0]` or `some … in expressions.<blk>` 106/458; PILOT 7 (3, 31, 90, 209, 283, 296, 316).

**R-TF-30. Attributes written as blocks (legacy SDK `ConfigModeAttr`).** Some provider attributes are typed list/set-of-object but written with block syntax, for example aws `aws_security_group.ingress/egress`, `aws_route_table.route` and `aws_network_acl.ingress/egress`. For these, `FixUpBlockAttrs` merges all such blocks into **one expression**:
- If every block is constant, `constant_value` is a list of objects that contains **every element attribute**, with missing ones set to `null`.
- Otherwise there is only `references`, the union over all blocks, and the constant parts are lost.

Whether this applies depends on the provider **schema**, not on the syntax.
- Source: EXPR L103-104. B2A L15-53, L155-201, L203-248.
- Real plans:
  - Task 428: `aws_route_table.public.expressions.route = {"references": ["aws_internet_gateway._.id", "aws_internet_gateway._"]}`. The constant `cidr_block` is gone.
  - Task 343: `aws_security_group.main.expressions.ingress = {"constant_value": [{"cidr_blocks": ["0.0.0.0/0"], …, "ipv6_cidr_blocks": null, "self": null, …}]}`.
  - 9/426 plans have such constant lists.
- IaC-Eval dependence: `expressions.(ingress|egress|route)` 15/458 (PILOT 1: 428). Positional `ingress.constant_value[0].protocol == "tcp"` occurs in 4/458.

**R-TF-31. `dynamic` blocks are not represented.**
- Source: EXPR L106-111. DOC L524.

## F. Expression representation (`constant_value` / `references`)

**R-TF-32. When `constant_value` is present.** Only when the expression, evaluated with a **nil EvalContext**, gives a value that `ctyjson.Marshal` can encode, meaning a wholly known value:
- Literals, lists and maps of literals, and templates without interpolation qualify.
- Any variable or resource reference gives an unknown value, so no `constant_value`.
- **Any function call** (`jsonencode(...)`, `file(...)`, …) also gives an unknown value, even if all its arguments are literals.
- A literal `null` gives `{"constant_value": null}`, with the key present.

Source: EXPR L38-48. HCL `traversal.go` L65-98 (nil context gives `cty.DynamicVal` plus "Variables not allowed"). HCL `hclsyntax/expression.go` L240-251 ("Function calls not allowed", `cty.DynamicVal`). CTY `cty/json/marshal.go` L27-28 (unknown gives an error) and `cty/json/value.go` L44-52 (error means nil bytes).
Real plans:
- Task 6: `assume_role_policy = jsonencode({...})` gives `{}`.
- Task 326 module `aws_default_network_acl.this.subnet_ids` gives `{"constant_value": null}` (26/426 plans).

IaC-Eval dependence: `constant_value` 223/458; PILOT 16 (3, 17, 83, 90, 110, 283, 287, 296, 316, 330, 334, 335, 337, 338, 408, 432).

**R-TF-33. Empty expressions `{}` are legal and common.** A function call with no references gives `{}`, with neither key. The adapter must not invent a `constant_value` for, say, a `jsonencode` policy. Terraform does not emit one.
- Source: same as R-TF-32. EXPR L86-88 (`Empty()`).
- Real plans: 68/426 plans have at least one `{}` expression; the usual case is `assume_role_policy = jsonencode(...)`.

**R-TF-34. `constant_value` and `references` are computed independently.** In practice they never occur together, because an expression with a reference is never wholly known.
- Source: EXPR L44-81.
- Real plans: 0 expressions with both keys in 426 plans.

**R-TF-35. How `references` is built (order matters).** References are processed in `expr.Variables()` order, which is source order. For each reference:
1. Emit `Subject + remaining traversal`.
2. Drop one trailing step at a time and emit each result.
3. Emit the bare `Subject`.
4. Then add one more entry when it applies:
   - if the subject is a **keyed resource instance**, the un-keyed resource;
   - if it is a **module output**, the module call;
   - if it is a **keyed module instance**, the module call.

Index steps are written `[0]` or `["key"]`. The `.attr` form always comes **before** the bare `type.name`.

Source: EXPR L50-81, L158-184. REFS L27-45, L75-84. HCL `hclsyntax/variables.go` L14-56. DOC L501-520 (example list, consistent).

Real plans:

| Expression | `references` |
|---|---|
| `aws_s3_bucket.example.id` | `["aws_s3_bucket.example.id", "aws_s3_bucket.example"]` (task 283) |
| `aws_eks_cluster.cluster.certificate_authority[0].data` | `["…certificate_authority[0].data", "…certificate_authority[0]", "…certificate_authority", "aws_eks_cluster.cluster"]` (task 90) |
| `data.aws_availability_zones.available.names[0]` | `["…names[0]", "…names", "data.aws_availability_zones.available"]` (task 4) |
| `var.x` | `["var.x"]` (from the code) |
| `module.m.out` | `["module.m.out", "module.m"]` (from the code) |

IaC-Eval dependence:
- `references[0] == "type.name.attr"` 31/458; PILOT 3 (3, 83, 432). This needs the attribute-first order and the **correct attribute name** (`.arn`, `.name`, `.id`, `.zone_id`, `.endpoint` …).
- `references[0]` used at all: 67/458 (PILOT 3, 17, 31, 83, 432).
- `address in …references`: 80/458 (R-TF-24).
- `references[1]`: 0/458.

**R-TF-36. Subject grammar.**
- `type.name`, plus `[key]` only if the next step is a literal index
- `data.type.name[...]`
- `module.call`, `module.call[key]`, `module.call[key].output`
- `var.x`, `local.x`, `path.x`, `terraform.x`, `count.x`, `each.x`
- `self`
- the `resource.` escape

Source: PREF L114-298 (roots), L301-393 (resource refs), L180-251 (module refs).

**R-TF-37. No deduplication.** Every occurrence of a traversal yields its own expansion, so repeated subjects repeat.
- Source: REFS L18-21. EXPR L50-81.
- Real plans: 41/426 plans contain duplicate entries. Task 60 `policy` has `["aws_s3_bucket.januarysecond.arn", "aws_s3_bucket.januarysecond", "aws_s3_bucket.januarysecond.arn", "aws_s3_bucket.januarysecond", …]`.
- Task 90 example: `null_resource.k8s_patcher.triggers` has exactly 8 entries:
  - `endpoint` contributes 2
  - `certificate_authority[0].data` contributes 4, including a second `aws_eks_cluster.cluster`
  - `data.aws_eks_cluster_auth.eks.token` contributes 2

  Its rule requires `count(k8s_patcher.expressions.triggers.references) == 8`. That count depends on exact expansion, the duplicate, and the **data-source** reference. This fits the reported Python miss on task 90, but I did not re-run the adapter to confirm it.
- IaC-Eval dependence: `count(…references)` 10/458; PILOT 2 (90: `== 4` and `== 8`; 209).

**R-TF-38. Only static traversals count.** Only root scope traversals with literal steps are collected. A dynamic index ends the traversal: `aws_subnet.public[count.index].id` gives `["aws_subnet.public", "count.index"]`, with **no** `.id` and no keyed form. Function wrappers are transparent: `base64decode(x.y.z)` still yields `x.y.z…`.
- Source: HCL `hclsyntax/variables.go` L28-56 (only `ScopeTraversalExpr` nodes). PREF L362-370 (no remaining steps gives a bare `Resource` subject).
- Real plans: task 428 `aws_route_table_association.public.subnet_id` is `["aws_subnet.public", "count.index"]`, and `cidr_block = [...][count.index]` gives `["count.index"]`. 30/426 plans have a bare resource reference with no attribute form.

**R-TF-39. For-expression locals are excluded.** Variables local to a `for` expression (`[for s in aws_subnet.x : s.id]`) are left out; only the collection traversal (`aws_subnet.x`) is reported.
- Source: HCL `hclsyntax/variables.go` L40-53 (ChildScope local names).

## G. Instance addresses and keys

**R-TF-40. Instance addresses.**
- Count instance: `type.name[0]`.
- for_each instance: `type.name["key"]`, with an HCL-quoted key.
- Module instances: `module.m[0].…` or `module.m["k"].…`.
- `index` is a JSON number for count and a JSON string for for_each, in both `planned_values` and `resource_changes`.
- The **config** resource (R-TF-24) is a single entry with no index.

Source: IKEY L56-88. MI L265-288. PLAN L483-489. RES L23-24, L75. DOC L273-277.
Real plans: task 428 has `aws_subnet.public[0]` and `[1]` with `"index": 0` and `1`, while config has one `aws_subnet.public` with `count_expression`. 32/426 plans have int indices; there are no string indices in the dataset.
IaC-Eval dependence: `.index` 0/458.

**R-TF-41. Module placement.** Resources inside modules:
- in `resource_changes`, carry `module_address` (`module.vpc`) and a full address (`module.vpc.aws_x.y[0]`);
- in `planned_values`, sit under `child_modules[*].resources`;
- in `configuration`, sit under `module_calls.<name>.module.resources`, with module-relative addresses.

Source: PLAN L499. VAL L96-166. CFG L376-442.
Real plans: task 326.
IaC-Eval dependence: 0/458.

## H. Consistency invariants across sections

**R-TF-42. Cross-section invariants.** These follow from the rules above, and the rules depend on them:
1. The config `type`/`name` equal the `type`/`name` in `planned_values` and `resource_changes`.
2. The config `address` (module-relative `type.name`) equals the bare entries that other resources' `references` contain (R-TF-24, R-TF-35).
3. Every root `provider_config_key` is a key of `provider_config`.
4. For creates, `planned_values…values` equals `resource_changes[].change.after`.
5. A data source shows up in exactly one of `prior_state` (read during plan) or `planned_values` plus `resource_changes` (deferred read).

Source: CFG L135-142, L447-453. VAL L178-228. PLAN L404-451.
Real plans: checked on tasks 283, 3, 428 and 57.

---

## Docs vs code differences (Terraform v1.5.7)

| # | Topic | Docs (DOC = v1.5.7 mdx) | Code at v1.5.7 / real plans |
|---|---|---|---|
| D1 | `format_version` | "1.0" (L18-19, L72) | `"1.2"` (PLAN L32); 426/426 plans say 1.2. `prior_state.format_version` is "1.0" (STATE L26). |
| D2 | `proposed_unknown` | listed (L86-89) | not in the plan struct (PLAN L51-66); absent from all plans |
| D3 | top-level `terraform_version`, `timestamp` | not in the plan example | emitted (PLAN L53, L65, L222-223) |
| D4 | provider map key | prose says `provider_configs` (L357); example says `provider_config` (L361) | `provider_config` (CFG L23) |
| D5 | module-call source | `resolved_source` (L461-467) | `source`, raw as written (CFG L51, L393-401); also `version_constraint`, `depends_on` |
| D6 | config resource `address` | "opaque absolute address" (L408) | module-relative `v.Addr().String()` (CFG L449); task 326 module resources have no `module.vpc.` prefix |
| D7 | single nested block | example shows `<expression-representation>` (L543) | nested block-expressions object (EXPR L136-138) |
| D8 | `provider_name` | example `"aws"`, described as just the provider name, with no module path or alias (L279-286) | FQN `registry.terraform.io/hashicorp/aws` (VAL L182, PLAN L502) |
| D9 | coverage of `resource_changes` | "All resources in the configuration are included" (L104-106) | only planned changes; data sources read at plan time live only in `prior_state` (PLAN L263-268, L378-384; BPLAN L152-170) |
| D10 | unknowns in values | "omitted or set to null" (L292-297) | object attributes omitted; list/set elements set to null (PLAN L678-725) |
| D11 | fields the docs do not list | — | config `variables`, `depends_on`, output `description`; provider `version_constraint`; change `importing`, `generated_config`; `action_reason` values `replace_by_triggers`, `delete_because_no_move_target`, `read_because_check_nested` (CFG L35, L47, L107, L113-114; PLAN L37, L43, L46, L134, L142) |
| D12 | when `constant_value` is set | "set only if the expression contains no references" (L496-499) | stricter: also absent for any function call or other expression that is not wholly known with a nil context, giving `{}` (EXPR L44-48; HCL expression.go L240-251) |
| D13 | `references` details | example list only (L507-520) | no dedup (REFS L18-21); dynamic index ends the traversal (HCL variables.go); attributes-as-blocks merge into one expression (B2A). Not documented. |
| D14 | live docs (v1.16.x) | add `applyable`, `complete`, `errored` | not emitted by 1.5.7; no rule uses them |

## What each adapter variant must satisfy (mapping only, not a new measurement)

- **P1** (`planned_values` + `resource_changes`): R-TF-1..19 and 40-42. Most important are R-TF-8 (local `name`, `type`), R-TF-9/16 (absent vs null, unknowns omitted) and R-TF-15 (`actions`).
- **P2** (+ `configuration` `constant_value`): adds R-TF-20..34. Watch for R-TF-30 (attributes-as-blocks become one list-of-objects constant with nulls), R-TF-32/33 (no constants through function calls; `{}` is legal), R-TF-28 (absent unset arguments), R-TF-29 (list nesting of blocks) and R-TF-21/22 (alias-aware `provider_config` keys; task 3).
- **P3** (+ `references`): adds R-TF-35..39. The exact order (attribute first, then bare `type.name`, then un-keyed resource), the **true attribute name**, duplicates (R-TF-37), data-source subjects (`data.type.name.attr`), the dynamic-index truncation (R-TF-38) and `count.index`/`each.*`/`var.*`/`local.*` entries all affect rules that use `references[0]`, `count(...)` or `address in`.
