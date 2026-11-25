# What is proved in Lean: the six theorems, and the soundness theorem on `verify` beneath `sound`

Six theorems are proved in Lean of one committer, prover and verifier, `compile (flashProve setup)`,
at every public setup `setup` (`PublicSetup`: three public files, what the reader returns at them,
and `FilesInUse`). [STATEMENTS.html](STATEMENTS.html) opens on them:

- Soundness, `sound`: a cheating committer and prover with q hash queries between them get the
  verifier to accept output tokens that are not the model's, at the weights that one extractor
  reads from the commitment and the committer's hash queries, with probability at most about
  q/2^124 + 2^-101. That is a bound, not a security level (`lean/LIMITS.md`, L11).
- Soundness with binding, `soundAndBinding`: soundness and binding, with one extractor for both:
  nobody opens the commitment to weights other than that extractor's, except with probability
  about q/2^124 + 2^-100, where q counts the hash queries of whoever made the commitment and of
  the opener together.
- Completeness, at the requests that can be served, `completeOnCanServe`: at every request that
  can be served (`CanServe`) and whose output tokens are the model's, the honest proof is rejected
  with probability at most 2^-40. Nothing is said of a request outside `CanServe`, among them
  those where the model has no result, or of an output that is not the model's: there the honest
  prover's reply is the empty proof. Which requests can be served depends on the weights.
- Zero knowledge, at the requests that can be served, `zeroKnowledgeOnCanServe`: there is a bound
  that stays at or below 2^-154 within 2^64 hash queries and 688,127 replies, and zero knowledge
  holds within this bound on the requests that can be served and whose output tokens are the
  model's: one simulator, which may depend on the public setup and is handed nothing of the
  weights in the experiment. What the public files tell of the weights is not counted. Whether a
  request can be served depends on the weights, and that is not hidden. By itself it says nothing
  of a refused request. One request per proof and one commitment are covered, not batches. What
  else it does not cover: `lean/LIMITS.md`, L93, L83.
- The reply at a refused request, `refusedHandsOutNoProof`: every reply that the prover can return
  at a refused request is the empty proof. A request is refused if it is ill-formed, if the model
  has no result on it, or if its result is other tokens. That a refusal is right is not covered:
  an empty proof proves nothing, and a prover can return it at a request that it could serve.
- The replies fit, `repliesFit`: 688,127 (`finalReplyCount`) is at most `onlineRunsPerCopy setup`,
  the number of runs of the online IOP that the honest settings give one copy; the opened columns
  fit each table; and one run each of the honest sampler of commitment randomness, the honest
  committer and the honest prover make together at most 2^48 hash queries. `onlineRunsPerCopy` is
  a written number, 688,127 too: the first compares two written numbers. The second is what ties
  that number to a table: 62 + 688,127 · 64 columns are within a copy's 44,040,191. The prover
  counts no replies, so nothing in it enforces the first two.
- All six ask for exact match, which the verifier does not test: public files with another policy
  are not covered (`lean/LIMITS.md`, L5). A provider that picks its public files after seeing the
  hash function is not covered either (`lean/LIMITS.md`, L28). One public setup is known
  (`FilesInUse`; `filesInUse_stored`): the library's stored full-size files (`storedSetup`); their
  scale file is that of an example with synthetic weights (by the head of `lean/Ladder/Stored.lean`;
  no theorem).

All six are proved in Lean. What each says, with its limits: "The final statement's six fields".

**The Lean verifier.** Two Lean terms bear this name: one verifier, with and without its hash
function. The audit page's Lean verifier is `leanVerifier setup`, that is `(compile (flashProve
setup)).accepts blake2bHash`: the compiled verifier with each of its hash queries answered by
BLAKE2b. On the other pages the Lean verifier is `verify` (`lean/Ladder.lean`): the verifier of that
same system, before any hash function is supplied (`compile_flashProve_verify_eq`, with
`theDescription_eq`). As in any proof in the random-oracle model, the six speak of the verifier
under a hash function drawn at random, not of `leanVerifier`, where BLAKE2b stands in its place: the
three that speak of acceptance (`sound`, `soundAndBinding`, `completeOnCanServe`) draw the hash
function at random, so their verifier is `verify` under a random hash function, not at BLAKE2b; the
other three do not call the verifier. `leanVerifier setup` equals `finalVerifierProgram` at that
setup's files (`leanVerifier_eq`). Wherever the user's files read as a claim, the verdict of
`verdictOf`, the function whose parts `lean-verify` evaluates (`verdictOf_at`), is
`finalVerifierProgram` at the user's public files (`verdictOf_eq_finalVerifierProgram`), and it is
`verify`'s value at BLAKE2b (`verdictOf_map`). So, where the user's files read as a claim and the
user's public files are a public setup's, and only there, that verdict is `leanVerifier`'s
(`verdictOf_eq_leanVerifier`); the command does not establish that the public files are a public
setup's. Five of the files that this function takes come from a parser outside Lean, of which
nothing is proved, and nothing is proved of a run (`lean/LIMITS.md`, L53; L9).

The line `sound` rests on a theorem on `verify`: *the soundness theorem on `verify`*,
`VerifierAndGoals.AtTheName.sound_of_verify_at` (`lean/Johnson/Goal/Skeleton/SoundOfVerifyAt.lean`):
`verify` is proved sound at the given public files, in the random-oracle model and at exact match.
`finalSound` takes it at the files and carries `Sound` over to the compiled system
(`theDescription_eq`, `lean/Johnson/Goal/Description/Description.lean`;
`compile_flashProve_sound_iff`, `lean/Johnson/Face/FinalStatement.lean`; `finalSound` itself:
`lean/Johnson/Face/FinalSoundProof.lean`), and `sound` is `finalSound` at a public setup. Beside
Lean's own kernel, a second kernel written by others (nanoda: `lean/CHECKING.md`, "The independent
checker") has accepted the soundness theorem on `verify` with all that lies beneath it. Of the six,
the independent checker has accepted `sound`, `repliesFit` and `refusedHandsOutNoProof` by name,
over a build of this repository's files; over such a build the three on binding, completeness and
zero knowledge have been checked by Lean's kernel alone. Most of this page is about the soundness
theorem on `verify`.

## The soundness theorem on `verify`

**Soundness** is proved, in Lean, for the verifier written in Lean: it accepts a proof of a false
claim with probability at most about 2^-124 per hash query (with a floor of about 2^-101), in the
random-oracle model, for [exact-match](../guide/terms.md) claims; under the [clipped-gap
policy](../guide/terms.md) that serving uses, Lean proves only that the reply meets that policy
([Known limits](../guide/known-limits.md)). The C++ verifier and the CUDA prover are written to
follow the same protocol and are tested against it, not themselves proved.

Where its conditions stand: "Look first at four things" (what you must check yourself), "Its reach"
(at which public files) and "What it does not say", 3 (the theorem is for exact match, while the
clipped-gap policy is the expected use: [guide/known-limits.md](../guide/known-limits.md)).
Completeness and zero knowledge are proved in Lean for the protocol, at full size, each up to a
small stated error: first for the interactive protocol (IOP), then for the compiled
(non-interactive) prover and the same Lean verifier, in the random-oracle model. Both are at the
exact-match policy, with fresh random masks, for one commitment and one request per proof, not for
batches. The honest prover in these theorems is a Lean definition, not the CUDA prover. Lean's
theorem on zero knowledge is for exact match: under a clipped-gap policy no Lean theorem covers what
a whole proof reveals ("Completeness and zero knowledge: what is proved for the protocol, and what
is not", "The three statements at one protocol", "The final statement's six fields").

To check it yourself: "How to check it". Terms: [TERMS.md](TERMS.md). All limits and gaps, entry by
entry: [LIMITS.md](LIMITS.md), [GAPS.md](GAPS.md). To audit the statement and its definitions:
[STATEMENTS.html](STATEMENTS.html) (in plain text: [AUDIT.md](AUDIT.md)). The two long pages,
LIMITS.md and GAPS.md, are written to be looked up, not read through. A
number behind lean/GAPS.md, as in "lean/GAPS.md, 52", is an entry of that page, not a line; a label
behind lean/LIMITS.md, as in "L15", is an entry there.

`verify` takes three public files (parameter, layout and scale file), a commitment to a language
model's weights, a prompt, a list of output tokens and a proof, and accepts or rejects. On this page
`verify` is the Lean verifier and `cp_verify` the C++ verifier; the three public files are also
called configuration files, and files in scope an admissible configuration.

## The statement, as Lean prints it

```
VerifierAndGoals.AtTheName.sound_of_verify_at (Z : VerifierAndGoals.PublicFiles) (pp : Inst.Model.ScalesAndPolicy)
  (scope : VerifierAndGoals.InScope Z = true) (read : VerifierAndGoals.readFiles Z = Except.ok pp)
  (exact : pp.pol = Inst.Model.AcceptancePolicy.exact) :
  VerifiableInference.Sound
    (VerifierAndGoals.systemOfRecord (VerifierAndGoals.atSecondHashFunction VerifierAndGoals.theDescription) Z
      (VerifierAndGoals.settingsOfRead pp))
    fun t => VerifierAndGoals.soundnessErrorInQueries t 1
VerifierAndGoals.AtTheName.nearestSound_of_verify :
  VerifierAndGoals.NearestSound VerifierAndGoals.theDescription fun t => VerifierAndGoals.soundnessErrorInQueries t 1
