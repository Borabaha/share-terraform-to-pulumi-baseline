# Pulumi side of the IV adapter: specification (R-PU rules)

Written 15 Oct 2026 for Bora's MSc thesis (Terraform to Pulumi translation; IV = the original study's unchanged
`intent.rego` evaluated by OPA 1.1.0 on a Terraform-plan-shaped JSON).

These are the rules the IV adapter has to follow when it reads `pulumi preview --json` output and turns
Pulumi names and shapes back into Terraform ones. Each rule cites a source (URL plus file and line range,
paraphrased) and, where possible, a check against the pilot data in
`pipeline/runs/pilot-aligned/<task>/`.

> **Note for this repository.** The local source copies (`specs/src/`) and the check scripts named below
> (`survey_preview.py`, `check_keys.py`, `validate_reversal.py`, `check_defaults.py`, `compare_metadata.py`,
> `compare_schema.py`, `compare_heuristic.py`, `get_mapping.py`) stay in my working folder and are not included.
> Every rule cites its public source by URL at a fixed tag. The aws get-mapping file is included as
> `tables/aws-6.72.0-terraform-mapping.json`.

## 0. Version pins, how the rules were checked, abbreviations

| Component | Version used in the pilot | Source tag cited below |
|---|---|---|
| Pulumi CLI / engine / SDKs | 3.267.0 (`pulumi version`; `@pulumi/pulumi` 3.267.0 in `runs/pilot-aligned/node_modules`) | `pulumi/pulumi@v3.267.0` |
| pulumi-aws provider | 6.72.0 (plugin `resource-aws-v6.72.0`, `@pulumi/aws` 6.72.0) | `pulumi/pulumi-aws@v6.72.0` |
| pulumi-terraform-bridge (built into pulumi-aws 6.72.0) | v3.104.0 (pulumi-aws `provider/go.mod` L19) | `pulumi/pulumi-terraform-bridge@v3.104.0` |
| Upstream TF provider inside pulumi-aws 6.72.0 | terraform-provider-aws **v5.90.1**: the `upstream` submodule SHA `32ce1ab8…` equals the commit behind tag v5.90.1 (GitHub API). The original plans were made with aws **5.90.0**. | n/a |
| Terraform-to-Pulumi converter | `converter-terraform-v1.4.0` (installed plugin) | `pulumi/pulumi-converter-terraform@v1.4.0` |
| pluralizer used by the bridge | `github.com/pulumi/inflector v0.1.1` (bridge `go.mod` L46) | `pulumi/inflector@v0.1.1` |
| Pulumi docs | `pulumi/docs` master at `f7d743e61ea702512df3d0afa9ea47a2ce84c96d` (14 Oct 2026) | n/a |

URL prefixes (each line range is a GitHub `#Lx-Ly` anchor on that blob):

- **PU** = `https://github.com/pulumi/pulumi/blob/v3.267.0/`
- **BR** = `https://github.com/pulumi/pulumi-terraform-bridge/blob/v3.104.0/`
- **AWS** = `https://github.com/pulumi/pulumi-aws/blob/v6.72.0/`
- **CV** = `https://github.com/pulumi/pulumi-converter-terraform/blob/v1.4.0/`
- **INF** = `https://github.com/pulumi/inflector/blob/v0.1.1/inflector.go`
- **DOCS** = `https://github.com/pulumi/docs/blob/f7d743e61ea702512df3d0afa9ea47a2ce84c96d/`

Local copies of every cited file (downloaded with curl at the tags above) are in `iv-study/specs/src/`.
Two artefacts were produced locally from the installed aws 6.72.0 plugin. Neither touches the cloud or
any stack state:

- `src/aws-6.72.0-get-mapping-terraform.json`: `pulumi package get-mapping terraform aws@6.72.0` (10.66 MB; 1,497 resources, 605 data sources). Script: `get_mapping.py`.
- `src/aws-6.72.0-schema.json`: `pulumi package get-schema aws@6.72.0` (35 MB).

Scripts that check the rules against the data. All of them only read their inputs. Their outputs are quoted in the rules below.

