# Trinomial factors of Newman polynomials

This repository accompanies the manuscript
*Coefficient Propagation and Conjugate Obstructions for Trinomial Factors of
Newman Polynomials*.

## Why this project, and my role

I wanted to test whether an AI research workflow could produce a mathematical result that other people could inspect and reproduce.

I initiated the project, supplied the objective, supervised the workflow and selected the retained outputs. AI Researcher and Critic roles produced the exploration, proofs, computation, verification code and manuscript. I did not independently derive every result.

The contribution is the restricted result below and its reproducible evidence, together with a documented account of how it was produced. It is not a solution to the full conjecture or a claim of external peer review. [Workflow and responsibility](docs/autonomous-research-workflow.md).

## Main result

Consider a normalized factorization of a Newman polynomial into monic
polynomials with nonnegative real coefficients, with one factor of the form

$$
1+a x^2+x^v,
$$

where $v\ge 5$ is odd. The manuscript proves that a genuinely fractional
coefficient $a$ cannot have algebraic degree two, three, or four. Therefore,
within this family, every genuinely fractional $a$ has algebraic degree at
least five.

This is a result for a specific trinomial family. It does not settle the full
unfair $0$-$1$ polynomial conjecture.

## Repository structure

| Path | Contents |
| --- | --- |
| `paper/manuscript.pdf` | Typeset manuscript |
| `paper/manuscript.tex` | LaTeX source |
| `docs/literature.md` | Literature context and novelty boundary |
| `docs/autonomous-research-workflow.md` | AI roles, prompt, schedule, version chronology, and retained timing |
| `reproducibility/source.zip` | Computation and verification source code |
| `reproducibility/certificates.zip` | Exact retained certificates |
| `reproducibility/verify.py` | Unified integrity and reproduction entry point |

The large collection of machine-generated certificates is compressed into a
single archive so that the repository remains easy to navigate. Both archives
contain their own SHA-256 manifests.

## Verification

Integrity verification uses only the Python standard library:

```bash
python reproducibility/verify.py
```

The fast mathematical checks use the retained exact certificates:

```bash
python reproducibility/verify.py --fast
```

The complete regeneration is substantially more expensive and additionally
requires `python-flint` and Tectonic:

```bash
python -m pip install -r reproducibility/requirements.txt
python reproducibility/verify.py --full
```

See [reproducibility/README.md](reproducibility/README.md) for the expected
counts and computational architecture.

## Computational summary

The quartic computation retains 6,977 irreducible minimal polynomials and
6,982 target roots. It verifies 62,838 finite root–exponent pairs, 6,982
uniform negative-tail certificates, and 99,340 positive-prefix blocks. The
maximum obstruction block is 110.

## License

The verification software and source code are available under the MIT
License. The manuscript, documentation, computational data, and certificates
are available under the Creative Commons Attribution 4.0 International
License. See [LICENSE](LICENSE) for the exact scope and attribution details.
