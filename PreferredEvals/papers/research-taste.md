# Research taste: selection, experiment planning and human labels

- [Anthropic TASTE, Aug. 2026](https://alignment.anthropic.com/2026/taste/): paired safety proposals, experienced human annotators, discussion and confident agreement. Its 92-pair result is a particular expert population; do not treat a new single LLM grader as the same ground truth.
- [TasteVal, Jaffe and Sherburn, Oct. 2026](https://arxiv.org/abs/2610.06824): an experiment-design Researcher under a fixed Coder and hard compute/wall-time budgets; 8 research tasks withheld. Reproduce the *method* on openly designed tasks rather than inventing the hidden suite.
- [IdeaTaste, Zhong et al., Nov. 2026](https://arxiv.org/abs/2611.03424): forecast-like 2025 literature snapshots evaluated against 2026 community activity, with hindsight and paper-matching limitations. Keep publication time split inviolable.
- [SciTaste-Bench, Gao et al., Oct. 2026](https://arxiv.org/abs/2610.28653): cross-disciplinary academic taste dimensions and metadata-based scoring. Document field normalization and label provenance.

**Design move:** pairwise blinded scoring with confidence, majority/adjudication, plus a separate prospective experimental budget trial. Measure how often preferred proposals succeed and experiment quality per cost. Test judge agreement on held-out authors/topics before optimization.