| Script | What it checks |
|---|---|
| `survey_preview.py` | structure of all 60 pilot preview files (30 tasks × TS/Py) |
| `check_keys.py` | inputs keys vs `propertyDependencies` vs `__defaults`, autonames, unknowns, flattened objects |
| `validate_reversal.py` | full reversal (token, resource name, every program-set key, MaxItemsOne, values) against the control `terraform/plan.json`; writes `out/validate_reversal.json` |
| `check_defaults.py` | provider-filled defaults vs control TF plan values |
| `compare_metadata.py` | local `bridge-metadata.json` vs runtime `get-mapping` (tokens, maxItemsOne) |
| `compare_schema.py` | naming plus MaxItemsOne port vs the real Pulumi package schema, all resources and nested blocks |
| `compare_heuristic.py` | heuristic plural reversal (as in the 6 Oct prototype) vs the exact algorithm |

---

## A. Getting the input

**R-PU-1: Use `pulumi preview --json` in digest mode. Never use the streaming mode.**
`--json` is described as serialising the preview diffs, operations and overall output as JSON. The setting
`PULUMI_ENABLE_STREAMING_JSON_PREVIEW` switches to a stream of engine events instead
(PU `pkg/cmd/pulumi/operations/preview.go` L760-L763). In digest mode the CLI collects every engine event
and prints a single indented JSON document at the end (PU `pkg/backend/display/display.go` L118, L126-L141;
PU `pkg/backend/display/json.go` L157-L268, the print happens at L264-L267). A hidden `--output json` flag
also exists. It produces a different "structured operation summary" and cannot be combined with `--json`
(preview.go L401-L409, L764-L769). The adapter must make sure the streaming variable is unset, and must not
use `--output json`. The `--json` page in DOCS `content/docs/iac/cli/commands/pulumi_preview.md` L48 says
the same thing.

**R-PU-2: Top-level shape.**
`PreviewDigest` = `{config, steps, diagnostics, duration, changeSummary, maybeCorrupt}`, all `omitempty`
(PU `pkg/display/json.go` L31-L48). `duration` is a Go `time.Duration`, i.e. nanoseconds. `config` holds
the stack config with secrets blinded (json.go L180-L182).
*Pilot:* all 60 files have `config`, `steps`, `duration` and `changeSummary`. 19 also have `diagnostics`.
No file has `maybeCorrupt`.

**R-PU-3: A failed preview still emits a digest, but with partial steps.**
Diagnostics (warnings and errors) are added to the digest (json.go L185-L194), failed-operation events are
ignored (L238-L241), and the document is printed anyway. So a preview that failed contains only the
resources registered before the error.
*Pilot:* task 156 TypeScript printed `steps` = [Stack, iam Role] plus one `severity: "error"` diagnostic
(an invalid `event_pattern` JSON). The adapter must decide eligibility from the preview exit code (or an
error-severity diagnostic) and never from the presence of steps.

**R-PU-4: Preview against an empty stack.**
`shouldShow` hides `same` steps unless `--show-sames` is given. With `--json` it also hides non-logical
replacement steps unless `--show-replacement-steps` is given (PU `pkg/backend/display/display.go`
L317-L338). On a stack that already has state, unchanged resources would silently disappear.
*Pilot:* every one of the 216 steps is `op: "create"` (each run used fresh state).

**R-PU-5: Step shape.**
`PreviewStep` = `{op, urn, provider, oldState, newState, diffReasons, replaceReasons, detailedDiff}`.
`oldState` and `newState` are `apitype.ResourceV3`. `detailedDiff` has no `omitempty`, so it is always
present and is `null` for creates (PU `pkg/display/json.go` L58-L76). Steps are built by
`getPreviewMetadataStep` (PU `pkg/backend/display/json.go` L270-L317).
*Pilot:* step keys are `op, urn, newState, detailedDiff` (216/216) plus `provider` (156, every step except
the stacks).

**R-PU-6: What to skip.**
The root stack (`pulumi:pulumi:Stack`, `custom: false`) is always emitted (json.go L213 `isRootStack`).
Only `custom: true` resources correspond to Terraform resources. Component resources (`custom: false`) and
provider resources (`pulumi:providers:<pkg>`) are not resources in Terraform's sense. Provider resources
are still read for R-PU-25.

## B. What `newState` contains

**R-PU-7: `newState` is the state before the step runs. A create step has no `outputs`.**
The digest's steps come from `ResourcePreEvent`, which fires before the step executes. Outputs events only
replace steps for refresh operations (json.go L209-L237). The new state's metadata is `step.New()`
(PU `pkg/engine/events.go` L530-L557). For a create, that state is built from the program's goal with
`Outputs: nil` (PU `pkg/resource/deploy/step_generator.go` L851-L871, nil at L858). The `ResourceV3`
fields are listed in PU `sdk/go/common/apitype/core.go` L489-L565.
*Pilot:* 0 of 216 steps carry `outputs`. Provider-computed attributes (`arn`, `id`, `endpoint`, …) are never
visible. This matches Terraform, where they are unknown at plan time anyway.

