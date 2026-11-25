# SWMD-SRG/1
id: srg04
title: The Council Ledger
start: opening
tie: last
VAR council.Trust = 0.8 | public
VAR council.Support = 0 | public
VAR council.Trust[other] = -0.4 | hidden
VAR council.Trust[other][third] = 0.35 | hidden
ENC opening turn=0..0 | A:TRUE
OPT negotiate | V:TRUE | P:TRUE
ORX negotiate/r_first -> accepted | O:Negotiate a commitment. | E:SET council.Trust = NUDGE(P(council.Trust),C(-0.2)); SET council.Support = P(council.Trust); SET council.Trust[other][third] = C(-0.5) | D:ADD(P(council.Trust[other]),C(0.4)) | G:TRUE
ORX negotiate/r_last -> accepted | O:Negotiate a commitment. | E:SET council.Support = P(council.Trust); SET council.Trust = NUDGE(P(council.Trust),C(-0.2)); SET council.Trust = NUDGE(P(council.Trust),C(0.1)) | D:C(0) | G:TRUE
ORX negotiate/r_hidden -> accepted | O:Negotiate a commitment. | E:NONE | D:C(3) | G:LT(P(council.Trust[other][third]),C(0))
OPT refuse | V:GE(P(council.Trust),C(0.8)) | P:TRUE
ORX refuse/r_refuse -> refused | O:Refuse. | E:SET council.Support = C(-0.2) | D:C(1) | G:TRUE
OPT impossible | V:TRUE | P:LT(P(council.Trust),C(0))
ORX impossible/r_impossible -> refused | O:Impossible. | E:NONE | D:C(1) | G:TRUE
ENC accepted turn=1..1 | A:GE(P(council.Support),C(0.3))
ENC refused turn=1..1 | A:TRUE
