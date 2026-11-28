"""Certified statement-mutation curriculum. Public prompts and gold are separate."""
from collections import Counter
from hashlib import sha256
from itertools import product

SPLITS = {"gate": "train", "degree": "train", "characteristic": "train",
          "uniformity": "dev", "approximation": "test", "polynomial": "test",
          "scope": "test"}
LABELS = {"entailed", "counterexample", "unresolved"}


def make_case(group, prompt, label, certificate, level):
    return {"id": sha256(prompt.encode()).hexdigest()[:20], "split": SPLITS[group],
            "group": group, "prompt": prompt, "label": label,
            "certificate": certificate, "evidence_level": level}


def cases():
    rows = []

    def add(group, prompt, label, certificate, level="paper_derivation"):
        rows.append(make_case(group, prompt, label, certificate, level))

    context = ("Over a field let O be minimum binary arithmetic gate count with free leaves and subtraction, "
               "and A minimum gate count with charged leaves and only addition/multiplication. "
               "The simulation gives O <= A <= 4*O+2. ")
    for claim, label, cert in (
        ("O <= A", "entailed", "The first simulation inequality."),
        ("A <= 4*O+2", "entailed", "The second simulation inequality."),
        ("For every natural B, O>B implies A>B", "entailed", "Transitivity of B<O<=A."),
        ("A <= O", "counterexample", "For f=x, O=0 and A=1."),
        ("A <= 4*O", "counterexample", "For f=x, O=0 and A=1."),
        ("For every natural B, A>B implies O>B", "counterexample", "For f=x and B=0, A=1 and O=0."),
    ):
        add("gate", context + "Assess: " + claim + ".", label, cert)

    for n, d in ((3, 3), (8, 2), (4, 3), (16, 3), (5, 3), (32, 4)):
        degree, cap = 2**n, n**d
        add("degree", f"Over any field start with x and square the previous polynomial {n} times. "
            f"Assess: the resulting formal polynomial has total degree at most {n}^{d}.",
            "entailed" if degree <= cap else "counterexample",
            f"Induction on squaring gives x^(2^{n}); degree={degree}, cap={cap}.")

    for p, equal in ((2, True), (3, True), (5, False), (7, True), (11, False), (13, True)):
        actual = p == 2
        prompt = f"Over F_{p}, assess: the formal permanent and determinant polynomials " + (
            "are identical in every positive matrix size." if equal else "differ in at least one matrix size.")
        cert = ("In characteristic two all permutation signs equal one, term by term." if actual else
                f"At size two, evaluate at the all-ones matrix: permanent={2 % p}, determinant=0.")
        add("characteristic", prompt, "entailed" if equal == actual else "counterexample", cert)

    context = ("For a relation R(i,n) on natural indices, pointwise eventual validity means "
               "forall i exists N forall n>=N R(i,n); uniform eventual validity means "
               "exists N forall i forall n>=N R(i,n). ")
    for claim, label, cert in (
        ("Uniform validity implies pointwise validity", "entailed", "Reuse the common N for each i."),
        ("Pointwise validity implies uniform validity", "counterexample", "R(i,n):=i<=n. Choose N=i pointwise; for any proposed common N, i=N+1,n=N fails."),
        ("On a nonempty finite index set, pointwise validity implies uniform validity", "entailed", "Take the maximum of the finitely many thresholds."),
        ("A uniform threshold N also works on every subset of the index set", "entailed", "Restrict the universal quantifier."),
        ("A threshold uniform on each singleton index set implies a global uniform threshold", "counterexample", "R(i,n):=i<=n. Every singleton has a threshold, but i=N+1,n=N defeats a global N."),
        ("Uniform validity on every finite nonempty subset implies uniform validity on all naturals", "counterexample", "R(i,n):=i<=n. Each finite subset has a maximum, but the full set does not."),
    ):
        add("uniformity", context + "Assess: " + claim + ".", label, cert)

    # Exhaust all abstract one-witness models, not the actual complexity classes.
    rules = (("If all approximate witnesses meet a bound, all exact witnesses meet it", "bound", False),
             ("If all exact witnesses meet a bound, all approximate witnesses meet it", "bound", True),
             ("If no approximate witness exists, no exact witness exists", "absence", False),
             ("If no exact witness exists, no approximate witness exists", "absence", True),
             ("If an exact witness exists, an approximate witness exists", "existence", False),
             ("If an approximate witness exists, an exact witness exists", "existence", True))
    for claim, kind, reverse in rules:
        bad = abstract_countermodels(kind, reverse)
        cert = ("Set inclusion E subset A gives the implication pointwise." if not bad else
                "One-element abstract universe; E,A,G membership bits=" + str(bad[0]) +
                ". The premise holds and the conclusion fails. This does not establish a circuit-complexity gap.")
        add("approximation", "In an abstract witness model E is a subset of A, for exact and approximate witnesses. "
            "A bound means a predicate G on witnesses. Assess: " + claim + ".",
            "counterexample" if bad else "entailed", cert, "abstract_logic")

    for p in (2, 3, 5):
        values = tuple((x**p-x) % p for x in range(p))
        for formal in (True, False):
            add("polynomial", f"Over F_{p}, compare x^{p}-x with the zero polynomial. Assess: they are " +
                ("equal as formal polynomials." if formal else "equal as functions on the field."),
                "counterexample" if formal else "entailed",
                (f"Coefficient of x^{p} is 1, not 0." if formal else f"Values at all field elements: {values}."),
                "finite_exact")

    context = ("Evidence packet: OpenAI comparator declares vp_ne_vnp on Fin n × Bool, and its scope note distinguishes exact "
               "Lean separation from the manuscript border bound. Anthropic Statement declares MainTheoremApprox using Laurent "
               "coefficients; Solution declares separationClosure : SeparationClosure. Only source interfaces were archived in "
               "EvalMath; no upstream proof rebuild, size-index equivalence or geometric closure certificate was supplied. "
               "Assess whether the following is established by this packet: ")
    for claim, label, cert in (
        ("OpenAI's comparator declares exact VP/VNP separation on families with variables Fin n × Bool.", "entailed", "Comparator.lean: vp_ne_vnp and Fin n × Bool."),
        ("Anthropic's statement declares a Laurent-series approximation lower-bound endpoint.", "entailed", "Statement.lean: Approximates and MainTheoremApprox."),
        ("Anthropic's solution exposes a proof endpoint of SeparationClosure.", "entailed", "Solution.lean: theorem separationClosure : SeparationClosure. This is a source declaration observation, not a local kernel audit."),
        ("Both quantitative border lower bounds admit a common canonical theorem via the published Lean endpoints.", "unresolved", "OpenAI's comparator is exact and the source interfaces supply no common canonical border theorem."),
        ("The different matrix/family size indices have a proved quantitative translation in EvalMath.", "unresolved", "No size-index equivalence certificate in CPF-02."),
        ("Laurent approximation agrees with the geometric border notion for every field in the releases.", "unresolved", "The Laurent definition alone supplies no geometric closure bridge."),
    ):
        add("scope", context + claim, label, cert, "pinned_interface_only")
    return rows


def abstract_countermodels(kind, reverse):
    bad = []
    for e, a, g in product((False, True), repeat=3):
        if e and not a:
            continue
        if kind == "bound":
            premise, conclusion = not a or g, not e or g
        elif kind == "absence":
            premise, conclusion = not a, not e
        elif kind == "existence":
            premise, conclusion = e, a
        else:
            raise ValueError(kind)
        if reverse:
            premise, conclusion = conclusion, premise
        if premise and not conclusion:
            bad.append((e, a, g))
    return bad


def exports():
    rows = cases()
    prompts = [{k: r[k] for k in ("id", "split", "prompt")} for r in rows]
    gold = [{k: r[k] for k in ("id", "split", "group", "label", "certificate", "evidence_level")} for r in rows]
    return prompts, gold


def summary():
    rows = cases()
    return {"cases": len(rows), "groups": dict(sorted(Counter(r["group"] for r in rows).items())),
            "splits": dict(sorted(Counter(r["split"] for r in rows).items())),
            "labels": dict(sorted(Counter(r["label"] for r in rows).items()))}