**R-PU-8: `inputs` holds the provider-checked inputs, not the program text.**
The engine replaces `new.Inputs` with the provider's `Check` result (step_generator.go L1354-L1396). For
bridged providers that result contains:
- provider-applied defaults, listed in `__defaults` (R-PU-12);
- Pulumi-generated names (R-PU-13);
- provider pre-check rewrites such as `tagsAll` (R-PU-15).

The key set the program (or the SDK) actually wrote is the set of keys in `propertyDependencies` (R-PU-18).
*Pilot:* for 148 of 156 custom resources, `inputs` keys = `propertyDependencies` keys ∪ `__defaults`. All 8
exceptions are `tagsAll` (tasks 90 Py and 432). The two sets never overlap.

## C. Values

**R-PU-9: The unknown sentinel. One string for every type, at any depth.**
In serialized state and preview JSON every computed value, whatever its type (string, number, bool, list,
object), is written as the string `04da6b54-80e4-46f7-96ec-b56ff0331ba9` (PU
`pkg/resource/stack/deployment.go` L62-L66, L796-L797). An unknown `Output` is first made computed and then
serialized the same way (L802-L813).

Typed sentinels also exist: bool, number, array, asset, archive and object each have their own UUID
(PU `sdk/go/common/resource/sig/sig.go` L44-L78). They are used only on the gRPC wire
(PU `sdk/go/common/resource/plugin/rpc.go` L68-L74, L279-L301). The adapter should still accept all 7 as
unknown, defensively.

The update-plans docs say the same UUID represents unknown values (DOCS
`content/docs/iac/operations/stack-management/update-plans.md` L184-L189). Provider references use the same
UUID as the unknown provider ID (R-PU-25).

Mapping to Terraform: leave the attribute out of `planned_values` / `change.after` and set `after_unknown`
to `true` at that path. In `configuration` the expression exists but has no `constant_value`.

*Pilot:* 116 sentinel occurrences, all inside `inputs`. On the 154 paired resources, 99 unknown leaves were
found. In 99 of 99 cases the control TF plan had no value at that path and `after_unknown` was `true`. In 0
cases Terraform knew a value that Pulumi did not.

**Granularity caveat for TF sets.** When a Pulumi list holds an unknown element and the TF attribute is a
set (get-mapping type 7), Terraform marks the whole attribute unknown. Examples: `aws_route53_record.records`
in task 3, `subnet_ids` in tasks 90, 91 and 175 (11 cases). For such attributes, any unknown element makes
the whole attribute unknown. (TF lists were not observed with unknown elements in the pilot, so their case
is unverified.)

**R-PU-10: Secrets are always printed as the string `"[secret]"`, even with `--show-secrets`.**
`stateForJSONOutput` calls `MassageSecrets(s.Inputs, false)`, with show-secrets hard-wired to false, and
`massagePropertyValue` turns every secret into the string `[secret]` (PU `pkg/backend/display/json.go`
L45-L71, L85-L98). `SerializeResource` is also called with showSecrets false (L299, L308).

Where secrets come from: the generated SDK wraps inputs that the schema marks as secret. In the local
`@pulumi/aws` 6.72.0 `rds/instance.js`, `password` is wrapped in `pulumi.secret` at L446 and
`additionalSecretOutputs: ["password"]` is added at L480. This is why the field shows up in `newState`.

Adapter: treat `"[secret]"` as "set by the program, value not visible". In `configuration` the key exists
but has no `constant_value`. Never compare the value. The only Pulumi artefact that can carry the plaintext
is a saved plan with `--show-secrets` (preview.go L704-L710; R-PU-33). Otherwise the value can only be
recovered from program text.
*Pilot:* 4 occurrences, all `password` of `aws_db_instance` (tasks 3 and 408, TS and Py). The control TF plan
holds a plaintext `constant_value` for these.

**R-PU-11: Signature objects.**
A dict containing the key `4dabf18193072939515e22adb298388d` is a typed value. The signature value says
which type (sig.go L17-L42):

| Signature value | Type |
|---|---|
| `c44067f5…` | asset |
| `0def7320…` | archive |
| `5cf8f730…` | resource reference: `urn`, optional `id`, `packageVersion` (deployment.go L842-L853) |
| `803fd329…` | byte string: base64 `value` (L896-L901) |
| `8ad145fe-0d11-4827-bfd7-1abcbf086f5c` | float NaN/Inf, hex `value` (deployment.go L903-L912) |

