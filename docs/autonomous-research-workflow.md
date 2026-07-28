# Autonomous AI research workflow

This document records how the accompanying manuscript was produced.

## Responsibility and authorship

The human orchestrator initiated the project, supplied the research objective,
configured and supervised the workflow, selected retained outputs, and
authorized release. An autonomous AI Researcher–Critic workflow produced the
mathematical exploration, proof development, computation, verification code,
internal criticism, and manuscript prose. The labels “Researcher” and
“Critic” refer to AI roles rather than additional authors.

The human orchestrator did not independently derive every proof or
calculation. The repository is therefore designed to expose the mathematical
output to direct inspection through source code, exact certificates, hashes,
and reproducible checks.

## Operating model

The project maintained three coordination records:

- a JSON state file holding the phase, lock, current manuscript, hashes,
  feedback state, and last-run metrics;
- a Critic feedback document;
- a version summary and cycle log.

At each scheduled invocation, a single worker read those records and selected
exactly one role from the persisted phase. It never performed both Researcher
and Critic work in the same invocation.

The Researcher explored proofs, repaired Critic findings, searched for
counterexamples, performed exact computation and literature checks, drafted
the paper, and created a new version only after material progress. The Critic
reviewed the exact source and PDF hashes, checked the logical chain, replayed
computations, searched for counterexamples and edge cases, assessed novelty
and exposition, and returned structured feedback without editing the
manuscript.

Before a role could start, referenced files had to exist, be nonempty, and
match their recorded SHA-256 hashes. Completed PDFs had to be compiled from
the retained source, contain selectable vector text, and pass visual
inspection. Failures, duplicate inputs, stale locks, and no-progress runs were
recorded without being described as mathematical advances.

## Schedule

The research artifacts span 10–28 July 2026.

From 17 July onward, the stable schedule was:

| Item | Setting |
| --- | --- |
| Worker cadence | one invocation every 6 hours |
| Roles per invocation | at most one |
| Researcher minimum | 300 active minutes |
| Critic minimum | 60 active minutes |
| Researcher stale-lock threshold | 7 hours |
| Critic stale-lock threshold | 2 hours |
| Successful handoff | stop immediately after the state transition |

The phase, not the wall-clock slot, selected the role. A recent consistent
active lock caused an immediate no-change stop. A stale or inconsistent lock
was recovered, logged, and then processed in the corresponding role.

## Stable automation prompt

The following is the public form of the stable state-aware prompt. Local
absolute paths and the workstation username are replaced by repository-neutral
placeholders; the operational instructions are otherwise retained.

> You are the single scheduled worker for a two-role MathResearch cycle. The
> only roles are Researcher and Critic. Work only in `[PROJECT_ROOT]`.
>
> Coordination files:
>
> - State: `[PROJECT_ROOT]/.codex/researcher-critic-cycle.json`
> - Critic feedback: `[PROJECT_ROOT]/.codex/critic-feedback.md`
> - Project summary and cycle log: `[PROJECT_ROOT]/VersionSummary.md`
>
> At each scheduled invocation, inspect the state and perform at most one
> complete role iteration. Never perform both roles in the same invocation.

### Shared dispatch and safety prompt

> 1. Read and parse the state, feedback, and project summary before changing
> anything. If the state is unreadable, report the exact blocking error and
> stop without changing research artifacts.
> 2. Select the role only from `phase`. A recent consistent running lock has
> priority. Recover stale or inconsistent Researcher and Critic locks after
> seven and two hours, respectively, and record the exact recovery. Never
> guess a role from an invalid phase.
> 3. Before claiming a role, validate every referenced source, PDF,
> computation artifact, feedback file, and retained review by existence,
> non-emptiness, modification time, and SHA-256 hash. A rename or
> byte-identical copy is not new.
> 4. Claim the selected role atomically by setting the phase to its running
> state, recording the active role and UTC start time, and clearing obsolete
> errors. Do not change manuscript or review metadata at claim time.
> 5. Begin the minimum duration only after a successful claim. Researcher must
> perform at least 300 active minutes and Critic at least 60 active minutes.
> Do not sleep, poll, or idle to fill the interval. Record role, start,
> completion, elapsed minutes, outcome, and input/output versions before
> handoff.
> 6. Update the cycle log on every invocation except an immediate
> recent-lock stop. Do not invent progress for no-op, recovery, validation
> failure, duplicate, or no-progress runs.
> 7. After a successful handoff, stop. Do not begin the role named by the new
> phase in the same invocation.

### Researcher prompt

> 1. Address every substantive pending Critic criticism. Distinguish repaired
> issues, open issues, and suggestions not adopted. Do not mark feedback
> addressed until the manuscript is materially improved.
> 2. Continue serious work on the conjecture for at least five active hours:
> seek rigorous proofs, repair gaps, explore genuinely new proof angles and
> relevant theorems, run exact and reproducible computations where useful,
> and perform responsible novelty and literature checks. Do not merely
> reformat, rename, or restate the manuscript.
> 3. A material iteration must create exactly one incremented version
> containing a nonempty primary source, a nonempty PDF compiled directly from
> that source, and all scripts and data needed to reproduce computations.
> Never overwrite, delete, or rename earlier artifacts. Rasterized page-image
> PDFs are forbidden. Render and visually inspect the selectable-text vector
> PDF at high zoom.
> 4. Recompute SHA-256 hashes and modification times for the new PDF, source,
> and computation artifacts. Confirm that the source and PDF are genuinely
> new and the version increased by exactly one.
> 5. If the minimum time was spent without material progress, retain all prior
> files, restore the idle Researcher phase, record the attempt precisely, and
> stop without handoff.
> 6. For a genuine new version, atomically publish exact paths, hashes,
> modification times, computation artifacts, and a material-change summary;
> mark addressed feedback honestly; hand off to Critic; clear the lock; and
> stop.

