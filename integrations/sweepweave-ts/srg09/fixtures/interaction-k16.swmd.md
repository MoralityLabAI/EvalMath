# SWMD-SRG/2
id: interaction_16
title: "Council evidence ledger"
about: "Finite evidence and belief experiment."
start: decision
turn-base: 0
tie: first
direct: strict
VAR analyst.p0[source] = 0 | hidden
VAR analyst.p1[source] = 0 | hidden
VAR analyst.p2[source] = 0 | hidden
VAR analyst.p3[source] = 0 | hidden
VAR analyst.p4[source] = 0 | hidden
VAR analyst.p5[source] = 0 | hidden
VAR analyst.p6[source] = 0 | hidden
VAR analyst.p7[source] = 0 | hidden
VAR analyst.r0[reviewer][source] = 0 | hidden
VAR analyst.r1[reviewer][source] = 0 | hidden
VAR analyst.r2[reviewer][source] = 0 | hidden
VAR analyst.r3[reviewer][source] = 0 | hidden
VAR analyst.r4[reviewer][source] = 0 | hidden
VAR analyst.r5[reviewer][source] = 0 | hidden
VAR analyst.r6[reviewer][source] = 0 | hidden
VAR analyst.r7[reviewer][source] = 0 | hidden
VAR observer.r0[reviewer][source] = 0 | hidden
VAR observer.r1[reviewer][source] = 0 | hidden
VAR observer.r2[reviewer][source] = 0 | hidden
VAR observer.r3[reviewer][source] = 0 | hidden
VAR observer.r4[reviewer][source] = 0 | hidden
VAR observer.r5[reviewer][source] = 0 | hidden
VAR observer.r6[reviewer][source] = 0 | hidden
VAR observer.r7[reviewer][source] = 0 | hidden
VAR analyst.common = 0 | hidden
VAR analyst.goal = 0 | hidden
SPOOL main | A:TRUE | E:decision,positive,negative
ENC decision turn=0..0 | I:0 | A:TRUE | Q:C(0) | N:"Council record" | T:"The signed score contrast is a sum of observer-owned pairwise interactions and linear terms."
OPT act | V:TRUE | P:TRUE | T:"Request a ruling."
ORX act/rp -> positive | E:SET analyst.goal = C(0.25) | D:ADD(P(analyst.common),MUL(C(0.5),ADD(MUL(C(1),P(analyst.p0[source]),P(analyst.r0[reviewer][source])),MUL(C(-1),P(analyst.p1[source]),P(analyst.r1[reviewer][source])),MUL(C(1),P(analyst.p2[source]),P(analyst.r2[reviewer][source])),MUL(C(-1),P(analyst.p3[source]),P(analyst.r3[reviewer][source])),MUL(C(1),P(analyst.p4[source]),P(analyst.r4[reviewer][source])),MUL(C(-1),P(analyst.p5[source]),P(analyst.r5[reviewer][source])),MUL(C(1),P(analyst.p6[source]),P(analyst.r6[reviewer][source])),MUL(C(-1),P(analyst.p7[source]),P(analyst.r7[reviewer][source])),MUL(C(0.25),P(analyst.p0[source])),MUL(C(0.25),P(analyst.p1[source])),MUL(C(0.25),P(analyst.p2[source])),MUL(C(0.25),P(analyst.p3[source])),MUL(C(0.25),P(analyst.p4[source])),MUL(C(0.25),P(analyst.p5[source])),MUL(C(0.25),P(analyst.p6[source])),MUL(C(0.25),P(analyst.p7[source]))))) | G:TRUE | T:"Record updated."
ORX act/rn -> negative | E:SET analyst.goal = C(-0.25) | D:ADD(P(analyst.common),MUL(C(-0.5),ADD(MUL(C(1),P(analyst.p0[source]),P(analyst.r0[reviewer][source])),MUL(C(-1),P(analyst.p1[source]),P(analyst.r1[reviewer][source])),MUL(C(1),P(analyst.p2[source]),P(analyst.r2[reviewer][source])),MUL(C(-1),P(analyst.p3[source]),P(analyst.r3[reviewer][source])),MUL(C(1),P(analyst.p4[source]),P(analyst.r4[reviewer][source])),MUL(C(-1),P(analyst.p5[source]),P(analyst.r5[reviewer][source])),MUL(C(1),P(analyst.p6[source]),P(analyst.r6[reviewer][source])),MUL(C(-1),P(analyst.p7[source]),P(analyst.r7[reviewer][source])),MUL(C(0.25),P(analyst.p0[source])),MUL(C(0.25),P(analyst.p1[source])),MUL(C(0.25),P(analyst.p2[source])),MUL(C(0.25),P(analyst.p3[source])),MUL(C(0.25),P(analyst.p4[source])),MUL(C(0.25),P(analyst.p5[source])),MUL(C(0.25),P(analyst.p6[source])),MUL(C(0.25),P(analyst.p7[source]))))) | G:TRUE | T:"Record updated."
ENC positive turn=1..1 | I:1 | A:TRUE | Q:C(0) | N:"Council record" | T:"Positive."
ENC negative turn=1..1 | I:2 | A:TRUE | Q:C(0) | N:"Council record" | T:"Negative."
