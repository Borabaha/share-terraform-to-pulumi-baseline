"""R-PU-14 table: defaults that exist only on the Pulumi side (bridge overlay `default.value` in get-mapping, which the
generated SDK also applies through the package schema `default`), together with the value Terraform itself would plan.

Pulumi side (read-only inputs):
  * get-mapping fields[...].default.value (aws-6.72.0-terraform-mapping.json in this folder)
  * package schema inputProperties[...].default and types[...].properties[...].default
    (aws-6.72.0-schema.json in this folder; not included because it is 35 MB, made with
    `pulumi package get-schema aws@6.72.0`)
  Both sources must list exactly the same fields; main() compares their counts.
Terraform side: the schema `Default:` of the same attribute in hashicorp/terraform-provider-aws v5.90.0, the provider
version behind the plans in the original package (tfplan.json). The values were looked up in the raw source files at
https://raw.githubusercontent.com/hashicorp/terraform-provider-aws/v5.90.0/internal/service/<file> (line numbers in
TF_DEFAULTS). `terraform providers schema -json` does not export defaults, so they are cited from the source.
Output: pulumi_only_defaults.json
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
MAPPING = HERE + '/aws-6.72.0-terraform-mapping.json'
PKG_SCHEMA = HERE + '/aws-6.72.0-schema.json'
GH = 'https://github.com/hashicorp/terraform-provider-aws/blob/v5.90.0/internal/service/'

# (tf_type, TF attribute path) -> (Terraform default, source file#lines)
TF_DEFAULTS = {
    ('aws_api_gateway_api_key', 'description'): ('Managed by Terraform', 'apigateway/api_key.go#L54-L57'),
    ('aws_appsync_api_key', 'description'): ('Managed by Terraform', 'appsync/api_key.go#L49-L52'),
    ('aws_db_option_group', 'option_group_description'): ('Managed by Terraform', 'rds/option_group.go#L125-L129'),
    ('aws_db_parameter_group', 'description'): ('Managed by Terraform', 'rds/parameter_group.go#L51-L55'),
    ('aws_db_parameter_group', 'parameter/apply_method'): ('immediate', 'rds/parameter_group.go#L83-L86 (types.ApplyMethodImmediate)'),
    ('aws_db_subnet_group', 'description'): ('Managed by Terraform', 'rds/subnet_group.go#L47-L50'),
    ('aws_docdb_subnet_group', 'description'): ('Managed by Terraform', 'docdb/subnet_group.go#L45-L48'),
    ('aws_elasticache_parameter_group', 'description'): ('Managed by Terraform', 'elasticache/parameter_group.go#L47-L51'),
    ('aws_elasticache_subnet_group', 'description'): ('Managed by Terraform', 'elasticache/subnet_group.go#L46-L49'),
    ('aws_media_package_channel', 'description'): ('Managed by Terraform', 'mediapackage/channel.go#L50-L53'),
    ('aws_neptune_subnet_group', 'description'): ('Managed by Terraform', 'neptune/subnet_group.go#L44-L47'),
    ('aws_rds_cluster_parameter_group', 'description'): ('Managed by Terraform', 'rds/cluster_parameter_group.go#L49-L53'),
    ('aws_redshift_parameter_group', 'description'): ('Managed by Terraform', 'redshift/parameter_group.go#L49-L53'),
    ('aws_redshift_subnet_group', 'description'): ('Managed by Terraform', 'redshift/subnet_group.go#L45-L48'),
    ('aws_route53_zone', 'comment'): ('Managed by Terraform', 'route53/zone.go#L50-L53'),
    ('aws_security_group', 'description'): ('Managed by Terraform', 'ec2/vpc_security_group.go#L68-L72'),
}


def main():
    m = json.load(open(MAPPING, encoding='utf-8'))
    found = {}

    def walk(tf, fields, path):
        for a, f in (fields or {}).items():
            d = f.get('default') or {}
            if 'value' in d:
                found[(tf, '/'.join(path + [a]))] = d['value']
            walk(tf, (f.get('element') or {}).get('fields') or f.get('fields'), path + [a])
    for tf, r in m['resources'].items():
        walk(tf, r.get('fields'), [])
    # cross-check against the package schema (R-PU-14)
    s = json.load(open(PKG_SCHEMA, encoding='utf-8'))
    pkg_defaults = sorted([(tok, p, ps['default']) for tok, r in s['resources'].items()
                           for p, ps in (r.get('inputProperties') or {}).items() if 'default' in ps] +
                          [(tok, p, ps['default']) for tok, t in s.get('types', {}).items()
                           for p, ps in (t.get('properties') or {}).items() if 'default' in ps])
    assert len(pkg_defaults) == len(found) == len(TF_DEFAULTS), (len(pkg_defaults), len(found), len(TF_DEFAULTS))
    assert set(found) == set(TF_DEFAULTS), set(found) ^ set(TF_DEFAULTS)
    rows = []
    for (tf, path), pv in sorted(found.items()):
        tv, src = TF_DEFAULTS[(tf, path)]
        rows.append({'tf_type': tf, 'path': path.split('/'), 'pulumi_default': pv, 'tf_default': tv,
                     'tf_source': GH + src})
    json.dump({'_doc': __doc__.strip().splitlines()[0], 'entries': rows,
               'package_schema_defaults': pkg_defaults}, open(HERE + '/pulumi_only_defaults.json', 'w', encoding='utf-8'),
              indent=1)
    print(len(rows), 'entries;', sum(r['pulumi_default'] != r['tf_default'] for r in rows), 'differ from Terraform')


if __name__ == '__main__':
    main()
