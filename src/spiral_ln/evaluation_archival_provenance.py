"""ADG-05: exact Bayesian planning with copied reports and source revocation.

Every numerical result is a finite synthetic law under known likelihoods.
No hidden outcomes are available to the policies.  Independent source origins
are conditional on H; deterministic copies share their origin's report.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
from math import prod

MISSING = -1
# local state: accessible, report, noisy audit, definitive registry status
EMPTY = (0, MISSING, MISSING, MISSING)
OPEN = (1, MISSING, MISSING, MISSING)


@dataclass(frozen=True)
class Source:
    prior: F  # P(valid)
    accuracy: F  # P(report = H | valid); invalid report is fair noise
    gates: int = 0  # unit-cost catalogue hops
    fetch: int = 1
    audit: F = F(3, 4)  # symmetric accuracy for validity

    def __post_init__(self):
        if not 0 < self.prior < 1 or not F(1,2) <= self.accuracy <= 1 or not F(1,2) <= self.audit <= 1:
            raise ValueError('invalid source parameters')
        if self.gates not in (0,1,2) or self.fetch < 1:
            raise ValueError('invalid cost')


@lru_cache(maxsize=None)
def likelihood(src, local, h):
    """Marginal likelihood of the observed origin history conditional on H."""
    _, report, audit, registry = local
    result = F(0)
    for valid in (0,1):
        if registry != MISSING and registry != valid:
            continue
        weight = src.prior if valid else 1-src.prior
        if report != MISSING:
            acc = src.accuracy if valid else F(1,2)
            weight *= acc if report == h else 1-acc
        if audit != MISSING:
            weight *= src.audit if audit == valid else 1-src.audit
        result += weight
    return result


@dataclass(frozen=True)
class Result:
    correct: F = F(0)
    false: F = F(0)
    abstain: F = F(0)
    spent: F = F(0)
    audit: F = F(0)
    registry: F = F(0)
    gated: F = F(0)

    @property
    def utility(self):
        return self.correct - 4*self.false

    def weighted(self, w):
        return Result(*(v*w for v in vars(self).values()))

    def __add__(self, other):
        return Result(*(a+b for a,b in zip(vars(self).values(),vars(other).values())))


class Planner:
    """A source-factor ledger and exact finite-horizon decision oracle.

    Reward = +1 correct, -4 false, 0 abstain; ties favor stopping. The
    true distribution always grades outcomes, even for misspecified policies.
    """
    def __init__(self, sources, copies=3, order=None):
        self.sources = tuple(sources)
        self.copies = copies
        self.order = tuple(range(len(sources))) if order is None else tuple(order)
        self.initial = tuple((s.gates, 1, -1,-1) if i == 0 else EMPTY for i,s in enumerate(sources))
        # Instance-local caches permit reclaiming all root state after each census row.
        for name in ('masses','posterior','actions','transitions','value','macro_value','evaluate'):
            setattr(self, name, lru_cache(None)(getattr(self,name)))

    def masses(self, state, naive=False):
        # Naive arm treats replicated report as separate origins; audit and registry
        # still update the original factor. This is an intentional misspecification.
        return tuple(prod(likelihood(s,o,h) * (likelihood(s,(o[0],o[1],-1,-1),h)**(self.copies-1) if naive and i==0 else 1)
                          for i,(s,o) in enumerate(zip(self.sources,state))) for h in (0,1))

    def posterior(self, state, naive=False):
        a,b = self.masses(state,naive)
        return b/(a+b)

    def actions(self, state, budget):
        out=[]
        for i in self.order:
            src=self.sources[i]; g,r,a,v=state[i]
            if g < src.gates:
                if budget>=1: out.append((i,'gate',1))
                continue
            if r<0:
                if budget>=src.fetch: out.append((i,'fetch',src.fetch))
                continue
            if a<0 and v<0 and budget>=1: out.append((i,'audit',1))
            if v<0 and budget>=2: out.append((i,'registry',2))
        return tuple(out)

    def transitions(self,state,action):
        i,kind,cost=action; g,r,a,v=state[i]
        if kind=='gate':
            nexts=[(g+1,r,a,v)]
        elif kind=='fetch': nexts=[(g,y,a,v) for y in (0,1)]
        elif kind=='audit': nexts=[(g,r,y,v) for y in (0,1)]
        elif kind=='registry': nexts=[(g,r,a,y) for y in (0,1)]
        else: raise ValueError(kind)
        den=sum(self.masses(state)); out=[]
        for local in nexts:
            nxt=state[:i]+(local,)+state[i+1:]
            p=sum(self.masses(nxt))/den
            if p: out.append((p,nxt))
        assert sum(p for p,_ in out)==1
        return tuple(out)

    def decision(self,state,naive=False):
        p=self.posterior(state,naive)
        if p>F(4,5): return 1
        if p<F(1,5): return 0
        return None

    def stop(self,state,naive=False):
        d=self.decision(state,naive)
        if d is None: return Result(abstain=F(1))
        p=self.posterior(state)
        correct=p if d==1 else 1-p
        return Result(correct=correct,false=1-correct)

    def value(self,state,budget,horizon):
        best=self.stop(state).utility; action=None
        if horizon>0:
            for a in self.actions(state,budget):
                q=sum(p*self.value(nxt,budget-a[2],horizon-1)[0] for p,nxt in self.transitions(state,a))
                if q>best: best,action=q,a
        return best,action

    def macro_value(self,state,budget):
        """Strong myopic control: price whole deterministic catalogue+fetch chain.

        Each macro forecasts one stochastic observation, then replans; it cannot
        see value that needs multiple stochastic observations to cross threshold.
        """
        best=self.stop(state).utility; choice=None
        for i in self.order:
            s=self.sources[i]; g,r,_,_=state[i]
            if r<0 and g<s.gates:
                total=s.gates-g+s.fetch
                if total>budget: continue
                opened=state[:i]+((s.gates,r,-1,-1),)+state[i+1:]
                a=(i,'fetch',s.fetch)
                q=sum(p*self.stop(nxt).utility for p,nxt in self.transitions(opened,a))
                if q>best: best,choice=q,(i,'gate',1)
        for a in self.actions(state,budget):
            q=sum(p*self.stop(nxt).utility for p,nxt in self.transitions(state,a))
            if q>best: best,choice=q,a
        return best,choice

    def evaluate(self,state,budget,mode):
        if mode=='copies': return self.stop(state,True)
        if mode=='stop': return self.stop(state)
        if mode=='macro': a=self.macro_value(state,budget)[1]
        else:
            horizon={'one':1,'two':2,'full':budget}[mode]
            a=self.value(state,budget,min(budget,horizon))[1]
        if a is None: return self.stop(state)
        result=Result(spent=F(a[2]),audit=F(a[1]=='audit'),registry=F(a[1]=='registry'),gated=F(a[1]=='gate'))
        for p,nxt in self.transitions(state,a):
            result+=self.evaluate(nxt,budget-a[2],mode).weighted(p)
        return result

    def run(self,budget,mode):
        return self.evaluate(self.initial,budget,mode)

    def clear(self):
        for name in ('masses','posterior','actions','transitions','value','macro_value','evaluate'):
            getattr(self,name).cache_clear()


def profiles():
    """72 exact development cells, not 72 independent historical populations."""
    for prior in (F(1,3),F(2,3),F(5,6)):
        for acc in (F(3,4),F(1)):
            for gate in (1,2):
                for budget in (3,4,5):
                    for audit in (F(2,3),F(5,6)):
                        sources=(Source(prior,acc,audit=audit),Source(F(5,6),F(1),gates=gate,fetch=1,audit=audit),
                                 Source(F(2,3),F(3,4),fetch=1,audit=audit))
                        yield sources,budget


def exhaustive_likelihood(src, local, h):
    """Independent sum over complete report, audit, validity assignments."""
    _, observed_r, observed_a, observed_v=local
    total=F(0)
    for v in (0,1):
        for r in (0,1):
            for a in (0,1):
                if any(x!=-1 and x!=y for x,y in ((observed_r,r),(observed_a,a),(observed_v,v))): continue
                pv=src.prior if v else 1-src.prior
                pa=src.audit if a==v else 1-src.audit
                acc=src.accuracy if v else F(1,2)
                pr=acc if r==h else 1-acc
                total+=pv*pa*pr
    return total


def revocation_witness():
    """Two equal current posteriors require opposite updates after revoking A."""
    s=Source(F(2,3),F(1))
    p=Planner((s,s))
    left=((0,1,-1,-1),(0,0,-1,-1))
    right=((0,0,-1,-1),(0,1,-1,-1))
    revoked=lambda st: ((0,st[0][1],-1,0),st[1])
    return {'left_before':p.posterior(left),'right_before':p.posterior(right),
            'left_after':p.posterior(revoked(left)),'right_after':p.posterior(revoked(right)),
            'left_after_naive_copies':p.posterior(revoked(left),True),
            'right_after_naive_copies':p.posterior(revoked(right),True)}


def brute_value(sources,budget):
    """Independent latent-world decision tree for small budgets.

    Enumerates H and complete (valid, report, audit) triples.  It neither
    calls the factorized likelihood/transition code nor uses Planner states.
    Initial report is 1.  Each list of worlds is an unnormalized measure.
    """
    from itertools import product
    worlds=[]
    for h in (0,1):
        for assignment in product(tuple(product((0,1),repeat=3)),repeat=len(sources)):
            if assignment[0][1]!=1: continue
            w=F(1,2)
            for s,(v,r,a) in zip(sources,assignment):
                w*=s.prior if v else 1-s.prior
                acc=s.accuracy if v else F(1,2)
                w*=acc if h==r else 1-acc
                w*=s.audit if a==v else 1-s.audit
            if w: worlds.append((h,assignment,w))
    initial_mass=sum(x[2] for x in worlds)
    # A is observed. Separate stage counters and query-history flags.
    def walk(rows,remaining,gates,observed):
        zero=sum(w for h,_,w in rows if h==0); one=sum(w for h,_,w in rows if h==1)
        best=max(F(0),zero-4*one,one-4*zero)
        for i,s in enumerate(sources):
            if gates[i]<s.gates:
                if remaining>=1:
                    gg=list(gates); gg[i]+=1
                    best=max(best,walk(rows,remaining-1,tuple(gg),observed))
                continue
            flags=observed[i]
            possibilities=[]
            if 'r' not in flags:
                if remaining>=s.fetch: possibilities.append(('r',1,s.fetch))
            else:
                if 'a' not in flags and 'v' not in flags and remaining>=1: possibilities.append(('a',2,1))
                if 'v' not in flags and remaining>=2: possibilities.append(('v',0,2))
            for key,col,cost in possibilities:
                oo=list(observed); oo[i]=flags+key
                groups=([x for x in rows if x[1][i][col]==j] for j in (0,1))
                value=sum(walk(group,remaining-cost,gates,tuple(oo)) for group in groups if group)
                best=max(best,value)
        return best
    return walk(worlds,budget,tuple(s.gates if i==0 else 0 for i,s in enumerate(sources)),tuple('r' if i==0 else '' for i in range(len(sources))))/initial_mass
