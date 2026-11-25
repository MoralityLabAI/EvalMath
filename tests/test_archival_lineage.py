from fractions import Fraction as F
from itertools import product
from spiral_ln.evaluation_archival_lineage import (
    Oracle, Profile, GRAPHS, distribution, profiles, boundary_profiles,
    revocation_witness, threshold_witness, utility,
)


def test_initial_graph_truth_joint_against_closed_form():
    for p in list(profiles())[::3]+list(boundary_profiles())[::3]:
        o=Oracle(p); masses={}
        for gi,g in enumerate(GRAPHS):
            pg=p.independent_prior if gi==4 else (1-p.independent_prior)/4
            for h in (0,1):
                mass=F(0)
                for strong in (0,1):
                    pc=p.strong_prior if strong else 1-p.strong_prior
                    accuracy=(F(11,12) if strong else F(5,8)) if not p.boundary else (F(5,6) if strong else F(3,4))
                    signs={g[0]:1,g[1]:p.b_report}
                    if g[0]==g[1] and p.b_report==0:continue
                    pr=pg*pc/2
                    for sign in signs.values():pr*=accuracy if sign==h else 1-accuracy
                    mass+=pr
                masses[gi,h]=mass
        total=sum(masses.values())
        for (gi,h),mass in masses.items():
            assert F(o.mass(o.gmask[gi]&o.hmask[h]),o.mass(o.root))==mass/total
        o.clear()


def test_query_partition_and_gate_legality():
    o=Oracle(list(profiles())[-1]); root=o.root
    assert 0 not in dict(o.actions(0,0,4)) and 2 not in dict(o.actions(0,0,4))
    [(m,u,op)]=o.children(root,0,0,7)
    assert m==root and op==1 and 0 in dict(o.actions(u,op,3))
    for i in dict(o.actions(u,op,3)):
        children=list(o.children(m,u,op,i))
        assert sum(o.mass(x) for x,_,_ in children)==o.mass(m)
    assert all(not (i in (1,2,8)) for i,_ in o.actions(0,0,4,False))


def independent_value(p, budget):
    # Separate list-of-worlds recursion, no bit masks or Oracle methods.
    rows=distribution(p)
    costs=(3,1,1,2,4,4,4) if p.boundary else (1,1,1,1,2,2,2)
    def visit(rs,remaining,used,opened):
        m=[sum(w for r,w in rs if r[0]==h) for h in (0,1)]
        best=max(0,m[1]-4*m[0],m[0]-4*m[1])
        for i,c in enumerate((*costs,1,1)):
            if c>remaining or i in used:continue
            if i==0 and 7 not in opened:continue
            if i==2 and 8 not in opened:continue
            if i==6 and 0 not in used:continue
            if i in (7,8):
                if i in opened:continue
                val=visit(rs,remaining-c,used|{i},opened|{i})
            else:
                groups={}
                for r,w in rs:groups.setdefault(r[2+i],[]).append((r,w))
                val=sum(visit(x,remaining-c,used|{i},opened) for x in groups.values())
            best=max(best,val)
        return best
    return F(visit(rows,budget,set(),set() if p.c_gated else {7}),sum(w for _,w in rows))


def test_independent_tree():
    for p in [list(profiles())[11],list(profiles())[35],list(boundary_profiles())[0],list(boundary_profiles())[-1]]:
        o=Oracle(p)
        for b in (1,2,3):
            assert F(o.value(o.root,0,o.open,b,b)[0],o.mass(o.root))==independent_value(p,b)
        o.clear()


def test_witnesses():
    w=revocation_witness()
    assert w=={'copy_before':F(5,6),'copy_revoked':F(1,2),'independent_before':F(25,26),
               'independent_revoked':F(5,6),'mixture_before':F(55,62),'mixture_revoked':F(11,18)}
    assert threshold_witness()['lineage_gain']==F(2,13)


def test_policy_conservation_and_bounds():
    for p in (list(profiles())[-1],list(boundary_profiles())[2]):
        o=Oracle(p); full=o.run('full'); known=o.run('known')
        for m in ('stop','independent','map','one','two','macro','no_lineage','full','known'):
            r=o.run(m)
            assert sum(r[:3])==1 and r[3]<=p.budget
            assert utility(known)>=utility(r)
            if m!='known': assert utility(full)>=utility(r)
            if m not in ('independent','map'):assert r[1]<=F(1,5)*(r[0]+r[1])
        o.clear()
