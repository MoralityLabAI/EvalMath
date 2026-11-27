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
    wfal wfal wtru wi wfal wfal wi wtru wfal wi wi wi wtru wfal wi wfal wtru wi wfal wfal wi wtru wfal
    wi wi wi wfal wfal wi wtru wfal wi wi wtru wfal wi wfal wtru wi wfal wtru wi wfal wfal wi wtru wfal wi wi
    wi wfal wfal wi wtru wfal wi wi wi wtru falim wfal wtru wi wfal wfal wi wtru wfal wi wi pm2.27 ax-mp wfal
    wfal wi wfal wfal wi wtru wfal wi wi wtru wfal wi wi wfal id wfal wfal wi wtru wfal wi pm2.27 ax-mp syl
    wtru wtru wfal wi wfal wi tru wtru wfal pm2.27 ax-mp syl con3i ax-mp
  $.
