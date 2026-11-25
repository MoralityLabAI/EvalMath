import Mathlib

/-! MIT-01 supporting lemma; listed in CLAIMS.md. -/
namespace InstrumentTransfer

theorem paid_gain_iff (n k b c q : ℚ) (hn : 0 < n) (hk : 0 < k)
    (hbc : 0 < b - c) :
    b / n < (b - c) * q / k ↔ b * k / (n * (b - c)) < q := by
  rw [div_lt_div_iff₀ hn hk, div_lt_iff₀ (mul_pos hn hbc)]
  rw [show (b - c) * q * n = q * (n * (b - c)) by ring]

end InstrumentTransfer
