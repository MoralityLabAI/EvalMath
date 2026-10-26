# Reviewing EvalMath

This guide is for a reviewer, human or model, asked to check this repository. The work was produced by
a lead model delegating to subagents. Every delegated result was rerun and, for the sharpest claims,
checked with independent code; the [journey map](docs/feedback_channel_journey_2026-10-11_13.md) and
the redacted [session log](docs/session_logs/2026-10-11_feedback_channel/README.md) show how. That
process found many errors, so assume more remain. The most useful review finds them.

## What to check

1. **Every claim labelled *algebraic identity*.** Is it proved for every parameter its statement
   covers, including boundary cases? Earlier errors clustered at boundaries: categories with no
   failures, accuracy exactly 1, horizons of one step, product indices starting at zero, ties between
   optimal actions.
2. **Every claim labelled *finite verified example*.** Is it described as finite everywhere it is
   used, including in the synthesis? Is any grid regularity promoted to a theorem anywhere?
3. **The Lean formalizations.** For each row of [`lean/CLAIMS.md`](lean/CLAIMS.md), does the Lean
   statement say what the note says, with the same quantifiers and hypotheses? A row labelled *full*
   that is weaker than the note is a bug, and so is a hypothesis that makes the theorem trivial.
4. **The computer-assisted proof** in [`paper/selection_law_kl_containment.md`](paper/selection_law_kl_containment.md)
   D.5 (*K* = 4 to 30). Check the constants' derivation, the directed rounding, and the two cited
   inputs (Robbins' Stirling bounds; Poisson summation, cited from memory).
5. **The counterexamples.** Each is stated exactly; re-derive at least the gate counterexample in
   [`paper/evaluation_feedback_multigen.md`](paper/evaluation_feedback_multigen.md) §6 and
   Counterexample 9 in [`paper/leak_topology.md`](paper/leak_topology.md) with your own code.
6. **The receipts.** `python scripts/check_receipts.py --all` should report every receipt as
   regenerating identically apart from its timestamp, with matching source hashes.
7. **The synthesis.** Does [`paper/feedback_channel_findings.md`](paper/feedback_channel_findings.md)
   state each result no more strongly than its note does?

## Results to test first

- Training-signal L4: observed accuracy a − ε + 2(1 − a)ε₁ reaches the ceiling without memorization
  iff ε₁ ≥ ½, for *a* < 1.
- Reuse inflation: the running maximum of *GK* + 1 draws and the bound √(ln(*GK* + 1)/(2*n*)).
- Theorem B: KL(best-of-*K* ‖ base) ≤ ln *K* − (*K* − 1)/*K* for every finite law and tie rule.
- Lattice Theorems 10 and 11 and Corollary 14 (committing until a hit is optimal iff *H* ≤ 2).
- Multigen Proposition 10 and the two-gain counterexample.
- Gold calibration: the six four-rater equalities, the copying-grader residual, and the coverage of the
  §11 interval.
- Leak topology Theorem 1 (fibre dimension equals the cycle rank) and Counterexample 9.

## How to report

For a wrong claim, give the note, the claim's label and an exact witness: parameters, state, and the
values on each side. For a gap in a proof, name the step and what it assumes. For a Lean fidelity
problem, give the theorem name and the hypothesis or quantifier that differs. Please keep findings
separate from suggestions.

## External claim-fidelity review

The [OpenAI ETH case study](paper/proof_fidelity_openai_eth.md) has a separate
source-integrity audit. Reviewers should distinguish the admitted comparator
specification from the actual Lean implementation, check the square-root-log
versus log-log-squared exponent scopes, and rerun its receipt. Upstream Lean
kernel compilation and the manuscript-only tensor contraction remain outside
the automated source checker.

## Scope

Nothing here is evidence about any real model, judge or grader. The session log was redacted of private
material unrelated to this work; its README states the rules and the checks made.