```

`systemOfRecord D Z s` is the argument system whose verifier is `verify` at the protocol `D` and the
files `Z`. `atSecondHashFunction D` is `D` with the protocol's second, fixed hash function,
`OnBytes.secondHashFunction`, put in (`lean/Ladder.lean`; "What it rests on", "Two hash functions").
The second is the same statement with `Z` and `pp` quantified inside a definition (`NearestSound`,
`lean/Ladder/Package.lean`). (Soundness without the exact-match premise is not proved at all files
in scope, and is not expected to hold at a small error: `lean/Ladder/Package.lean`.) What `Sound`
asks: "The experiment". What `soundnessErrorInQueries t 1` is: "The error". What `InScope` admits:
"Its reach".

## In short

- **Proved, of the protocol as written in Lean.** The Lean verifier, `verify` (not the C++ verifier
  that users run by default), is proved sound at the given public files, in the random-oracle model
  and at exact match (greedy decoding: the policy, set in the parameter file, under which every
  output token must be the model's own choice), against a committer and a prover who may both cheat.
  (The theorem: `VerifierAndGoals.AtTheName.sound_of_verify_at`, in
  `lean/Johnson/Goal/Skeleton/SoundOfVerifyAt.lean`.) It accepts a false claim with probability at
  most about q/2^124 + 2^-101 after q queries to the random oracle, the committer's and the prover's
  added up. "False" means false at the weights that a fixed extractor reads off the commitment and
  the committer's hash queries. The main conditions, beside exact match (which `verify` does not
  test: you check it in the parameter file): one proof format and model size (`verify` rejects
  others), and public files that are fixed before the hash function is sampled (a provider that
  tunes them to the real hash function is outside the statement). The bound is for one commitment,
  one prompt, one output, one proof and one call of `verify`. Outside the files at which an honest
  proof has been accepted the theorem may hold only because `verify` rejects everything ("Its
  reach").

  The oracle stands for the format's hash function; a second, fixed hash function, built on
  BLAKE2b's compression function, is taken as separate from it. The same is proved of its executable
  form, a Lean term that a machine can run, where the functions on bytes that stand for the hash
  function answer with 32 bytes, as the real one does. Lean's kernel has checked the proofs, which
  rest on Lean's three standard axioms alone and on no conjecture on error-correcting codes; the
  random oracle and the second hash function belong to the statement, not to the proof's axioms. (Of
  an illustrative committer, a Lean committer that models one part of `cp_commit` (no theorem ties
  the two), more is proved: "What the commitment gives, as proved".) (What Lean proves beside
  soundness: "Completeness and zero knowledge: what is proved for the protocol, and what is not".)
- **What an accept means.** Except on an event of probability at most that bound (over the hash
  function and the parties' coins), an accept by `verify`, not by the C++ verifier, implies that
  each output token is the model's own choice (the theorem's "model": "Look first at four
  things", 3), at the public files that you hold and the weights that, at those files, were settled
  when the commitment was made. This bounds the chance of a false accept, not the chance that a
  given accept is false. The statement holds under the conditions above, and only if you also do
  three things and grant two (to do: check the policy's three lines, read the scale file, check the
  output's length: "Look first at four things", 1 and 3; to grant: that the code that turns your
  files into the claim is right: 4 there; and what a run trusts: "What has been run").
- **[Completeness](../guide/terms.md) and [zero knowledge](../guide/weight-hiding.md)** are proved
  in Lean for the protocol, at full size, each up to a small stated error: first for the interactive
  protocol (IOP), then for the compiled (non-interactive) prover and the same Lean verifier, in the
  random-oracle model. The honest prover in these theorems is a Lean definition, not the CUDA
  prover. Completeness covers well-formed requests on which the model has a result and the claimed
  output is that result. Where the model has no result it says nothing. Zero knowledge holds against
  an honest verifier in the IOP and, after compiling, against any verifier within a bound on its
  hash queries and replies, on one copy of the table; the simulator's running time is not modelled.
  Both are at the exact-match policy, with fresh random masks, for one commitment and one request
  per proof, not for batches. One bit per request is revealed (served or refused: a request is
  refused if it is ill-formed, if the model has no result on it, or if its result is other tokens),
  and it depends on the weights. A service that chooses to say "failed" reveals one label of three
  in its place (served, failed or other tokens). Neither says anything of what the public files
  themselves tell of the weights, or of timing. Both theorems are about the Lean prover exactly as
  written, default values included. Whether that text is the prover that the protocol's authors
  mean, and that the CUDA prover implements, is for the audit of the definition. The definition
  isn't a program: among other things it obtains the model's trace by a non-constructive choice.
  ("Completeness and zero knowledge: what is proved for the protocol, and what is not", "The three
  statements at one protocol", "The final statement's six fields".) The soundness theorem on
  `verify` itself says nothing on hiding.
- **The programs.** In runs, every honest full-size proof from the CUDA prover that was put to the
  Lean verifier with its own claim, in a call that ran to its end, was accepted — at essentially two
  configurations, on synthetic weights, most requests of one shape. The prover of these runs was
  built from sources that differ from this repository's; in what:
  [docs/limits.md](../docs/limits.md#the-timed-runs). Of 57 lying proofs tried at full size none was
  accepted by either verifier. Which of these calls were made over this repository's Lean files:
  "What has been run". Nothing is proved of the C++ verifier that the examples and most users run,
  of the CUDA prover, or of the committer, and no theorem says that they run the protocol the Lean
  verifier checks: that rests on tests. Nor is correctness of extraction (that the extracted weights
  are the ones put in) proved for `cp_commit`. The tests, and how narrow they are: "What has been
  run".

## Look first at four things

Two premises on the public files, one reading, and one gap that stands in front of the theorem, not
in it.

1. **Exact match.** Exact match is a premise on the parameter file, not a test in the text of
   `verify`. Files with another policy are in scope, and some put no condition on the counted
   tokens. At exact match the parameter file's three policy lines `C`, `theta`, `cap` read 256,
   256, 0. So a user, or the program that calls `verify` for them, must check these three lines. At
   other policies the theorem under a policy (`soundUnderPolicy_of_verify_at`), below, gives only
   that the output meets the policy, which alone is weak ("Alone it is weak").

2. **The public files are fixed first.** The three public files are fixed before the hash function
   is sampled, like system parameters; the commitment, prompt, output and proof may depend on the
   hash and are covered. The IOPs and the tests on the public files are written out in Lean with a
   32-byte constant in the place of the files' digest; the hashed strings hold the digests that the
   verifier gets from the oracle (`lean/SOUNDNESS-PROOF-MAP.md`, "How the statement enters the
   hash"; by reading: no theorem says that every challenge depends on them: `lean/GAPS.md`, 5),
   which is meant to guard against public files tuned to the hash function, a case outside the
   theorem. A provider that tunes the public files themselves to the real hash function is outside
   the statement. No theorem ties a commitment to one set of public files.

3. **The model.** "The model" means the extracted weights, which no theorem says are the ones
   `cp_commit` put in (for an illustrative committer it is proved: "What the commitment gives, as
   proved"), run at the public scale and parameter files, which you must hold and read. Scale files
   in scope can switch off any of the model's blocks, up to all of them (worked out by hand, not
   proved). So read the scale file that you are given. At each position it is the greedy next token
   after the prompt and the output's own earlier tokens, as an integer program computes it, not the
   floating-point model. (How far the two differ: "What it does not say", 5.) Nothing is said about
   where the model would stop. Any prefix counts as correct, the empty one too. (At exact match the
   theorem under a policy rules the empty output out, at the same error:
   `Policy.meetsPolicy_exact_iff`.) So check the output's length yourself. The theorem names no
   public model, and no theorem shows that a real model's weights meet the program's range
   conditions. That narrows what can be certified. It does not weaken soundness. (A count outside
   Lean, by the integer-model package's own range checks, found none failing on each of some
   hundreds of windows, which come from far fewer prompts than there are windows, at a public
   model's 4-bit weights; what that count does not show: `lean/LIMITS.md`, "At real weights: a
   count, no theorem".) No theorem describes the five constant look-up tables in the Lean text
   (cosine, sine, the exponential, SiLU and the sigmoid).

4. **The claim.** The proof's bytes are the adversary's and need no trust: the theorem holds for
   every proof string, and a second theorem for every proof parser with a bounded number of hash
   queries, at an error that grows with them (`sound_of_verify_parsers_at`). The public files, the
   commitment, the prompt and the output must come from the user. Three short Lean functions make
   the last three from a user's files (`PV.Program.claimOf`, `lean/Johnson/PVR/Program.lean`, and
   the two readers that it calls, `PV.Front.idOf` and `PV.Front.userOf`,
   `lean/Johnson/Top/Fire/Code/PvFront.lean`), under no theorem: a slip there would make `verify`
   check the wrong claim (`lean/GAPS.md`, gap 37).

## In exact terms

At public files that are in scope, are read, ask for exact match and are fixed before the hash
function is sampled, a fixed extractor reads at most one set of weights off the commitment and the
committer's hash queries, before any proof is made, and `verify` accepts an output that is not the
model's output at those weights, or any output where there are none, with probability at most about
q/2^124 + 2^-101, where q counts the committer's and the prover's queries to the format's hash
function, a random oracle.

The theorem is `VerifierAndGoals.AtTheName.sound_of_verify_at`, in
`lean/Johnson/Goal/Skeleton/SoundOfVerifyAt.lean`. `verify` is the verifier of a non-interactive
argument in the random oracle model. It is compiled in Lean, by Merkle trees and the Fiat–Shamir
transformation, from an interactive oracle proof that is itself written in Lean
(`VerifierAndGoals.theDescription`). That this interactive oracle proof is the protocol of the C++
programs is not proved (`lean/Ladder.lean`, point 7 of its opening comment).

### The experiment

`Sound` (`lean/VerifiableInference/Statements.lean`) is a game. The hash function is sampled. A
committer, with at most a hash queries, gives out a commitment and hands its state on. The extractor
is given the commitment and the committer's queries with their answers, and returns weights or none.
A prover, with that state and at most b queries, picks a prompt, an output and a proof, and `verify`
decides. `Sound` says that there is one extractor such that, whatever the committer and the prover,
`verify` accepts a false claim with probability at most the bound at q = a + b.

### The error

`verify` lets a false claim pass with probability at most about 16·(q + 2^23)/2^128 after q hash
queries, the committer's and the prover's added up. That is about q/2^124 + 2^-101: 124 bits per
hash query, and the bound is never smaller than about 2^-101. At q = 2^64 that is about 2^-60.

- **The error.** `soundnessErrorInQueries q 1 = 16 · T / 2^128 + (T + 2)² / 2^256` with `T = q + 1 +
  2^23`: 1 for the proof parser's hash query, 2^23 as a fixed allowance for the verifier's own
  queries as the compiler counts them. It says nothing from about q = 2^124 on.
- **The unit.** One query returns 32 bytes. A real BLAKE2b call that returns 64 bytes (each
  Fiat–Shamir challenge call, a proof-of-work attempt among them) is two queries, every other real
  call is one. So 124 bits per query, with its floor of about 2^-101, is at least 123 bits per real
  call.
- **Proof of work is counted.** Without their 20 to 32 bits of it, the rounds that sample query
  positions have errors of about 2^-96 to 2^-110 (added up by a program, no theorem). They are bits
  of single rounds, not the chance of a forgery. The theorem's own bound is stated whole and does
  not lean on that sum; each attempt at the proof of work is paid for in hash queries, inside q.
  (The rounds one by one: `lean/GAPS.md`, 36.)

### Its reach

The theorem holds for one fixed proof format and model size ("in scope": only the scale file and
eight numbers of the parameter file may vary), if the parameter file asks that every output token
equal the model's own ("exact match"), and if the three public files are fixed before the hash
function is sampled. The small example's files are out of scope: `verify` rejects them.

The proof needs sixteen conditions that are not proved for all files in scope. Each is a test inside
`verify`, on the public files alone, whatever the proof: the theorem is about the verifier with
these tests. Where one fails, `verify` rejects everything. They are proved to pass at the library's
written copy of the full-size public files (`AtFullSide.Top.theLive_zFull`, in a side library), not
at this repository's files, and at that copy with only the policy changed; at seven further sets in
scope they were evaluated and passed, over Lean files that differ from this repository's. That the
written copies have the bytes of this repository's two full-size example sets is compared by a
program in this repository, which a reader can run, not by Lean
(`lean/scripts/check_stored_examples.py`; `lean/CHECKING.md`): no theorem ties the Lean terms to a
file on disk. At all other files in scope nothing is known, so there the theorem may hold only
because `verify` rejects everything. At the two stored sets the runs show accepts, so there the
tests pass in a run too.

- **The side library.** Some constants beneath the side library's theorems fail in Lean's kernel at
  the default thread stack and pass at a larger one, at which that library is compiled;
  `leanchecker`, which has no option for the stack, fails on them, so the script does not hand them
  to it: all twenty-three modules of that library that are shown to need the larger stack, with
  every other module of `lean/AtFullSide/` and `lean/ShapeLines/`, are sent past `leanchecker` by
  the script, to Lean's own replay at the wider stack (`lean/CHECKING.md`). (Seen for twenty-two in
  runs over Lean files that differ from this repository's, `lean/GAPS.md`, 73, and for
  `lean/AtFullSide/Layout/TieRfl.lean` on two machines, `lean/scripts/RULES.txt`.) The soundness
  theorems — on `verify` (`sound_of_verify_at`), the compiled line (`finalSound`), the executable
  form's two (`theForm_eq_verify`, `sound_of_the_form_events`), and soundness as an IOP with its
  figure — do not depend on such a constant: no file beneath any of them imports the side library.
  The theorems that show the stored full-size files meet those conditions rest on at least one such
  constant, by way of `theLive_zFull` (`filesInUse_stored`, `statementAtStoredFiles_holds` and the
  two "AtWritten" files). Of the theorems of "The three statements at one protocol" and "The final
  statement's six fields", those whose files lie under `lean/AtFullSide/` stand in the side library;
  it and `lean/ShapeLines/` are compiled with a larger thread stack. By import lines modules that
  hold such constants lie beneath the modules of `complete_in_scope`, `zkOnServedRequests_inScope`,
  `completeOnServedRequests_at_every_files_in_use`, `finalAtT1_filled_withRoom`,
  `threeAtFiles_in_use`, `theFinalStatementHolds`, `finalZeroKnowledgeOneBit_value`,
  `finalRefusedHandsOutNoProof_value`, `theFinalStatementOneBitHolds`,
  `theHonestPart_complete_where_the_worst_case_check_passes` and
  `theHonestPart_complete_where_some_worst_case_check_passes` (these two are the completeness
  theorem at weights that pass a worst-case check, in two forms: `lean/LIMITS.md`, L93), and of
  `finalSoundAndBinding_value` and `rejectsNoProof_value`; `lean/ShapeLines/` lies beneath those of
  the first eleven and not of these two. By a walk over the constants of the build of this
  repository's files that [CHECK-RESULTS.md](CHECK-RESULTS.md) tells as made in seven calls, proofs
  included (a program's finding, no theorem; it takes as given the twenty-three modules that
  `lean/GAPS.md`, 73, names, and measures no stack), `finalSoundAndBinding_value`,
  `rejectsNoProof_value` and `finalRefusedHandsOutNoProof_value` (and `finalHandsOutNoProof_value`,
  which this page does not otherwise name) reach no constant of these modules, and each of the
  others reaches at least one. (`lean/GAPS.md`, 52 and 73; `lean/LIMITS.md`, L69.)

### The formal name, and how the theorem fills the definition in

**The formal name.** `Sound` is index-binding knowledge soundness, in its witness-free case, as
defined in `lean/ZKCP/Defs.lean` (`HasIndexBinding`; the terms: [TERMS.md](TERMS.md)), for a claim
(a prompt with an output that is said to be the model's): a second checked theorem, `sound_iff`
(`lean/VerifiableInference/Agreement.lean`), says so of every argument system, and a third,
`indexBinding_of_verify_at` (`lean/Johnson/Goal/Skeleton/SoundOfVerifyForms.lean`), says it of
`verify`. The name does not mean that a prover knew the weights, nor that a commitment stands for
the same weights under all public files. No form with a witness (the model's whole run, read off the
proof and the prover's queries) is stated at `verify`.

**How the theorem fills the definition in,** beside the missing witness: one error, at the sum q of
the two parties' bounds on their queries (two who share one budget of q queries as they go are
covered at 2q at most: `lean/LIMITS.md`, L38); the key is the 256-bit commitment alone; the
extractor is straight-line, but a rule defined with choice, not a program with a running time; the
bound is for one proof; and the public files stand outside what the committer chooses with the hash
function in hand. The last makes the theorem say less than the definition asks, for a reader who
counts these files among what the committer publishes.

**The soundness theorems in the definition's Lean form, as corollaries.** They also stand in that
form, and for at most N proofs that one prover sends at once under one commitment at N times the
error, the error taken at the whole list's hash queries (`soundManyProofs_union_of_verify_at`,
`lean/Johnson/Goal/Skeleton/SoundOfVerifyForms.lean`), for a prover that has seen no honest proof;
for separate sessions no theorem states it. Every limit on this page holds of them too.

### What it rests on

Lean's kernel has checked every proof of the main library that is named here; they rest on Lean's
three standard axioms alone, and no conjecture on codes is assumed. (The side library's proofs: "Its
reach".) "Usual" marks what goes with every proof of this kind.

- **Lean's kernel and three standard axioms:** `propext`, `Classical.choice`, `Quot.sound`. The
  kernel is trusted, not proved; the pinned version, 4.29.1, is older than fixes of publicly known
  soundness bugs in it: `lean/LIMITS.md`, L45. (Some proofs and a few definitions beneath the
  statement are written with tactics, notation and small programs of this library's own. The kernel
  checks every term that they build, so no proof rests on them. What a definition written so means:
  `lean/GAPS.md`, 18.)
- **Two hash functions.** The format's hash function is the random oracle. The second hash function
  digests the public tables and parts of the statement, the prover's prompt and output among them.
  The theorem fixes it as one named function (`secondHashFunction`) and assumes no further property
  of it, collision resistance included. It is not proved for every function in its place. What is
  assumed is that it may be treated as separate from the sampled one. (Why a collision of the second
  hash function merges no two queries: `lean/SOUNDNESS-PROOF-MAP.md`, "How the statement enters the
  hash".) Usual: the committer and the prover query the oracle classically, one bit string at a time
  (`RandomizedAlgorithm`, `lean/VerifiableInference/RandomOracleModel.lean`), so nothing is claimed
  against a quantum adversary. Usual too: the bound is over a hash function drawn at random, and of
  the real one it says nothing; so it does not rule out a verifier that treats the real hash
  function specially (`lean/Ladder.lean`, point 10). Here that is not only formal: one constant
  beneath `verify` is a value of the real hash function (`recordCfg`, in
  lean/OnBytes/Params/EntryDryRecord.lean, the digest of one example's three public files); that
  nothing beneath `verify` reads it is a reading of the code, and no theorem in this repository says
  it. (`lean/GAPS.md`, 51. It is not the 32-byte constant of "Look first at four things", 2, which
  is a fixed value where the oracle's digest of the files goes.) (Of the programs, and of the
  theorem on `innerCompiledVerifier`, another theorem of this library, more is assumed: that the
  second hash function resists collisions: `lean/LIMITS.md`, V3, "Assumption 2".)
- **Beside the soundness theorem on `verify`.** The soundness theorem on `verify` that this page
  cites (`sound_of_verify_at`), and `finalSound` above it (`lean/LIMITS.md`, L93), do not rest on
  soundness as an IOP (`lean/LIMITS.md`, L89): by import lines the file of its proofs lies beneath
  neither. The proof of the soundness theorem on `verify` takes the round-by-round soundness of the
  key, copy and proof protocols one by one (`keySound`, `entrySound`, `proofSound`, three of the
  compiler's named hypotheses; where each is proved at `theDescription`: `lean/LIMITS.md`, L57) and
  hands them to the compiler's theorem on `innerCompiledVerifier`, in the form
  `verifierAcceptingNoMoreThanBehindReadingAndParser_soundFor`
  (`lean/Johnson/Top/InnerCompiledVerifierByPublicReading.lean`); the soundness theorem on `verify`
  has no hypothesis beyond those in its statement, so nothing more is assumed by that road. A second
  theorem (`sound_of_verify_at_through_the_IOP`, `lean/E2E/SoundAsIOPAtFilesProofs.lean`) has the
  statement of the soundness theorem on `verify` to the letter, with no further hypothesis, and is
  proved through soundness as an IOP, not through that theorem: it draws the three from soundness as
  an IOP and hands them to the same theorem of the compiler. It adds little assurance: the three
  parts of soundness as an IOP are themselves proved from one lemma of the first proof and from
  sisters of the other two, which rest on the same theorems: it is the same proof by another road,
  no second derivation. The law on the out-of-domain point as it is made from hash answers is
  proved, by one lemma that both proofs use (`entryFull_seedLawK`,
  `lean/OnBytes/Flat/RecordSeed.lean`); soundness as an IOP gives nothing of it. The second theorem
  does not go through `compile` (`lean/Johnson/Face/Compiler.lean`).

### The theorems on codes

The proof rests on theorems on Reed–Solomon codes, above all mutual correlated agreement below the
Johnson radius. As typed in this repository they are proved in this library, not assumed, from files
adapted from ArkLib and Mathlib (`lean/LIMITS.md`, L15). That says nothing on whether the published
theorem (Theorem 4.6 of ePrint 2025/2055, the full version of a paper published at STOC 2026) is
formally verified. Their match to the published statements has not been independently compared.

The soundness proof runs by list decoding up to (just inside) the Johnson radius. Where a sampled
oracle message is committed at a radius of at least half the code's distance, its Merkle root fixes
only a short list of codewords, and the out-of-domain sample picks at most one of them, but for a
counted chance of a clash that the bound pays for. That the proof takes this road is read from its
text and from the list of what the compiled theorem depends on; no theorem says it. At all written
pairs of shape and radius of the proof file the radius is at least half the distance (where a
stage's rows lie in two codes, the smaller of their two distances): theorems on the written numbers:
`lean/LIMITS.md`, L89. (`lean/LIMITS.md`, L15, L81.)

## How to check it

First install Lean: `lean/CHECKING.md`, "Before you start" and steps 2 and 3 (elan; Lean 4.29.1,
which `lean-toolchain` pins). As with any Lean project, a build runs code from this repository as
your user. Then, from the repository's top (the second line fetches Mathlib's compiled files:
`lean/CHECKING.md`, "Before you start" and step 3):

```
cd lean
lake exe cache get
LEAN_ABORT_ON_PANIC=1 lake build Johnson.Goal.Skeleton.SoundOfVerifyAt > .lake/sound_of_verify_at.log 2>&1; echo "exit status: $?"
grep -A1 "sound_of_verify_at' depends" .lake/sound_of_verify_at.log
```

This compiles about 16,000 files of this library. The answer must read
`'VerifierAndGoals.AtTheName.sound_of_verify_at' depends on axioms: [propext, Classical.choice,
Quot.sound]`, with nothing else in the brackets, and the exit status must be 0. The theorems on the
executable form are checked the same way: build `Johnson.PVR.SoundOfTheForm` and
`Johnson.PVR.SoundOfTheFormEvents`; each file ends by asking Lean for the axioms of each of its
theorems by name, so search that build's log for `PV.Ride.theForm_eq_verify` and
`PV.Ride.sound_of_the_form_events`. What is proved of the Lean committer is checked the same way:
build `Johnson.Bind.Cpp.NoTwoOpeningsAtLive` and `Johnson.Bind.Cpp.SoundAtCommittedExact`, which
have `Johnson.Bind.Cpp.TheTie` and `Johnson.Bind.Cpp.SoundAtCommitted` beneath them (by the import
lines; untried), and, for the theorems at the library's written copies,
`AtFullSide.Bind.LiveAtNamed`, a module of the side library ("Its reach"); each of the five files
ends by asking Lean for the axioms of its theorems by name (`Johnson.Bind.Cpp.JoinControls`, for
`hollow_meets_join`, is built apart). The six theorems at the top of this page are checked the same
way: build `AtFullSide.Face.TheSixLines`, a module of the side library ("Its reach"), which ends by
asking Lean for the axioms of each of them by name (the command: `lean/CHECKING.md`, "The six
theorems, and eight more"). The theorems of "The final statement's six fields" and "The three
statements at one protocol" are checked the same way: build
`AtFullSide.Face.TheFinalStatementOneBitHolds` and `AtFullSide.Face.TheThreeAtTheFiles`, modules of
the side library ("Its reach"), which have the files of the others beneath them (by the import
lines), but for `E2E.SoundAsIOPNumbers`, `Johnson.Face.ExecutableVerifier`,
`AtFullSide.CompletenessAndZeroKnowledge.LifeNumberAt135`,
`AtFullSide.CompletenessAndZeroKnowledge.RejectsTheEmptyForm`,
`AtFullSide.E2E.CompleteWhereTheWorstCaseCheckPasses`,
`AtFullSide.E2E.CompleteWhereSomeWorstCaseCheckPasses` and
`AtFullSide.Face.ExecutableVerifierIsLeanVerifier`: build these by name too; each ends by asking
Lean for the axioms of those of its theorems that this page names. The two modules named first end
by asking Lean for the axioms of `VerifiableInference.Compilation.theFinalStatementOneBitHolds`,
`VerifiableInference.Compilation.theFinalStatementBothHold` and
`VerifiableInference.Compilation.threeAtFiles_in_use`, among others. A build alone does not fail on
an unfinished proof or a new axiom: that answer is what shows that none lies beneath this name. It
reads the compiled files and re-checks nothing. The library's own whole check is `scripts/check.py`
(`lean/CHECKING.md`). The library's full check sends the modules of the side library `AtFullSide/`
and of `ShapeLines/` through the kernel's second pass by another call than the rest, each at the
stack at which Lake compiles it (`lean/CHECKING.md`). A whole run of it over this repository's Lean
files passed at every step; its last line says that no theorem got a verdict on binders or on
`Classical.choice` (the whole line, and what the check doesn't cover: `lean/CHECK-RESULTS.md`).

But for the independent checker's passes on the soundness theorem on `verify` and on `sound`,
`repliesFit` and `refusedHandsOutNoProof`, none of what follows in this section was run over this
repository's files as they stand. An independent proof checker (a second kernel) reads text that
this project's own exporter writes, no run shows it refusing a wrong proof, and for four theorems
(three about the commitment) it gave no verdict (`lean/GAPS.md`, 18 (b); `lean/LIMITS.md`, L25,
L80). Over a build of this repository's files (that the compiled files that these passes read were
that build's is known from a report alone; Lean's own files were not compared with a list of
checksums) the independent checker has accepted the soundness theorem on `verify`, with every
declaration beneath it, and nothing that does not lie beneath it, in a pass on that theorem's export
alone (`lean/CHECK-RESULTS.md`). So these pages tell of no theorem of this repository, but that one,
those on which it rests, and `sound`, `repliesFit` and `refusedHandsOutNoProof` with theirs, that
has more than Lean's own kernel over this repository's files: not the results on hiding
(`lean/LIMITS.md`, L62 to L65), not the other three of the six, not the theorems on completeness and
zero knowledge.

## The executable form, and how to run it

`verify` as typed cannot be executed. Lean marks it noncomputable. Its executable form can
(`lean/Johnson/PVR/RideThe.lean`; in the Lean files' comments: the step-by-step form). Put any
function on bytes with 32-byte answers (a real call that returns 64 counts as two) in the hash
function's place (the real one has them: `Fmt.size_oracle`): at all public files and on every parsed
proof file the form's verdict is `verify`'s decision (`PV.Ride.theForm_eq_verify`,
`lean/Johnson/PVR/SoundOfTheForm.lean`). And a soundness statement of its own,
`PV.Ride.SoundOfDecision`, is proved of the form's decision, the hash function drawn at random and
handed to the form as functions on bytes from which it is read back, at the same bound and under the
same three hypotheses, in scope, read and exact match (`PV.Ride.sound_of_the_form_events`,
`lean/Johnson/PVR/SoundOfTheFormEvents.lean`).

Where these functions answer with 32 bytes, "the form is sound" and "`verify` is sound" are one
statement (`PV.Ride.soundOfDecision_form_iff`). The library's own functions (`Run.oOf`) do; they are
defined with the axiom of choice, have no code, and are not the real hash function. For others the
statement bounds a lower integral, since measurability is not shown. (`Run.oOf` stands in the
theorem alone: it is handed to the form and is no part of it.) These are statements about the term's
value, not about whether or when an evaluation ends. The form runs `verify`'s tests on the public
files itself, so an accept is an accept with those tests passed.

Proofs aside, which the compiler erases, none of the library's own definitions beneath that form
names the axiom of choice, is marked noncomputable by Lean, or is replaced by other code when
compiled, by `implemented_by` or `extern` (no theorem). For replaced code a file of the library
holds it at every build: `lean/Johnson/PVR/ProgramGuard.lean` walks all constants that
`PV.Program.run` uses, by the kernel's terms, and does not compile if the compiled code of one of
this library's is not made from the definition that the kernel checked. For choice and noncomputable
it is the finding of two searches in Lean, by programs that are not part of this repository, over a
build of Lean files that differ from this repository's; that Lean compiles the form and does not
mark it noncomputable is shown by the build itself.

**To run it.** One command, `lean-verify`, runs the executable form, inside Lean, on the C++
prover's proof files, which a small parser cuts for it (the command line, a sample call and what a
call costs: `tools/lean-verify/README.md`; in one run a call that ended in an accept took 1,287 to
1,532 seconds, 35 calls side by side on one machine, over Lean files that differ from this
repository's). `lean-verify` (`tools/lean-verify/lean_verify.sh`) reads the files, puts the real
hash function in, calls the form and prints its verdict. Any verdict that the function which it
evaluates gives is `verify`'s value at the claim that `claimOf` read
(`PV.Program.verdictOf_is_verify`, `lean/Johnson/PVR/Program.lean`); wherever that claim reads, a
verdict is given (`PV.Program.verdictOf_eq`, `lean/Johnson/PVR/ProgramTotal.lean`). No theorem
speaks of `run` (`PV.Program.run`, in the first of these files, which reads the files, prints the
claim and evaluates that function), of compiled code, or of whether `claimOf` cuts your files as the
format page means.

An accept's line says what the script saw in the parameter file: "VERDICT: ACCEPT (exact match)", or
"VERDICT: ACCEPT (under the files' policy …; NOT exact match …)". It gives a verdict, with exit code
0, in both cases; the soundness theorem on `verify` speaks of the first alone, and of the second the
theorem under a policy, which alone is weak ("The theorem under a policy: other acceptance
policies", "Alone it is weak"). It runs with a helper library that Lean's own compiler makes from
this repository's modules (with the C compiler that Lean's own release brings, it is untried).
`lean-verify` is a command of this repository, not a stand-alone program: no stand-alone verifier
program is proved sound. The verifier program's text under `lean/OnBytes/` (its Main and Shell),
which follows cp_verify's source, is not `verify`, and nothing is proved of its soundness.

## What has been run

One Lean file, with one definition and four theorems, which nothing else imports, was added after
the runs reported here and checked on its own. Three of the check script's pinned values were
changed and three of its stored lists were extended for it; nothing else in the script or the lists
changed. (`lean/CHECK-RESULTS.md`.)

At full size and on synthetic weights the command `lean-verify`, which runs `verify`'s executable
form inside Lean, accepted all 47 honest proofs among the 109 calls of the reference run that are
told here, in a call that ran to its end (calls outside this run that did not: `lean/GAPS.md`, 14,
"What can be repeated (l)"): 47 of 47. It has also accepted 41 further proofs, of the timed runs as
reported, on synthetic weights, none of them among the 47 (`lean/CHECK-RESULTS.md`). These calls
were made over this repository's Lean files; every file of the command and of the parser outside
`lean/` that the traced calls beside them opened has this repository's checksum (none of the run's
own calls was traced: `lean/GAPS.md`, 14, "Which programs (k)"; `lean/CHECK-RESULTS.md`). Of the 47:
45 at exact match; 2 under the stored tolerant policy, where an accept says less; 42 from a prover
built from sources that differ from this repository's, by report and not by a check
([docs/limits.md](../docs/limits.md#the-timed-runs); `lean/GAPS.md`, 14, "Which programs (k)"); at
essentially two configurations, most requests of one shape and most proofs of one next token (39
requests, at 7 commitments). All of them are proofs that the C++ verifier accepted (which build:
`lean/GAPS.md`, 14, "Which programs (k)"). These 42 are a part of what that prover made, taken by
rules fixed beforehand: 41 of the 723 that it made at exact match, and one under the stored tolerant
policy (that it made 723, and the rules, are by report and not by a check). The proofs from the runs
on real weights were checked by `cp_verify` alone (what ran, and how each proof was checked:
[docs/limits.md](../docs/limits.md#the-timed-runs); which builds:
[docs/limits.md](../docs/limits.md#what-was-run-on-these-programs)); none has been put to the Lean
verifier (`lean/GAPS.md`, 57).

At full size 57 lying proofs were tried (24 distinct proofs for 21 false replies to one request; 33
carrying a planted lie, for the true replies to three requests): none was accepted by either
verifier (which build of the C++ verifier: `lean/GAPS.md`, 14, "Which programs (k)"; the C++
verifier judged them in other runs; the Lean verifier's parser refused 3 outright, and a no-verdict
is not a rejection); no proof of a false claim carrying the second kind of lie has been put to
either verifier at full size in the runs this page reports; one commitment, synthetic weights, exact
match, lies of a few kinds, every rejection at one verifier step; no prover built to search for
forgeries; other attacks mostly at small sizes. Apart from that run, one malicious committer's false
copy's file at full size was tried and rejected through the executable form of `verify`, in a run
over Lean files that differ from this repository's, not repeated over this repository's files
(`lean/GAPS.md`, 33). The test programs that made the lying proofs are not in this repository, so
those trials cannot be repeated from it. In another run, over Lean files that differ from this
repository's, inside that step all 24 were refused at one and the same place, and no run shows the
clipped-gap policy's own limits rejecting anything. As controls, an honest proof was set five times
beside a claim that is not its own: four times beside another token of the reply (three times
another next token, once another last token of a reply of 1,001), once beside another commitment ID.
All five were rejected (controls of one shallow kind). None was put to the command under a tolerant
policy.

A proof file does not show which program made it: that 42 of the 47 honest proofs came from the
prover told above, and the lying ones from test programs, is how the runs were set up, not something
a verifier can check. "Honest", "lying", "true", "false" and "a planted lie" are the labels that the
files came with: no run decided them. Nor are the 109 calls on these proofs blind: each had been
made before on the same input files.

By a theorem on the executable form (`PV.Ride.verdictThe_is_theDescription`: at any function in the
hash function's place, a verdict that the form gives is `verify`'s decision) each verdict in a run,
accept or reject, is `verify`'s own, at the real hash function, as far as Lean's evaluator, compiler
and runtime, the helper library and the C compiler that builds it, and the file that drives the run
are trusted. Of the 109 calls told above and those on the 41 further proofs, that is this
repository's `verify`; of the other runs, `verify` as it stood at those calls (`lean/GAPS.md`, 26).
The kernel checks proofs, not runs. A run also trusts Lean's compiler, evaluator and runtime, a C
compiler, and some constants of Lean's own library and the packages, none of this library's, whose
compiled code is not the kernel-checked definition. This is testing, not proof.

The two stored examples are `examples/full-size/` (exact match) and
`examples/full-size-clipped-gap/` (a tolerant policy); their public files are "the two stored sets".
`lean-verify` ships, so a reader can repeat with it, from this repository (with Lean and the
packages as a reader gets them this is untried: `lean/GAPS.md`, 45 (e)), the accept of the first
stored example's proof and, under its tolerant policy, of the second's (an accept there says less
than at exact match), and two rejections: of that proof beside another commitment ID, and beside
another last token of its reply. (What the second example's output is: "The theorem under a policy:
other acceptance policies", "What the stored tolerant policy gives".) Only these two proofs are in
this repository: the other honest proofs, the altered files and the lying proofs are not, so the
rest cannot be repeated from it. The runs told on this page were made on this project's own
machines, their logs have not been independently reviewed, and none has been repeated elsewhere
(`lean/GAPS.md`, 18 (g)).

### Altered proof files that leave the claim untouched were accepted

One input at a time was altered: the claimed reply (5), a public file (5), the parsed key file (8),
the parsed copy's file, which holds a further encoding of the weights (6), or the parsed proof file
(17). Of these 41 altered inputs the executable form rejected 32, and all five that altered the
claimed reply; the nine parsed files that it accepted leave the claim untouched: soundness allows
that, and that a proof cannot be altered is not claimed. Each of the nine accepted altered inputs is
an alteration of the parsed proof file, made behind the proof parser (eight at exact match, one
under the tolerant stored policy), with bits turned in Merkle-path entries that the verifier's walk
does not take (by reading and by runs, not proved); claim, commitment and public files were
untouched. So no claim false by its own policy was accepted: the nine altered the proof file, never
the claim. Two of the nine were accepted where a rejection was expected.

At four matched places in one honest proof (not common files: the raw proof with one digest altered,
the parsed file with the matching entry turned) `cp_verify` and the form both rejected at one, and
they parted at three: where three digests that the prover sent were altered, `cp_verify` and the
parser rejected the raw proof, and the form accepted the parsed file: so the two verifiers part on
these files. The `cp_verify` and the parser used there were built from sources that differ from this
repository's (`lean/GAPS.md`, 14, "Which programs (k)"). The two verifiers were given the input in
different forms, and there none of these altered proofs reached `verify`, since that parser refused
them; no input is known at which `cp_verify` and the road that ships, from the raw proof through the
parser to `verify`, part (`lean/GAPS.md`, 66). These 41 were put to the executable form directly (31
of them on altered parsed files), over a build of Lean files that differ from this repository's and
not through this repository's command (five of them to a copy of the form's file that differs from
this repository's). `lean-verify` parses by itself and takes no parsed file, so it cannot play the
31 that alter one. The four matched alterations were made once, in one of the runs that these 41
count.

## What the commitment gives, as proved

For an illustrative committer written in Lean that models one part of `cp_commit` (no theorem ties
the two), Lean proves three things of its commitment: the extracted weights are the ones that
committer put in (correctness of extraction), its commitment cannot be opened to weights other than
the extractor's (binding of the commitment in the opening form, also called extractability of the
commitment), and it has no two openings — at files in scope that are read and where
`protocolDataWellFormed` passes (the tests on the public files that the proof needs; `verify` makes
further ones), as it does, by theorems of a side library, at the library's written copies of the two
stored sets of public files. (`Bind.Cpp.extractsCommitted`, at an error of about 2^-89 at that
committer's query count; `Bind.Cpp.bindsAt`, at about (t + 2^23)/2^124 after t queries;
`Bind.Cpp.noTwoOpenings_live`, at twice `bindsAt`'s error; at the library's written copies of the
two stored sets of public files their premise is met by `AtFullSide.Tie.premises_zFull` and
`AtFullSide.Tie.premises_zGap`.) They are not had for nothing: a committer that does not read the
weights fails all three, by theorems (`Bind.Cpp.blindTwin_fails` for the running committer fed a
table of zeros; for any such committer within the committer's query count, `blindDoesNotBind`,
`blind_twoOpenings`, `blind_extracts`, `lean/Johnson/Bind/Cpp/Controls.lean`).

And soundness after an honest commitment is proved of it: after that committer's commitment to
weights w (fixed, like the files, before the hash function is sampled), an output that `verify`
accepts meets the files' policy at w, at all files in scope that are read (also where
`protocolDataWellFormed` fails, because `verify` then rejects everything), except on an event of
probability about 2^-88 + p/2^124, on average over the committer's seed, after p queries of the
prover, who is given that seed, the committer's own 2^35 queries being charged
(`Bind.Cpp.soundAtCommitted_own`, `lean/Johnson/Bind/Cpp/SoundAtCommitted.lean`). At exact match
that output is the model's output at w, and not empty, at the same error
(`Bind.Cpp.soundAtCommitted_exact_nonempty`, `Bind.Cpp.soundAtCommitted_exact`,
`lean/Johnson/Bind/Cpp/SoundAtCommittedExact.lean`). (In the definition's terms:
[TERMS.md](TERMS.md); its limits, entry by entry: `lean/LIMITS.md`, L61.)

**The limits.** All of this is proved of that Lean committer, not of `cp_commit`, to which no
theorem ties it (the two were compared in values on the small example, over Lean files that differ
from this repository's and with a `cp_commit` built, by the dates and not by a comparison, from
sources that differ from this repository's); and the system in the statement of the soundness
theorem on `verify` has a constant committer (a committer that returns one constant whatever the
weights, and so commits to nothing; the committer of the six lines is another: the one that
`compile` makes (`lean/Johnson/Face/Compiler.lean`), which encodes the weights and hashes the key)
where its honest committer goes, so of that system itself none of it can be stated with any content;
`compile flashProveAtFiles`, which has the same verifier, has a committer of its own ("The final
statement's six fields", 4). And no theorem says that `verify` accepts any proof under the
illustrative committer's commitment (it makes no key file, and no honest prover is written for it),
nor that a given commitment is of that committer's make; so soundness after an honest commitment
forbids something only beside an accept, and its form is no test of a committer: the constant
committer meets it too (`Bind.Cpp.hollow_meets_join`). At full size the Lean committer of this
section cannot be run (by the file's own count, about 2^72 multiplications); it has been run at
small shapes alone (outside the build: over Lean files that differ from this repository's), where
none of these theorems is stated. No test of these properties has been run. Soundness, binding,
completeness and zero knowledge of one committer, prover and verifier stand together in one Lean
value ("The final statement's six fields").

## Completeness and zero knowledge: what is proved for the protocol, and what is not

**How these theorems stand.** The theorems named in this section and in the next two are part of
this repository's Lean build, and for each Lean prints no axiom beyond its three standard ones
(`propext`, `Classical.choice`, `Quot.sound`). Those whose files lie under `lean/AtFullSide/` stand
in the side library, the others in the main library. The side library rests on a third,
`lean/ShapeLines/`: these two need larger thread stacks and a large machine to build
([CHECKING.md](CHECKING.md)). The independent checker has been run, on the export of the soundness
theorem on `verify` and, by name, on those of `sound`, `repliesFit` and `refusedHandsOutNoProof`, as
the exporter writes them over a build of this repository's files; what it accepted:
[CHECK-RESULTS.md](CHECK-RESULTS.md). The Lean verifier's reference run has been made over this
repository's Lean files (what was run, and what came of it: [CHECK-RESULTS.md](CHECK-RESULTS.md)). A
whole run of the library's full check over this repository's Lean files passed at every step; its
last line says that no theorem got a verdict on binders or on `Classical.choice` (the whole line,
and what the check doesn't cover: [CHECK-RESULTS.md](CHECK-RESULTS.md)).

- **Completeness.** For one commitment and one well-formed request, if the model's result is the
  claimed tokens, the honest proof is accepted, except with probability at most 2^-40, over the hash
  function and the committer's and the prover's coins. (`FinalComplete`, "The final statement's six
  fields", 2.) Completeness covers well-formed requests on which the model has a result and the
  claimed output is that result. Such requests are called served. Where the model has no result it
  says nothing. That such requests exist is shown only at made-up weights; at some valid weights, at
  the settings that the stored public files give, none can be served
  (`canServe_nowhere_atHaltingWeights`); and no request to a real model is shown to be among those
  that can. Before hashing: "The three statements at one protocol".
- **Zero knowledge.** Zero knowledge holds against an honest verifier in the IOP and, after
  compiling, against any verifier within a bound on its hash queries and replies, on one copy of the
  table; the simulator's running time is not modelled. The hash function is drawn at random. Take
  any public files that the verifier takes, whose policy is exact match and which pass the test
  `protocolDataWellFormed` on the public files, which the verifier makes too; the stored full-size
  files are such a set. Then there is one simulator, fixed before the weights, which may depend on
  the public files. For all weights and for any verifier that queries the hash function classically,
  with no bound on its running time: the verifier gets one commitment and then, in any order and
  adaptively, asks up to 2^64 hash queries and up to 688,127 replies, each at a request, well-formed
  or not, that is picked from all it has seen so far. What it sees with the honest Lean committer
  and prover (the commitment, the replies, the hash answers, its own coins) is within 2^-157 +
  688,127 · 2^-174, which is below 2^-154, in total variation, of what the simulator makes. The
  simulator gets each request, the largest number of replies and, of the weights, one bit for each
  request: served or refused (in the corollary, one label for each request: served, failed or other
  tokens). (The corollary: "The final statement's six fields", 3.) It makes the commitment and the
  replies, and it answers the hash queries in the hash function's place, never one query in two
  ways. The probability is over the hash function, the committer's and the prover's coins and the
  verifier's own. In the error, 2^-157 is what the hashing costs at these numbers, and 2^-174 bounds
  the chance, before hashing, for a served request, over the verifier's messages that pass the
  proof-of-work tests, that the online prover stops for a reason that depends on its secrets (it is
  counted once for each reply); for the offline and the link prover that chance is 0. A nonce search
  that runs out is inside what is simulated: it shows as the empty proof (`noProofForm`: a form all
  of whose parts are empty) at a served request, which looks like the reply to a refused request; in
  the corollary, as the empty proof beside the label "served". (`FinalZeroKnowledgeOneBit`, "The
  final statement's six fields", 3.) (Which files these are: "Its reach".)
- **Its bounds.** One commitment with one copy of the table, one request per proof, exact match. The
  committed table of weights is stored encoded, with random masks, and each proof opens some of its
  columns. One encoding bears only so many openings before its masks are used up: 44,040,191
  columns, enough for 688,127 replies. To serve more under one commitment, the protocol makes
  further encodings of the same table ("copies"), each tied to the commitment's key file by a link
  proof. The zero-knowledge line is about a prover with exactly one copy, and that number sits
  inside the value `honestProversAndSettings`, in its settings. The bit is revealed, not hidden: it
  depends on the weights, and over many requests the bits tell what the model answers (in full:
  lean/LIMITS.md, L93). Nothing in the prover counts replies, and beyond these numbers the line says
  nothing. It says nothing of what the public files themselves tell of the weights, or of timing:
  it's about the Lean prover as a definition, default values included. The line says nothing of what
  the public files themselves tell of the weights, of what is published beside the commitment, or of
  timing. The simulator's running time isn't modelled. The verifier has no hash query before the
  commitment, and the weights and the public files are fixed before the hash function is drawn. A
  second, fixed hash function inside the format isn't treated as random. In the same Lean value
  stand soundness, binding and completeness of the same committer, prover and verifier, so the line
  isn't met by a prover that hands out nothing. One bit per request is revealed (served or refused),
  and it depends on the weights. A service that chooses to say "failed" reveals one label of three
  in its place (served, failed or other tokens). The numbers on zero knowledge are statistical
  distances, not a security level. Lean's theorem on zero knowledge is for exact match: under a
  clipped-gap policy no Lean theorem covers what a whole proof reveals. A prover that serves such a
  policy also answers requests whose output is not the model's, which the Lean prover of these
  theorems refuses, and there the answer itself tells how far a token lies from the model's choice.
- **The honest prover.** The honest prover in these theorems is a Lean definition, not the CUDA
  prover. Both theorems are about the Lean prover exactly as written, default values included.
  Whether that text is the prover that the protocol's authors mean, and that the CUDA prover
  implements, is for the audit of the definition. The definition isn't a program: among other things
  it obtains the model's trace by a non-constructive choice. That Lean's description is the protocol
  that the programs run is not proved; it is tested.
- **The limits.** Both are at the exact-match policy, with fresh random masks, for one commitment
  and one request per proof, not for batches. Batches are what the programs serve: all that is
  proved here is for one request per proof. Lean has no statement on hiding for more than one
  commitment. Before any hashing, with fixed-message provers (provers that send the same messages
  whatever the weights, and so show nothing of them; at public files in use the protocol's honest
  provers are others) and fresh random values, what is shown of a committed table (its out-of-domain
  answers and its opened columns) has the same distribution whatever the weights, within a budget of
  44,040,191 opened columns over the table's whole life. The proof has no slack: at one column more
  the statement for a single table, from which this is proved, fails (`not_hidE_own`); that the
  result itself fails there is not proved. Nothing in Lean keeps count of the columns that a table
  has opened. The programs keep that count, in a file for each table, and behind their counter no
  Lean theorem stands. That 219 random values are enough for the 219 positions that a proof shows of
  a row that the prover keeps from one segment of a request's proof to the next (one example of a
  count that has no slack) is argued on paper only; no Lean result in this library speaks of that
  number (`lean/GAPS.md`, 15 (10)). (Attacks and tests on hiding, and their results, for the
  protocol and for the programs: [guide/weight-hiding.md](../guide/weight-hiding.md).) The programs
  derive their masks from a secret seed, which no Lean theorem covers. (Entry by entry:
  `lean/LIMITS.md`, L62 to L66. On the provers' own messages a result on hiding counts only beside
  completeness of the same provers: L63, L64; `lean/GAPS.md`, the appendix to 15; 75.)
- **Beside these.** Results on parts of both proofs, as reductions or with fixed-message provers,
  stand in the library too (`completeOn_last`, `linkFits_at`, `privacyWithNumber_description`,
  `linkLaidAtOnce`, `whole_atFiles`, `homeExactAt`): `lean/LIMITS.md`, L27, L62 to L66.

## The three statements at one protocol

Before any hashing: about one protocol; completeness and zero knowledge about one triple of provers
in it. (`lean/E2E/ThreeAtOneProtocol.lean`.) At given public files the protocol is one Lean term,
`AtPublicFiles.AtFiles.protocolAtFiles files` (`lean/E2E/BridgeJoinAtFiles.lean`): an interactive
oracle proof (IOP) in three parts. Offline: the proof in the key file, on the committed table. Link:
from a further table (a copy) to the first. Online: the proof for one request, on that further
table. Every committed table has an out-of-domain sample, offline and online: the verifier names a
seed (the out-of-domain point), and the sample is the seed with the answers at it; the masking words
that the provers send beside them carry none, by design. `protocolAtFiles files` is the object in
the input at which `verify` calls the compiled verifier (`object_description`,
`lean/E2E/DescriptionTie.lean`). (Of `protocolAtFiles Z` to the letter:
`protocol_is_the_compiled_verifiers`, `lean/E2E/ThreeAtOneProtocol.lean`.) The honest provers are
`AtPublicFiles.AtFiles.HonestTerm.honestProvers files (thePartsAt files)`
(`lean/E2E/TheHonestProver.lean`, `lean/E2E/KeyArgumentsAt.lean`). These statements speak of this
triple with its online prover made to refuse a request that is not served
(`VerifiableInference.Compilation.theProvers`,
`lean/Johnson/Face/HonestProversWithCompiledPart.lean`). The provers' definition uses the verifier's
block functions.

```
structure ThreeAtOneProtocol {Index Request : Type} (L : HolographicProtocol Index Request) (provers : HonestProvers L)
    (work : PartsWork L) (copyNumberIn : ℕ → Plains L.onlineBatch.loc.shape → Bool)
    (served wide : Index → Request → Prop) (inRange : Index → Prop)
    (offlineMarks : RoundSplits L.offline.shape) (offlinePlaces : ℕ) (linkMarks : RoundSplits L.link.shape)
    (linkPlaces : ℕ) (roundBound completenessError : ℝ≥0∞) (budget : Budget) : Prop where
  sound : L.IndexKnowledgeSoundIOP wide offlineMarks offlinePlaces linkMarks linkPlaces roundBound
  complete : CompleteIOP L provers work copyNumberIn served completenessError
  zeroKnowledge : ∃ simulators : RunSimulators L,
    HonestVerifierZeroKnowledge work provers simulators inRange served budget
  servedIsTrue : ∀ index request, served index request → wide index request

