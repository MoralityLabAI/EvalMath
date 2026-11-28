; AIRIS-05. All observations and likelihood facts belong to a bounded public episode.
; Hypothesis symbols denote possible mechanisms, never a privileged true hypothesis.
(= (BitXor 0 0) 0)
(= (BitXor 0 1) 1)
(= (BitXor 1 0) 1)
(= (BitXor 1 1) 0)

(= (TemporalCode (Y $x $y $z))
   (let* (($p (BitXor $x $y))
          ($q (BitXor $y $z)))
         (D $p $q)))

(= (LikelihoodFor $a $d $h)
   (match &self (Likelihood $a $d $h $n) $n))

(= (EventFactor $event $h)
   (let* ((($a $raw) (match &self (Evidence $event $a $y) ($a $y)))
          ($d (TemporalCode $raw)))
         (LikelihoodFor $a $d $h)))

(= (PriorFor $h)
   (match &self (Prior $h $n) $n))

(= (PosteriorWeight $h $events)
   (if (== $events ())
       (PriorFor $h)
       (let* ((($first $rest) (decons-atom $events))
              ($factor (EventFactor $first $h))
              ($old (PosteriorWeight $h $rest)))
             (* $factor $old))))
