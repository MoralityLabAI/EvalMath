# Elicitation without Backpropagation (Baker et al., 2026)

- **Paper:** https://arxiv.org/abs/2607.18804
- **Authors:** Garrett Baker, Vinayak Pathak, Daniel Murfet, Susan Wei.
- **Code:** https://github.com/timaeus-research/elicitation
- **Relevance to EvalMath:** The same latent-prior Monte Carlo bank supplies importance-weighted PPT gradients for an arbitrary number of utilities. Adaptive prompt or utility search can select the bank's sampling noise. An ESS statistic diagnoses weight concentration, not post-selection generalization.
- **Local research crossover:** [`../../paper/ppt_adaptive_reuse.md`](../../paper/ppt_adaptive_reuse.md), `PPT-EVAL-01`.
- **Status:** Paper indexed; exact synthetic counterexamples and certificate logic verified; model-scale reproduction pending. The upstream publication is referenced rather than copied here.