abbrev ThreeAtFiles (Hs : HonestProvers (protocolAtFiles Z)) (offlineStops linkStops onlineStops : ℝ≥0∞) : Prop :=
  ThreeAtOneProtocol (protocolAtFiles Z) (proversAtFiles Z hr Hs) (workAtFiles Z) (copyNumberAtFiles Z)
    (ServedRequest committerCoinCountLessOne Z hr) (relationAtFiles Z) rangeAtFiles (filesAt Z).annT (offlinePlaces Z)
    (filesAt Z).annL 1 ((2 : ℝ≥0∞)⁻¹ ^ 128) completenessTarget
    (budgetAtFiles offlineStops linkStops onlineStops)

theorem threeAtFiles_in_use (files : PublicFiles) (parameters : Inst.Model.ScalesAndPolicy)
    (inUse : FilesInUse files parameters) :
    ThreeAtFiles files inUse.read (HonestProvers.ofThreeProvers (honestProvers files (thePartsAt files)))
      0 0 (ENNReal.ofReal ((2 : ℝ) ^ (-174 : ℝ)))
```

- **`sound`.** Soundness at this level, round by round, with a named extractor of the weights. By
  the name `IndexKnowledgeSoundIOP` no equivalence with a printed definition of round-by-round
  knowledge soundness is claimed. (`soundAsIOPAtTheProtocol`, `lean/E2E/SoundAsIOPAtFiles.lean`,
  `lean/E2E/SoundAsIOPAtFilesProofs.lean`.) As a probability: at most 67,391 × 2^-96, below 2^-79.
  (`probabilityInScope`, `lean/E2E/SoundAsIOPNumbers.lean`.) This is before hashing, and not the
  compiled figure: it is what round-by-round counting yields when proof of work is treated as
  challenge bits instead of being charged to the adversary's hash queries; after compiling, the
  figure is finalSoundnessError's.
- **`complete`, `zeroKnowledge`.** Completeness at this level, at the protocol's honest provers on
  served requests, with error at most 2^-41, over the prover's coins and the challenges that pass
  the proof of work; and honest-verifier zero knowledge. These definitions are this library's own,
  and no published definition word for word: an auditor should read them first. In ordinary words,
  with their limits: `lean/LIMITS.md`, L90, L91, L92. Two of these limits: at this level one bit for
  each request is not hidden (whether it is served, which depends on the weights); and a statement
  of this form is met by a prover that shows nothing, so it counts only beside completeness of the
  same provers. (`CompleteOnServedRequests`, `lean/E2E/CompleteAsIOPAtFiles.lean`;
  `ZeroKnowledgeOnServedRequests`, `lean/VerifiableInference/Final/ZeroKnowledgeAtTheProtocol.lean`;
  `HonestVerifierZeroKnowledge`, `lean/VerifiableInference/Final/ZeroKnowledgeBeforeHashing.lean`.)
  Their theorems at the files: `completeOnServedRequests_at_every_files_in_use`
  (`lean/AtFullSide/E2E/CompleteAtEveryFilesInUse.lean`; beneath it `complete_at_the_files`, of
  which `complete_in_scope` is a corollary, `lean/AtFullSide/Honest/CompleteAtTheFiles.lean`) and
  `zkOnServedRequests_inScope` (`lean/AtFullSide/E2E/ZeroKnowledgeFromTheRows.lean`). The two name
  the provers by two terms, and the two terms are the same by unfolding one definition
  (`termLetters`).
- **The three together.** The theorem that binds them, about one protocol, with completeness and
  zero knowledge about one triple of provers in it, at every set of files in use.
  (`threeAtFiles_in_use`, `lean/AtFullSide/Face/TheThreeAtTheFiles.lean`.)

**What the one binder, the structure `ThreeAtOneProtocol`, does not give.**

- Soundness reads neither `provers` nor `work`. Its tie to the work bits stands outside the
  structure, in two theorems at the public files: `work_clears_as_soundness`,
  `work_passes_as_soundness`.
- The relations differ, as in the three statements: soundness stands at a wider relation, the other
  two at the served requests; the field `servedIsTrue` says that the one lies in the other.
- The numbers stand over different distributions and are not to be compared: `roundBound` (at the
  files 2^-128) is a share of all of one round's challenges, the bits of proof of work among them;
  `completenessError` is over the provers' coins and the challenges that pass the proof-of-work
  tests.
- Soundness is here in its form in parts: online it speaks of a batch, where the other two speak of
  one request; both read the one field `L.onlineBatch`. Its form for one whole run and its bound on
  a prover's probability are further theorems on soundness (`lean/E2E/SoundAsIOPAtFiles.lean`,
  `lean/E2E/SoundAsIOPProbabilityAtFiles.lean`) and no field here.
- Soundness reads more of `L` than its three verifiers (the decoder, the collisions, the extractor,
  the batch's numbers): none of these reads the object's honest provers; the theorem that carries
  soundness from one value of them to another is `soundAsIOPAtFiles_provers`
  (`lean/E2E/SoundAsIOPAtFilesProofs.lean`), not `verifiers_at_every_provers`.
- The field `zeroKnowledge` is the first part of the field `simulated` of
  `ZeroKnowledgeOnServedRequests`. That statement's claim on the whole life of a commitment and its
  fields «some request is served» and «two indices serve one request» are not in the structure.
- The general structure does not ask that `served` holds of anything: where it holds of nothing,
  `complete` says little.
- Of the online prover inside the triple no theorem of `lean/E2E/ThreeAtOneProtocol.lean` speaks:
  `offline_prover_inside` and `link_prover_inside` are of the other two (the offline and the link
  prover inside the triple are the honest provers' own).
- Nothing in the structure ties `L.encodeIndex` and `L.recOf`, which completeness and zero knowledge
  read, to the decoder and the extractor, which soundness reads: that the extractor returns the
  honest index from an honest table stands outside it.
- The clause on the whole life and the two guards (some request is served; two indices serve one
  request) are the zero-knowledge theorem's, not the binder's.
- At the interactive level the statements speak of indices in range; the index of any weights is in
  range, by a theorem beside them.
- **Zero knowledge alone.** A statement of this form can hold for nothing: a prover that sent fixed
  messages and refused what is not served, or that always stopped for a public reason, would meet
  it. What shuts that out is completeness of the same provers, so the two are to be read together,
  as about one triple of provers and one protocol (`lean/LIMITS.md`, L92). Comments in the files
  beneath these theorems speak of shares and letters of the proof's frame. These are premises of
  lemmas, which the closed theorem proves; none is a clause of its statement (`lean/LIMITS.md`,
  L91).
- These statements are about the Lean provers exactly as written, default values included, on served
  requests. Whether that text is the prover that the protocol's authors mean, and that the CUDA
  prover implements, is for the audit of the definition. The definition isn't a program: among other
  things it obtains the model's trace by a non-constructive choice.

(Entry by entry: `lean/LIMITS.md`, L88 to L92.)

## The final statement's six fields

Each of the six theorems is a theorem of its own in `lean/AtFullSide/Face/TheSixLines.lean`, and
[STATEMENTS.html](STATEMENTS.html) opens on them. Their statements, as the file has them:

```
theorem sound (setup : PublicSetup) : Sound (compile (flashProve setup)) finalSoundnessError

