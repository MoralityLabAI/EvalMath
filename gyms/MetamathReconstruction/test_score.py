import unittest
from score import report, validate

def fixture():
    bank = ["bad", "gold", "alt", "other"]
    inputs, oracle = {}, {}
    for i, split in [(1,"train"),(201,"dev"),(401,"public_challenge")]:
        id_ = str(i)
        inputs[id_] = {"id":id_, "source_index":i, "split":split,
                       "candidates":bank, "candidate_signatures":dict.fromkeys(bank,{})}
        oracle[id_] = {"id":id_,"reference_action":"gold",
                       "accepted_actions":["gold","alt"],
                       "immediate_legal_actions":["bad","gold","alt"]}
    return inputs, oracle

class TestScore(unittest.TestCase):
    def test_alternative_and_missing(self):
        x,y = fixture()
        r = report(x,y,{"201":{"ranking":["alt"]}})
        self.assertEqual(r["dev"]["model_top1"],1)
        self.assertEqual(r["public_challenge"]["model_top1"],0)
        self.assertEqual(r["dev"]["random_top1_expected"],0.5)
        self.assertEqual(r["dev"]["prefix_legal_top1"],0)
        self.assertEqual(r["dev"]["train_frequency_top1"],1)
        self.assertEqual(r["dev"]["prefix_legal_verifier_calls"],4)

    def test_invalid_predictions(self):
        x,y = fixture()
        for p in ({"201":{"ranking":["gold","gold"]}},
                  {"201":{"ranking":["unknown"]}},{"extra":{"ranking":[]}}):
            with self.subTest(p=p), self.assertRaises(ValueError):
                report(x,y,p)

    def test_split(self):
        x,y = fixture()
        x["401"]["split"] = "train"
        with self.assertRaises(ValueError):
            validate(x,y)

    def test_bad_oracle(self):
        x,y = fixture()
        y["401"]["accepted_actions"] = ["unknown"]
        with self.assertRaises(ValueError):
            validate(x,y)

if __name__ == "__main__":
    unittest.main()
