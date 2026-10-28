"""Float consistency checks on D.5 version 0.4 (selection KL): the Gaussian constants and the
second-order margin delta_K, computed here by independent quadrature (mpmath), against
(i) the note's tables (E[M_K], c_K, c(K)),
(ii) the identity delta_K = c(K) E[M_K] / 2 (quadrature-only in the note),
(iii) exact sqrt(n) D_n at n = 400 and 900 (from check_selection_d5_sweep.py `values`), to test the
     effective bound |sqrt(n) D_n - delta_K| <= C_K / n with the note's C_K.
These are consistency checks of the proof's OUTPUT, not a re-derivation of its interval constants.

Run:  python reviews/checks/check_selection_d5_constants.py
"""
from __future__ import annotations

import subprocess
import sys
from math import log, sqrt

import mpmath as mp

mp.mp.dps = 30

phi = lambda x: mp.npdf(x)
Phi = lambda x: mp.ncdf(x)


def E_max_moment(K, r):
    return mp.quad(lambda x: x**r * K * Phi(x) ** (K - 1) * phi(x), [-mp.inf, 0, mp.inf])


def H_derivs(K):
    # H_K(u) = (K/2) u (1-u) - varphi_K(u),  2 varphi_K(u) = 1 - u^K - (1-u)^K
    u = mp.mpf
    H = lambda t: K / mp.mpf(2) * t * (1 - t) - (1 - t**K - (1 - t) ** K) / 2
    return [lambda t, j=j: mp.diff(H, t, j) for j in range(5)]


def delta_K(K):
    H = H_derivs(K)
    psi = lambda b: phi(b) * (b**3 - b) / 12
    chi = lambda z: psi(z) - z * phi(z) / 2
    p = lambda z: z**2 / 2 - z**4 / 12 - mp.mpf(1) / 4
    I1 = mp.quad(lambda z: H[1](Phi(z)) * psi(z), [-mp.inf, 0, mp.inf])
    I2 = mp.quad(lambda z: phi(z) ** 2 * (2 * p(z) * H[2](Phi(z)) + H[3](Phi(z)) * chi(z)), [-mp.inf, 0, mp.inf])
    I3 = mp.quad(lambda z: phi(z) ** 4 * H[4](Phi(z)), [-mp.inf, 0, mp.inf])
    return (I1 + I2 + I3 / 12) / 2


def exact_sqrtn_D(K, ns):
    out = subprocess.run([sys.executable, "-I", __file__.replace("constants", "sweep"), "values", str(K), *map(str, ns)],
                         capture_output=True, text=True, check=True).stdout
    vals = {}
    for line in out.strip().splitlines():
        parts = dict(tok.rstrip(":").split("=") for tok in line.split() if "=" in tok)
        vals[int(parts["n"])] = float(parts["sqrt(n)*D_n"])
    return vals


def main():
    print("Gaussian constants (quadrature):")
    table = {2: (0.56419, 0.90775), 3: (0.84628, 0.91051), 5: (1.16296, 0.91403), 10: (1.53875, 0.91873), 100: (2.50759, 0.93256)}
    for K, (em, ck) in table.items():
        E1 = E_max_moment(K, 1)
        lamK = log(K) - (K - 1) / K
        c = float(E1) / sqrt(2 * lamK)
        print(f"  K={K}: E[M_K]={float(E1):.5f} (note {em}), c_K={c:.5f} (note {ck})  [{'OK' if abs(float(E1)-em)<6e-6 and abs(c-ck)<6e-6 else 'FAIL'}]")
    print("closed forms: K=2 1/sqrt(pi)=%.6f, K=3 3/(2sqrt(pi))=%.6f, K=4 6 atan(sqrt2)/pi^1.5=%.6f" % (1 / sqrt(mp.pi), 3 / (2 * sqrt(mp.pi)), 6 * mp.atan(sqrt(2)) / mp.pi**1.5))

    print("\nSecond-order margin delta_K and c(K):")
    C = {4: 0.741294, 5: 1.852897, 6: 3.2488, 8: 6.749227, 10: 11.11855, 15: 25.722004, 20: 45.586835, 25: 71.196006, 30: 103.723039}
    cK_note = {4: 0.020561, 5: 0.045497, 10: 0.15910, 20: 0.30889}
    results = {}
    for K in [4, 5, 10, 20, 30]:
        E1 = E_max_moment(K, 1)
        E3 = E_max_moment(K, 3)
        cK = (E3 - mp.mpf(5) / 2 * E1) / (6 * E1)
        dK = delta_K(K)
        ident = cK * E1 / 2
        results[K] = (float(dK), float(cK), float(E1))
        flag = "OK" if abs(float(dK - ident)) < 1e-8 else "FAIL"
        note = f" (note c({K})={cK_note[K]})" if K in cK_note else ""
        print(f"  K={K}: delta_K={float(dK):.9f}  c(K)E[M_K]/2={float(ident):.9f}  c(K)={float(cK):.6f}{note}  [identity {flag}]")

    print("\nEffective bound |sqrt(n) D_n - delta_K| <= C_K/n at n=400, 900 (exact D_n, float delta_K):")
    for K in [4, 10, 20, 30]:
        vals = exact_sqrtn_D(K, [400, 900])
        dK = results[K][0]
        for n, v in vals.items():
            dev = v - dK
            bound = C[K] / n
            print(f"  K={K} n={n}: sqrt(n)D_n={v:.9f} delta_K={dK:.9f} dev={dev:+.3e} n*dev={n*dev:+.4f} C_K/n={bound:.3e}  [{'OK' if abs(dev) <= bound else 'FAIL'}]  ratio bound/|dev| = {bound/abs(dev):.1f}")


if __name__ == "__main__":
    main()