theorem soundAndBinding (setup : PublicSetup) :
    SoundAndBinding (compile (flashProve setup)) finalBindingError

theorem completeOnCanServe (setup : PublicSetup) :
    CompleteOn (compile (flashProve setup)) (CanServe (settingsOfRead setup.readParameters))
      finalCompletenessError

theorem zeroKnowledgeOnCanServe (setup : PublicSetup) :
    ∃ error : ℕ → ℕ → ℝ≥0∞,
      (∀ asked replies, asked ≤ finalVerifierQueries → replies ≤ finalReplyCount →
        error asked replies ≤ finalZeroKnowledgeError) ∧
      ZeroKnowledgeOn (compile (flashProve setup))
        (CanServe (settingsOfRead setup.readParameters)) error

theorem refusedHandsOutNoProof (setup : PublicSetup) :
    HandsOutNoProof (compile (flashProve setup))
      (fun weights request =>
        requestOutcome (settingsOfRead setup.readParameters) weights request = .refused)
      isNoProof

theorem repliesFit (setup : PublicSetup) :
    finalReplyCount ≤ onlineRunsPerCopy setup ∧
      (∀ reading, TableBudgetFits ((flashProve setup).settings reading).furtherCopies
        (onlineRunsPerCopy setup)) ∧
      WithinBudget (compile (flashProve setup)) honestQueryBudget
