"""Tests for eight registered comparisons and offline Ideation Arena conversion."""
import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from campaign_report import registered,holm,report
from ideation_arena import extract

REG=Path(__file__).resolve().parents[2]/"results/campaign-20261121/registration.json"

class CampaignTests(unittest.TestCase):
    def setUp(self):
        self.reg=json.loads(REG.read_text())
        self.index={"schema":"preferred-evals/campaign-receipt-index-v1",
                    "comparisons":{x["id"]:{"reason":"missing"} for x in registered(self.reg)}}
    def test_eight_and_registered_effect(self):
        result=report(self.reg,self.index,REG.parent)
        self.assertEqual(len(result["comparisons"]),8)
        self.assertEqual(result["minimum_effect"],.10)
        self.assertEqual(result["completed_with_p"],0)
        self.assertTrue(all(x["status"]=="missing_receipts" for x in result["comparisons"]))
    def test_holm_uses_whole_family(self):
        self.assertEqual(holm([.001,.01,.02,None,None,None,None,None])[:3],[.008,.07,.12])
    def test_reject_wrong_registration(self):
        self.reg["test"]["minimum_effect"]="0.05"
        with self.assertRaisesRegex(ValueError,"minimum effect"):
            report(self.reg,self.index,REG.parent)
    def test_receipt_attestation_and_denominators(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            fsi={"minimum_effect":.10,"planned_comparisons":8,"p_unadjusted":.01,"n_cases":2,
                 "n_clusters":1,"cluster_macro_effect":.5,"verdict":"suggestive"}
            paired={"total_assigned_rollouts":3,"n_paired_scored":2,"n_infra_or_missing":1,
                    "candidate_correct_paired":2,"baseline_correct_paired":1,"n_roots_paired_scored":1}
            (root/"fsi.json").write_text(json.dumps(fsi))
            (root/"paired.json").write_text(json.dumps(paired))
            self.index["comparisons"]["between-1"]={"fsi_result":"fsi.json","paired_receipt":"paired.json"}
            result=report(self.reg,self.index,root)
            self.assertEqual(result["comparisons"][0]["holm_p_eight"],.08)
            self.assertEqual(result["comparisons"][0]["missing_or_error"],1)
            fsi["planned_comparisons"]=1;(root/"fsi.json").write_text(json.dumps(fsi))
            with self.assertRaisesRegex(ValueError,"comparison family"):
                report(self.reg,self.index,root)
    def test_ideation_arena_license_and_label_isolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"data.json"
            p.write_text(json.dumps([
              {"query_text":"Same context","response_a":"Proposal alpha","response_b":"Proposal beta","dimension_results":{"D4":"A"}},
              {"query_text":"Same context","response_a":"Proposal gamma","response_b":"Proposal delta","dimension_results":{"D4":"B"}},
              {"query_text":"Other context","response_a":"Proposal x","response_b":"Proposal y","dimension_results":{"D4":"Tie"}}]))
            with self.assertRaisesRegex(ValueError,"noncommercial"):
                extract(p)
            tasks,labels,skipped=extract(p,license_ack=True)
            self.assertEqual(len(tasks),2)
            self.assertEqual(tasks[0]["root_id"],tasks[1]["root_id"])
            self.assertNotIn("answer",tasks[0])
            self.assertEqual([x["answer"] for x in labels],["A","B"])
            self.assertEqual(skipped["tie"],1)
if __name__=="__main__":unittest.main()
