"""ADG-06: finite Bayesian discovery with latent source lineage.

Integer mass arithmetic after exact rational enumeration. Only the evaluator
has a realized latent world. The planner conditions on public query outcomes.
"""
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from math import lcm

GRAPHS = ((0,0,0),(0,0,1),(0,1,0),(0,1,1),(0,1,2))
# All stochastic query fields are indices in a complete-world tuple.
FIELDS = ('C','clue_AB','lineage','audit_A','registry_A','registry_B','registry_C')
OUTCOMES = (2,2,5,2,2,2,2)
COSTS = (1,1,1,1,2,2,2)
GATE_C, GATE_LINEAGE = 7,8
NAMES = FIELDS + ('catalog_C','catalog_lineage')


@dataclass(frozen=True)
class Profile:
    independent_prior: F
    strong_prior: F
    clue_accuracy: F
    b_report: int
    budget: int
    c_gated: bool = True
    boundary: bool = False


def distribution(p):
    """P(H,G, observations | A=1,B=b_report); unnormalized integer masses.

    Weak/strong calibration is a common latent variable, so origin factors
    are independent only conditional on BOTH H and that calibration regime.
    Reports and validity are copied exactly within each origin block.
    """
    rows = defaultdict(F)
    for gi,g in enumerate(GRAPHS):
        pg = p.independent_prior if gi==4 else (1-p.independent_prior)/4
        n = max(g)+1
        for strong,h in product((0,1), repeat=2):
            pc = p.strong_prior if strong else 1-p.strong_prior
            q,acc,audit = (F(5,6),F(1),F(5,6)) if strong else (F(1,2),F(3,4),F(2,3))
            if p.boundary:
                q,acc,audit = (F(2,3),F(1),F(2,3)) if strong else (F(1,2),F(1),F(1,2))
            for valid in product((0,1), repeat=n):
                pv = pg*pc/2
                for v in valid: pv *= q if v else 1-q
                for reports in product((0,1), repeat=n):
                    if reports[g[0]]!=1 or reports[g[1]]!=p.b_report: continue
                    w = pv
                    for v,r in zip(valid,reports):
                        a = acc if v else F(1,2)
                        w *= a if r==h else 1-a
                    if not w: continue
                    for clue,au in product((0,1),repeat=2):
                        prob = w*(p.clue_accuracy if clue==int(g[0]==g[1]) else 1-p.clue_accuracy)
                        prob *= audit if au==valid[g[0]] else 1-audit
                        row = (h,gi,reports[g[2]],clue,gi,au,*(valid[i] for i in g))
                        rows[row] += prob
    rows = {r:w for r,w in rows.items() if w}
    den = lcm(*(w.denominator for w in rows.values()))
    return tuple((r,int(w*den)) for r,w in sorted(rows.items()))