Secret objects (`1b470612…`) cannot appear in a preview digest because of R-PU-10. Strings that are not
valid UTF-8 are printed as `b"<base64>"` (json.go L39-L51).

Assets and archives map to the Terraform field given by the field's asset translation in get-mapping
(`fields[tf].asset`). For `aws_lambda_function`, the Pulumi property `code` replaces TF `filename`, and the
bridge fills the hash field `source_code_hash` (AWS `provider/resources.go` L2887-L2898).
*Pilot:* 1 archive (task 156 Python, `code`). Its `path` `./supplement/lambda_func.zip` equals TF
`filename` in the control plan.

**R-PU-12: `__defaults`: provider-filled keys, on every object level.**
Each object value carries a hidden key `__defaults` that records which properties were filled by default
values (BR `pkg/tfbridge/schema.go` L131-L133, L182-L187). The list holds **Pulumi** property names
(`getInfoFromTerraformName`, L769, appended at L853) and is sorted (L951-L954). Defaults come from:
- bridge overlays: literal values, env/config values, computed functions including autonames
  (schema.go L720-L867);
- TF schema defaults (schema.go L870 onward).

`__meta` is another reserved key (L1016-L1017). Both are skipped when converting to TF (L612-L615).

Adapter rules:
- strip `__defaults` and `__meta` everywhere;
- keys listed in `__defaults` were not written by the program, so they get no `configuration` expression
  (TF configuration only lists attributes that were written);
- they do belong in `planned_values`, because a TF plan also contains schema defaults;
- nested objects work the same way: their program-set keys are their keys minus their own `__defaults`.

*Pilot:* paired resources have 304 top-level default-filled keys. 298 equal the control TF planned value.
The other 6 are Pulumi-generated names that Terraform leaves unknown (R-PU-13). Non-empty nested
`__defaults` occur in 7 block kinds (e.g. `rootBlockDevice.deleteOnTermination`,
`vpcConfig.endpointPrivateAccess`).

**R-PU-13: Pulumi-generated names are known in the Pulumi preview but unknown in the TF plan.**
Auto-named properties get a value built from the URN name, a separator and 7 random hex characters, already
during preview. The bridge sources:
- BR `pkg/tfbridge/names.go` L283-L303 (`-` plus 7 random characters);
- BR `pkg/tfbridge/info/autonaming.go` L94-L109 (`Randlen: 7`) and L147-L229 (URN name at L170;
  `NewUniqueName` at L212-L219; engine autonaming modes at L174-L211).

The docs agree: physical names default to the logical name plus a random suffix (DOCS
`content/docs/iac/concepts/resources/names.md` L129-L140). get-mapping flags these fields with
`default.autonamed: true`.

Some providers use their own functions instead, flagged only `default.isFunc: true`. Example: the
`aws_db_instance.identifier` default is `NewUniqueHex(name, 7, maxlen)`, with **no separator** (AWS
`provider/resources.go` L3207-L3223).

In Terraform these attributes are missing from the configuration and unknown in the plan. Adapter:
- treat every `__defaults` key whose get-mapping default is `autonamed` or `isFunc` as "not configured;
  unknown in plan";
- treat any downstream value whose `propertyDependencies` points at the generating resource as a reference,
  never as a constant (R-PU-21).

*Pilot:* 6 generated names: 4 flagged autonamed (iam Role `name` ×2 in task 296, lambda Permission
`statementId` and EventTarget `targetId` in task 156 Py) and 2 isFunc (`identifier` `default9b13782` /
`defaultd973820`, task 408). The control TF plan has all 6 unknown. In task 296 the autoname also flows into
`aws_iam_role_policy_attachment.role` as a *known* string in Pulumi, while TF has `role` unknown with a
reference in configuration.

Possible alternative: auto-naming can be configured as `mode: verbatim` or `mode: disabled` (names.md
L349-L381). This would not reproduce Terraform's unknowns either, so the unknown treatment above is
preferred.

**R-PU-14: SDK-side schema defaults look like program-set values.**
The generated SDK applies Pulumi package-schema defaults before it registers the resource. Example: in the
local `@pulumi/aws` 6.72.0 `route53/zone.js` L117, `comment` falls back to "Managed by Pulumi". Such keys
appear in `propertyDependencies` (with `[]`) and **not** in `__defaults`, and their values can differ from
the TF default. Bridge overlay defaults can differ too: `managedByPulumi` is used for several description
fields (AWS `provider/resources.go` L840-L841). get-mapping shows them as `default.value` (e.g.
`aws_security_group.description`).