```

`setup` holds three public files, what the reader returns at them, and `FilesInUse`. `compile
(flashProve setup)` is `finalSystem honestProversAndSettings files settings` at these, by unfolding.
All six are proved in Lean.

`sound`, `soundAndBinding`, `refusedHandsOutNoProof` and `repliesFit` are points 1, 4, 5 and 6
below. `sound` and `refusedHandsOutNoProof` ask `FilesInUse`, which points 1 and 5 do not: they ask
`FilesTaken` (in scope, read so, exact match stated), not the test; `sound` is said at
`honestProversAndSettings`, and point 1 holds whatever the honest provers and settings.

`completeOnCanServe` and `zeroKnowledgeOnCanServe` are stated on the requests that can be served
(`CanServe`, `lean/VerifiableInference/CanServe.lean`) and whose output tokens are the model's.
`CanServe`: every token is in the vocabulary, the output is not empty, and the model has a value on
the whole window of 1,024 tokens. The last condition depends on the weights. `completeOnCanServe` is
equivalent to point 2 (`finalComplete_iff_completeOn`, `lean/Johnson/Face/Checks.lean`), and the
file draws point 2 from it (`completeAtWellFormedRequests`). From `zeroKnowledgeOnCanServe` and
`refusedHandsOutNoProof` the file draws point 3 (`zeroKnowledgeAtEveryRequest`), within the same
bound; that point 3 gives `zeroKnowledgeOnCanServe` back is not proved. What goes with the two
lines, in the file's own words:

- `completeOnCanServe`: **Completeness** as the general property CompleteOn
  (VerifiableInference/Steps.lean), at the requests that can be served. Nothing is said of a request
  outside CanServe, among them those where the model has no result, or of an output that is not the
  model's.
- `zeroKnowledgeOnCanServe`: **Zero knowledge** on the requests that can be served and whose output
  tokens are the model's (ZeroKnowledgeOn, VerifiableInference/MoreStatements.lean): its own
  simulator, which is handed nothing of the weights in the experiment. It may depend on the public
  files; what these tell of the weights is not counted. Whether a request can be served depends on
  the weights, and that is not hidden: the chooser of requests may know the weights and is the same
  in both experiments. It says nothing of a refused request by itself: with refusedHandsOutNoProof
  it gives zeroKnowledgeAtEveryRequest, within the same bar, in which the simulator is told one bit
  for each request: served or refused. One request to a proof and one commitment are covered, not
  batches. The bound is not a named function: the statement says that there is one, and that it
  stays at or below finalZeroKnowledgeError within the stated limits; ZeroKnowledgeOn takes it as an
  argument.

The limits under points 2 and 3 below hold of these two as well.

In the same file: `leanVerifier`, the compiled verifier with BLAKE2b: `leanVerifier setup` equals
`finalVerifierProgram` at that setup's files (`leanVerifier_eq`; "The executable verifier", below);
the first four lines at the stored files (`sound_stored`, `soundAndBinding_stored`,
`complete_stored`, `zeroKnowledge_stored`); the corollary with the label (`zeroKnowledgeWithLabel`);
and `rejectsEmptyProof`.

One structure, `FinalStatementOneBit`, at `honestProversAndSettings`, the honest provers and
settings, has six fields, points 1 to 6 below: `sound`, `binding`, `handsOutNoProof` and
`repliesFit`, of which the theorems `sound`, `soundAndBinding`, `refusedHandsOutNoProof` and
`repliesFit` are the cases at a public setup; `complete`, completeness in the equivalent form of
point 2; and `zeroKnowledge`, point 3, which follows from the lines above and is not proved to give
`zeroKnowledgeOnCanServe` back. `finalSystem honest files settings` is `compile (flashProveAtFiles
files settings (honest files settings))`. (`lean/Johnson/Face/FinalStatementOneBit.lean`, above
`lean/Johnson/Face/FinalStatement.lean`; `honestProversAndSettings`:
`lean/AtFullSide/Face/HonestProversAndSettingsValue.lean`; `compile`:
`lean/Johnson/Face/Compiler.lean`.) `compile flashProveAtFiles`'s verifier is
`VerifierAndGoals.verify`, this page's `verify`, at the description of the soundness theorem on
`verify` (`compile_flashProve_verify_eq`, `lean/Johnson/Face/FinalStatement.lean`).

```
structure FinalStatementOneBit (honest : HonestProversAndSettings) (zeroKnowledgeError : ℝ≥0∞) : Prop where
  sound : FinalSound honest
  complete : FinalComplete honest
  zeroKnowledge : FinalZeroKnowledgeOneBit honest zeroKnowledgeError
  binding : FinalSoundAndBinding honest
  handsOutNoProof : FinalRefusedHandsOutNoProof honest
  repliesFit : RepliesFit honest
