# RH numerator step gym

This additive curriculum supplies eight Lean proof tasks, `RHCG-021` through
`RHCG-028`, and six small initial-goal candidate pairs. They all belong to the
existing `rh-recurrence-construction-v1` training family. The source and recorded
artifacts for `RHCompactification` remain unchanged.

The mathematical source is `lean/FeedbackChannel/RHNumeratorStep.lean`. It uses
the earlier module's general recursion theorem, with `Init` as the underlying
Lean dependency. Each learner file contains the complete trusted earlier module
followed by the new module's prefix and the current theorem statement. The
current proof body and later declarations are withheld from that file.

## Mathematical scope

For arbitrary total natural functions `mul`, `add`, and `den`, the step relation is

\[
R(y,a,b) \iff (y=0\land b=a)\;\lor\;
\exists x,d,u,\ y=x+1\land d=\mathrm{den}(x)
\land u=\mathrm{mul}(y,a)\land b=\mathrm{add}(u,d).
\]

The obligations establish its zero and successor normal forms, identify its
deterministic graph, prove totality and functionality, normalize the recurrence,
construct its unique solution, and identify that solution with the existing
joint numerator after specializing `den` to the constructed denominator.
The first seven obligations permit any total denominator function. The final
obligation supplies the denominator recurrence through that specialization.

These statements concern Lean's `Nat` and total functions. RH-PL-18's Hilbert
certificates retain their own set-theoretic encoding and verifier. The package
records this fidelity boundary in every full task.

## Standalone setup and checks

Run the Python commands below from the repository root. Install the pinned Lean
toolchain with the official Elan installer if Elan is not already available:

```bash
curl -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -o /tmp/elan-init.sh
bash /tmp/elan-init.sh -y --default-toolchain none
"$HOME/.elan/bin/elan" toolchain install leanprover/lean4:v4.34.1
python -m pip install -e ".[test]"
```

The checker launches Lean from the repository's `lean/` directory, where
`lean-toolchain` selects 4.34.1. An absolute path to the release's `bin/lean` is
also accepted by `--lean-cmd`. The standalone checks compile inlined source and
require no local module cache.

```bash
python -m spiral_ln.rh_numerator_gym check
python scripts/verify_rh_numerator_native.py --lean-cmd "$HOME/.elan/bin/lean" --output /tmp/rh_numerator_native.json
RHNUM_LEAN="$HOME/.elan/bin/lean" python -m pytest -q tests/test_rh_numerator_gym.py
```

`check` validates source-derived tasks, artifact hashes, pack identities, labels,
runtime metadata, and the training scope. The native verifier then recompiles
the module and each teacher, replays each public `trace_state`, checks every
candidate against its complete theorem, and exercises six rejection controls.
Its receipt binds the verifier script, renderer, shared checker, and both Lean
sources. Lean reports no axioms for the first six obligations; the two function
uniqueness obligations use `Quot.sound` through function extensionality.

To regenerate this extension's source-derived artifacts after an authorized
source change:

```bash
python -m spiral_ln.rh_numerator_gym build
python -m spiral_ln.rh_numerator_gym pack-build --lean-cmd "$HOME/.elan/bin/lean"
python scripts/verify_rh_numerator_native.py --lean-cmd "$HOME/.elan/bin/lean"
```

## Proof-revision episodes

The new renderer delegates verification to the existing `LeanChecker` and uses
the existing `RevisionGym`. Start the line-delimited JSON server with:

```bash
python -m spiral_ln.rh_numerator_gym serve --lean-cmd "$HOME/.elan/bin/lean" --max-attempts 4
```

Each input line uses `{"op":"reset","id":"RHCG-021"}`,
`{"op":"step","proof":"..."}`, or `{"op":"close"}`. A reset exposes the
authenticated task and its remaining attempt budget. Each submitted proof
consumes one attempt, including rejected and unknown outcomes. The reward is
the change in verified-best potential from the shared gym: verified completion
earns one unit, followed by a bounded bonus for reducing the complete supplied
Lean source relative to the reference source. Prefix bytes count toward that
metric. Rejected and unknown attempts earn zero.

Every accepted candidate comes from a fresh Lean process and an axiom audit.
The backend enforces a 20-second default timeout, Lean's 768 MiB memory limit,
and 400,000 heartbeats. Timeout, resource, infrastructure, and unavailable-audit
outcomes remain unknown. The surface checker restricts submissions to ordinary
proof bodies and blocks target/future references. Operating-system isolation is
the host's responsibility.

## Candidate-ranking pack

`pack/manifest.json` uses `datagoblin.checked-candidate-pack.v1`. Public rows
contain the six native initial goals and two candidate proof bodies per goal.
Receipts live in `train.receipts.jsonl`. The near-miss candidate changes a
necessary proof step; its rejection is checked by Lean. Candidate IDs and their
order derive from hashes without oracle names.

The exact PPT input is `<STATEMENT> {statement}\n<GOALS> {context}`. These six
inputs occupy 134–214 UTF-8 bytes, and candidate proofs occupy 94–303 bytes.
Both fit the pinned reader's 384-byte cap. Full trusted source remains in the
separately hashed harnesses under `pack/sources/`.

From the EvalMath repository root, set `LOOPED_ROOT` to the existing
LoopedTransformers checkout pinned by the shared trainer contract. With a sibling
checkout, run:

```bash
RH_NUM_ROOT="$PWD"
LOOPED_ROOT="../LoopedTransformers"
cd "$LOOPED_ROOT/research/lean_cgrt_hrm400"
python -m ppt_gym train --pack "$RH_NUM_ROOT/gyms/RHNumeratorStep/pack" --plan a --out "$RH_NUM_ROOT/output/rh_numerator/ppt-smoke-replay" --width 32 --heads 4 --max-bytes 384 --depths 1 2 --steps 32 --threads 1 --max-seconds 60 --seed 17
```

## Recorded training check

The [adapter receipt](adapter_receipt.json) records acceptance by the original
DataGoblin and PPT loaders at the shared contract's pinned commits. All six
cases were usable, with six positive and six negative candidate labels. Every
input fit its byte cap.

The new pack completed 32 CPU optimizer updates through the pinned PPT trainer.
Its 25,571-parameter model used width 32, four attention heads, eight workspace
slots and recurrent depths 1 and 2. All six cases appear in the step log. The
recorded runtime used seed 17, one thread and Torch `2.5.1+cpu`; the upstream
trainer reported 0.200 seconds for its training loop.

[training_smoke.json](training_smoke.json) binds the run to pack manifest
`5c6eab4e72d30ef40f822bd869882864376ed9417b9231dde06ea3991146d71b`
and preserves checkpoint hash
`3421aba14f032e8017450b3097d46f6f3d627a80493a92d2fbe3eb885e246d99`.
The complete [training_steps.jsonl](training_steps.jsonl) contains one record per
update. The fast integrity verifier checks the recorded source and runtime
bindings; fresh native compilation has its own command above.

From the EvalMath repository root:

```bash
python scripts/verify_rh_numerator.py
python scripts/check_receipts.py --only rh_numerator
```

The shared trainer contract is pinned in
`gyms/RHCompactification/trainer_contract.json`. This pack contains only public
training data from one existing family. A held-out split remains unallocated.
The recorded run supplies engineering evidence for the adapter and trainer,
with the preflight verdict `REDESIGN_OR_PILOT_ONLY`. Model-effect claims require
a separate evaluation design. Recurrent ranking
passes and the full-proof episode's submission budget are recorded separately.
