"""RHT-04: independently enumerate every world of the bipartite UGC exploit."""
from fractions import Fraction as Q
from itertools import product

from spiral_ln.evaluation_leak_topology import margins_of, cell_counts, box, cycle_rank
from spiral_ln.evaluation_reward_ugc_fixture import bipartite_goodhart_fixture
from spiral_ln.evaluation_reward_hacking_topology import (
    minimum_gold_audit, cycle_alias_witness, reconstruct_gold,
)
from spiral_ln.unique_games_topology import optimum_by_labels


def _score(game, labels):
    return tuple(int(labels[e.v] == (labels[e.u] ^ e.shift))
                 for e in game.edges)


def test_strict_proxy_optimizer_hacks_even_with_fully_identifiable_gold():
    r=bipartite_goodhart_fixture()
    graph=r["disclosure_graph"]
    game=r["constraint_game"]
    assert cycle_rank(graph)==3
    assert len(r["reachable"])<=2**game.vertices
    assert minimum_gold_audit(graph,r["gold_weights"])["count"]==0
    assert cycle_alias_witness(graph,r["gold_weights"]) is None
    assert optimum_by_labels(game)[0]==Q(7,8)
    assert r["unguarded"].selected_proxy_score==7
    assert r["unguarded"].worst_selected_true_utility==1
    assert r["unguarded"].wrong_fibre_gap==1
    assert r["unguarded"].hidden_fibre_gap==0
    assert r["guarded"].selected_proxy_score==5
    assert r["guarded"].minimum_gold_level==2


def test_all_sixty_four_assignments_verify_the_gold_proxy_conflict():
    r=bipartite_goodhart_fixture()
    game=r["constraint_game"]
    scores=[]
    for labels in product((0,1),repeat=game.vertices):
        x=_score(game,labels)
        proxy=sum(x)
        gold=x[0]+x[1]
        scores.append((proxy,gold,labels))
        if labels[0]==labels[1]:
            assert proxy<=5
            assert gold<=2
        else:
            assert proxy<=7
            assert gold<=1
    best_proxy=max(proxy for proxy,_,_ in scores)
    best_gold=max(gold for _,gold,_ in scores)
    assert (best_proxy,best_gold)==(7,2)
    assert all(gold==1 for proxy,gold,_ in scores if proxy==7)
    assert all(proxy<=5 for proxy,gold,_ in scores if gold==2)
    assert _score(game,r["low_proxy_gold_assignment"])==(1,1,1,0,1,0,1,0)
    assert _score(game,r["high_proxy_low_gold_assignment"])==(1,0,1,1,1,1,1,1)


def test_gold_can_be_reconstructed_from_public_category_margins():
    r=bipartite_goodhart_fixture()
    from spiral_ln.evaluation_reward_hacking_topology import audit_reconstruction
    graph=r["disclosure_graph"]
    t=r["gold_weights"]
    formula=audit_reconstruction(graph,t,())
    assert formula is not None
    # Gold equals the intersection column-zero margin.
    for x in box(graph["sizes"]):
        y=margins_of(graph,x)
        gold=x[0]+x[4]
        assert gold==y[2]  # row vertices 0,1, then first column index 2
        assert reconstruct_gold(graph,x,formula)==gold


def test_proxy_score_only_ledger_can_cause_regret_while_gold_score_is_public():
    r=bipartite_goodhart_fixture()
    game=r["constraint_game"]
    a=_score(game,r["low_proxy_gold_assignment"])
    b=_score(game,r["high_proxy_low_gold_assignment"])
    assert (sum(a),sum(b))==(5,7)
    assert (a[0]+a[1],b[0]+b[1])==(2,1)
    table_a=cell_counts(r["disclosure_graph"],"".join(str(x) for x in a))
    table_b=cell_counts(r["disclosure_graph"],"".join(str(x) for x in b))
    y_a=margins_of(r["disclosure_graph"],table_a)
    y_b=margins_of(r["disclosure_graph"],table_b)
    assert (y_a[2],y_b[2])==(2,1)