### Critic prompt

> 1. Before claiming Critic, compare the current PDF and source hashes with the
> last reviewed manuscript. If the manuscript is not genuinely new, return
> control to Researcher, record the duplicate reason, and stop without
> starting the review clock.
> 2. Perform at least 60 active minutes of rigorous independent review. Verify
> every theorem, lemma, proof transition, computation, table, and claimed
> implication. Replay relevant exact computations, search for
> counterexamples and edge cases, and check internal consistency, exposition,
> novelty, and relevant literature. Distinguish fatal errors, major gaps,
> minor corrections, and verified strengths. Give exact corrections and
> prioritized next steps. Do not modify the manuscript or perform Researcher
> work.
> 3. Produce a nonempty selectable-text vector review PDF for the exact
> manuscript version. State the reviewed version and PDF/source SHA-256
> hashes, and cover problems, proposed repairs, prioritized next steps,
> verified strengths, novelty, and publication readiness. Never overwrite an
> earlier review. Render and visually inspect the PDF at high zoom.
> 4. Replace the feedback document with the complete new review and exact
> source, manuscript, feedback, and review hashes.
> 5. Atomically record the reviewed manuscript, set feedback to pending for
> the Researcher, return the phase to Researcher, clear the lock, record exact
> completion metrics, and stop.

### Failure prompt

> If any failure occurs after a role is claimed, restore that role’s idle
> phase, clear the active-role lock, record the exact failure and honest
> partial elapsed time, add a concise cycle-log entry when possible, and stop.
> Never publish a partial manuscript or partial review handoff as complete.

## Human prompts and intervention

The human orchestrator supplied the conjecture and repeatedly requested
substantive continuation, final verification, concise release preparation,
and an explicit last Critic cycle. Human interventions also stopped optional
long computations when local compute was limited. Those stops were treated as
scope decisions: incomplete optional calculations were excluded rather than
reported as completed evidence.

This document publishes the stable research-control prompt with
workstation-specific paths replaced by repository-neutral placeholders.

## Version chronology

The workflow produced 18 numbered internal manuscript iterations. The public
paper is intentionally unnumbered.

| Internal iteration | Main development |
| --- | --- |
| 1 | Local coefficient obstructions, half-bias restriction, integrality and norm-divisor strategy |
| 2 | Conjugate bounds and uniform quadratic exclusion for the smaller gap two |
| 3 | First bounded cubic computational pipeline |
| 4 | Analytic repair and honest separation of theorem from numerical evidence |
| 5 | Exact Sturm/Schur catalog and independently replayed feasibility systems |
| 6 | Exact endpoint separation and stronger independent audit |
| 7 | Case-dependent conjugate cutoffs and mostly portable Farkas certificates |
| 8 | Portable integer contradictions for every retained bounded cubic system |
| 9 | Repair of the nonnegative-factorization scope and an exact counterexample to ordinary divisibility |
| 10 | Bounded cubic extension from product degree 66 to 69 |
| 11 | Bounded cubic extension to product degree 75 |
| 12 | Removal of the product-degree cap for the smaller-gap-two cubic case |
| 13 | First predecessor safe-lattice theorem and large modular stress audit |
| 14 | Three-block predecessor safe-lattice extension |
| 15 | Four- and five-block safe-lattice extensions |
| 16 | Six-block safe-lattice extension and expanded exact audit chain |
| 17 | Uniform quartic exclusion, giving algebraic degree at least five in the stated family |
| 18 | Final audit, consistency, packaging, and release hardening without a broader theorem |

The mathematical result in the released paper is the culmination of this
sequence; the internal iteration number is not part of the title or theorem
statement.

## Retained time accounting

The surviving late-stage ledger records 40.68 hours of Researcher and Critic
workflow time, including unsuccessful and repeated handoff attempts.

The final production-and-review pair is recorded exactly:

| Role | Retained elapsed time |
| --- | ---: |
| Final Researcher production and release audit | 358.38 minutes |
| Final Critic review and release closure | 65.31 minutes |
| Total | 423.69 minutes (7.06 hours) |

The 40.68-hour total deduplicates superseded snapshots of the same role claim
while retaining genuine failed and repeated handoff attempts.

## Reproducibility boundary

The repository retains the final manuscript source and PDF, exact
computational certificates, verification programs, archive manifests, and a
unified verification entry point. The large generated data are packaged into
two manifest-protected archives.

The public repository does not contain the private scheduling state, local
paths, authentication material, or complete conversation transcripts. The
published prompt and chronology are sufficient to explain the workflow
design, while the mathematical claims must be assessed from the proof,
programs, and certificates themselves.
