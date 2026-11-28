import pytest
from spiral_ln.evaluation_cpf02 import census, compile_charged, free_polynomial, charged_polynomial


def test_census():
    assert census() == {"field_program_checks": {"0": 12, "1": 720, "2": 64800},
                        "maximum_charged_gates": {"0": 2, "1": 6, "2": 10}}


def test_characteristic_two_and_reuse():
    gates = (("sub", ("x", 0), ("x", 1)), ("mul", 0, 0))
    compiled, out = compile_charged(gates, 1)
    assert free_polynomial(gates, 1, 2) == charged_polynomial(compiled, out, 2) == {(0, 0): 1, (1, 1): 1}
    assert len(compiled) < 4*len(gates) + 2


def test_invalid_topology():
    with pytest.raises(ValueError):
        compile_charged((("add", 0, ("x", 0)),), 0)
