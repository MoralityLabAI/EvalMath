# SWMD-SRG/2
id: council_copy_correct
title: "Council evidence ledger"
about: "Finite evidence and belief experiment."
start: opening
turn-base: 0
tie: first
direct: strict
VAR council.regime = 0 | hidden
VAR bob.stance = 0 | hidden
VAR analyst.claim[alice] = 0 | hidden
VAR analyst.claim[bob] = 0 | hidden
VAR analyst.repeat[bob] = 0 | hidden
VAR analyst.stance[reviewer][bob] = 0 | hidden
VAR observer.stance[reviewer][bob] = 0 | hidden
VAR analyst.stance[bob] = 0 | hidden
VAR analyst.A = 0 | public
VAR analyst.B = 0 | public
VAR analyst.D = 0 | public
VAR analyst.M = 0 | public
VAR analyst.audit = 0 | public
SPOOL main | A:TRUE | E:opening,read_a,read_b,read_c,decision,audited,win,loss,settled,audited_win,audited_loss
ENC opening turn=0..0 | I:0 | A:TRUE | Q:C(0) | N:"Council record" | T:"Truth and Bob's reporting stance are independently uniform signs. Alice matches truth with probability 3/4. Bob matches truth times stance with probability 7/8. The repeated Bob report is a perfect copy, not new evidence. The reviewer sign matches Bob's stance with probability 7/8. Reports and reviewer noise are otherwise conditionally independent. M is the reviewer's report. A correct direct decision pays 8, an incorrect one 0, settlement pays 5. Exact audit and correct commitment pays 6 in two actions; an unfinished audit pays 0."
OPT read_0 | V:TRUE | P:TRUE | T:"Read the next evidence field."
ORX read_0/receipt_0 -> read_a | E:SET analyst.A = P(analyst.claim[alice]) | D:C(1) | G:TRUE | T:"Record updated."
ENC read_a turn=1..1 | I:1 | A:TRUE | Q:C(0) | N:"Council record" | T:"Truth and Bob's reporting stance are independently uniform signs. Alice matches truth with probability 3/4. Bob matches truth times stance with probability 7/8. The repeated Bob report is a perfect copy, not new evidence. The reviewer sign matches Bob's stance with probability 7/8. Reports and reviewer noise are otherwise conditionally independent. M is the reviewer's report. A correct direct decision pays 8, an incorrect one 0, settlement pays 5. Exact audit and correct commitment pays 6 in two actions; an unfinished audit pays 0."
OPT read_1 | V:TRUE | P:TRUE | T:"Read the next evidence field."
ORX read_1/receipt_1 -> read_b | E:SET analyst.B = P(analyst.claim[bob]) | D:C(1) | G:TRUE | T:"Record updated."
ENC read_b turn=2..2 | I:2 | A:TRUE | Q:C(0) | N:"Council record" | T:"Truth and Bob's reporting stance are independently uniform signs. Alice matches truth with probability 3/4. Bob matches truth times stance with probability 7/8. The repeated Bob report is a perfect copy, not new evidence. The reviewer sign matches Bob's stance with probability 7/8. Reports and reviewer noise are otherwise conditionally independent. M is the reviewer's report. A correct direct decision pays 8, an incorrect one 0, settlement pays 5. Exact audit and correct commitment pays 6 in two actions; an unfinished audit pays 0."
OPT read_2 | V:TRUE | P:TRUE | T:"Read the next evidence field."
ORX read_2/receipt_2 -> read_c | E:SET analyst.D = P(analyst.repeat[bob]) | D:C(1) | G:TRUE | T:"Record updated."
ENC read_c turn=3..3 | I:3 | A:TRUE | Q:C(0) | N:"Council record" | T:"Truth and Bob's reporting stance are independently uniform signs. Alice matches truth with probability 3/4. Bob matches truth times stance with probability 7/8. The repeated Bob report is a perfect copy, not new evidence. The reviewer sign matches Bob's stance with probability 7/8. Reports and reviewer noise are otherwise conditionally independent. M is the reviewer's report. A correct direct decision pays 8, an incorrect one 0, settlement pays 5. Exact audit and correct commitment pays 6 in two actions; an unfinished audit pays 0."
OPT read_3 | V:TRUE | P:TRUE | T:"Read the next evidence field."
ORX read_3/receipt_3 -> decision | E:SET analyst.M = P(analyst.stance[reviewer][bob]) | D:C(1) | G:TRUE | T:"Record updated."
ENC decision turn=4..4 | I:4 | A:TRUE | Q:C(0) | N:"Council record" | T:"Truth and Bob's reporting stance are independently uniform signs. Alice matches truth with probability 3/4. Bob matches truth times stance with probability 7/8. The repeated Bob report is a perfect copy, not new evidence. The reviewer sign matches Bob's stance with probability 7/8. Reports and reviewer noise are otherwise conditionally independent. M is the reviewer's report. A correct direct decision pays 8, an incorrect one 0, settlement pays 5. Exact audit and correct commitment pays 6 in two actions; an unfinished audit pays 0."
OPT positive | V:TRUE | P:TRUE | T:"Commit positive."
ORX positive/pwin -> win | E:NONE | D:C(1) | G:GT(P(council.regime),C(0)) | T:"Record updated."
ORX positive/ploss -> loss | E:NONE | D:C(0) | G:TRUE | T:"Record updated."
OPT negative | V:TRUE | P:TRUE | T:"Commit negative."
ORX negative/nwin -> win | E:NONE | D:C(1) | G:LT(P(council.regime),C(0)) | T:"Record updated."
ORX negative/nloss -> loss | E:NONE | D:C(0) | G:TRUE | T:"Record updated."
OPT settle | V:TRUE | P:TRUE | T:"Accept settlement."
ORX settle/swin -> settled | E:NONE | D:C(1) | G:TRUE | T:"Record updated."
OPT audit | V:TRUE | P:TRUE | T:"Audit truth exactly."
ORX audit/audit_receipt -> audited | E:SET analyst.audit = P(council.regime) | D:C(1) | G:TRUE | T:"Record updated."
ENC audited turn=5..5 | I:5 | A:TRUE | Q:C(0) | N:"Council record" | T:"The audit reveals the true regime in analyst.audit. Choose the matching sign."
OPT final_positive | V:TRUE | P:TRUE | T:"Commit positive after audit."
ORX final_positive/apwin -> audited_win | E:NONE | D:C(1) | G:GT(P(council.regime),C(0)) | T:"Record updated."
ORX final_positive/aploss -> audited_loss | E:NONE | D:C(0) | G:TRUE | T:"Record updated."
OPT final_negative | V:TRUE | P:TRUE | T:"Commit negative after audit."
ORX final_negative/anwin -> audited_win | E:NONE | D:C(1) | G:LT(P(council.regime),C(0)) | T:"Record updated."
ORX final_negative/anloss -> audited_loss | E:NONE | D:C(0) | G:TRUE | T:"Record updated."
ENC win turn=5..5 | I:6 | A:TRUE | Q:C(0) | N:"Council record" | T:"Direct correct."
ENC loss turn=5..5 | I:7 | A:TRUE | Q:C(0) | N:"Council record" | T:"Direct incorrect."
ENC settled turn=5..5 | I:8 | A:TRUE | Q:C(0) | N:"Council record" | T:"Settlement."
ENC audited_win turn=6..6 | I:9 | A:TRUE | Q:C(0) | N:"Council record" | T:"Audit correct."
ENC audited_loss turn=6..6 | I:10 | A:TRUE | Q:C(0) | N:"Council record" | T:"Audit incorrect."
