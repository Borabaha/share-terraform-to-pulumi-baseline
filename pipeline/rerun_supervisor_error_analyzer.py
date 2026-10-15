"""Runs the error analyzer from the original code (iac_research/analysis/error_analyzer.py) again on the original
experiment outputs and compares the result with the report saved in the original package. The package is not
changed; the output goes to pipeline/runs/error-analyzer-check/.

matplotlib and seaborn are not installed here and are only used for the charts, so mock modules stand in for them.
The classification and the statistics come from the original code unchanged.

Usage: python rerun_supervisor_error_analyzer.py [experiment_name]   (default: initial_4o_Baseline)
"""
import difflib, os, sys
from unittest import mock

LAB = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(LAB, '..', 'original-package', 'iac-research-without-agent')
sys.path.insert(0, PKG)
for m in ('matplotlib', 'matplotlib.pyplot', 'seaborn'):
    sys.modules[m] = mock.MagicMock()
from iac_research.analysis.error_analyzer import IaCErrorAnalyzer  # noqa: E402

exp = sys.argv[1] if len(sys.argv) > 1 else 'initial_4o_Baseline'
run = os.path.join(PKG, 'validation', 'runs', exp)
out = os.path.join(LAB, 'runs', 'error-analyzer-check', exp)
os.makedirs(out, exist_ok=True)

# The Baseline run keeps its results in val_results/ and its report in multi_error_analysis_results/val/;
# the other runs use init_results/ and error_analysis_results/.
res = 'val_results' if os.path.isdir(os.path.join(run, 'val_results')) else 'init_results'
rep = next(p for p in (os.path.join(run, 'multi_error_analysis_results', 'val', 'error_analysis_report.md'),
                       os.path.join(run, 'error_analysis_results', 'error_analysis_report.md')) if os.path.exists(p))
a = IaCErrorAnalyzer(os.path.join(run, res, 'terraform_results.csv'), os.path.join(run, res, 'opa_results.csv'))
a.load_data(); a.merge_results(); a.classify_errors()
a.generate_error_report(out)

ours = open(os.path.join(out, 'error_analysis_report.md'), encoding='utf-8').read().splitlines()
theirs = open(rep, encoding='utf-8').read().splitlines()
diff = list(difflib.unified_diff(theirs, ours, "supervisors' report", 'our reproduction', lineterm='', n=0))
print(f'{exp}: report lines {len(ours)} | differing lines {sum(1 for d in diff if d[:1] in "+-" and d[:3] not in ("+++", "---"))}')
print('\n'.join(diff[:40]) if diff else 'REPORTS IDENTICAL')
