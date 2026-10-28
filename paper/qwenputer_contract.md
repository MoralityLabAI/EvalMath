# QPC-01: exact memory transitions as an EvalLang calibration target

Evidence: algebraic identity plus finite verified examples. Version 1, 2026-10-28.
The receipt checks 1,512 memory cases and 1,512 corresponding rotated updates.
The 13 unit tests cover additional negative controls. No Lean elaboration or
Qwenputer checkpoint execution is claimed.

Use row-address memory S in Q^(n x d), a unit address vector k, and row value v.
The explicitly gated delta update is

    T(S,k,v,a,b) = a*S + b*k*(v - k^T*(a*S)).

At a=b=1 and k=e_i, row i becomes v and every other row is unchanged.
Indeed, row j receives e_i[j]*(v-S[i]); direct substitution proves the claim.
Reading with e_i returns v. The Python symbolic oracle performs a direct tuple
replacement independently of the delta-rule implementation.

For an orthogonal address-space map U, simultaneously transform S to U*S,
k to U*k, and read queries q to U*q. Then T(U*S,U*k,v,a,b)=U*T(S,k,v,a,b),
because U^T*U=I. This is a coordinate change of this memory operation.
Conjugating an arbitrary pretrained transformer requires further architectural
work; changing the state alone does not preserve its computation.

Let phi decode the declared memory cells and let delta_symbolic overwrite them.
The equation phi(T(S,u))=delta_symbolic(phi(S),u), plus a valid initial state,
gives trace agreement by induction over writes. Evaluator sufficiency additionally
requires E=e o phi on the declared reachable domain. Two memories with equal
visible first rows and different second rows demonstrate why this condition must
be checked separately when the evaluator reads the second row.

An exact finite checker decides only its declared finite domain. Kernel verification,
floating-point kernel behavior, circuit recovery, model-wide interpretations, and
predictions after RL updates remain separate obligations. Beta=2 is a deliberately
constructed sign-flip control. It does not establish anything about learned intent.

## Provenance and integration boundary

The external motivation is [Agrawal's Qwenputer write-up](https://divagr.com/blog/qwenputer),
checked 2026-10-28. Its model results remain upstream author reports. This patch
implements fresh rational fixtures; no upstream implementation code is vendored.
The additional [recurrent-state study](https://divagr.com/blog/hybrid-models-can-hide-reasoning-in-their-rnn-state)
motivates keeping attention and recurrent interventions separate in future runs.

This additive module leaves the active EvalLang owner and existing verification
registry unchanged. Its own receipt command is an explicit acceptance gate:

    PYTHONPATH=src python -m unittest discover -s tests -p 'test_qwenputer_contract.py' -v
    python scripts/verify_qwenputer_contract.py --check output/qwenputer_contract_v1.json

Repeat both under `python -O`. Before integration into scored evaluations, obtain
independent review and connect this receipt to the repository's central checker.
