# ETH counting to cipher inversion: representation audit (CA-02)

**Date:** 2026-10-27. **Evidence levels:** cited pinned theorem statement, cited NIST circuit census, algebraic encoding identities, finite exact toy examples. No actual AES key recovery is attempted. The ETH result remains subject to independent Lean replay and expert review (EvalMath PRs #10–#11).

## Mathematical transfer

For any circuit on **b** Boolean input bits with **g** fan-in-two AND, XOR, or XNOR gates, introduce one fresh Boolean variable for each gate, and impose its truth table in CNF. Each AND costs three clauses, each XOR/XNOR four clauses, all of width at most three. Constrain designated output bits by unit clauses. Thus, for a chosen set of output pins,

\[
N=b+g,\qquad M=3g_{\wedge}+4g_{\oplus,\leftrightarrow}+h.
\]

The encoding is *parsimonious* with respect to the b free input bits: for each input, every intermediate gate variable has exactly one consistent value. Hence each satisfying assignment of the output constraint on the original b inputs has exactly one extension to the CNF, preserving the exact preimage count. Inputs fixed as constants can be simplified, although the ledger deliberately charges all published NIST gates without simplification.

OpenAI's October 2026 pinned Lean scope claims a deterministic exact fixed-width-CNF counter with running time

\[
\mathrm{poly}(L)\,2^{O_k(N(\log\log N)^2/\sqrt{\log N})}.
\]

This implies a generic **asymptotic** subexponential inverter for circuit families with \(g=O(b)\), polynomially bounded output length and a uniformly available circuit description: adding progressively fixed input literals and testing whether the resulting count is positive reconstructs a preimage with at most b decision/counting calls. A bound of \(2^{o(b)}\) is consistent with the *polynomial-time* definition of one-way functions; it excludes a family-level \(2^{\Omega(b)}\) inversion lower bound under the stated assumptions. The fixed-density manuscript claim improves the exponent to \(O(N/\sqrt{\log N})\) for \(M\le D N\), where fixed D and the hidden constants are inherited from the encoding. These statements concern the claim in the manuscript and its pinned formalization scope; they are conditional on verification of that mathematics.

## Compact local predicates

For \(f:{0,1}^b\to{0,1}^m\) with each output bit determined by at most a fixed \(d\) input bits, specify each given output bit by blocking all local input tuples that would yield the wrong value. This yields at most \(m2^d\) clauses, each of width at most \(d\), directly over **b** unknown input variables. If \(d\) is fixed and \(m\) is polynomial in b, the *general-density* theorem gives a \(2^{o(b)}\)-time inverter with polynomial factor in \(b+m\). For \(m=O(b)\), the paper's stronger fixed-density theorem may apply. Goldreich's constant-locality one-way function/PRG proposal is a natural asymptotic test case: it is structurally a local CSP with a fixed predicate, and a successful algorithm would be a generic subexponential inverter, **not** a polynomial-time break of the underlying one-wayness assumption.

## XOR elimination and sparse polynomial systems

An AND/XOR/XNOR Boolean straight-line program can be represented without retaining any linear gate outputs. Use the original input coordinates and one variable per AND. Track each XOR/XNOR wire as an affine form over these coordinates. For every AND output \(z\) fed by forms \(A,B\), impose the quadratic Boolean equation

\[
z+A B=0\quad\text{in }\mathbb F_2[x_1,\ldots,x_N]/(x_i^2-x_i).
\]

Pins become affine equations, and each complete satisfying assignment extends uniquely to the original gate wires. This reduces the *declared variables* from \(b+g\) to \(b+g_{\wedge}\). It can increase the *number of listed polynomial monomials* because products of dense affine forms expand into many quadratic terms.

The pinned manuscript's quantitative-reduction.tex, Lemma lem:tensor-sparse-query, explicitly claims exact counting of shared zeros for \(a\le cN\) equations in **N Boolean variables**, each listed with at most \(\lceil\log_2 N\rceil^c\) monomials of degree at most fixed \(k\), in

\[
N^{O_{k,c}(1)}\,2^{O_{k,c}(N\log\log N/\sqrt{\log N})}
\]

bit operations and polynomial space, for fixed positive integer \(k,c\) and \(N\ge20\). This stronger sparse-polynomial *lemma* is part of the **manuscript proof**, and does not appear in the documented Lean endpoint's statement scope. Simply saying that an equation is quadratic, or algebraically sparse in a circuit representation, does not establish its required *listed monomial* bound after elimination. In particular the degree restriction and the monomial-count restriction are separate.

Our positive control expands a 24-input XOR parity into one 25-term linear equation, at \(N=24\), meeting \(k=c=2\), \(a\le cN\). The negative control forms the product of two disjoint 12-input parities. One fresh AND variable remains, giving \(N=25\), a quadratic equation of **145** monomials (144 cross terms plus the output), above the \(\lceil\log_2 25\rceil^2=25\) limit. Exact evaluation confirms the representation identities on finite witnesses. These are eligibility and encoding checks, not an implementation of OpenAI's counting method.

## AES-128 census and honest bounds

[NIST's circuit complexity catalogue](https://csrc.nist.gov/projects/circuit-complexity/list-of-circuits) publishes **AES-128(k,m)** as 6,400 AND, 21,356 XOR and 844 XNOR gates, total **28,600**. Holding one plaintext fixed and pinning 128 ciphertext bits, the unsimplified Tseitin construction above has at most **28,728** variables and **108,128** clauses, all width at most 3. The ratio is **224.4375 CNF variables per 128-bit key bit**.

With all XOR/XNOR gate outputs *symbolically* eliminated, the 6,400 AND outputs and 128 key variables would give at most **6,528 declared coordinates** before optional linear elimination. That is only a coordinate census; the actual AES quadratic equations have not been generated or measured. The number of expanded monomials and the sparsity-lemma's fixed-c eligibility remain **unverified**. In a unit-coefficient illustration, \(N/\sqrt{\log_2 N}\) at \(N=28,728\) is **7,464.9**, compared with the 128-bit brute-force exponent. For \(N=6,528\), the corresponding sparse-lemma *scale* \(N\log_2\log_2 N/\sqrt{\log_2 N}\) is **6,718.3**. Neither value is a theorem-level finite-size runtime estimate; the big-O constants and initial thresholds are unquantified and potentially enormous. Neither encoding demonstrates any AES attack.

### Updated NIST AES-128 full-circuit Pareto census

NIST's current flat Encipher catalogue provides two source-pinned alternatives
to the older 28,600-gate reference. Each has 256 input bits (128 plaintext,
128 key), 128 output bits and a complete unrolled encryption + key expansion.

| Variant | AND | XOR/XNOR | Total gates | Tseitin variables | Tseitin clauses | XOR-eliminated coordinates |
|---|---:|---:|---:|---:|---:|---:|
| Lower total gate count | 6,400 | 21,456 | 27,856 | 27,984 | 105,152 | 6,528 |
| Lower AND count | 5,800 | 27,856 | 33,656 | 33,784 | 128,952 | 5,928 |

The full-circuit counts are sourced from these independently retrieved headers,
pinned to NIST Circuits commit 8366158a4324ef902ce740f29ddc9f7ebb1018b2:

* [27,856-gate AES-128 Encipher](https://github.com/usnistgov/Circuits/blob/8366158a4324ef902ce740f29ddc9f7ebb1018b2/data/slp/aes/aes-encipher/aes128-encipher-a6400-ad50-g27856-gd286-xx21456-616.circ.txt), Git blob SHA-1 6875e0d6f5878f9cbab255d62ebaad6848cb6c53.
* [5,800-AND AES-128 Encipher](https://github.com/usnistgov/Circuits/blob/8366158a4324ef902ce740f29ddc9f7ebb1018b2/data/slp/aes/aes-encipher/aes128-encipher-a5800-ad50-g33656-gd388-xx27856-4016.circ.txt), Git blob SHA-1 a1dbbb143b13f8bb7c9e5f7b3e0f3d5c27785eae.

The upper bounds charge every gate after the plaintext is substituted and
pin 128 ciphertext output bits. Gate-level simplification could reduce the
formula further. XOR elimination has 6,528 versus 5,928 declared coordinates,
but actual expanded monomial counts remain unknown. With an illustration
coefficient of one, the fixed-density CNF scales are approximately
7,280.9 and 8,710.2, respectively; corresponding sparse-polynomial
scales are approximately 6,718.3 and 6,107.9. These figures rank
representations under assumed cost functions. They provide no AES key-recovery
algorithm, since the manuscript's actual constants, finite-size applicability
and post-elimination sparsity are unverified.

This is a Pareto comparison within two documented NIST options, not a
claim that either circuit is globally smallest. Both source blob hashes were
confirmed against the pinned NIST commit. A complete SLP execution is future
work.


Lightweight ciphers invite a larger version of this audit because gate counts differ greatly by construction. Care is needed with area metrics: gate equivalents (GE) for a time-multiplexed hardware core and the number of gates in a full unrolled encryption circuit measure different objects. PRESENT, for example, has 31 rounds and 16 four-bit S-box invocations per round; a fully unrolled counting formula still represents the entire computation, including its key schedule. Report exact bit-circuit counts before inferring a smaller CNF exponent.

## Verification and review gates

The crypto_encoding_bridge.py code provides count-preserving CNF encoding, symbolic XOR elimination over the Boolean quotient ring, direct fixed-locality CNF, bounded sparse-polynomial truth-table CNF, syntactic eligibility inventory, and an explicitly labelled NIST gate-census calculation. Twelve exact tests cover gate and witness bijections, cancellation, local predicates, polynomial multiplication, positive/negative sparsity controls, and the AES arithmetic. Source-hashed receipts are generated by scripts/verify_crypto_encoding_bridge.py. Every claimed shortcut remains conditional on the independent correctness oracle; speedups require wall-clock, memory, operation counts and held-out-scaling evidence in addition to the inequalities above.

### Sources and reproduction

* Upstream source pinned to [openai/math@7ef5c0c quantitative-reduction.tex](https://github.com/openai/math/blob/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/build/quantitative-reduction.tex).
* Upstream [Lean scope 378.md](https://github.com/openai/math/blob/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/lean/docs/378.md).
* [NIST published AES gate census](https://csrc.nist.gov/projects/circuit-complexity/list-of-circuits).
* [Goldreich local-function reference, O'Donnell and Witmer](https://www.cs.cmu.edu/~dwitmer/papers/csp-prg.pdf).
* [PRESENT circuit structural overview](https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/iet-cds.2019.0363).

Reproduce from EvalMath root:

    PYTHONPATH=src python -m pytest -q tests/test_crypto_encoding_bridge.py
    PYTHONPATH=src python scripts/verify_crypto_encoding_bridge.py --output /tmp/crypto_bridge.json
