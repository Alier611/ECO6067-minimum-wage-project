"""Independently retrieve the author's archive and compare it with course data.

Optional network step; not required on every reproducibility run.
Archive and restaurant-level source files remain excluded from Git.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import urllib.request
import zipfile

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
SOURCE = 'https://davidcard.berkeley.edu/data_sets/njmin.zip'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive', type=Path, help='Use an already downloaded archive instead of downloading.')
    args = p.parse_args()
    if args.archive:
        data = args.archive.read_bytes()
    else:
        with urllib.request.urlopen(SOURCE, timeout=30) as response:
            data = response.read(2_000_000)
        destination = ROOT / 'data/raw/author_njmin.zip'
        destination.write_bytes(data)
    course = pd.read_csv(ROOT / 'data/raw/public.csv')
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        original = archive.read('public.dat')
        author = pd.read_csv(io.BytesIO(original), sep=r'\s+', header=None, na_values='.')
        program = archive.read('check.sas')
        sas = program.decode('latin1')
        files = archive.namelist()
    equal = author.shape == course.shape and np.array_equal(author.to_numpy(float), course.to_numpy(float), equal_nan=True)
    if not equal:
        raise ValueError('Author and course values differ. Investigate rather than overwrite course data.')
    statement = 'MODEL DEMP=GAP BK KFC ROYS CENTRALJ SOUTHJ PA1 PA2;'
    if statement not in sas:
        raise ValueError('Expected author model statement changed; inspect the source.')
    report = {
        'source_page':'https://davidcard.berkeley.edu/data_sets.html',
        'readme_url':'https://davidcard.berkeley.edu/readme/njmin-readme.txt',
        'archive_url':SOURCE,
        'archive_sha256':hashlib.sha256(data).hexdigest(),
        'public_dat_sha256':hashlib.sha256(original).hexdigest(),
        'check_sas_sha256':hashlib.sha256(program).hexdigest(),
        'archive_members':files, 'rows':len(author), 'columns':len(author.columns),
        'all_numeric_values_and_missing_positions_equal':bool(equal),
        'comparison_method':'Read original ASCII whitespace-delimited data, parse dots as missing, compare 46 columns in source order; no rounding or tolerance.',
        'author_program_model_v_statement':statement,
        'author_program_note':'This check.sas statement excludes CO_OWNED; the published Table 4 indicates chain and ownership controls.',
        'source_scope':'Author README describes book chapter 2 survey files and a checking program; not claimed to be the exact historical publication-production program.'
    }
    path = ROOT / 'results/author_source_verification.json'
    path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('Independent author-data verification passed: 410 x 46 values and missing positions identical.')


if __name__ == '__main__':
    main()
