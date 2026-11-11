"""RHT-02: finite path, terminal-boundary and loop reward-hacking controls."""
from fractions import Fraction as Q

import pytest
from spiral_ln.evaluation_reward_path_gauge import (
    RewardPathGame,RewardTransition,potential_if_exact,
    boundary_relative_certificate,path_returns,policy_rank_reversal,
    directed_loop_exploit,
)


def E(source,target,gold,proxy):
    return RewardTransition(source,target,Q(gold),Q(proxy))


def test_exact_boundary_relative_shaping_preserves_every_allowed_ranking():
    # Both terminals have potential 2, initial potential 0.
    game=RewardPathGame(4,0,(2,3),(
        E(0,1,0,1),E(1,2,4,5),E(1,3,1,2),E(0,2,3,5),
        E(0,3,0,2),
    ))
    cert=boundary_relative_certificate(game)
    assert cert is not None
    assert cert["common_path_offset"]==2
    for path in ((0,1),(0,2),(3,),(4,)):
        u,p=path_returns(game,path)
        assert p-u==2
    assert not policy_rank_reversal(game,(0,1),(0,2))
    assert not policy_rank_reversal(game,(0,1),(4,))


def test_no_cycles_still_allows_terminal_reward_hacking():
    game=RewardPathGame(3,0,(1,2),(
        E(0,1,2,2),E(0,2,0,3),
    ))
    assert potential_if_exact(game) is not None
    assert boundary_relative_certificate(game) is None
    assert policy_rank_reversal(game,(0,),(1,))
    assert path_returns(game,(0,))==(2,2)
    assert path_returns(game,(1,))==(0,3)


def test_nonzero_cycle_proxy_arbitrage_under_repeatable_loop():
    game=RewardPathGame(2,0,(0,),(
        E(0,1,0,1),E(1,0,0,1),
    ))
    assert potential_if_exact(game) is None
    loop=directed_loop_exploit(game,(0,1))
    assert loop is not None
    assert loop["true_per_lap"]==0
    assert loop["proxy_per_lap"]==2
    assert loop["proxy_minus_true"]==2
    for n in range(1,9):
        path=(0,1)*n
        assert path_returns(game,path)==(0,2*n)


def test_negative_proxy_loop_is_not_repeatable_positive_exploit():
    game=RewardPathGame(2,0,(0,),(
        E(0,1,0,0),E(1,0,0,-1),
    ))
    assert potential_if_exact(game) is None
    assert directed_loop_exploit(game,(0,1)) is None


def test_positive_proxy_loop_with_positive_true_return_requires_context():
    game=RewardPathGame(2,0,(0,),(
        E(0,1,2,2),E(1,0,2,3),
    ))
    assert directed_loop_exploit(game,(0,1)) is None
    assert potential_if_exact(game) is None


def test_same_terminal_positive_shaping_return_is_common_offset():
    game=RewardPathGame(4,0,(3,),(
        E(0,1,1,2),E(1,3,1,2),E(0,2,2,4),E(2,3,1,1),
    ))
    # Phi[0]=0, Phi[1]=1, Phi[3]=2, Phi[2]=2.
    cert=boundary_relative_certificate(game)
    assert cert is not None
    assert cert["common_path_offset"]==2
    assert path_returns(game,(0,1))==(2,4)
    assert path_returns(game,(2,3))==(3,5)


def test_disconnected_declared_terminal_blocks_a_uniform_certificate():
    game=RewardPathGame(3,0,(1,2),(E(0,1,1,2),))
    assert potential_if_exact(game) is not None
    assert boundary_relative_certificate(game) is None


def test_invalid_transition_sequences_and_terminal_requirements():
    with pytest.raises(ValueError):
        RewardPathGame(2,0,(),(E(0,1,0,0),))
    with pytest.raises(ValueError):
        RewardPathGame(2,0,(1,), (E(0,3,0,1),))
    game=RewardPathGame(3,0,(2,), (E(0,1,0,1),E(1,2,0,0)))
    with pytest.raises(ValueError):
        path_returns(game,(1,))
    with pytest.raises(ValueError):
        path_returns(game,(0,))
    with pytest.raises(ValueError):
        directed_loop_exploit(game,(0,1))
    with pytest.raises(ValueError):
        directed_loop_exploit(game,())
