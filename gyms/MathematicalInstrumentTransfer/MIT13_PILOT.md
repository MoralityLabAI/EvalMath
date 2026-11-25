# MIT-13 real-model proof pilot (development roots, no sealed split)

Seven arms on MIT-06 families plus a cross-domain `transfer` family and eight Lean 4 targets. Generated from
`mit13_fixtures.py` (seeds 91000 and up, disjoint from MIT-06's 83000-86031). Evidence class: open development only.

## Generate fixtures
```
cd gyms/MathematicalInstrumentTransfer
python mit13_fixtures.py --output OUT --roots-per-family 8 --budget 4096 --tokenizer cli --gguf MODEL.gguf
```
Tokenizer backends: `cli` runs `C:\Users\patri\tools\llama-b12686\bin\llama-tokenize.exe -m MODEL.gguf --stdin --ids --no-bos -ngl 0 --log-disable`
(vocabulary only, no GPU; about one process launch per count), `http` (`--base-url http://127.0.0.1:PORT`, uses `/tokenize` of a
running server), `whitespace` (tests only). Counts are cached in `OUT/token_cache.json` keyed by sha256(text) plus a model key.

Outputs: `prompts.jsonl` (opaque `id`, `prompt`, `max_tokens`), `private.jsonl` (gold, arm, family, root, variant, candidate,
expected_mapping_valid, adaptive menu and gold letter, token counts, prompt sha256, dispatch id), `manifest.json` (sha256 of both files
and of the source files). Never expose `private.jsonl` to the model or the dispatcher.

## Run (GPU part; placeholders)
```
llama-server -m MODEL.gguf --port PORT <frozen sampling and template flags>
python mit13_dispatch.py --base-url http://127.0.0.1:PORT --prompts OUT/prompts.jsonl --output OUT/responses.jsonl --seed 13 --retries 1
python mit13_score.py --private OUT/private.jsonl --responses OUT/responses.jsonl --output OUT/scores.json --budget 4096 --checkpoint CHECKPOINT_HASH --effect-arm instrument --pilot-out OUT/pilot.json
python ../../skills/evalmath-mechinterp-power/scripts/preflight.py --pilot OUT/pilot.json
```
The dispatcher resumes by skipping ids already in the responses file. `--budget` at scoring must equal the budget used at generation.
Lean rows are checked through WSL (`~/.elan/toolchains/leanprover--lean4---v4.34.1`, core Lean, CPU).

## Arms
unaided; source (relevant source text); instrument (abstract technique); near_miss (inapplicable candidate certificate); oracle (valid
candidate); sham (irrelevant source token-matched to the source prompt); adaptive (menu of the four family instruments in a seeded
order, lettered A-D, the model reports `selected_instrument`). False targets get unaided, instrument, adaptive. The `transfer` family is a
staffing-cost claim with covering structure; its source and instrument arms carry the LP-duality text, its applicable instrument for the
adaptive arm is the covering one (the LP bound with inequalities reversed), and its contract names no certificate type. Lean rows:
unaided and instrument; the response is `{"proof": "<tactic block after := by>"}`.

## Scoring
Closure (exact `verify`, or Lean pass with axioms within propext, Classical.choice, Quot.sound) is scored separately from applicability
(`mapping_valid` against gold for near_miss and oracle, with false accepts counted; `selected_instrument` against the applicable family for
adaptive). Missing, malformed, over-budget and failed rows count as closure failures and keep a `status`. Pilot units are roots; the
paired effect is closure(effect arm) minus closure(sham); the matched sham observation is closure(sham) minus closure(unaided).
`units_independent` is written as false and `heldout_sealed` as false, so preflight returns REDESIGN_OR_PILOT_ONLY by construction.

## Matched and not matched
Matched: total prompt token count of sham versus source rows, within 2 tokens under the chosen tokenizer (both counts recorded per row);
one fixed system prompt; fresh single-turn chat per row; one total token budget covering prompt and every attempt; server usage tokens
(with a `/tokenize` cross-check field).
Not matched: sham content and difficulty cues beyond length; instrument and near_miss text length; wall-clock (recorded separately per attempt);
chat-template overhead is estimated as 24 tokens when capping the first attempt; one sample per row, so within-root sampling noise is not measured;
sham counts depend on the tokenizer used at generation.
Lean filter rejects text containing sorry, admit, axiom, native_decide, implemented_by, extern, unsafe, `@[`, import, open, set_option,
metaprogramming commands, top-level commands, `#`, and the target theorem's own name.
