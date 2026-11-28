"""Exploratory MIC-14b: at most two reveals, 2048 canonical certificate bytes."""
from mic14 import *
BUDGET=2048

class CostReplay(Replay):
    def __init__(self,d,p):
        super().__init__(d,p)
        self.cost=[len(json.dumps(n,separators=(',',':'),sort_keys=True).encode()) for n in self.nodes]
    def eligible(self,front,budget):
        return self.candidates(tuple((i,c) for i,c in front if self.cost[i]<=budget))
    def budget_gain(self,front,perm,i,budget=BUDGET):
        assert self.cost[i]<=budget
        u=self.upper(front,perm);f,p=self.step(front,perm,i);left=budget-self.cost[i]
        best=min([self.upper(f,p)]+[self.upper(*self.step(f,p,j)) for j,_ in self.eligible(f,left)])
        return u-best
    def rows(self):
        front=((0,self.total),);perm=0;hist=[];past=[];rows=[];step=0
        while front:
            cand=self.eligible(front,BUDGET);u=self.upper(front,perm)
            if len(hist)>=H and len(cand)>=2:
                gains=[self.budget_gain(front,perm,i) for i,_ in cand];x=[]
                for i,c in cand:
                    f=self.features(i,c);f[-1]=self.cost[i]/BUDGET;x.append(f)
                rows.append(dict(step=step,history=hist[-H:],history_nodes=past[-H:],candidates=x,obligations=[dict(node=i,raw=[hex(v) for v in self.raw[i]],cap=c,bytes=self.cost[i]) for i,c in cand],common=[self.lower/self.total,u/self.total,perm/self.total,len(front)/32,self.n/128],gains=gains,total=self.total,oracle_gain=max(gains),informative=max(gains)>min(gains),upper=u,lower=self.lower,budget=BUDGET))
            i,cap=self.candidates(front)[0];f,p=self.step(front,perm,i);hist.append(self.event(i,cap,f,p,u));past.append(i);front,perm=f,p;step+=1
        return rows,self.upper(front,perm)