Adapter: keep a list of these Pulumi-only defaults from the package schema (`default` fields) plus
get-mapping (`default.value`). Treat them as defaults, i.e. no configuration expression. Do not take their
value as the TF value.
*Pilot:* 4 of the 5 value disagreements on paired resources are exactly this
(`aws_route53_zone.comment`: Pulumi "Managed by Pulumi" vs TF "Managed by Terraform", tasks 3 and 316, both
languages).

**R-PU-15: `tagsAll` is written by pulumi-aws's Check.**
`applyTags` merges the provider's default tags into `tags` and sets `tagsAll` to the same merged map
(AWS `provider/tags.go` L25-L67). It is installed as `PreCheckCallback` on every resource that has
`tags_all` (AWS `provider/resources.go` L5657-L5676). `tags_all` is marked computed-only and deprecated
(L5699-L5707).

Adapter:
- `tagsAll` maps to TF `tags_all` in `planned_values` only, never in `configuration`;
- if the provider config has `defaultTags`, the Pulumi `tags` value already contains them, so it differs
  from TF `tags`.

*Pilot:* 8 resources have `tagsAll`, always equal to `tags`. No default tags were used.

**R-PU-16: JSON-valued strings must be compared semantically.**
The TF plan stores normalised JSON (e.g. IAM policies). Pulumi keeps whatever the program wrote. This is
pilot evidence only, not a cited rule.
*Pilot:* 17 leaves were equal only after parsing both sides as JSON.

**R-PU-17: TF sets are hash-ordered.**
Get the TF type from get-mapping (`provider.resources[tf][attr].type`, where 7 = set; BR
`pkg/tfshim/shim.go` L70-L82). Pulumi keeps program order, so set elements must be compared regardless of
order.
*Pilot:* 6 lists matched only after re-ordering (lex intent `sample_utterances` / `slot`, cloudfront
`geo_restriction.locations`).

## D. Dependencies and references

**R-PU-18: `propertyDependencies` = top-level Pulumi key → URNs. No attribute and no nested path.**
The RPC that registers a resource sends `dependencies` (a list of URNs) and `propertyDependencies` (a map
from property key to a list of URNs, `urns` only) (PU `proto/pulumi/resource.proto` L191-L212). These fields
are stored unchanged in `ResourceV3` (core.go L512-L513, L519-L520).

How the SDKs fill it:
- Node: one entry per top-level property whose value is not `undefined` (PU `sdk/nodejs/runtime/rpc.ts`
  L168-L205; `resource.ts` L153-L165, L1083-L1100).
- Python: properties that serialize to `None` are dropped, and the key is the camelCase Pulumi name
  translated from snake_case (PU `sdk/python/lib/pulumi/runtime/rpc.py` L204-L215, L243-L255).

Consequences:
- (a) The keys are the camelCase Pulumi names in both languages.
- (b) Constant properties are present with `[]`, so the key set is the program/SDK-written set used by P2.
- (c) The **attribute** of a reference is not recorded. For example, TF `aws_route53_zone.main.zone_id`
  arrives only as the zone's URN.

*Pilot:* across the control configurations of the 30 pilot tasks there are 132 references to resources. The
attribute is `id` in 66, `arn` in 25, `name` in 20, `endpoint` in 4, `zone_id` in 4, others 13. So guessing
`id` (P3id) is right for 50% of them. The attribute has to come from program text (P3src) or from matching
values.

**R-PU-19: `dependencies` = explicit `dependsOn` ∪ all property dependencies.**
Node: PU `sdk/nodejs/runtime/resource.ts` L1003-L1006, L1088-L1100. Python: PU
`sdk/python/lib/pulumi/runtime/resource.py` L276-L282. So TF `depends_on` =
`dependencies` minus the union of all `propertyDependencies` values.
*Pilot:* 4 resources (all task 90 Python) have such extra URNs. In TF they are explicit `depends_on`.

**R-PU-20: Data sources become invokes, so there is no step, URN or dependency for them.**
The converter turns every TF data resource into an `invoke(...)` call (CV `pkg/convert/tf.go`
L2496-L2540). The DOCS `content/docs/integrations/terraform/convert-hcl.md` L397-L405 example shows a data
source written as an invoke. An invoke result is a plain value: if it is known at preview time it looks like
a constant, and its `propertyDependencies` entry is `[]`. TF configuration instead has
`references: ["data.<type>.<name>…"]`.
*Pilot:* there are 18 references to data sources in the control configurations. One of them causes the
task 90 Python miss. This information can only be recovered from program text (invoke call sites).

