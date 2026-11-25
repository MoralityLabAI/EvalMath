"""Deterministic cooperative fuel and resumable exact coefficient calculations.
A unit is a generator advance, including the final return. Each yielded step
bounds one small recurrence/loop action for graphs of at most ten vertices.
This is logical fuel, not a Python instruction, memory, or time limit.
"""
from collections import Counter
from itertools import combinations
from math import comb


class Exhausted(Exception):
    pass


class Meter:
    def __init__(self, cap):
        if type(cap) is not int or cap < 0:
            raise ValueError('fuel cap')
        self.cap = cap
        self.used = 0
        self.ledger = Counter()

    @property
    def left(self):
        return self.cap - self.used

    def tick(self, phase, n=1):
        if type(n) is not int or n < 1:
            raise ValueError('positive integer charge required')
        if n > self.left:
            raise Exhausted
        self.used += n
        self.ledger[phase] += n

    def fork(self):
        other = Meter(self.cap)
        other.used = self.used
        other.ledger = self.ledger.copy()
        return other


class Task:
    def __init__(self, gen):
        self.gen = gen
        self.done = False
        self.result = None
        self.steps = 0

    def advance(self, meter, phase, quantum=None):
        """Resume with at most quantum charged steps. No result before return."""
        if quantum is not None and (type(quantum) is not int or quantum < 0):
            raise ValueError('quantum')
        start = self.steps
        while not self.done and (quantum is None or self.steps-start < quantum):
            if not meter.left:
                break
            meter.tick(phase)
            self.steps += 1
            try:
                next(self.gen)
            except StopIteration as e:
                self.result = e.value
                self.done = True
        return self.done

    def require(self, meter, phase):
        if not self.advance(meter, phase):
            raise Exhausted
        return self.result


def coefficient_task(g, inv, ks, vector=False):
    """Generator for targeted or shared vector recurrences. Pure until return."""
    n, edges = g
    if not 1 <= n <= 10:
        raise ValueError('graph order outside bounded gym')
    full = (1 << n)-1
    adj = [0]*n
    for a,b in edges:
        yield
        adj[a] |= 1 << b
        adj[b] |= 1 << a
    if inv == 'clique':
        for i in range(n):
            yield
            adj[i] = full ^ (1 << i) ^ adj[i]
    ks = tuple(range(n+1)) if vector else tuple(ks)
    if any(not 0 <= k <= n for k in ks):
        raise ValueError('coefficient index')
    memo = {}
    if inv in ('independence','clique','matching'):
        matching = inv == 'matching'
        if vector:
            def vec(s):
                yield
                if s in memo:
                    return memo[s]
                if not s:
                    return (1,)
                bit=s&-s;v=bit.bit_length()-1;rest=s^bit
                a=list((yield from vec(rest)))
                children=[]
                if matching:
                    nbr=adj[v]&rest
                    while nbr:
                        yield
                        u=nbr&-nbr;nbr^=u;children.append(rest^u)
                else:
                    children.append(rest&~adj[v])
                for child in children:
                    yield
                    p=yield from vec(child)
                    a.extend([0]*max(0,len(p)+1-len(a)))
                    for j,x in enumerate(p):
                        yield
                        a[j+1]+=x
                memo[s]=tuple(a)
                return memo[s]
            a=yield from vec(full)
            return a+(0,)*(n+1-len(a))
        def count(s,k):
            yield
            key=s,k
            if key in memo:
                return memo[key]
            if k==0:
                return 1
            if k<0 or s.bit_count()<k*(2 if matching else 1):
                return 0
            if not matching and k==1:
                return s.bit_count()
            bit=s&-s;v=bit.bit_length()-1;rest=s^bit
            total=yield from count(rest,k)
            if matching:
                nbr=adj[v]&rest
                while nbr:
                    yield
                    u=nbr&-nbr;nbr^=u
                    total+=yield from count(rest^u,k-1)
            else:
                total+=yield from count(rest&~adj[v],k-1)
            memo[key]=total
            return total
        out=[]
        for k in ks:
            yield
            out.append((yield from count(full,k)))
        return tuple(out)
    if inv=='domination':
        closed=[]
        for i,a in enumerate(adj):
            yield
            closed.append(a|(1<<i))
        if vector:
            cover=[0]*(full+1);out=[0]*(n+1)
            for s in range(1,full+1):
                yield
                b=s&-s;cover[s]=cover[s^b]|closed[b.bit_length()-1]
                if cover[s]==full:
                    out[s.bit_count()]+=1
            return tuple(out)
        out=[]
        for k in ks:
            yield
            total=0
            for sub in combinations(closed,k):
                yield
                cover=0
                for a in sub:
                    yield
                    cover|=a
                    if cover==full:
                        total+=1;break
            out.append(total)
        return tuple(out)
    if inv=='chromatic':
        ind=[True]+[False]*full
        for s in range(1,full+1):
            yield
            b=s&-s;ind[s]=ind[s^b] and not(adj[b.bit_length()-1]&(s^b))
        if vector:
            def parts(s):
                yield
                if not s:return (1,)
                if s in memo:return memo[s]
                b=s&-s;u0=(s^b)&~adj[b.bit_length()-1];u=u0
                a=[0]*(s.bit_count()+1)
                while True:
                    yield
                    if ind[u]:
                        vals=yield from parts(s^(u|b))
                        for j,c in enumerate(vals):
                            yield
                            a[j+1]+=c
                    if not u:break
                    u=(u-1)&u0
                memo[s]=tuple(a);return memo[s]
            counts=yield from parts(full)
        else:
            def part(s,k):
                yield
                key=s,k
                if key in memo:return memo[key]
                if not s:return int(k==0)
                size=s.bit_count()
                if k<=0 or k>size:return 0
                if k==size:return 1
                if k==1:return int(ind[s])
                b=s&-s;u0=(s^b)&~adj[b.bit_length()-1];u=u0;total=0
                while True:
                    yield
                    if u.bit_count()<=size-k and ind[u]:
                        total+=yield from part(s^(b|u),k-1)
                    if not u:break
                    u=(u-1)&u0
                memo[key]=total;return total
            counts=[0]*(n+1)
            for k in range(min(ks,default=n+1),n+1):
                yield
                counts[k]=yield from part(full,k)
        # Falling-factorial coefficients; shared exact signed Stirling table.
        stir=[[1]]
        for j in range(1,n+1):
            yield
            row=[0]*(j+1)
            for i,c in enumerate(stir[-1]):
                yield
                row[i]-=(j-1)*c;row[i+1]+=c
            stir.append(row)
        out=[]
        for k in ks:
            yield
            total=0
            for j in range(k,n+1):
                yield
                total+=counts[j]*stir[j][k]
            out.append(total)
        return tuple(out)
    raise ValueError(inv)
