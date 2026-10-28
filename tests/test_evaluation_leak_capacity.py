"""Independent exact checks for capacity-sensitive feedback disclosure."""

from fractions import Fraction

import pytest

from spiral_ln.evaluation_leak_capacity import (
    bounded_witness, collision_counts_direct, collision_counts_lattice,
    critical_uniform_capacity, observation_matrix, positive_bounded_moves,
    sparse_kernel_certificate,
)
from spiral_ln.evaluation_leak_topology import (
    NONLOCAL_SUPPORT, fibre_dimension_k, margin_rows_k, separate_faces,
    supports_in_grid,
)


def test_matrix_matches_original_module_on_all_surjective_cube_supports():
    for cells in supports_in_grid((2, 2, 2)):
        for faces in (separate_faces(3), ((0, 1), (2,)), ((0, 1), (0, 2), (1, 2))):
            reordered = tuple(reversed(cells))
            ordered, capacities, rows = observation_matrix(reordered, faces)
            assert ordered == tuple(sorted(cells))
            assert capacities == (1,) * len(cells)
            assert rows == tuple(map(tuple, margin_rows_k(cells, faces)))


def test_nonlocal_kernel_requires_capacity_two():
    faces = ((0,), (1,), (2,))
    assert fibre_dimension_k(NONLOCAL_SUPPORT, faces) == 1
    assert bounded_witness(NONLOCAL_SUPPORT, faces) is None
    assert critical_uniform_capacity(NONLOCAL_SUPPORT, faces, 2) == 2
    assert sparse_kernel_certificate(NONLOCAL_SUPPORT, faces) == (1, -2, 1, 1, -1)
    second = tuple(2 if c == (0, 0, 1) else 1 for c in NONLOCAL_SUPPORT)
    witness = bounded_witness(NONLOCAL_SUPPORT, faces, second)
    assert witness is not None
    assert tuple(abs(z) for z in witness["move"]) == (1, 2, 1, 1, 1)
    leakage = collision_counts_lattice(NONLOCAL_SUPPORT, faces, second)
    assert leakage["integer_move_pairs"] == 1
    assert leakage["collision_ratio"] == Fraction(49, 48)
    assert leakage["joint_collision_probability"] == Fraction(3, 128)
    assert leakage["observed_collision_probability"] == Fraction(49, 2048)
    assert collision_counts_direct(NONLOCAL_SUPPORT, faces, second) == (
        leakage["joint_record_pairs"], leakage["observed_record_pairs"])


def test_all_unit_cube_supports_against_independent_count_oracle():
    supports = tuple(supports_in_grid((2, 2, 2)))
    assert len(supports) == 193
    positive_rank, strict, silent_rank = 0, 0, 0
    for cells in supports:
        faces = separate_faces(3)
        result = collision_counts_lattice(cells, faces)
        assert (result["joint_record_pairs"], result["observed_record_pairs"]) == (
            collision_counts_direct(cells, faces))
        assert result["strict"] == (bounded_witness(cells, faces) is not None)
        assert result["strict"] == (result["collision_ratio"] > 1)
        dim = fibre_dimension_k(cells, faces)
        positive_rank += dim > 0
        strict += result["strict"]
        silent_rank += dim > 0 and not result["strict"]
    assert (positive_rank, strict, silent_rank) == (99, 91, 8)



def test_sparse_rational_kernel_certificates_are_exact():
    for cells in supports_in_grid((2, 2, 2)):
        for faces in (separate_faces(3), ((0, 1), (2,)),
                      ((0, 1), (0, 2), (1, 2)), ((0, 1, 2),)):
            cert = sparse_kernel_certificate(cells, faces)
            dimension = fibre_dimension_k(cells, faces)
            assert (cert is None) == (dimension == 0)
            if cert is not None:
                _, _, rows = observation_matrix(cells, faces)
                assert any(cert) and all(sum(a*b for a,b in zip(row, cert)) == 0 for row in rows)
                assert max(abs(v) for v in cert) <= 2
                assert bounded_witness(cells, faces, (max(abs(v) for v in cert),)*len(cells))


def test_two_joint_maps_plus_one_separate_has_unit_witness_iff_rank_positive():
    for cells in supports_in_grid((2, 2, 2)):
        for faces in (((0, 1), (2,)), ((0, 2), (1,)), ((1, 2), (0,))):
            assert (bounded_witness(cells, faces) is not None) == (
                fibre_dimension_k(cells, faces) > 0)


def test_direct_oracle_with_repeated_cells_and_empty_observation():
    support = ((0, 0), (0, 1), (1, 0), (1, 1))
    for faces, capacities in (
        (((0,), (1,)), (1, 1, 1, 1)),
        (((0,), (1,)), (1, 2, 1, 2)),
        (((0, 1),), (2, 1, 2, 1)),
        ((), (1, 1, 1, 1)),
        (((),), (2, 2, 1, 1)),
    ):
        r = collision_counts_lattice(support, faces, capacities)
        assert (r["joint_record_pairs"], r["observed_record_pairs"]) == (
            collision_counts_direct(support, faces, capacities))
    assert collision_counts_lattice(support, (((0, 1)),))["collision_ratio"] == 1


def test_capacity_monotonicity_of_strictness():
    for cells in list(supports_in_grid((2, 2, 2)))[:40]:
        for faces in (separate_faces(3), ((0, 1), (2,))):
            small = bounded_witness(cells, faces) is not None
            big = bounded_witness(cells, faces, (2,) * len(cells)) is not None
            assert not small or big


@pytest.mark.parametrize("cells,faces,sizes", [
    ((), ((0,),), None),
    (((0,), (0,)), ((0,),), None),
    (((0,),), ((1,),), None),
    (((0,),), ((0, 0),), None),
    (((0,),), ((0,),), (0,)),
    (((0,),), ((0,),), (True,)),
    (((0,),), ((0,),), (1, 2)),
    (((0,), (0, 1)), ((0,),), None),
])
def test_invalid_cell_inputs_are_rejected(cells, faces, sizes):
    with pytest.raises(ValueError):
        observation_matrix(cells, faces, sizes)


def test_invalid_moves_and_limits():
    with pytest.raises(ValueError):
        list(positive_bounded_moves(((1, 0),), (1,)))
    with pytest.raises(ValueError):
        list(positive_bounded_moves((), (0,)))
    with pytest.raises(ValueError):
        critical_uniform_capacity(((0,),), (), 0)


def test_single_cell_no_observation():
    r = collision_counts_lattice(((0,),), (), (2,))
    assert r["joint_record_pairs"] == 6 and r["observed_record_pairs"] == 16
    assert r["collision_ratio"] == Fraction(8, 3)
    assert r["joint_collision_probability"] == Fraction(3, 8)
    assert r["observed_collision_probability"] == 1
