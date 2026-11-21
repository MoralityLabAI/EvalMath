# Software engineering scoring integrity

- [OpenAI, Separating Signal from Noise (July 2026)](https://openai.com/index/separating-signal-from-noise-coding-evaluations/): systematic SWE-bench Pro task defects, including strict tests, ambiguous requirements and insufficient coverage; roughly 30% estimated broken.
- [Anthropic, Infrastructure Noise (Feb. 2026)](https://www.anthropic.com/research/infrastructure-noise): Terminal-Bench 2.0 performance varies with resource enforcement; measured six percentage-point span.
- [SWE-Bench Pro Verified (Sept. 2026)](https://arxiv.org/abs/2609.08149): academic proposed anti-leak and task-quality repair protocols. Independently validate patches and source availability.
- [Thinking Machines Inkling Verify](https://github.com/thinking-machines-lab/inkling-verify): fresh-container DeepSWE scoring, pinned Podman images, multi-run aggregation.

**Design move:** gold-patch check, three-way failure triage (model/infra/invalid task), upfront resource floor and hard limit, and full assigned denominator alongside gold-valid subset. Blind human adjudication on ambiguous cases.
