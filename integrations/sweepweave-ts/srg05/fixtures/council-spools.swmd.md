# SWMD-SRG/2
id: council
title: "Council | public account"
about: "A compact test."
start: opening
turn-base: 0
tie: first
direct: strict
VAR a.trust = 0 | public
VAR a.trust[b] = 0.3 | hidden
SPOOL act1 | A:TRUE | E:opening
SPOOL act2 | A:FALSE | E:preferred,alternate,closed
ENC opening turn=0..0 | I:0 | A:TRUE | Q:C(0) | N:"Opening" | T:"The council meets."
OPT verify | V:TRUE | P:NOT(SEEN(verify)) | T:"Verify the record."
ORX verify/r1 -> wild | E:SET a.trust = C(0.5); SPOOL act2 = TRUE; SPOOL act1 = FALSE | D:C(1) | G:TRUE | T:"The second chamber opens."
OPT ignore | V:TRUE | P:TRUE | T:"Ignore the record."
ORX ignore/r2 -> wild | E:NONE | D:C(1) | G:TRUE | T:"Nothing changes."
ENC preferred turn=1..1 | I:1 | A:AND(ACTIVE(act2),SEEN(r1),GE(P(a.trust),C(0.5))) | Q:C(0.8) | N:"Preferred" | T:"Verified."
ENC alternate turn=1..1 | I:2 | A:TRUE | Q:C(0.8) | N:"Alternate" | T:"An alternative."
ENC closed turn=2..2 | I:3 | A:TRUE | Q:C(1) | N:"Closed" | T:"Too early."