class Oracle:
    def __init__(self,p,reverse=False):
        self.p=p
        rows=distribution(p)
        self.weights=tuple(w for _,w in rows)
        self.root=(1<<len(rows))-1
        self.hmask=tuple(sum(1<<i for i,(r,_) in enumerate(rows) if r[0]==h) for h in (0,1))
        self.gmask=tuple(sum(1<<i for i,(r,_) in enumerate(rows) if r[1]==g) for g in range(5))
        self.masks=tuple(tuple(sum(1<<i for i,(r,_) in enumerate(rows) if r[2+j]==y) for y in range(n)) for j,n in enumerate(OUTCOMES))
        self.order=tuple(reversed(range(9))) if reverse else tuple(range(9))
        self.open=0 if p.c_gated else 1
        self.costs=(3,1,1,2,4,4,4) if p.boundary else COSTS
        for name in ('mass','decision','terminal','value','macro','evaluate'):
            setattr(self,name,lru_cache(None)(getattr(self,name)))

    def mass(self,mask):
        total=0
        while mask:
            bit=mask&-mask; mask^=bit
            total+=self.weights[bit.bit_length()-1]
        return total

    def posterior(self,mask):
        return F(self.mass(mask&self.hmask[1]),self.mass(mask))

    def graph_posterior(self,mask):
        return tuple(F(self.mass(mask&m),self.mass(mask)) for m in self.gmask)

    def decision(self,mask):
        a,b=(self.mass(mask&m) for m in self.hmask)
        if b>4*a:return 1
        if a>4*b:return 0
        return -1

    def terminal(self,mask):
        a,b=(self.mass(mask&m) for m in self.hmask)
        return max(0,b-4*a,a-4*b)

    def actions(self,used,opened,budget,allow_lineage=True):
        for i in self.order:
            if used&(1<<i):continue
            if i==GATE_C:
                if not opened&1 and budget>=1:yield i,1
            elif i==GATE_LINEAGE:
                if allow_lineage and not opened&2 and budget>=1:yield i,1
            elif self.costs[i]<=budget:
                if i==0 and not opened&1:continue
                if i==2 and (not allow_lineage or not opened&2):continue
                if i==1 and not allow_lineage:continue
                if i==6 and not used&1:continue
                yield i,self.costs[i]

    def children(self,mask,used,opened,i):
        u=used|(1<<i)
        if i>=7:
            yield mask,u,opened|(1<<(i-7))
        else:
            for outcome in self.masks[i]:
                sub=mask&outcome
                if sub:yield sub,u,opened

    def value(self,mask,used,opened,budget,horizon,allow_lineage=True):
        best=self.terminal(mask); choice=-1; spent=0
        if not mask or not horizon:return best,choice,spent
        for i,c in self.actions(used,opened,budget,allow_lineage):
            descendants=[self.value(m,u,o,budget-c,horizon-1,allow_lineage) for m,u,o in self.children(mask,used,opened,i)]
            q=sum(z[0] for z in descendants)
            expense=c*self.mass(mask)+sum(z[2] for z in descendants)
            if (q,-expense)>(best,-spent):best,choice,spent=q,i,expense
        return best,choice,spent

    def macro(self,mask,used,opened,budget):
        best=self.terminal(mask); choice=-1; spent=0
        if not mask:return best,choice
        for i,c in self.actions(used,opened,budget):
            expense=c
            if i>=7:
                j=0 if i==7 else 2
                expense+=self.costs[j]
                if budget<expense:continue
                q=sum(self.terminal(mask&outcome) for outcome in self.masks[j])
            else:q=sum(self.terminal(m) for m,_,_ in self.children(mask,used,opened,i))
            if (q,-expense)>(best,-spent):best,choice,spent=q,i,expense
        return best,choice

    def evaluate(self,mask,used,opened,budget,mode,fixed=-1):
        """Unnormalized integer totals; score all policies against true mass."""
        belief=mask if fixed<0 else mask&self.gmask[fixed]
        if mode=='stop' or not belief: i=-1
        elif mode=='macro':i=self.macro(belief,used,opened,budget)[1]
        else:
            horizon={'one':1,'two':2}.get(mode,budget)
            i=self.value(belief,used,opened,budget,min(horizon,budget),mode!='no_lineage' and fixed<0)[1]
        mass=self.mass(mask)
        if i<0:
            d=self.decision(belief); g=max(range(5),key=lambda j:self.mass(belief&self.gmask[j])) if belief else -1
            correct=self.mass(mask&self.hmask[d]) if d>=0 else 0
            return (correct,mass-correct if d>=0 else 0,mass if d<0 else 0,0,0,0,
                    self.mass(mask&self.gmask[g]) if g>=0 else 0)
        c=1 if i>=7 else self.costs[i]
        totals=[0,0,0,c*mass,int(i in (1,2))*mass,int(i==2)*mass,0]
        for m,u,o in self.children(mask,used,opened,i):
            for j,z in enumerate(self.evaluate(m,u,o,budget-c,mode,fixed)):totals[j]+=z
        return tuple(totals)

    def run(self,mode):
        if mode=='known':
            rows=[self.evaluate(m,0,self.open,self.p.budget,'full',i) for i,g in enumerate(self.gmask) if (m:=self.root&g)]
            totals=tuple(map(sum,zip(*rows)))
        else:
            fixed=4 if mode=='independent' else max(range(5),key=lambda i:self.mass(self.gmask[i])) if mode=='map' else -1
            totals=self.evaluate(self.root,0,self.open,self.p.budget,'full' if fixed>=0 else mode,fixed)
        return tuple(F(x,self.mass(self.root)) for x in totals)

    def clear(self):
        for name in ('mass','decision','terminal','value','macro','evaluate'):getattr(self,name).cache_clear()


def profiles():
    for prior,strong,clue,b,budget in product((F(1,4),F(3,4)),(F(1,4),F(3,4)),(F(2,3),F(5,6)),(0,1),(2,3,4)):
        yield Profile(prior,strong,clue,b,budget)


def utility(result):return result[0]-4*result[1]


def revocation_witness():
    """Known two-source copy vs independent graphs; positive reports, q=2/3.

    Prior copy/independent odds 1:1; validity independent of H; invalid report fair.
    Values computed independently by summing over latent validity/report assignments.
    """
    out={}
    for status in ('copy','independent','mixture'):
        for revoked in (False,True):
            masses=[F(0),F(0)]
            for same in (False,True):
                if status!='mixture' and same!=(status=='copy'):continue
                for h in (0,1):
                    for vs in product((0,1),repeat=1 if same else 2):
                        if revoked and vs[0]:continue
                        w=F(1,2)
                        for v in vs:w*=F(2,3) if v else F(1,3)
                        for v in vs:w*=(F(int(h==1)) if v else F(1,2))
                        masses[h]+=w
            out[f'{status}_{"revoked" if revoked else "before"}']=masses[1]/sum(masses)
    return out


def boundary_profiles():
    """Post-hoc diagnostic: longer retrieval, weak audit, attribution near threshold."""
    for prior,strong,clue,budget in product((F(1,4),F(3,4)),(F(1,4),F(3,4)),(F(2,3),F(5,6)),(2,3,4)):
        yield Profile(prior,strong,clue,1,budget,boundary=True)


def threshold_witness():
    # q=1/2 and valid reports perfect. Conditional on two + signs, P(G=ind)=5/13.
    p_ind=F(5,13); p_copy=1-p_ind
    p=p_ind*F(9,10)+p_copy*F(3,4)
    u=lambda x:max(F(0),5*x-4,1-5*x)
    return {'posterior':p,'independent_probability':p_ind,'stop_utility':u(p),
            'lineage_utility':p_ind*u(F(9,10))+p_copy*u(F(3,4)),
            'lineage_gain':p_ind*u(F(9,10))+p_copy*u(F(3,4))-u(p)}
