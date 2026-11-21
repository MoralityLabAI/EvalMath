"""Unit tests for PreferredEvals planning gates, evidence accounting and v1 ingestion."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from manifest import catalog_check, lint
from paired_receipts import compile_receipt
from prime_v1 import import_trace_rows


def fixture(name):
    return json.loads((HERE / "examples" / name).read_text())


class PreferredEvalsV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((HERE / "catalog.json").read_text())
        cls.manifest = fixture("development.json")
        cls.rows = fixture("paired-development.json")

    def test_full_catalog_and_unique_category_registry(self):
        self.assertEqual(catalog_check(self.catalog), [])
        self.assertGreaterEqual(len(self.catalog["benchmarks"]), 30)
        self.assertGreaterEqual(len(self.catalog["categories"]), 9)
        self.assertTrue(any(x["access"] == "tasks_withheld" for x in self.catalog["benchmarks"]))

    def test_unsealed_development_is_pilot_only(self):
        result = lint(self.manifest, self.catalog)
        self.assertEqual(result["decision"], "PILOT_ONLY")
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["n_independent_units_declared"], 3)

    def test_tasteval_tasks_withheld_and_no_faux_confirmation(self):
        data = copy.deepcopy(self.manifest)
        data["benchmark_id"] = "tasteval"
        self.assertIn("tasks withheld", " ".join(lint(data, self.catalog)["errors"]))
        data["benchmark_id"] = "deepswe"
        data["stage"] = "confirmation"
        failures = " ".join(lint(data, self.catalog)["errors"])
        self.assertIn("sealed readout", failures)
        self.assertIn(">=20 independent roots", failures)
        self.assertIn("verified hash provenance", failures)

    def test_taste_requires_dataset_authorization(self):
        data = copy.deepcopy(self.manifest)
        data["benchmark_id"] = "taste"
        errors = " ".join(lint(data, self.catalog)["errors"])
        self.assertIn("dataset_authorized", errors)
        data["provenance"]["dataset_authorized"] = True
        self.assertEqual(lint(data, self.catalog)["decision"], "PILOT_ONLY")

    def test_root_id_uniqueness_and_resource_headroom(self):
        data = copy.deepcopy(self.manifest)
        data["sampling"]["root_ids"].append("dev-repo-task-01")
        self.assertIn("duplicates", " ".join(lint(data, self.catalog)["errors"]))
        data = copy.deepcopy(self.manifest)
        data["runner"]["resources"]["ram_gb_ceiling"] = 1
        self.assertIn("hard ceiling", " ".join(lint(data, self.catalog)["errors"]))

    def test_prime_v1_api_must_be_explicit(self):
        data = copy.deepcopy(self.manifest)
        data["runner"]["harness"] = "prime_v1"
        data["runner"]["api"] = "verifiers"
        self.assertIn("verifiers.v1", " ".join(lint(data, self.catalog)["errors"]))
        data["runner"]["api"] = "verifiers.v1"
        self.assertEqual(lint(data, self.catalog)["decision"], "PILOT_ONLY")

    def test_causal_claim_needs_sham(self):
        data = copy.deepcopy(self.manifest)
        data["claim"]["causal"] = True
        self.assertIn("matched sham", " ".join(lint(data, self.catalog)["errors"]))
        data["controls"]["matched_sham_id"] = "equal-dose-control"
        self.assertEqual(lint(data, self.catalog)["decision"], "PILOT_ONLY")

    def test_paired_receipts_keep_errors_and_clusters(self):
        report = compile_receipt(self.manifest, self.catalog, self.rows)
        self.assertEqual(report["full_denominator"]["assigned"], 5)
        self.assertEqual(report["full_denominator"]["scored_pairs"], 3)
        self.assertEqual(report["status_counts"]["infra_error"], 1)
        self.assertEqual(report["status_counts"]["invalid_gold"], 1)
        cases = report["fsi_01_manifest"]["cases"]
        self.assertEqual([x["cluster_id"] for x in cases], ["dev-repo-task-01", "dev-repo-task-01", "dev-repo-task-03"])
        self.assertFalse(report["fsi_01_manifest"]["sealed_readout"])
        self.assertFalse(report["fsi_01_manifest"]["clusters_independent"])
        self.assertEqual(report, compile_receipt(self.manifest, self.catalog, self.rows))

    def test_no_inferred_root_and_no_silent_missing_status(self):
        bad = copy.deepcopy(self.rows)
        bad[0]["root_id"] = "other"
        with self.assertRaisesRegex(ValueError, "undeclared root_id"):
            compile_receipt(self.manifest, self.catalog, bad)
        bad = copy.deepcopy(self.rows)
        del bad[0]["status"]
        with self.assertRaisesRegex(ValueError, "status must be explicit"):
            compile_receipt(self.manifest, self.catalog, bad)

    def test_prime_v1_trace_ingestion_needs_external_task_roots(self):
        task = {"task":{"data":{"name":"synthetic-task"}},
                "traces":[{"ok":True,"stop_condition":"agent_completed",
                           "errors":[],"metrics":{"task_success":1.0},
                           "rewards":{"r":{"score":0.5,"weight":0.5}},"model_calls":[{"model":"m"}]}]}
        with self.assertRaisesRegex(ValueError, "mapped"):
            import_trace_rows([task], {"other-task":"root"})
        rows = import_trace_rows([task], {"synthetic-task":"independent-root"})
        self.assertEqual(rows[0]["root_id"], "independent-root")
        self.assertEqual(rows[0]["model_calls_count"], 1)
        self.assertEqual(rows[0]["weighted_reward"], 0.25)
        self.assertEqual(rows[0]["primary_metric"], 1.0)


if __name__ == "__main__":
    unittest.main()
