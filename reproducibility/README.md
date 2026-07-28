# Reproducibility

## Contents

- `source.zip` contains the Python generators and independent verification
  programs in their original flat layout.
- `certificates.zip` contains the retained JSON and CSV proof objects.
- Each archive contains a `MANIFEST.sha256` file covering every other member.
- `archives.sha256` records the hashes of both archives.
- `verify.py` is the single entry point for integrity checks and replay.

The verifier extracts the two archives into an isolated temporary directory,
adds the manuscript source, and runs the selected checks there. It does not
modify the repository.

## Modes

### Integrity

```bash
python reproducibility/verify.py
```

Checks the manuscript hashes, archive hashes, member lists, and every archived
member hash. No third-party package is required.

### Fast checks

```bash
python reproducibility/verify.py --fast
```

In addition to integrity verification, runs the final manuscript/data
consistency checks and the complete quartic bundle verifier against the
retained certificates.

Expected quartic summary:

- 6,977 minimal polynomials;
- 6,982 target roots;
- 62,838 finite root–exponent pairs;
- maximum obstruction block 110;
- no failed tail or prefix certificate.

### Complete regeneration

```bash
python -m pip install -r reproducibility/requirements.txt
python reproducibility/verify.py --full
```

This regenerates the cubic and quartic catalogs and their principal exact
objects, replays the independent FLINT/Arb audits, and recompiles the
manuscript. It is computationally expensive.

## Retained environment

- Python 3.13.7
- python-flint 0.9.0
- NumPy 2.5.1
- SciPy 1.18.0
- SymPy 1.14.0
- Tectonic 0.16.9