```

At public files that the verifier takes, at the exact-match policy; all but soundness and the reply
also ask that the files pass the test on the public files (`FilesInUse`). One such set is known: the
stored full-size files (`filesInUse_stored`). That set is a value written in Lean
(`VerifierAndGoals.storedPublicFiles`), tied to no file on a disk ("Its reach"). `compile
flashProveAtFiles` is short for `finalSystem honestProversAndSettings files settings`.

1. **`sound`.** Under a random hash function, an output that is not that of the weights that an
   extractor reads off the commitment and the committer's queries is accepted with probability at
   most finalSoundnessError (about q/2^124 + 2^-101 after q hash queries). The extractor is a
   function, not shown computable. (`finalSound`, `lean/Johnson/Face/FinalSoundProof.lean`.)
   `finalSound` rests on `VerifierAndGoals.AtTheName.sound_of_verify_at`, the soundness theorem on
   `verify`, whatever the honest provers and settings.
2. **`complete`.** For one commitment and one well-formed request, if the model's result is the
   claimed tokens, the honest proof is accepted, except with probability at most 2^-40, over the
   hash function and the committer's and the prover's coins. (`finalAtT1_filled_withRoom`,
   `lean/AtFullSide/E2E/TheCompiledStepFilled.lean`.)
3. **`zeroKnowledge`.** A simulator that may depend on the public files and is told, of each
   request, well-formed or not, only one bit (served or refused) makes the commitment, the replies
   (each a proof or the empty proof) and the hash answers; for one commitment with one copy of the
   table, up to 688127 replies and 2^64 queries, its view is within the error of the real one.
   (`finalZeroKnowledgeOneBit_value`,
   `lean/AtFullSide/CompletenessAndZeroKnowledge/OneBitAtHonestProversAndSettings.lean`.) No
   statement bounds what many bits reveal together. As a corollary (`finalZeroKnowledge_of_oneBit`),
   for a service that chooses to say "failed": the same at every well-formed request, with one label
   for it (served, failed or other tokens) told to the simulator and shown beside each proof. With
   the label a verifier learns, for every request of its choice, which of the three holds, and so,
   over many requests, where the model has no result. No statement bounds what many labels reveal
   together.
4. **`binding`.** Soundness, and binding of the same committer: an opening of the commitment to
   other weights than the extractor gives is rarely found. (`finalSoundAndBinding_value`,
   `lean/AtFullSide/Face/FinalBindingAtTheValue.lean`.) To open is to name weights and one number
   for the committer's randomness. That names fewer openings than any choice of coins would: nothing
   is said of an opening in which the salts of the first table's leaves have another public start or
   another length. At a small `coinBound` binding would say next to nothing: at 0 there is one
   setting of coins. At the honest provers and settings of the six theorems the bound leaves none of
   these out: `coinBound` + 1 is the committer's whole range, and at public files in use every
   encoding randomness of the first table and every member of the list of its salts are named
   together by a number up to `coinBound` (a theorem:
   `lean/AtFullSide/Face/FinalBindingOpeningsAtHonestProversAndSettingsOf.lean:39`). No number is
   given for `coinBound`. Nothing is said of two openings to the same weights, or of several
   commitments. The commitment covers the first table's root, its out-of-domain sample and a part of
   what is read off the public files, and not the key file's proofs, copies or links. Soundness
   holds whatever the honest provers and settings, binding for all whose tables' salts have one
   length, the same whatever the public readings return: they read no prover. The extractor is a
   function, not shown computable.
5. **`handsOutNoProof`.** At a refused request every reply that the prover can return is the empty
   proof. (`finalRefusedHandsOutNoProof_value`,
   `lean/AtFullSide/Face/TheFinalStatementOneBitHolds.lean`.) As a corollary
   (`finalHandsOutNoProof_of_refused`): at every request the label of the reply is requestLabel's,
   and outside served the form beside it holds no proof.
6. **`repliesFit`.** The numbers that the proof of zero knowledge reads: the replies are at most a
   stated number of runs of the online IOP a copy, at which the opened columns fit each table; and
   one run of the sampler, one of the committer and one of the prover together stay within 2^48 hash
   queries. (`finalAtT1_filled_withRoom`, `lean/AtFullSide/E2E/TheCompiledStepFilled.lean`.)

All six fields together: `theFinalStatementOneBitHolds`, and with the corollary
`theFinalStatementBothHold`, `lean/AtFullSide/Face/TheFinalStatementOneBitHolds.lean`. Its
statement, as the file has it:

```
theorem theFinalStatementOneBitHolds_at {zeroKnowledgeError : ℝ≥0∞}
    (room : stepErrorAtTheStops ≤ zeroKnowledgeError) :
    FinalStatementOneBit honestProversAndSettings zeroKnowledgeError

