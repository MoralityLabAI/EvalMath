"""Independent finite free-leaf to charged-input circuit compiler."""
from itertools import product

LEAVES = (("x", 0), ("x", 1), ("c", -1), ("c", 0))
OPS = ("add", "sub", "mul")


def compile_charged(gates, out):
    """Each operand is a leaf tuple or earlier free-gate index. Return charged DAG."""
    charged = [("c", -1)]
    mapped = []

    def put(g):
        charged.append(g)
        return len(charged) - 1

    def operand(a):
        if isinstance(a, int):
            if not 0 <= a < len(mapped):
                raise ValueError("non-topological reference")
            return mapped[a]
        if len(a) != 2 or a[0] not in ("x", "c"):
            raise ValueError("invalid leaf")
        return put(a)

    for op, a, b in gates:
        i, j = operand(a), operand(b)
        if op == "sub":
            j = put(("mul", 0, j))
            op = "add"
        if op not in ("add", "mul"):
            raise ValueError("invalid operation")
        mapped.append(put((op, i, j)))
    k = operand(out)
    return tuple(charged), k


def leaf(a, p):
    tag, v = a
    return {(v,): 1} if tag == "x" else ({(): v % p} if v % p else {})


def arithmetic(op, a, b, p):
    r = {}
    if op == "mul":
        for x, v in a.items():
            for y, w in b.items():
                z = tuple(sorted(x + y))
                r[z] = (r.get(z, 0) + v*w) % p
    else:
        r.update(a)
        for z, w in b.items():
            r[z] = (r.get(z, 0) + (w if op == "add" else -w)) % p
    return {z: v for z, v in r.items() if v}


def free_polynomial(gates, out, p):
    table = []

    def value(a):
        return table[a] if isinstance(a, int) else leaf(a, p)

    for op, a, b in gates:
        table.append(arithmetic(op, value(a), value(b), p))
    return value(out)


def charged_polynomial(gates, out, p):
    table = []
    for k, gate in enumerate(gates):
        if gate[0] in ("x", "c"):
            table.append(leaf(gate, p))
        else:
            op, a, b = gate
            if op not in ("add", "mul") or not (0 <= a < k and 0 <= b < k):
                raise ValueError("invalid charged circuit")
            table.append(arithmetic(op, table[a], table[b], p))
    return table[out]


def programs(depth):
    if depth == 0:
        yield ()
        return
    for prefix in programs(depth-1):
        operands = LEAVES + tuple(range(depth-1))
        for gate in product(OPS, operands, operands):
            yield prefix + (gate,)


def census():
    counts = {}
    max_cost = {}
    for n in range(3):
        count = cost = 0
        for gates in programs(n):
            for out in LEAVES + tuple(range(n)):
                compiled, k = compile_charged(gates, out)
                assert len(compiled) <= 4*n + 2
                cost = max(cost, len(compiled))
                for p in (2, 3, 5):
                    assert free_polynomial(gates, out, p) == charged_polynomial(compiled, k, p)
                    count += 1
        counts[str(n)] = count
        max_cost[str(n)] = cost
    return {"field_program_checks": counts, "maximum_charged_gates": max_cost}
