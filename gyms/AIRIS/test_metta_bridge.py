import unittest
from importlib.util import find_spec
from partial import prior

@unittest.skipUnless(find_spec("hyperon"),"native Hyperon required; dedicated CI installs pinned runtime")
class MeTTaTests(unittest.TestCase):
    def test_native_census(self):
        from metta_bridge import census
        r=census()
        self.assertEqual(r["public_single_episode_cases"],64)
        self.assertEqual(r["lifecycle_cases"],6)
        self.assertEqual(r["lifecycle"][-1]["result"]["weights"],prior(None))

    def test_identity_validation(self):
        from metta_bridge import Event,checked_events
        e=Event(0,(0,1,0),(0,0,0))
        with self.assertRaises(ValueError):
            checked_events((e,e))
        with self.assertRaises(ValueError):
            Event(0,(0,1,0),(0,0,2))
        with self.assertRaises(ValueError):
            Event(-1,(0,1,0),(0,0,0))

    def test_known_prior_and_impossible_history(self):
        from metta_bridge import NativeMemory,Event
        m=NativeMemory(0)
        e=Event(0,(0,1,0),(0,1,1))
        w=m.weights((e,))
        self.assertEqual(sum(x>0 for x in w),1)
        f=Event(1,(0,1,0),(0,0,0))
        with self.assertRaises(ValueError):
            m.weights((e,f))
        self.assertEqual(m.weights(()),prior(0))

if __name__=="__main__":
    unittest.main()
