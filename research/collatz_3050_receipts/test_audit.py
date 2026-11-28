import copy
import json
import math
import unittest
from pathlib import Path
from audit import ARMS, MODEL, PINS, ROLES, audit, canonical_hash, validate_manifest


def manifest():
    return json.loads((Path(__file__).parent/"fixture.json").read_text())


def contract(m):
    return {"schema":"BPD-COL-02/native-streamed-run/v1","model_id":"Nanbeige/Nanbeige4.2-3B","revision":MODEL,
            "cases_manifest_sha256":m["manifest_sha256"],"source_sha256":PINS,"loop_count":2,"batch_size":1,"max_tokens":128,
            "dtype":"bfloat16","use_cache":False,"arms":list(ARMS),"delivered_dose_relative_tolerance":.02,
            "delivered_dose_absolute_tolerance":1e-6,"scientific_floor_answer_probability":.05}


def output(label, p):
    q = {label:p, "B" if label=="A" else "A":1-p}
    return {"probabilities":q, "answer_logits":{k:math.log(v) for k,v in q.items()}}


def row(c):
    target=c["effect_donor"]["label"]
    clean={k:output(c[k]["label"],.9) for k in ROLES}
    for k in ROLES:
        clean[k]["first_pass"]=output(c[k]["label"],.8)
    arms={}
    for k,p in zip(ARMS,[.1,.75,.12,.12,.9]):
        d=0 if k=="identity" else 10 if k=="full_donor_prefix" else 1
        arms[k]={**output(target,p),"physical_dose":d,"measured_dose":d,"admission":True,
                 "protected_readout_max_abs":0,"patch_calls":1}
    return {"case_id":c["case_id"],"root_id":c["root_id"],"status":"completed","clean":clean,"arms":arms}


class AuditTests(unittest.TestCase):
    def test_pinned_arithmetic_fixture(self):
        m=manifest()
        self.assertEqual(len(validate_manifest(m)),4)
        r=audit(m,contract(m),[row(c) for c in m["cases"]])
        self.assertEqual(r["n_eligible_units"],4)
        self.assertAlmostEqual(r["primary_root_mean"],.63)
        self.assertIsNone(r["matched_sham_floor"])

    def test_failure_and_missing_cases(self):
        m=manifest()
        r=row(m["cases"][0])
        r["arms"]["effect"]["protected_readout_max_abs"]=1
        result=audit(m,contract(m),[r])
        self.assertEqual(result["n_attempted_cases"],1)
        self.assertEqual(result["n_eligible_units"],0)
        self.assertIsNone(result["primary_root_mean"])

    def test_forged_rehashed_manifest(self):
        m=manifest()
        m["cases"][0]["recipient"]["trace"][-1]=3
        m["manifest_sha256"]=canonical_hash({k:v for k,v in m.items() if k!="manifest_sha256"})
        with self.assertRaises(ValueError):
            validate_manifest(m)

    def test_probability_and_duplicates(self):
        m=manifest()
        r=row(m["cases"][0])
        with self.assertRaises(ValueError):
            audit(m,contract(m),[r,r])
        r["arms"]["effect"]["answer_logits"]["A"]+=2
        with self.assertRaises(ValueError):
            audit(m,contract(m),[r])


if __name__=="__main__":
    unittest.main()
