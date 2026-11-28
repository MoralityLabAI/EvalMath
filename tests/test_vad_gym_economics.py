"""VAD-11E: the economics replay is deterministic and pinned to the kernel receipt it reads."""
import hashlib
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "scripts"))
import verify_vad_gym_economics as e


def test_replay_matches_committed_receipt():
    gym = root / "output/verified_abstraction/vad_11_gym.json"
    committed = json.loads((root / "output/verified_abstraction/vad_11e_economics.json").read_text())
    assert committed["receipt_sha256"] == hashlib.sha256(gym.read_bytes()).hexdigest()
    fresh = e.run(gym)
    assert fresh["pooled_ms"] == committed["pooled_ms"]
    assert fresh["families"] == committed["families"]


def test_oracle_prebuilt_set_is_never_worse_than_direct_or_online():
    fresh = e.run(root / "output/verified_abstraction/vad_11_gym.json")
    for f, row in fresh["families"].items():
        p = row["policies_ms"]
        assert p["oracle_prebuilt_set"] <= p["direct"]
        assert p["oracle_prebuilt_set"] <= p["greedy0"] + 1e-9
