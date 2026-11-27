$( FeedbackChannel.CPF03.approximate_bound_transfer; set-valued translation. $)
${
  ml-ev-approx-transfer.h1 $e |- A C_ B $.
  ml-ev-approx-transfer.h2 $e |- B C_ C $.
  ml-ev-approx-transfer $p |- A C_ C $=
    cA cB cC ml-ev-approx-transfer.h1 ml-ev-approx-transfer.h2 sstri
  $.
$}

$( FeedbackChannel.CPF03.no_reverse_bound; countermodel certificate. $)
  ml-ev-no-reverse-counterexample $p |- -. ( ( F. -> T. ) -> ( ( F. -> F. ) -> ( T. -> F. ) ) ) $=
    wfal wn wfal wtru wi wfal wfal wi wtru wfal wi wi wi wn fal wfal wtru wi wfal wfal wi wtru wfal wi wi wi
    wfal wfal wtru wi wfal wfal wi wtru wfal wi wi wi wtru wfal wi wfal wfal wtru wi wfal wfal wi wtru wfal
    wi wi wi wfal wfal wi wtru wfal wi wi wtru wfal wi wfal wtru wi wfal wtru wi wfal wfal wi wtru wfal wi wi
    wi wfal wfal wi wtru wfal wi wi wi wtru falim wfal wtru wi wfal wfal wi wtru wfal wi wi pm2.27 ax-mp wfal
    wfal wi wfal wfal wi wtru wfal wi wi wtru wfal wi wi wfal id wfal wfal wi wtru wfal wi pm2.27 ax-mp syl
    wtru wtru wfal wi wfal wi tru wtru wfal pm2.27 ax-mp syl con3i ax-mp
  $.

$( FeedbackChannel.CPF.conditional_audit; rational arithmetic translation. $)
${
  ml-ev-conditional-audit.h1 $e |- A e. QQ $.
  ml-ev-conditional-audit.h2 $e |- B e. QQ $.
  ml-ev-conditional-audit.h3 $e |- 0 <_ A $.
  ml-ev-conditional-audit.h4 $e |- 0 <_ B $.
  ml-ev-conditional-audit.h5 $e |- B <_ 1 $.
  ml-ev-conditional-audit $p |- ( 0 <_ ( A x. B ) /\ ( A x. B ) <_ A ) $=
    cc0 cA cB cmul co cle wbr cA cB cmul co cA cle wbr cc0 cA cle wbr cc0 cB cle wbr cc0 cA cB cmul co cle
    wbr ml-ev-conditional-audit.h3 ml-ev-conditional-audit.h4 cA cB cA cq wcel cA cr wcel
    ml-ev-conditional-audit.h1 cA qre ax-mp cB cq wcel cB cr wcel ml-ev-conditional-audit.h2 cB qre ax-mp
    mulge0i mp2an cA cB cmul co cA c1 cmul co cA cle cB cr wcel c1 cr wcel cA cr wcel cc0 cA cle wbr wa w3a
    cB c1 cle wbr cA cB cmul co cA c1 cmul co cle wbr cB cr wcel c1 cr wcel cA cr wcel cc0 cA cle wbr wa cB
    cq wcel cB cr wcel ml-ev-conditional-audit.h2 cB qre ax-mp 1re cA cr wcel cc0 cA cle wbr cA cq wcel cA cr
    wcel ml-ev-conditional-audit.h1 cA qre ax-mp ml-ev-conditional-audit.h3 pm3.2i 3pm3.2i
    ml-ev-conditional-audit.h5 cB c1 cA lemul2a mp2an cA cA cr wcel cA cc wcel cA cq wcel cA cr wcel
    ml-ev-conditional-audit.h1 cA qre ax-mp cA recn ax-mp mulridi breqtri pm3.2i
  $.
$}
