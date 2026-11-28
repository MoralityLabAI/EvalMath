# Small-epsilon family scale certificates from original SizesAt and PlacesAt

Exact pinned upstream source at commit f150e02623b1e2bbe1f1da8eab5ffee5e930a6a3:

- Formalism/SharpRestriction/GlobalSchurBounds/ZetaZeroFreeRegion.lean,
  Git blob 7746e5a5affe67117d4ba907dbcd2788f539db6e, defines
  SizesAt and PlacesAt.
- Formalism/SharpRestriction/GlobalSchurBounds/RamificationTwoAndConjugationAtQAndD.lean,
  Git blob 1c1495ef81c77fa96f3c1a70106c1da9e24c0c5d, proves
  the identity x*delta1 = x^(1-epsilon/8) inside theorem windows.

To match the actual family theorem, epsilon must be positive and below 1/52.
Take epsilon=2^-j, j=6 or7, and let L=log2(x)=16/epsilon.
Define the integer cardinalities and parameters by their binary logs:

    log2(n)   = 2L+128
    log2(nT)  = 2L+125
    log2(nT2) = 2L+112
    log2(m)   = L/2-1
    log2(k)   = 9L/2+160

with b=1, C=aE=Err=0 for the scalar-only test.

The exact-rational checker verifies the six SizesAt inequalities,
the three PlacesAt inequalities, both finite-set cardinality caps
and 0<epsilon<1/52. It separately checks all 16 original SizeWindows
scalar conjuncts, including 26 <= x^(3epsilon/8) = 64.

For epsilon=1/64 the exponents are L=1024, log2(n)=2176,
log2(nT)=2173, log2(nT2)=2160, log2(m)=511 and log2(k)=4768.
For epsilon=1/128 they become L=2048, 4224, 4221, 4208, 1023 and 9376.

These strong source-regime scalar certificates repair a limitation of
the initial SizeWindows-only family n=sqrt(x): the latter fails the
original SizesAt requirement n >= x^(2+31epsilon/4).

The test establishes arithmetic consistency of finitely many scalar
inequalities for two specific choices of epsilon. The original family
theorems quantify over every sufficiently small positive epsilon,
arbitrarily large x, and actual groups, character sums and geometric
witnesses. b=1 also does not satisfy SmallCosts in the intended
large-x regime. No part of this certificate proves RH.
