"""ESF-01 generator and custody regressions; no model or network required."""
from fractions import Fraction as F
from random import Random

import pytest

from spiral_ln.evaluation_synthetic_foundry import (
    FAMILIES, PROFILES, digest, generate, make_case, solve, task, write_pack,
)


@pytest.mark.parametrize("family", FAMILIES)
@pytest.mark.parametrize("profile", PROFILES)
def test_all_native_families(family, profile):
    rng=Random(98231)
    for _ in range(5):
        x=make_case(family,rng,profile)
        public,gold=task(family,x,profile)
        assert public["task_id"]==gold["task_id"]==digest({"family":family,"input":x})
        assert "answer" not in public
        assert set(public["requested_fields"])==set(gold["answer"])
        assert gold["answer"]==solve(family,x)


def test_known_mathematics():
    assert solve("disclosure",{"n":8,"budget":3})["adaptive_success"]=="1"
    assert solve("disclosure",{"n":8,"budget":3})["fixed_success"]=="3/4"
    assert solve("patch",{"categories":[[2,1],[16,9]]})["optimal_expected_patches"]=="3/2"
    assert solve("cpf",{"a":"1/20","b":"1/20","r":"1/400","audit_pass_given_both":"1/2"})["residual"]=="1/800"
    assert solve("audit",{"p":"1/2","sensitivity":"9/10","false_positive":"1/10"})["audit_value"]=="2/5"
    assert solve("paired",{"p_hidden_prediction":"1/2","n_pairs":17,
                           "authenticated_residual_available":False})["public_brier"]=="1/4"
    assert solve("private_stopping",{"accuracy":"3/4"})["private_stopping_value"]=="5/4"
    w={"weights":[1,1,1,1],"bits":[[0,0],[0,1],[1,0],[1,1]],
       "continuation_weights":[1,1,1],"states":1}
    assert solve("revocation",w)["minimum_regret"]=="1/2"
    w["states"]=4
    assert solve("revocation",w)["minimum_regret"]=="0"
    assert solve("capacity",{"support":[[0,0],[0,1],[1,0],[1,1]],
                             "faces":[[0],[1]],"sizes":[1]*4})["collision_exists"]
    assert solve("capacity",{"support":[[0,0],[0,1],[1,1]],
                             "faces":[[0],[1]],"sizes":[1]*3})["collision_exists"] is False


def test_split_and_export(tmp_path):
    families=["judge","cpf","adaptive_risk","bpd"]
    train,train_gold=generate(families,"baseline",12,42,"discovery")
    dev,dev_gold=generate(families,"baseline",12,42,"development")
    assert len(train)==len(train_gold)==len(dev)==len(dev_gold)==48
    assert not ({t["task_id"] for t in train}&{t["task_id"] for t in dev})
    assert train==generate(families,"baseline",12,42,"discovery")[0]
    m=write_pack(tmp_path/"pack",train,train_gold,seed=42,split="discovery",profile="baseline")
    assert m["actual_count"]==48
    assert m["teacher_data_included"] is False
    assert "pending" in m["training_admission"]
    assert all("answer" not in r for r in train)
    assert len((tmp_path/"pack"/"tasks.jsonl").read_text().splitlines())==48
    assert len((tmp_path/"pack"/"evaluator_gold.jsonl").read_text().splitlines())==48
    with pytest.raises(FileExistsError):
        write_pack(tmp_path/"pack",train,train_gold,seed=42,split="discovery",profile="baseline")


def test_regret_and_risk_invariants():
    for family in ("selection","covert","adaptive_risk","adaptive_cpf","filtration","revocation"):
        rng=Random(17)
        for _ in range(12):
            r=solve(family,make_case(family,rng))
            if family in {"selection","covert"}:
                assert F(r["public_risk"])<=F(r["risk_with_messages"])<=F(r["full_information_risk"])
            elif family=="adaptive_risk":
                assert F(r["adaptive_risk"])>=F(r["fixed_risk"])
            elif family=="adaptive_cpf":
                assert F(r["adaptive_residual"])<=F(r["fixed_residual"])
            elif family=="filtration":
                assert F(r["risk_before"])>=F(r["risk_after"])
            else:
                assert F(r["minimum_regret"])+F(r["optimal_success"])==1