**R-PU-21: A known value is not necessarily a constant.**
Values coming from other resources can be known during preview. Examples: autonames (R-PU-13), inputs
passed through, invoke results (R-PU-20). TF configuration uses `references` for any expression that
mentions a resource. Rule: never emit `constant_value` for a key whose `propertyDependencies` list is
non-empty.

## E. Identity, providers, resource names

**R-PU-22: URN parsing.**
Format: `urn:pulumi:<stack>::<project>::<qualified type>::<name>`, where the qualified type includes parent
types joined with `$` (PU `sdk/go/common/resource/urn.go` L35-L44). The resource token is the last
`$`-segment of the type part. The logical name is the part after the type.

**R-PU-23: Pairing Pulumi logical names with TF addresses.**
The converter keeps TF resource names as logical names. For counted resources, the code generator emits
`<base>-${range}` in TS and `f"<base>-{range}"` in Python. For components it adds a `${name}-` prefix
(PU `pkg/codegen/nodejs/gen_program.go` L1164-L1178; `pkg/codegen/python/gen_program.go` L1074-L1088).

Pairing order:
1. `(tf_type, name)`;
2. otherwise `<base>-<i>` → TF `<type>.<base>[i]`;
3. `for_each` keys follow the same rule (not seen in the pilot).

*Pilot:* 146 resources paired directly and 8 through the count suffix (task 428 `public-0` / `public-1`),
154 of 156 in total. Task 428 also shows why the type has to be part of the key: the route table is named
`public` and the subnets `public-<i>`. The 2 unpaired resources are non-AWS (`null:index/resource:Resource`
and `command:local:Command`, task 90 Python). They need the `null` / `command` provider mappings.

**R-PU-24: Type token ↔ TF type comes only from the mapping.**
Use get-mapping `resources[<tf>].tok`, or bridge-metadata `auto-aliasing.resources[<tf>].current`. Tokens
cannot be derived from strings. Examples:
- `aws_s3_bucket` → `aws:s3/bucketV2:BucketV2`, while `aws_s3_bucket_legacy` → `aws:s3/bucket:Bucket`;
- `aws_s3_bucket_cors_configuration` → `…/bucketCorsConfigurationV2:…V2`;
- `aws_alb` → `aws:alb/loadBalancer:LoadBalancer`.

*Checked:* in 6.72.0 the reverse map is a function (0 token collisions over 1,497 resources). The
bridge-metadata `current` token agrees with get-mapping for 1,497 of 1,497 resources. No `past` aliases are
recorded.

**R-PU-25: Provider references → `provider_config_key`.**
`newState.provider` (and `step.provider`) is `<provider URN>::<provider ID>` (PU
`sdk/go/common/providers/reference.go` L94-L101). During preview the ID is the unknown UUID (`UnknownID`,
L27-L32). Default providers are named `default_<major>_<minor>_<patch>` (PU
`pkg/resource/deploy/providers/provider.go` L101-L121), and a provider whose name starts with `default`
counts as a default provider (reference.go L48-L51).

Mapping: a default provider of package `<pkg>` → `provider_config_key` `"<pkg>"`. An explicit
`pulumi:providers:<pkg>` resource named `N` → `"<pkg>.N"` (adapter convention).

**Limit:** converter v1.4.0 drops every provider block that has an alias, with the warning that provider
aliases are not supported (CV `pkg/convert/tf.go` L4643-L4652). After conversion such resources use the
default provider, so `aws.<alias>` cannot be recovered from preview output.
*Pilot:* provider name segments are `default_6_72_0` ×154, `default_0_0_10` ×1 (null) and `default_1_2_1` ×1
(command). There are 0 explicit provider resources. This explains task 3, whose rule requires
`provider_config_key == "aws.main"`.

## F. TF ↔ Pulumi names and shapes

**R-PU-26: The authoritative mapping is `pulumi package get-mapping terraform aws@<ver>`.**
The bridge answers the keys `"tf"` and `"terraform"` with `MarshalProviderInfo` (BR
`pkg/tfbridge/provider.go` L1923-L1948). Command reference: DOCS
`content/docs/iac/cli/commands/pulumi_package_get-mapping.md` L11-L24. The JSON is `MarshallableProvider`
(BR `pkg/tfbridge/info/info.go` L1281-L1288):

