# TFAF: Theorem Fidelity Under Adversarial Formalization

**Status:** six independent semantic mutation examples, a pinned upstream source-contract audit, and small Lean witness theorems. This is neither a replay nor a refutation of the Unique Games proof.

## Upstream source pin

- Repository: https://github.com/openai/math
- Commit: 7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a (2026-10-26)
- Theorem entry: lean/OAI/Computability/UniqueGames/Theorem.lean, OAI.UniqueGamesTheorem.theorem11
- Contract: lean/OAI/Computability/UniqueGames/Model.lean
- Comparator: lean/ComparatorChallenges/UniqueGamesTheorem.json
- Manifest with five independently pinned Git blob SHAs: upstream_pin.json

The ComparatorChallenges/UniqueGamesTheorem.lean challenge template intentionally ends in a **sorry placeholder**. The actual proof entry in OAI/Computability/UniqueGames/Theorem.lean invokes a concrete construction and contains no such placeholder. The comparator manifest identifies the solution module OAI.Computability.UniqueGames.Main. Treating the challenge template as the full proof would create a false alarm.

The pinned BinaryGapReduction contract places its alphabet, coordinate isomorphism and polynomial-time machine outside the input quantifier. It also requires permutation tables, nonempty simple bipartite instances, F2 translation constraints, existential completeness, and universal soundness. The source checker compares twelve specific field signatures plus the theorem entry and comparator manifest. These are textual checks; full Lean elaboration and proof dependency auditing remain separate.

## Six adversarial statement mutations

| ID | Mutation | Verified illustration |
|---|---|---|
| TF-01 | Existential rather than universal soundness | A bad labeling scores 0 on an equality edge with OPT=1 |
| TF-02 | Drop permutation requirement | Universal relation accepts all label pairs, but is not a permutation |
| TF-03 | Weaken completeness/soundness gap | Four distinct bipartite F2 translation edges give OPT=3/4 |
| TF-04 | Replace decoded 3SAT language | (x OR x OR x) AND (NOT x OR NOT x OR NOT x) is unsatisfiable |
| TF-05 | Allow alphabet to depend on input size | Exponential alphabet growth is unbounded; Lean gives a proof |
| TF-06 | Omit polynomial runtime | Construct a witness where 2^n > C n^d for every selected C,d |

TF-02 deliberately tests a generalized binary relation that cannot inhabit the pinned permutation-table type. TF-03 is a fully valid small Unique Game, including simple bipartite endpoints and translation constraints. It illustrates semantic separation; none of the examples proves an NP-hardness assertion.

For TF-06, set k=d+1 and choose n >= 2k and n > C 2^k k!. The binomial theorem gives 2^n >= binom(n,k). Since all k factors in n(n-1)...(n-k+1) are at least n/2, binom(n,k) >= n^k/(2^k k!) > C n^d. The checker computes an exact certificate for chosen inputs. The general asymptotic reasoning is documented mathematically and remains outside the Lean witness module.

## Reproduce

From repository root:

~~~bash
python -m unittest discover -s research/theorem_fidelity -p 'test_*.py' -v
python scripts/check_theorem_fidelity.py
python research/theorem_fidelity/upstream_contract.py --fetch
~~~

The pinned-source command fetches five immutable GitHub paths, checks Git blob hashes, checks twelve semantic field signatures, and verifies the comparator/solution distinction. Alternatively, pass --snapshot PATH to read those exact source files offline.

For independent local Lean witnesses:

~~~bash
cd lean
lake build
lake env lean axioms_check.lean
~~~

The main verification workflow runs these Lean checks and reports unexpected axioms. The theorem-fidelity workflow checks Python and the pinned upstream sources. Neither compiles the complete upstream OpenAI formalization.

The committed output/theorem_fidelity.json receipt records case outputs, evidence levels, local source hashes and the upstream commit. scripts/check_theorem_fidelity.py recomputes and compares it deterministically.

**Next gate:** compile OpenAI's pinned solution module independently and check the elaborated theorem type, axiom footprint and transitive proof dependencies before using model scores to judge the upstream theorem.
