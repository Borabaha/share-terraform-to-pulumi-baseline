"""Export the official Terraform-Pulumi mappings (R-PU-24/26) for the non-aws bridged packages that the converted
programs use.

`pulumi package get-mapping terraform <pkg>@<ver>` reads the static mapping from the locally installed provider
plugin. It needs no stack, no state and no cloud access. Automatic plugin download is turned off, so only plugins that
are already installed are used.
The aws@6.72.0 mapping is not rebuilt here. The adapter reads tables/aws-6.72.0-terraform-mapping.json, which was made
once, outside this script, with `pulumi package get-mapping terraform aws@6.72.0`.
"""
import os, subprocess

PULUMI = 'C:/Program Files (x86)/Pulumi/pulumi.exe'
HERE = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
PKGS = ['null@0.0.10', 'random@4.18.0', 'archive@0.3.2']   # versions installed in ~/.pulumi/plugins (the pilot used null 0.0.10)

env = dict(os.environ, PULUMI_DISABLE_AUTOMATIC_PLUGIN_ACQUISITION='true', PULUMI_SKIP_UPDATE_CHECK='true',
           PULUMI_CONFIG_PASSPHRASE='thesis-local')
for src in PKGS:
    out = f"{HERE}/{src.replace('@', '-')}-terraform-mapping.json"
    p = subprocess.run([PULUMI, 'package', 'get-mapping', 'terraform', src, '--out', out, '--non-interactive'],
                       env=env, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600, cwd=HERE)
    print(src, 'rc', p.returncode, (p.stderr or '')[-400:].strip(), os.path.getsize(out) if os.path.exists(out) else 'missing')