theorem theFinalStatementOneBitHolds : FinalStatementOneBit honestProversAndSettings finalZeroKnowledgeError

theorem theFinalStatementBothHold :
    FinalStatementOneBit honestProversAndSettings finalZeroKnowledgeError ∧
      FinalStatement honestProversAndSettings finalZeroKnowledgeError
```

The sum in the first form, `stepErrorAtTheStops`, is 2^-157, for the compiled step, plus the
interactive errors 0 and 0 and 688127 times 2^-174. `finalZeroKnowledgeError` is 2^-154: the least
power of two that fits. It is not a chosen target.

`FinalStatement`, the six fields with the label shown: `lean/Johnson/Face/FinalStatement.lean`; it
has a theorem of its own too, `theFinalStatementHolds`,
`lean/AtFullSide/Face/TheFinalStatementHolds.lean`.

**The executable verifier.** `((compile flashProveAtFiles).verify …).evaluate blake2bHash` is
`finalVerifierProgram` (`finalSystem_verifier_at_blake2b`), and, wherever the user's files read as a
claim, the verdict of `verdictOf`, the function whose parts `lean-verify` evaluates (`verdictOf_at`,
`lean/Johnson/PVR/Program.lean`), is `finalVerifierProgram` at the user's public files
(`verdictOf_eq_finalVerifierProgram`; it and `finalSystem_verifier_at_blake2b` are in
`lean/Johnson/Face/ExecutableVerifier.lean`). `verdictOf` parses the claim from the user's files
(`claimOf`) and applies `executableVerifier` to it (`verdictOf_eq_executableVerifier`, proved by
unfolding definitions). For every public setup, `executableVerifier` applied to the setup's public
files returns the verdict of `leanVerifier` (`executableVerifier_eq_leanVerifier`).
`verdictOf_eq_leanVerifier` is the same fact, stated for `verdictOf`; it therefore has two further
hypotheses: the claim can be parsed, and the public files are those of the setup. They are in
`lean/AtFullSide/Face/ExecutableVerifierIsLeanVerifier.lean`, with the definition of
`executableVerifier` and the instance of the first at the stored public files
(`executableVerifier_eq_leanVerifier_stored`). `executableVerifier_eq_leanVerifier` applies only
when the public files are those of a public setup. The command `lean-verify` does not enforce this:
it does not reject public files that specify a policy other than exact match. No theorem shows that
`claimOf` implements the file format. "Executable" means that Lean compiles the definition of
`executableVerifier`, which is not marked noncomputable; Lean's list of axioms for it also names the
axiom of choice (`lean/GAPS.md`, 56).

**The numbers.**

- `finalSoundnessError q` = 16 (q + 1 + 2^23) / 2^128 + (q + 2^23 + 3)^2 / 2^256, about q / 2^124 +
  2^-101. q counts the hash queries of the committer and the prover together.
- `finalBindingError q` = max (soundnessErrorInQueries q 2^23) (bindingErrorInQueries q), about q /
  2^124 + 2^-100.
- `finalCompletenessError` = 2^-40.
- At the interactive level the completeness error is at most 2^-41.
- `finalZeroKnowledgeError` = 2^-154, the least power of two that fits.
- 2^-174 bounds the chance, before hashing, for a served request, over the verifier's messages that
  pass the proof-of-work tests, that the online prover stops for a reason that depends on its
  secrets (it is counted once for each reply); for the offline and the link prover that chance is 0.
- The numbers on zero knowledge are statistical distances, not a security level.
- The zero-knowledge error, with one request to a run, is below 2^-154 over these 688,127 replies,
  and, by a lemma on the stated term (`life_number_at_most`,
  `lean/AtFullSide/CompletenessAndZeroKnowledge/LifeNumberAt135.lean`), below 2^-135 over the
  interactive statement's whole budget of up to 710,324 copies with up to 688,127 runs of the online
  IOP each.
- In point 3, 2^64 bounds the verifier's hash queries, and 688127 the replies under one commitment:
  a reply at a refused request, which is the empty proof, counts too.
- The hash function is not an argument of `compile`: the lines on soundness, binding, completeness
  and zero knowledge draw it at random, so they are statements in the random-oracle model. A second,
  fixed hash function, made of BLAKE2b's compression function with another counter, stands inside
  the protocol's description in all of them: that one is not a random oracle.

**What these lines do not say.**

- They are about `honestProversAndSettings` exactly as written. It is one closed term: default
  values stand in it at named places, the online prover's own among them. It is a definition and not
  a program: it takes the model's trace by a non-constructive choice.
- One request per proof; one commitment; exact match; the prover keeps no state, nothing counts the
  replies, and all its coins are fresh and uniform.
- A request counts as served only if the model gives a value at every position of the zero-filled
  window, the padding after the output included; so a true output can be refused (in the corollary
  with the label: told "failed") on account of the padding (for weights that pass a worst-case check
  a theorem rules it out; for others none does, and no example is proved).
- In point 3 nothing stands beside a proof: it is about the system that `compile` yields, with no
  wrapper round it. In that corollary the label beside a proof is a function in the statement, and
  nothing in `compile` emits it.
- Where the model has no result on a request, or another result than the claimed output, the
  completeness line says nothing. The requests of which that line speaks are those that meet
  `CanServe` and whose output is the model's (`finalComplete_iff_completeOn`,
  `lean/Johnson/Face/Checks.lean`), so the limits of that condition go with it (`lean/LIMITS.md`,
  L27).
- Under a tolerant acceptance policy Lean proves of the compiled verifier only that an accepted
  reply meets the policy; its soundness there is stated and not proved.
- That a request is refused is unchecked, as the label is: an empty proof proves nothing, and a
  prover can return it at a request that it could serve. The compiled verifier rejects it, under
  every hash function and at all public files (`rejectsNoProof_value`). In that corollary the label
  is unchecked too: a service that chooses to say "failed" does not prove it and can say it falsely,
  and the same holds of "other tokens": no proof goes with either, and the verifier checks nothing
  there.
- The final statement has no line that says that two different sets of weights both serve some
  request; at the interactive level the statement on zero knowledge has such a guard (two indices
  serve one request, shown at made-up weights).
- Completeness, zero knowledge and the replies' numbers come from the two theorems at the
  interactive level ("The three statements at one protocol"), through the compiler's theorems
  (`finalAtT1_filled`, `finalAtT1_filled_withRoom`; zero knowledge:
  `finalZeroKnowledgeOneBit_value`, `finalZeroKnowledgeOneBit_at`,
  `lean/AtFullSide/CompletenessAndZeroKnowledge/OneBitAtHonestProversAndSettings.lean`). These three
  lines are worth what the two theorems beneath them are worth: everything that goes with those goes
  with these.
- 2^-41 and 2^-40 are two bounds over two distributions: the first before hashing, among the
  challenges that pass the proof-of-work tests; the second after hashing, over the hash function and
  the coins, the searches for a nonce that run out included. No figure here is 128 bits, and none is
  a security level (`lean/LIMITS.md`, L84).
- The committer is a Lean term that no theorem ties to a program; the commitment has 256 bits, and
  the key file is not under it.
- At BLAKE2b no theorem shows that `verify` accepts anything: there it is tested by runs.
- The figures of the line on zero knowledge bound a statistical distance at these numbers of hash
  queries and replies: they are not a security level.
- The library also has statements on completeness written for any description of the protocol, which
  they take as a parameter, among them `G3'pol`. It is proved of no description, and the final
  statement does not depend on it (by the compiled library's record of the constants that each
  statement and proof uses).

(Entry by entry: `lean/LIMITS.md`, L88, L93.)

## What it does not say

