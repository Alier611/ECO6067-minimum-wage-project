# Data sources and access

Input: `data/raw/public.csv`, the course attachment supplied by the student.
Supporting documents: the uploaded course README and DATA_DICTIONARY.
Dataset: 410 restaurant observations, 46 columns; 331 NJ, 79 PA.
Package described by the course: `01_DID.zip`.
The exact input SHA-256 is recorded automatically in `results/provenance.json`.

Use the original filename and preserve its bytes. Obtain it from the course
download or the existing attachment, then copy it to the input path above.
Originally the project used only the course input. In the core-replication stage
the author archive was independently downloaded and numerically compared.
Source page: https://davidcard.berkeley.edu/data_sets.html
README: https://davidcard.berkeley.edu/readme/njmin-readme.txt
Archive: https://davidcard.berkeley.edu/data_sets/njmin.zip
Retrieval session date (Hong Kong): 2026-10-09.
Actual archive members: check.sas, codebook, public.dat, read.me, survey1.nj,
survey2.nj. SHA-256 values and exact 410x46 equality evidence are recorded in
results/author_source_verification.json. Optional retrieval/comparison code:
verify_author_data.py. No values or missing positions differed from course data.
Public access alone is not treated as a verified redistribution license.
The student confirmed that the processed CSV may be uploaded and manually
published data/processed/analysis.csv. Raw course data remain excluded from Git.
For raw-input reproduction, the teaching team obtains public.csv from the
course 01_DID.zip and places it at data/raw/public.csv. Use its original bytes
for the stored input SHA-256 and exact repeat-run check. The repository includes
the final processed data, full code and source-access instructions.

Repository: https://github.com/Alier611/ECO6067-minimum-wage-project
Publication and processed-data push were confirmed by the student's terminal
and repository screenshots on 10 October 2026. They do not constitute a new
independent raw-data comparison; that completed comparison is recorded above.

Paper reference: Card and Krueger (1994), AER 84(4), pp. 772-793.
FTE and closure rules: p. 775 and Table 3 notes, p. 780.
Regression sample and wage-gap construction: pp. 779-781 and Table 4, p. 780.
Printed p. 780 is PDF page 9 in the supplied file, not PDF page 780.

The public check.sas program explicitly retains permanently closed stores when
second-period wages are unavailable. Its region-adjusted level-change model
excludes CO_OWNED, unlike the printed Table 4 ownership-control label. The project
preserves both model specifications. The author README describes a book-related
checking program; it does not prove this was the exact 1994 final table program.
No third-party replication output is used as a benchmark.
