import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import verify_vad_batch_calibrated as v

def test_calibration_and_charges():
    rows=[]
    for split,d,l in (("cal",10,5),("test",12,8)):
        for rep in range(2):
            for arm,t in (("direct",d),("lemma",l)):
                rows.append(dict(family="F1",block=0,horizon=8,split=split,repeat=rep,arm=arm,ok=True,total_wall=t,cpu=t,peak_rss_kib=100))
    assert v.choose([r for r in rows if r["split"]=="cal"])=="lemma"
    s=v.summarize(rows,{"F1/0/8":"lemma"})[0]
    assert s["gain_selected"]==1.5
    assert s["calibration_all_wall"]==30
    assert s["gain_charged_one"]==12/23
    assert s["break_even_sessions_one"]==15/4
    assert s["paired_savings"]==[4,4]

def test_split_names():
    for family in v.G.FAMILIES:
        x=v.splits(family,0,8)
        assert not {s["seed"] for s in x["cal"]}&{s["seed"] for s in x["test"]}
        for split in x:
            for strategy in ("S_direct" if family=="F5" else "S_decide","S_lemma"):
                source,names,units=v.B.render(x[split],strategy)
                assert len(names)>=8
                assert source.count("namespace VAD13_")==8
