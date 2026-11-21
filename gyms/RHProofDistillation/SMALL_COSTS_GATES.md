# SmallCosts: two simultaneous scale constraints

The original [SmallCosts definition](https://github.com/leanprover-community/riemann-hypothesis/blob/f150e02623b1e2bbe1f1da8eab5ffee5e930a6a3/src/Formalism/SizeWindowBrackets/GrowthBoundGivesRiemannHypothesis.lean)
requires, among its conjuncts:

```text
2*f*(x+1)*theta <= 1/x
6*f*(x+1)*(eta+1) <= b/x
```

With x>0, f>0 and eta>=0, these imply the necessary bounds:

```text
theta <= 1/(2*f*x*(x+1))
b >= 6*f*x*(x+1)
```

`f` is instantiated by `fPl H = (PhiSet (H := H)).card`, a
positive finite cardinality in the source construction.

This creates a high-b and low-theta requirement as x grows.
The exact dyadic SizeWindows witnesses in this gym use b=1;
they are deliberately limited to that predicate and do not
establish satisfaction of SmallCosts, ThinScales, or the full
`GrowthInequalityDataExists` conjunction.

Tasks RH-D-014 and RH-D-015 formalize the two implications
as independent verified Lean reconstruction targets.