- `provider.resources[tf][attr]`: TF schema (L941-L950): `type` (1 bool, 2 int, 3 float, 4 string, 5 list, 6 map, 7 set; BR `pkg/tfshim/shim.go` L70-L82), `optional`, `required`, `computed`, `maxItems`, and `element` = `{schema}` or `{resource}`.
- `resources[tf]` = `{tok, fields}` (L1212-L1219). `fields[attr]` holds **overrides only** (L1102-L1114): `name`, `maxItemsOne`, `element.fields` (nested blocks), `asset`, `default{autonamed,isFunc,value,envvars}` (L1170-L1174), `secret`.

All other names are computed with R-PU-27.

**R-PU-27: Forward naming algorithm (`terraformToPulumiName`). Reverse by inverting the forward map.**
Source: BR `pkg/tfbridge/names.go` L137-L232.
1. An override `name` wins (L147-L151).
2. List or set attributes are pluralized with `inflector.Pluralize` when they are not MaxItemsOne. MaxItemsOne
   here means the override if set, otherwise `maxItems != 1` (L153-L173). The plural is skipped if it
   collides with another attribute in the same object, unless that attribute was renamed (L175-L206).
3. snake_case → camelCase: an underscore (after the first non-underscore character) capitalises the next
   a–z letter; a trailing underscore is kept (L208-L231).
4. Apply recursively inside nested blocks, using `fields[attr].element.fields` as the nested overrides.

Pluralize: INF L106-L170 (rules plus irregulars), L68-L97 (uninflected words), L309-L311.

The bridge itself reverses names by iterating the TF schema through the forward function and inverting.
Its fallback only de-camelizes and **does not singularize** (names.go L30-L61; schema.go L1425-L1440). So
the adapter must never singularize heuristically.
*Checked:*
- Python port (`validate_reversal.py`) vs the real Pulumi package schema: 52,261 of 52,264 attribute names
  correct. The 3 misses are `definition` of three QuickSight resources, which the package schema omits.
- Pilot: 481 of 481 program-set top-level keys of the 154 paired resources (nested included) reversed with
  no unresolved name.
- A heuristic reversal (camel + `s`/`es`/`ies`, as in the 6 Oct prototype) disagrees on 23 of 115,455 names
  across all resources (9 wrong, 14 unresolved). Examples: `partition_index`→`partitionIndices`,
  `kinesis`→`kineses`, `x_axis`→`xAxes`, and `private_ip`/`private_ips` collisions. None of them occur in
  the pilot.

**R-PU-28: MaxItemsOne: flattened TF list/set blocks become one-element lists again.**
`IsMaxItemsOne` = list or set **and** (the override `maxItemsOne` if set, otherwise TF `maxItems == 1`) (BR
`pkg/tfbridge/schema.go` L1386-L1399). The bridge itself wraps a flattened value into a one-element list,
and turns null into `[]`, before calling Terraform (L358-L380).

Plugin-Framework single nested objects are a separate case. A shim `TypeMap` whose element is a resource is
always a Pulumi object (schema.go L71-L74, L525-L534). How the TF JSON plan represents it (object vs list)
was not checked here.

TF `maxItems` alone is **not** enough. In aws 6.72.0:
- 40 fields have TF MaxItems = 1 but stay lists in Pulumi (e.g. `aws_route53_record`
  `alias`/`weighted_routing_policy`/…, `aws_lambda_function.architectures`);
- 9 fields have MaxItems ≠ 1 but are flattened (e.g. `aws_eks_cluster.certificate_authority`).

*Checked:*
- Package schema: 13,486 of 13,486 blocks have the shape this rule predicts (direct `$ref` vs array).
- bridge-metadata `maxItemsOne` agrees with get-mapping in 47,371 of 47,371 field comparisons.
- Pilot: 58 wraps (e.g. `default_user_settings`, `vpc_config`, `root_block_device`,
  `default_cache_behavior/0/forwarded_values/0/cookies`), none with a value difference.
- Pilot: `weightedRoutingPolicies` (a list) maps to `weighted_routing_policy` (a list). Only the name
  changes, not the shape.

**R-PU-29: Map keys are user data and are never renamed.**
For a map-typed property the bridge keeps keys as they are (BR `pkg/tfbridge/schema.go` L564-L586, comment
at L572). Only schema attribute names follow R-PU-27.
*Pilot:* `tags: {"Name": …}` and `triggers` come through unchanged.

