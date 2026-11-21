# Exact sufficient scalar conditions for LargeX and SmallCosts

Source pin: f150e02623b1e2bbe1f1da8eab5ffee5e930a6a3.
Original LargeX and smallCosts proofs occur in
Formalism/SharpRestriction/GlobalSchurBounds/RamificationTwoAndConjugationAtQAndD.lean.

The first two source-regime witnesses chose log2(x)=16/epsilon.
At these scales x^(epsilon/8)=4, so the sufficient logarithmic
criterion for 8*x^5 <= exp(x^(epsilon/8)) fails.

Increase to log2(x)=256/epsilon, with epsilon=1/64 and 1/128.
Choose binary exponents of the other parameters at the central
SizesAt scales:

    L = log2(x), q = epsilon*L = 256
    log2(n) = 2L+8q
    log2(m) = (L-q/8)/2
    log2(k) = 9L/2+10q
    log2(nT) = log2(n)-q/8-1
    log2(nT2) = log2(n)-q

To test scalar SmallCosts choose f=2n, eta=1,
b=12*f*x*(x+1), theta=1/(4*f*x*(x+1)), Cd=CL=0, c=1.
Under these choices the two rational cost inequalities hold directly.

LargeX includes 8*x^5 <= exp(x^(epsilon/8)) and
48*x^5 <= exp(x^(epsilon/4)). Since x=2^L and log(2)<=1,
log(8*x^5)<=3+5L and log(48*x^5)<=6+5L.
Monotonicity of exp makes the integer inequalities
3+5L <= x^(epsilon/8) and 6+5L <= x^(epsilon/4)
sufficient. The checker verifies them with exact integer arithmetic.

For Cd=CL=0, moveCost=3 log(x+1). Since x>=1 and x=2^L,
log(x+1)<=L+1, so it suffices that
3(L+1)<=x^(1/2+epsilon). The source's two other power
thresholds are checked with exact dyadic exponents.

Both examples also pass the six SizesAt and three PlacesAt bounds,
the finite-set cardinality caps, and all sixteen SizeWindows scalar
conditions after substituting the new b.

These conditions are an exact arithmetic certificate with documented
elementary calculus implications. The Python tests do not formally
prove the general logarithm and exponential comparison facts in Lean.
These free scalar choices are not asserted to be the actual
Scale.b or Scale.theta, nor do they construct any arithmetic
character estimates, adm5/6/7, or the eventual family witness.

## Verified CI receipt

The exact source-attested [workflow run](https://github.com/MoralityLabAI/EvalMath/actions/runs/44903295524) passed 12 CPU-only tests and emitted the complete [JSON artifact](https://github.com/MoralityLabAI/EvalMath/actions/runs/44903295524/artifacts/14706404309). The archived JSON SHA-256 is `8b28912df718694c1e3978fc8520d270ed3f1b5a845d5ad2430735598c40249d`. The repo retains a [compact machine-readable verification receipt](joint_scalar_envelope_receipt.json) with the same source identities, scale exponents, pass counts and limitations.
