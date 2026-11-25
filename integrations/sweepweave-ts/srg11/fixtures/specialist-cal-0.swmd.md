# SWMD-SRG/2
id: srg11_econ_0
title: "Adaptive evidence council"
about: "Observer-specific finite evidence model."
start: decision0
turn-base: 0
tie: first
direct: strict
VAR world.truth = 0 | hidden
VAR world.context = 0 | hidden
VAR analyst.context[reviewer][source] = 0 | hidden
VAR reviewer.report[analyst] = 0 | hidden
VAR source.x = 0 | hidden
VAR source.y = 0 | hidden
VAR source.q = 0 | hidden
VAR analyst.initial = 0 | hidden
VAR reviewer.initial = 0 | hidden
VAR public.x = 0 | public
VAR public.y = 0 | public
VAR public.q = 0 | public
SPOOL main | A:TRUE | E:decision0,decision1,decision2,correct,incorrect,settled
ENC decision0 turn=0..0 | I:0 | A:TRUE | Q:C(0) | N:"Evidence council" | T:"T and Z are independent uniform signs. Analyst initial report estimates Z with reliability 7/8; reviewer initial report estimates T with reliability 6/8. X estimates T with reliability 7/8 when Z is positive and 4/8 otherwise. Y swaps those reliabilities. Q estimates Z with reliability 7/8. Reports are conditionally independent given T,Z. Observer access: blind (analyst sees analyst.initial; reviewer sees reviewer.initial; joint sees both; blind sees neither). Query registers are public, zero means unqueried. Each query costs 1 utility, can be used once and consumes one action. A correct commitment pays 16, an incorrect one 0, settlement 10, less incurred query cost. An unfinished horizon pays negative incurred cost. Choose a first action maximizing expected utility with optimal later decisions."
OPT positive_0 | V:TRUE | P:TRUE | T:"Commit positive."
ORX positive_0/r_positive_0_ok -> correct | E:NONE | D:C(1) | G:EQ(P(world.truth),C(1)) | T:"The council records the result."
ORX positive_0/r_positive_0_bad -> incorrect | E:NONE | D:C(0) | G:TRUE | T:"The council records the result."
OPT negative_0 | V:TRUE | P:TRUE | T:"Commit negative."
ORX negative_0/r_negative_0_ok -> correct | E:NONE | D:C(1) | G:EQ(P(world.truth),C(-1)) | T:"The council records the result."
ORX negative_0/r_negative_0_bad -> incorrect | E:NONE | D:C(0) | G:TRUE | T:"The council records the result."
OPT settle_0 | V:TRUE | P:TRUE | T:"Accept settlement."
ORX settle_0/r_settle_0 -> settled | E:NONE | D:C(1) | G:TRUE | T:"The council records the result."
OPT x_0 | V:EQ(P(public.x),C(0)) | P:TRUE | T:"Query X."
ORX x_0/r_x_0 -> decision1 | E:SET public.x = P(source.x) | D:C(1) | G:TRUE | T:"The council records the result."
OPT y_0 | V:EQ(P(public.y),C(0)) | P:TRUE | T:"Query Y."
ORX y_0/r_y_0 -> decision1 | E:SET public.y = P(source.y) | D:C(1) | G:TRUE | T:"The council records the result."
OPT q_0 | V:EQ(P(public.q),C(0)) | P:TRUE | T:"Query Q."
ORX q_0/r_q_0 -> decision1 | E:SET public.q = P(source.q) | D:C(1) | G:TRUE | T:"The council records the result."
ENC decision1 turn=1..1 | I:1 | A:TRUE | Q:C(0) | N:"Evidence council" | T:"T and Z are independent uniform signs. Analyst initial report estimates Z with reliability 7/8; reviewer initial report estimates T with reliability 6/8. X estimates T with reliability 7/8 when Z is positive and 4/8 otherwise. Y swaps those reliabilities. Q estimates Z with reliability 7/8. Reports are conditionally independent given T,Z. Observer access: blind (analyst sees analyst.initial; reviewer sees reviewer.initial; joint sees both; blind sees neither). Query registers are public, zero means unqueried. Each query costs 1 utility, can be used once and consumes one action. A correct commitment pays 16, an incorrect one 0, settlement 10, less incurred query cost. An unfinished horizon pays negative incurred cost. Choose a first action maximizing expected utility with optimal later decisions."
OPT positive_1 | V:TRUE | P:TRUE | T:"Commit positive."
ORX positive_1/r_positive_1_ok -> correct | E:NONE | D:C(1) | G:EQ(P(world.truth),C(1)) | T:"The council records the result."
ORX positive_1/r_positive_1_bad -> incorrect | E:NONE | D:C(0) | G:TRUE | T:"The council records the result."
OPT negative_1 | V:TRUE | P:TRUE | T:"Commit negative."
ORX negative_1/r_negative_1_ok -> correct | E:NONE | D:C(1) | G:EQ(P(world.truth),C(-1)) | T:"The council records the result."
ORX negative_1/r_negative_1_bad -> incorrect | E:NONE | D:C(0) | G:TRUE | T:"The council records the result."
OPT settle_1 | V:TRUE | P:TRUE | T:"Accept settlement."
ORX settle_1/r_settle_1 -> settled | E:NONE | D:C(1) | G:TRUE | T:"The council records the result."
OPT x_1 | V:EQ(P(public.x),C(0)) | P:TRUE | T:"Query X."
ORX x_1/r_x_1 -> decision2 | E:SET public.x = P(source.x) | D:C(1) | G:TRUE | T:"The council records the result."
OPT y_1 | V:EQ(P(public.y),C(0)) | P:TRUE | T:"Query Y."
ORX y_1/r_y_1 -> decision2 | E:SET public.y = P(source.y) | D:C(1) | G:TRUE | T:"The council records the result."
OPT q_1 | V:EQ(P(public.q),C(0)) | P:TRUE | T:"Query Q."
ORX q_1/r_q_1 -> decision2 | E:SET public.q = P(source.q) | D:C(1) | G:TRUE | T:"The council records the result."
ENC decision2 turn=2..2 | I:2 | A:TRUE | Q:C(0) | N:"Evidence council" | T:"T and Z are independent uniform signs. Analyst initial report estimates Z with reliability 7/8; reviewer initial report estimates T with reliability 6/8. X estimates T with reliability 7/8 when Z is positive and 4/8 otherwise. Y swaps those reliabilities. Q estimates Z with reliability 7/8. Reports are conditionally independent given T,Z. Observer access: blind (analyst sees analyst.initial; reviewer sees reviewer.initial; joint sees both; blind sees neither). Query registers are public, zero means unqueried. Each query costs 1 utility, can be used once and consumes one action. A correct commitment pays 16, an incorrect one 0, settlement 10, less incurred query cost. An unfinished horizon pays negative incurred cost. Choose a first action maximizing expected utility with optimal later decisions."
OPT positive_2 | V:TRUE | P:TRUE | T:"Commit positive."
ORX positive_2/r_positive_2_ok -> correct | E:NONE | D:C(1) | G:EQ(P(world.truth),C(1)) | T:"The council records the result."
ORX positive_2/r_positive_2_bad -> incorrect | E:NONE | D:C(0) | G:TRUE | T:"The council records the result."
OPT negative_2 | V:TRUE | P:TRUE | T:"Commit negative."
ORX negative_2/r_negative_2_ok -> correct | E:NONE | D:C(1) | G:EQ(P(world.truth),C(-1)) | T:"The council records the result."
ORX negative_2/r_negative_2_bad -> incorrect | E:NONE | D:C(0) | G:TRUE | T:"The council records the result."
OPT settle_2 | V:TRUE | P:TRUE | T:"Accept settlement."
ORX settle_2/r_settle_2 -> settled | E:NONE | D:C(1) | G:TRUE | T:"The council records the result."
ENC correct turn=1..3 | I:3 | A:TRUE | Q:C(0) | N:"Evidence council" | T:"Correct commitment."
ENC incorrect turn=1..3 | I:4 | A:TRUE | Q:C(0) | N:"Evidence council" | T:"Incorrect commitment."
ENC settled turn=1..3 | I:5 | A:TRUE | Q:C(0) | N:"Evidence council" | T:"Settlement."
