# Lean companions in Metamath: CF-01

CPF03 inclusion transfer and a concrete formal counterexample to reverse transfer.

Explicit uncompressed proofs against pinned set.mm 806509385370b29fe8b1723804777ac21b1ce194. No new axioms or syntax. The manifest records exact scoped premises, conclusions, proof sizes, Lean source blob IDs and human mappings. Types are interpreted as sets, functions as set-coded graphs; pointwise certificates specialize universal premises. Supporting proofs and countermodel certificates are distinguished from full ports. Proof verification does not automate cross-foundation statement equivalence.

Reproduce: python formal/metamath/verify.py /path/to/set.mm /path/to/mmverify.py /path/to/metamath /tmp/mm-ports --negative. Full C and Python verifiers must agree and reject a mutated certificate. No existing Lean source changed. CI pending at registration.
