"""Rebuild into empty folders and compare preparation, core tables and extension."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    raw = ROOT / 'data/raw/public.csv'
    before = sha(raw)
    with tempfile.TemporaryDirectory(prefix='eco6067_repeat_') as d:
        folder = Path(d)
        out, processed = folder / 'results', folder / 'processed'
        subprocess.run([sys.executable, str(ROOT / 'run_project.py'), '--stage', 'extend',
                        '--input', str(raw), '--output-dir', str(out),
                        '--processed-dir', str(processed)], check=True)
        comparisons = {}
        for path in sorted(out.iterdir()):
            original = ROOT / 'results' / path.name
            comparisons['results/' + path.name] = original.is_file() and sha(original) == sha(path)
        comparisons['data/processed/analysis.csv'] = sha(ROOT / 'data/processed/analysis.csv') == sha(processed / 'analysis.csv')
        report_out = folder / 'report'
        subprocess.run([sys.executable, str(ROOT / 'build_report.py'), '--results', str(out),
                        '--output', str(report_out)], check=True)
        for path in sorted(report_out.iterdir()):
            original = ROOT / 'report' / path.name
            comparisons['report/' + path.name] = original.is_file() and sha(original) == sha(path)
        if not all(comparisons.values()):
            raise RuntimeError('Repeat run differs: ' + ', '.join(k for k, v in comparisons.items() if not v))
        missing = subprocess.run([sys.executable, str(ROOT / 'run_project.py'), '--input', str(folder / 'absent.csv')], capture_output=True, text=True)
        error_check = missing.returncode != 0 and 'Missing public.csv' in missing.stderr
        if not error_check:
            raise RuntimeError('Missing-input guidance check failed.')
    if sha(raw) != before:
        raise RuntimeError('Original input changed.')
    report = {'fresh_output_directory': True, 'file_hash_comparisons': comparisons,
              'raw_sha256_unchanged': True, 'missing_input_message_verified': True,
              'scope': 'Preparation, full Table 3 / Table 4 outputs, prespecified ownership extension, and regenerated PDF/Markdown report.'}
    (ROOT / 'results/reproducibility_check.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'Reproducibility check passed: {len(comparisons)} files identical; raw input unchanged.')


if __name__ == '__main__':
    main()