**R-PU-30: `bridge-metadata.json` is a build-time record, not a runtime contract.**
The bridge keeps decision history in a `bridge-metadata.json` blob in source control. It is described as
opaque and not meant for runtime use (BR `pkg/tfbridge/auto_aliasing.go` L119-L126; purpose L30-L53; keys
L111-L117; structs L127-L151). Contents:
- `auto-aliasing.{resources,datasources}[tf] = {current, past[{name,inCodegen,majorVersion}], majorVersion, fields{tf_field:{maxItemsOne, elem{fields}}}}`;
- `auto-settings` (`maxItemsOneOverrides` paths with `$` for list elements, `aliases`, `renames`);
- `mux` (token → which sub-provider serves it).

It has no Pulumi property names and only lists list or set fields. Use it as a cross-check or fallback for
tokens and MaxItemsOne. Use get-mapping for names.
*Local copy:* 1,497 resources, 601 data sources.

**R-PU-31: Version alignment.**
pulumi-aws 6.72.0 = bridge v3.104.0 + upstream TF provider v5.90.1 (AWS `provider/go.mod` L19-L21; `../upstream`
replace at L35; submodule SHA as in §0). The control TF plans use 5.90.0. Schema drift is expected to be
negligible, but differences in an attribute set should be checked against `terraform providers schema -json`
of 5.90.0. This was not done here.

## G. Limits of preview output (not fixable by the adapter)

**R-PU-32: The preview cannot see some things.**
- Resources created inside an `apply` whose input is unknown are missing from the preview (DOCS update-plans.md L50-L55).
- Explicit providers with unknown config get no full check, so their resources have no defaults or normalisation (L57-L60).
- Converter artefacts pass through unchanged. *Pilot:* doubly-escaped JSON strings in converted TypeScript: task 86 `document` (the remaining value difference) and task 156 `eventPattern` (which made that preview fail).

**R-PU-33: Alternative input: the saved plan from `pulumi preview --save-plan`.**
Format: PU `sdk/go/common/apitype/plan.go` L25-L103. `resourcePlans[urn].goal` holds `type`, `name`,
`custom`, `inputDiff.adds`, `parent`, `dependencies`, `provider`, `propertyDependencies`, … It also has
`steps`, an advisory `state` (proposed outputs) and a `seed`. The format is experimental and may change
(DOCS update-plans.md L70-L72). Unknowns use the same UUID (L184-L189). With `--show-secrets` the plan file
contains plaintext secrets (preview.go L707-L710). This is the only Pulumi artefact that could carry secrets
(R-PU-10) and preview-time outputs. It was not used in the pilot.

---

## H. What this means for the adapter variants (all derived from the rules above)

- **P1** (planned_values + resource_changes) needs R-PU-6/7/9/11/12/13/15/17/22-24/26-29.
  - Program-set values plus defaults match TF on the pilot. On 154 paired resources: 487 equal leaves,
    17 JSON-equal, 6 set re-orderings, 99 unknowns all consistent.
  - Remaining issues: 5 value differences (4× R-PU-14 SDK defaults, 1× R-PU-32 converter escaping) and
    13 granularity cases (11× TF sets with an unknown element, R-PU-9; 2× autoname propagation, R-PU-13/21).
- **P2** (+ `configuration.constant_value`) also needs R-PU-8/10/12/14/18 for the program-set key set and
  R-PU-21 so that derived values do not become constants.
- **P3id / P3src** (+ `references`) rely on R-PU-18/19/20.
  - `propertyDependencies` gives target URNs only. The attribute is `id` in 50% of the control references.
  - Data-source references (R-PU-20) are invisible in the preview.
  - Provider aliases (R-PU-25) are gone after conversion.
  - These two match the two known misses: Python task 90 and task 3.

## I. Notes on the deleted 6 Oct prototype

Taken from the recovered `iv-study/E-prototype/iv_adapter_proto.py` (the same code as in the LLM agent
transcript it was recovered from; neither is included in this repository). These were read, not re-run.
- Reverse names used candidates `camel`, `+s`, `+es`, `y→ies` (its L121-L136, candidates at L132), with a `snake()` fallback (L138-L139). R-PU-27 measures that heuristic as 23 of 115,455 names off; none in the pilot.
- Token fallback built `<pkg>_<snake(name)>` when the token was missing from the mapping (L87-L94). R-PU-24 says to use the mapping only.
- Autonames were detected only by `default.autonamed` (L157-L158). R-PU-13 adds `isFunc` defaults (the RDS `identifier` of task 408).
- MaxItemsOne came from bridge-metadata (L160-L161). It agrees with get-mapping on every field checked (R-PU-28/30).