What the soundness theorem on `verify` does not say, the heavier first. (What the theorems on
completeness and zero knowledge do not say: "Completeness and zero knowledge: what is proved for the
protocol, and what is not"; "The final statement's six fields", "What these lines do not say".) What
is marked "Of the programs" is a limit of the C++ and CUDA programs, not of the theorem. Each line
points to the entries that tell it whole.

- **1. Which verifier is proved.** Soundness is proved of the verifier written in Lean. Of the
  programs nothing is: the top of this page, "The programs". (`lean/GAPS.md`, 45, 56, 65, 26.)
- **2. The theorem's conditions.** The bound (about 124 bits per query; not «128 bits») is for one
  proof, in the random-oracle model for the hash, with the format's second, fixed hash function
  assumed independent of it, for one proof format and model size, against classical adversaries, and
  only for configuration files fixed before the hash function is drawn. N proofs handed in at once
  under one commitment cost N times that error, the error taken at the whole list's hash queries;
  for proofs checked one after another no bound is stated. (`lean/GAPS.md`, 36, 5, 60, 70, 35;
  `lean/LIMITS.md`, L8.)
- **3. Exact match only.** The theorem is for the policy under which the claimed output must be the
  model's exactly, and the Lean verifier does not itself test that the policy files say so: a reader
  checks the policy's three numbers. Under the looser clipped-gap policy that also ships, an accept
  says only that the output's token costs meet the policy's limits at the weights the extractor
  reads off the commitment — which by itself bars little; the written argument covers the conditions
  of the proof's last segment, which runs the clipped-gap equations, only in part, and Lean's
  theorem for that policy says only that the output meets it. See "Look first at four things", 1,
  and "The theorem under a policy: other acceptance policies". (`lean/GAPS.md`, 44, 6;
  `lean/LIMITS.md`, L5.)
- **4. What «false» and «the model» mean.** A claim is about the weights that the theorem's
  extractor reads off the commitment, run as the integer program at the public files the provider
  wrote; a yes does not say whose weights they are, that the shipped committer made the commitment,
  or which real model it is — a provider can commit to any model it likes, a small or degenerate one
  included. Only the named output positions are covered. Scale files, prefixes and the output's
  length: "Look first at four things", 3. (`lean/GAPS.md`, 54, 64, 59, 69; `lean/LIMITS.md`, L2, L7,
  L29, L37.)
- **5. The integer model is not the floating-point model.** Proofs are about the integer (quantized,
  fixed-point) model; how far its outputs track the original floating-point model's is a
  measurement, not part of any proof, and no trained weights are shown to meet the protocol's range
  conditions. (`lean/LIMITS.md`, L44, L7, L27; the measurement:
  [docs/limits.md](../docs/limits.md#the-integer-model).)
- **6. The commitment.** That the weights the extractor reads are the ones a committer put in, and,
  through binding at one extractor, that one commitment cannot be opened to two weight sets, are
  proved of an illustrative committer written in Lean and of the compiled committer (the line
  `soundAndBinding`, with `finalExtracts_value` and `bindingOf_value` beside it, both in
  `lean/AtFullSide/Face/FinalBindingAtTheValue.lean`; "The final statement's six fields", 4), not of
  the shipped committer; no theorem ties a commitment to one set of public files or one policy, so
  the user must hold the right public files as it holds the commitment. «Bound» means not openable
  to other weights, not that the commitment holds any. See "What the commitment gives, as proved".
  (`lean/GAPS.md`, 64, 72, 10, 71, 69, 77, 78; `lean/LIMITS.md`, L28, L32, L61.)
- **7. Completeness.** A verifier that rejects everything is sound too, with error 0
  (`rejectAll_sound`, `lean/VerifiableInference/Checks.lean`). Completeness is a further statement
  ("Completeness and zero knowledge: what is proved for the protocol, and what is not").
  Completeness covers well-formed requests on which the model has a result and the claimed output is
  that result. Where the model has no result it says nothing. The honest prover in these theorems is
  a Lean definition, not the CUDA prover. At BLAKE2b no theorem shows that `verify` accepts
  anything: there it is tested by runs. How the tests came out: "What has been run".
  (`lean/GAPS.md`, 52, 14, 55; `lean/LIMITS.md`, L9, L27.)
- **8. The claim is formed outside the theorem.** The Lean verifier's command turns the user's three
  files into commitment ID, prompt and output with short functions that no theorem covers; a fault
  there would give an accept about a different claim than the user's (the command prints the claim
  it judged, and a second reader of the files must agree to the byte). See "Look first at four
  things", 4. (`lean/GAPS.md`, 37, 17, 46, 56.)
- **9. A library that can be misused.** (Of the programs.) A program that calls the `blocks/`
  library directly, outside the contract in blocks/chain/closed.h, can be made to accept a false
  claim; at least one such way is known to work at the full target at toy size. That the C++
  verifier is not exposed rests on reading its source, not on a test.
  ([docs/limits.md](../docs/limits.md#false-claims-in-test-programs).)
- **10. Altered stored tables can verify.** (Of the programs.) A committer that alters part of the
  table it stores beside a commitment can still have its proofs accepted by the C++ verifier; in
  every such case the claim stayed true, shown by a separate count and argument, not by a proof.
  ([docs/limits.md](../docs/limits.md#soundness).)
- **11. Proofs are malleable.** Some bytes of an honest proof, or of a commitment's files, can be
  altered and the proof still accepted, for the same true claim; non-malleability is not claimed,
  and an accept does not show that this exact file came from the prover. The two verifiers can part
  on such altered files (one accepts the parsed file where the other rejects the raw one). See
  "Altered proof files that leave the claim untouched were accepted". (`lean/GAPS.md`, 66, 14;
  `lean/LIMITS.md`, V0.)
- **12. The two verifiers are close, not identical.** The Lean verifier runs sixteen tests of its
  own on the public files — conditions the proof needs, made tests at its gate rather than proved
  for all files in scope — and refuses where one fails (where they are proved to pass, and what
  follows elsewhere: "Its reach"); a parameter file can pass the C++ verifier and yet give less
  soundness than the figures it prints. In one comparison of their hash calls, over Lean files that
  differ from this repository's (`lean/GAPS.md`, 22), 881,280 of the Lean verifier's 1,166,983
  matched the C++ verifier's, the rest explained only in part. The C++ verifier's test of the
  parameter file admits the cost exponent 7 as well as 8 (a token's cost is its logit gap + 2^8);
  the Lean verifier's scope, the theorem and every written argument cover 8 only; all shipped files
  use 8, and the Lean verifier's command reports exact match only at 8. (`lean/GAPS.md`, 25, 22, 73,
  27; `lean/LIMITS.md`, L5.)
- **13. The C++ programs' printed «bits» are their own accounting, not a theorem.** (Of the
  programs.) The weakest round prints 128.00 bits with up to 32 bits of proof of work counted by
  assumption (96.23 without), no margin, about 6 bits fewer per batch of 64; the proved figure is
  the Lean theorem's (about 124 bits per hash query, item 2), not the programs' printed one.
  ([docs/limits.md](../docs/limits.md#the-soundness-figure); what they rest on: [the same
  page](../docs/limits.md#what-the-theorem-assumes).)
- **14. Tests against lying proofs are narrow.** How narrow: "What has been run". (`lean/GAPS.md`,
  76, 33, 14.)
- **15. What the Lean proof rests on.** No conjecture on codes is assumed: the coding theory it
  needs is proved inside the library, in files adapted from other formalizations, whose match to the
  published statements has not been independently compared. `verify` and the definitions beneath the
  statements are definitions: the kernel checks proofs, not what a definition means, so a reader of
  the statements must read those definitions. The independent proof checker: "How to check
  it". (`lean/LIMITS.md`, L15, L46, L25; `lean/GAPS.md`, 12, 18.)
- **16. The hash is modelled, the code is not verified.** BLAKE2b is treated as a random oracle; one
  constant beneath `verify` is a value of the real hash function; that nothing reads it is read, not
  proved ("What it rests on"). (`lean/LIMITS.md`, L8, V3, L45; `lean/GAPS.md`, 7, 46, 51.) (Of the
  programs:) BLAKE2b's implementation and the ChaCha20 stream are ordinary code tested against
  published vectors and against each other, and the GPU kernels are tested in part and mostly at
  small sizes ([SUITE.md](../SUITE.md)); none of it is verified; compilers and hardware are trusted.
  ([docs/limits.md](../docs/limits.md#which-verifier-has-a-theorem).)
- **17. One configuration family.** «Admissible configuration» is a stated range of sizes and
  parameters; outside it nothing is claimed and the Lean verifier refuses. A guard inside the Lean
  verifier can cost completeness (a refusal), never soundness. (`lean/GAPS.md`, 35, 57, 68.)
- **18. Batches and members.** A batch proof covers many requests under one commitment, and one
  member's proof can be shown on its own, without the other members' inputs and outputs being part
  of what is handed over; what is proved per member is the statement of item 2, N-fold for N members
  at once; what, if anything, the other members' data leak through it no theorem says ("Completeness
  and zero knowledge: what is proved for the protocol, and what is not", "The limits.";
  `lean/GAPS.md`, the appendix).

## The theorem under a policy: other acceptance policies

`soundUnderPolicy_of_verify_at` (`lean/Johnson/Goal/Skeleton/SoundOfVerifyPolicy.lean`) drops the
third hypothesis, exact match. For all public files in scope an accepted output **meets the policy
that the files state, except on an event of probability at most the stated bound**
(`Policy.MeetsPolicy`, `lean/Policy/Front/MeetsPolicy.lean`) at the weights that the protocol's own
extractor returns. That is not index binding for the model's own relation. The limits on this page
hold of it too.

- **What a policy says.** Each counted output token (those inside the window of 1,024 tokens of
  prompt and output: `Policy.countedTokens`, `lean/Policy/Front/MeetsPolicy.lean`) costs 256 plus
  its gap to the model's first choice: for a token of the vocabulary, how far its integer score lies
  below the first choice's, and 1 more if the first choice is the token of the lower number, tie or
  not (`logitGap`, same file; `Policy.logitGap_eq_choice`,
  `lean/Policy/Front/MeetsPolicyGuards.lean`). The costs, each clipped at `C`, have a mean of at
  most `theta`, and at most `cap` tokens cost more than `C`. That bounds a mean and a count over one
  output, which the prover picks: up to `cap` tokens may be any tokens. The prompt's tokens are not
  scored: a reply that is cut into several outputs has a mean and a count in each. In scope 256 ≤
  `theta` ≤ `C` < 2^32 and `cap` ≤ 1,024.
- **Some policies in scope mean nothing.** With `C` = `theta` the mean says nothing. If `cap` is
  also at least the number of counted tokens, as at (256, 256, 1024), the count says nothing either.
  `verify` does not reject such files (the C++ programs do, where the call names the policy and at
  least one token is counted), so there only the token after a full window of 1,024 tokens is
  certified.
- **What the stored tolerant policy gives.** At (25856, 512, 1), in an output of at most 99 counted
  tokens that meets it, every counted token's gap is below 25,600 and the mean gap is at most 256;
  at every length, for 0 < g ≤ 25,600, at most 256 n / g of its n counted tokens have a gap of g or
  more (`gaps_of_meetsPolicy_qExample_short`, `card_gap_ge_mul_le_qExample`,
  `lean/Policy/Front/MeetsPolicyAtGap.lean`). At the library's written copies of the two stored
  sets, for 1 ≤ n ≤ 1,023: a policy with `theta` ≤ `C` < 2^32 is met, under all weights, by every
  output of n counted tokens that has scores and whose token after a full window is the model's,
  exactly if `theta` = `C` and `cap` ≥ n (`VerifierAndGoals.AtFiles.every_output_at_meets_iff`,
  `lean/Johnson/Goal/Files/MeetsPolicyAtFiles.lean`). The weights that show it are made up: nothing
  follows for a trained model. At other files in scope "only if" can fail: with the final norm's
  exponents at most 11 apart, the policy (2^32 − 1, 2,436,593,409, 0) bars nothing
  (`exists_policy_of_close_scales`, `lean/Policy/Front/MeetsPolicyIdleAtScales.lean`). A form of the
  theorem under a policy with its claim rewritten in gaps: `soundForGaps_of_verify_at`
  (`lean/Johnson/Goal/Skeleton/SoundOfVerifyGaps.lean`). Under the tolerant stored policy the
  accepted output departs from the model's first choice at one position, within that policy's limit,
  as that example was made to show. That rests on one run of the integer-model package
  (`integrations/vllm/integer_model/`, in Python, outside Lean), on sources of the package that
  differ from this repository's, not on the proof. By the exact-match relation that output would
  count as false.
- **A gap is in the weights' own units.** Under all-zero weights every well-formed output of at most
  one window meets every policy with `theta` and `C` of at least 257 (`meetsPolicy_zeroWeights`;
  past a full window the token must be token 0).
- **Alone it is weak.** By itself it bars nothing against a committer who commits to weights under
  which every output meets the policy: under many tolerant policies some choice of weights —
  all-zero weights, which are in range, for one — lets every well-formed output meet the policy (the
  numbers: "A gap is in the weights' own units"), and the theorem speaks of the weights that its
  extractor reads off the commitment and the committer's hash queries at the given public files,
  whoever made the commitment. So it means something only together with correctness of extraction at
  the same extractor — that the extracted weights are the ones an honest committer put in, which
  cannot be stated with any content of the system in the statement of the soundness theorem on
  `verify`, whose committer is the constant committer — with knowing who made the commitment, which
  no theorem says, and with completeness, which under such a policy is tested, not proved
  (`lean/GAPS.md`, 6). (For one illustrative committer the joining with correctness of extraction is
  proved: "What the commitment gives, as proved", above.)
- **It is not the test of the public paper on Token-DiFR** (arXiv 2511.20621). The mean has that
  test's form. To meet it is not to pass that test: there the checker runs a model that it knows,
  pools many outputs' tokens and fits the clip to honest runs.

## What to read

Who wrote the library: `lean/README.md`, `lean/CREDITS.md`.

The proof is Lean's to check. Its kernel has checked it, so the proofs need no reader
(`lean/LIMITS.md`, L45). The meaning lies in the definitions that the statement names. The
statements and the definitions beneath them are set out, or named by file, for a reader in
[AUDIT.md](AUDIT.md) (as a web page, which is the one to read: [STATEMENTS.html](STATEMENTS.html)).
For soundness that is the statement `Sound`, and what the theorem on the Lean verifier puts into it
beside the verifier: the model, and how the public files are read. Read also AUDIT.md's Appendix B,
which names the files of the concrete hash function (what is assumed of it: "What it rests on"), and
`PV.Program.claimOf` with what it calls (`PV.Front.idOf` and `userOf` among them), which builds the
claim from a user's files under no theorem (`lean/GAPS.md`, gap 37). What the kernel does not check:
"What it does not say", 15. The limits, entry by entry: `lean/GAPS.md`.

Where a comment and Lean's printed statement differ, the statement counts.
