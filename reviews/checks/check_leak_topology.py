"""Independent reconstruction of leak topology Theorems 1, 7, 8 and Counterexample 9 / Proposition 10.

Everything is rebuilt from the note's definitions: category maps as partitions, cells as nonempty
intersections, margin matrices with one 0/1 row per observed block-tuple, the nerve K_P, links,
rank-selected subcomplexes, merged-colour graphs, and the connecting map Psi of Theorem 8.
Ranks over Q by fraction-free elimination; simplicial homology over Q (and over Z via Smith normal
form is not needed for the dimension claims, which are rational).  Nothing imported from spiral_ln.

Run:  python reviews/checks/check_leak_topology.py
"""
from __future__ import annotations

import itertools
import random
from fractions import Fraction


# ------------------------------------------------------------------ linear algebra over Q
def rank(rows):
    M = [[Fraction(v) for v in r] for r in rows]
    if not M:
        return 0
    r = 0
    ncol = len(M[0])
    for c in range(ncol):
        piv = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c] / M[r][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        r += 1
        if r == len(M):
            break
    return r


def kernel_basis(rows, ncol):
    """Rational kernel basis of the matrix with the given rows (as lists)."""
    M = [[Fraction(v) for v in r] for r in rows]
    pivots = []
    r = 0
    for c in range(ncol):
        piv = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        M[r] = [v / M[r][c] for v in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        pivots.append(c)
        r += 1
        if r == len(M):
            break
    free = [c for c in range(ncol) if c not in pivots]
    basis = []
    for f in free:
        v = [Fraction(0)] * ncol
        v[f] = Fraction(1)
        for i, pc in enumerate(pivots):
            v[pc] = -M[i][f]
        basis.append(v)
    return basis


# ------------------------------------------------------------------ cells, margins, nerve
def cells_of(maps, n):
    """maps: list of partitions (list of blocks, each a set of items). Returns dict cell(tuple of block
    indices) -> set of items."""
    out = {}
    for item in range(n):
        key = tuple(next(b for b, blk in enumerate(m) if item in blk) for m in maps)
        out.setdefault(key, set()).add(item)
    return out


def margin_rows(cells, faces):
    """One row per observed block-tuple of each face S (a tuple of map indices)."""
    cl = sorted(cells)
    rows = []
    for S in faces:
        groups = sorted({tuple(c[j] for j in S) for c in cl})
        for g in groups:
            rows.append([1 if tuple(c[j] for j in S) == g else 0 for c in cl])
    return cl, rows


def fibre_dim(cells, faces):
    cl, rows = margin_rows(cells, faces)
    return len(cl) - rank(rows)


def nerve(cells, k):
    """Simplicial complex on vertices (map j, block b): faces = subsets of blocks with a common cell."""
    verts = sorted({(j, c[j]) for c in cells for j in range(k)})
    faces = set()
    for c in cells:
        vs = tuple((j, c[j]) for j in range(k))
        for r in range(1, k + 1):
            for sub in itertools.combinations(vs, r):
                faces.add(sub)
    return verts, faces


def betti(faces):
    """Reduced Betti numbers over Q of a simplicial complex given by its face set (tuples of vertices,
    sorted). Includes the empty face for reduced homology."""
    byd = {}
    for f in faces:
        byd.setdefault(len(f) - 1, []).append(tuple(sorted(f)))
    for d in byd:
        byd[d].sort()
    maxd = max(byd) if byd else -1
    idx = {d: {f: i for i, f in enumerate(byd[d])} for d in byd}
    ranks = {}
    for d in range(0, maxd + 1):
        if d == 0:
            # augmentation
            rows = [[1] * len(byd[0])]
        else:
            rows = []
            for f in byd[d]:
                row = [0] * len(byd[d - 1])
                for i in range(len(f)):
                    g = f[:i] + f[i + 1:]
                    row[idx[d - 1][g]] = (-1) ** i
                rows.append(row)
            rows = [list(col) for col in zip(*rows)] if rows else []
        ranks[d] = rank(rows) if rows and rows[0] else 0
    b = {}
    for d in range(0, maxd + 1):
        nd = len(byd[d])
        b[d] = nd - ranks[d] - ranks.get(d + 1, 0)
    return b


def link(faces, sigma):
    sig = set(sigma)
    out = set()
    for f in faces:
        if sig.isdisjoint(f) and tuple(sorted(set(f) | sig)) in faces:
            out.add(f)
    return out


def rank_selected(faces, colours):
    return {f for f in faces if all(v[0] in colours for v in f)}


def graph_components(vertices, edges):
    parent = {v: v for v in vertices}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    comps = {}
    for v in vertices:
        comps.setdefault(find(v), set()).add(v)
    return list(comps.values())


def beta1_graph(vertices, edges):
    return len(edges) - len(vertices) + len(graph_components(vertices, edges))


# ------------------------------------------------------------------ Theorem 8 for three maps, separate
def theorem8(cells):
    """Separate observation of maps 0,1,2; project away map 2.  Returns f(P), beta1(G), f(P'), rank Psi
    and the predicted f(P) = beta1(G) + f(P') - rank Psi."""
    k = 3
    fP = fibre_dim(cells, [(0,), (1,), (2,)])
    Pp = {c[:2] for c in cells}  # merged support of maps 0,1
    fPp = fibre_dim({c: None for c in Pp}, [(0,), (1,)])
    # G: bipartite graph with vertices P' (cells of maps 0,1 merged) and blocks of map 2; edge per cell
    V = [("p", c[:2]) for c in Pp] + [("v", b) for b in sorted({c[2] for c in cells})]
    E = [(("p", c[:2]), ("v", c[2])) for c in cells]
    b1G = beta1_graph(V, E)
    comps = graph_components(V, E)
    # Psi: y in ker M_sep(P') -> per-component sums over P' vertices
    clp, rowsp = margin_rows({c: None for c in Pp}, [(0,), (1,)])
    kb = kernel_basis(rowsp, len(clp))
    psi_rows = []
    for y in kb:
        psi_rows.append([sum(y[clp.index(v[1])] for v in C if v[0] == "p") for C in comps])
    rPsi = rank([list(col) for col in zip(*psi_rows)]) if psi_rows else 0
    return fP, b1G, fPp, rPsi, b1G + fPp - rPsi, len(comps)


def theorem7_link_formula(cells, k, W):
    """Delta = {S : W not subset of S}; dim ker = sum over R-cells r of tilde beta_{|W|-1}(lk r)."""
    R = [j for j in range(k) if j not in W]
    faces_obs = [tuple(sorted(set(range(k)) - {w})) for w in W]
    direct = fibre_dim(cells, faces_obs)
    verts, faces = nerve(cells, k)
    total = 0
    rcells = sorted({tuple(c[j] for j in R) for c in cells})
    for r in rcells:
        sigma = tuple((j, r[i]) for i, j in enumerate(R))
        if R:
            lk = link(faces, sigma)
        else:
            lk = faces
        b = betti(lk) if lk else {}
        total += b.get(len(W) - 1, 0)
    return direct, total


def main():
    print("== Theorem 1 on random pairs of maps: dim ker M = |E| - |V| + c")
    rng = random.Random(3)
    bad = 0
    for _ in range(400):
        n = rng.randint(3, 9)
        maps = []
        for _ in range(2):
            nb = rng.randint(1, min(4, n))
            lab = [rng.randrange(nb) for _ in range(n)]
            blocks = [set(i for i in range(n) if lab[i] == b) for b in range(nb)]
            maps.append([b for b in blocks if b])
        cells = cells_of(maps, n)
        f = fibre_dim(cells, [(0,), (1,)])
        V = [("r", c[0]) for c in cells] + [("c", c[1]) for c in cells]
        V = sorted(set(V))
        E = [(("r", c[0]), ("c", c[1])) for c in cells]
        if f != beta1_graph(V, E):
            bad += 1
    print(f"  400 random pairs: mismatches {bad}  [{'OK' if bad == 0 else 'FAIL'}]")

    print("\n== Counterexample 9: two triples on six items")
    P0 = [[{0, 1, 2, 3}, {4, 5}], [{0, 1, 4}, {2, 5}, {3}], [{0, 2}, {1, 5}, {3, 4}]]
    P1 = [[{0, 1, 2, 3}, {4, 5}], [{0, 1}, {2, 4}, {3, 5}], [{0, 4}, {1, 5}, {2, 3}]]
    sep = [(0,), (1,), (2,)]
    data = {}
    for name, maps in [("P0", P0), ("P1", P1)]:
        cells = cells_of(maps, 6)
        assert all(len(v) == 1 for v in cells.values()), "one item per cell"
        f = fibre_dim(cells, sep)
        verts, faces = nerve(cells, 3)
        b = betti(faces)
        fv = tuple(sum(1 for fc in faces if len(fc) == d) for d in (1, 2, 3))
        coloured_f = tuple(sorted(sum(1 for fc in faces if len(fc) == 1 and fc[0][0] == j) for j in range(3))) + \
                     tuple(sorted(sum(1 for fc in faces if len(fc) == 2 and {v[0] for v in fc} == set(pair)) for pair in [(0, 1), (0, 2), (1, 2)])) + (fv[2],)
        rs = {}
        for pair in [(0, 1), (0, 2), (1, 2)]:
            sub = rank_selected(faces, set(pair))
            vs = [fc for fc in sub if len(fc) == 1]
            es = [fc for fc in sub if len(fc) == 2]
            rs[pair] = (len(graph_components([v[0] for v in vs], [(e[0], e[1]) for e in es])), beta1_graph([v[0] for v in vs], [(e[0], e[1]) for e in es]))
        # vertex links: as multiset of (betti0_reduced, betti1) data; and whether forests
        vlinks = sorted((len(link(faces, v)), betti(link(faces, v)).get(0, 0), betti(link(faces, v)).get(1, 0)) for v in [fc for fc in faces if len(fc) == 1])
        elinks = sorted(len(link(faces, e)) for e in [fc for fc in faces if len(fc) == 2])
        # merged-colour graphs: merge maps a,b into one map, intersection graph with the third
        merged = {}
        for (a, b2), c in [((0, 1), 2), ((0, 2), 1), ((1, 2), 0)]:
            V = sorted({("m", (cl[a], cl[b2])) for cl in cells} | {("s", cl[c]) for cl in cells})
            E = [(("m", (cl[a], cl[b2])), ("s", cl[c])) for cl in cells]
            merged[(a, b2)] = (len(graph_components(V, E)), beta1_graph(V, E))
        t8 = theorem8(cells)
        data[name] = dict(f=f, betti=b, fvec=fv, coloured_f=coloured_f, rank_selected=rs, vlinks=vlinks, elinks=elinks, merged=merged, t8=t8)
        print(f"  {name}: f = {f}; nerve reduced Betti = {b}; f-vector {fv}; coloured face numbers {coloured_f}")
        print(f"       rank-selected 2-map graphs (components, beta1): {rs}")
        print(f"       vertex links (size, b0~, b1): {vlinks}")
        print(f"       edge links (sizes): {elinks}; merged-colour graphs (components, beta1): {merged}")
        print(f"       Theorem 8: f(P)={t8[0]}, beta1(G)={t8[1]}, f(P')={t8[2]}, rank Psi={t8[3]}, predicted {t8[4]}, components of G {t8[5]}")
    checks = {
        "f(P0)=0, f(P1)=1": (data["P0"]["f"], data["P1"]["f"]) == (0, 1),
        "nerves have b1=3, b0~=b2=0 (wedge of three circles, rationally)": all(d["betti"].get(1) == 3 and d["betti"].get(0, 0) == 0 and d["betti"].get(2, 0) == 0 for d in data.values()),
        "three rank-selected graphs connected with beta1=1 in both": all(all(v == (1, 1) for v in d["rank_selected"].values()) for d in data.values()),
        "vertex links agree as multisets of HOMOTOPY TYPES (reduced Betti numbers)": sorted(v[1:] for v in data["P0"]["vlinks"]) == sorted(v[1:] for v in data["P1"]["vlinks"]),
        "vertex links agree as multisets of GRAPHS (face counts) -- the note's wording 'multisets of forests'": data["P0"]["vlinks"] == data["P1"]["vlinks"],
        "edge-link data agree": data["P0"]["elinks"] == data["P1"]["elinks"],
        "merged-colour graphs: two trees each (c=2, beta1=0)": all(all(v == (2, 0) for v in d["merged"].values()) for d in data.values()),
        "coloured face numbers agree (2,3,3;5,5,6;6)": data["P0"]["coloured_f"] == data["P1"]["coloured_f"] == (2, 3, 3, 5, 5, 6, 6),
        "Theorem 8 exact in both": all(d["t8"][0] == d["t8"][4] for d in data.values()),
        "Theorem 8: beta1(G)=0, f(P')=1, rank Psi = 1 (P0) / 0 (P1), G has two components": data["P0"]["t8"][1:4] == (0, 1, 1) and data["P1"]["t8"][1:4] == (0, 1, 0) and data["P0"]["t8"][5] == data["P1"]["t8"][5] == 2,
    }
    for k_, v in checks.items():
        print(f"  [{'OK' if v else 'FAIL'}] {k_}")
    # record-level: P1 confuses 101001 with 010110
    cells1 = cells_of(P1, 6)
    cl, rows = margin_rows(cells1, sep)
    def margins(rec):
        x = [sum(rec[i] for i in cells1[c]) for c in cl]
        return tuple(sum(a * b for a, b in zip(r, x)) for r in rows)
    r1 = [int(ch) for ch in "101001"]; r2 = [int(ch) for ch in "010110"]
    print(f"  [{'OK' if margins(r1) == margins(r2) and r1 != r2 else 'FAIL'}] P1: records 101001 and 010110 have equal separate margins")
    cells0 = cells_of(P0, 6)
    cl0, rows0 = margin_rows(cells0, sep)
    seen = {}
    clash = False
    for rec in itertools.product([0, 1], repeat=6):
        x = [sum(rec[i] for i in cells0[c]) for c in cl0]
        m = tuple(sum(a * b for a, b in zip(r, x)) for r in rows0)
        if m in seen:
            clash = True
        seen[m] = rec
    print(f"  [{'OK' if not clash else 'FAIL'}] P0: separate margins reveal every record (64 distinct margin vectors)")

    print("\n== Theorem 7 (link formula) vs direct rank, all coordinate-surjective supports of 2x2x2, every W")
    grid = list(itertools.product(range(2), repeat=3))
    supports = [s for r in range(1, 9) for s in itertools.combinations(grid, r) if all({c[j] for c in s} == {0, 1} for j in range(3))]
    print(f"  supports: {len(supports)}")
    mism = 0
    ncmp = 0
    for s in supports:
        cells = {c: None for c in s}
        for Wsize in (1, 2, 3):
            for W in itertools.combinations(range(3), Wsize):
                d, t = theorem7_link_formula(cells, 3, W)
                ncmp += 1
                if d != t:
                    mism += 1
    print(f"  comparisons {ncmp}, mismatches {mism}  [{'OK' if mism == 0 else 'FAIL'}]")

    print("\n== Theorem 8 on all 193 supports (project away map 2)")
    mism = 0
    rpos = 0
    for s in supports:
        t8 = theorem8({c: None for c in s})
        if t8[0] != t8[4]:
            mism += 1
        rpos += t8[3] > 0
    print(f"  mismatches {mism}; rank Psi > 0 in {rpos} supports  [{'OK' if mism == 0 else 'FAIL'}]")

    print("\n== Proposition 10 / non-local fibre vector: five cells (000),(001),(011),(101),(110)")
    five = {(0, 0, 0): None, (0, 0, 1): None, (0, 1, 1): None, (1, 0, 1): None, (1, 1, 0): None}
    cl, rows = margin_rows(five, sep)
    kb = kernel_basis(rows, 5)
    print("  cells", cl, " kernel basis", [[str(v) for v in b] for b in kb])
    z = [1, -2, 1, 1, -1]
    inker = all(sum(a * b for a, b in zip(r, z)) == 0 for r in rows)
    print(f"  [{'OK' if len(kb) == 1 and inker else 'FAIL'}] fibre dimension 1 and (1,-2,1,1,-1) is in the kernel")
    # unit capacity: no 0/1 difference is a nonzero multiple of z
    confused = any(all(abs(t * v) <= 1 for v in z) for t in range(1, 3))
    print(f"  [{'OK' if not confused else 'FAIL'}] no nonzero multiple of z fits unit cells -> item-level at unit capacity")
    # with cell (001) of size 2: records 100110 and 011001 under gamma0={0,1,2}|{3,4}, gamma1={0,1,3}|{2,4}, gamma2={0,4}|{1,2,3}
    maps = [[{0, 1, 2}, {3, 4, 5}], [{0, 1, 3}, {2, 4, 5}], [{0, 4, 5}, {1, 2, 3}]]  # item 5 added to cell (1,1,0)? check below
    # the note's maps are on five items with cell (001) doubled; realise by adding item 5 to the cell of item 1? find cell of each item:
    cells5 = cells_of([[{0, 1, 2}, {3, 4}], [{0, 1, 3}, {2, 4}], [{0, 4}, {1, 2, 3}]], 5)
    print("  five-item cells:", {c: sorted(v) for c, v in cells5.items()})
    # add a sixth item to cell (0,0,1): the item whose cell is (0,0,1)
    # The note does not say how the six items are numbered after doubling cell (001). Appending the new
    # item as item 5 does NOT reproduce the note's pair (the difference of the two records is then
    # (1,-2,-1,1,1), not +-z). Numbering the items by cell, (000),(001),(001),(011),(101),(110), does:
    maps6 = [[{0, 1, 2, 3}, {4, 5}], [{0, 1, 2, 4}, {3, 5}], [{0, 5}, {1, 2, 3, 4}]]
    cells6 = cells_of(maps6, 6)
    cl6, rows6 = margin_rows(cells6, sep)
    def marg6(rec):
        x = [sum(rec[i] for i in cells6[c]) for c in cl6]
        return tuple(sum(a * b for a, b in zip(r, x)) for r in rows6)
    ra = [int(ch) for ch in "100110"]; rb = [int(ch) for ch in "011001"]
    print(f"  [{'OK' if marg6(ra) == marg6(rb) else 'FAIL'}] with cell (001) doubled, 100110 and 011001 collide (cells: {dict((c, sorted(v)) for c, v in cells6.items())})")


if __name__ == "__main__":
    main()
