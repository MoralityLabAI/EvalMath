import unittest
from importlib.util import find_spec
from fractions import Fraction as F
from partial import MODELS,SCHEDULES,SCALE,enumerate_channel
from router_data import weights,teacher,split,regret,canonical


class RouterDataTests(unittest.TestCase):
    def test_exact_teacher_against_hidden_path_oracle(self):
        h=(((0,1,0),(0,1,1)),((1,0,1),(1,1,0)))
        likelihoods=[]
        for r,t in MODELS:
            p=F(1,12)
            for a,y in h:
                p*=enumerate_channel(a,r,t,"full").get(y,0)
            likelihoods.append(p)
        total=sum(likelihoods)
        ns,den=teacher(weights(h))
        for i,a in enumerate(SCHEDULES):
            q=F(0)
            for y in ((x,z,b) for x in range(2) for z in range(2) for b in range(2)):
                target=[F(0)]*4
                for p,(r,t) in zip(likelihoods,MODELS):
                    target[t]+=p*enumerate_channel(a,r,t,"full").get(y,0)
                q+=max(target)
            self.assertEqual(F(ns[i],den),q/total)

    def test_equivalent_histories_group(self):
        a=((0,1,0),(0,1,1))
        b=((1,1,0),(0,1,0))
        comp=(a[0],tuple(v^1 for v in a[1]))
        self.assertEqual(weights((a,b)),weights((b,a)))
        self.assertEqual(weights((a,b)),weights((comp,b)))
        data=split(1200,500)
        gs=[{weights(h) for h in data[k]} for k in ("train","short","long")]
        self.assertFalse(gs[0]&gs[1] or gs[0]&gs[2] or gs[1]&gs[2])

    def test_regret_ties(self):
        h=(((0,1,0),(0,1,1)),)
        nums,den=teacher(weights(h))
        self.assertEqual(min(regret(h,a) for a in range(8)),0)
        for a in range(8):
            self.assertEqual(regret(h,a),F(max(nums)-nums[a],den))

    @unittest.skipUnless(find_spec("torch"),"dedicated router CPU CI installs torch")
    def test_shapes_and_parameter_matching(self):
        from router import make_model,parameter_count,encode,train
        h=(((0,1,0),(0,1,1)),)
        x,m,y=encode([h,h+h])
        counts=[]
        for arm in ("tied","reset","histogram"):
            model=make_model(arm)
            counts.append(parameter_count(model))
            self.assertEqual(model(x,m).shape,(2,8))
            model,losses=train(arm,101,(x,m,y),1)
            self.assertEqual(len(losses),1)
        self.assertEqual(counts,[2144,2144,2120])
        self.assertLess(max(counts)/min(counts),1.02)


if __name__=="__main__":
    unittest.main()
