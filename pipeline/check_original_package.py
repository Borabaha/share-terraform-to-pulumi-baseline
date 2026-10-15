"""Checks that original-package/ is an unchanged copy of the Zenodo release.

original-package/ holds only the part of the original replication package that the scripts here use: the dataset
and tracking files (ground_truth/), the pass function (iac_research/validation/analyzer.py), the error analyzer
(iac_research/analysis/), the six experiment results it reads (validation/runs/), and the LICENSE and README.
Every file is compared byte for byte with the same file in the Zenodo zip, and nothing in original-package/ may be
missing from the zip.

Usage: python check_original_package.py <path to iac-research-code-replication-package.zip>
       (Zenodo DOI 10.5281/zenodo.20272829, MD5 0a0568f4c9906dc8c46a1f8241a5af61)
"""
import hashlib, os, sys, zipfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LOCAL = os.path.join(REPO, 'original-package')

zip_path = sys.argv[1]
print('zip MD5:', hashlib.md5(open(zip_path, 'rb').read()).hexdigest())
z = zipfile.ZipFile(zip_path)
in_zip = {i.filename: i for i in z.infolist() if not i.is_dir()}

same, differ, not_in_zip = 0, [], []
for d, _, files in os.walk(LOCAL):
    for f in files:
        rel = os.path.relpath(os.path.join(d, f), LOCAL).replace(os.sep, '/')
        if rel not in in_zip:
            not_in_zip.append(rel)
        elif open(os.path.join(d, f), 'rb').read() == z.read(in_zip[rel]):
            same += 1
        else:
            differ.append(rel)

print(f'identical to the zip: {same} files')
print(f'different from the zip: {len(differ)}', *differ[:20], sep='\n  ')
print(f'not in the zip: {len(not_in_zip)}', *not_in_zip[:20], sep='\n  ')
sys.exit(1 if differ or not_in_zip else 0)
