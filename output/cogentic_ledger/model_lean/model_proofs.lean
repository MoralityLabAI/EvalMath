import Init
set_option linter.unusedVariables false

theorem cogModel_0166c7d22f3e1a7458df13256d0e483728cc75d5f3225cc5723c5877c476b190 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 : Prop) (f0 : p0) (f3 : p3) (f12 : p12) (r0 : p19 → p34 → p24) (r1 : p8 → p19 → p34) (r2 : p3 → p6 → p23) (r3 : p9 → p26 → p15) (r4 : p0 → p10 → p17) (r5 : p0 → p12 → p24 → p36) (r6 : p35 → p4) (r7 : p0 → p28) (r8 : p0 → p3 → p12 → p35) (r9 : p21 → p37) (r10 : p2 → p27 → p7) (r11 : p1 → p12 → p27) (r12 : p12 → p27 → p36 → p25) (r13 : p13 → p32 → p33) (r14 : p3 → p12 → p8) (r15 : p0 → p19) (r16 : p0 → p12 → p31) (r17 : p35 → p9) (r18 : p4 → p16 → p21) (r19 : p12 → p14 → p18) (r20 : p2 → p7 → p32) (r21 : p0 → p12 → p10) (r22 : p9 → p28 → p37 → p30) (r23 : p2 → p19 → p1) (r24 : p3 → p26) (r25 : p3 → p9 → p12 → p16) (r26 : p19 → p31 → p2) (r27 : p27 → p36 → p11) (r28 : p4 → p5 → p16 → p22) (r29 : p12 → p20 → p29) (r30 : p0 → p9 → p10 → p5) (r31 : p1 → p11 → p13) : p33 := by
  have h31 : p31 := r16 f0 f12
  have h19 : p19 := r15 f0
  have h2 : p2 := r26 h19 h31
  have h1 : p1 := r23 h2 h19
  have h27 : p27 := r11 h1 f12
  have h7 : p7 := r10 h2 h27
  have h32 : p32 := r20 h2 h7
  have h8 : p8 := r14 f3 f12
  have h34 : p34 := r1 h8 h19
  have h24 : p24 := r0 h19 h34
  have h36 : p36 := r5 f0 f12 h24
  have h11 : p11 := r27 h27 h36
  have h13 : p13 := r31 h1 h11
  have h33 : p33 := r13 h13 h32
  exact h33
#print axioms cogModel_0166c7d22f3e1a7458df13256d0e483728cc75d5f3225cc5723c5877c476b190

theorem cogModel_27dac72e1a2107a71f5d39f1bdfd80180717f7515a07731a8a1189d5f9532d1e (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 : Prop) (f16 : p16) (f30 : p30) (f36 : p36) (r0 : p17 → p37 → p27) (r1 : p0 → p30 → p21) (r2 : p6 → p25 → p17) (r3 : p16 → p30 → p14) (r4 : p32 → p29) (r5 : p2 → p0) (r6 : p10 → p30 → p31) (r7 : p9 → p35 → p36 → p4) (r8 : p8 → p19 → p23 → p33) (r9 : p36 → p24) (r10 : p2 → p6 → p28) (r11 : p14 → p30 → p35) (r12 : p11 → p21 → p23) (r13 : p30 → p9) (r14 : p12 → p27 → p13) (r15 : p16 → p30 → p36 → p2) (r16 : p16 → p30 → p36 → p32) (r17 : p7 → p16 → p22) (r18 : p12 → p27 → p34) (r19 : p28 → p37 → p15) (r20 : p2 → p34 → p19) (r21 : p25 → p28 → p37 → p5) (r22 : p16 → p36 → p20) (r23 : p14 → p29 → p30 → p1) (r24 : p30 → p38 → p26) (r25 : p5 → p17 → p37 → p12) (r26 : p16 → p30 → p6) (r27 : p0 → p16 → p37) (r28 : p3 → p30 → p18) (r29 : p12 → p15 → p37 → p11) (r30 : p0 → p28 → p36 → p25) (r31 : p11 → p25 → p8) : p33 := by
  have h2 : p2 := r15 f16 f30 f36
  have h0 : p0 := r5 h2
  have h21 : p21 := r1 h0 f30
  have h37 : p37 := r27 h0 f16
  have h6 : p6 := r26 f16 f30
  have h28 : p28 := r10 h2 h6
  have h15 : p15 := r19 h28 h37
  have h25 : p25 := r30 h0 h28 f36
  have h17 : p17 := r2 h6 h25
  have h27 : p27 := r0 h17 h37
  have h5 : p5 := r21 h25 h28 h37
  have h12 : p12 := r25 h5 h17 h37
  have h34 : p34 := r18 h12 h27
  have h19 : p19 := r20 h2 h34
  have h11 : p11 := r29 h12 h15 h37
  have h8 : p8 := r31 h11 h25
  have h23 : p23 := r12 h11 h21
  have h33 : p33 := r8 h8 h19 h23
  exact h33
#print axioms cogModel_27dac72e1a2107a71f5d39f1bdfd80180717f7515a07731a8a1189d5f9532d1e

theorem cogModel_1efbfe2e7b41b5eb1550298975ac2ad6eab78eaa285610cdfdafa9306e17306d (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 p41 p42 p43 p44 : Prop) (f4 : p4) (f10 : p10) (f13 : p13) (f34 : p34) (f37 : p37) (r0 : p10 → p24 → p26) (r1 : p28 → p35 → p23) (r2 : p9 → p17 → p16) (r3 : p4 → p24) (r4 : p2 → p14 → p42 → p30) (r5 : p10 → p13 → p17) (r6 : p15 → p17 → p14) (r7 : p10 → p34 → p37 → p18) (r8 : p35 → p37 → p36) (r9 : p1 → p27 → p33) (r10 : p0 → p20 → p43 → p29) (r11 : p13 → p18 → p3) (r12 : p7 → p34 → p31) (r13 : p5 → p44 → p35) (r14 : p15 → p38 → p42) (r15 : p9 → p37 → p5) (r16 : p34 → p20) (r17 : p4 → p36 → p39) (r18 : p13 → p18 → p37 → p1) (r19 : p4 → p5 → p25 → p22) (r20 : p37 → p43) (r21 : p5 → p25 → p38) (r22 : p5 → p37 → p25) (r23 : p24 → p6) (r24 : p4 → p39 → p15) (r25 : p5 → p32 → p44) (r26 : p27 → p37 → p43 → p8) (r27 : p24 → p11) (r28 : p15 → p2) (r29 : p9 → p10 → p17 → p32) (r30 : p10 → p36 → p38 → p28) (r31 : p10 → p12 → p40) (r32 : p22 → p37 → p21) (r33 : p3 → p19) (r34 : p1 → p24 → p37 → p27) (r35 : p4 → p18 → p37 → p0) (r36 : p4 → p37 → p9) (r37 : p10 → p18 → p37 → p41) : p30 := by
  have h17 : p17 := r5 f10 f13
  have h9 : p9 := r36 f4 f37
  have h5 : p5 := r15 h9 f37
  have h25 : p25 := r22 h5 f37
  have h38 : p38 := r21 h5 h25
  have h32 : p32 := r29 h9 f10 h17
  have h44 : p44 := r25 h5 h32
  have h35 : p35 := r13 h5 h44
  have h36 : p36 := r8 h35 f37
  have h39 : p39 := r17 f4 h36
  have h15 : p15 := r24 f4 h39
  have h2 : p2 := r28 h15
  have h14 : p14 := r6 h15 h17
  have h42 : p42 := r14 h15 h38
  have h30 : p30 := r4 h2 h14 h42
  exact h30
#print axioms cogModel_1efbfe2e7b41b5eb1550298975ac2ad6eab78eaa285610cdfdafa9306e17306d

theorem cogModel_0c51c3214f93267dfb790cafb2287ca342d54aa937ee6b95defa42a06ea74caf (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 : Prop) (f1 : p1) (f6 : p6) (f17 : p17) (r0 : p11 → p12 → p19) (r1 : p7 → p8) (r2 : p14 → p0) (r3 : p1 → p7) (r4 : p3 → p14) (r5 : p1 → p6 → p22 → p12) (r6 : p12 → p21) (r7 : p6 → p9 → p5) (r8 : p15 → p17 → p13) (r9 : p6 → p12 → p16) (r10 : p1 → p6 → p16 → p18) (r11 : p10 → p4) (r12 : p1 → p17 → p21 → p11) (r13 : p0 → p10) (r14 : p2 → p3) (r15 : p1 → p11 → p22 → p20) (r16 : p1 → p6 → p17 → p22) (r17 : p8 → p2) : p4 := by
  have h7 : p7 := r3 f1
  have h8 : p8 := r1 h7
  have h2 : p2 := r17 h8
  have h3 : p3 := r14 h2
  have h14 : p14 := r4 h3
  have h0 : p0 := r2 h14
  have h10 : p10 := r13 h0
  have h4 : p4 := r11 h10
  exact h4
#print axioms cogModel_0c51c3214f93267dfb790cafb2287ca342d54aa937ee6b95defa42a06ea74caf

theorem cogModel_a4fad239383dc7276a433d03df00d79dc045d718427824bc10144ac2d786bdc8 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 p41 p42 p43 p44 p45 : Prop) (f0 : p0) (f23 : p23) (f33 : p33) (r0 : p29 → p44 → p39) (r1 : p23 → p33 → p3) (r2 : p1 → p27) (r3 : p0 → p28 → p41 → p34) (r4 : p0 → p3 → p16) (r5 : p1 → p33 → p43 → p2) (r6 : p22 → p27 → p31) (r7 : p0 → p25) (r8 : p0 → p17 → p5) (r9 : p0 → p23 → p26 → p19) (r10 : p18 → p22 → p9) (r11 : p10 → p40) (r12 : p0 → p23 → p33 → p6) (r13 : p8 → p22 → p43 → p44) (r14 : p0 → p9 → p43 → p8) (r15 : p0 → p7 → p41 → p12) (r16 : p1 → p18 → p30 → p24) (r17 : p0 → p12 → p25 → p15) (r18 : p11 → p33 → p42) (r19 : p0 → p23 → p43) (r20 : p6 → p38) (r21 : p20 → p21 → p4) (r22 : p23 → p33 → p1) (r23 : p0 → p3 → p38 → p32) (r24 : p9 → p22 → p39 → p21) (r25 : p14 → p23 → p36) (r26 : p23 → p24 → p43 → p35) (r27 : p0 → p2 → p18) (r28 : p27 → p29 → p37 → p20) (r29 : p23 → p40 → p26) (r30 : p3 → p38 → p40 → p45) (r31 : p0 → p41 → p7) (r32 : p12 → p23 → p10) (r33 : p23 → p27 → p33 → p30) (r34 : p2 → p27 → p30 → p22) (r35 : p1 → p27 → p31 → p11) (r36 : p11 → p44 → p37) (r37 : p23 → p41) (r38 : p12 → p41 → p13) (r39 : p7 → p10 → p32 → p28) (r40 : p2 → p8 → p29) : p4 := by
  have h1 : p1 := r22 f23 f33
  have h27 : p27 := r2 h1
  have h30 : p30 := r33 f23 h27 f33
  have h43 : p43 := r19 f0 f23
  have h2 : p2 := r5 h1 f33 h43
  have h22 : p22 := r34 h2 h27 h30
  have h18 : p18 := r27 f0 h2
  have h9 : p9 := r10 h18 h22
  have h8 : p8 := r14 f0 h9 h43
  have h44 : p44 := r13 h8 h22 h43
  have h29 : p29 := r40 h2 h8
  have h39 : p39 := r0 h29 h44
  have h21 : p21 := r24 h9 h22 h39
  have h31 : p31 := r6 h22 h27
  have h11 : p11 := r35 h1 h27 h31
  have h37 : p37 := r36 h11 h44
  have h20 : p20 := r28 h27 h29 h37
  have h4 : p4 := r21 h20 h21
  exact h4
#print axioms cogModel_a4fad239383dc7276a433d03df00d79dc045d718427824bc10144ac2d786bdc8

theorem cogModel_861ae1fdd286ef4422bbb9dd0e245f51705cf9e38c6cd1b9c378723daaaec58e (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 p41 p42 p43 p44 p45 p46 p47 : Prop) (f11 : p11) (f28 : p28) (f35 : p35) (f41 : p41) (r0 : p24 → p29 → p35 → p43) (r1 : p18 → p27 → p28 → p45) (r2 : p13 → p41 → p1) (r3 : p11 → p33) (r4 : p11 → p39 → p20) (r5 : p26 → p38) (r6 : p24 → p27 → p35 → p18) (r7 : p25 → p35 → p41 → p46) (r8 : p35 → p40 → p34) (r9 : p28 → p35 → p19) (r10 : p25 → p2) (r11 : p11 → p37 → p31) (r12 : p25 → p28 → p35 → p26) (r13 : p3 → p11 → p9) (r14 : p35 → p38 → p6) (r15 : p25 → p28 → p46 → p47) (r16 : p28 → p35 → p25) (r17 : p8 → p28 → p24) (r18 : p20 → p13) (r19 : p15 → p16 → p42 → p7) (r20 : p35 → p41 → p47 → p5) (r21 : p23 → p28 → p39) (r22 : p8 → p45 → p12) (r23 : p14 → p28 → p22) (r24 : p25 → p28 → p38 → p36) (r25 : p11 → p14 → p24 → p23) (r26 : p4 → p45 → p42) (r27 : p10 → p28 → p41 → p21) (r28 : p2 → p46 → p0) (r29 : p8 → p19 → p14) (r30 : p4 → p12 → p23 → p16) (r31 : p4 → p22 → p28 → p15) (r32 : p46 → p10) (r33 : p11 → p44 → p17) (r34 : p36 → p32) (r35 : p43 → p27) (r36 : p1 → p45 → p4) (r37 : p35 → p8) (r38 : p14 → p23 → p43 → p30) (r39 : p14 → p24 → p29) : p7 := by
  have h8 : p8 := r37 f35
  have h24 : p24 := r17 h8 f28
  have h19 : p19 := r9 f28 f35
  have h14 : p14 := r29 h8 h19
  have h22 : p22 := r23 h14 f28
  have h23 : p23 := r25 f11 h14 h24
  have h39 : p39 := r21 h23 f28
  have h20 : p20 := r4 f11 h39
  have h13 : p13 := r18 h20
  have h1 : p1 := r2 h13 f41
  have h29 : p29 := r39 h14 h24
  have h43 : p43 := r0 h24 h29 f35
  have h27 : p27 := r35 h43
  have h18 : p18 := r6 h24 h27 f35
  have h45 : p45 := r1 h18 h27 f28
  have h12 : p12 := r22 h8 h45
  have h4 : p4 := r36 h1 h45
  have h42 : p42 := r26 h4 h45
  have h16 : p16 := r30 h4 h12 h23
  have h15 : p15 := r31 h4 h22 f28
  have h7 : p7 := r19 h15 h16 h42
  exact h7
#print axioms cogModel_861ae1fdd286ef4422bbb9dd0e245f51705cf9e38c6cd1b9c378723daaaec58e

theorem cogModel_3a26610448a98e66624944854ce8ea675e69ed11f89ad9a8648e7cb351b2bd12 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 : Prop) (f10 : p10) (f20 : p20) (f23 : p23) (f26 : p26) (r0 : p16 → p26 → p13) (r1 : p3 → p6 → p20 → p17) (r2 : p9 → p23 → p14) (r3 : p1 → p25 → p19) (r4 : p11 → p12 → p17 → p1) (r5 : p26 → p28 → p29 → p33) (r6 : p9 → p10 → p25) (r7 : p6 → p23 → p26 → p11) (r8 : p22 → p0) (r9 : p20 → p32 → p9) (r10 : p17 → p19 → p32 → p31) (r11 : p9 → p23 → p1) (r12 : p10 → p22) (r13 : p6 → p20 → p11) (r14 : p0 → p22 → p32) (r15 : p23 → p28) (r16 : p7 → p9 → p32 → p14) (r17 : p10 → p32 → p7) (r18 : p7 → p12 → p25) (r19 : p17 → p22 → p32 → p9) (r20 : p10 → p20 → p33 → p4) (r21 : p26 → p29) (r22 : p6 → p10 → p3) (r23 : p1 → p20 → p5) (r24 : p0 → p20 → p32) (r25 : p2 → p23 → p32 → p7) (r26 : p6 → p26 → p3) (r27 : p20 → p28 → p33 → p18) (r28 : p24 → p31 → p27) (r29 : p8 → p23 → p15) (r30 : p1 → p12 → p5) (r31 : p0 → p3 → p11 → p2) (r32 : p20 → p23 → p6) (r33 : p26 → p32 → p12) (r34 : p0 → p23 → p2) (r35 : p14 → p26 → p19) (r36 : p3 → p5 → p17 → p24) (r37 : p20 → p30 → p21) : p27 := by
  have h6 : p6 := r32 f20 f23
  have h3 : p3 := r22 h6 f10
  have h17 : p17 := r1 h3 h6 f20
  have h22 : p22 := r12 f10
  have h0 : p0 := r8 h22
  have h11 : p11 := r13 h6 f20
  have h32 : p32 := r24 h0 f20
  have h12 : p12 := r33 f26 h32
  have h9 : p9 := r19 h17 h22 h32
  have h7 : p7 := r17 f10 h32
  have h25 : p25 := r18 h7 h12
  have h14 : p14 := r16 h7 h9 h32
  have h19 : p19 := r35 h14 f26
  have h31 : p31 := r10 h17 h19 h32
  have h1 : p1 := r4 h11 h12 h17
  have h5 : p5 := r30 h1 h12
  have h24 : p24 := r36 h3 h5 h17
  have h27 : p27 := r28 h24 h31
  exact h27
#print axioms cogModel_3a26610448a98e66624944854ce8ea675e69ed11f89ad9a8648e7cb351b2bd12

theorem cogModel_6aad105f0509dbbe12328a3c167a271fc3aedbd80660c390872c3e2ce3117f21 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 : Prop) (f4 : p4) (f22 : p22) (f27 : p27) (r0 : p8 → p32 → p3) (r1 : p0 → p11 → p2) (r2 : p27 → p32 → p16) (r3 : p4 → p24 → p23) (r4 : p14 → p27 → p28 → p29) (r5 : p22 → p27 → p0) (r6 : p18 → p22 → p12) (r7 : p0 → p15 → p27 → p25) (r8 : p7 → p22 → p9) (r9 : p23 → p24 → p19) (r10 : p4 → p20) (r11 : p27 → p31) (r12 : p8 → p24 → p32 → p5) (r13 : p4 → p22 → p14) (r14 : p4 → p13 → p14 → p28) (r15 : p0 → p19 → p26) (r16 : p31 → p17) (r17 : p4 → p32 → p8) (r18 : p0 → p4 → p24) (r19 : p0 → p23 → p24 → p11) (r20 : p21 → p22 → p33) (r21 : p25 → p34 → p6) (r22 : p14 → p22 → p27 → p13) (r23 : p4 → p27 → p32) (r24 : p2 → p23 → p32 → p34) (r25 : p10 → p27 → p1) (r26 : p0 → p11 → p15) (r27 : p13 → p17 → p30) : p6 := by
  have h0 : p0 := r5 f22 f27
  have h32 : p32 := r23 f4 f27
  have h24 : p24 := r18 h0 f4
  have h23 : p23 := r3 f4 h24
  have h11 : p11 := r19 h0 h23 h24
  have h15 : p15 := r26 h0 h11
  have h2 : p2 := r1 h0 h11
  have h25 : p25 := r7 h0 h15 f27
  have h34 : p34 := r24 h2 h23 h32
  have h6 : p6 := r21 h25 h34
  exact h6
#print axioms cogModel_6aad105f0509dbbe12328a3c167a271fc3aedbd80660c390872c3e2ce3117f21

theorem cogModel_426a3fdc8c8777ffe98ab6a51220c520acb18522c719f03d59adb2096c2b0f2a (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 : Prop) (f3 : p3) (f6 : p6) (f18 : p18) (f32 : p32) (f34 : p34) (r0 : p6 → p37 → p11) (r1 : p31 → p32 → p38) (r2 : p3 → p38 → p5) (r3 : p6 → p32 → p35 → p21) (r4 : p3 → p18 → p34 → p19) (r5 : p21 → p34 → p30) (r6 : p29 → p32 → p23) (r7 : p2 → p25 → p5) (r8 : p19 → p37) (r9 : p23 → p35 → p7) (r10 : p30 → p34 → p7) (r11 : p34 → p37 → p21) (r12 : p3 → p8 → p4) (r13 : p16 → p32 → p0) (r14 : p1 → p21 → p24 → p38) (r15 : p18 → p25 → p1) (r16 : p3 → p23 → p24) (r17 : p25 → p32 → p35) (r18 : p30 → p34 → p24) (r19 : p6 → p18 → p34 → p27) (r20 : p9 → p18 → p33 → p13) (r21 : p18 → p25 → p37) (r22 : p21 → p35 → p30) (r23 : p24 → p29 → p31 → p2) (r24 : p19 → p35) (r25 : p32 → p14) (r26 : p11 → p21 → p29 → p23) (r27 : p1 → p35 → p11) (r28 : p30 → p32 → p31) (r29 : p27 → p28 → p26) (r30 : p32 → p38 → p10) (r31 : p6 → p32 → p28) (r32 : p18 → p28 → p34 → p15) (r33 : p3 → p32 → p9) (r34 : p18 → p38 → p10) (r35 : p15 → p33) (r36 : p6 → p32 → p19) (r37 : p23 → p34 → p31) (r38 : p32 → p37 → p29) (r39 : p1 → p35 → p29) (r40 : p3 → p6 → p34 → p25) (r41 : p19 → p32 → p1) (r42 : p5 → p10 → p12 → p22) (r43 : p3 → p17 → p36) (r44 : p3 → p20) (r45 : p2 → p21 → p23 → p12) : p22 := by
  have h25 : p25 := r40 f3 f6 f34
  have h1 : p1 := r15 f18 h25
  have h37 : p37 := r21 f18 h25
  have h29 : p29 := r38 f32 h37
  have h21 : p21 := r11 f34 h37
  have h23 : p23 := r6 h29 f32
  have h31 : p31 := r37 h23 f34
  have h24 : p24 := r16 f3 h23
  have h2 : p2 := r23 h24 h29 h31
  have h5 : p5 := r7 h2 h25
  have h12 : p12 := r45 h2 h21 h23
  have h38 : p38 := r14 h1 h21 h24
  have h10 : p10 := r30 f32 h38
  have h22 : p22 := r42 h5 h10 h12
  exact h22
#print axioms cogModel_426a3fdc8c8777ffe98ab6a51220c520acb18522c719f03d59adb2096c2b0f2a

theorem cogModel_6d8e1152807323850608acec3c8e7e7f8d4b04563e200948803bad47e5a0bea8 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 : Prop) (f5 : p5) (f14 : p14) (f29 : p29) (f33 : p33) (r0 : p2 → p14 → p27) (r1 : p14 → p27 → p29 → p36) (r2 : p2 → p5 → p11 → p19) (r3 : p9 → p33 → p6) (r4 : p3 → p22 → p15) (r5 : p14 → p36 → p26) (r6 : p3 → p5 → p29 → p21) (r7 : p5 → p31 → p33 → p25) (r8 : p3 → p21 → p2) (r9 : p3 → p8 → p27 → p23) (r10 : p1 → p33 → p7) (r11 : p4 → p15 → p0) (r12 : p29 → p33 → p3) (r13 : p14 → p34 → p4) (r14 : p5 → p29 → p17) (r15 : p19 → p21 → p32) (r16 : p24 → p29 → p18) (r17 : p14 → p21 → p13) (r18 : p28 → p34) (r19 : p10 → p27 → p8) (r20 : p25 → p29 → p20) (r21 : p2 → p27 → p28 → p22) (r22 : p14 → p21 → p16) (r23 : p5 → p12 → p17 → p31) (r24 : p14 → p29 → p10) (r25 : p10 → p14 → p29 → p11) (r26 : p14 → p30 → p35) (r27 : p8 → p10 → p28) (r28 : p14 → p12) : p0 := by
  have h3 : p3 := r12 f29 f33
  have h10 : p10 := r24 f14 f29
  have h21 : p21 := r6 h3 f5 f29
  have h2 : p2 := r8 h3 h21
  have h27 : p27 := r0 h2 f14
  have h8 : p8 := r19 h10 h27
  have h28 : p28 := r27 h8 h10
  have h22 : p22 := r21 h2 h27 h28
  have h34 : p34 := r18 h28
  have h15 : p15 := r4 h3 h22
  have h4 : p4 := r13 f14 h34
  have h0 : p0 := r11 h4 h15
  exact h0
#print axioms cogModel_6d8e1152807323850608acec3c8e7e7f8d4b04563e200948803bad47e5a0bea8

theorem cogModel_b22552e5712e3c23f20f009bb5b4ce71d68c7d23e4184e6026494efc34b3bfdc (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 : Prop) (f18 : p18) (f24 : p24) (f27 : p27) (r0 : p21 → p27 → p14) (r1 : p1 → p9 → p11 → p10) (r2 : p11 → p17 → p27 → p23) (r3 : p18 → p27 → p15) (r4 : p27 → p29 → p4) (r5 : p0 → p3 → p16) (r6 : p10 → p18 → p26 → p19) (r7 : p18 → p24 → p27 → p5) (r8 : p18 → p26 → p9) (r9 : p11 → p24 → p7) (r10 : p14 → p27 → p3) (r11 : p18 → p27 → p11) (r12 : p12 → p18 → p20) (r13 : p18 → p19 → p0) (r14 : p11 → p17 → p7) (r15 : p18 → p23 → p27 → p9) (r16 : p11 → p18 → p24 → p26) (r17 : p23 → p27 → p1) (r18 : p9 → p11 → p19 → p0) (r19 : p18 → p27 → p17) (r20 : p18 → p25) (r21 : p27 → p13) (r22 : p18 → p19 → p3) (r23 : p9 → p18 → p21) (r24 : p2 → p27 → p28) (r25 : p1 → p11 → p24 → p21) (r26 : p7 → p23 → p27 → p1) (r27 : p1 → p21 → p14) (r28 : p8 → p24 → p22) (r29 : p24 → p6) (r30 : p24 → p17) : p16 := by
  have h11 : p11 := r11 f18 f27
  have h26 : p26 := r16 h11 f18 f24
  have h9 : p9 := r8 f18 h26
  have h17 : p17 := r19 f18 f27
  have h7 : p7 := r14 h11 h17
  have h21 : p21 := r23 h9 f18
  have h23 : p23 := r2 h11 h17 f27
  have h14 : p14 := r0 h21 f27
  have h3 : p3 := r10 h14 f27
  have h1 : p1 := r26 h7 h23 f27
  have h10 : p10 := r1 h1 h9 h11
  have h19 : p19 := r6 h10 f18 h26
  have h0 : p0 := r13 f18 h19
  have h16 : p16 := r5 h0 h3
  exact h16
#print axioms cogModel_b22552e5712e3c23f20f009bb5b4ce71d68c7d23e4184e6026494efc34b3bfdc

theorem cogModel_6c13cb57a222687dd27189f3c9b8cd09d5bc78fb3a4410273d41a8c1d9b76bfa (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 : Prop) (f12 : p12) (f15 : p15) (f21 : p21) (f23 : p23) (r0 : p15 → p23 → p30 → p11) (r1 : p12 → p17 → p24 → p16) (r2 : p5 → p17 → p10) (r3 : p5 → p21 → p8) (r4 : p20 → p26 → p32 → p4) (r5 : p7 → p12 → p15 → p0) (r6 : p2 → p23 → p33) (r7 : p1 → p12 → p9) (r8 : p8 → p18 → p17) (r9 : p15 → p14) (r10 : p0 → p5 → p12 → p32) (r11 : p12 → p13 → p23 → p28) (r12 : p12 → p15 → p23 → p19) (r13 : p8 → p10 → p31 → p22) (r14 : p15 → p18 → p7) (r15 : p15 → p21 → p23 → p6) (r16 : p5 → p15 → p31 → p3) (r17 : p15 → p17 → p20) (r18 : p12 → p15 → p23 → p5) (r19 : p3 → p6 → p32 → p26) (r20 : p10 → p21 → p24) (r21 : p14 → p19 → p21 → p30) (r22 : p21 → p26 → p25) (r23 : p15 → p21 → p31) (r24 : p12 → p14 → p28 → p27) (r25 : p4 → p25 → p29) (r26 : p14 → p23 → p30 → p13) (r27 : p12 → p31 → p18) : p29 := by
  have h6 : p6 := r15 f15 f21 f23
  have h5 : p5 := r18 f12 f15 f23
  have h31 : p31 := r23 f15 f21
  have h3 : p3 := r16 h5 f15 h31
  have h18 : p18 := r27 f12 h31
  have h7 : p7 := r14 f15 h18
  have h0 : p0 := r5 h7 f12 f15
  have h32 : p32 := r10 h0 h5 f12
  have h26 : p26 := r19 h3 h6 h32
  have h25 : p25 := r22 f21 h26
  have h8 : p8 := r3 h5 f21
  have h17 : p17 := r8 h8 h18
  have h20 : p20 := r17 f15 h17
  have h4 : p4 := r4 h20 h26 h32
  have h29 : p29 := r25 h4 h25
  exact h29
#print axioms cogModel_6c13cb57a222687dd27189f3c9b8cd09d5bc78fb3a4410273d41a8c1d9b76bfa

theorem cogModel_8b961715aa3597037b8959a127fd9ef1b47ac0f91568b84ae6a26dec602f8d9d (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 p41 : Prop) (f13 : p13) (f23 : p23) (f27 : p27) (f34 : p34) (f41 : p41) (r0 : p23 → p41 → p16) (r1 : p20 → p34 → p5) (r2 : p10 → p15 → p11) (r3 : p23 → p34 → p22) (r4 : p15 → p20 → p26 → p5) (r5 : p13 → p34 → p33) (r6 : p13 → p34 → p19) (r7 : p11 → p27 → p28) (r8 : p23 → p33 → p12) (r9 : p16 → p18 → p21) (r10 : p4 → p33 → p37 → p9) (r11 : p16 → p21 → p23 → p35) (r12 : p16 → p29 → p18) (r13 : p19 → p41 → p4) (r14 : p6 → p21 → p41 → p10) (r15 : p39 → p41 → p1) (r16 : p34 → p36 → p32) (r17 : p0 → p13 → p35) (r18 : p2 → p21 → p28) (r19 : p6 → p13 → p15) (r20 : p23 → p34 → p25) (r21 : p2 → p31 → p26) (r22 : p23 → p28 → p20) (r23 : p20 → p34 → p24) (r24 : p27 → p41 → p29) (r25 : p10 → p41 → p2) (r26 : p14 → p23 → p17) (r27 : p18 → p22 → p29 → p15) (r28 : p27 → p38 → p3) (r29 : p21 → p23 → p31) (r30 : p0 → p6 → p31) (r31 : p22 → p6) (r32 : p10 → p36 → p24) (r33 : p5 → p24 → p32 → p7) (r34 : p20 → p36 → p32) (r35 : p6 → p23 → p21) (r36 : p2 → p15 → p26 → p20) (r37 : p22 → p34 → p18) (r38 : p13 → p40 → p30) (r39 : p13 → p34 → p29) (r40 : p10 → p22 → p2) (r41 : p13 → p23 → p16) (r42 : p6 → p27 → p0) (r43 : p18 → p28 → p36) (r44 : p8 → p23 → p37) (r45 : p19 → p8) : p7 := by
  have h22 : p22 := r3 f23 f34
  have h18 : p18 := r37 h22 f34
  have h6 : p6 := r31 h22
  have h15 : p15 := r19 h6 f13
  have h21 : p21 := r35 h6 f23
  have h31 : p31 := r29 h21 f23
  have h10 : p10 := r14 h6 h21 f41
  have h11 : p11 := r2 h10 h15
  have h2 : p2 := r40 h10 h22
  have h28 : p28 := r7 h11 f27
  have h26 : p26 := r21 h2 h31
  have h36 : p36 := r43 h18 h28
  have h24 : p24 := r32 h10 h36
  have h32 : p32 := r16 f34 h36
  have h20 : p20 := r36 h2 h15 h26
  have h5 : p5 := r4 h15 h20 h26
  have h7 : p7 := r33 h5 h24 h32
  exact h7
#print axioms cogModel_8b961715aa3597037b8959a127fd9ef1b47ac0f91568b84ae6a26dec602f8d9d

theorem cogModel_1c77f8a388e149153851766aa5b50204ef0440d1d6cc9cc12dfdd3a2ea346ea5 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 : Prop) (f24 : p24) (f25 : p25) (f35 : p35) (r0 : p8 → p24 → p25 → p7) (r1 : p24 → p33 → p3) (r2 : p17 → p24 → p2) (r3 : p11 → p25 → p29) (r4 : p10 → p12 → p28 → p27) (r5 : p10 → p15 → p22) (r6 : p5 → p10 → p22 → p17) (r7 : p20 → p14) (r8 : p25 → p35 → p21) (r9 : p2 → p6 → p15 → p4) (r10 : p25 → p31 → p32) (r11 : p6 → p5) (r12 : p5 → p22 → p12) (r13 : p24 → p25 → p26 → p20) (r14 : p4 → p13 → p19 → p18) (r15 : p4 → p21 → p19) (r16 : p10 → p23 → p0) (r17 : p5 → p17 → p23) (r18 : p26 → p16) (r19 : p6 → p28 → p9) (r20 : p10 → p24 → p6) (r21 : p9 → p18 → p27 → p1) (r22 : p10 → p24 → p15) (r23 : p0 → p24 → p25 → p13) (r24 : p24 → p35 → p10) (r25 : p35 → p26) (r26 : p16 → p24 → p25 → p34) (r27 : p24 → p26 → p35 → p8) (r28 : p24 → p36) (r29 : p2 → p4 → p28) (r30 : p6 → p21 → p30) : p1 := by
  have h10 : p10 := r24 f24 f35
  have h6 : p6 := r20 h10 f24
  have h15 : p15 := r22 h10 f24
  have h22 : p22 := r5 h10 h15
  have h5 : p5 := r11 h6
  have h17 : p17 := r6 h5 h10 h22
  have h2 : p2 := r2 h17 f24
  have h4 : p4 := r9 h2 h6 h15
  have h12 : p12 := r12 h5 h22
  have h28 : p28 := r29 h2 h4
  have h9 : p9 := r19 h6 h28
  have h27 : p27 := r4 h10 h12 h28
  have h21 : p21 := r8 f25 f35
  have h19 : p19 := r15 h4 h21
  have h23 : p23 := r17 h5 h17
  have h0 : p0 := r16 h10 h23
  have h13 : p13 := r23 h0 f24 f25
  have h18 : p18 := r14 h4 h13 h19
  have h1 : p1 := r21 h9 h18 h27
  exact h1
#print axioms cogModel_1c77f8a388e149153851766aa5b50204ef0440d1d6cc9cc12dfdd3a2ea346ea5

theorem cogModel_a01a0cef86e84c9d97e16a65388a99719274cc2b89fffd9b5ad5b9b5984a2ac5 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 : Prop) (f8 : p8) (f16 : p16) (f22 : p22) (f23 : p23) (r0 : p23 → p18) (r1 : p23 → p14) (r2 : p2 → p16 → p21) (r3 : p24 → p19) (r4 : p6 → p12) (r5 : p14 → p4) (r6 : p11 → p6) (r7 : p12 → p7) (r8 : p19 → p11) (r9 : p4 → p24) (r10 : p8 → p16 → p5) (r11 : p8 → p22 → p23 → p15) (r12 : p7 → p17) (r13 : p13 → p23 → p20) (r14 : p1 → p22 → p9) (r15 : p17 → p10) (r16 : p15 → p0) (r17 : p0 → p3) : p10 := by
  have h14 : p14 := r1 f23
  have h4 : p4 := r5 h14
  have h24 : p24 := r9 h4
  have h19 : p19 := r3 h24
  have h11 : p11 := r8 h19
  have h6 : p6 := r6 h11
  have h12 : p12 := r4 h6
  have h7 : p7 := r7 h12
  have h17 : p17 := r12 h7
  have h10 : p10 := r15 h17
  exact h10
#print axioms cogModel_a01a0cef86e84c9d97e16a65388a99719274cc2b89fffd9b5ad5b9b5984a2ac5

theorem cogModel_60000f4cfe7545b1e5dd17a0b37e00928176aea98f0bea5fea020ec681c81914 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 : Prop) (f12 : p12) (f19 : p19) (f22 : p22) (r0 : p19 → p14) (r1 : p7 → p12 → p15) (r2 : p0 → p9) (r3 : p3 → p5) (r4 : p6 → p8 → p1) (r5 : p6 → p19 → p24 → p10) (r6 : p12 → p19 → p24 → p11) (r7 : p12 → p20 → p16) (r8 : p19 → p21 → p2) (r9 : p5 → p0) (r10 : p13 → p4) (r11 : p4 → p3) (r12 : p19 → p22 → p6) (r13 : p18 → p19 → p23) (r14 : p6 → p19 → p22 → p24) (r15 : p19 → p22 → p8) (r16 : p22 → p17) (r17 : p17 → p13) : p9 := by
  have h17 : p17 := r16 f22
  have h13 : p13 := r17 h17
  have h4 : p4 := r10 h13
  have h3 : p3 := r11 h4
  have h5 : p5 := r3 h3
  have h0 : p0 := r9 h5
  have h9 : p9 := r2 h0
  exact h9
#print axioms cogModel_60000f4cfe7545b1e5dd17a0b37e00928176aea98f0bea5fea020ec681c81914

theorem cogModel_d434af171606d68ec0d203b68f771ceddbf3a80c00fbf6c5f77f378f172c5ffb (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 : Prop) (f13 : p13) (f15 : p15) (f28 : p28) (f31 : p31) (f39 : p39) (r0 : p8 → p23 → p32) (r1 : p39 → p9) (r2 : p12 → p14) (r3 : p2 → p8 → p38) (r4 : p13 → p31 → p12) (r5 : p14 → p23 → p31 → p34) (r6 : p4 → p39 → p34) (r7 : p4 → p8 → p30) (r8 : p1 → p31 → p4) (r9 : p29 → p39 → p27) (r10 : p1 → p18 → p27) (r11 : p13 → p34 → p30) (r12 : p24 → p31 → p26) (r13 : p13 → p23 → p24) (r14 : p13 → p22 → p38) (r15 : p2 → p28 → p35 → p18) (r16 : p15 → p1) (r17 : p15 → p30 → p22) (r18 : p15 → p38 → p39 → p6) (r19 : p1 → p8 → p26) (r20 : p8 → p14 → p38 → p29) (r21 : p15 → p24 → p32) (r22 : p20 → p39 → p19) (r23 : p14 → p26 → p29 → p10) (r24 : p2 → p15 → p39 → p35) (r25 : p9 → p31 → p36 → p5) (r26 : p15 → p26 → p32 → p2) (r27 : p1 → p12 → p4) (r28 : p13 → p31 → p1) (r29 : p33 → p39 → p3) (r30 : p8 → p22 → p39 → p37) (r31 : p30 → p32 → p22) (r32 : p31 → p0) (r33 : p9 → p13 → p21) (r34 : p18 → p31 → p16) (r35 : p28 → p39 → p12) (r36 : p1 → p4 → p14 → p8) (r37 : p2 → p31 → p37) (r38 : p2 → p13 → p35) (r39 : p15 → p18 → p28 → p16) (r40 : p12 → p31 → p23) (r41 : p12 → p13 → p23) (r42 : p15 → p36 → p17) (r43 : p10 → p16 → p27 → p7) (r44 : p9 → p17 → p28 → p11) (r45 : p15 → p28 → p36) (r46 : p15 → p31 → p25) (r47 : p15 → p38 → p29) (r48 : p4 → p12 → p24) : p7 := by
  have h1 : p1 := r28 f13 f31
  have h4 : p4 := r8 h1 f31
  have h34 : p34 := r6 h4 f39
  have h12 : p12 := r4 f13 f31
  have h14 : p14 := r2 h12
  have h8 : p8 := r36 h1 h4 h14
  have h26 : p26 := r19 h1 h8
  have h24 : p24 := r48 h4 h12
  have h32 : p32 := r21 f15 h24
  have h2 : p2 := r26 f15 h26 h32
  have h35 : p35 := r38 h2 f13
  have h38 : p38 := r3 h2 h8
  have h29 : p29 := r20 h8 h14 h38
  have h27 : p27 := r9 h29 f39
  have h10 : p10 := r23 h14 h26 h29
  have h18 : p18 := r15 h2 f28 h35
  have h16 : p16 := r34 h18 f31
  have h7 : p7 := r43 h10 h16 h27
  exact h7
#print axioms cogModel_d434af171606d68ec0d203b68f771ceddbf3a80c00fbf6c5f77f378f172c5ffb

theorem cogModel_7204fed6a789ce3201b8c1db0ec4702f90fbd69e537831c3e6705b3125ede1db (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 p41 p42 p43 p44 p45 : Prop) (f6 : p6) (f35 : p35) (f43 : p43) (r0 : p0 → p2 → p22 → p4) (r1 : p37 → p45 → p27) (r2 : p0 → p22 → p21) (r3 : p3 → p26 → p1) (r4 : p39 → p22) (r5 : p20 → p43 → p9) (r6 : p6 → p35 → p43 → p11) (r7 : p4 → p40) (r8 : p2 → p4 → p15) (r9 : p11 → p35 → p41 → p19) (r10 : p16 → p19 → p36 → p24) (r11 : p2 → p6 → p43 → p39) (r12 : p16 → p35 → p41 → p37) (r13 : p12 → p18) (r14 : p6 → p13 → p12) (r15 : p17 → p36 → p3) (r16 : p11 → p42 → p10) (r17 : p43 → p0) (r18 : p8 → p37 → p43 → p42) (r19 : p4 → p22 → p39 → p34) (r20 : p16 → p31 → p41 → p36) (r21 : p6 → p34 → p39 → p32) (r22 : p35 → p41) (r23 : p6 → p35 → p41 → p16) (r24 : p28 → p20) (r25 : p8 → p12 → p31) (r26 : p10 → p16 → p36 → p17) (r27 : p12 → p17 → p26) (r28 : p11 → p16 → p19 → p45) (r29 : p38 → p43 → p23) (r30 : p13 → p19 → p8) (r31 : p6 → p35 → p39 → p28) (r32 : p6 → p2) (r33 : p30 → p34 → p25) (r34 : p0 → p6 → p35 → p30) (r35 : p11 → p37 → p13) (r36 : p33 → p43 → p7) (r37 : p28 → p30 → p5) (r38 : p11 → p41 → p29) (r39 : p25 → p28 → p30 → p44) (r40 : p2 → p35 → p39 → p14) : p1 := by
  have h41 : p41 := r22 f35
  have h16 : p16 := r23 f6 f35 h41
  have h37 : p37 := r12 h16 f35 h41
  have h11 : p11 := r6 f6 f35 f43
  have h13 : p13 := r35 h11 h37
  have h12 : p12 := r14 f6 h13
  have h19 : p19 := r9 h11 f35 h41
  have h8 : p8 := r30 h13 h19
  have h42 : p42 := r18 h8 h37 f43
  have h10 : p10 := r16 h11 h42
  have h31 : p31 := r25 h8 h12
  have h36 : p36 := r20 h16 h31 h41
  have h17 : p17 := r26 h10 h16 h36
  have h3 : p3 := r15 h17 h36
  have h26 : p26 := r27 h12 h17
  have h1 : p1 := r3 h3 h26
  exact h1
#print axioms cogModel_7204fed6a789ce3201b8c1db0ec4702f90fbd69e537831c3e6705b3125ede1db

theorem cogModel_9774335c958285216371a2ebf0e782b5e58cfb51e69e6f1c9e620993ec647a5b (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 : Prop) (f5 : p5) (f16 : p16) (f18 : p18) (f21 : p21) (r0 : p12 → p31) (r1 : p18 → p21 → p7) (r2 : p10 → p21 → p15) (r3 : p5 → p18 → p26) (r4 : p5 → p11 → p20) (r5 : p10 → p18 → p4) (r6 : p25 → p26 → p29 → p17) (r7 : p16 → p24 → p1) (r8 : p4 → p7 → p30) (r9 : p4 → p12 → p21 → p14) (r10 : p4 → p8 → p18 → p13) (r11 : p18 → p26 → p19) (r12 : p6 → p27 → p3) (r13 : p18 → p0) (r14 : p16 → p21 → p26 → p25) (r15 : p5 → p17 → p22) (r16 : p7 → p15 → p28 → p8) (r17 : p16 → p18 → p21 → p10) (r18 : p18 → p30 → p31 → p27) (r19 : p5 → p7 → p28) (r20 : p8 → p14 → p21 → p6) (r21 : p8 → p15 → p12) (r22 : p16 → p23 → p9) (r23 : p4 → p7 → p15 → p2) (r24 : p0 → p25 → p24) (r25 : p16 → p21 → p29) : p3 := by
  have h10 : p10 := r17 f16 f18 f21
  have h4 : p4 := r5 h10 f18
  have h7 : p7 := r1 f18 f21
  have h30 : p30 := r8 h4 h7
  have h15 : p15 := r2 h10 f21
  have h28 : p28 := r19 f5 h7
  have h8 : p8 := r16 h7 h15 h28
  have h12 : p12 := r21 h8 h15
  have h14 : p14 := r9 h4 h12 f21
  have h31 : p31 := r0 h12
  have h6 : p6 := r20 h8 h14 f21
  have h27 : p27 := r18 f18 h30 h31
  have h3 : p3 := r12 h6 h27
  exact h3
#print axioms cogModel_9774335c958285216371a2ebf0e782b5e58cfb51e69e6f1c9e620993ec647a5b

theorem cogModel_1721f3e21281778d918065237a6087b6d4cec3215c79901cd2bcb795a06664cb (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 : Prop) (f0 : p0) (f25 : p25) (f29 : p29) (f34 : p34) (r0 : p29 → p33) (r1 : p10 → p27) (r2 : p25 → p29 → p32 → p13) (r3 : p0 → p5 → p29 → p23) (r4 : p3 → p13 → p14 → p10) (r5 : p3 → p13 → p14 → p9) (r6 : p29 → p34 → p14) (r7 : p0 → p16 → p17) (r8 : p6 → p29 → p35) (r9 : p23 → p1) (r10 : p2 → p22 → p24) (r11 : p0 → p14 → p25 → p3) (r12 : p0 → p30) (r13 : p0 → p5) (r14 : p5 → p29 → p34 → p4) (r15 : p8 → p34 → p11) (r16 : p9 → p25 → p8) (r17 : p1 → p4 → p5 → p28) (r18 : p25 → p33 → p31) (r19 : p29 → p21) (r20 : p0 → p12 → p20) (r21 : p10 → p11 → p22) (r22 : p5 → p25 → p34 → p26) (r23 : p34 → p18) (r24 : p7 → p25 → p19) (r25 : p0 → p32) (r26 : p9 → p11 → p27 → p2) (r27 : p0 → p3 → p8 → p15) : p24 := by
  have h14 : p14 := r6 f29 f34
  have h3 : p3 := r11 f0 h14 f25
  have h32 : p32 := r25 f0
  have h13 : p13 := r2 f25 f29 h32
  have h9 : p9 := r5 h3 h13 h14
  have h10 : p10 := r4 h3 h13 h14
  have h27 : p27 := r1 h10
  have h8 : p8 := r16 h9 f25
  have h11 : p11 := r15 h8 f34
  have h22 : p22 := r21 h10 h11
  have h2 : p2 := r26 h9 h11 h27
  have h24 : p24 := r10 h2 h22
  exact h24
#print axioms cogModel_1721f3e21281778d918065237a6087b6d4cec3215c79901cd2bcb795a06664cb

theorem cogModel_ad5a1ad9512fd069ff6c371c5a99f19a7fdf6d06f3d6a40a820d5c9ca8bb6f42 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 : Prop) (f1 : p1) (f17 : p17) (f20 : p20) (f28 : p28) (r0 : p4 → p12 → p25) (r1 : p15 → p28 → p10) (r2 : p22 → p31 → p5) (r3 : p12 → p26 → p27) (r4 : p20 → p22 → p30) (r5 : p7 → p18 → p12) (r6 : p1 → p17 → p3) (r7 : p17 → p32 → p15) (r8 : p28 → p31 → p5) (r9 : p20 → p28 → p3) (r10 : p7 → p16 → p21 → p26) (r11 : p20 → p24 → p28 → p0) (r12 : p20 → p24 → p0) (r13 : p8 → p20 → p23) (r14 : p0 → p1 → p28 → p18) (r15 : p18 → p30 → p14) (r16 : p1 → p24 → p22) (r17 : p15 → p17 → p21) (r18 : p1 → p4 → p25) (r19 : p0 → p3 → p30) (r20 : p17 → p20 → p28 → p8) (r21 : p1 → p2 → p8 → p13) (r22 : p17 → p21 → p16) (r23 : p3 → p6 → p21) (r24 : p25 → p27 → p29) (r25 : p31 → p16) (r26 : p11 → p17 → p19) (r27 : p1 → p3 → p22) (r28 : p22 → p28 → p32) (r29 : p9 → p28 → p34) (r30 : p1 → p7 → p4) (r31 : p6 → p20 → p31) (r32 : p17 → p18 → p32 → p15) (r33 : p1 → p24) (r34 : p1 → p17 → p20 → p33) (r35 : p6 → p24 → p30 → p10) (r36 : p14 → p18 → p20 → p31) (r37 : p20 → p35) (r38 : p30 → p32 → p6) (r39 : p0 → p1 → p22 → p32) (r40 : p20 → p21 → p7) (r41 : p8 → p17 → p35 → p2) (r42 : p14 → p21 → p30 → p7) (r43 : p16 → p32 → p4) : p29 := by
  have h3 : p3 := r6 f1 f17
  have h22 : p22 := r27 f1 h3
  have h32 : p32 := r28 h22 f28
  have h15 : p15 := r7 f17 h32
  have h21 : p21 := r17 h15 f17
  have h16 : p16 := r22 f17 h21
  have h7 : p7 := r40 f20 h21
  have h26 : p26 := r10 h7 h16 h21
  have h4 : p4 := r43 h16 h32
  have h25 : p25 := r18 f1 h4
  have h24 : p24 := r33 f1
  have h0 : p0 := r12 f20 h24
  have h18 : p18 := r14 h0 f1 f28
  have h12 : p12 := r5 h7 h18
  have h27 : p27 := r3 h12 h26
  have h29 : p29 := r24 h25 h27
  exact h29
#print axioms cogModel_ad5a1ad9512fd069ff6c371c5a99f19a7fdf6d06f3d6a40a820d5c9ca8bb6f42

theorem cogModel_46779cde45884f824b50eeaa770ba785852b6c94d90dbc039b0bd9307fd5749d (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 p41 p42 : Prop) (f7 : p7) (f9 : p9) (f14 : p14) (f36 : p36) (f40 : p40) (r0 : p31 → p38 → p26) (r1 : p0 → p2 → p7 → p23) (r2 : p4 → p12 → p36 → p41) (r3 : p2 → p6 → p25) (r4 : p7 → p35 → p18) (r5 : p7 → p36 → p24) (r6 : p0 → p16 → p3) (r7 : p3 → p7 → p37) (r8 : p5 → p23 → p24 → p1) (r9 : p11 → p21 → p15) (r10 : p12 → p17 → p40 → p10) (r11 : p30 → p36 → p33) (r12 : p7 → p27) (r13 : p25 → p40 → p21) (r14 : p0 → p3 → p11) (r15 : p0 → p37 → p5) (r16 : p1 → p14 → p40 → p38) (r17 : p8 → p34) (r18 : p0 → p9 → p13) (r19 : p8 → p17) (r20 : p22 → p36 → p28) (r21 : p4 → p12) (r22 : p14 → p4) (r23 : p13 → p40 → p6) (r24 : p1 → p31) (r25 : p2 → p40 → p16) (r26 : p9 → p0) (r27 : p4 → p12 → p34 → p20) (r28 : p1 → p36 → p31) (r29 : p9 → p14 → p19) (r30 : p6 → p9 → p3) (r31 : p23 → p25 → p36 → p21) (r32 : p29 → p40 → p32) (r33 : p2 → p36 → p23) (r34 : p2 → p7 → p29 → p32) (r35 : p16 → p40 → p25) (r36 : p7 → p9 → p0) (r37 : p0 → p2 → p7 → p6) (r38 : p0 → p13 → p16) (r39 : p14 → p8) (r40 : p9 → p40 → p24) (r41 : p1 → p9 → p38) (r42 : p16 → p37 → p29) (r43 : p9 → p42 → p39) (r44 : p0 → p14 → p19 → p2) : p26 := by
  have h24 : p24 := r5 f7 f36
  have h0 : p0 := r26 f9
  have h13 : p13 := r18 h0 f9
  have h6 : p6 := r23 h13 f40
  have h3 : p3 := r30 h6 f9
  have h37 : p37 := r7 h3 f7
  have h5 : p5 := r15 h0 h37
  have h19 : p19 := r29 f9 f14
  have h2 : p2 := r44 h0 f14 h19
  have h23 : p23 := r33 h2 f36
  have h1 : p1 := r8 h5 h23 h24
  have h31 : p31 := r24 h1
  have h38 : p38 := r41 h1 f9
  have h26 : p26 := r0 h31 h38
  exact h26
#print axioms cogModel_46779cde45884f824b50eeaa770ba785852b6c94d90dbc039b0bd9307fd5749d

theorem cogModel_aa819ba6adf75679a59410676aebf7a326ae8191951bc5d8707a2bec3e254aba (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 : Prop) (f4 : p4) (f5 : p5) (f27 : p27) (r0 : p4 → p27 → p20) (r1 : p5 → p21 → p34) (r2 : p5 → p24 → p23) (r3 : p21 → p35 → p9) (r4 : p6 → p21 → p1) (r5 : p7 → p24) (r6 : p0 → p27 → p6) (r7 : p4 → p5 → p27 → p26) (r8 : p1 → p9 → p34 → p30) (r9 : p5 → p22 → p0) (r10 : p2 → p22 → p27 → p16) (r11 : p5 → p21 → p1) (r12 : p5 → p19 → p9) (r13 : p4 → p18 → p11) (r14 : p27 → p17) (r15 : p6 → p27 → p13) (r16 : p4 → p31 → p32) (r17 : p4 → p5 → p10) (r18 : p6 → p7 → p27 → p13) (r19 : p10 → p20 → p25) (r20 : p5 → p35 → p19) (r21 : p5 → p13 → p3) (r22 : p2 → p4 → p0) (r23 : p0 → p27 → p7) (r24 : p27 → p28) (r25 : p2 → p20 → p24 → p23) (r26 : p0 → p20 → p6) (r27 : p16 → p22 → p7) (r28 : p10 → p22) (r29 : p20 → p27 → p2) (r30 : p24 → p27 → p35) (r31 : p5 → p17 → p29) (r32 : p19 → p35 → p34) (r33 : p10 → p27 → p2) (r34 : p27 → p33 → p8) (r35 : p12 → p25 → p3) (r36 : p4 → p7 → p27 → p12) (r37 : p5 → p27 → p15) (r38 : p5 → p27 → p20) (r39 : p4 → p23 → p21) (r40 : p24 → p27 → p35 → p19) (r41 : p26 → p27 → p29 → p14) : p30 := by
  have h10 : p10 := r17 f4 f5
  have h2 : p2 := r33 h10 f27
  have h0 : p0 := r22 h2 f4
  have h6 : p6 := r6 h0 f27
  have h7 : p7 := r23 h0 f27
  have h24 : p24 := r5 h7
  have h23 : p23 := r2 f5 h24
  have h35 : p35 := r30 h24 f27
  have h19 : p19 := r40 h24 f27 h35
  have h34 : p34 := r32 h19 h35
  have h9 : p9 := r12 f5 h19
  have h21 : p21 := r39 f4 h23
  have h1 : p1 := r4 h6 h21
  have h30 : p30 := r8 h1 h9 h34
  exact h30
#print axioms cogModel_aa819ba6adf75679a59410676aebf7a326ae8191951bc5d8707a2bec3e254aba

theorem cogModel_2b1242d93e9de878d575d4b633414ef2f06a0f987ae3e3791cc9179484908ab0 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 : Prop) (f4 : p4) (f8 : p8) (f20 : p20) (f28 : p28) (r0 : p7 → p15 → p27) (r1 : p4 → p28 → p10) (r2 : p9 → p17 → p26 → p29) (r3 : p1 → p24 → p28 → p14) (r4 : p8 → p10 → p20 → p23) (r5 : p4 → p21) (r6 : p4 → p20 → p28 → p25) (r7 : p4 → p20 → p24) (r8 : p4 → p14 → p18) (r9 : p2 → p21 → p28 → p7) (r10 : p25 → p28 → p3) (r11 : p12 → p27 → p26) (r12 : p12 → p20 → p9) (r13 : p20 → p28 → p1) (r14 : p3 → p8 → p12 → p17) (r15 : p4 → p8 → p10 → p0) (r16 : p2 → p3 → p15) (r17 : p7 → p11 → p27 → p5) (r18 : p16 → p20 → p6) (r19 : p21 → p28 → p2) (r20 : p3 → p4 → p28 → p11) (r21 : p19 → p28 → p22) (r22 : p7 → p13 → p15 → p12) (r23 : p15 → p13) : p29 := by
  have h25 : p25 := r6 f4 f20 f28
  have h3 : p3 := r10 h25 f28
  have h21 : p21 := r5 f4
  have h2 : p2 := r19 h21 f28
  have h15 : p15 := r16 h2 h3
  have h13 : p13 := r23 h15
  have h7 : p7 := r9 h2 h21 f28
  have h27 : p27 := r0 h7 h15
  have h12 : p12 := r22 h7 h13 h15
  have h26 : p26 := r11 h12 h27
  have h17 : p17 := r14 h3 f8 h12
  have h9 : p9 := r12 h12 f20
  have h29 : p29 := r2 h9 h17 h26
  exact h29
#print axioms cogModel_2b1242d93e9de878d575d4b633414ef2f06a0f987ae3e3791cc9179484908ab0

theorem cogModel_3050e957a485db5a9de128979d11e0462145c5488aee0b56d411b3f0cc4d71cc (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 : Prop) (f5 : p5) (f26 : p26) (f29 : p29) (r0 : p1 → p7 → p2) (r1 : p5 → p18 → p20 → p33) (r2 : p5 → p16 → p3) (r3 : p5 → p29 → p13) (r4 : p26 → p28 → p30) (r5 : p5 → p13 → p10) (r6 : p26 → p33 → p11) (r7 : p2 → p26 → p28 → p30) (r8 : p1 → p21 → p26 → p28) (r9 : p1 → p30 → p19) (r10 : p6 → p29 → p18) (r11 : p5 → p29 → p0) (r12 : p5 → p15 → p27) (r13 : p5 → p26 → p4) (r14 : p0 → p29 → p7) (r15 : p17 → p20 → p32) (r16 : p20 → p28 → p6) (r17 : p1 → p26 → p28) (r18 : p26 → p21) (r19 : p5 → p26 → p21) (r20 : p19 → p29 → p25) (r21 : p7 → p18 → p17) (r22 : p26 → p0) (r23 : p18 → p29 → p23) (r24 : p5 → p33 → p11) (r25 : p26 → p29 → p8) (r26 : p25 → p29 → p17) (r27 : p0 → p5 → p29 → p1) (r28 : p24 → p29 → p12) (r29 : p19 → p28 → p18) (r30 : p2 → p31) (r31 : p22 → p29 → p16) (r32 : p8 → p29 → p22) (r33 : p2 → p18 → p21 → p23) (r34 : p23 → p26 → p9) (r35 : p29 → p33 → p9) (r36 : p6 → p20 → p25) (r37 : p9 → p11 → p32 → p14) (r38 : p2 → p28 → p20) (r39 : p5 → p30 → p19) : p14 := by
  have h0 : p0 := r11 f5 f29
  have h7 : p7 := r14 h0 f29
  have h1 : p1 := r27 h0 f5 f29
  have h21 : p21 := r19 f5 f26
  have h28 : p28 := r8 h1 h21 f26
  have h30 : p30 := r4 f26 h28
  have h19 : p19 := r39 f5 h30
  have h25 : p25 := r20 h19 f29
  have h17 : p17 := r26 h25 f29
  have h18 : p18 := r29 h19 h28
  have h23 : p23 := r23 h18 f29
  have h9 : p9 := r34 h23 f26
  have h2 : p2 := r0 h1 h7
  have h20 : p20 := r38 h2 h28
  have h32 : p32 := r15 h17 h20
  have h33 : p33 := r1 f5 h18 h20
  have h11 : p11 := r6 f26 h33
  have h14 : p14 := r37 h9 h11 h32
  exact h14
#print axioms cogModel_3050e957a485db5a9de128979d11e0462145c5488aee0b56d411b3f0cc4d71cc

theorem cogModel_7f9823beb15c2a7740c681920441742cdaa6202c5ce0d88fc4a5a2b767c3bd9f (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 : Prop) (f7 : p7) (f9 : p9) (f12 : p12) (f13 : p13) (r0 : p9 → p12 → p17) (r1 : p9 → p23 → p11) (r2 : p7 → p20 → p5) (r3 : p6 → p18) (r4 : p10 → p6) (r5 : p9 → p15 → p16) (r6 : p7 → p23) (r7 : p4 → p9 → p0) (r8 : p13 → p10) (r9 : p9 → p17 → p21 → p19) (r10 : p1 → p22) (r11 : p8 → p1) (r12 : p7 → p12 → p13 → p14) (r13 : p7 → p21) (r14 : p22 → p3) (r15 : p2 → p8) (r16 : p18 → p2) : p3 := by
  have h10 : p10 := r8 f13
  have h6 : p6 := r4 h10
  have h18 : p18 := r3 h6
  have h2 : p2 := r16 h18
  have h8 : p8 := r15 h2
  have h1 : p1 := r11 h8
  have h22 : p22 := r10 h1
  have h3 : p3 := r14 h22
  exact h3
#print axioms cogModel_7f9823beb15c2a7740c681920441742cdaa6202c5ce0d88fc4a5a2b767c3bd9f

theorem cogModel_b70f78e3493a3c01fc8415dcc5ef56ce342a4d2027dd4381ca8b2af31c13ffc7 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 : Prop) (f4 : p4) (f6 : p6) (f14 : p14) (f15 : p15) (r0 : p8 → p14 → p22 → p1) (r1 : p10 → p20 → p22 → p11) (r2 : p19 → p16) (r3 : p20 → p10) (r4 : p6 → p12) (r5 : p2 → p11 → p3) (r6 : p4 → p14 → p23 → p8) (r7 : p14 → p15 → p23) (r8 : p16 → p18) (r9 : p17 → p5) (r10 : p13 → p17) (r11 : p0 → p6 → p21) (r12 : p4 → p14 → p2) (r13 : p5 → p19) (r14 : p12 → p13) (r15 : p4 → p14 → p23 → p20) (r16 : p4 → p10 → p22) (r17 : p9 → p15 → p7) : p18 := by
  have h12 : p12 := r4 f6
  have h13 : p13 := r14 h12
  have h17 : p17 := r10 h13
  have h5 : p5 := r9 h17
  have h19 : p19 := r13 h5
  have h16 : p16 := r2 h19
  have h18 : p18 := r8 h16
  exact h18
#print axioms cogModel_b70f78e3493a3c01fc8415dcc5ef56ce342a4d2027dd4381ca8b2af31c13ffc7

theorem cogModel_4e7932b4e82721c50df17646e207e2bbebd6a395f03c894faefba02052980ba0 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 p41 p42 : Prop) (f3 : p3) (f33 : p33) (f35 : p35) (f38 : p38) (r0 : p12 → p20 → p36 → p13) (r1 : p3 → p10 → p42 → p1) (r2 : p14 → p41 → p2) (r3 : p38 → p28) (r4 : p4 → p15 → p33 → p24) (r5 : p7 → p23 → p37 → p12) (r6 : p1 → p31 → p30) (r7 : p30 → p40 → p32) (r8 : p3 → p10 → p42) (r9 : p3 → p34 → p7) (r10 : p22 → p38 → p29) (r11 : p38 → p27) (r12 : p6 → p35 → p38 → p0) (r13 : p5 → p9 → p33 → p39) (r14 : p26 → p40) (r15 : p10 → p23 → p41 → p14) (r16 : p17 → p42 → p26) (r17 : p3 → p9) (r18 : p7 → p20 → p37) (r19 : p0 → p3 → p16 → p5) (r20 : p11 → p36 → p31) (r21 : p3 → p36 → p38 → p41) (r22 : p6 → p25) (r23 : p6 → p33 → p35 → p21) (r24 : p0 → p6 → p38 → p16) (r25 : p38 → p34) (r26 : p1 → p2 → p11) (r27 : p7 → p33 → p41 → p23) (r28 : p0 → p8) (r29 : p3 → p15) (r30 : p35 → p38 → p6) (r31 : p3 → p33 → p38 → p4) (r32 : p35 → p38 → p36) (r33 : p20 → p33 → p10) (r34 : p33 → p36 → p20) (r35 : p3 → p19 → p18) (r36 : p2 → p34 → p17) : p32 := by
  have h36 : p36 := r32 f35 f38
  have h41 : p41 := r21 f3 h36 f38
  have h34 : p34 := r25 f38
  have h20 : p20 := r34 f33 h36
  have h10 : p10 := r33 h20 f33
  have h42 : p42 := r8 f3 h10
  have h1 : p1 := r1 f3 h10 h42
  have h7 : p7 := r9 f3 h34
  have h23 : p23 := r27 h7 f33 h41
  have h14 : p14 := r15 h10 h23 h41
  have h2 : p2 := r2 h14 h41
  have h11 : p11 := r26 h1 h2
  have h31 : p31 := r20 h11 h36
  have h30 : p30 := r6 h1 h31
  have h17 : p17 := r36 h2 h34
  have h26 : p26 := r16 h17 h42
  have h40 : p40 := r14 h26
  have h32 : p32 := r7 h30 h40
  exact h32
#print axioms cogModel_4e7932b4e82721c50df17646e207e2bbebd6a395f03c894faefba02052980ba0

theorem cogModel_ac4fb7d4a11cc4b69766254c944242725df933d3c96e2956a00ac71396235c0d (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 : Prop) (f3 : p3) (f22 : p22) (f24 : p24) (r0 : p9 → p16 → p24 → p27) (r1 : p3 → p37 → p31) (r2 : p0 → p24 → p26 → p5) (r3 : p3 → p35 → p40 → p2) (r4 : p20 → p22 → p34) (r5 : p3 → p38 → p6) (r6 : p22 → p24 → p38) (r7 : p4 → p14 → p39 → p15) (r8 : p3 → p13 → p32) (r9 : p2 → p24 → p7) (r10 : p4 → p40 → p30) (r11 : p3 → p24 → p35) (r12 : p30 → p38 → p25) (r13 : p22 → p38 → p40 → p14) (r14 : p6 → p17 → p39) (r15 : p20 → p22 → p11) (r16 : p23 → p28 → p39 → p36) (r17 : p10 → p17 → p22 → p28) (r18 : p3 → p22 → p24 → p9) (r19 : p15 → p22 → p40 → p13) (r20 : p11 → p20 → p24 → p16) (r21 : p24 → p26 → p28 → p4) (r22 : p3 → p9 → p20 → p21) (r23 : p9 → p20 → p24 → p18) (r24 : p6 → p38 → p1) (r25 : p15 → p24 → p35 → p0) (r26 : p1 → p38 → p19) (r27 : p3 → p22 → p40) (r28 : p1 → p35 → p38 → p17) (r29 : p3 → p22 → p20) (r30 : p3 → p19 → p26) (r31 : p5 → p32 → p33 → p12) (r32 : p13 → p28 → p40 → p33) (r33 : p8 → p24 → p29) (r34 : p3 → p6 → p22 → p23) (r35 : p7 → p35 → p10) : p12 := by
  have h40 : p40 := r27 f3 f22
  have h35 : p35 := r11 f3 f24
  have h2 : p2 := r3 f3 h35 h40
  have h7 : p7 := r9 h2 f24
  have h10 : p10 := r35 h7 h35
  have h38 : p38 := r6 f22 f24
  have h14 : p14 := r13 f22 h38 h40
  have h6 : p6 := r5 f3 h38
  have h1 : p1 := r24 h6 h38
  have h19 : p19 := r26 h1 h38
  have h26 : p26 := r30 f3 h19
  have h17 : p17 := r28 h1 h35 h38
  have h28 : p28 := r17 h10 h17 f22
  have h4 : p4 := r21 f24 h26 h28
  have h39 : p39 := r14 h6 h17
  have h15 : p15 := r7 h4 h14 h39
  have h0 : p0 := r25 h15 f24 h35
  have h5 : p5 := r2 h0 f24 h26
  have h13 : p13 := r19 h15 f22 h40
  have h32 : p32 := r8 f3 h13
  have h33 : p33 := r32 h13 h28 h40
  have h12 : p12 := r31 h5 h32 h33
  exact h12
#print axioms cogModel_ac4fb7d4a11cc4b69766254c944242725df933d3c96e2956a00ac71396235c0d

theorem cogModel_84f485edcea7f3a1ffa849dc577e88fa814e5e667ad117923fc0a47b213414bb (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 : Prop) (f3 : p3) (f9 : p9) (f20 : p20) (f24 : p24) (f25 : p25) (r0 : p16 → p2) (r1 : p0 → p23) (r2 : p11 → p4) (r3 : p6 → p20 → p24 → p13) (r4 : p3 → p16) (r5 : p12 → p17) (r6 : p1 → p12) (r7 : p10 → p25 → p15) (r8 : p3 → p21 → p7) (r9 : p2 → p0) (r10 : p4 → p27) (r11 : p14 → p24 → p25 → p26) (r12 : p3 → p20 → p14) (r13 : p6 → p20 → p18) (r14 : p9 → p20 → p25 → p5) (r15 : p23 → p11) (r16 : p3 → p19 → p22) (r17 : p13 → p18 → p20 → p8) (r18 : p9 → p24 → p25 → p6) (r19 : p27 → p1) : p17 := by
  have h16 : p16 := r4 f3
  have h2 : p2 := r0 h16
  have h0 : p0 := r9 h2
  have h23 : p23 := r1 h0
  have h11 : p11 := r15 h23
  have h4 : p4 := r2 h11
  have h27 : p27 := r10 h4
  have h1 : p1 := r19 h27
  have h12 : p12 := r6 h1
  have h17 : p17 := r5 h12
  exact h17
#print axioms cogModel_84f485edcea7f3a1ffa849dc577e88fa814e5e667ad117923fc0a47b213414bb

theorem cogModel_9337febda1f2eaae72a42d024d660bc865cccd852d21eccfa13a2380dc385b85 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 : Prop) (f10 : p10) (f11 : p11) (f17 : p17) (r0 : p10 → p17 → p4) (r1 : p11 → p5) (r2 : p6 → p13) (r3 : p13 → p12) (r4 : p17 → p19 → p7) (r5 : p4 → p10 → p15 → p0) (r6 : p18 → p8) (r7 : p10 → p14 → p9) (r8 : p8 → p6) (r9 : p10 → p2) (r10 : p12 → p16) (r11 : p1 → p4 → p10 → p15) (r12 : p5 → p18) (r13 : p4 → p17 → p1) (r14 : p10 → p17 → p3) : p16 := by
  have h5 : p5 := r1 f11
  have h18 : p18 := r12 h5
  have h8 : p8 := r6 h18
  have h6 : p6 := r8 h8
  have h13 : p13 := r2 h6
  have h12 : p12 := r3 h13
  have h16 : p16 := r10 h12
  exact h16
#print axioms cogModel_9337febda1f2eaae72a42d024d660bc865cccd852d21eccfa13a2380dc385b85

theorem cogModel_282f57f997831eeb1dee661e1ab4930bd275ec03e546d00863cf5f0fd7b73d53 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 : Prop) (f9 : p9) (f10 : p10) (f22 : p22) (f24 : p24) (r0 : p6 → p1) (r1 : p12 → p26 → p4) (r2 : p3 → p17) (r3 : p10 → p27 → p23) (r4 : p24 → p21) (r5 : p9 → p25 → p19) (r6 : p7 → p22 → p11) (r7 : p2 → p22 → p15) (r8 : p9 → p10 → p24 → p7) (r9 : p9 → p16 → p0) (r10 : p20 → p14) (r11 : p11 → p26 → p13) (r12 : p21 → p20) (r13 : p14 → p6) (r14 : p1 → p3) (r15 : p7 → p22 → p12) (r16 : p17 → p5) (r17 : p9 → p26) (r18 : p22 → p24 → p18) (r19 : p5 → p8) : p8 := by
  have h21 : p21 := r4 f24
  have h20 : p20 := r12 h21
  have h14 : p14 := r10 h20
  have h6 : p6 := r13 h14
  have h1 : p1 := r0 h6
  have h3 : p3 := r14 h1
  have h17 : p17 := r2 h3
  have h5 : p5 := r16 h17
  have h8 : p8 := r19 h5
  exact h8
#print axioms cogModel_282f57f997831eeb1dee661e1ab4930bd275ec03e546d00863cf5f0fd7b73d53

theorem cogModel_cde02ff3f3b836cd81ebee875b458d5e3db8f3e7712761158272be070e4a1740 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 : Prop) (f5 : p5) (f22 : p22) (f27 : p27) (f30 : p30) (r0 : p21 → p29 → p30 → p34) (r1 : p5 → p27 → p31) (r2 : p2 → p14 → p13) (r3 : p5 → p27 → p19) (r4 : p2 → p3 → p4 → p14) (r5 : p5 → p15 → p30 → p26) (r6 : p28 → p34 → p33) (r7 : p7 → p11 → p21 → p25) (r8 : p7 → p31 → p21) (r9 : p14 → p27 → p28) (r10 : p5 → p22 → p36 → p6) (r11 : p2 → p24 → p29 → p1) (r12 : p5 → p27 → p30 → p15) (r13 : p2 → p8 → p16) (r14 : p22 → p29 → p3) (r15 : p5 → p27 → p7) (r16 : p7 → p30 → p31 → p11) (r17 : p17 → p22 → p37) (r18 : p5 → p15 → p22 → p36) (r19 : p9 → p31 → p32) (r20 : p3 → p31 → p4) (r21 : p12 → p22 → p0) (r22 : p1 → p16 → p18 → p35) (r23 : p23 → p27 → p20) (r24 : p10 → p14 → p32 → p8) (r25 : p7 → p30 → p29) (r26 : p4 → p28 → p24) (r27 : p10 → p33 → p18) (r28 : p3 → p21 → p10) (r29 : p2 → p5 → p9) (r30 : p11 → p34 → p2) : p35 := by
  have h7 : p7 := r15 f5 f27
  have h29 : p29 := r25 h7 f30
  have h3 : p3 := r14 f22 h29
  have h31 : p31 := r1 f5 f27
  have h21 : p21 := r8 h7 h31
  have h34 : p34 := r0 h21 h29 f30
  have h10 : p10 := r28 h3 h21
  have h4 : p4 := r20 h3 h31
  have h11 : p11 := r16 h7 f30 h31
  have h2 : p2 := r30 h11 h34
  have h14 : p14 := r4 h2 h3 h4
  have h28 : p28 := r9 h14 f27
  have h33 : p33 := r6 h28 h34
  have h18 : p18 := r27 h10 h33
  have h9 : p9 := r29 h2 f5
  have h32 : p32 := r19 h9 h31
  have h8 : p8 := r24 h10 h14 h32
  have h16 : p16 := r13 h2 h8
  have h24 : p24 := r26 h4 h28
  have h1 : p1 := r11 h2 h24 h29
  have h35 : p35 := r22 h1 h16 h18
  exact h35
#print axioms cogModel_cde02ff3f3b836cd81ebee875b458d5e3db8f3e7712761158272be070e4a1740

theorem cogModel_8f164260ea678330e6343d5d41f4d73cafb47e10f5c084dba1e3ffa90ce7f595 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 : Prop) (f9 : p9) (f17 : p17) (f18 : p18) (r0 : p21 → p11) (r1 : p1 → p5) (r2 : p6 → p2) (r3 : p7 → p20) (r4 : p9 → p14) (r5 : p17 → p1) (r6 : p10 → p18 → p19) (r7 : p9 → p17 → p18 → p22) (r8 : p9 → p17 → p16) (r9 : p13 → p7) (r10 : p9 → p18 → p22 → p21) (r11 : p14 → p18 → p15) (r12 : p0 → p8) (r13 : p8 → p13) (r14 : p3 → p0) (r15 : p5 → p3) (r16 : p12 → p17 → p4) (r17 : p9 → p15 → p18 → p6) : p20 := by
  have h1 : p1 := r5 f17
  have h5 : p5 := r1 h1
  have h3 : p3 := r15 h5
  have h0 : p0 := r14 h3
  have h8 : p8 := r12 h0
  have h13 : p13 := r13 h8
  have h7 : p7 := r9 h13
  have h20 : p20 := r3 h7
  exact h20
#print axioms cogModel_8f164260ea678330e6343d5d41f4d73cafb47e10f5c084dba1e3ffa90ce7f595

theorem cogModel_b7b1daa3bd001bd5a21b08a170da037a342e875e004d8c5dd13afb14cf04bf5d (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 : Prop) (f4 : p4) (f18 : p18) (f26 : p26) (r0 : p23 → p29 → p21) (r1 : p18 → p26 → p6) (r2 : p1 → p30 → p36 → p17) (r3 : p4 → p26 → p34) (r4 : p0 → p7 → p27) (r5 : p1 → p2 → p28) (r6 : p4 → p26 → p2) (r7 : p20 → p0) (r8 : p7 → p14 → p20 → p23) (r9 : p7 → p23 → p29 → p11) (r10 : p2 → p4 → p3) (r11 : p15 → p35 → p12) (r12 : p16 → p18 → p36 → p19) (r13 : p17 → p19 → p28 → p22) (r14 : p10 → p26 → p13) (r15 : p2 → p30 → p7) (r16 : p4 → p34 → p31) (r17 : p0 → p21 → p23 → p1) (r18 : p9 → p18 → p34 → p15) (r19 : p3 → p36 → p29) (r20 : p25 → p26 → p24) (r21 : p15 → p35) (r22 : p6 → p14 → p21 → p16) (r23 : p4 → p26 → p34 → p9) (r24 : p2 → p6 → p30) (r25 : p4 → p15 → p8) (r26 : p6 → p30 → p36) (r27 : p26 → p32) (r28 : p3 → p26 → p20) (r29 : p26 → p33 → p5) (r30 : p2 → p6 → p26 → p14) : p22 := by
  have h2 : p2 := r6 f4 f26
  have h6 : p6 := r1 f18 f26
  have h30 : p30 := r24 h2 h6
  have h36 : p36 := r26 h6 h30
  have h14 : p14 := r30 h2 h6 f26
  have h3 : p3 := r10 h2 f4
  have h29 : p29 := r19 h3 h36
  have h20 : p20 := r28 h3 f26
  have h0 : p0 := r7 h20
  have h7 : p7 := r15 h2 h30
  have h23 : p23 := r8 h7 h14 h20
  have h21 : p21 := r0 h23 h29
  have h16 : p16 := r22 h6 h14 h21
  have h19 : p19 := r12 h16 f18 h36
  have h1 : p1 := r17 h0 h21 h23
  have h28 : p28 := r5 h1 h2
  have h17 : p17 := r2 h1 h30 h36
  have h22 : p22 := r13 h17 h19 h28
  exact h22
#print axioms cogModel_b7b1daa3bd001bd5a21b08a170da037a342e875e004d8c5dd13afb14cf04bf5d

theorem cogModel_a1bee6596fa865d06fa6cdff5a65e12c2a205dc5cb819aaa7cd0fab118b74ca3 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 p41 : Prop) (f3 : p3) (f5 : p5) (f12 : p12) (f20 : p20) (r0 : p19 → p4) (r1 : p12 → p18 → p40) (r2 : p2 → p12 → p1) (r3 : p3 → p5 → p12 → p18) (r4 : p20 → p30 → p38) (r5 : p4 → p39) (r6 : p3 → p25 → p6) (r7 : p5 → p34 → p35) (r8 : p21 → p28 → p40 → p2) (r9 : p3 → p12 → p7) (r10 : p1 → p12 → p23 → p25) (r11 : p18 → p25 → p16) (r12 : p28 → p21) (r13 : p0 → p1 → p10 → p41) (r14 : p5 → p17 → p21 → p11) (r15 : p20 → p19) (r16 : p24 → p35 → p8) (r17 : p2 → p32 → p40 → p27) (r18 : p12 → p40 → p31) (r19 : p13 → p20 → p36) (r20 : p5 → p27 → p0) (r21 : p2 → p9 → p21 → p17) (r22 : p11 → p20 → p23) (r23 : p21 → p41 → p6) (r24 : p3 → p25 → p16) (r25 : p6 → p17 → p40 → p24) (r26 : p11 → p12 → p10) (r27 : p3 → p9 → p40) (r28 : p3 → p21 → p31) (r29 : p1 → p31 → p0) (r30 : p4 → p14) (r31 : p3 → p18 → p40 → p32) (r32 : p3 → p22 → p29) (r33 : p0 → p20 → p40 → p33) (r34 : p20 → p32 → p17) (r35 : p12 → p21 → p32) (r36 : p20 → p28 → p21) (r37 : p20 → p32 → p37 → p10) (r38 : p11 → p16 → p35) (r39 : p20 → p26 → p15) (r40 : p5 → p28) (r41 : p3 → p23 → p25) (r42 : p9 → p31 → p32 → p1) (r43 : p12 → p37 → p33) (r44 : p21 → p27 → p37) (r45 : p2 → p20 → p27) (r46 : p31 → p40 → p41 → p34) (r47 : p5 → p20 → p9) (r48 : p0 → p27 → p37 → p23) (r49 : p6 → p12 → p24) : p8 := by
  have h18 : p18 := r3 f3 f5 f12
  have h40 : p40 := r1 f12 h18
  have h31 : p31 := r18 f12 h40
  have h28 : p28 := r40 f5
  have h21 : p21 := r36 f20 h28
  have h32 : p32 := r35 f12 h21
  have h17 : p17 := r34 f20 h32
  have h11 : p11 := r14 f5 h17 h21
  have h23 : p23 := r22 h11 f20
  have h25 : p25 := r41 f3 h23
  have h16 : p16 := r11 h18 h25
  have h10 : p10 := r26 h11 f12
  have h35 : p35 := r38 h11 h16
  have h6 : p6 := r6 f3 h25
  have h24 : p24 := r49 h6 f12
  have h8 : p8 := r16 h24 h35
  exact h8
#print axioms cogModel_a1bee6596fa865d06fa6cdff5a65e12c2a205dc5cb819aaa7cd0fab118b74ca3

theorem cogModel_d6b5a0da64103492184946e1883eb03dffefa0b9fc20be5197b1e8c42d54afb7 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 : Prop) (f11 : p11) (f17 : p17) (f20 : p20) (r0 : p22 → p3) (r1 : p17 → p23 → p25) (r2 : p8 → p11 → p13 → p2) (r3 : p10 → p8) (r4 : p10 → p20 → p13) (r5 : p3 → p24) (r6 : p11 → p17 → p20 → p15) (r7 : p1 → p17 → p6) (r8 : p11 → p20 → p21 → p9) (r9 : p7 → p22) (r10 : p20 → p16) (r11 : p11 → p15 → p17 → p10) (r12 : p24 → p0) (r13 : p5 → p7) (r14 : p0 → p18) (r15 : p11 → p15 → p21) (r16 : p20 → p5) (r17 : p17 → p19 → p4) (r18 : p14 → p17 → p12) : p18 := by
  have h5 : p5 := r16 f20
  have h7 : p7 := r13 h5
  have h22 : p22 := r9 h7
  have h3 : p3 := r0 h22
  have h24 : p24 := r5 h3
  have h0 : p0 := r12 h24
  have h18 : p18 := r14 h0
  exact h18
#print axioms cogModel_d6b5a0da64103492184946e1883eb03dffefa0b9fc20be5197b1e8c42d54afb7

theorem cogModel_21259e063287e973262f9be4ec08ab98973a69247e320d6ca2e2e8e2f7cee272 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 : Prop) (f14 : p14) (f15 : p15) (f16 : p16) (f34 : p34) (f39 : p39) (r0 : p9 → p17 → p7) (r1 : p36 → p28) (r2 : p14 → p3) (r3 : p14 → p16 → p38 → p17) (r4 : p16 → p26 → p34 → p12) (r5 : p24 → p34 → p1) (r6 : p7 → p15 → p11) (r7 : p17 → p26 → p34 → p9) (r8 : p16 → p18 → p5) (r9 : p3 → p27) (r10 : p13 → p26 → p10) (r11 : p9 → p4) (r12 : p19 → p39 → p32) (r13 : p3 → p21 → p34 → p20) (r14 : p16 → p18) (r15 : p1 → p4 → p13) (r16 : p24 → p40 → p33) (r17 : p14 → p15 → p38) (r18 : p5 → p18 → p25 → p2) (r19 : p17 → p26 → p39 → p37) (r20 : p12 → p8) (r21 : p15 → p25) (r22 : p8 → p17 → p40) (r23 : p25 → p29) (r24 : p4 → p37 → p24) (r25 : p18 → p21 → p30) (r26 : p10 → p35 → p23) (r27 : p3 → p15 → p39 → p36) (r28 : p7 → p12 → p33 → p31) (r29 : p18 → p39 → p6) (r30 : p13 → p26 → p40 → p35) (r31 : p34 → p39 → p21) (r32 : p0 → p39 → p22) (r33 : p34 → p39 → p26) : p23 := by
  have h26 : p26 := r33 f34 f39
  have h12 : p12 := r4 f16 h26 f34
  have h8 : p8 := r20 h12
  have h38 : p38 := r17 f14 f15
  have h17 : p17 := r3 f14 f16 h38
  have h40 : p40 := r22 h8 h17
  have h9 : p9 := r7 h17 h26 f34
  have h4 : p4 := r11 h9
  have h37 : p37 := r19 h17 h26 f39
  have h24 : p24 := r24 h4 h37
  have h1 : p1 := r5 h24 f34
  have h13 : p13 := r15 h1 h4
  have h10 : p10 := r10 h13 h26
  have h35 : p35 := r30 h13 h26 h40
  have h23 : p23 := r26 h10 h35
  exact h23
#print axioms cogModel_21259e063287e973262f9be4ec08ab98973a69247e320d6ca2e2e8e2f7cee272

theorem cogModel_66a193c8d55899c2fd89e83ec0850bc945d403b3b24a2ec7f47e522a8729492f (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 : Prop) (f8 : p8) (f22 : p22) (f23 : p23) (f31 : p31) (f35 : p35) (r0 : p10 → p28 → p31 → p24) (r1 : p22 → p31 → p10) (r2 : p8 → p35 → p13) (r3 : p18 → p34 → p33) (r4 : p24 → p35 → p1) (r5 : p1 → p8 → p36) (r6 : p6 → p16 → p19 → p7) (r7 : p8 → p18 → p33) (r8 : p31 → p3) (r9 : p5 → p35 → p19) (r10 : p31 → p35 → p10) (r11 : p2 → p26 → p18) (r12 : p23 → p28) (r13 : p4 → p35 → p20) (r14 : p28 → p35 → p15) (r15 : p5 → p36 → p6) (r16 : p5 → p31 → p19) (r17 : p9 → p22 → p0) (r18 : p3 → p8 → p22 → p21) (r19 : p35 → p37) (r20 : p23 → p31 → p13) (r21 : p22 → p26 → p34) (r22 : p14 → p22 → p2) (r23 : p15 → p24 → p2) (r24 : p17 → p22 → p28 → p16) (r25 : p8 → p27 → p29) (r26 : p8 → p23 → p31 → p28) (r27 : p22 → p23 → p30) (r28 : p8 → p18 → p24 → p17) (r29 : p25 → p30 → p12) (r30 : p8 → p30 → p31 → p25) (r31 : p2 → p26 → p34) (r32 : p13 → p28 → p35 → p15) (r33 : p14 → p34 → p5) (r34 : p14 → p22 → p28 → p26) (r35 : p18 → p35 → p5) (r36 : p8 → p24 → p1) (r37 : p11 → p31 → p32) (r38 : p10 → p31 → p14) : p7 := by
  have h28 : p28 := r12 f23
  have h10 : p10 := r1 f22 f31
  have h14 : p14 := r38 h10 f31
  have h24 : p24 := r0 h10 h28 f31
  have h1 : p1 := r4 h24 f35
  have h36 : p36 := r5 h1 f8
  have h15 : p15 := r14 h28 f35
  have h2 : p2 := r23 h15 h24
  have h26 : p26 := r34 h14 f22 h28
  have h34 : p34 := r31 h2 h26
  have h18 : p18 := r11 h2 h26
  have h17 : p17 := r28 f8 h18 h24
  have h16 : p16 := r24 h17 f22 h28
  have h5 : p5 := r33 h14 h34
  have h6 : p6 := r15 h5 h36
  have h19 : p19 := r9 h5 f35
  have h7 : p7 := r6 h6 h16 h19
  exact h7
#print axioms cogModel_66a193c8d55899c2fd89e83ec0850bc945d403b3b24a2ec7f47e522a8729492f

theorem cogModel_2fd6156211b98acca9c233eb7a3d490bad85da457e624ec3bf3e787dc1980e85 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 : Prop) (f0 : p0) (f1 : p1) (f4 : p4) (f15 : p15) (f21 : p21) (r0 : p19 → p21 → p14) (r1 : p1 → p9 → p12) (r2 : p17 → p13) (r3 : p16 → p7) (r4 : p4 → p15 → p21 → p19) (r5 : p15 → p19 → p9) (r6 : p3 → p22) (r7 : p12 → p15 → p11) (r8 : p7 → p20) (r9 : p1 → p16) (r10 : p2 → p17) (r11 : p1 → p10 → p6) (r12 : p0 → p4 → p18) (r13 : p20 → p3) (r14 : p22 → p2) (r15 : p8 → p21 → p5) : p13 := by
  have h16 : p16 := r9 f1
  have h7 : p7 := r3 h16
  have h20 : p20 := r8 h7
  have h3 : p3 := r13 h20
  have h22 : p22 := r6 h3
  have h2 : p2 := r14 h22
  have h17 : p17 := r10 h2
  have h13 : p13 := r2 h17
  exact h13
#print axioms cogModel_2fd6156211b98acca9c233eb7a3d490bad85da457e624ec3bf3e787dc1980e85

theorem cogModel_9f11d96629fbec7a7cb1ba8649a63e15e2a9847ed2067d2f0d5e33357bf31d62 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 : Prop) (f0 : p0) (f3 : p3) (f21 : p21) (f23 : p23) (f27 : p27) (r0 : p13 → p16 → p26 → p18) (r1 : p9 → p16 → p29 → p24) (r2 : p6 → p18 → p10) (r3 : p0 → p31 → p10) (r4 : p3 → p20) (r5 : p3 → p27 → p16) (r6 : p3 → p33 → p1) (r7 : p16 → p9) (r8 : p0 → p20 → p21 → p14) (r9 : p16 → p27 → p35) (r10 : p3 → p16 → p32 → p29) (r11 : p21 → p23 → p30 → p5) (r12 : p3 → p21 → p15) (r13 : p24 → p29 → p36) (r14 : p3 → p21 → p23 → p13) (r15 : p23 → p27 → p30) (r16 : p13 → p36 → p31) (r17 : p5 → p27 → p35 → p32) (r18 : p23 → p31 → p7) (r19 : p10 → p16 → p23 → p8) (r20 : p18 → p23 → p6) (r21 : p21 → p11) (r22 : p29 → p26) (r23 : p22 → p27 → p8) (r24 : p0 → p12 → p2) (r25 : p5 → p35 → p34) (r26 : p10 → p27 → p17) (r27 : p16 → p35) (r28 : p5 → p31 → p7) (r29 : p0 → p29 → p26) (r30 : p26 → p27 → p36) (r31 : p18 → p36 → p6) (r32 : p3 → p5 → p32) (r33 : p3 → p34 → p29) (r34 : p16 → p29 → p28) (r35 : p21 → p34 → p4) (r36 : p10 → p13 → p19) (r37 : p6 → p23 → p22) (r38 : p7 → p9 → p28 → p17) (r39 : p27 → p34 → p4) (r40 : p0 → p27 → p30) (r41 : p21 → p23 → p16) (r42 : p8 → p17 → p19 → p37) (r43 : p21 → p23 → p27 → p25) : p37 := by
  have h13 : p13 := r14 f3 f21 f23
  have h16 : p16 := r41 f21 f23
  have h9 : p9 := r7 h16
  have h30 : p30 := r15 f23 f27
  have h5 : p5 := r11 f21 f23 h30
  have h32 : p32 := r32 f3 h5
  have h29 : p29 := r10 f3 h16 h32
  have h26 : p26 := r29 f0 h29
  have h36 : p36 := r30 h26 f27
  have h31 : p31 := r16 h13 h36
  have h18 : p18 := r0 h13 h16 h26
  have h6 : p6 := r31 h18 h36
  have h28 : p28 := r34 h16 h29
  have h22 : p22 := r37 h6 f23
  have h8 : p8 := r23 h22 f27
  have h7 : p7 := r28 h5 h31
  have h17 : p17 := r38 h7 h9 h28
  have h10 : p10 := r2 h6 h18
  have h19 : p19 := r36 h10 h13
  have h37 : p37 := r42 h8 h17 h19
  exact h37
#print axioms cogModel_9f11d96629fbec7a7cb1ba8649a63e15e2a9847ed2067d2f0d5e33357bf31d62

theorem cogModel_0a45458abe3013d26a5b23dc9741bc229ed802d4f6303a82d9a46f2f2609143b (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 : Prop) (f3 : p3) (f6 : p6) (f31 : p31) (r0 : p23 → p31 → p13) (r1 : p6 → p5) (r2 : p6 → p26 → p1) (r3 : p3 → p24 → p29) (r4 : p1 → p31 → p20) (r5 : p6 → p21 → p2) (r6 : p6 → p31 → p12) (r7 : p12 → p25 → p7) (r8 : p4 → p33 → p0) (r9 : p3 → p18 → p33 → p21) (r10 : p6 → p36 → p11) (r11 : p4 → p18 → p26) (r12 : p27 → p31 → p24) (r13 : p34 → p38 → p35) (r14 : p2 → p6 → p4) (r15 : p3 → p31 → p33) (r16 : p2 → p31 → p7) (r17 : p21 → p32 → p2) (r18 : p3 → p14 → p27 → p37) (r19 : p6 → p28 → p17) (r20 : p0 → p24 → p29) (r21 : p6 → p7 → p0) (r22 : p6 → p33 → p32) (r23 : p1 → p3 → p20) (r24 : p3 → p20 → p14) (r25 : p15 → p29 → p37 → p10) (r26 : p3 → p31 → p12) (r27 : p14 → p21 → p31 → p15) (r28 : p31 → p33) (r29 : p1 → p11 → p33 → p14) (r30 : p31 → p18) (r31 : p3 → p34 → p8) (r32 : p0 → p6 → p31 → p1) (r33 : p21 → p25 → p36 → p27) (r34 : p18 → p31 → p32) (r35 : p12 → p21 → p26 → p36) (r36 : p6 → p34) (r37 : p34 → p30) (r38 : p6 → p9 → p16) (r39 : p7 → p31 → p26) (r40 : p1 → p31 → p27) (r41 : p14 → p31 → p37) (r42 : p7 → p11 → p24) (r43 : p6 → p31 → p38) (r44 : p18 → p32 → p25) (r45 : p3 → p22 → p19) : p10 := by
  have h33 : p33 := r15 f3 f31
  have h32 : p32 := r22 f6 h33
  have h12 : p12 := r6 f6 f31
  have h18 : p18 := r30 f31
  have h25 : p25 := r44 h18 h32
  have h7 : p7 := r7 h12 h25
  have h21 : p21 := r9 f3 h18 h33
  have h0 : p0 := r21 f6 h7
  have h26 : p26 := r39 h7 f31
  have h36 : p36 := r35 h12 h21 h26
  have h11 : p11 := r10 f6 h36
  have h1 : p1 := r32 h0 f6 f31
  have h20 : p20 := r4 h1 f31
  have h27 : p27 := r33 h21 h25 h36
  have h24 : p24 := r42 h7 h11
  have h29 : p29 := r20 h0 h24
  have h14 : p14 := r29 h1 h11 h33
  have h37 : p37 := r41 h14 f31
  have h15 : p15 := r27 h14 h21 f31
  have h10 : p10 := r25 h15 h29 h37
  exact h10
#print axioms cogModel_0a45458abe3013d26a5b23dc9741bc229ed802d4f6303a82d9a46f2f2609143b

theorem cogModel_c3416faf55e0f4884be91906a8659b1be20c4dfb0718d52f40b9afff891d2ad3 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 : Prop) (f5 : p5) (f9 : p9) (f25 : p25) (r0 : p30 → p32 → p34 → p7) (r1 : p0 → p26 → p24) (r2 : p24 → p30 → p19) (r3 : p9 → p20 → p25 → p32) (r4 : p9 → p15 → p11) (r5 : p16 → p19 → p33 → p1) (r6 : p7 → p24 → p26 → p16) (r7 : p6 → p31 → p32 → p29) (r8 : p22 → p25 → p21) (r9 : p3 → p30 → p31 → p14) (r10 : p6 → p14 → p30 → p0) (r11 : p5 → p9 → p20) (r12 : p5 → p21 → p28) (r13 : p13 → p27 → p17) (r14 : p6 → p30 → p34 → p31) (r15 : p14 → p25 → p34 → p26) (r16 : p18 → p29 → p34 → p35) (r17 : p8 → p14 → p18) (r18 : p2 → p35 → p33) (r19 : p25 → p30) (r20 : p25 → p29 → p30 → p2) (r21 : p7 → p32 → p3) (r22 : p22 → p25 → p27 → p10) (r23 : p25 → p27) (r24 : p25 → p34) (r25 : p5 → p10 → p28 → p13) (r26 : p5 → p22) (r27 : p4 → p9 → p12) (r28 : p6 → p9 → p20 → p8) (r29 : p22 → p28 → p23) (r30 : p20 → p25 → p6) : p1 := by
  have h30 : p30 := r19 f25
  have h34 : p34 := r24 f25
  have h20 : p20 := r11 f5 f9
  have h6 : p6 := r30 h20 f25
  have h31 : p31 := r14 h6 h30 h34
  have h32 : p32 := r3 f9 h20 f25
  have h29 : p29 := r7 h6 h31 h32
  have h7 : p7 := r0 h30 h32 h34
  have h2 : p2 := r20 f25 h29 h30
  have h3 : p3 := r21 h7 h32
  have h14 : p14 := r9 h3 h30 h31
  have h0 : p0 := r10 h6 h14 h30
  have h26 : p26 := r15 h14 f25 h34
  have h8 : p8 := r28 h6 f9 h20
  have h18 : p18 := r17 h8 h14
  have h35 : p35 := r16 h18 h29 h34
  have h33 : p33 := r18 h2 h35
  have h24 : p24 := r1 h0 h26
  have h19 : p19 := r2 h24 h30
  have h16 : p16 := r6 h7 h24 h26
  have h1 : p1 := r5 h16 h19 h33
  exact h1
#print axioms cogModel_c3416faf55e0f4884be91906a8659b1be20c4dfb0718d52f40b9afff891d2ad3

theorem cogModel_fb951bba6485e802998463961d9dae50f19ce2dda2d48adc84889d477824243d (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 p41 p42 : Prop) (f8 : p8) (f13 : p13) (f16 : p16) (f19 : p19) (f36 : p36) (r0 : p0 → p12 → p41) (r1 : p10 → p39 → p17) (r2 : p19 → p23 → p27) (r3 : p6 → p30) (r4 : p19 → p2) (r5 : p3 → p23 → p29) (r6 : p14 → p19 → p26) (r7 : p4 → p15 → p32) (r8 : p12 → p13 → p27 → p5) (r9 : p6 → p24) (r10 : p13 → p36 → p40 → p3) (r11 : p16 → p6) (r12 : p3 → p5 → p40 → p18) (r13 : p11 → p13 → p0) (r14 : p19 → p35) (r15 : p1 → p19 → p37) (r16 : p5 → p19 → p15) (r17 : p0 → p9 → p39 → p34) (r18 : p16 → p33 → p20) (r19 : p8 → p13 → p19 → p10) (r20 : p24 → p36 → p21) (r21 : p15 → p27 → p31) (r22 : p9 → p23 → p12) (r23 : p25 → p31 → p32 → p42) (r24 : p0 → p5 → p4) (r25 : p16 → p7) (r26 : p9 → p13 → p23 → p38) (r27 : p13 → p23 → p40 → p39) (r28 : p0 → p18 → p40 → p25) (r29 : p8 → p11 → p9) (r30 : p8 → p19 → p36 → p23) (r31 : p36 → p28) (r32 : p19 → p22) (r33 : p3 → p23 → p39 → p11) (r34 : p8 → p13 → p16 → p40) : p42 := by
  have h40 : p40 := r34 f8 f13 f16
  have h3 : p3 := r10 f13 f36 h40
  have h23 : p23 := r30 f8 f19 f36
  have h27 : p27 := r2 f19 h23
  have h39 : p39 := r27 f13 h23 h40
  have h11 : p11 := r33 h3 h23 h39
  have h0 : p0 := r13 h11 f13
  have h9 : p9 := r29 f8 h11
  have h12 : p12 := r22 h9 h23
  have h5 : p5 := r8 h12 f13 h27
  have h4 : p4 := r24 h0 h5
  have h18 : p18 := r12 h3 h5 h40
  have h25 : p25 := r28 h0 h18 h40
  have h15 : p15 := r16 h5 f19
  have h32 : p32 := r7 h4 h15
  have h31 : p31 := r21 h15 h27
  have h42 : p42 := r23 h25 h31 h32
  exact h42
#print axioms cogModel_fb951bba6485e802998463961d9dae50f19ce2dda2d48adc84889d477824243d

theorem cogModel_a7d53f3e1c640fb1dc1616a755c665fdf01fe7ce8e8058d32f0e0ac9f73a9c8a (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 p41 p42 : Prop) (f6 : p6) (f10 : p10) (f30 : p30) (r0 : p17 → p37 → p20) (r1 : p4 → p30 → p37) (r2 : p2 → p30 → p5) (r3 : p1 → p23) (r4 : p6 → p10 → p38 → p42) (r5 : p37 → p42 → p17) (r6 : p4 → p10 → p35) (r7 : p6 → p25 → p29) (r8 : p13 → p40 → p42 → p34) (r9 : p37 → p38 → p9) (r10 : p9 → p10 → p13) (r11 : p6 → p10 → p38) (r12 : p13 → p37 → p14) (r13 : p6 → p0) (r14 : p26 → p38 → p11) (r15 : p13 → p30 → p39) (r16 : p13 → p38 → p39 → p2) (r17 : p10 → p30 → p16) (r18 : p31 → p34 → p19) (r19 : p6 → p30 → p4) (r20 : p6 → p10 → p20 → p36) (r21 : p0 → p7) (r22 : p5 → p13 → p12) (r23 : p18 → p30 → p32) (r24 : p6 → p10 → p21) (r25 : p17 → p37 → p39 → p28) (r26 : p0 → p16 → p30 → p22) (r27 : p2 → p36 → p27) (r28 : p5 → p26 → p36 → p40) (r29 : p33 → p37 → p26) (r30 : p16 → p1) (r31 : p14 → p38 → p39 → p33) (r32 : p15 → p30 → p3) (r33 : p10 → p30 → p41) (r34 : p10 → p40 → p31) (r35 : p8 → p30 → p24) : p19 := by
  have h4 : p4 := r19 f6 f30
  have h37 : p37 := r1 h4 f30
  have h38 : p38 := r11 f6 f10
  have h42 : p42 := r4 f6 f10 h38
  have h9 : p9 := r9 h37 h38
  have h13 : p13 := r10 h9 f10
  have h14 : p14 := r12 h13 h37
  have h39 : p39 := r15 h13 f30
  have h33 : p33 := r31 h14 h38 h39
  have h26 : p26 := r29 h33 h37
  have h2 : p2 := r16 h13 h38 h39
  have h5 : p5 := r2 h2 f30
  have h17 : p17 := r5 h37 h42
  have h20 : p20 := r0 h17 h37
  have h36 : p36 := r20 f6 f10 h20
  have h40 : p40 := r28 h5 h26 h36
  have h31 : p31 := r34 f10 h40
  have h34 : p34 := r8 h13 h40 h42
  have h19 : p19 := r18 h31 h34
  exact h19
#print axioms cogModel_a7d53f3e1c640fb1dc1616a755c665fdf01fe7ce8e8058d32f0e0ac9f73a9c8a

theorem cogModel_8322fc602db360ad90ff6b6e530af4d616a07d23dfeaf4adc1b7787b7fe793a9 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 p41 p42 p43 p44 p45 p46 p47 : Prop) (f14 : p14) (f18 : p18) (f43 : p43) (r0 : p5 → p31 → p37) (r1 : p28 → p43 → p15) (r2 : p43 → p19) (r3 : p19 → p43 → p45 → p12) (r4 : p19 → p43 → p45) (r5 : p17 → p43 → p9) (r6 : p7 → p40 → p25) (r7 : p29 → p32 → p47) (r8 : p20 → p32 → p35) (r9 : p14 → p19 → p43 → p42) (r10 : p18 → p8) (r11 : p3 → p14 → p0) (r12 : p18 → p19 → p26 → p17) (r13 : p44 → p40) (r14 : p14 → p43 → p32) (r15 : p8 → p14 → p1) (r16 : p11 → p12 → p36) (r17 : p18 → p43 → p45 → p6) (r18 : p32 → p39 → p13) (r19 : p9 → p11 → p45 → p30) (r20 : p14 → p24 → p10) (r21 : p2 → p18 → p4) (r22 : p1 → p20 → p32 → p2) (r23 : p1 → p35 → p24) (r24 : p26 → p21) (r25 : p14 → p34 → p27) (r26 : p1 → p43 → p5) (r27 : p14 → p41) (r28 : p17 → p19 → p42 → p46) (r29 : p2 → p37 → p44) (r30 : p29 → p35 → p39) (r31 : p38 → p43 → p23) (r32 : p11 → p43 → p46 → p33) (r33 : p4 → p5 → p8 → p31) (r34 : p9 → p22 → p16) (r35 : p4 → p5 → p32 → p29) (r36 : p18 → p43 → p20) (r37 : p18 → p26) (r38 : p17 → p26 → p11) (r39 : p5 → p13 → p47 → p7) (r40 : p14 → p18 → p36 → p22) : p25 := by
  have h32 : p32 := r14 f14 f43
  have h20 : p20 := r36 f18 f43
  have h35 : p35 := r8 h20 h32
  have h8 : p8 := r10 f18
  have h1 : p1 := r15 h8 f14
  have h5 : p5 := r26 h1 f43
  have h2 : p2 := r22 h1 h20 h32
  have h4 : p4 := r21 h2 f18
  have h29 : p29 := r35 h4 h5 h32
  have h39 : p39 := r30 h29 h35
  have h31 : p31 := r33 h4 h5 h8
  have h37 : p37 := r0 h5 h31
  have h44 : p44 := r29 h2 h37
  have h13 : p13 := r18 h32 h39
  have h40 : p40 := r13 h44
  have h47 : p47 := r7 h29 h32
  have h7 : p7 := r39 h5 h13 h47
  have h25 : p25 := r6 h7 h40
  exact h25
#print axioms cogModel_8322fc602db360ad90ff6b6e530af4d616a07d23dfeaf4adc1b7787b7fe793a9

theorem cogModel_41583a4984845b528018a332add9fe3ff664be3c7dff541d22227debacc2fab9 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 : Prop) (f2 : p2) (f9 : p9) (f15 : p15) (f26 : p26) (r0 : p2 → p9 → p26 → p16) (r1 : p26 → p29 → p31) (r2 : p1 → p26 → p10) (r3 : p2 → p15 → p32) (r4 : p2 → p9 → p26 → p8) (r5 : p11 → p15 → p35) (r6 : p1 → p8 → p5) (r7 : p8 → p25 → p38) (r8 : p21 → p26 → p6) (r9 : p1 → p8 → p33 → p3) (r10 : p34 → p36 → p33) (r11 : p15 → p13) (r12 : p7 → p24 → p11) (r13 : p2 → p20 → p38 → p36) (r14 : p13 → p15 → p19 → p0) (r15 : p14 → p28 → p37 → p30) (r16 : p2 → p9 → p25) (r17 : p2 → p26 → p29) (r18 : p9 → p24) (r19 : p2 → p8 → p9 → p20) (r20 : p0 → p13 → p19 → p22) (r21 : p9 → p16 → p26 → p4) (r22 : p8 → p17 → p25 → p14) (r23 : p9 → p17 → p18 → p28) (r24 : p12 → p18 → p17) (r25 : p20 → p35 → p18) (r26 : p2 → p9 → p10 → p34) (r27 : p2 → p24 → p38 → p1) (r28 : p11 → p34 → p12) (r29 : p23 → p26 → p27) (r30 : p2 → p26 → p38 → p7) (r31 : p17 → p35 → p37) (r32 : p15 → p16 → p26 → p19) : p30 := by
  have h25 : p25 := r16 f2 f9
  have h8 : p8 := r4 f2 f9 f26
  have h20 : p20 := r19 f2 h8 f9
  have h24 : p24 := r18 f9
  have h38 : p38 := r7 h8 h25
  have h7 : p7 := r30 f2 f26 h38
  have h11 : p11 := r12 h7 h24
  have h35 : p35 := r5 h11 f15
  have h18 : p18 := r25 h20 h35
  have h1 : p1 := r27 f2 h24 h38
  have h10 : p10 := r2 h1 f26
  have h34 : p34 := r26 f2 f9 h10
  have h12 : p12 := r28 h11 h34
  have h17 : p17 := r24 h12 h18
  have h37 : p37 := r31 h17 h35
  have h14 : p14 := r22 h8 h17 h25
  have h28 : p28 := r23 f9 h17 h18
  have h30 : p30 := r15 h14 h28 h37
  exact h30
#print axioms cogModel_41583a4984845b528018a332add9fe3ff664be3c7dff541d22227debacc2fab9

theorem cogModel_a58686eb468f5bb0172a26748c0aa591fc29975fb0e9315b6c1b777c56e1af41 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 : Prop) (f4 : p4) (f11 : p11) (f12 : p12) (f20 : p20) (r0 : p6 → p10 → p16 → p22) (r1 : p2 → p12 → p33) (r2 : p20 → p31 → p17) (r3 : p11 → p30 → p23) (r4 : p4 → p12 → p20 → p27) (r5 : p11 → p14 → p21) (r6 : p10 → p12 → p31 → p26) (r7 : p11 → p13 → p9) (r8 : p2 → p3 → p16 → p6) (r9 : p4 → p12 → p14) (r10 : p11 → p20 → p25 → p16) (r11 : p5 → p31 → p24) (r12 : p3 → p20 → p10) (r13 : p0 → p30 → p2) (r14 : p0 → p25 → p3) (r15 : p11 → p25 → p0) (r16 : p25 → p30 → p33 → p31) (r17 : p24 → p28 → p32) (r18 : p11 → p20 → p29) (r19 : p12 → p21 → p1) (r20 : p0 → p11 → p26 → p28) (r21 : p6 → p10 → p20 → p8) (r22 : p11 → p20 → p7) (r23 : p0 → p20 → p18) (r24 : p4 → p11 → p30) (r25 : p11 → p30 → p25) (r26 : p15 → p20 → p19) (r27 : p4 → p18 → p22 → p5) : p32 := by
  have h30 : p30 := r24 f4 f11
  have h25 : p25 := r25 f11 h30
  have h0 : p0 := r15 f11 h25
  have h18 : p18 := r23 h0 f20
  have h2 : p2 := r13 h0 h30
  have h33 : p33 := r1 h2 f12
  have h31 : p31 := r16 h25 h30 h33
  have h16 : p16 := r10 f11 f20 h25
  have h3 : p3 := r14 h0 h25
  have h10 : p10 := r12 h3 f20
  have h26 : p26 := r6 h10 f12 h31
  have h28 : p28 := r20 h0 f11 h26
  have h6 : p6 := r8 h2 h3 h16
  have h22 : p22 := r0 h6 h10 h16
  have h5 : p5 := r27 f4 h18 h22
  have h24 : p24 := r11 h5 h31
  have h32 : p32 := r17 h24 h28
  exact h32
#print axioms cogModel_a58686eb468f5bb0172a26748c0aa591fc29975fb0e9315b6c1b777c56e1af41

theorem cogModel_426e14ff50ce9ef1aff33dac19602781c2e44141304d78e90542bce8ce6a858b (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 : Prop) (f8 : p8) (f18 : p18) (f20 : p20) (f21 : p21) (r0 : p11 → p15) (r1 : p8 → p18 → p21 → p16) (r2 : p21 → p11) (r3 : p9 → p13) (r4 : p8 → p16 → p21 → p6) (r5 : p2 → p19) (r6 : p13 → p4) (r7 : p4 → p3) (r8 : p18 → p20 → p21 → p2) (r9 : p0 → p22) (r10 : p15 → p0) (r11 : p16 → p21 → p10) (r12 : p22 → p9) (r13 : p17 → p18 → p12) (r14 : p7 → p8 → p1) (r15 : p5 → p20 → p14) : p3 := by
  have h11 : p11 := r2 f21
  have h15 : p15 := r0 h11
  have h0 : p0 := r10 h15
  have h22 : p22 := r9 h0
  have h9 : p9 := r12 h22
  have h13 : p13 := r3 h9
  have h4 : p4 := r6 h13
  have h3 : p3 := r7 h4
  exact h3
#print axioms cogModel_426e14ff50ce9ef1aff33dac19602781c2e44141304d78e90542bce8ce6a858b

theorem cogModel_3a9b69b33b6bea46f559bd14d6b4c14a4c6ae4c438d772248548c7afc40f4b36 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 : Prop) (f2 : p2) (f3 : p3) (f20 : p20) (r0 : p5 → p9) (r1 : p9 → p13) (r2 : p16 → p6) (r3 : p0 → p20 → p19) (r4 : p6 → p12) (r5 : p12 → p5) (r6 : p15 → p20 → p10) (r7 : p4 → p7) (r8 : p14 → p18) (r9 : p2 → p3 → p20 → p1) (r10 : p13 → p14) (r11 : p2 → p21) (r12 : p7 → p16) (r13 : p1 → p3 → p20 → p17) (r14 : p3 → p17 → p8) (r15 : p3 → p4) (r16 : p3 → p8 → p17 → p11) : p18 := by
  have h4 : p4 := r15 f3
  have h7 : p7 := r7 h4
  have h16 : p16 := r12 h7
  have h6 : p6 := r2 h16
  have h12 : p12 := r4 h6
  have h5 : p5 := r5 h12
  have h9 : p9 := r0 h5
  have h13 : p13 := r1 h9
  have h14 : p14 := r10 h13
  have h18 : p18 := r8 h14
  exact h18
#print axioms cogModel_3a9b69b33b6bea46f559bd14d6b4c14a4c6ae4c438d772248548c7afc40f4b36

theorem cogModel_ddc65443e7442b34a89ac68efa545ea16b6983c4bb6e9421e04a9e57c71aec7c (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 : Prop) (f5 : p5) (f6 : p6) (f8 : p8) (f9 : p9) (f17 : p17) (r0 : p8 → p12) (r1 : p2 → p20) (r2 : p13 → p28) (r3 : p9 → p16 → p26) (r4 : p7 → p21) (r5 : p9 → p14 → p27) (r6 : p5 → p7) (r7 : p23 → p10) (r8 : p16 → p19) (r9 : p8 → p25) (r10 : p5 → p6 → p17 → p2) (r11 : p22 → p13) (r12 : p8 → p11 → p0) (r13 : p16 → p18 → p19 → p15) (r14 : p17 → p16) (r15 : p3 → p23) (r16 : p5 → p24 → p4) (r17 : p28 → p3) (r18 : p1 → p22) (r19 : p21 → p1) (r20 : p5 → p20 → p18) : p10 := by
  have h7 : p7 := r6 f5
  have h21 : p21 := r4 h7
  have h1 : p1 := r19 h21
  have h22 : p22 := r18 h1
  have h13 : p13 := r11 h22
  have h28 : p28 := r2 h13
  have h3 : p3 := r17 h28
  have h23 : p23 := r15 h3
  have h10 : p10 := r7 h23
  exact h10
#print axioms cogModel_ddc65443e7442b34a89ac68efa545ea16b6983c4bb6e9421e04a9e57c71aec7c

theorem cogModel_fedfbadf56bf64bd3ef4190d460b2aabd9532cd8a6f1f3b9bb6de23f0c0f2900 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 : Prop) (f0 : p0) (f10 : p10) (f25 : p25) (f28 : p28) (f34 : p34) (r0 : p0 → p25 → p34 → p22) (r1 : p0 → p9 → p23) (r2 : p2 → p36) (r3 : p16 → p25 → p27 → p31) (r4 : p10 → p12) (r5 : p17 → p28 → p8) (r6 : p22 → p13) (r7 : p16 → p34 → p19) (r8 : p7 → p28 → p35) (r9 : p0 → p10 → p34 → p16) (r10 : p1 → p8 → p33 → p15) (r11 : p2 → p3 → p12 → p20) (r12 : p0 → p12 → p3) (r13 : p28 → p29) (r14 : p25 → p34 → p4) (r15 : p34 → p2) (r16 : p16 → p17 → p1) (r17 : p5 → p21 → p31 → p37) (r18 : p19 → p27 → p31 → p21) (r19 : p5 → p10 → p11 → p17) (r20 : p12 → p28 → p29 → p9) (r21 : p0 → p30) (r22 : p19 → p28 → p31 → p5) (r23 : p11 → p28 → p37 → p26) (r24 : p5 → p21 → p28 → p11) (r25 : p4 → p13 → p28 → p32) (r26 : p11 → p17 → p33) (r27 : p0 → p28 → p34 → p27) (r28 : p14 → p28 → p6) (r29 : p25 → p24) (r30 : p2 → p10 → p34 → p18) : p15 := by
  have h16 : p16 := r9 f0 f10 f34
  have h19 : p19 := r7 h16 f34
  have h27 : p27 := r27 f0 f28 f34
  have h31 : p31 := r3 h16 f25 h27
  have h5 : p5 := r22 h19 f28 h31
  have h21 : p21 := r18 h19 h27 h31
  have h11 : p11 := r24 h5 h21 f28
  have h17 : p17 := r19 h5 f10 h11
  have h33 : p33 := r26 h11 h17
  have h1 : p1 := r16 h16 h17
  have h8 : p8 := r5 h17 f28
  have h15 : p15 := r10 h1 h8 h33
  exact h15
#print axioms cogModel_fedfbadf56bf64bd3ef4190d460b2aabd9532cd8a6f1f3b9bb6de23f0c0f2900

theorem cogModel_57d85f03cfe6eec670c675b8c2e3bae7ab20d2eb019c8c5259b34a5aac18c087 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 : Prop) (f12 : p12) (f14 : p14) (f22 : p22) (f30 : p30) (r0 : p14 → p22 → p30 → p3) (r1 : p1 → p30 → p26) (r2 : p13 → p25 → p23) (r3 : p5 → p23 → p25 → p15) (r4 : p1 → p30 → p29) (r5 : p12 → p18 → p25 → p10) (r6 : p14 → p4) (r7 : p12 → p22 → p28 → p16) (r8 : p22 → p31 → p21) (r9 : p14 → p27 → p0) (r10 : p12 → p29 → p8) (r11 : p3 → p14 → p22 → p27) (r12 : p12 → p26 → p18) (r13 : p12 → p22 → p25) (r14 : p8 → p14 → p10) (r15 : p12 → p35 → p33) (r16 : p3 → p12 → p30 → p13) (r17 : p3 → p22 → p23 → p9) (r18 : p2 → p10 → p11) (r19 : p3 → p12 → p27) (r20 : p15 → p27 → p26) (r21 : p0 → p8 → p12 → p2) (r22 : p8 → p14 → p2) (r23 : p1 → p15 → p29) (r24 : p12 → p34 → p32) (r25 : p14 → p33 → p1) (r26 : p14 → p28 → p34) (r27 : p0 → p12 → p7) (r28 : p7 → p30 → p5) (r29 : p7 → p23 → p5) (r30 : p6 → p12 → p24) (r31 : p12 → p17 → p19) (r32 : p22 → p30 → p6) (r33 : p0 → p22 → p30 → p7) (r34 : p9 → p13 → p33 → p20) (r35 : p22 → p25) (r36 : p22 → p23 → p35) (r37 : p29 → p30 → p8) (r38 : p14 → p22 → p28) : p11 := by
  have h25 : p25 := r13 f12 f22
  have h3 : p3 := r0 f14 f22 f30
  have h27 : p27 := r19 h3 f12
  have h0 : p0 := r9 f14 h27
  have h7 : p7 := r27 h0 f12
  have h5 : p5 := r28 h7 f30
  have h13 : p13 := r16 h3 f12 f30
  have h23 : p23 := r2 h13 h25
  have h15 : p15 := r3 h5 h23 h25
  have h26 : p26 := r20 h15 h27
  have h18 : p18 := r12 f12 h26
  have h10 : p10 := r5 f12 h18 h25
  have h35 : p35 := r36 f22 h23
  have h33 : p33 := r15 f12 h35
  have h1 : p1 := r25 f14 h33
  have h29 : p29 := r23 h1 h15
  have h8 : p8 := r10 f12 h29
  have h2 : p2 := r22 h8 f14
  have h11 : p11 := r18 h2 h10
  exact h11
#print axioms cogModel_57d85f03cfe6eec670c675b8c2e3bae7ab20d2eb019c8c5259b34a5aac18c087

theorem cogModel_074a2460eae073aec15d5e012dc9fac5d955f74436f5d1c5f5cccdbde178d0df (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 : Prop) (f3 : p3) (f5 : p5) (f22 : p22) (r0 : p12 → p21 → p25 → p4) (r1 : p1 → p32 → p14) (r2 : p0 → p8 → p9) (r3 : p3 → p21 → p0) (r4 : p2 → p5 → p10) (r5 : p9 → p11 → p6) (r6 : p5 → p18 → p22 → p35) (r7 : p7 → p18 → p30 → p25) (r8 : p36 → p27) (r9 : p3 → p24 → p30 → p21) (r10 : p2 → p3 → p26) (r11 : p20 → p22 → p16) (r12 : p5 → p20 → p38) (r13 : p2 → p5 → p23) (r14 : p8 → p18 → p35 → p7) (r15 : p1 → p3 → p8) (r16 : p5 → p18 → p12) (r17 : p9 → p21 → p15) (r18 : p5 → p22 → p18) (r19 : p5 → p17 → p31) (r20 : p12 → p22 → p30) (r21 : p2 → p5 → p13) (r22 : p5 → p22 → p20) (r23 : p5 → p22 → p1) (r24 : p6 → p15 → p19 → p34) (r25 : p5 → p28) (r26 : p10 → p36) (r27 : p3 → p25 → p32) (r28 : p3 → p12 → p35 → p24) (r29 : p3 → p5 → p22 → p29) (r30 : p22 → p33 → p37) (r31 : p3 → p4 → p7 → p11) (r32 : p5 → p8 → p14 → p19) (r33 : p3 → p2) : p34 := by
  have h1 : p1 := r23 f5 f22
  have h8 : p8 := r15 h1 f3
  have h18 : p18 := r18 f5 f22
  have h12 : p12 := r16 f5 h18
  have h30 : p30 := r20 h12 f22
  have h35 : p35 := r6 f5 h18 f22
  have h7 : p7 := r14 h8 h18 h35
  have h25 : p25 := r7 h7 h18 h30
  have h32 : p32 := r27 f3 h25
  have h24 : p24 := r28 f3 h12 h35
  have h21 : p21 := r9 f3 h24 h30
  have h0 : p0 := r3 f3 h21
  have h4 : p4 := r0 h12 h21 h25
  have h11 : p11 := r31 f3 h4 h7
  have h9 : p9 := r2 h0 h8
  have h15 : p15 := r17 h9 h21
  have h6 : p6 := r5 h9 h11
  have h14 : p14 := r1 h1 h32
  have h19 : p19 := r32 f5 h8 h14
  have h34 : p34 := r24 h6 h15 h19
  exact h34
#print axioms cogModel_074a2460eae073aec15d5e012dc9fac5d955f74436f5d1c5f5cccdbde178d0df

theorem cogModel_ea5bd0fa8682cd13ab001b0da28fe1c10deda20aa8d5e647cf64c0582af0bc3b (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 p41 : Prop) (f12 : p12) (f33 : p33) (f38 : p38) (r0 : p38 → p37) (r1 : p22 → p33 → p13) (r2 : p11 → p16 → p33 → p41) (r3 : p9 → p34 → p24) (r4 : p0 → p5 → p18 → p4) (r5 : p30 → p33 → p38 → p27) (r6 : p24 → p33 → p38 → p8) (r7 : p1 → p4 → p10 → p6) (r8 : p33 → p21) (r9 : p33 → p38 → p17) (r10 : p16 → p29) (r11 : p16 → p37 → p38 → p39) (r12 : p9 → p28 → p18) (r13 : p25 → p38 → p30) (r14 : p33 → p36 → p15) (r15 : p2 → p5 → p38 → p34) (r16 : p23 → p9) (r17 : p7 → p12 → p19) (r18 : p12 → p37 → p11) (r19 : p12 → p33 → p25) (r20 : p5 → p27 → p32 → p28) (r21 : p12 → p13 → p38 → p7) (r22 : p13 → p22 → p37 → p31) (r23 : p5 → p12 → p25 → p2) (r24 : p0 → p9 → p10) (r25 : p7 → p33 → p39 → p40) (r26 : p12 → p33 → p38 → p5) (r27 : p8 → p30 → p0) (r28 : p12 → p33 → p38 → p16) (r29 : p31 → p41 → p3) (r30 : p12 → p18 → p33 → p1) (r31 : p14 → p33 → p20) (r32 : p5 → p8 → p28 → p26) (r33 : p12 → p27 → p38 → p32) (r34 : p16 → p33 → p22) (r35 : p5 → p25 → p23) (r36 : p7 → p33 → p35) : p6 := by
  have h5 : p5 := r26 f12 f33 f38
  have h25 : p25 := r19 f12 f33
  have h23 : p23 := r35 h5 h25
  have h9 : p9 := r16 h23
  have h30 : p30 := r13 h25 f38
  have h27 : p27 := r5 h30 f33 f38
  have h32 : p32 := r33 f12 h27 f38
  have h28 : p28 := r20 h5 h27 h32
  have h18 : p18 := r12 h9 h28
  have h1 : p1 := r30 f12 h18 f33
  have h2 : p2 := r23 h5 f12 h25
  have h34 : p34 := r15 h2 h5 f38
  have h24 : p24 := r3 h9 h34
  have h8 : p8 := r6 h24 f33 f38
  have h0 : p0 := r27 h8 h30
  have h10 : p10 := r24 h0 h9
  have h4 : p4 := r4 h0 h5 h18
  have h6 : p6 := r7 h1 h4 h10
  exact h6
#print axioms cogModel_ea5bd0fa8682cd13ab001b0da28fe1c10deda20aa8d5e647cf64c0582af0bc3b

theorem cogModel_569b88bba8b52472a60779a488fe02949237a52efa847c78cf1857338ec743a8 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 p41 p42 p43 p44 p45 p46 p47 p48 : Prop) (f2 : p2) (f17 : p17) (f24 : p24) (f42 : p42) (r0 : p25 → p39 → p4) (r1 : p1 → p2 → p47) (r2 : p24 → p42 → p43) (r3 : p1 → p5 → p36 → p6) (r4 : p1 → p18 → p48) (r5 : p2 → p23 → p24 → p20) (r6 : p5 → p27 → p36 → p46) (r7 : p2 → p26 → p42 → p41) (r8 : p2 → p7 → p23 → p29) (r9 : p13 → p23 → p3) (r10 : p2 → p14 → p16) (r11 : p2 → p37 → p34) (r12 : p20 → p29 → p11) (r13 : p17 → p21 → p10) (r14 : p24 → p41 → p42 → p32) (r15 : p17 → p36) (r16 : p17 → p35 → p8) (r17 : p26 → p18) (r18 : p12 → p37 → p39) (r19 : p17 → p26) (r20 : p15 → p23 → p33 → p35) (r21 : p1 → p5) (r22 : p1 → p26 → p27 → p22) (r23 : p24 → p35 → p43 → p12) (r24 : p2 → p24 → p40) (r25 : p24 → p40 → p42 → p23) (r26 : p17 → p31) (r27 : p7 → p34 → p13) (r28 : p32 → p42 → p46 → p19) (r29 : p2 → p44 → p7) (r30 : p15 → p37 → p38) (r31 : p2 → p24 → p42 → p44) (r32 : p17 → p41 → p27) (r33 : p20 → p37 → p40 → p9) (r34 : p2 → p41 → p42 → p1) (r35 : p3 → p43 → p30) (r36 : p9 → p30 → p34 → p25) (r37 : p26 → p0) (r38 : p24 → p45 → p28) (r39 : p23 → p43 → p37) (r40 : p9 → p20 → p15) (r41 : p9 → p44 → p33) : p4 := by
  have h43 : p43 := r2 f24 f42
  have h40 : p40 := r24 f2 f24
  have h23 : p23 := r25 f24 h40 f42
  have h37 : p37 := r39 h23 h43
  have h34 : p34 := r11 f2 h37
  have h20 : p20 := r5 f2 h23 f24
  have h9 : p9 := r33 h20 h37 h40
  have h15 : p15 := r40 h9 h20
  have h44 : p44 := r31 f2 f24 f42
  have h7 : p7 := r29 f2 h44
  have h13 : p13 := r27 h7 h34
  have h3 : p3 := r9 h13 h23
  have h30 : p30 := r35 h3 h43
  have h25 : p25 := r36 h9 h30 h34
  have h33 : p33 := r41 h9 h44
  have h35 : p35 := r20 h15 h23 h33
  have h12 : p12 := r23 f24 h35 h43
  have h39 : p39 := r18 h12 h37
  have h4 : p4 := r0 h25 h39
  exact h4
#print axioms cogModel_569b88bba8b52472a60779a488fe02949237a52efa847c78cf1857338ec743a8

theorem cogModel_06ebbafec7cb514edf71b01c9b1d1696c6f29a232d37ea4391c98001657e5642 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 : Prop) (f1 : p1) (f3 : p3) (f5 : p5) (f13 : p13) (f24 : p24) (r0 : p15 → p24 → p4) (r1 : p16 → p23) (r2 : p12 → p18) (r3 : p1 → p5 → p19 → p22) (r4 : p19 → p25) (r5 : p23 → p8) (r6 : p18 → p21) (r7 : p3 → p17) (r8 : p5 → p10 → p14) (r9 : p1 → p10) (r10 : p2 → p6) (r11 : p10 → p20) (r12 : p8 → p12) (r13 : p0 → p1 → p7) (r14 : p3 → p13 → p22 → p11) (r15 : p21 → p2) (r16 : p3 → p16) (r17 : p6 → p9) (r18 : p13 → p19) : p9 := by
  have h16 : p16 := r16 f3
  have h23 : p23 := r1 h16
  have h8 : p8 := r5 h23
  have h12 : p12 := r12 h8
  have h18 : p18 := r2 h12
  have h21 : p21 := r6 h18
  have h2 : p2 := r15 h21
  have h6 : p6 := r10 h2
  have h9 : p9 := r17 h6
  exact h9
#print axioms cogModel_06ebbafec7cb514edf71b01c9b1d1696c6f29a232d37ea4391c98001657e5642

theorem cogModel_0f3f2b76231a093ef0dca26965db21198e8c7348f7a0cb74a3797f411bb467f9 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 : Prop) (f8 : p8) (f19 : p19) (f22 : p22) (f31 : p31) (f37 : p37) (r0 : p8 → p11 → p1) (r1 : p19 → p26 → p27 → p12) (r2 : p1 → p4 → p8 → p28) (r3 : p8 → p24 → p17) (r4 : p14 → p27 → p3) (r5 : p8 → p9 → p11) (r6 : p14 → p24 → p17) (r7 : p20 → p22 → p33 → p15) (r8 : p3 → p10 → p9) (r9 : p8 → p20 → p31 → p38) (r10 : p13 → p19 → p1) (r11 : p2 → p6 → p37 → p5) (r12 : p22 → p31 → p14) (r13 : p19 → p22 → p2) (r14 : p10 → p22 → p12) (r15 : p14 → p26 → p10) (r16 : p22 → p31 → p37 → p24) (r17 : p1 → p36 → p0) (r18 : p29 → p32 → p35) (r19 : p32 → p37 → p35) (r20 : p2 → p8 → p19 → p33) (r21 : p9 → p37 → p11) (r22 : p1 → p22 → p28) (r23 : p9 → p26 → p32) (r24 : p26 → p27 → p36 → p29) (r25 : p19 → p31 → p36) (r26 : p3 → p36 → p4) (r27 : p8 → p19 → p20) (r28 : p17 → p37 → p27) (r29 : p9 → p24 → p13) (r30 : p22 → p26 → p27) (r31 : p2 → p38 → p21) (r32 : p22 → p34 → p23) (r33 : p9 → p37 → p13) (r34 : p8 → p37 → p24) (r35 : p26 → p37 → p10) (r36 : p25 → p31 → p39) (r37 : p14 → p19 → p24 → p26) (r38 : p29 → p37 → p9) (r39 : p18 → p31 → p30) (r40 : p8 → p10 → p29) (r41 : p10 → p19 → p3) (r42 : p8 → p22 → p35 → p7) (r43 : p6 → p8 → p37 → p40) (r44 : p19 → p14) (r45 : p1 → p22 → p0) (r46 : p31 → p6) (r47 : p0 → p7 → p28 → p16) : p16 := by
  have h36 : p36 := r25 f19 f31
  have h24 : p24 := r34 f8 f37
  have h14 : p14 := r44 f19
  have h26 : p26 := r37 h14 f19 h24
  have h10 : p10 := r35 h26 f37
  have h29 : p29 := r40 f8 h10
  have h3 : p3 := r41 h10 f19
  have h9 : p9 := r38 h29 f37
  have h32 : p32 := r23 h9 h26
  have h13 : p13 := r29 h9 h24
  have h11 : p11 := r5 f8 h9
  have h4 : p4 := r26 h3 h36
  have h35 : p35 := r18 h29 h32
  have h7 : p7 := r42 f8 f22 h35
  have h1 : p1 := r0 f8 h11
  have h0 : p0 := r17 h1 h36
  have h28 : p28 := r2 h1 h4 f8
  have h16 : p16 := r47 h0 h7 h28
  exact h16
#print axioms cogModel_0f3f2b76231a093ef0dca26965db21198e8c7348f7a0cb74a3797f411bb467f9

theorem cogModel_b88019d5bf6a3581cf2b419299f27feaccd44bd5be60827f50272440ef1da7be (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 : Prop) (f2 : p2) (f4 : p4) (f22 : p22) (f23 : p23) (f31 : p31) (r0 : p3 → p22 → p32 → p26) (r1 : p10 → p32 → p19) (r2 : p23 → p32 → p24) (r3 : p9 → p24 → p21) (r4 : p10 → p23 → p8) (r5 : p4 → p7 → p29) (r6 : p2 → p8 → p15) (r7 : p12 → p6) (r8 : p2 → p23 → p0) (r9 : p22 → p31 → p32 → p24) (r10 : p2 → p4 → p5) (r11 : p23 → p31 → p25) (r12 : p8 → p22 → p20) (r13 : p2 → p22 → p27) (r14 : p4 → p22 → p13) (r15 : p2 → p13 → p3) (r16 : p9 → p24 → p26 → p10) (r17 : p0 → p22 → p31 → p3) (r18 : p2 → p13 → p11) (r19 : p0 → p4 → p32) (r20 : p19 → p23 → p18) (r21 : p2 → p16 → p32) (r22 : p19 → p22 → p20) (r23 : p15 → p18 → p20 → p1) (r24 : p4 → p14 → p28) (r25 : p2 → p11 → p9) (r26 : p4 → p21 → p23 → p8) (r27 : p4 → p31 → p16) (r28 : p23 → p30 → p17) (r29 : p23 → p12) : p1 := by
  have h16 : p16 := r27 f4 f31
  have h32 : p32 := r21 f2 h16
  have h24 : p24 := r9 f22 f31 h32
  have h13 : p13 := r14 f4 f22
  have h11 : p11 := r18 f2 h13
  have h9 : p9 := r25 f2 h11
  have h21 : p21 := r3 h9 h24
  have h3 : p3 := r15 f2 h13
  have h26 : p26 := r0 h3 f22 h32
  have h10 : p10 := r16 h9 h24 h26
  have h8 : p8 := r26 f4 h21 f23
  have h15 : p15 := r6 f2 h8
  have h20 : p20 := r12 h8 f22
  have h19 : p19 := r1 h10 h32
  have h18 : p18 := r20 h19 f23
  have h1 : p1 := r23 h15 h18 h20
  exact h1
#print axioms cogModel_b88019d5bf6a3581cf2b419299f27feaccd44bd5be60827f50272440ef1da7be

theorem cogModel_a479a2cdadd03d5a8a9ba71466c12ae4abc17271a98849f10e0abf692f950b90 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 : Prop) (f13 : p13) (f25 : p25) (f26 : p26) (f30 : p30) (f33 : p33) (r0 : p15 → p28 → p19) (r1 : p13 → p30 → p32) (r2 : p4 → p8 → p23 → p17) (r3 : p4 → p25 → p15) (r4 : p4 → p10 → p23) (r5 : p29 → p9) (r6 : p33 → p2) (r7 : p11 → p24) (r8 : p0 → p2 → p25 → p35) (r9 : p13 → p25 → p33 → p0) (r10 : p9 → p35 → p5) (r11 : p27 → p30 → p6) (r12 : p20 → p26 → p1) (r13 : p26 → p29 → p33 → p11) (r14 : p14 → p34 → p21) (r15 : p19 → p25 → p22) (r16 : p2 → p11 → p30 → p7) (r17 : p25 → p20) (r18 : p1 → p26 → p28) (r19 : p20 → p30 → p4) (r20 : p13 → p29) (r21 : p4 → p17 → p14) (r22 : p13 → p31 → p3) (r23 : p15 → p18 → p8) (r24 : p13 → p25 → p33 → p18) (r25 : p1 → p17 → p18 → p34) (r26 : p0 → p13 → p30 → p12) (r27 : p2 → p35 → p16) (r28 : p4 → p18 → p25 → p10) : p21 := by
  have h18 : p18 := r24 f13 f25 f33
  have h20 : p20 := r17 f25
  have h4 : p4 := r19 h20 f30
  have h1 : p1 := r12 h20 f26
  have h10 : p10 := r28 h4 h18 f25
  have h23 : p23 := r4 h4 h10
  have h15 : p15 := r3 h4 f25
  have h8 : p8 := r23 h15 h18
  have h17 : p17 := r2 h4 h8 h23
  have h14 : p14 := r21 h4 h17
  have h34 : p34 := r25 h1 h17 h18
  have h21 : p21 := r14 h14 h34
  exact h21
#print axioms cogModel_a479a2cdadd03d5a8a9ba71466c12ae4abc17271a98849f10e0abf692f950b90

theorem cogModel_06a26f627b471fd201642e928ec6fe1edd4be20a29020880c59b00c6211fbe29 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 : Prop) (f1 : p1) (f5 : p5) (f11 : p11) (f22 : p22) (r0 : p13 → p3) (r1 : p1 → p6 → p16) (r2 : p5 → p22 → p2) (r3 : p1 → p22 → p9) (r4 : p14 → p19) (r5 : p8 → p0) (r6 : p19 → p13) (r7 : p5 → p7) (r8 : p1 → p21 → p20) (r9 : p0 → p10) (r10 : p7 → p14) (r11 : p9 → p18) (r12 : p11 → p17) (r13 : p3 → p8) (r14 : p5 → p12) (r15 : p5 → p23 → p4) (r16 : p1 → p15) : p10 := by
  have h7 : p7 := r7 f5
  have h14 : p14 := r10 h7
  have h19 : p19 := r4 h14
  have h13 : p13 := r6 h19
  have h3 : p3 := r0 h13
  have h8 : p8 := r13 h3
  have h0 : p0 := r5 h8
  have h10 : p10 := r9 h0
  exact h10
#print axioms cogModel_06a26f627b471fd201642e928ec6fe1edd4be20a29020880c59b00c6211fbe29

theorem cogModel_ddb6bb666d2faf94d2d66fec7384790dff37fefef476badff83fd6e854b68833 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 : Prop) (f3 : p3) (f6 : p6) (f8 : p8) (f21 : p21) (r0 : p2 → p8 → p22 → p29) (r1 : p6 → p8 → p21 → p10) (r2 : p3 → p18 → p21 → p25) (r3 : p3 → p21 → p22 → p5) (r4 : p10 → p12 → p13) (r5 : p6 → p23 → p1) (r6 : p0 → p27 → p20) (r7 : p3 → p15 → p27) (r8 : p8 → p12) (r9 : p6 → p8 → p21 → p12) (r10 : p1 → p14 → p20 → p17) (r11 : p12 → p21 → p15) (r12 : p15 → p21 → p26) (r13 : p6 → p8 → p21 → p22) (r14 : p0 → p3 → p1) (r15 : p6 → p15 → p30) (r16 : p3 → p22 → p18) (r17 : p13 → p21 → p27) (r18 : p3 → p12 → p13) (r19 : p13 → p15 → p21 → p30) (r20 : p3 → p11 → p9) (r21 : p3 → p12 → p15) (r22 : p3 → p15 → p26) (r23 : p21 → p28 → p19) (r24 : p18 → p2) (r25 : p8 → p21 → p10) (r26 : p23 → p30 → p14) (r27 : p13 → p27 → p30 → p23) (r28 : p21 → p26 → p0) (r29 : p4 → p8 → p16) (r30 : p3 → p6 → p30 → p24) (r31 : p21 → p22 → p7) (r32 : p12 → p26 → p27 → p0) : p17 := by
  have h12 : p12 := r9 f6 f8 f21
  have h13 : p13 := r18 f3 h12
  have h15 : p15 := r11 h12 f21
  have h26 : p26 := r12 h15 f21
  have h30 : p30 := r19 h13 h15 f21
  have h0 : p0 := r28 f21 h26
  have h1 : p1 := r14 h0 f3
  have h27 : p27 := r17 h13 f21
  have h20 : p20 := r6 h0 h27
  have h23 : p23 := r27 h13 h27 h30
  have h14 : p14 := r26 h23 h30
  have h17 : p17 := r10 h1 h14 h20
  exact h17
#print axioms cogModel_ddb6bb666d2faf94d2d66fec7384790dff37fefef476badff83fd6e854b68833

theorem cogModel_7111151837d85e18e1aba664e2d791d6a5ee4dd0165235dac1671a525a0e2313 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 : Prop) (f2 : p2) (f9 : p9) (f19 : p19) (f22 : p22) (r0 : p16 → p19 → p20) (r1 : p3 → p22 → p17) (r2 : p19 → p22 → p26) (r3 : p2 → p3 → p9 → p10) (r4 : p2 → p19 → p15) (r5 : p2 → p9 → p8) (r6 : p5 → p12 → p26 → p23) (r7 : p9 → p22 → p8) (r8 : p9 → p19 → p6) (r9 : p9 → p23 → p18) (r10 : p12 → p24 → p13) (r11 : p8 → p22 → p28) (r12 : p15 → p19 → p26 → p12) (r13 : p2 → p8 → p12) (r14 : p9 → p15 → p5) (r15 : p5 → p9 → p23) (r16 : p2 → p25) (r17 : p9 → p15) (r18 : p2 → p19 → p3) (r19 : p14 → p27) (r20 : p8 → p22 → p24 → p18) (r21 : p13 → p18 → p21) (r22 : p8 → p15 → p28) (r23 : p2 → p9 → p26) (r24 : p7 → p19 → p1) (r25 : p4 → p22 → p0) (r26 : p10 → p14) (r27 : p5 → p8 → p24) (r28 : p9 → p26 → p5) (r29 : p2 → p25 → p11) (r30 : p19 → p23 → p13) : p21 := by
  have h8 : p8 := r5 f2 f9
  have h26 : p26 := r2 f19 f22
  have h15 : p15 := r4 f2 f19
  have h12 : p12 := r13 f2 h8
  have h5 : p5 := r14 f9 h15
  have h24 : p24 := r27 h5 h8
  have h23 : p23 := r6 h5 h12 h26
  have h13 : p13 := r10 h12 h24
  have h18 : p18 := r20 h8 f22 h24
  have h21 : p21 := r21 h13 h18
  exact h21
#print axioms cogModel_7111151837d85e18e1aba664e2d791d6a5ee4dd0165235dac1671a525a0e2313

theorem cogModel_010161dfd17b5d4c9479487bd24d9a76e4872f007f30977580d313659ba0c0cd (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 : Prop) (f6 : p6) (f7 : p7) (f10 : p10) (f15 : p15) (f19 : p19) (r0 : p10 → p19 → p2) (r1 : p7 → p15 → p19 → p22) (r2 : p6 → p19 → p20) (r3 : p19 → p1) (r4 : p2 → p17) (r5 : p6 → p10 → p15 → p12) (r6 : p12 → p20 → p9) (r7 : p9 → p17 → p18 → p5) (r8 : p6 → p14 → p11) (r9 : p6 → p19 → p22 → p4) (r10 : p8 → p19 → p0) (r11 : p6 → p10 → p21) (r12 : p4 → p21 → p3) (r13 : p7 → p19 → p14) (r14 : p19 → p20 → p18) (r15 : p7 → p16 → p13) : p5 := by
  have h12 : p12 := r5 f6 f10 f15
  have h2 : p2 := r0 f10 f19
  have h17 : p17 := r4 h2
  have h20 : p20 := r2 f6 f19
  have h9 : p9 := r6 h12 h20
  have h18 : p18 := r14 f19 h20
  have h5 : p5 := r7 h9 h17 h18
  exact h5
#print axioms cogModel_010161dfd17b5d4c9479487bd24d9a76e4872f007f30977580d313659ba0c0cd

theorem cogModel_dd4fc1f17a19a0d284b9a7f9d36855f07e328bbee53255fafa1450d6da307c08 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 : Prop) (f2 : p2) (f3 : p3) (f25 : p25) (r0 : p2 → p3 → p1) (r1 : p23 → p26 → p0) (r2 : p3 → p14 → p18) (r3 : p3 → p22 → p25 → p23) (r4 : p8 → p12 → p21) (r5 : p11 → p4) (r6 : p7 → p26) (r7 : p2 → p3 → p22) (r8 : p27 → p6) (r9 : p3 → p9 → p10) (r10 : p1 → p25 → p11) (r11 : p2 → p11 → p15 → p17) (r12 : p3 → p5 → p16) (r13 : p2 → p3 → p22 → p24) (r14 : p2 → p25 → p7) (r15 : p13 → p25 → p8) (r16 : p24 → p13) (r17 : p0 → p13 → p12) (r18 : p2 → p20 → p19) (r19 : p2 → p3 → p27) (r20 : p2 → p25 → p15) : p21 := by
  have h22 : p22 := r7 f2 f3
  have h23 : p23 := r3 f3 h22 f25
  have h24 : p24 := r13 f2 f3 h22
  have h7 : p7 := r14 f2 f25
  have h26 : p26 := r6 h7
  have h0 : p0 := r1 h23 h26
  have h13 : p13 := r16 h24
  have h12 : p12 := r17 h0 h13
  have h8 : p8 := r15 h13 f25
  have h21 : p21 := r4 h8 h12
  exact h21
#print axioms cogModel_dd4fc1f17a19a0d284b9a7f9d36855f07e328bbee53255fafa1450d6da307c08

theorem cogModel_637c6ebcd353f09a7fb32b1f86fbf71fe98fbef37b8553ad89f44e68e3ca4b11 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 : Prop) (f9 : p9) (f11 : p11) (f18 : p18) (f19 : p19) (f21 : p21) (r0 : p19 → p26 → p12) (r1 : p11 → p18 → p19 → p1) (r2 : p1 → p19 → p24) (r3 : p5 → p21 → p16) (r4 : p11 → p23 → p6) (r5 : p11 → p19 → p26 → p5) (r6 : p11 → p20 → p13) (r7 : p0 → p19 → p17) (r8 : p16 → p25) (r9 : p11 → p19 → p26) (r10 : p9 → p21 → p3) (r11 : p9 → p21 → p8) (r12 : p3 → p23) (r13 : p11 → p21 → p22) (r14 : p2 → p4 → p25 → p15) (r15 : p9 → p12 → p18 → p10) (r16 : p5 → p10 → p27 → p4) (r17 : p5 → p27 → p2) (r18 : p5 → p9 → p22 → p27) (r19 : p11 → p14 → p7) : p15 := by
  have h26 : p26 := r9 f11 f19
  have h22 : p22 := r13 f11 f21
  have h12 : p12 := r0 f19 h26
  have h10 : p10 := r15 f9 h12 f18
  have h5 : p5 := r5 f11 f19 h26
  have h16 : p16 := r3 h5 f21
  have h25 : p25 := r8 h16
  have h27 : p27 := r18 h5 f9 h22
  have h2 : p2 := r17 h5 h27
  have h4 : p4 := r16 h5 h10 h27
  have h15 : p15 := r14 h2 h4 h25
  exact h15
#print axioms cogModel_637c6ebcd353f09a7fb32b1f86fbf71fe98fbef37b8553ad89f44e68e3ca4b11

theorem cogModel_f5d28228b3e45539afae1e25534013cc5922716ab8cdff9a60321b9f02512382 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 : Prop) (f3 : p3) (f16 : p16) (f18 : p18) (r0 : p12 → p16 → p0) (r1 : p1 → p11 → p16 → p2) (r2 : p3 → p6 → p14) (r3 : p7 → p8) (r4 : p3 → p4 → p9 → p11) (r5 : p1 → p3 → p9) (r6 : p21 → p13) (r7 : p3 → p23) (r8 : p15 → p7) (r9 : p4 → p1) (r10 : p23 → p15) (r11 : p16 → p17 → p10) (r12 : p8 → p21) (r13 : p11 → p19 → p5) (r14 : p16 → p22 → p20) (r15 : p3 → p19) (r16 : p16 → p18 → p4) : p13 := by
  have h23 : p23 := r7 f3
  have h15 : p15 := r10 h23
  have h7 : p7 := r8 h15
  have h8 : p8 := r3 h7
  have h21 : p21 := r12 h8
  have h13 : p13 := r6 h21
  exact h13
#print axioms cogModel_f5d28228b3e45539afae1e25534013cc5922716ab8cdff9a60321b9f02512382

theorem cogModel_433dbdf08c0dc222b1948120cbe8dde9e2480babeb3a498b3acf43f155f308de (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 : Prop) (f8 : p8) (f12 : p12) (f16 : p16) (f23 : p23) (r0 : p11 → p23 → p15) (r1 : p8 → p23 → p14) (r2 : p10 → p19 → p6) (r3 : p7 → p16 → p21) (r4 : p9 → p18 → p24 → p1) (r5 : p9 → p18 → p0) (r6 : p12 → p23 → p9) (r7 : p8 → p12 → p16 → p19) (r8 : p8 → p12 → p16 → p25) (r9 : p8 → p16 → p19 → p10) (r10 : p6 → p2) (r11 : p1 → p9 → p12 → p22) (r12 : p0 → p1 → p7 → p17) (r13 : p12 → p16 → p24) (r14 : p9 → p24 → p7) (r15 : p8 → p23 → p18) (r16 : p17 → p21 → p22 → p3) (r17 : p8 → p23 → p20) (r18 : p4 → p12 → p5) (r19 : p16 → p20 → p13) : p3 := by
  have h9 : p9 := r6 f12 f23
  have h18 : p18 := r15 f8 f23
  have h0 : p0 := r5 h9 h18
  have h24 : p24 := r13 f12 f16
  have h1 : p1 := r4 h9 h18 h24
  have h7 : p7 := r14 h9 h24
  have h22 : p22 := r11 h1 h9 f12
  have h17 : p17 := r12 h0 h1 h7
  have h21 : p21 := r3 h7 f16
  have h3 : p3 := r16 h17 h21 h22
  exact h3
#print axioms cogModel_433dbdf08c0dc222b1948120cbe8dde9e2480babeb3a498b3acf43f155f308de

theorem cogModel_a99ec383adf55963ac86e885c467091849674ca8d4a146f185572110882d09dc (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 : Prop) (f2 : p2) (f6 : p6) (f11 : p11) (f33 : p33) (r0 : p7 → p11 → p37 → p36) (r1 : p2 → p6 → p28 → p15) (r2 : p2 → p15 → p33 → p10) (r3 : p2 → p11 → p33 → p37) (r4 : p6 → p3) (r5 : p2 → p11 → p28) (r6 : p4 → p0) (r7 : p28 → p27) (r8 : p6 → p20 → p23) (r9 : p1 → p33 → p25) (r10 : p7 → p11 → p35 → p31) (r11 : p2 → p6 → p33 → p13) (r12 : p2 → p6 → p33 → p24) (r13 : p8 → p20 → p35) (r14 : p2 → p11 → p8) (r15 : p6 → p13 → p18) (r16 : p26 → p31 → p19) (r17 : p6 → p14 → p12) (r18 : p3 → p6 → p18 → p29) (r19 : p2 → p22 → p17) (r20 : p4 → p33 → p20) (r21 : p10 → p33 → p9) (r22 : p7 → p8 → p4) (r23 : p6 → p21 → p34) (r24 : p0 → p8 → p35 → p26) (r25 : p6 → p11 → p33 → p7) (r26 : p16 → p27 → p5) (r27 : p0 → p6 → p20 → p32) (r28 : p33 → p30) (r29 : p10 → p24 → p16) : p19 := by
  have h8 : p8 := r14 f2 f11
  have h7 : p7 := r25 f6 f11 f33
  have h4 : p4 := r22 h7 h8
  have h0 : p0 := r6 h4
  have h20 : p20 := r20 h4 f33
  have h35 : p35 := r13 h8 h20
  have h26 : p26 := r24 h0 h8 h35
  have h31 : p31 := r10 h7 f11 h35
  have h19 : p19 := r16 h26 h31
  exact h19
#print axioms cogModel_a99ec383adf55963ac86e885c467091849674ca8d4a146f185572110882d09dc

theorem cogModel_880b4b7b0d91f465ef993274d161b1b3bfaa5fdab4af2d28eef397204fc3a05d (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 : Prop) (f0 : p0) (f2 : p2) (f4 : p4) (f6 : p6) (f22 : p22) (r0 : p12 → p22 → p21) (r1 : p22 → p13) (r2 : p5 → p9 → p11 → p19) (r3 : p7 → p10) (r4 : p2 → p8 → p15 → p9) (r5 : p22 → p7) (r6 : p0 → p8 → p5) (r7 : p7 → p18 → p23) (r8 : p1 → p22 → p14) (r9 : p0 → p2 → p18) (r10 : p2 → p16 → p3) (r11 : p6 → p7 → p13 → p17) (r12 : p4 → p22 → p15) (r13 : p4 → p15 → p11) (r14 : p0 → p4 → p23 → p20) (r15 : p0 → p4 → p8) (r16 : p22 → p25 → p24) : p19 := by
  have h15 : p15 := r12 f4 f22
  have h8 : p8 := r15 f0 f4
  have h11 : p11 := r13 f4 h15
  have h5 : p5 := r6 f0 h8
  have h9 : p9 := r4 f2 h8 h15
  have h19 : p19 := r2 h5 h9 h11
  exact h19
#print axioms cogModel_880b4b7b0d91f465ef993274d161b1b3bfaa5fdab4af2d28eef397204fc3a05d

theorem cogModel_90cc7c9a943381ef00e8e34b91e983ac14e9bcdeee32981c48e6f71d62c6e4fc (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 : Prop) (f0 : p0) (f6 : p6) (f13 : p13) (f14 : p14) (f18 : p18) (r0 : p6 → p23) (r1 : p13 → p18 → p22 → p26) (r2 : p13 → p18 → p22) (r3 : p4 → p18 → p9) (r4 : p15 → p20 → p16) (r5 : p4 → p11 → p20) (r6 : p12 → p18 → p20) (r7 : p8 → p22 → p3) (r8 : p0 → p24 → p9) (r9 : p10 → p8) (r10 : p5 → p7 → p10) (r11 : p13 → p14 → p18 → p5) (r12 : p18 → p19 → p21) (r13 : p6 → p13 → p24 → p11) (r14 : p4 → p24 → p12) (r15 : p9 → p12 → p18 → p15) (r16 : p13 → p18 → p24) (r17 : p2 → p14 → p1) (r18 : p5 → p13 → p18 → p7) (r19 : p4 → p6 → p12) (r20 : p0 → p6 → p14 → p4) (r21 : p0 → p13 → p18 → p24) (r22 : p4 → p18 → p11) (r23 : p18 → p25 → p17) : p16 := by
  have h24 : p24 := r21 f0 f13 f18
  have h11 : p11 := r13 f6 f13 h24
  have h9 : p9 := r8 f0 h24
  have h4 : p4 := r20 f0 f6 f14
  have h20 : p20 := r5 h4 h11
  have h12 : p12 := r14 h4 h24
  have h15 : p15 := r15 h9 h12 f18
  have h16 : p16 := r4 h15 h20
  exact h16
#print axioms cogModel_90cc7c9a943381ef00e8e34b91e983ac14e9bcdeee32981c48e6f71d62c6e4fc

theorem cogModel_0a95cd7218d92784a6ebece29fd279dd265226cc39b390c873eaa219fdd83858 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 : Prop) (f1 : p1) (f9 : p9) (f10 : p10) (r0 : p3 → p4) (r1 : p1 → p17 → p11) (r2 : p9 → p10 → p14) (r3 : p2 → p9 → p13 → p18) (r4 : p13 → p14 → p16) (r5 : p5 → p3) (r6 : p10 → p6) (r7 : p9 → p12 → p8) (r8 : p1 → p10 → p14 → p2) (r9 : p1 → p5) (r10 : p1 → p2 → p13) (r11 : p10 → p15 → p0) (r12 : p9 → p10 → p13 → p7) : p4 := by
  have h5 : p5 := r9 f1
  have h3 : p3 := r5 h5
  have h4 : p4 := r0 h3
  exact h4
#print axioms cogModel_0a95cd7218d92784a6ebece29fd279dd265226cc39b390c873eaa219fdd83858

theorem cogModel_fc6d0e9b43aeaf6cc754d4db641596a382f808f13a29f566c0ef90c7b656bb05 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 : Prop) (f3 : p3) (f5 : p5) (f11 : p11) (f17 : p17) (f20 : p20) (r0 : p17 → p16) (r1 : p17 → p20 → p4) (r2 : p15 → p23 → p26 → p13) (r3 : p3 → p8 → p17 → p27) (r4 : p11 → p18 → p15) (r5 : p2 → p5 → p9) (r6 : p3 → p5 → p12) (r7 : p11 → p17 → p22 → p8) (r8 : p3 → p11 → p18) (r9 : p1 → p20 → p21) (r10 : p3 → p4 → p26) (r11 : p3 → p4 → p15) (r12 : p3 → p17 → p20 → p22) (r13 : p3 → p4) (r14 : p5 → p14 → p16 → p25) (r15 : p5 → p11 → p18) (r16 : p4 → p18 → p23) (r17 : p10 → p17 → p19) (r18 : p3 → p12 → p24 → p7) (r19 : p3 → p5 → p11 → p14) (r20 : p11 → p24) (r21 : p0 → p5 → p6) : p13 := by
  have h18 : p18 := r8 f3 f11
  have h15 : p15 := r4 f11 h18
  have h4 : p4 := r1 f17 f20
  have h23 : p23 := r16 h4 h18
  have h26 : p26 := r10 f3 h4
  have h13 : p13 := r2 h15 h23 h26
  exact h13
#print axioms cogModel_fc6d0e9b43aeaf6cc754d4db641596a382f808f13a29f566c0ef90c7b656bb05

theorem cogModel_11e4a907d2a18071001883c051f22b2cde4b6f4d4567409301eae5ccfc02d349 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 : Prop) (f3 : p3) (f6 : p6) (f21 : p21) (r0 : p3 → p19) (r1 : p1 → p12 → p8) (r2 : p3 → p10 → p16) (r3 : p3 → p13 → p17 → p12) (r4 : p9 → p11) (r5 : p3 → p6 → p21 → p1) (r6 : p6 → p7 → p0) (r7 : p11 → p18) (r8 : p3 → p9) (r9 : p18 → p14) (r10 : p6 → p20) (r11 : p1 → p20 → p21 → p17) (r12 : p19 → p13) (r13 : p4 → p21 → p5) (r14 : p2 → p3 → p15) : p14 := by
  have h9 : p9 := r8 f3
  have h11 : p11 := r4 h9
  have h18 : p18 := r7 h11
  have h14 : p14 := r9 h18
  exact h14
#print axioms cogModel_11e4a907d2a18071001883c051f22b2cde4b6f4d4567409301eae5ccfc02d349

theorem cogModel_e689b6ce078bcda1b5f6c5b698326d34351f4e472997cc41de13b65b9341a44f (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 : Prop) (f6 : p6) (f7 : p7) (f15 : p15) (f24 : p24) (f27 : p27) (r0 : p4 → p5 → p24 → p0) (r1 : p6 → p15 → p26) (r2 : p7 → p21 → p22) (r3 : p0 → p2 → p6 → p8) (r4 : p7 → p27 → p12) (r5 : p24 → p27 → p5) (r6 : p6 → p24 → p4) (r7 : p10 → p27 → p18) (r8 : p15 → p9) (r9 : p6 → p8 → p10 → p18) (r10 : p3 → p15 → p11) (r11 : p6 → p14 → p25) (r12 : p15 → p20 → p27 → p13) (r13 : p6 → p7 → p9 → p1) (r14 : p2 → p15 → p24 → p16) (r15 : p6 → p4) (r16 : p0 → p24 → p16) (r17 : p7 → p8 → p17) (r18 : p4 → p5 → p2) (r19 : p10 → p15 → p16 → p17) (r20 : p24 → p12) (r21 : p2 → p7 → p10) (r22 : p17 → p18 → p19) (r23 : p5 → p6 → p2) (r24 : p6 → p24 → p23) (r25 : p1 → p15 → p20) : p19 := by
  have h5 : p5 := r5 f24 f27
  have h4 : p4 := r6 f6 f24
  have h0 : p0 := r0 h4 h5 f24
  have h16 : p16 := r16 h0 f24
  have h2 : p2 := r18 h4 h5
  have h8 : p8 := r3 h0 h2 f6
  have h17 : p17 := r17 f7 h8
  have h10 : p10 := r21 h2 f7
  have h18 : p18 := r7 h10 f27
  have h19 : p19 := r22 h17 h18
  exact h19
#print axioms cogModel_e689b6ce078bcda1b5f6c5b698326d34351f4e472997cc41de13b65b9341a44f

theorem cogModel_574ee4368ef55e9c942da5475c033f9ff71c6e20d46756f8048afbed584d95a2 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 : Prop) (f5 : p5) (f19 : p19) (f20 : p20) (r0 : p4 → p24 → p1) (r1 : p5 → p10 → p12 → p14) (r2 : p0 → p10 → p12 → p11) (r3 : p5 → p19 → p18) (r4 : p0 → p10) (r5 : p1 → p16 → p17 → p15) (r6 : p0 → p10 → p22) (r7 : p5 → p20 → p24) (r8 : p19 → p20 → p12) (r9 : p20 → p23 → p3) (r10 : p5 → p11 → p13) (r11 : p4 → p19 → p17) (r12 : p5 → p10 → p2) (r13 : p8 → p20 → p9) (r14 : p19 → p20 → p4) (r15 : p4 → p18 → p16) (r16 : p20 → p0) (r17 : p10 → p20 → p22 → p7) (r18 : p5 → p21 → p6) : p15 := by
  have h18 : p18 := r3 f5 f19
  have h24 : p24 := r7 f5 f20
  have h4 : p4 := r14 f19 f20
  have h1 : p1 := r0 h4 h24
  have h16 : p16 := r15 h4 h18
  have h17 : p17 := r11 h4 f19
  have h15 : p15 := r5 h1 h16 h17
  exact h15
#print axioms cogModel_574ee4368ef55e9c942da5475c033f9ff71c6e20d46756f8048afbed584d95a2

theorem cogModel_ec767ca8886f24d8934eb439022153e20492c4ff1b65640ffaf7ef6a76cd07dd (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 : Prop) (f5 : p5) (f10 : p10) (f16 : p16) (f19 : p19) (f22 : p22) (r0 : p18 → p22 → p26 → p20) (r1 : p13 → p25 → p15) (r2 : p19 → p14) (r3 : p19 → p22 → p9) (r4 : p10 → p19 → p26) (r5 : p10 → p13 → p25 → p24) (r6 : p8 → p10 → p7) (r7 : p5 → p10 → p22 → p11) (r8 : p16 → p3) (r9 : p9 → p18 → p22 → p21) (r10 : p10 → p17) (r11 : p5 → p15 → p19 → p12) (r12 : p2 → p5 → p4) (r13 : p0 → p16 → p23) (r14 : p20 → p21 → p27) (r15 : p5 → p10 → p22 → p18) (r16 : p5 → p25) (r17 : p6 → p16 → p1) (r18 : p16 → p13) : p27 := by
  have h9 : p9 := r3 f19 f22
  have h26 : p26 := r4 f10 f19
  have h18 : p18 := r15 f5 f10 f22
  have h20 : p20 := r0 h18 f22 h26
  have h21 : p21 := r9 h9 h18 f22
  have h27 : p27 := r14 h20 h21
  exact h27
#print axioms cogModel_ec767ca8886f24d8934eb439022153e20492c4ff1b65640ffaf7ef6a76cd07dd

theorem cogModel_16cbee9dfe8e73fd0e1a362722ff2ae5dbf87a8fe45120ba4ad6e0f6f011e679 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 : Prop) (f13 : p13) (f15 : p15) (f19 : p19) (r0 : p19 → p3) (r1 : p7 → p22 → p25) (r2 : p15 → p19 → p0) (r3 : p9 → p15 → p24) (r4 : p2 → p6 → p13 → p11) (r5 : p13 → p19 → p2) (r6 : p0 → p19 → p22) (r7 : p17 → p19 → p21) (r8 : p13 → p15 → p3) (r9 : p0 → p15 → p19 → p4) (r10 : p8 → p18 → p14) (r11 : p15 → p19 → p26 → p6) (r12 : p10 → p13 → p7) (r13 : p15 → p26) (r14 : p0 → p15 → p22) (r15 : p1 → p13 → p18) (r16 : p13 → p15 → p10) (r17 : p12 → p19 → p16) (r18 : p0 → p7 → p1) (r19 : p13 → p27 → p23) (r20 : p0 → p10 → p7) (r21 : p19 → p20) (r22 : p0 → p1 → p22 → p18) (r23 : p7 → p10 → p19 → p5) (r24 : p19 → p25 → p8) : p14 := by
  have h0 : p0 := r2 f15 f19
  have h22 : p22 := r6 h0 f19
  have h10 : p10 := r16 f13 f15
  have h7 : p7 := r12 h10 f13
  have h25 : p25 := r1 h7 h22
  have h1 : p1 := r18 h0 h7
  have h8 : p8 := r24 f19 h25
  have h18 : p18 := r22 h0 h1 h22
  have h14 : p14 := r10 h8 h18
  exact h14
#print axioms cogModel_16cbee9dfe8e73fd0e1a362722ff2ae5dbf87a8fe45120ba4ad6e0f6f011e679

theorem cogModel_2484d3b2c5628b0937a065883ee5f1fd3650297a7a136b0d503a71b20953fdab (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 : Prop) (f11 : p11) (f15 : p15) (f20 : p20) (f23 : p23) (f26 : p26) (r0 : p9 → p23 → p4) (r1 : p18 → p23 → p13) (r2 : p11 → p26 → p1) (r3 : p11 → p15 → p21 → p12) (r4 : p23 → p24 → p17) (r5 : p1 → p22 → p2) (r6 : p9 → p26 → p22) (r7 : p2 → p19 → p16) (r8 : p1 → p22 → p26 → p19) (r9 : p1 → p9 → p11 → p8) (r10 : p23 → p26 → p5) (r11 : p15 → p27 → p3) (r12 : p20 → p26 → p1) (r13 : p10 → p20 → p6) (r14 : p11 → p15 → p0) (r15 : p11 → p20 → p21) (r16 : p8 → p26 → p2) (r17 : p11 → p9) (r18 : p0 → p5 → p20 → p7) (r19 : p11 → p20 → p14) (r20 : p11 → p14 → p25) (r21 : p9 → p20 → p22) (r22 : p1 → p11 → p20 → p4) : p16 := by
  have h1 : p1 := r2 f11 f26
  have h9 : p9 := r17 f11
  have h8 : p8 := r9 h1 h9 f11
  have h22 : p22 := r21 h9 f20
  have h2 : p2 := r16 h8 f26
  have h19 : p19 := r8 h1 h22 f26
  have h16 : p16 := r7 h2 h19
  exact h16
#print axioms cogModel_2484d3b2c5628b0937a065883ee5f1fd3650297a7a136b0d503a71b20953fdab

theorem cogModel_ec97006f0fc68c3abdd757da55dd1c0333e326048780576f8307997227ece709 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 : Prop) (f2 : p2) (f14 : p14) (f15 : p15) (f16 : p16) (r0 : p1 → p14 → p6) (r1 : p2 → p14 → p17 → p11) (r2 : p0 → p14 → p25 → p7) (r3 : p2 → p16 → p25) (r4 : p22 → p24) (r5 : p2 → p15 → p19) (r6 : p16 → p17) (r7 : p2 → p5 → p23) (r8 : p2 → p3) (r9 : p7 → p8 → p10 → p18) (r10 : p14 → p16 → p0) (r11 : p3 → p16 → p8) (r12 : p15 → p17 → p9) (r13 : p20 → p22 → p12) (r14 : p14 → p16 → p25 → p10) (r15 : p2 → p13 → p22) (r16 : p13 → p22 → p20) (r17 : p17 → p21) (r18 : p2 → p13) (r19 : p16 → p19 → p4) : p18 := by
  have h0 : p0 := r10 f14 f16
  have h3 : p3 := r8 f2
  have h25 : p25 := r3 f2 f16
  have h8 : p8 := r11 h3 f16
  have h7 : p7 := r2 h0 f14 h25
  have h10 : p10 := r14 f14 f16 h25
  have h18 : p18 := r9 h7 h8 h10
  exact h18
#print axioms cogModel_ec97006f0fc68c3abdd757da55dd1c0333e326048780576f8307997227ece709

theorem cogModel_13a47f78ae51a15d343301ce1841d4d8454249873720d813de195c995b3f020e (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 : Prop) (f0 : p0) (f22 : p22) (f23 : p23) (r0 : p0 → p10 → p24 → p18) (r1 : p1 → p4 → p8) (r2 : p24 → p6) (r3 : p0 → p22 → p11) (r4 : p4 → p22 → p23 → p5) (r5 : p23 → p24 → p19) (r6 : p22 → p24) (r7 : p10 → p15 → p24 → p7) (r8 : p0 → p5 → p16 → p14) (r9 : p22 → p23 → p13) (r10 : p23 → p10) (r11 : p2 → p23 → p27) (r12 : p0 → p16 → p4) (r13 : p3 → p22 → p12) (r14 : p8 → p14 → p17) (r15 : p15 → p26) (r16 : p0 → p4 → p1) (r17 : p10 → p23 → p15) (r18 : p10 → p22 → p25 → p9) (r19 : p10 → p22 → p25) (r20 : p18 → p20) (r21 : p11 → p23 → p28) (r22 : p22 → p23 → p16) (r23 : p13 → p16 → p23 → p21) : p17 := by
  have h16 : p16 := r22 f22 f23
  have h4 : p4 := r12 f0 h16
  have h1 : p1 := r16 f0 h4
  have h5 : p5 := r4 h4 f22 f23
  have h8 : p8 := r1 h1 h4
  have h14 : p14 := r8 f0 h5 h16
  have h17 : p17 := r14 h8 h14
  exact h17
#print axioms cogModel_13a47f78ae51a15d343301ce1841d4d8454249873720d813de195c995b3f020e

theorem cogModel_0734eb4ffa657c58b526cf9e115c4332a83512fc01ad3ace055e73926c620953 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 : Prop) (f3 : p3) (f17 : p17) (f26 : p26) (f30 : p30) (f32 : p32) (r0 : p3 → p11 → p19) (r1 : p26 → p31) (r2 : p1 → p17 → p23) (r3 : p3 → p30 → p22) (r4 : p3 → p31 → p32 → p27) (r5 : p30 → p18) (r6 : p5 → p17 → p32 → p16) (r7 : p30 → p15) (r8 : p3 → p26 → p24) (r9 : p24 → p31 → p7) (r10 : p8 → p17 → p18 → p0) (r11 : p24 → p27 → p28 → p4) (r12 : p16 → p8) (r13 : p2 → p4 → p30 → p20) (r14 : p6 → p20 → p13) (r15 : p26 → p30 → p25) (r16 : p17 → p28) (r17 : p4 → p6 → p9) (r18 : p9 → p26 → p29) (r19 : p13 → p29 → p10) (r20 : p14 → p30 → p12) (r21 : p3 → p4 → p21) (r22 : p7 → p26 → p31 → p2) (r23 : p17 → p26 → p5) (r24 : p3 → p27 → p28 → p6) : p10 := by
  have h28 : p28 := r16 f17
  have h31 : p31 := r1 f26
  have h27 : p27 := r4 f3 h31 f32
  have h6 : p6 := r24 f3 h27 h28
  have h24 : p24 := r8 f3 f26
  have h4 : p4 := r11 h24 h27 h28
  have h9 : p9 := r17 h4 h6
  have h7 : p7 := r9 h24 h31
  have h2 : p2 := r22 h7 f26 h31
  have h29 : p29 := r18 h9 f26
  have h20 : p20 := r13 h2 h4 f30
  have h13 : p13 := r14 h6 h20
  have h10 : p10 := r19 h13 h29
  exact h10
#print axioms cogModel_0734eb4ffa657c58b526cf9e115c4332a83512fc01ad3ace055e73926c620953

theorem cogModel_f8f1fde0c98cb5ef5d4129d4dd40192f201ff35ffae09053c171a5760b45523a (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 : Prop) (f10 : p10) (f25 : p25) (f29 : p29) (r0 : p2 → p10 → p16) (r1 : p10 → p25 → p3) (r2 : p25 → p11) (r3 : p10 → p29 → p22) (r4 : p10 → p22 → p29 → p7) (r5 : p20 → p26 → p27) (r6 : p15 → p17 → p18 → p20) (r7 : p0 → p4 → p17) (r8 : p10 → p14 → p29 → p28) (r9 : p0 → p9 → p15) (r10 : p8 → p10 → p30) (r11 : p18 → p25 → p26) (r12 : p0 → p10 → p17 → p13) (r13 : p25 → p23) (r14 : p0 → p4 → p9) (r15 : p10 → p25 → p29 → p5) (r16 : p21 → p27 → p28 → p24) (r17 : p10 → p12 → p6) (r18 : p4 → p13 → p25 → p14) (r19 : p10 → p25 → p19) (r20 : p29 → p0) (r21 : p29 → p1) (r22 : p0 → p9 → p18) (r23 : p15 → p20 → p21) (r24 : p25 → p29 → p4) : p24 := by
  have h4 : p4 := r24 f25 f29
  have h0 : p0 := r20 f29
  have h17 : p17 := r7 h0 h4
  have h9 : p9 := r14 h0 h4
  have h18 : p18 := r22 h0 h9
  have h15 : p15 := r9 h0 h9
  have h26 : p26 := r11 h18 f25
  have h20 : p20 := r6 h15 h17 h18
  have h27 : p27 := r5 h20 h26
  have h21 : p21 := r23 h15 h20
  have h13 : p13 := r12 h0 f10 h17
  have h14 : p14 := r18 h4 h13 f25
  have h28 : p28 := r8 f10 h14 f29
  have h24 : p24 := r16 h21 h27 h28
  exact h24
#print axioms cogModel_f8f1fde0c98cb5ef5d4129d4dd40192f201ff35ffae09053c171a5760b45523a

theorem cogModel_d62f6513ed334dc300e0c47bd6017d9b587714bbc35b43330ce679c7288a4c8a (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 : Prop) (f5 : p5) (f9 : p9) (f14 : p14) (f21 : p21) (f24 : p24) (r0 : p14 → p21 → p23 → p22) (r1 : p17 → p4) (r2 : p5 → p6 → p8 → p2) (r3 : p4 → p18) (r4 : p9 → p22 → p25 → p20) (r5 : p21 → p27 → p12) (r6 : p14 → p22 → p25 → p27) (r7 : p21 → p26 → p1) (r8 : p11 → p20 → p22 → p3) (r9 : p13 → p24 → p7) (r10 : p14 → p24 → p27 → p10) (r11 : p5 → p14 → p19 → p11) (r12 : p9 → p24 → p19) (r13 : p5 → p14 → p21 → p17) (r14 : p19 → p23 → p25) (r15 : p4 → p17 → p21 → p0) (r16 : p17 → p8) (r17 : p3 → p10 → p12 → p15) (r18 : p0 → p14 → p21 → p6) (r19 : p21 → p23) (r20 : p5 → p16) : p15 := by
  have h19 : p19 := r12 f9 f24
  have h23 : p23 := r19 f21
  have h25 : p25 := r14 h19 h23
  have h11 : p11 := r11 f5 f14 h19
  have h22 : p22 := r0 f14 f21 h23
  have h20 : p20 := r4 f9 h22 h25
  have h27 : p27 := r6 f14 h22 h25
  have h3 : p3 := r8 h11 h20 h22
  have h12 : p12 := r5 f21 h27
  have h10 : p10 := r10 f14 f24 h27
  have h15 : p15 := r17 h3 h10 h12
  exact h15
#print axioms cogModel_d62f6513ed334dc300e0c47bd6017d9b587714bbc35b43330ce679c7288a4c8a

theorem cogModel_e71cf6628d58d2368db0c2534c9c026369babd11dedafa377b62d705797d66e0 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 : Prop) (f6 : p6) (f8 : p8) (f16 : p16) (f17 : p17) (f18 : p18) (r0 : p8 → p16 → p18 → p3) (r1 : p0 → p5 → p2) (r2 : p16 → p20) (r3 : p3 → p6 → p8 → p9) (r4 : p3 → p9 → p11) (r5 : p6 → p12 → p24) (r6 : p6 → p8 → p4) (r7 : p16 → p22 → p15) (r8 : p6 → p8 → p18 → p14) (r9 : p17 → p18 → p21) (r10 : p8 → p19 → p1) (r11 : p4 → p17 → p5) (r12 : p4 → p14 → p21 → p0) (r13 : p3 → p11 → p23 → p13) (r14 : p7 → p8 → p10) (r15 : p8 → p20 → p23) : p2 := by
  have h21 : p21 := r9 f17 f18
  have h14 : p14 := r8 f6 f8 f18
  have h4 : p4 := r6 f6 f8
  have h5 : p5 := r11 h4 f17
  have h0 : p0 := r12 h4 h14 h21
  have h2 : p2 := r1 h0 h5
  exact h2
#print axioms cogModel_e71cf6628d58d2368db0c2534c9c026369babd11dedafa377b62d705797d66e0

theorem cogModel_2d391975b43e2e2470bede210be6d59cee638571683cf9d73f30274bdb8a4d99 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 : Prop) (f6 : p6) (f8 : p8) (f12 : p12) (f16 : p16) (f19 : p19) (r0 : p0 → p5 → p22) (r1 : p6 → p8 → p3) (r2 : p4 → p8 → p21) (r3 : p19 → p23 → p2) (r4 : p4 → p9 → p10 → p18) (r5 : p5 → p6 → p20) (r6 : p5 → p6 → p17) (r7 : p12 → p16 → p19 → p23) (r8 : p4 → p12 → p16 → p10) (r9 : p6 → p16 → p19 → p5) (r10 : p4 → p21 → p1) (r11 : p3 → p19 → p9) (r12 : p8 → p16 → p0) (r13 : p6 → p16 → p4) (r14 : p11 → p19 → p15) (r15 : p14 → p16 → p7) (r16 : p17 → p20 → p22 → p13) : p13 := by
  have h0 : p0 := r12 f8 f16
  have h5 : p5 := r9 f6 f16 f19
  have h22 : p22 := r0 h0 h5
  have h20 : p20 := r5 h5 f6
  have h17 : p17 := r6 h5 f6
  have h13 : p13 := r16 h17 h20 h22
  exact h13
#print axioms cogModel_2d391975b43e2e2470bede210be6d59cee638571683cf9d73f30274bdb8a4d99

theorem cogModel_22332dffa5eb800ef3f4429276b030beb7d952417c8f582c2c10c62054e2e10e (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 : Prop) (f4 : p4) (f5 : p5) (f9 : p9) (f17 : p17) (f22 : p22) (r0 : p5 → p17 → p20 → p18) (r1 : p9 → p17 → p22 → p8) (r2 : p17 → p21 → p2) (r3 : p7 → p20) (r4 : p4 → p9 → p22 → p14) (r5 : p5 → p23) (r6 : p4 → p22 → p25) (r7 : p9 → p1) (r8 : p5 → p6 → p16) (r9 : p5 → p7) (r10 : p4 → p3) (r11 : p9 → p13 → p12) (r12 : p8 → p0) (r13 : p0 → p16 → p19 → p26) (r14 : p4 → p5 → p17 → p6) (r15 : p5 → p8 → p19) (r16 : p9 → p17 → p10) (r17 : p1 → p15) (r18 : p17 → p24 → p11) : p26 := by
  have h8 : p8 := r1 f9 f17 f22
  have h6 : p6 := r14 f4 f5 f17
  have h0 : p0 := r12 h8
  have h19 : p19 := r15 f5 h8
  have h16 : p16 := r8 f5 h6
  have h26 : p26 := r13 h0 h16 h19
  exact h26
#print axioms cogModel_22332dffa5eb800ef3f4429276b030beb7d952417c8f582c2c10c62054e2e10e

theorem cogModel_7a16e28114ca8f509299710f589a50ab9d7a4672d724dc6f7816ba7dc6327c6c (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 : Prop) (f1 : p1) (f9 : p9) (f10 : p10) (r0 : p4 → p9 → p14) (r1 : p9 → p13 → p5) (r2 : p18 → p8) (r3 : p3 → p17 → p16) (r4 : p2 → p6 → p19) (r5 : p1 → p2 → p9 → p15) (r6 : p9 → p10 → p12) (r7 : p2 → p19 → p11) (r8 : p1 → p20 → p3) (r9 : p9 → p10 → p6) (r10 : p9 → p6) (r11 : p9 → p10 → p2) (r12 : p9 → p20 → p3) (r13 : p1 → p11 → p17) (r14 : p1 → p15 → p20) (r15 : p12 → p7) (r16 : p6 → p10 → p15) (r17 : p7 → p10 → p18) (r18 : p1 → p7 → p8 → p0) (r19 : p1 → p20 → p17) (r20 : p10 → p19 → p11) : p16 := by
  have h2 : p2 := r11 f9 f10
  have h6 : p6 := r9 f9 f10
  have h15 : p15 := r5 f1 h2 f9
  have h19 : p19 := r4 h2 h6
  have h11 : p11 := r7 h2 h19
  have h17 : p17 := r13 f1 h11
  have h20 : p20 := r14 f1 h15
  have h3 : p3 := r8 f1 h20
  have h16 : p16 := r3 h3 h17
  exact h16
#print axioms cogModel_7a16e28114ca8f509299710f589a50ab9d7a4672d724dc6f7816ba7dc6327c6c

theorem cogModel_86d2f2b91653158685405f0028ef639bb8cccd21f880a49d7f11335265547bb6 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 : Prop) (f0 : p0) (f12 : p12) (f18 : p18) (f22 : p22) (r0 : p14 → p17 → p6) (r1 : p0 → p18 → p16) (r2 : p16 → p22 → p11) (r3 : p17 → p23) (r4 : p2 → p12 → p13) (r5 : p0 → p22 → p16) (r6 : p12 → p17) (r7 : p2 → p14) (r8 : p12 → p18 → p22 → p2) (r9 : p18 → p22 → p19) (r10 : p0 → p24 → p21) (r11 : p12 → p22 → p19) (r12 : p4 → p12 → p1) (r13 : p15 → p22 → p11) (r14 : p12 → p19 → p7) (r15 : p0 → p17 → p18 → p3) (r16 : p5 → p17 → p9) (r17 : p18 → p20 → p10) (r18 : p0 → p18 → p15) (r19 : p0 → p22 → p5) (r20 : p16 → p18 → p7) (r21 : p18 → p22 → p15) (r22 : p12 → p16 → p8) (r23 : p7 → p8 → p11 → p25) : p25 := by
  have h19 : p19 := r9 f18 f22
  have h15 : p15 := r18 f0 f18
  have h7 : p7 := r14 f12 h19
  have h11 : p11 := r13 h15 f22
  have h16 : p16 := r1 f0 f18
  have h8 : p8 := r22 f12 h16
  have h25 : p25 := r23 h7 h8 h11
  exact h25
#print axioms cogModel_86d2f2b91653158685405f0028ef639bb8cccd21f880a49d7f11335265547bb6

theorem cogModel_e49ef45bc00895aa806733529be5bfa0974fdd8effd524b41ade74139ddb9036 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 : Prop) (f1 : p1) (f11 : p11) (f12 : p12) (f13 : p13) (f19 : p19) (r0 : p6 → p12 → p15) (r1 : p19 → p4) (r2 : p0 → p12 → p19 → p14) (r3 : p13 → p19 → p0) (r4 : p11 → p10) (r5 : p9 → p2) (r6 : p7 → p9) (r7 : p8 → p7) (r8 : p10 → p12 → p19 → p17) (r9 : p1 → p16 → p18) (r10 : p1 → p8) (r11 : p5 → p11 → p3) : p2 := by
  have h8 : p8 := r10 f1
  have h7 : p7 := r7 h8
  have h9 : p9 := r6 h7
  have h2 : p2 := r5 h9
  exact h2
#print axioms cogModel_e49ef45bc00895aa806733529be5bfa0974fdd8effd524b41ade74139ddb9036

theorem cogModel_1a83c01e3d0be1ef9def7cf5ac08bdcdffab3d581fdca26285fc0e56f351b7af (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 : Prop) (f8 : p8) (f9 : p9) (f17 : p17) (r0 : p3 → p7) (r1 : p17 → p21 → p13) (r2 : p4 → p26 → p14) (r3 : p8 → p17 → p19) (r4 : p0 → p5 → p24) (r5 : p4 → p8 → p3) (r6 : p8 → p9 → p20) (r7 : p17 → p18 → p5) (r8 : p2 → p17 → p10) (r9 : p9 → p20 → p23) (r10 : p4 → p19 → p20 → p23) (r11 : p4 → p9 → p17 → p3) (r12 : p9 → p14 → p0) (r13 : p9 → p17 → p11) (r14 : p4 → p17 → p19 → p22) (r15 : p8 → p22 → p26) (r16 : p7 → p14 → p26 → p5) (r17 : p1 → p8 → p12) (r18 : p17 → p4) (r19 : p8 → p9 → p25 → p21) (r20 : p6 → p9 → p15) (r21 : p8 → p17 → p25) (r22 : p7 → p17 → p14) (r23 : p4 → p7 → p26 → p18) (r24 : p9 → p16) (r25 : p8 → p18 → p0) : p24 := by
  have h4 : p4 := r18 f17
  have h3 : p3 := r11 h4 f9 f17
  have h7 : p7 := r0 h3
  have h14 : p14 := r22 h7 f17
  have h19 : p19 := r3 f8 f17
  have h22 : p22 := r14 h4 f17 h19
  have h0 : p0 := r12 f9 h14
  have h26 : p26 := r15 f8 h22
  have h5 : p5 := r16 h7 h14 h26
  have h24 : p24 := r4 h0 h5
  exact h24
#print axioms cogModel_1a83c01e3d0be1ef9def7cf5ac08bdcdffab3d581fdca26285fc0e56f351b7af

theorem cogModel_87ee93134e084952145d7e67fb6bee945026de63865f4f1464525f1aff56ab30 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 : Prop) (f13 : p13) (f14 : p14) (f23 : p23) (f27 : p27) (r0 : p7 → p23 → p10) (r1 : p7 → p27 → p0) (r2 : p14 → p17 → p23 → p16) (r3 : p10 → p27 → p8) (r4 : p13 → p14 → p7) (r5 : p1 → p13 → p18) (r6 : p14 → p20 → p23 → p22) (r7 : p4 → p10 → p19) (r8 : p0 → p14 → p12) (r9 : p6 → p13 → p19) (r10 : p14 → p27 → p11) (r11 : p0 → p13 → p21) (r12 : p10 → p13 → p21) (r13 : p13 → p21 → p4) (r14 : p0 → p14 → p8) (r15 : p12 → p13 → p4) (r16 : p13 → p14 → p23 → p9) (r17 : p2 → p14 → p0) (r18 : p26 → p27 → p5) (r19 : p6 → p27 → p15) (r20 : p3 → p14 → p24) (r21 : p15 → p19 → p25) (r22 : p14 → p27 → p17) (r23 : p23 → p26) (r24 : p7 → p27 → p10) (r25 : p0 → p10 → p12) (r26 : p8 → p13 → p6) (r27 : p4 → p13 → p15) (r28 : p13 → p23 → p27 → p7) (r29 : p14 → p27 → p2) (r30 : p14 → p20) : p25 := by
  have h7 : p7 := r28 f13 f23 f27
  have h0 : p0 := r1 h7 f27
  have h8 : p8 := r14 h0 f14
  have h12 : p12 := r8 h0 f14
  have h21 : p21 := r11 h0 f13
  have h4 : p4 := r15 h12 f13
  have h6 : p6 := r26 h8 f13
  have h15 : p15 := r27 h4 f13
  have h19 : p19 := r9 h6 f13
  have h25 : p25 := r21 h15 h19
  exact h25
#print axioms cogModel_87ee93134e084952145d7e67fb6bee945026de63865f4f1464525f1aff56ab30

theorem cogModel_f2df68b1f2192a68af8bf96b38e6fc4e2665f7223bb3437fd1f09343b66ed084 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 : Prop) (f0 : p0) (f10 : p10) (f25 : p25) (r0 : p10 → p13 → p23 → p30) (r1 : p13 → p23 → p20) (r2 : p1 → p5 → p10 → p9) (r3 : p10 → p20 → p25 → p21) (r4 : p0 → p25 → p11) (r5 : p17 → p25 → p22) (r6 : p10 → p25 → p5) (r7 : p13 → p16 → p17 → p28) (r8 : p5 → p1) (r9 : p0 → p10 → p6) (r10 : p25 → p30 → p17) (r11 : p0 → p10 → p25 → p13) (r12 : p10 → p26 → p3) (r13 : p21 → p28 → p12) (r14 : p23 → p28 → p14) (r15 : p18 → p25 → p15) (r16 : p2 → p25 → p19) (r17 : p24 → p25 → p4) (r18 : p27 → p29 → p30 → p16) (r19 : p12 → p14 → p8) (r20 : p0 → p10 → p29) (r21 : p10 → p11 → p25 → p7) (r22 : p13 → p29 → p27) (r23 : p0 → p25 → p23) : p8 := by
  have h23 : p23 := r23 f0 f25
  have h13 : p13 := r11 f0 f10 f25
  have h20 : p20 := r1 h13 h23
  have h21 : p21 := r3 f10 h20 f25
  have h29 : p29 := r20 f0 f10
  have h27 : p27 := r22 h13 h29
  have h30 : p30 := r0 f10 h13 h23
  have h16 : p16 := r18 h27 h29 h30
  have h17 : p17 := r10 f25 h30
  have h28 : p28 := r7 h13 h16 h17
  have h12 : p12 := r13 h21 h28
  have h14 : p14 := r14 h23 h28
  have h8 : p8 := r19 h12 h14
  exact h8
#print axioms cogModel_f2df68b1f2192a68af8bf96b38e6fc4e2665f7223bb3437fd1f09343b66ed084

theorem cogModel_fe613eaa64e74d76cf601cfe4f0c442a4d2c8032252e1639e5ec258f711f18bd (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 : Prop) (f6 : p6) (f7 : p7) (f8 : p8) (f16 : p16) (f17 : p17) (r0 : p7 → p5) (r1 : p4 → p18) (r2 : p2 → p7 → p9) (r3 : p13 → p16 → p3) (r4 : p1 → p13 → p14 → p0) (r5 : p18 → p15) (r6 : p14 → p1) (r7 : p7 → p12) (r8 : p6 → p13) (r9 : p8 → p13 → p14) (r10 : p1 → p3 → p14 → p19) (r11 : p10 → p16 → p11) (r12 : p5 → p4) : p15 := by
  have h5 : p5 := r0 f7
  have h4 : p4 := r12 h5
  have h18 : p18 := r1 h4
  have h15 : p15 := r5 h18
  exact h15
#print axioms cogModel_fe613eaa64e74d76cf601cfe4f0c442a4d2c8032252e1639e5ec258f711f18bd

theorem cogModel_45f2f2f665c51a02ebf50688736b0b9c24abd013655d92ae9aacd2408ebfa581 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 : Prop) (f2 : p2) (f10 : p10) (f12 : p12) (r0 : p10 → p15) (r1 : p2 → p7 → p12 → p14) (r2 : p4 → p10 → p12 → p18) (r3 : p0 → p2 → p14 → p11) (r4 : p2 → p0) (r5 : p2 → p13 → p17) (r6 : p9 → p10 → p12 → p7) (r7 : p2 → p10 → p12 → p9) (r8 : p15 → p19) (r9 : p12 → p6) (r10 : p6 → p7 → p9 → p4) (r11 : p19 → p1) (r12 : p5 → p12 → p16) (r13 : p3 → p10 → p8) : p1 := by
  have h15 : p15 := r0 f10
  have h19 : p19 := r8 h15
  have h1 : p1 := r11 h19
  exact h1
#print axioms cogModel_45f2f2f665c51a02ebf50688736b0b9c24abd013655d92ae9aacd2408ebfa581

theorem cogModel_bcf2164c71fc699d8b008d161ddb675a98b33a5e21fc02fe72f3c7478e9e37ad (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 : Prop) (f12 : p12) (f13 : p13) (f18 : p18) (r0 : p16 → p17 → p27) (r1 : p9 → p17 → p5) (r2 : p10 → p18 → p11) (r3 : p9 → p18 → p16) (r4 : p0 → p9 → p7) (r5 : p12 → p13 → p18 → p9) (r6 : p10 → p28) (r7 : p13 → p25 → p3) (r8 : p12 → p13 → p10) (r9 : p10 → p21 → p28 → p8) (r10 : p13 → p19 → p22) (r11 : p0 → p14 → p15) (r12 : p11 → p12 → p18 → p20) (r13 : p5 → p24 → p14) (r14 : p12 → p18 → p4) (r15 : p13 → p24 → p1) (r16 : p12 → p24) (r17 : p11 → p12 → p20 → p23) (r18 : p7 → p15 → p6) (r19 : p5 → p13 → p0) (r20 : p10 → p12 → p18 → p21) (r21 : p13 → p26 → p2) (r22 : p9 → p24 → p17) : p6 := by
  have h9 : p9 := r5 f12 f13 f18
  have h24 : p24 := r16 f12
  have h17 : p17 := r22 h9 h24
  have h5 : p5 := r1 h9 h17
  have h14 : p14 := r13 h5 h24
  have h0 : p0 := r19 h5 f13
  have h15 : p15 := r11 h0 h14
  have h7 : p7 := r4 h0 h9
  have h6 : p6 := r18 h7 h15
  exact h6
#print axioms cogModel_bcf2164c71fc699d8b008d161ddb675a98b33a5e21fc02fe72f3c7478e9e37ad

theorem cogModel_c32094c1edf006c58a787d3aeab46facdd1bbffed247e78ec90a865e498f346b (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 : Prop) (f2 : p2) (f12 : p12) (f13 : p13) (f19 : p19) (f20 : p20) (r0 : p3 → p12 → p19 → p28) (r1 : p2 → p20 → p21 → p27) (r2 : p5 → p12 → p15 → p7) (r3 : p9 → p20 → p25) (r4 : p2 → p19 → p20 → p6) (r5 : p7 → p0) (r6 : p0 → p11) (r7 : p3 → p22 → p18) (r8 : p13 → p19 → p20 → p1) (r9 : p12 → p26) (r10 : p1 → p3 → p4) (r11 : p20 → p21 → p22) (r12 : p26 → p5) (r13 : p16 → p20 → p8) (r14 : p12 → p21 → p3) (r15 : p1 → p12 → p29) (r16 : p2 → p13 → p19 → p15) (r17 : p1 → p21) (r18 : p1 → p20 → p23) (r19 : p11 → p13 → p10) (r20 : p24 → p17) (r21 : p4 → p18 → p28 → p14) (r22 : p5 → p24) : p14 := by
  have h1 : p1 := r8 f13 f19 f20
  have h21 : p21 := r17 h1
  have h22 : p22 := r11 f20 h21
  have h3 : p3 := r14 f12 h21
  have h18 : p18 := r7 h3 h22
  have h4 : p4 := r10 h1 h3
  have h28 : p28 := r0 h3 f12 f19
  have h14 : p14 := r21 h4 h18 h28
  exact h14
#print axioms cogModel_c32094c1edf006c58a787d3aeab46facdd1bbffed247e78ec90a865e498f346b

theorem cogModel_aae8597be1c2fae45a870b772a78a4c81acaeb5fc11b0e1cbd0139e38d967258 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 : Prop) (f4 : p4) (f10 : p10) (f22 : p22) (r0 : p14 → p16) (r1 : p6 → p16 → p22 → p1) (r2 : p4 → p15 → p19) (r3 : p4 → p10 → p28) (r4 : p10 → p26 → p14) (r5 : p8 → p28 → p15) (r6 : p8 → p15 → p22 → p17) (r7 : p4 → p22 → p11) (r8 : p10 → p7) (r9 : p4 → p22 → p8) (r10 : p12 → p28 → p13) (r11 : p10 → p20 → p25) (r12 : p13 → p17 → p19 → p24) (r13 : p0 → p4 → p5) (r14 : p4 → p9) (r15 : p10 → p22 → p26) (r16 : p21 → p23 → p6) (r17 : p10 → p28 → p12) (r18 : p10 → p14 → p16 → p27) (r19 : p26 → p23) (r20 : p10 → p21) (r21 : p11 → p27 → p2) (r22 : p10 → p18 → p3) : p24 := by
  have h8 : p8 := r9 f4 f22
  have h28 : p28 := r3 f4 f10
  have h12 : p12 := r17 f10 h28
  have h15 : p15 := r5 h8 h28
  have h13 : p13 := r10 h12 h28
  have h17 : p17 := r6 h8 h15 f22
  have h19 : p19 := r2 f4 h15
  have h24 : p24 := r12 h13 h17 h19
  exact h24
#print axioms cogModel_aae8597be1c2fae45a870b772a78a4c81acaeb5fc11b0e1cbd0139e38d967258

theorem cogModel_88a26aab1404ed4e731db0551524167c1c654a6fbb5c02f5739c7a033c043b77 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 : Prop) (f6 : p6) (f14 : p14) (f15 : p15) (r0 : p1 → p12 → p20) (r1 : p15 → p16 → p8) (r2 : p1 → p2 → p6 → p12) (r3 : p14 → p1) (r4 : p1 → p15 → p2) (r5 : p12 → p7) (r6 : p6 → p11 → p5) (r7 : p6 → p15 → p16) (r8 : p15 → p9) (r9 : p14 → p21 → p22) (r10 : p15 → p23 → p0) (r11 : p6 → p19 → p17) (r12 : p10 → p14 → p18) (r13 : p12 → p15 → p13) (r14 : p6 → p14 → p23) (r15 : p6 → p14 → p9) (r16 : p2 → p6 → p21 → p3) (r17 : p0 → p8 → p4) (r18 : p6 → p23 → p8) (r19 : p1 → p15 → p21) : p4 := by
  have h16 : p16 := r7 f6 f15
  have h23 : p23 := r14 f6 f14
  have h8 : p8 := r1 f15 h16
  have h0 : p0 := r10 f15 h23
  have h4 : p4 := r17 h0 h8
  exact h4
#print axioms cogModel_88a26aab1404ed4e731db0551524167c1c654a6fbb5c02f5739c7a033c043b77

theorem cogModel_836920ef09907617154c03c9a408c4c2cc3b3d8d0073aaef7fb2f0dc64c96435 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 : Prop) (f15 : p15) (f17 : p17) (f18 : p18) (f20 : p20) (f26 : p26) (r0 : p17 → p26 → p2) (r1 : p11 → p15 → p4) (r2 : p1 → p18 → p26 → p6) (r3 : p17 → p26 → p19) (r4 : p18 → p23 → p27) (r5 : p15 → p21) (r6 : p16 → p24) (r7 : p18 → p8) (r8 : p9 → p26 → p5) (r9 : p10 → p16) (r10 : p6 → p17 → p19 → p22) (r11 : p8 → p10) (r12 : p15 → p18 → p1) (r13 : p12 → p7) (r14 : p24 → p12) (r15 : p2 → p15 → p17 → p25) (r16 : p26 → p14) (r17 : p6 → p15 → p0) (r18 : p13 → p20 → p3) : p7 := by
  have h8 : p8 := r7 f18
  have h10 : p10 := r11 h8
  have h16 : p16 := r9 h10
  have h24 : p24 := r6 h16
  have h12 : p12 := r14 h24
  have h7 : p7 := r13 h12
  exact h7
#print axioms cogModel_836920ef09907617154c03c9a408c4c2cc3b3d8d0073aaef7fb2f0dc64c96435

theorem cogModel_398dcde6824cf01b5e9db1fdb7acd5b7e0608c70892d4b754b9cc902a2a3d43a (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 : Prop) (f10 : p10) (f13 : p13) (f16 : p16) (f22 : p22) (f24 : p24) (r0 : p9 → p13 → p24 → p20) (r1 : p13 → p24 → p19) (r2 : p10 → p22 → p24 → p8) (r3 : p2 → p24 → p23) (r4 : p10 → p13 → p16 → p9) (r5 : p19 → p22 → p24 → p0) (r6 : p15 → p16 → p12) (r7 : p1 → p8 → p16 → p5) (r8 : p5 → p7 → p8 → p14) (r9 : p1 → p24 → p7) (r10 : p5 → p10 → p17) (r11 : p13 → p22 → p1) (r12 : p4 → p22 → p3) (r13 : p6 → p13 → p21) (r14 : p14 → p17 → p11) (r15 : p0 → p16 → p20 → p18) : p11 := by
  have h8 : p8 := r2 f10 f22 f24
  have h1 : p1 := r11 f13 f22
  have h7 : p7 := r9 h1 f24
  have h5 : p5 := r7 h1 h8 f16
  have h17 : p17 := r10 h5 f10
  have h14 : p14 := r8 h5 h7 h8
  have h11 : p11 := r14 h14 h17
  exact h11
#print axioms cogModel_398dcde6824cf01b5e9db1fdb7acd5b7e0608c70892d4b754b9cc902a2a3d43a

theorem cogModel_5124c1cb4c2dd6e81a2eed666c8bac79f5cdc351375573f8871c8652794aaec6 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 : Prop) (f2 : p2) (f10 : p10) (f19 : p19) (r0 : p10 → p19 → p18) (r1 : p2 → p16 → p12) (r2 : p22 → p24 → p9) (r3 : p10 → p18 → p19 → p6) (r4 : p19 → p22 → p24) (r5 : p8 → p14 → p7) (r6 : p19 → p22 → p15) (r7 : p2 → p10 → p19 → p22) (r8 : p22 → p29 → p4) (r9 : p10 → p19 → p22 → p24) (r10 : p14 → p22 → p29) (r11 : p1 → p4 → p7 → p13) (r12 : p6 → p28 → p27) (r13 : p10 → p14 → p8) (r14 : p14 → p26 → p8) (r15 : p6 → p10 → p21) (r16 : p2 → p15 → p14) (r17 : p21 → p0) (r18 : p18 → p25) (r19 : p15 → p24 → p14) (r20 : p9 → p19 → p29) (r21 : p2 → p10 → p26) (r22 : p8 → p24 → p1) (r23 : p2 → p8 → p1) (r24 : p10 → p23 → p5) (r25 : p21 → p25 → p28 → p11) (r26 : p18 → p21 → p17) (r27 : p2 → p19 → p22) (r28 : p18 → p28) (r29 : p19 → p20 → p3) : p13 := by
  have h26 : p26 := r21 f2 f10
  have h22 : p22 := r7 f2 f10 f19
  have h15 : p15 := r6 f19 h22
  have h24 : p24 := r9 f10 f19 h22
  have h9 : p9 := r2 h22 h24
  have h29 : p29 := r20 h9 f19
  have h4 : p4 := r8 h22 h29
  have h14 : p14 := r19 h15 h24
  have h8 : p8 := r14 h14 h26
  have h7 : p7 := r5 h8 h14
  have h1 : p1 := r22 h8 h24
  have h13 : p13 := r11 h1 h4 h7
  exact h13
#print axioms cogModel_5124c1cb4c2dd6e81a2eed666c8bac79f5cdc351375573f8871c8652794aaec6

theorem cogModel_e5e6ffc66da0179eef5adf22e40e73153871bfd05b77afd1ccd13da986bbd078 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 : Prop) (f5 : p5) (f7 : p7) (f9 : p9) (f20 : p20) (f25 : p25) (r0 : p9 → p14 → p20 → p0) (r1 : p9 → p12) (r2 : p4 → p18 → p16) (r3 : p15 → p21 → p14) (r4 : p10 → p20 → p2) (r5 : p16 → p24 → p27 → p1) (r6 : p7 → p23 → p15) (r7 : p9 → p22) (r8 : p5 → p9 → p18) (r9 : p4 → p18 → p24) (r10 : p7 → p9 → p20 → p21) (r11 : p0 → p21 → p26 → p17) (r12 : p11 → p25 → p3) (r13 : p7 → p8 → p13) (r14 : p5 → p9 → p6) (r15 : p19 → p27) (r16 : p20 → p25 → p19) (r17 : p20 → p25 → p26) (r18 : p7 → p25 → p4) (r19 : p20 → p25 → p23) : p1 := by
  have h19 : p19 := r16 f20 f25
  have h18 : p18 := r8 f5 f9
  have h27 : p27 := r15 h19
  have h4 : p4 := r18 f7 f25
  have h16 : p16 := r2 h4 h18
  have h24 : p24 := r9 h4 h18
  have h1 : p1 := r5 h16 h24 h27
  exact h1
#print axioms cogModel_e5e6ffc66da0179eef5adf22e40e73153871bfd05b77afd1ccd13da986bbd078

theorem cogModel_c646e13a59d24f7d543632d4bdadf30da0a62c9690e370d33c2237f505ef107d (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 : Prop) (f1 : p1) (f2 : p2) (f10 : p10) (f14 : p14) (r0 : p8 → p4) (r1 : p14 → p15) (r2 : p14 → p19) (r3 : p1 → p2 → p10 → p9) (r4 : p8 → p10 → p14 → p25) (r5 : p12 → p7) (r6 : p14 → p24 → p11) (r7 : p14 → p19 → p25 → p0) (r8 : p2 → p8) (r9 : p14 → p20 → p17) (r10 : p4 → p13) (r11 : p16 → p18) (r12 : p2 → p14 → p15 → p3) (r13 : p18 → p12) (r14 : p7 → p23) (r15 : p5 → p10 → p22) (r16 : p1 → p21 → p6) (r17 : p14 → p16) : p23 := by
  have h16 : p16 := r17 f14
  have h18 : p18 := r11 h16
  have h12 : p12 := r13 h18
  have h7 : p7 := r5 h12
  have h23 : p23 := r14 h7
  exact h23
#print axioms cogModel_c646e13a59d24f7d543632d4bdadf30da0a62c9690e370d33c2237f505ef107d

theorem cogModel_fd6d21e756102160273ed586bc83892ec2015f296e0faa9ed0ff0a6ee1ae6a97 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 : Prop) (f2 : p2) (f6 : p6) (f11 : p11) (f17 : p17) (f24 : p24) (r0 : p8 → p15 → p21) (r1 : p6 → p24 → p14) (r2 : p2 → p17 → p8) (r3 : p6 → p11 → p17 → p12) (r4 : p2 → p11 → p15 → p0) (r5 : p6 → p21 → p13) (r6 : p12 → p10) (r7 : p2 → p16) (r8 : p21 → p18) (r9 : p6 → p19) (r10 : p2 → p11 → p17 → p1) (r11 : p13 → p18 → p5) (r12 : p1 → p10 → p4) (r13 : p6 → p22 → p26) (r14 : p17 → p25 → p23) (r15 : p11 → p17 → p15) (r16 : p2 → p9 → p3) (r17 : p17 → p7) (r18 : p1 → p11 → p20) : p5 := by
  have h8 : p8 := r2 f2 f17
  have h15 : p15 := r15 f11 f17
  have h21 : p21 := r0 h8 h15
  have h18 : p18 := r8 h21
  have h13 : p13 := r5 f6 h21
  have h5 : p5 := r11 h13 h18
  exact h5
#print axioms cogModel_fd6d21e756102160273ed586bc83892ec2015f296e0faa9ed0ff0a6ee1ae6a97

theorem cogModel_387a7418b325a7647eade3ccb4e7165fc513ff26b69da9a192712c62b559ed9e (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 : Prop) (f0 : p0) (f2 : p2) (f6 : p6) (f7 : p7) (f18 : p18) (r0 : p5 → p7 → p3) (r1 : p15 → p1) (r2 : p2 → p6 → p10) (r3 : p0 → p9) (r4 : p1 → p8) (r5 : p14 → p16) (r6 : p7 → p19 → p12) (r7 : p4 → p20) (r8 : p13 → p11) (r9 : p8 → p4) (r10 : p14 → p17 → p13) (r11 : p18 → p15) (r12 : p10 → p14) (r13 : p2 → p6 → p18 → p17) : p20 := by
  have h10 : p10 := r2 f2 f6
  have h15 : p15 := r11 f18
  have h1 : p1 := r1 h15
  have h8 : p8 := r4 h1
  have h4 : p4 := r9 h8
  have h20 : p20 := r7 h4
  exact h20
#print axioms cogModel_387a7418b325a7647eade3ccb4e7165fc513ff26b69da9a192712c62b559ed9e

theorem cogModel_1b172b533d318a1d83a5cd1ec24225119fc0afc090ccce1f1a3eb13dcbe7f763 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 : Prop) (f4 : p4) (f6 : p6) (f9 : p9) (f11 : p11) (f19 : p19) (r0 : p7 → p15) (r1 : p18 → p19 → p13) (r2 : p11 → p7) (r3 : p5 → p12) (r4 : p6 → p19 → p2) (r5 : p12 → p17) (r6 : p1 → p11 → p8) (r7 : p17 → p10) (r8 : p9 → p11 → p19 → p1) (r9 : p15 → p5) (r10 : p0 → p16) (r11 : p4 → p11 → p19 → p0) (r12 : p0 → p1 → p4 → p20) (r13 : p3 → p6 → p14) : p10 := by
  have h7 : p7 := r2 f11
  have h15 : p15 := r0 h7
  have h5 : p5 := r9 h15
  have h12 : p12 := r3 h5
  have h17 : p17 := r5 h12
  have h10 : p10 := r7 h17
  exact h10
#print axioms cogModel_1b172b533d318a1d83a5cd1ec24225119fc0afc090ccce1f1a3eb13dcbe7f763

theorem cogModel_6072496de7ce8d0a4d81bb8b1df7cfdf4fc1efc13919a02f495bb6a98fdc75bc (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 : Prop) (f1 : p1) (f6 : p6) (f10 : p10) (f13 : p13) (f27 : p27) (r0 : p27 → p28 → p12) (r1 : p7 → p27 → p3) (r2 : p1 → p13 → p15 → p9) (r3 : p7 → p13 → p15 → p28) (r4 : p12 → p14 → p25 → p18) (r5 : p3 → p27 → p14) (r6 : p10 → p20 → p17) (r7 : p10 → p29 → p4) (r8 : p1 → p28 → p25) (r9 : p5 → p27 → p26) (r10 : p27 → p2) (r11 : p6 → p27 → p15) (r12 : p6 → p13 → p23) (r13 : p8 → p13 → p24) (r14 : p1 → p6 → p16 → p22) (r15 : p10 → p13 → p19) (r16 : p1 → p10 → p27 → p21) (r17 : p2 → p10 → p7) (r18 : p10 → p13 → p16) (r19 : p13 → p19 → p0) (r20 : p13 → p16 → p27 → p11) : p18 := by
  have h15 : p15 := r11 f6 f27
  have h2 : p2 := r10 f27
  have h7 : p7 := r17 h2 f10
  have h3 : p3 := r1 h7 f27
  have h28 : p28 := r3 h7 f13 h15
  have h14 : p14 := r5 h3 f27
  have h12 : p12 := r0 f27 h28
  have h25 : p25 := r8 f1 h28
  have h18 : p18 := r4 h12 h14 h25
  exact h18
#print axioms cogModel_6072496de7ce8d0a4d81bb8b1df7cfdf4fc1efc13919a02f495bb6a98fdc75bc

theorem cogModel_d9415d50ee0995353bda875c1b46c7c4813c7fa64a8779d2e1371c9bd36efb06 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 : Prop) (f9 : p9) (f13 : p13) (f17 : p17) (r0 : p19 → p20) (r1 : p13 → p18 → p1) (r2 : p2 → p4 → p11) (r3 : p2 → p17 → p4) (r4 : p11 → p13 → p14 → p8) (r5 : p4 → p11 → p21 → p0) (r6 : p13 → p7) (r7 : p7 → p5) (r8 : p14 → p12) (r9 : p13 → p17 → p2) (r10 : p10 → p19) (r11 : p13 → p14) (r12 : p5 → p10) (r13 : p2 → p11 → p17 → p21) (r14 : p11 → p3) (r15 : p20 → p6) (r16 : p9 → p16 → p15) : p6 := by
  have h2 : p2 := r9 f13 f17
  have h7 : p7 := r6 f13
  have h5 : p5 := r7 h7
  have h10 : p10 := r12 h5
  have h19 : p19 := r10 h10
  have h20 : p20 := r0 h19
  have h6 : p6 := r15 h20
  exact h6
#print axioms cogModel_d9415d50ee0995353bda875c1b46c7c4813c7fa64a8779d2e1371c9bd36efb06

theorem cogModel_556fcb1ec024138edbe4a8eaea4300c7363c14b1e7b450a8945c508acf07dd50 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 : Prop) (f1 : p1) (f15 : p15) (f28 : p28) (r0 : p1 → p17 → p20) (r1 : p4 → p18 → p23) (r2 : p2 → p10 → p7) (r3 : p11 → p21) (r4 : p1 → p12 → p9) (r5 : p17 → p24 → p28 → p27) (r6 : p1 → p26 → p25) (r7 : p1 → p15 → p28 → p4) (r8 : p8 → p21 → p28 → p13) (r9 : p11 → p16 → p21 → p0) (r10 : p1 → p20 → p5) (r11 : p15 → p18) (r12 : p15 → p28 → p17) (r13 : p1 → p23 → p16) (r14 : p22 → p28 → p10) (r15 : p1 → p6 → p3) (r16 : p5 → p22 → p2) (r17 : p15 → p28 → p8) (r18 : p8 → p15 → p11) (r19 : p1 → p28 → p19) (r20 : p17 → p28 → p14) (r21 : p20 → p24 → p22) (r22 : p17 → p19 → p24) : p7 := by
  have h19 : p19 := r19 f1 f28
  have h17 : p17 := r12 f15 f28
  have h20 : p20 := r0 f1 h17
  have h5 : p5 := r10 f1 h20
  have h24 : p24 := r22 h17 h19
  have h22 : p22 := r21 h20 h24
  have h2 : p2 := r16 h5 h22
  have h10 : p10 := r14 h22 f28
  have h7 : p7 := r2 h2 h10
  exact h7
#print axioms cogModel_556fcb1ec024138edbe4a8eaea4300c7363c14b1e7b450a8945c508acf07dd50

theorem cogModel_e0d97c3bc63e070e85f0ac960b1ed6fdb71dfe4e52cee6044743f97ac3662ea0 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 : Prop) (f4 : p4) (f5 : p5) (f7 : p7) (f8 : p8) (f14 : p14) (r0 : p2 → p15) (r1 : p15 → p1) (r2 : p8 → p2) (r3 : p6 → p8 → p11) (r4 : p7 → p10 → p14 → p18) (r5 : p4 → p12) (r6 : p0 → p7 → p9) (r7 : p4 → p10) (r8 : p7 → p16 → p3) (r9 : p8 → p10 → p12 → p17) (r10 : p10 → p13) : p1 := by
  have h2 : p2 := r2 f8
  have h15 : p15 := r0 h2
  have h1 : p1 := r1 h15
  exact h1
#print axioms cogModel_e0d97c3bc63e070e85f0ac960b1ed6fdb71dfe4e52cee6044743f97ac3662ea0

theorem cogModel_eb7f719df86c572599c1c2d868ce758f01e6e2bea64e2c66ae48e19eb14d499f (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 : Prop) (f3 : p3) (f5 : p5) (f13 : p13) (r0 : p2 → p13 → p0) (r1 : p4 → p16 → p11) (r2 : p5 → p7 → p16 → p12) (r3 : p4 → p7) (r4 : p14 → p9) (r5 : p3 → p7 → p8) (r6 : p5 → p14) (r7 : p9 → p10) (r8 : p3 → p17 → p6) (r9 : p3 → p5 → p13 → p4) (r10 : p3 → p4 → p16) (r11 : p12 → p13 → p1) (r12 : p5 → p15) : p10 := by
  have h14 : p14 := r6 f5
  have h9 : p9 := r4 h14
  have h10 : p10 := r7 h9
  exact h10
#print axioms cogModel_eb7f719df86c572599c1c2d868ce758f01e6e2bea64e2c66ae48e19eb14d499f

theorem cogModel_0101ef2a021a7ee46b2bc7e4d1a6a790313f778ec5db47666abb47c8c1f6e894 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 : Prop) (f8 : p8) (f16 : p16) (f20 : p20) (r0 : p16 → p11) (r1 : p0 → p8 → p15 → p17) (r2 : p2 → p12 → p19) (r3 : p16 → p14) (r4 : p0 → p15) (r5 : p11 → p16 → p2) (r6 : p4 → p20 → p21) (r7 : p8 → p20 → p5) (r8 : p8 → p16 → p20 → p0) (r9 : p5 → p11 → p16 → p2) (r10 : p8 → p16 → p20 → p11) (r11 : p6 → p16 → p9) (r12 : p0 → p1) (r13 : p1 → p3) (r14 : p11 → p20 → p12) (r15 : p11 → p16 → p12) (r16 : p13 → p20 → p18) (r17 : p8 → p22 → p10) (r18 : p1 → p7) : p19 := by
  have h5 : p5 := r7 f8 f20
  have h11 : p11 := r10 f8 f16 f20
  have h2 : p2 := r5 h11 f16
  have h12 : p12 := r14 h11 f20
  have h19 : p19 := r2 h2 h12
  exact h19
#print axioms cogModel_0101ef2a021a7ee46b2bc7e4d1a6a790313f778ec5db47666abb47c8c1f6e894

theorem cogModel_e511c8afebafba979279f84fa9019c90580ba6a8b49136f071953fdfe81e28d7 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 : Prop) (f1 : p1) (f9 : p9) (f13 : p13) (f14 : p14) (f23 : p23) (r0 : p23 → p0) (r1 : p14 → p23 → p6) (r2 : p6 → p9 → p13 → p16) (r3 : p15 → p3) (r4 : p1 → p9 → p15 → p17) (r5 : p0 → p8) (r6 : p17 → p22) (r7 : p12 → p14 → p20) (r8 : p18 → p19) (r9 : p5 → p14 → p10) (r10 : p1 → p7 → p2) (r11 : p17 → p4) (r12 : p8 → p18) (r13 : p17 → p11) (r14 : p1 → p4 → p23 → p21) (r15 : p1 → p9 → p14 → p15) : p19 := by
  have h0 : p0 := r0 f23
  have h8 : p8 := r5 h0
  have h18 : p18 := r12 h8
  have h19 : p19 := r8 h18
  exact h19
#print axioms cogModel_e511c8afebafba979279f84fa9019c90580ba6a8b49136f071953fdfe81e28d7

theorem cogModel_f010e3891f9bece254f95a14f6ced5a194a847d60e85a6368a5157943b7a393d (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 : Prop) (f0 : p0) (f10 : p10) (f12 : p12) (f31 : p31) (r0 : p8 → p11 → p18) (r1 : p20 → p32) (r2 : p4 → p10 → p31 → p6) (r3 : p12 → p22 → p14) (r4 : p33 → p2) (r5 : p10 → p28 → p5) (r6 : p10 → p19 → p32 → p27) (r7 : p12 → p26 → p15) (r8 : p12 → p16 → p34 → p8) (r9 : p12 → p31 → p21) (r10 : p2 → p10 → p33 → p29) (r11 : p10 → p30 → p7) (r12 : p12 → p23 → p35) (r13 : p20 → p24) (r14 : p0 → p10 → p12 → p13) (r15 : p0 → p10 → p12 → p25) (r16 : p2 → p26 → p29 → p11) (r17 : p0 → p26) (r18 : p12 → p13 → p31 → p3) (r19 : p0 → p12 → p31 → p20) (r20 : p0 → p2 → p31 → p16) (r21 : p1 → p12 → p31 → p17) (r22 : p10 → p25 → p4) (r23 : p0 → p26 → p31 → p33) (r24 : p3 → p26 → p31 → p34) (r25 : p19 → p9) (r26 : p12 → p30) (r27 : p10 → p20 → p31 → p1) (r28 : p24 → p30 → p19) : p18 := by
  have h26 : p26 := r17 f0
  have h33 : p33 := r23 f0 h26 f31
  have h2 : p2 := r4 h33
  have h16 : p16 := r20 f0 h2 f31
  have h29 : p29 := r10 h2 f10 h33
  have h11 : p11 := r16 h2 h26 h29
  have h13 : p13 := r14 f0 f10 f12
  have h3 : p3 := r18 f12 h13 f31
  have h34 : p34 := r24 h3 h26 f31
  have h8 : p8 := r8 f12 h16 h34
  have h18 : p18 := r0 h8 h11
  exact h18
#print axioms cogModel_f010e3891f9bece254f95a14f6ced5a194a847d60e85a6368a5157943b7a393d

theorem cogModel_dfd3005fbedccb3b3ea946cffed5ee640ccda2ed32ec943bef91594e052d47e8 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 : Prop) (f2 : p2) (f12 : p12) (f23 : p23) (f24 : p24) (r0 : p2 → p24 → p27) (r1 : p5 → p24 → p26) (r2 : p12 → p23 → p17) (r3 : p6 → p20 → p21) (r4 : p3 → p12 → p13) (r5 : p2 → p11 → p24 → p1) (r6 : p12 → p25) (r7 : p2 → p23 → p20) (r8 : p4 → p12 → p14) (r9 : p23 → p18) (r10 : p12 → p20 → p27 → p6) (r11 : p7 → p15) (r12 : p2 → p12 → p20) (r13 : p12 → p11) (r14 : p11 → p12 → p1) (r15 : p1 → p23 → p21) (r16 : p6 → p23 → p22) (r17 : p12 → p15 → p17 → p8) (r18 : p24 → p19) (r19 : p12 → p18 → p24 → p7) (r20 : p23 → p24 → p27) (r21 : p21 → p22 → p10) (r22 : p7 → p0) (r23 : p9 → p23 → p16) (r24 : p11 → p23 → p6) : p10 := by
  have h20 : p20 := r7 f2 f23
  have h27 : p27 := r0 f2 f24
  have h11 : p11 := r13 f12
  have h1 : p1 := r14 h11 f12
  have h6 : p6 := r10 f12 h20 h27
  have h21 : p21 := r15 h1 f23
  have h22 : p22 := r16 h6 f23
  have h10 : p10 := r21 h21 h22
  exact h10
#print axioms cogModel_dfd3005fbedccb3b3ea946cffed5ee640ccda2ed32ec943bef91594e052d47e8

theorem cogModel_bc5297b9e8a287e26b878b40b4517cd6ffe0b01598d04d46f4994f2801f4639a (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 : Prop) (f7 : p7) (f13 : p13) (f21 : p21) (r0 : p6 → p7 → p23 → p22) (r1 : p7 → p13 → p21 → p6) (r2 : p4 → p6 → p13 → p3) (r3 : p0 → p15) (r4 : p7 → p24 → p18) (r5 : p13 → p21 → p23) (r6 : p7 → p13 → p22 → p9) (r7 : p7 → p13 → p19 → p24) (r8 : p9 → p13 → p27 → p26) (r9 : p7 → p22 → p27) (r10 : p12 → p28) (r11 : p19 → p24 → p20) (r12 : p7 → p14 → p16) (r13 : p3 → p10 → p17 → p8) (r14 : p21 → p25 → p10) (r15 : p9 → p11 → p22 → p4) (r16 : p5 → p21 → p1) (r17 : p21 → p12) (r18 : p7 → p21 → p29) (r19 : p7 → p12 → p21 → p0) (r20 : p22 → p29 → p2) (r21 : p21 → p23 → p29 → p11) (r22 : p7 → p13 → p21 → p19) (r23 : p9 → p25 → p27 → p17) (r24 : p11 → p27 → p25) : p8 := by
  have h6 : p6 := r1 f7 f13 f21
  have h23 : p23 := r5 f13 f21
  have h22 : p22 := r0 h6 f7 h23
  have h27 : p27 := r9 f7 h22
  have h9 : p9 := r6 f7 f13 h22
  have h29 : p29 := r18 f7 f21
  have h11 : p11 := r21 f21 h23 h29
  have h4 : p4 := r15 h9 h11 h22
  have h3 : p3 := r2 h4 h6 f13
  have h25 : p25 := r24 h11 h27
  have h10 : p10 := r14 f21 h25
  have h17 : p17 := r23 h9 h25 h27
  have h8 : p8 := r13 h3 h10 h17
  exact h8
#print axioms cogModel_bc5297b9e8a287e26b878b40b4517cd6ffe0b01598d04d46f4994f2801f4639a

theorem cogModel_3b67b9e2f0abe821ded04f9de51900912d359b14c78f3cadd55cedca40514065 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 : Prop) (f8 : p8) (f22 : p22) (f24 : p24) (f27 : p27) (f28 : p28) (r0 : p2 → p27 → p9) (r1 : p30 → p26) (r2 : p24 → p27 → p30 → p0) (r3 : p18 → p23 → p33 → p12) (r4 : p11 → p22 → p24 → p19) (r5 : p24 → p28 → p3) (r6 : p8 → p27 → p36 → p14) (r7 : p17 → p32 → p23) (r8 : p1 → p8 → p33) (r9 : p24 → p28 → p11) (r10 : p16 → p21 → p27 → p35) (r11 : p35 → p1) (r12 : p30 → p13) (r13 : p27 → p28 → p37) (r14 : p3 → p27 → p28 → p30) (r15 : p24 → p27 → p6) (r16 : p17 → p22 → p32) (r17 : p20 → p22 → p29) (r18 : p37 → p34) (r19 : p24 → p25 → p31) (r20 : p6 → p16) (r21 : p8 → p17 → p22 → p5) (r22 : p14 → p28 → p10) (r23 : p28 → p15) (r24 : p16 → p19 → p28 → p17) (r25 : p22 → p27 → p36) (r26 : p1 → p21 → p32 → p18) (r27 : p6 → p28 → p21) (r28 : p3 → p10 → p36 → p7) (r29 : p8 → p4) : p12 := by
  have h6 : p6 := r15 f24 f27
  have h21 : p21 := r27 h6 f28
  have h16 : p16 := r20 h6
  have h35 : p35 := r10 h16 h21 f27
  have h1 : p1 := r11 h35
  have h33 : p33 := r8 h1 f8
  have h11 : p11 := r9 f24 f28
  have h19 : p19 := r4 h11 f22 f24
  have h17 : p17 := r24 h16 h19 f28
  have h32 : p32 := r16 h17 f22
  have h23 : p23 := r7 h17 h32
  have h18 : p18 := r26 h1 h21 h32
  have h12 : p12 := r3 h18 h23 h33
  exact h12
#print axioms cogModel_3b67b9e2f0abe821ded04f9de51900912d359b14c78f3cadd55cedca40514065

theorem cogModel_021b71b220d26a398a21c4dcad24a54f8888b357410a6e63e8978c1e922665f8 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 : Prop) (f1 : p1) (f16 : p16) (f18 : p18) (r0 : p9 → p8) (r1 : p16 → p11) (r2 : p21 → p2) (r3 : p1 → p20 → p14) (r4 : p11 → p6) (r5 : p8 → p3) (r6 : p1 → p18 → p0) (r7 : p4 → p18 → p15) (r8 : p1 → p7 → p16 → p21) (r9 : p6 → p9) (r10 : p1 → p13 → p5) (r11 : p3 → p19) (r12 : p1 → p16 → p7) (r13 : p17 → p18 → p12) (r14 : p16 → p18 → p21 → p10) : p19 := by
  have h11 : p11 := r1 f16
  have h6 : p6 := r4 h11
  have h9 : p9 := r9 h6
  have h8 : p8 := r0 h9
  have h3 : p3 := r5 h8
  have h19 : p19 := r11 h3
  exact h19
#print axioms cogModel_021b71b220d26a398a21c4dcad24a54f8888b357410a6e63e8978c1e922665f8

theorem cogModel_efd11557839e5b3d946e0fc03c4cace2641f88756e215de293dee3554dba70e2 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 : Prop) (f2 : p2) (f14 : p14) (f16 : p16) (f19 : p19) (f20 : p20) (r0 : p16 → p10) (r1 : p3 → p5 → p12 → p22) (r2 : p14 → p21 → p18) (r3 : p19 → p9) (r4 : p12 → p19 → p20 → p5) (r5 : p12 → p23) (r6 : p7 → p18 → p1) (r7 : p9 → p3) (r8 : p2 → p9 → p16 → p15) (r9 : p19 → p17) (r10 : p9 → p15 → p8) (r11 : p4 → p20 → p6) (r12 : p13 → p16 → p0) (r13 : p17 → p11) (r14 : p14 → p19 → p20 → p21) (r15 : p10 → p19 → p21 → p7) (r16 : p2 → p16 → p19 → p24) (r17 : p19 → p20 → p12) : p1 := by
  have h10 : p10 := r0 f16
  have h21 : p21 := r14 f14 f19 f20
  have h18 : p18 := r2 f14 h21
  have h7 : p7 := r15 h10 f19 h21
  have h1 : p1 := r6 h7 h18
  exact h1
#print axioms cogModel_efd11557839e5b3d946e0fc03c4cace2641f88756e215de293dee3554dba70e2

theorem cogModel_d933c54dff8c8e9d0f00b86a9a4978d4ee5c45f584a64de3c2891a32a32a21f6 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 : Prop) (f5 : p5) (f10 : p10) (f24 : p24) (f26 : p26) (r0 : p6 → p15 → p23 → p18) (r1 : p1 → p15 → p26 → p9) (r2 : p5 → p20) (r3 : p26 → p27 → p3) (r4 : p22 → p32 → p33 → p4) (r5 : p5 → p20 → p30) (r6 : p10 → p25 → p29) (r7 : p1 → p23) (r8 : p28 → p13) (r9 : p8 → p2) (r10 : p12 → p17 → p22) (r11 : p5 → p30 → p16) (r12 : p15 → p24 → p6) (r13 : p5 → p24 → p31 → p17) (r14 : p10 → p20 → p24 → p31) (r15 : p16 → p17 → p32) (r16 : p14 → p24 → p21) (r17 : p24 → p34 → p33) (r18 : p0 → p24 → p19) (r19 : p15 → p26 → p1) (r20 : p24 → p8) (r21 : p5 → p26 → p15) (r22 : p7 → p10 → p11) (r23 : p1 → p6 → p25) (r24 : p24 → p31 → p34) (r25 : p5 → p26 → p12) (r26 : p6 → p26 → p28) : p4 := by
  have h12 : p12 := r25 f5 f26
  have h20 : p20 := r2 f5
  have h30 : p30 := r5 f5 h20
  have h31 : p31 := r14 f10 h20 f24
  have h16 : p16 := r11 f5 h30
  have h34 : p34 := r24 f24 h31
  have h33 : p33 := r17 f24 h34
  have h17 : p17 := r13 f5 f24 h31
  have h32 : p32 := r15 h16 h17
  have h22 : p22 := r10 h12 h17
  have h4 : p4 := r4 h22 h32 h33
  exact h4
#print axioms cogModel_d933c54dff8c8e9d0f00b86a9a4978d4ee5c45f584a64de3c2891a32a32a21f6

theorem cogModel_160748f4ca1fcc3dded2a6ce4feefc329000d0700c4b8aab3f45eeb73e045088 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 : Prop) (f5 : p5) (f7 : p7) (f8 : p8) (f14 : p14) (f20 : p20) (r0 : p2 → p4) (r1 : p7 → p21 → p2) (r2 : p5 → p7 → p17) (r3 : p5 → p7 → p20 → p19) (r4 : p19 → p18) (r5 : p17 → p20 → p12) (r6 : p18 → p6) (r7 : p7 → p14 → p20 → p15) (r8 : p5 → p11 → p0) (r9 : p16 → p17 → p9) (r10 : p5 → p22 → p13) (r11 : p14 → p3) (r12 : p18 → p19 → p21) (r13 : p5 → p16) (r14 : p9 → p12 → p10) (r15 : p6 → p7 → p1) : p10 := by
  have h16 : p16 := r13 f5
  have h17 : p17 := r2 f5 f7
  have h9 : p9 := r9 h16 h17
  have h12 : p12 := r5 h17 f20
  have h10 : p10 := r14 h9 h12
  exact h10
#print axioms cogModel_160748f4ca1fcc3dded2a6ce4feefc329000d0700c4b8aab3f45eeb73e045088

theorem cogModel_06f313b54425d73acfda8cc5f23e005102478d16379427a9f5512c00a0c332d8 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 : Prop) (f1 : p1) (f3 : p3) (f6 : p6) (f17 : p17) (r0 : p17 → p8) (r1 : p3 → p16 → p12) (r2 : p8 → p15) (r3 : p5 → p9) (r4 : p1 → p6 → p2) (r5 : p3 → p13 → p14) (r6 : p11 → p17 → p7) (r7 : p6 → p0) (r8 : p15 → p10) (r9 : p6 → p17 → p4) (r10 : p3 → p17 → p16) (r11 : p12 → p17 → p5) : p10 := by
  have h8 : p8 := r0 f17
  have h15 : p15 := r2 h8
  have h10 : p10 := r8 h15
  exact h10
#print axioms cogModel_06f313b54425d73acfda8cc5f23e005102478d16379427a9f5512c00a0c332d8

theorem cogModel_de78590ec9bc38fada908ab16f94631ee08294c4ba9334bd7e55cc5a882c79d3 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 : Prop) (f3 : p3) (f6 : p6) (f14 : p14) (f18 : p18) (f20 : p20) (r0 : p3 → p14 → p17 → p4) (r1 : p1 → p8 → p13 → p7) (r2 : p3 → p6 → p23) (r3 : p6 → p15 → p24) (r4 : p18 → p20 → p16) (r5 : p17 → p2) (r6 : p0 → p2 → p4 → p10) (r7 : p14 → p17 → p0) (r8 : p18 → p22 → p11) (r9 : p6 → p14 → p17 → p0) (r10 : p3 → p8 → p13 → p12) (r11 : p3 → p18 → p20 → p23) (r12 : p3 → p21) (r13 : p6 → p18 → p17) (r14 : p20 → p23 → p2) (r15 : p6 → p20 → p17) (r16 : p1 → p16 → p20 → p19) (r17 : p6 → p18 → p8) (r18 : p6 → p21 → p13) (r19 : p3 → p18 → p1) (r20 : p6 → p23 → p4) (r21 : p3 → p9 → p5) : p10 := by
  have h23 : p23 := r11 f3 f18 f20
  have h4 : p4 := r20 f6 h23
  have h2 : p2 := r14 f20 h23
  have h17 : p17 := r13 f6 f18
  have h0 : p0 := r7 f14 h17
  have h10 : p10 := r6 h0 h2 h4
  exact h10
#print axioms cogModel_de78590ec9bc38fada908ab16f94631ee08294c4ba9334bd7e55cc5a882c79d3

theorem cogModel_364ebe313fb97627d28c7379826612dcc47a9bc72038fff9512e96845b255a15 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 : Prop) (f7 : p7) (f10 : p10) (f15 : p15) (f19 : p19) (f20 : p20) (r0 : p10 → p20 → p27 → p17) (r1 : p15 → p19 → p3) (r2 : p5 → p19 → p28) (r3 : p7 → p10 → p11 → p6) (r4 : p15 → p20 → p27 → p30) (r5 : p8 → p20 → p5) (r6 : p10 → p15 → p24 → p11) (r7 : p15 → p19 → p20 → p12) (r8 : p2 → p28 → p29 → p4) (r9 : p16 → p19 → p21) (r10 : p19 → p22 → p14) (r11 : p7 → p15 → p26 → p27) (r12 : p15 → p20 → p24) (r13 : p11 → p19 → p25) (r14 : p25 → p29) (r15 : p20 → p13) (r16 : p19 → p20 → p0) (r17 : p6 → p8 → p25 → p2) (r18 : p0 → p24 → p8) (r19 : p7 → p18 → p9) (r20 : p15 → p23 → p1) (r21 : p10 → p15 → p20 → p26) : p4 := by
  have h0 : p0 := r16 f19 f20
  have h24 : p24 := r12 f15 f20
  have h11 : p11 := r6 f10 f15 h24
  have h8 : p8 := r18 h0 h24
  have h6 : p6 := r3 f7 f10 h11
  have h5 : p5 := r5 h8 f20
  have h25 : p25 := r13 h11 f19
  have h28 : p28 := r2 h5 f19
  have h2 : p2 := r17 h6 h8 h25
  have h29 : p29 := r14 h25
  have h4 : p4 := r8 h2 h28 h29
  exact h4
#print axioms cogModel_364ebe313fb97627d28c7379826612dcc47a9bc72038fff9512e96845b255a15

theorem cogModel_19ca605fbd43bb023f744b16d05c478ca01968d4b638b1e05fda438cca42f143 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 : Prop) (f0 : p0) (f3 : p3) (f12 : p12) (r0 : p19 → p34 → p24) (r1 : p8 → p19 → p34) (r2 : p3 → p6 → p23) (r3 : p9 → p26 → p15) (r4 : p0 → p10 → p17) (r5 : p0 → p12 → p24 → p36) (r6 : p35 → p4) (r7 : p0 → p28) (r8 : p0 → p3 → p12 → p35) (r9 : p21 → p37) (r10 : p2 → p27 → p7) (r11 : p1 → p12 → p27) (r12 : p12 → p27 → p36 → p25) (r13 : p13 → p32 → p33) (r14 : p3 → p12 → p8) (r15 : p0 → p19) (r16 : p0 → p12 → p31) (r17 : p35 → p9) (r18 : p4 → p16 → p21) (r19 : p12 → p14 → p18) (r20 : p2 → p7 → p32) (r21 : p0 → p12 → p10) (r22 : p9 → p28 → p37 → p30) (r23 : p2 → p19 → p1) (r24 : p3 → p26) (r25 : p3 → p9 → p12 → p16) (r26 : p19 → p31 → p2) (r27 : p27 → p36 → p11) (r28 : p4 → p5 → p16 → p22) (r29 : p12 → p20 → p29) (r30 : p0 → p9 → p10 → p5) (r31 : p1 → p11 → p13) : p33 := by
  have h31 : p31 := r16 f0 f12
  have h19 : p19 := r15 f0
  have h2 : p2 := r26 h19 h31
  have h1 : p1 := r23 h2 h19
  have h27 : p27 := r11 h1 f12
  have h7 : p7 := r10 h2 h27
  have h32 : p32 := r20 h2 h7
  have h8 : p8 := r14 f3 f12
  have h34 : p34 := r1 h8 h19
  have h24 : p24 := r0 h19 h34
  have h36 : p36 := r5 f0 f12 h24
  have h11 : p11 := r27 h27 h36
  have h13 : p13 := r31 h1 h11
  have h33 : p33 := r13 h13 h32
  exact h33
#print axioms cogModel_19ca605fbd43bb023f744b16d05c478ca01968d4b638b1e05fda438cca42f143

theorem cogModel_2ea4151be21bc2bbcd4670d9b7d58cbf7024eed7ca6af7ec50a4b5e753164ae6 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 : Prop) (f16 : p16) (f30 : p30) (f36 : p36) (r0 : p17 → p37 → p27) (r1 : p0 → p30 → p21) (r2 : p6 → p25 → p17) (r3 : p16 → p30 → p14) (r4 : p32 → p29) (r5 : p2 → p0) (r6 : p10 → p30 → p31) (r7 : p9 → p35 → p36 → p4) (r8 : p8 → p19 → p23 → p33) (r9 : p36 → p24) (r10 : p2 → p6 → p28) (r11 : p14 → p30 → p35) (r12 : p11 → p21 → p23) (r13 : p30 → p9) (r14 : p12 → p27 → p13) (r15 : p16 → p30 → p36 → p2) (r16 : p16 → p30 → p36 → p32) (r17 : p7 → p16 → p22) (r18 : p12 → p27 → p34) (r19 : p28 → p37 → p15) (r20 : p2 → p34 → p19) (r21 : p25 → p28 → p37 → p5) (r22 : p16 → p36 → p20) (r23 : p14 → p29 → p30 → p1) (r24 : p30 → p38 → p26) (r25 : p5 → p17 → p37 → p12) (r26 : p16 → p30 → p6) (r27 : p0 → p16 → p37) (r28 : p3 → p30 → p18) (r29 : p12 → p15 → p37 → p11) (r30 : p0 → p28 → p36 → p25) (r31 : p11 → p25 → p8) : p33 := by
  have h2 : p2 := r15 f16 f30 f36
  have h0 : p0 := r5 h2
  have h21 : p21 := r1 h0 f30
  have h37 : p37 := r27 h0 f16
  have h6 : p6 := r26 f16 f30
  have h28 : p28 := r10 h2 h6
  have h25 : p25 := r30 h0 h28 f36
  have h15 : p15 := r19 h28 h37
  have h5 : p5 := r21 h25 h28 h37
  have h17 : p17 := r2 h6 h25
  have h12 : p12 := r25 h5 h17 h37
  have h11 : p11 := r29 h12 h15 h37
  have h8 : p8 := r31 h11 h25
  have h23 : p23 := r12 h11 h21
  have h27 : p27 := r0 h17 h37
  have h34 : p34 := r18 h12 h27
  have h19 : p19 := r20 h2 h34
  have h33 : p33 := r8 h8 h19 h23
  exact h33
#print axioms cogModel_2ea4151be21bc2bbcd4670d9b7d58cbf7024eed7ca6af7ec50a4b5e753164ae6

theorem cogModel_c823db5c0d93639f17125329923eb3bdaefaa65e64ce7a195f093af550a6dd4a (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 p41 p42 p43 p44 : Prop) (f4 : p4) (f10 : p10) (f13 : p13) (f34 : p34) (f37 : p37) (r0 : p10 → p24 → p26) (r1 : p28 → p35 → p23) (r2 : p9 → p17 → p16) (r3 : p4 → p24) (r4 : p2 → p14 → p42 → p30) (r5 : p10 → p13 → p17) (r6 : p15 → p17 → p14) (r7 : p10 → p34 → p37 → p18) (r8 : p35 → p37 → p36) (r9 : p1 → p27 → p33) (r10 : p0 → p20 → p43 → p29) (r11 : p13 → p18 → p3) (r12 : p7 → p34 → p31) (r13 : p5 → p44 → p35) (r14 : p15 → p38 → p42) (r15 : p9 → p37 → p5) (r16 : p34 → p20) (r17 : p4 → p36 → p39) (r18 : p13 → p18 → p37 → p1) (r19 : p4 → p5 → p25 → p22) (r20 : p37 → p43) (r21 : p5 → p25 → p38) (r22 : p5 → p37 → p25) (r23 : p24 → p6) (r24 : p4 → p39 → p15) (r25 : p5 → p32 → p44) (r26 : p27 → p37 → p43 → p8) (r27 : p24 → p11) (r28 : p15 → p2) (r29 : p9 → p10 → p17 → p32) (r30 : p10 → p36 → p38 → p28) (r31 : p10 → p12 → p40) (r32 : p22 → p37 → p21) (r33 : p3 → p19) (r34 : p1 → p24 → p37 → p27) (r35 : p4 → p18 → p37 → p0) (r36 : p4 → p37 → p9) (r37 : p10 → p18 → p37 → p41) : p30 := by
  have h17 : p17 := r5 f10 f13
  have h9 : p9 := r36 f4 f37
  have h5 : p5 := r15 h9 f37
  have h25 : p25 := r22 h5 f37
  have h38 : p38 := r21 h5 h25
  have h32 : p32 := r29 h9 f10 h17
  have h44 : p44 := r25 h5 h32
  have h35 : p35 := r13 h5 h44
  have h36 : p36 := r8 h35 f37
  have h39 : p39 := r17 f4 h36
  have h15 : p15 := r24 f4 h39
  have h2 : p2 := r28 h15
  have h42 : p42 := r14 h15 h38
  have h14 : p14 := r6 h15 h17
  have h30 : p30 := r4 h2 h14 h42
  exact h30
#print axioms cogModel_c823db5c0d93639f17125329923eb3bdaefaa65e64ce7a195f093af550a6dd4a

theorem cogModel_dca11e74cf62f48997350a6bead12978e498997fee0c29fbf90c41014eee52eb (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 : Prop) (f1 : p1) (f6 : p6) (f17 : p17) (r0 : p11 → p12 → p19) (r1 : p7 → p8) (r2 : p14 → p0) (r3 : p1 → p7) (r4 : p3 → p14) (r5 : p1 → p6 → p22 → p12) (r6 : p12 → p21) (r7 : p6 → p9 → p5) (r8 : p15 → p17 → p13) (r9 : p6 → p12 → p16) (r10 : p1 → p6 → p16 → p18) (r11 : p10 → p4) (r12 : p1 → p17 → p21 → p11) (r13 : p0 → p10) (r14 : p2 → p3) (r15 : p1 → p11 → p22 → p20) (r16 : p1 → p6 → p17 → p22) (r17 : p8 → p2) : p4 := by
  have h7 : p7 := r3 f1
  have h8 : p8 := r1 h7
  have h2 : p2 := r17 h8
  have h3 : p3 := r14 h2
  have h14 : p14 := r4 h3
  have h0 : p0 := r2 h14
  have h10 : p10 := r13 h0
  have h4 : p4 := r11 h10
  exact h4
#print axioms cogModel_dca11e74cf62f48997350a6bead12978e498997fee0c29fbf90c41014eee52eb

theorem cogModel_30b95d768600b0aed9d4c1060a7a5bc480add8044c8bcfe53c0864d08072c1a9 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 p41 p42 p43 p44 p45 : Prop) (f0 : p0) (f23 : p23) (f33 : p33) (r0 : p29 → p44 → p39) (r1 : p23 → p33 → p3) (r2 : p1 → p27) (r3 : p0 → p28 → p41 → p34) (r4 : p0 → p3 → p16) (r5 : p1 → p33 → p43 → p2) (r6 : p22 → p27 → p31) (r7 : p0 → p25) (r8 : p0 → p17 → p5) (r9 : p0 → p23 → p26 → p19) (r10 : p18 → p22 → p9) (r11 : p10 → p40) (r12 : p0 → p23 → p33 → p6) (r13 : p8 → p22 → p43 → p44) (r14 : p0 → p9 → p43 → p8) (r15 : p0 → p7 → p41 → p12) (r16 : p1 → p18 → p30 → p24) (r17 : p0 → p12 → p25 → p15) (r18 : p11 → p33 → p42) (r19 : p0 → p23 → p43) (r20 : p6 → p38) (r21 : p20 → p21 → p4) (r22 : p23 → p33 → p1) (r23 : p0 → p3 → p38 → p32) (r24 : p9 → p22 → p39 → p21) (r25 : p14 → p23 → p36) (r26 : p23 → p24 → p43 → p35) (r27 : p0 → p2 → p18) (r28 : p27 → p29 → p37 → p20) (r29 : p23 → p40 → p26) (r30 : p3 → p38 → p40 → p45) (r31 : p0 → p41 → p7) (r32 : p12 → p23 → p10) (r33 : p23 → p27 → p33 → p30) (r34 : p2 → p27 → p30 → p22) (r35 : p1 → p27 → p31 → p11) (r36 : p11 → p44 → p37) (r37 : p23 → p41) (r38 : p12 → p41 → p13) (r39 : p7 → p10 → p32 → p28) (r40 : p2 → p8 → p29) : p4 := by
  have h6 : p6 := r12 f0 f23 f33
  have h1 : p1 := r22 f23 f33
  have h27 : p27 := r2 h1
  have h30 : p30 := r33 f23 h27 f33
  have h43 : p43 := r19 f0 f23
  have h2 : p2 := r5 h1 f33 h43
  have h22 : p22 := r34 h2 h27 h30
  have h31 : p31 := r6 h22 h27
  have h11 : p11 := r35 h1 h27 h31
  have h18 : p18 := r27 f0 h2
  have h9 : p9 := r10 h18 h22
  have h8 : p8 := r14 f0 h9 h43
  have h29 : p29 := r40 h2 h8
  have h44 : p44 := r13 h8 h22 h43
  have h39 : p39 := r0 h29 h44
  have h21 : p21 := r24 h9 h22 h39
  have h37 : p37 := r36 h11 h44
  have h20 : p20 := r28 h27 h29 h37
  have h4 : p4 := r21 h20 h21
  exact h4
#print axioms cogModel_30b95d768600b0aed9d4c1060a7a5bc480add8044c8bcfe53c0864d08072c1a9

theorem cogModel_e111689e241ea617fb777ed676ddb0a772330cbe2b3d5c214a9f2d67e1e42fbe (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 p41 p42 p43 p44 p45 p46 p47 : Prop) (f11 : p11) (f28 : p28) (f35 : p35) (f41 : p41) (r0 : p24 → p29 → p35 → p43) (r1 : p18 → p27 → p28 → p45) (r2 : p13 → p41 → p1) (r3 : p11 → p33) (r4 : p11 → p39 → p20) (r5 : p26 → p38) (r6 : p24 → p27 → p35 → p18) (r7 : p25 → p35 → p41 → p46) (r8 : p35 → p40 → p34) (r9 : p28 → p35 → p19) (r10 : p25 → p2) (r11 : p11 → p37 → p31) (r12 : p25 → p28 → p35 → p26) (r13 : p3 → p11 → p9) (r14 : p35 → p38 → p6) (r15 : p25 → p28 → p46 → p47) (r16 : p28 → p35 → p25) (r17 : p8 → p28 → p24) (r18 : p20 → p13) (r19 : p15 → p16 → p42 → p7) (r20 : p35 → p41 → p47 → p5) (r21 : p23 → p28 → p39) (r22 : p8 → p45 → p12) (r23 : p14 → p28 → p22) (r24 : p25 → p28 → p38 → p36) (r25 : p11 → p14 → p24 → p23) (r26 : p4 → p45 → p42) (r27 : p10 → p28 → p41 → p21) (r28 : p2 → p46 → p0) (r29 : p8 → p19 → p14) (r30 : p4 → p12 → p23 → p16) (r31 : p4 → p22 → p28 → p15) (r32 : p46 → p10) (r33 : p11 → p44 → p17) (r34 : p36 → p32) (r35 : p43 → p27) (r36 : p1 → p45 → p4) (r37 : p35 → p8) (r38 : p14 → p23 → p43 → p30) (r39 : p14 → p24 → p29) : p7 := by
  have h8 : p8 := r37 f35
  have h24 : p24 := r17 h8 f28
  have h19 : p19 := r9 f28 f35
  have h14 : p14 := r29 h8 h19
  have h22 : p22 := r23 h14 f28
  have h23 : p23 := r25 f11 h14 h24
  have h39 : p39 := r21 h23 f28
  have h20 : p20 := r4 f11 h39
  have h13 : p13 := r18 h20
  have h1 : p1 := r2 h13 f41
  have h29 : p29 := r39 h14 h24
  have h43 : p43 := r0 h24 h29 f35
  have h27 : p27 := r35 h43
  have h18 : p18 := r6 h24 h27 f35
  have h45 : p45 := r1 h18 h27 f28
  have h12 : p12 := r22 h8 h45
  have h4 : p4 := r36 h1 h45
  have h42 : p42 := r26 h4 h45
  have h16 : p16 := r30 h4 h12 h23
  have h15 : p15 := r31 h4 h22 f28
  have h7 : p7 := r19 h15 h16 h42
  exact h7
#print axioms cogModel_e111689e241ea617fb777ed676ddb0a772330cbe2b3d5c214a9f2d67e1e42fbe

theorem cogModel_68ac635685490ab9d972cd8c251082c7d025b2c7d285c042c789cdb5c9ec1d82 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 : Prop) (f10 : p10) (f20 : p20) (f23 : p23) (f26 : p26) (r0 : p16 → p26 → p13) (r1 : p3 → p6 → p20 → p17) (r2 : p9 → p23 → p14) (r3 : p1 → p25 → p19) (r4 : p11 → p12 → p17 → p1) (r5 : p26 → p28 → p29 → p33) (r6 : p9 → p10 → p25) (r7 : p6 → p23 → p26 → p11) (r8 : p22 → p0) (r9 : p20 → p32 → p9) (r10 : p17 → p19 → p32 → p31) (r11 : p9 → p23 → p1) (r12 : p10 → p22) (r13 : p6 → p20 → p11) (r14 : p0 → p22 → p32) (r15 : p23 → p28) (r16 : p7 → p9 → p32 → p14) (r17 : p10 → p32 → p7) (r18 : p7 → p12 → p25) (r19 : p17 → p22 → p32 → p9) (r20 : p10 → p20 → p33 → p4) (r21 : p26 → p29) (r22 : p6 → p10 → p3) (r23 : p1 → p20 → p5) (r24 : p0 → p20 → p32) (r25 : p2 → p23 → p32 → p7) (r26 : p6 → p26 → p3) (r27 : p20 → p28 → p33 → p18) (r28 : p24 → p31 → p27) (r29 : p8 → p23 → p15) (r30 : p1 → p12 → p5) (r31 : p0 → p3 → p11 → p2) (r32 : p20 → p23 → p6) (r33 : p26 → p32 → p12) (r34 : p0 → p23 → p2) (r35 : p14 → p26 → p19) (r36 : p3 → p5 → p17 → p24) (r37 : p20 → p30 → p21) : p27 := by
  have h22 : p22 := r12 f10
  have h0 : p0 := r8 h22
  have h32 : p32 := r14 h0 h22
  have h9 : p9 := r9 f20 h32
  have h1 : p1 := r11 h9 f23
  have h5 : p5 := r23 h1 f20
  have h6 : p6 := r32 f20 f23
  have h3 : p3 := r22 h6 f10
  have h17 : p17 := r1 h3 h6 f20
  have h24 : p24 := r36 h3 h5 h17
  have h25 : p25 := r6 h9 f10
  have h19 : p19 := r3 h1 h25
  have h31 : p31 := r10 h17 h19 h32
  have h27 : p27 := r28 h24 h31
  exact h27
#print axioms cogModel_68ac635685490ab9d972cd8c251082c7d025b2c7d285c042c789cdb5c9ec1d82

theorem cogModel_8aa8e51dc10a2d8bd13c9fd071b4d4aed9bab7f29f5949910e0c53924d3fc0b7 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 : Prop) (f4 : p4) (f22 : p22) (f27 : p27) (r0 : p8 → p32 → p3) (r1 : p0 → p11 → p2) (r2 : p27 → p32 → p16) (r3 : p4 → p24 → p23) (r4 : p14 → p27 → p28 → p29) (r5 : p22 → p27 → p0) (r6 : p18 → p22 → p12) (r7 : p0 → p15 → p27 → p25) (r8 : p7 → p22 → p9) (r9 : p23 → p24 → p19) (r10 : p4 → p20) (r11 : p27 → p31) (r12 : p8 → p24 → p32 → p5) (r13 : p4 → p22 → p14) (r14 : p4 → p13 → p14 → p28) (r15 : p0 → p19 → p26) (r16 : p31 → p17) (r17 : p4 → p32 → p8) (r18 : p0 → p4 → p24) (r19 : p0 → p23 → p24 → p11) (r20 : p21 → p22 → p33) (r21 : p25 → p34 → p6) (r22 : p14 → p22 → p27 → p13) (r23 : p4 → p27 → p32) (r24 : p2 → p23 → p32 → p34) (r25 : p10 → p27 → p1) (r26 : p0 → p11 → p15) (r27 : p13 → p17 → p30) : p6 := by
  have h0 : p0 := r5 f22 f27
  have h32 : p32 := r23 f4 f27
  have h24 : p24 := r18 h0 f4
  have h23 : p23 := r3 f4 h24
  have h11 : p11 := r19 h0 h23 h24
  have h2 : p2 := r1 h0 h11
  have h34 : p34 := r24 h2 h23 h32
  have h15 : p15 := r26 h0 h11
  have h25 : p25 := r7 h0 h15 f27
  have h6 : p6 := r21 h25 h34
  exact h6
#print axioms cogModel_8aa8e51dc10a2d8bd13c9fd071b4d4aed9bab7f29f5949910e0c53924d3fc0b7

theorem cogModel_86fb80c90b5ff49481d595f2e09d708d1347e2791fd96ceb6a2fb4362a5e2a61 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 : Prop) (f3 : p3) (f6 : p6) (f18 : p18) (f32 : p32) (f34 : p34) (r0 : p6 → p37 → p11) (r1 : p31 → p32 → p38) (r2 : p3 → p38 → p5) (r3 : p6 → p32 → p35 → p21) (r4 : p3 → p18 → p34 → p19) (r5 : p21 → p34 → p30) (r6 : p29 → p32 → p23) (r7 : p2 → p25 → p5) (r8 : p19 → p37) (r9 : p23 → p35 → p7) (r10 : p30 → p34 → p7) (r11 : p34 → p37 → p21) (r12 : p3 → p8 → p4) (r13 : p16 → p32 → p0) (r14 : p1 → p21 → p24 → p38) (r15 : p18 → p25 → p1) (r16 : p3 → p23 → p24) (r17 : p25 → p32 → p35) (r18 : p30 → p34 → p24) (r19 : p6 → p18 → p34 → p27) (r20 : p9 → p18 → p33 → p13) (r21 : p18 → p25 → p37) (r22 : p21 → p35 → p30) (r23 : p24 → p29 → p31 → p2) (r24 : p19 → p35) (r25 : p32 → p14) (r26 : p11 → p21 → p29 → p23) (r27 : p1 → p35 → p11) (r28 : p30 → p32 → p31) (r29 : p27 → p28 → p26) (r30 : p32 → p38 → p10) (r31 : p6 → p32 → p28) (r32 : p18 → p28 → p34 → p15) (r33 : p3 → p32 → p9) (r34 : p18 → p38 → p10) (r35 : p15 → p33) (r36 : p6 → p32 → p19) (r37 : p23 → p34 → p31) (r38 : p32 → p37 → p29) (r39 : p1 → p35 → p29) (r40 : p3 → p6 → p34 → p25) (r41 : p19 → p32 → p1) (r42 : p5 → p10 → p12 → p22) (r43 : p3 → p17 → p36) (r44 : p3 → p20) (r45 : p2 → p21 → p23 → p12) : p22 := by
  have h25 : p25 := r40 f3 f6 f34
  have h1 : p1 := r15 f18 h25
  have h37 : p37 := r21 f18 h25
  have h21 : p21 := r11 f34 h37
  have h30 : p30 := r5 h21 f34
  have h31 : p31 := r28 h30 f32
  have h38 : p38 := r1 h31 f32
  have h5 : p5 := r2 f3 h38
  have h10 : p10 := r30 f32 h38
  have h24 : p24 := r18 h30 f34
  have h29 : p29 := r38 f32 h37
  have h2 : p2 := r23 h24 h29 h31
  have h23 : p23 := r6 h29 f32
  have h12 : p12 := r45 h2 h21 h23
  have h22 : p22 := r42 h5 h10 h12
  exact h22
#print axioms cogModel_86fb80c90b5ff49481d595f2e09d708d1347e2791fd96ceb6a2fb4362a5e2a61

theorem cogModel_93bd6e3aa15bfd72a120fcd652525f11423096e134355b8019c6103a53a61e9c (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 : Prop) (f5 : p5) (f14 : p14) (f29 : p29) (f33 : p33) (r0 : p2 → p14 → p27) (r1 : p14 → p27 → p29 → p36) (r2 : p2 → p5 → p11 → p19) (r3 : p9 → p33 → p6) (r4 : p3 → p22 → p15) (r5 : p14 → p36 → p26) (r6 : p3 → p5 → p29 → p21) (r7 : p5 → p31 → p33 → p25) (r8 : p3 → p21 → p2) (r9 : p3 → p8 → p27 → p23) (r10 : p1 → p33 → p7) (r11 : p4 → p15 → p0) (r12 : p29 → p33 → p3) (r13 : p14 → p34 → p4) (r14 : p5 → p29 → p17) (r15 : p19 → p21 → p32) (r16 : p24 → p29 → p18) (r17 : p14 → p21 → p13) (r18 : p28 → p34) (r19 : p10 → p27 → p8) (r20 : p25 → p29 → p20) (r21 : p2 → p27 → p28 → p22) (r22 : p14 → p21 → p16) (r23 : p5 → p12 → p17 → p31) (r24 : p14 → p29 → p10) (r25 : p10 → p14 → p29 → p11) (r26 : p14 → p30 → p35) (r27 : p8 → p10 → p28) (r28 : p14 → p12) : p0 := by
  have h3 : p3 := r12 f29 f33
  have h21 : p21 := r6 h3 f5 f29
  have h2 : p2 := r8 h3 h21
  have h27 : p27 := r0 h2 f14
  have h10 : p10 := r24 f14 f29
  have h8 : p8 := r19 h10 h27
  have h28 : p28 := r27 h8 h10
  have h34 : p34 := r18 h28
  have h4 : p4 := r13 f14 h34
  have h22 : p22 := r21 h2 h27 h28
  have h15 : p15 := r4 h3 h22
  have h0 : p0 := r11 h4 h15
  exact h0
#print axioms cogModel_93bd6e3aa15bfd72a120fcd652525f11423096e134355b8019c6103a53a61e9c

theorem cogModel_417ffbcc636d077e0995af11fb289cc10fa9813a2ab810062beaecfb6e72f756 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 : Prop) (f18 : p18) (f24 : p24) (f27 : p27) (r0 : p21 → p27 → p14) (r1 : p1 → p9 → p11 → p10) (r2 : p11 → p17 → p27 → p23) (r3 : p18 → p27 → p15) (r4 : p27 → p29 → p4) (r5 : p0 → p3 → p16) (r6 : p10 → p18 → p26 → p19) (r7 : p18 → p24 → p27 → p5) (r8 : p18 → p26 → p9) (r9 : p11 → p24 → p7) (r10 : p14 → p27 → p3) (r11 : p18 → p27 → p11) (r12 : p12 → p18 → p20) (r13 : p18 → p19 → p0) (r14 : p11 → p17 → p7) (r15 : p18 → p23 → p27 → p9) (r16 : p11 → p18 → p24 → p26) (r17 : p23 → p27 → p1) (r18 : p9 → p11 → p19 → p0) (r19 : p18 → p27 → p17) (r20 : p18 → p25) (r21 : p27 → p13) (r22 : p18 → p19 → p3) (r23 : p9 → p18 → p21) (r24 : p2 → p27 → p28) (r25 : p1 → p11 → p24 → p21) (r26 : p7 → p23 → p27 → p1) (r27 : p1 → p21 → p14) (r28 : p8 → p24 → p22) (r29 : p24 → p6) (r30 : p24 → p17) : p16 := by
  have h11 : p11 := r11 f18 f27
  have h26 : p26 := r16 h11 f18 f24
  have h9 : p9 := r8 f18 h26
  have h21 : p21 := r23 h9 f18
  have h14 : p14 := r0 h21 f27
  have h3 : p3 := r10 h14 f27
  have h17 : p17 := r30 f24
  have h23 : p23 := r2 h11 h17 f27
  have h7 : p7 := r14 h11 h17
  have h1 : p1 := r26 h7 h23 f27
  have h10 : p10 := r1 h1 h9 h11
  have h19 : p19 := r6 h10 f18 h26
  have h0 : p0 := r13 f18 h19
  have h16 : p16 := r5 h0 h3
  exact h16
#print axioms cogModel_417ffbcc636d077e0995af11fb289cc10fa9813a2ab810062beaecfb6e72f756

theorem cogModel_df7b2e947029b2e590ac29b8fdcb0d6d359431b5f32e7f9bb71c67997b27e7ac (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 p41 p42 p43 p44 p45 p46 p47 p48 p49 p50 p51 : Prop) (f5 : p5) (f10 : p10) (f20 : p20) (f22 : p22) (f32 : p32) (r0 : p6 → p22 → p36 → p27) (r1 : p21 → p22 → p37 → p33) (r2 : p20 → p46 → p7) (r3 : p20 → p50) (r4 : p10 → p15 → p42 → p38) (r5 : p16 → p21 → p32 → p8) (r6 : p22 → p3) (r7 : p5 → p26 → p1) (r8 : p18 → p22 → p43 → p19) (r9 : p5 → p20 → p0) (r10 : p4 → p5 → p45) (r11 : p22 → p47 → p40) (r12 : p0 → p50 → p39) (r13 : p3 → p44 → p15) (r14 : p27 → p33 → p43 → p49) (r15 : p10 → p22 → p43) (r16 : p20 → p43 → p21) (r17 : p8 → p48 → p23) (r18 : p10 → p28 → p11) (r19 : p32 → p34 → p38 → p35) (r20 : p5 → p16 → p32 → p18) (r21 : p2 → p16 → p21 → p12) (r22 : p16 → p36 → p2) (r23 : p9 → p16 → p21 → p48) (r24 : p5 → p20 → p22 → p47) (r25 : p10 → p20 → p42) (r26 : p0 → p10 → p22 → p34) (r27 : p9 → p22 → p33 → p29) (r28 : p12 → p43 → p48 → p17) (r29 : p22 → p32 → p24) (r30 : p10 → p22 → p30 → p31) (r31 : p3 → p20 → p25) (r32 : p9 → p18 → p19 → p36) (r33 : p22 → p43 → p16) (r34 : p5 → p12 → p29 → p13) (r35 : p5 → p22 → p50 → p44) (r36 : p22 → p47 → p41) (r37 : p20 → p23 → p32 → p6) (r38 : p13 → p17 → p14) (r39 : p9 → p18 → p23 → p37) (r40 : p10 → p39 → p51) (r41 : p15 → p42 → p30) (r42 : p5 → p20 → p22 → p9) : p14 := by
  have h43 : p43 := r15 f10 f22
  have h21 : p21 := r16 f20 h43
  have h16 : p16 := r33 f22 h43
  have h9 : p9 := r42 f5 f20 f22
  have h48 : p48 := r23 h9 h16 h21
  have h8 : p8 := r5 h16 h21 f32
  have h23 : p23 := r17 h8 h48
  have h6 : p6 := r37 f20 h23 f32
  have h18 : p18 := r20 f5 h16 f32
  have h37 : p37 := r39 h9 h18 h23
  have h33 : p33 := r1 h21 f22 h37
  have h29 : p29 := r27 h9 f22 h33
  have h19 : p19 := r8 h18 f22 h43
  have h36 : p36 := r32 h9 h18 h19
  have h2 : p2 := r22 h16 h36
  have h12 : p12 := r21 h2 h16 h21
  have h13 : p13 := r34 f5 h12 h29
  have h17 : p17 := r28 h12 h43 h48
  have h14 : p14 := r38 h13 h17
  exact h14
#print axioms cogModel_df7b2e947029b2e590ac29b8fdcb0d6d359431b5f32e7f9bb71c67997b27e7ac

theorem cogModel_4faaa86165b945097b6cce08a5c008d5c02bf4dde9d50c4050fa82e1305f7aca (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 : Prop) (f12 : p12) (f15 : p15) (f21 : p21) (f23 : p23) (r0 : p15 → p23 → p30 → p11) (r1 : p12 → p17 → p24 → p16) (r2 : p5 → p17 → p10) (r3 : p5 → p21 → p8) (r4 : p20 → p26 → p32 → p4) (r5 : p7 → p12 → p15 → p0) (r6 : p2 → p23 → p33) (r7 : p1 → p12 → p9) (r8 : p8 → p18 → p17) (r9 : p15 → p14) (r10 : p0 → p5 → p12 → p32) (r11 : p12 → p13 → p23 → p28) (r12 : p12 → p15 → p23 → p19) (r13 : p8 → p10 → p31 → p22) (r14 : p15 → p18 → p7) (r15 : p15 → p21 → p23 → p6) (r16 : p5 → p15 → p31 → p3) (r17 : p15 → p17 → p20) (r18 : p12 → p15 → p23 → p5) (r19 : p3 → p6 → p32 → p26) (r20 : p10 → p21 → p24) (r21 : p14 → p19 → p21 → p30) (r22 : p21 → p26 → p25) (r23 : p15 → p21 → p31) (r24 : p12 → p14 → p28 → p27) (r25 : p4 → p25 → p29) (r26 : p14 → p23 → p30 → p13) (r27 : p12 → p31 → p18) : p29 := by
  have h6 : p6 := r15 f15 f21 f23
  have h5 : p5 := r18 f12 f15 f23
  have h8 : p8 := r3 h5 f21
  have h31 : p31 := r23 f15 f21
  have h3 : p3 := r16 h5 f15 h31
  have h18 : p18 := r27 f12 h31
  have h7 : p7 := r14 f15 h18
  have h0 : p0 := r5 h7 f12 f15
  have h32 : p32 := r10 h0 h5 f12
  have h26 : p26 := r19 h3 h6 h32
  have h25 : p25 := r22 f21 h26
  have h17 : p17 := r8 h8 h18
  have h20 : p20 := r17 f15 h17
  have h4 : p4 := r4 h20 h26 h32
  have h29 : p29 := r25 h4 h25
  exact h29
#print axioms cogModel_4faaa86165b945097b6cce08a5c008d5c02bf4dde9d50c4050fa82e1305f7aca

theorem cogModel_4e528990abce5be3c9a3e4d2eb2f5dd0a152966532a3990894f57e438ce18866 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 p41 : Prop) (f13 : p13) (f23 : p23) (f27 : p27) (f34 : p34) (f41 : p41) (r0 : p23 → p41 → p16) (r1 : p20 → p34 → p5) (r2 : p10 → p15 → p11) (r3 : p23 → p34 → p22) (r4 : p15 → p20 → p26 → p5) (r5 : p13 → p34 → p33) (r6 : p13 → p34 → p19) (r7 : p11 → p27 → p28) (r8 : p23 → p33 → p12) (r9 : p16 → p18 → p21) (r10 : p4 → p33 → p37 → p9) (r11 : p16 → p21 → p23 → p35) (r12 : p16 → p29 → p18) (r13 : p19 → p41 → p4) (r14 : p6 → p21 → p41 → p10) (r15 : p39 → p41 → p1) (r16 : p34 → p36 → p32) (r17 : p0 → p13 → p35) (r18 : p2 → p21 → p28) (r19 : p6 → p13 → p15) (r20 : p23 → p34 → p25) (r21 : p2 → p31 → p26) (r22 : p23 → p28 → p20) (r23 : p20 → p34 → p24) (r24 : p27 → p41 → p29) (r25 : p10 → p41 → p2) (r26 : p14 → p23 → p17) (r27 : p18 → p22 → p29 → p15) (r28 : p27 → p38 → p3) (r29 : p21 → p23 → p31) (r30 : p0 → p6 → p31) (r31 : p22 → p6) (r32 : p10 → p36 → p24) (r33 : p5 → p24 → p32 → p7) (r34 : p20 → p36 → p32) (r35 : p6 → p23 → p21) (r36 : p2 → p15 → p26 → p20) (r37 : p22 → p34 → p18) (r38 : p13 → p40 → p30) (r39 : p13 → p34 → p29) (r40 : p10 → p22 → p2) (r41 : p13 → p23 → p16) (r42 : p6 → p27 → p0) (r43 : p18 → p28 → p36) (r44 : p8 → p23 → p37) (r45 : p19 → p8) : p7 := by
  have h29 : p29 := r39 f13 f34
  have h22 : p22 := r3 f23 f34
  have h18 : p18 := r37 h22 f34
  have h15 : p15 := r27 h18 h22 h29
  have h6 : p6 := r31 h22
  have h21 : p21 := r35 h6 f23
  have h10 : p10 := r14 h6 h21 f41
  have h2 : p2 := r40 h10 h22
  have h28 : p28 := r18 h2 h21
  have h36 : p36 := r43 h18 h28
  have h24 : p24 := r32 h10 h36
  have h32 : p32 := r16 f34 h36
  have h20 : p20 := r22 f23 h28
  have h5 : p5 := r1 h20 f34
  have h7 : p7 := r33 h5 h24 h32
  exact h7
#print axioms cogModel_4e528990abce5be3c9a3e4d2eb2f5dd0a152966532a3990894f57e438ce18866

theorem cogModel_c23914116199c606460623baa8097ebfb67618a05ad2710692d07b056fd26b1a (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 : Prop) (f24 : p24) (f25 : p25) (f35 : p35) (r0 : p8 → p24 → p25 → p7) (r1 : p24 → p33 → p3) (r2 : p17 → p24 → p2) (r3 : p11 → p25 → p29) (r4 : p10 → p12 → p28 → p27) (r5 : p10 → p15 → p22) (r6 : p5 → p10 → p22 → p17) (r7 : p20 → p14) (r8 : p25 → p35 → p21) (r9 : p2 → p6 → p15 → p4) (r10 : p25 → p31 → p32) (r11 : p6 → p5) (r12 : p5 → p22 → p12) (r13 : p24 → p25 → p26 → p20) (r14 : p4 → p13 → p19 → p18) (r15 : p4 → p21 → p19) (r16 : p10 → p23 → p0) (r17 : p5 → p17 → p23) (r18 : p26 → p16) (r19 : p6 → p28 → p9) (r20 : p10 → p24 → p6) (r21 : p9 → p18 → p27 → p1) (r22 : p10 → p24 → p15) (r23 : p0 → p24 → p25 → p13) (r24 : p24 → p35 → p10) (r25 : p35 → p26) (r26 : p16 → p24 → p25 → p34) (r27 : p24 → p26 → p35 → p8) (r28 : p24 → p36) (r29 : p2 → p4 → p28) (r30 : p6 → p21 → p30) : p1 := by
  have h10 : p10 := r24 f24 f35
  have h6 : p6 := r20 h10 f24
  have h5 : p5 := r11 h6
  have h15 : p15 := r22 h10 f24
  have h22 : p22 := r5 h10 h15
  have h12 : p12 := r12 h5 h22
  have h17 : p17 := r6 h5 h10 h22
  have h2 : p2 := r2 h17 f24
  have h4 : p4 := r9 h2 h6 h15
  have h28 : p28 := r29 h2 h4
  have h9 : p9 := r19 h6 h28
  have h27 : p27 := r4 h10 h12 h28
  have h21 : p21 := r8 f25 f35
  have h19 : p19 := r15 h4 h21
  have h23 : p23 := r17 h5 h17
  have h0 : p0 := r16 h10 h23
  have h13 : p13 := r23 h0 f24 f25
  have h18 : p18 := r14 h4 h13 h19
  have h1 : p1 := r21 h9 h18 h27
  exact h1
#print axioms cogModel_c23914116199c606460623baa8097ebfb67618a05ad2710692d07b056fd26b1a

theorem cogModel_2adb3aeb35bfae07585ca1d277818902c37f85e0efe5bb57b9e24956ba42307f (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 : Prop) (f8 : p8) (f16 : p16) (f22 : p22) (f23 : p23) (r0 : p23 → p18) (r1 : p23 → p14) (r2 : p2 → p16 → p21) (r3 : p24 → p19) (r4 : p6 → p12) (r5 : p14 → p4) (r6 : p11 → p6) (r7 : p12 → p7) (r8 : p19 → p11) (r9 : p4 → p24) (r10 : p8 → p16 → p5) (r11 : p8 → p22 → p23 → p15) (r12 : p7 → p17) (r13 : p13 → p23 → p20) (r14 : p1 → p22 → p9) (r15 : p17 → p10) (r16 : p15 → p0) (r17 : p0 → p3) : p10 := by
  have h14 : p14 := r1 f23
  have h4 : p4 := r5 h14
  have h24 : p24 := r9 h4
  have h19 : p19 := r3 h24
  have h11 : p11 := r8 h19
  have h6 : p6 := r6 h11
  have h12 : p12 := r4 h6
  have h7 : p7 := r7 h12
  have h17 : p17 := r12 h7
  have h10 : p10 := r15 h17
  exact h10
#print axioms cogModel_2adb3aeb35bfae07585ca1d277818902c37f85e0efe5bb57b9e24956ba42307f

theorem cogModel_ee81ab40c8e9959d54aeccbd9c04954c5de54434718c81e4e8b76312bbae6eb7 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 : Prop) (f12 : p12) (f19 : p19) (f22 : p22) (r0 : p19 → p14) (r1 : p7 → p12 → p15) (r2 : p0 → p9) (r3 : p3 → p5) (r4 : p6 → p8 → p1) (r5 : p6 → p19 → p24 → p10) (r6 : p12 → p19 → p24 → p11) (r7 : p12 → p20 → p16) (r8 : p19 → p21 → p2) (r9 : p5 → p0) (r10 : p13 → p4) (r11 : p4 → p3) (r12 : p19 → p22 → p6) (r13 : p18 → p19 → p23) (r14 : p6 → p19 → p22 → p24) (r15 : p19 → p22 → p8) (r16 : p22 → p17) (r17 : p17 → p13) : p9 := by
  have h17 : p17 := r16 f22
  have h13 : p13 := r17 h17
  have h4 : p4 := r10 h13
  have h3 : p3 := r11 h4
  have h5 : p5 := r3 h3
  have h0 : p0 := r9 h5
  have h9 : p9 := r2 h0
  exact h9
#print axioms cogModel_ee81ab40c8e9959d54aeccbd9c04954c5de54434718c81e4e8b76312bbae6eb7

theorem cogModel_b17c7a1d190b77a063367bab97e76f3aed7bede91034441cbb54646a49ee69dd (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 : Prop) (f13 : p13) (f15 : p15) (f28 : p28) (f31 : p31) (f39 : p39) (r0 : p8 → p23 → p32) (r1 : p39 → p9) (r2 : p12 → p14) (r3 : p2 → p8 → p38) (r4 : p13 → p31 → p12) (r5 : p14 → p23 → p31 → p34) (r6 : p4 → p39 → p34) (r7 : p4 → p8 → p30) (r8 : p1 → p31 → p4) (r9 : p29 → p39 → p27) (r10 : p1 → p18 → p27) (r11 : p13 → p34 → p30) (r12 : p24 → p31 → p26) (r13 : p13 → p23 → p24) (r14 : p13 → p22 → p38) (r15 : p2 → p28 → p35 → p18) (r16 : p15 → p1) (r17 : p15 → p30 → p22) (r18 : p15 → p38 → p39 → p6) (r19 : p1 → p8 → p26) (r20 : p8 → p14 → p38 → p29) (r21 : p15 → p24 → p32) (r22 : p20 → p39 → p19) (r23 : p14 → p26 → p29 → p10) (r24 : p2 → p15 → p39 → p35) (r25 : p9 → p31 → p36 → p5) (r26 : p15 → p26 → p32 → p2) (r27 : p1 → p12 → p4) (r28 : p13 → p31 → p1) (r29 : p33 → p39 → p3) (r30 : p8 → p22 → p39 → p37) (r31 : p30 → p32 → p22) (r32 : p31 → p0) (r33 : p9 → p13 → p21) (r34 : p18 → p31 → p16) (r35 : p28 → p39 → p12) (r36 : p1 → p4 → p14 → p8) (r37 : p2 → p31 → p37) (r38 : p2 → p13 → p35) (r39 : p15 → p18 → p28 → p16) (r40 : p12 → p31 → p23) (r41 : p12 → p13 → p23) (r42 : p15 → p36 → p17) (r43 : p10 → p16 → p27 → p7) (r44 : p9 → p17 → p28 → p11) (r45 : p15 → p28 → p36) (r46 : p15 → p31 → p25) (r47 : p15 → p38 → p29) (r48 : p4 → p12 → p24) : p7 := by
  have h1 : p1 := r28 f13 f31
  have h4 : p4 := r8 h1 f31
  have h34 : p34 := r6 h4 f39
  have h12 : p12 := r35 f28 f39
  have h14 : p14 := r2 h12
  have h8 : p8 := r36 h1 h4 h14
  have h26 : p26 := r19 h1 h8
  have h24 : p24 := r48 h4 h12
  have h32 : p32 := r21 f15 h24
  have h2 : p2 := r26 f15 h26 h32
  have h35 : p35 := r38 h2 f13
  have h18 : p18 := r15 h2 f28 h35
  have h27 : p27 := r10 h1 h18
  have h16 : p16 := r34 h18 f31
  have h38 : p38 := r3 h2 h8
  have h29 : p29 := r47 f15 h38
  have h10 : p10 := r23 h14 h26 h29
  have h7 : p7 := r43 h10 h16 h27
  exact h7
#print axioms cogModel_b17c7a1d190b77a063367bab97e76f3aed7bede91034441cbb54646a49ee69dd

theorem cogModel_5769d98e940d2aaaa413571d3787ddce03cb6f7a3c0876133fba0f11234d85d9 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 p41 p42 p43 p44 p45 : Prop) (f6 : p6) (f35 : p35) (f43 : p43) (r0 : p0 → p2 → p22 → p4) (r1 : p37 → p45 → p27) (r2 : p0 → p22 → p21) (r3 : p3 → p26 → p1) (r4 : p39 → p22) (r5 : p20 → p43 → p9) (r6 : p6 → p35 → p43 → p11) (r7 : p4 → p40) (r8 : p2 → p4 → p15) (r9 : p11 → p35 → p41 → p19) (r10 : p16 → p19 → p36 → p24) (r11 : p2 → p6 → p43 → p39) (r12 : p16 → p35 → p41 → p37) (r13 : p12 → p18) (r14 : p6 → p13 → p12) (r15 : p17 → p36 → p3) (r16 : p11 → p42 → p10) (r17 : p43 → p0) (r18 : p8 → p37 → p43 → p42) (r19 : p4 → p22 → p39 → p34) (r20 : p16 → p31 → p41 → p36) (r21 : p6 → p34 → p39 → p32) (r22 : p35 → p41) (r23 : p6 → p35 → p41 → p16) (r24 : p28 → p20) (r25 : p8 → p12 → p31) (r26 : p10 → p16 → p36 → p17) (r27 : p12 → p17 → p26) (r28 : p11 → p16 → p19 → p45) (r29 : p38 → p43 → p23) (r30 : p13 → p19 → p8) (r31 : p6 → p35 → p39 → p28) (r32 : p6 → p2) (r33 : p30 → p34 → p25) (r34 : p0 → p6 → p35 → p30) (r35 : p11 → p37 → p13) (r36 : p33 → p43 → p7) (r37 : p28 → p30 → p5) (r38 : p11 → p41 → p29) (r39 : p25 → p28 → p30 → p44) (r40 : p2 → p35 → p39 → p14) : p1 := by
  have h0 : p0 := r17 f43
  have h41 : p41 := r22 f35
  have h16 : p16 := r23 f6 f35 h41
  have h37 : p37 := r12 h16 f35 h41
  have h11 : p11 := r6 f6 f35 f43
  have h13 : p13 := r35 h11 h37
  have h12 : p12 := r14 f6 h13
  have h18 : p18 := r13 h12
  have h19 : p19 := r9 h11 f35 h41
  have h8 : p8 := r30 h13 h19
  have h31 : p31 := r25 h8 h12
  have h36 : p36 := r20 h16 h31 h41
  have h42 : p42 := r18 h8 h37 f43
  have h10 : p10 := r16 h11 h42
  have h17 : p17 := r26 h10 h16 h36
  have h3 : p3 := r15 h17 h36
  have h26 : p26 := r27 h12 h17
  have h1 : p1 := r3 h3 h26
  exact h1
#print axioms cogModel_5769d98e940d2aaaa413571d3787ddce03cb6f7a3c0876133fba0f11234d85d9

theorem cogModel_2ef1adc69cbda35f3573f64a29fdfd4e45afec8d8629bc4625b6693294fa6fb0 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 : Prop) (f5 : p5) (f16 : p16) (f18 : p18) (f21 : p21) (r0 : p12 → p31) (r1 : p18 → p21 → p7) (r2 : p10 → p21 → p15) (r3 : p5 → p18 → p26) (r4 : p5 → p11 → p20) (r5 : p10 → p18 → p4) (r6 : p25 → p26 → p29 → p17) (r7 : p16 → p24 → p1) (r8 : p4 → p7 → p30) (r9 : p4 → p12 → p21 → p14) (r10 : p4 → p8 → p18 → p13) (r11 : p18 → p26 → p19) (r12 : p6 → p27 → p3) (r13 : p18 → p0) (r14 : p16 → p21 → p26 → p25) (r15 : p5 → p17 → p22) (r16 : p7 → p15 → p28 → p8) (r17 : p16 → p18 → p21 → p10) (r18 : p18 → p30 → p31 → p27) (r19 : p5 → p7 → p28) (r20 : p8 → p14 → p21 → p6) (r21 : p8 → p15 → p12) (r22 : p16 → p23 → p9) (r23 : p4 → p7 → p15 → p2) (r24 : p0 → p25 → p24) (r25 : p16 → p21 → p29) : p3 := by
  have h10 : p10 := r17 f16 f18 f21
  have h4 : p4 := r5 h10 f18
  have h7 : p7 := r1 f18 f21
  have h30 : p30 := r8 h4 h7
  have h28 : p28 := r19 f5 h7
  have h15 : p15 := r2 h10 f21
  have h8 : p8 := r16 h7 h15 h28
  have h12 : p12 := r21 h8 h15
  have h31 : p31 := r0 h12
  have h27 : p27 := r18 f18 h30 h31
  have h14 : p14 := r9 h4 h12 f21
  have h6 : p6 := r20 h8 h14 f21
  have h3 : p3 := r12 h6 h27
  exact h3
#print axioms cogModel_2ef1adc69cbda35f3573f64a29fdfd4e45afec8d8629bc4625b6693294fa6fb0

theorem cogModel_cd2ccbdda64a318c9cd7966a871375fe155d6f9931760c1fb3196386aa628bdb (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 : Prop) (f0 : p0) (f25 : p25) (f29 : p29) (f34 : p34) (r0 : p29 → p33) (r1 : p10 → p27) (r2 : p25 → p29 → p32 → p13) (r3 : p0 → p5 → p29 → p23) (r4 : p3 → p13 → p14 → p10) (r5 : p3 → p13 → p14 → p9) (r6 : p29 → p34 → p14) (r7 : p0 → p16 → p17) (r8 : p6 → p29 → p35) (r9 : p23 → p1) (r10 : p2 → p22 → p24) (r11 : p0 → p14 → p25 → p3) (r12 : p0 → p30) (r13 : p0 → p5) (r14 : p5 → p29 → p34 → p4) (r15 : p8 → p34 → p11) (r16 : p9 → p25 → p8) (r17 : p1 → p4 → p5 → p28) (r18 : p25 → p33 → p31) (r19 : p29 → p21) (r20 : p0 → p12 → p20) (r21 : p10 → p11 → p22) (r22 : p5 → p25 → p34 → p26) (r23 : p34 → p18) (r24 : p7 → p25 → p19) (r25 : p0 → p32) (r26 : p9 → p11 → p27 → p2) (r27 : p0 → p3 → p8 → p15) : p24 := by
  have h14 : p14 := r6 f29 f34
  have h3 : p3 := r11 f0 h14 f25
  have h32 : p32 := r25 f0
  have h13 : p13 := r2 f25 f29 h32
  have h10 : p10 := r4 h3 h13 h14
  have h27 : p27 := r1 h10
  have h9 : p9 := r5 h3 h13 h14
  have h8 : p8 := r16 h9 f25
  have h11 : p11 := r15 h8 f34
  have h22 : p22 := r21 h10 h11
  have h2 : p2 := r26 h9 h11 h27
  have h24 : p24 := r10 h2 h22
  exact h24
#print axioms cogModel_cd2ccbdda64a318c9cd7966a871375fe155d6f9931760c1fb3196386aa628bdb

theorem cogModel_d30c368201489233d3613af053c4dda3ef59114db2010f16cd3882cfa47a6bbf (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 : Prop) (f1 : p1) (f17 : p17) (f20 : p20) (f28 : p28) (r0 : p4 → p12 → p25) (r1 : p15 → p28 → p10) (r2 : p22 → p31 → p5) (r3 : p12 → p26 → p27) (r4 : p20 → p22 → p30) (r5 : p7 → p18 → p12) (r6 : p1 → p17 → p3) (r7 : p17 → p32 → p15) (r8 : p28 → p31 → p5) (r9 : p20 → p28 → p3) (r10 : p7 → p16 → p21 → p26) (r11 : p20 → p24 → p28 → p0) (r12 : p20 → p24 → p0) (r13 : p8 → p20 → p23) (r14 : p0 → p1 → p28 → p18) (r15 : p18 → p30 → p14) (r16 : p1 → p24 → p22) (r17 : p15 → p17 → p21) (r18 : p1 → p4 → p25) (r19 : p0 → p3 → p30) (r20 : p17 → p20 → p28 → p8) (r21 : p1 → p2 → p8 → p13) (r22 : p17 → p21 → p16) (r23 : p3 → p6 → p21) (r24 : p25 → p27 → p29) (r25 : p31 → p16) (r26 : p11 → p17 → p19) (r27 : p1 → p3 → p22) (r28 : p22 → p28 → p32) (r29 : p9 → p28 → p34) (r30 : p1 → p7 → p4) (r31 : p6 → p20 → p31) (r32 : p17 → p18 → p32 → p15) (r33 : p1 → p24) (r34 : p1 → p17 → p20 → p33) (r35 : p6 → p24 → p30 → p10) (r36 : p14 → p18 → p20 → p31) (r37 : p20 → p35) (r38 : p30 → p32 → p6) (r39 : p0 → p1 → p22 → p32) (r40 : p20 → p21 → p7) (r41 : p8 → p17 → p35 → p2) (r42 : p14 → p21 → p30 → p7) (r43 : p16 → p32 → p4) : p29 := by
  have h3 : p3 := r6 f1 f17
  have h22 : p22 := r27 f1 h3
  have h32 : p32 := r28 h22 f28
  have h15 : p15 := r7 f17 h32
  have h21 : p21 := r17 h15 f17
  have h7 : p7 := r40 f20 h21
  have h4 : p4 := r30 f1 h7
  have h25 : p25 := r18 f1 h4
  have h16 : p16 := r22 f17 h21
  have h26 : p26 := r10 h7 h16 h21
  have h24 : p24 := r33 f1
  have h0 : p0 := r12 f20 h24
  have h18 : p18 := r14 h0 f1 f28
  have h12 : p12 := r5 h7 h18
  have h27 : p27 := r3 h12 h26
  have h29 : p29 := r24 h25 h27
  exact h29
#print axioms cogModel_d30c368201489233d3613af053c4dda3ef59114db2010f16cd3882cfa47a6bbf

theorem cogModel_04e1b87a57b2163a88a866ad34cdb14ebdff654f20cbe88954142b115e215651 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 p41 p42 : Prop) (f7 : p7) (f9 : p9) (f14 : p14) (f36 : p36) (f40 : p40) (r0 : p31 → p38 → p26) (r1 : p0 → p2 → p7 → p23) (r2 : p4 → p12 → p36 → p41) (r3 : p2 → p6 → p25) (r4 : p7 → p35 → p18) (r5 : p7 → p36 → p24) (r6 : p0 → p16 → p3) (r7 : p3 → p7 → p37) (r8 : p5 → p23 → p24 → p1) (r9 : p11 → p21 → p15) (r10 : p12 → p17 → p40 → p10) (r11 : p30 → p36 → p33) (r12 : p7 → p27) (r13 : p25 → p40 → p21) (r14 : p0 → p3 → p11) (r15 : p0 → p37 → p5) (r16 : p1 → p14 → p40 → p38) (r17 : p8 → p34) (r18 : p0 → p9 → p13) (r19 : p8 → p17) (r20 : p22 → p36 → p28) (r21 : p4 → p12) (r22 : p14 → p4) (r23 : p13 → p40 → p6) (r24 : p1 → p31) (r25 : p2 → p40 → p16) (r26 : p9 → p0) (r27 : p4 → p12 → p34 → p20) (r28 : p1 → p36 → p31) (r29 : p9 → p14 → p19) (r30 : p6 → p9 → p3) (r31 : p23 → p25 → p36 → p21) (r32 : p29 → p40 → p32) (r33 : p2 → p36 → p23) (r34 : p2 → p7 → p29 → p32) (r35 : p16 → p40 → p25) (r36 : p7 → p9 → p0) (r37 : p0 → p2 → p7 → p6) (r38 : p0 → p13 → p16) (r39 : p14 → p8) (r40 : p9 → p40 → p24) (r41 : p1 → p9 → p38) (r42 : p16 → p37 → p29) (r43 : p9 → p42 → p39) (r44 : p0 → p14 → p19 → p2) : p26 := by
  have h24 : p24 := r5 f7 f36
  have h19 : p19 := r29 f9 f14
  have h0 : p0 := r36 f7 f9
  have h13 : p13 := r18 h0 f9
  have h6 : p6 := r23 h13 f40
  have h3 : p3 := r30 h6 f9
  have h37 : p37 := r7 h3 f7
  have h5 : p5 := r15 h0 h37
  have h2 : p2 := r44 h0 f14 h19
  have h23 : p23 := r33 h2 f36
  have h1 : p1 := r8 h5 h23 h24
  have h31 : p31 := r24 h1
  have h38 : p38 := r41 h1 f9
  have h26 : p26 := r0 h31 h38
  exact h26
#print axioms cogModel_04e1b87a57b2163a88a866ad34cdb14ebdff654f20cbe88954142b115e215651

theorem cogModel_ff3b9f08733578b17bb58336874c73f79df7a7947c03060c9a1fe77b1a0737f0 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 p41 : Prop) (f3 : p3) (f5 : p5) (f6 : p6) (f39 : p39) (r0 : p3 → p6 → p30 → p15) (r1 : p3 → p32 → p40) (r2 : p6 → p20 → p39 → p4) (r3 : p16 → p17 → p12) (r4 : p6 → p39 → p9) (r5 : p11 → p28 → p17) (r6 : p3 → p6 → p19 → p41) (r7 : p3 → p19) (r8 : p12 → p32 → p40 → p34) (r9 : p5 → p6 → p39 → p29) (r10 : p3 → p6 → p8) (r11 : p6 → p16 → p37) (r12 : p15 → p21 → p41 → p33) (r13 : p15 → p23) (r14 : p3 → p39 → p28) (r15 : p19 → p30) (r16 : p0 → p30 → p2) (r17 : p4 → p20 → p23 → p36) (r18 : p39 → p38) (r19 : p16 → p27 → p29 → p22) (r20 : p30 → p20) (r21 : p6 → p35 → p31) (r22 : p28 → p11) (r23 : p11 → p29 → p37 → p1) (r24 : p11 → p27 → p32) (r25 : p7 → p37 → p40 → p26) (r26 : p39 → p14) (r27 : p6 → p30 → p18) (r28 : p8 → p28 → p27) (r29 : p11 → p37 → p7) (r30 : p9 → p30 → p0) (r31 : p3 → p21) (r32 : p5 → p29 → p32 → p16) (r33 : p7 → p40 → p25) (r34 : p25 → p26 → p24) (r35 : p13 → p39 → p10) : p24 := by
  have h8 : p8 := r10 f3 f6
  have h38 : p38 := r18 f39
  have h28 : p28 := r14 f3 f39
  have h11 : p11 := r22 h28
  have h17 : p17 := r5 h11 h28
  have h27 : p27 := r28 h8 h28
  have h32 : p32 := r24 h11 h27
  have h40 : p40 := r1 f3 h32
  have h19 : p19 := r7 f3
  have h41 : p41 := r6 f3 f6 h19
  have h29 : p29 := r9 f5 f6 f39
  have h16 : p16 := r32 f5 h29 h32
  have h37 : p37 := r11 f6 h16
  have h7 : p7 := r29 h11 h37
  have h25 : p25 := r33 h7 h40
  have h26 : p26 := r25 h7 h37 h40
  have h24 : p24 := r34 h25 h26
  exact h24
#print axioms cogModel_ff3b9f08733578b17bb58336874c73f79df7a7947c03060c9a1fe77b1a0737f0

theorem cogModel_f30fc1064e018e2526110b4bc9531b7b3b7fac4acf30f351986b82de08a83fe6 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 : Prop) (f4 : p4) (f5 : p5) (f27 : p27) (r0 : p4 → p27 → p20) (r1 : p5 → p21 → p34) (r2 : p5 → p24 → p23) (r3 : p21 → p35 → p9) (r4 : p6 → p21 → p1) (r5 : p7 → p24) (r6 : p0 → p27 → p6) (r7 : p4 → p5 → p27 → p26) (r8 : p1 → p9 → p34 → p30) (r9 : p5 → p22 → p0) (r10 : p2 → p22 → p27 → p16) (r11 : p5 → p21 → p1) (r12 : p5 → p19 → p9) (r13 : p4 → p18 → p11) (r14 : p27 → p17) (r15 : p6 → p27 → p13) (r16 : p4 → p31 → p32) (r17 : p4 → p5 → p10) (r18 : p6 → p7 → p27 → p13) (r19 : p10 → p20 → p25) (r20 : p5 → p35 → p19) (r21 : p5 → p13 → p3) (r22 : p2 → p4 → p0) (r23 : p0 → p27 → p7) (r24 : p27 → p28) (r25 : p2 → p20 → p24 → p23) (r26 : p0 → p20 → p6) (r27 : p16 → p22 → p7) (r28 : p10 → p22) (r29 : p20 → p27 → p2) (r30 : p24 → p27 → p35) (r31 : p5 → p17 → p29) (r32 : p19 → p35 → p34) (r33 : p10 → p27 → p2) (r34 : p27 → p33 → p8) (r35 : p12 → p25 → p3) (r36 : p4 → p7 → p27 → p12) (r37 : p5 → p27 → p15) (r38 : p5 → p27 → p20) (r39 : p4 → p23 → p21) (r40 : p24 → p27 → p35 → p19) (r41 : p26 → p27 → p29 → p14) : p30 := by
  have h17 : p17 := r14 f27
  have h20 : p20 := r0 f4 f27
  have h2 : p2 := r29 h20 f27
  have h0 : p0 := r22 h2 f4
  have h6 : p6 := r26 h0 h20
  have h13 : p13 := r15 h6 f27
  have h10 : p10 := r17 f4 f5
  have h22 : p22 := r28 h10
  have h16 : p16 := r10 h2 h22 f27
  have h7 : p7 := r27 h16 h22
  have h24 : p24 := r5 h7
  have h35 : p35 := r30 h24 f27
  have h19 : p19 := r20 f5 h35
  have h34 : p34 := r32 h19 h35
  have h9 : p9 := r12 f5 h19
  have h23 : p23 := r2 f5 h24
  have h21 : p21 := r39 f4 h23
  have h1 : p1 := r4 h6 h21
  have h30 : p30 := r8 h1 h9 h34
  exact h30
#print axioms cogModel_f30fc1064e018e2526110b4bc9531b7b3b7fac4acf30f351986b82de08a83fe6

theorem cogModel_6c06ece1867af6c9975c692e9d26c9cb230d491b8c3a47d25bd74bf2e5724378 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 : Prop) (f4 : p4) (f8 : p8) (f20 : p20) (f28 : p28) (r0 : p7 → p15 → p27) (r1 : p4 → p28 → p10) (r2 : p9 → p17 → p26 → p29) (r3 : p1 → p24 → p28 → p14) (r4 : p8 → p10 → p20 → p23) (r5 : p4 → p21) (r6 : p4 → p20 → p28 → p25) (r7 : p4 → p20 → p24) (r8 : p4 → p14 → p18) (r9 : p2 → p21 → p28 → p7) (r10 : p25 → p28 → p3) (r11 : p12 → p27 → p26) (r12 : p12 → p20 → p9) (r13 : p20 → p28 → p1) (r14 : p3 → p8 → p12 → p17) (r15 : p4 → p8 → p10 → p0) (r16 : p2 → p3 → p15) (r17 : p7 → p11 → p27 → p5) (r18 : p16 → p20 → p6) (r19 : p21 → p28 → p2) (r20 : p3 → p4 → p28 → p11) (r21 : p19 → p28 → p22) (r22 : p7 → p13 → p15 → p12) (r23 : p15 → p13) : p29 := by
  have h25 : p25 := r6 f4 f20 f28
  have h3 : p3 := r10 h25 f28
  have h21 : p21 := r5 f4
  have h2 : p2 := r19 h21 f28
  have h15 : p15 := r16 h2 h3
  have h13 : p13 := r23 h15
  have h7 : p7 := r9 h2 h21 f28
  have h12 : p12 := r22 h7 h13 h15
  have h9 : p9 := r12 h12 f20
  have h17 : p17 := r14 h3 f8 h12
  have h27 : p27 := r0 h7 h15
  have h26 : p26 := r11 h12 h27
  have h29 : p29 := r2 h9 h17 h26
  exact h29
#print axioms cogModel_6c06ece1867af6c9975c692e9d26c9cb230d491b8c3a47d25bd74bf2e5724378

theorem cogModel_a97d65f754485a71ea1b968c5638d654617874e41f1f69c2d2c1978ad9757968 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 : Prop) (f5 : p5) (f26 : p26) (f29 : p29) (r0 : p1 → p7 → p2) (r1 : p5 → p18 → p20 → p33) (r2 : p5 → p16 → p3) (r3 : p5 → p29 → p13) (r4 : p26 → p28 → p30) (r5 : p5 → p13 → p10) (r6 : p26 → p33 → p11) (r7 : p2 → p26 → p28 → p30) (r8 : p1 → p21 → p26 → p28) (r9 : p1 → p30 → p19) (r10 : p6 → p29 → p18) (r11 : p5 → p29 → p0) (r12 : p5 → p15 → p27) (r13 : p5 → p26 → p4) (r14 : p0 → p29 → p7) (r15 : p17 → p20 → p32) (r16 : p20 → p28 → p6) (r17 : p1 → p26 → p28) (r18 : p26 → p21) (r19 : p5 → p26 → p21) (r20 : p19 → p29 → p25) (r21 : p7 → p18 → p17) (r22 : p26 → p0) (r23 : p18 → p29 → p23) (r24 : p5 → p33 → p11) (r25 : p26 → p29 → p8) (r26 : p25 → p29 → p17) (r27 : p0 → p5 → p29 → p1) (r28 : p24 → p29 → p12) (r29 : p19 → p28 → p18) (r30 : p2 → p31) (r31 : p22 → p29 → p16) (r32 : p8 → p29 → p22) (r33 : p2 → p18 → p21 → p23) (r34 : p23 → p26 → p9) (r35 : p29 → p33 → p9) (r36 : p6 → p20 → p25) (r37 : p9 → p11 → p32 → p14) (r38 : p2 → p28 → p20) (r39 : p5 → p30 → p19) : p14 := by
  have h21 : p21 := r18 f26
  have h0 : p0 := r22 f26
  have h7 : p7 := r14 h0 f29
  have h1 : p1 := r27 h0 f5 f29
  have h28 : p28 := r17 h1 f26
  have h30 : p30 := r4 f26 h28
  have h19 : p19 := r9 h1 h30
  have h18 : p18 := r29 h19 h28
  have h23 : p23 := r23 h18 f29
  have h9 : p9 := r34 h23 f26
  have h17 : p17 := r21 h7 h18
  have h25 : p25 := r20 h19 f29
  have h2 : p2 := r0 h1 h7
  have h20 : p20 := r38 h2 h28
  have h32 : p32 := r15 h17 h20
  have h33 : p33 := r1 f5 h18 h20
  have h11 : p11 := r6 f26 h33
  have h14 : p14 := r37 h9 h11 h32
  exact h14
#print axioms cogModel_a97d65f754485a71ea1b968c5638d654617874e41f1f69c2d2c1978ad9757968

theorem cogModel_9f5100548d2924e4d00e3fe6c9ca86118b0b6b33422eb1bf34ded30714c1d8fc (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 : Prop) (f7 : p7) (f9 : p9) (f12 : p12) (f13 : p13) (r0 : p9 → p12 → p17) (r1 : p9 → p23 → p11) (r2 : p7 → p20 → p5) (r3 : p6 → p18) (r4 : p10 → p6) (r5 : p9 → p15 → p16) (r6 : p7 → p23) (r7 : p4 → p9 → p0) (r8 : p13 → p10) (r9 : p9 → p17 → p21 → p19) (r10 : p1 → p22) (r11 : p8 → p1) (r12 : p7 → p12 → p13 → p14) (r13 : p7 → p21) (r14 : p22 → p3) (r15 : p2 → p8) (r16 : p18 → p2) : p3 := by
  have h10 : p10 := r8 f13
  have h6 : p6 := r4 h10
  have h18 : p18 := r3 h6
  have h2 : p2 := r16 h18
  have h8 : p8 := r15 h2
  have h1 : p1 := r11 h8
  have h22 : p22 := r10 h1
  have h3 : p3 := r14 h22
  exact h3
#print axioms cogModel_9f5100548d2924e4d00e3fe6c9ca86118b0b6b33422eb1bf34ded30714c1d8fc

theorem cogModel_52cf40a26acb9a0fe56f4d04269fe66da33abca2b10ce2f5a3ed731242c3b54a (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 : Prop) (f4 : p4) (f6 : p6) (f14 : p14) (f15 : p15) (r0 : p8 → p14 → p22 → p1) (r1 : p10 → p20 → p22 → p11) (r2 : p19 → p16) (r3 : p20 → p10) (r4 : p6 → p12) (r5 : p2 → p11 → p3) (r6 : p4 → p14 → p23 → p8) (r7 : p14 → p15 → p23) (r8 : p16 → p18) (r9 : p17 → p5) (r10 : p13 → p17) (r11 : p0 → p6 → p21) (r12 : p4 → p14 → p2) (r13 : p5 → p19) (r14 : p12 → p13) (r15 : p4 → p14 → p23 → p20) (r16 : p4 → p10 → p22) (r17 : p9 → p15 → p7) : p18 := by
  have h12 : p12 := r4 f6
  have h13 : p13 := r14 h12
  have h17 : p17 := r10 h13
  have h5 : p5 := r9 h17
  have h19 : p19 := r13 h5
  have h16 : p16 := r2 h19
  have h18 : p18 := r8 h16
  exact h18
#print axioms cogModel_52cf40a26acb9a0fe56f4d04269fe66da33abca2b10ce2f5a3ed731242c3b54a

theorem cogModel_4feac95195d39fed87df9f84c9d3a3c47071e82bb64dd7e4c94ec2f45f1093a1 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 p41 p42 : Prop) (f3 : p3) (f33 : p33) (f35 : p35) (f38 : p38) (r0 : p12 → p20 → p36 → p13) (r1 : p3 → p10 → p42 → p1) (r2 : p14 → p41 → p2) (r3 : p38 → p28) (r4 : p4 → p15 → p33 → p24) (r5 : p7 → p23 → p37 → p12) (r6 : p1 → p31 → p30) (r7 : p30 → p40 → p32) (r8 : p3 → p10 → p42) (r9 : p3 → p34 → p7) (r10 : p22 → p38 → p29) (r11 : p38 → p27) (r12 : p6 → p35 → p38 → p0) (r13 : p5 → p9 → p33 → p39) (r14 : p26 → p40) (r15 : p10 → p23 → p41 → p14) (r16 : p17 → p42 → p26) (r17 : p3 → p9) (r18 : p7 → p20 → p37) (r19 : p0 → p3 → p16 → p5) (r20 : p11 → p36 → p31) (r21 : p3 → p36 → p38 → p41) (r22 : p6 → p25) (r23 : p6 → p33 → p35 → p21) (r24 : p0 → p6 → p38 → p16) (r25 : p38 → p34) (r26 : p1 → p2 → p11) (r27 : p7 → p33 → p41 → p23) (r28 : p0 → p8) (r29 : p3 → p15) (r30 : p35 → p38 → p6) (r31 : p3 → p33 → p38 → p4) (r32 : p35 → p38 → p36) (r33 : p20 → p33 → p10) (r34 : p33 → p36 → p20) (r35 : p3 → p19 → p18) (r36 : p2 → p34 → p17) : p32 := by
  have h28 : p28 := r3 f38
  have h36 : p36 := r32 f35 f38
  have h20 : p20 := r34 f33 h36
  have h10 : p10 := r33 h20 f33
  have h42 : p42 := r8 f3 h10
  have h1 : p1 := r1 f3 h10 h42
  have h34 : p34 := r25 f38
  have h7 : p7 := r9 f3 h34
  have h37 : p37 := r18 h7 h20
  have h41 : p41 := r21 f3 h36 f38
  have h23 : p23 := r27 h7 f33 h41
  have h14 : p14 := r15 h10 h23 h41
  have h2 : p2 := r2 h14 h41
  have h17 : p17 := r36 h2 h34
  have h26 : p26 := r16 h17 h42
  have h40 : p40 := r14 h26
  have h11 : p11 := r26 h1 h2
  have h31 : p31 := r20 h11 h36
  have h30 : p30 := r6 h1 h31
  have h32 : p32 := r7 h30 h40
  exact h32
#print axioms cogModel_4feac95195d39fed87df9f84c9d3a3c47071e82bb64dd7e4c94ec2f45f1093a1

theorem cogModel_a8e626be427eec1c161a167a2b441acb9c733a5f8bb5031e102c45b5afa4a03f (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 : Prop) (f3 : p3) (f22 : p22) (f24 : p24) (r0 : p9 → p16 → p24 → p27) (r1 : p3 → p37 → p31) (r2 : p0 → p24 → p26 → p5) (r3 : p3 → p35 → p40 → p2) (r4 : p20 → p22 → p34) (r5 : p3 → p38 → p6) (r6 : p22 → p24 → p38) (r7 : p4 → p14 → p39 → p15) (r8 : p3 → p13 → p32) (r9 : p2 → p24 → p7) (r10 : p4 → p40 → p30) (r11 : p3 → p24 → p35) (r12 : p30 → p38 → p25) (r13 : p22 → p38 → p40 → p14) (r14 : p6 → p17 → p39) (r15 : p20 → p22 → p11) (r16 : p23 → p28 → p39 → p36) (r17 : p10 → p17 → p22 → p28) (r18 : p3 → p22 → p24 → p9) (r19 : p15 → p22 → p40 → p13) (r20 : p11 → p20 → p24 → p16) (r21 : p24 → p26 → p28 → p4) (r22 : p3 → p9 → p20 → p21) (r23 : p9 → p20 → p24 → p18) (r24 : p6 → p38 → p1) (r25 : p15 → p24 → p35 → p0) (r26 : p1 → p38 → p19) (r27 : p3 → p22 → p40) (r28 : p1 → p35 → p38 → p17) (r29 : p3 → p22 → p20) (r30 : p3 → p19 → p26) (r31 : p5 → p32 → p33 → p12) (r32 : p13 → p28 → p40 → p33) (r33 : p8 → p24 → p29) (r34 : p3 → p6 → p22 → p23) (r35 : p7 → p35 → p10) : p12 := by
  have h40 : p40 := r27 f3 f22
  have h35 : p35 := r11 f3 f24
  have h2 : p2 := r3 f3 h35 h40
  have h7 : p7 := r9 h2 f24
  have h10 : p10 := r35 h7 h35
  have h38 : p38 := r6 f22 f24
  have h14 : p14 := r13 f22 h38 h40
  have h6 : p6 := r5 f3 h38
  have h1 : p1 := r24 h6 h38
  have h19 : p19 := r26 h1 h38
  have h26 : p26 := r30 f3 h19
  have h17 : p17 := r28 h1 h35 h38
  have h28 : p28 := r17 h10 h17 f22
  have h4 : p4 := r21 f24 h26 h28
  have h30 : p30 := r10 h4 h40
  have h39 : p39 := r14 h6 h17
  have h15 : p15 := r7 h4 h14 h39
  have h13 : p13 := r19 h15 f22 h40
  have h32 : p32 := r8 f3 h13
  have h33 : p33 := r32 h13 h28 h40
  have h0 : p0 := r25 h15 f24 h35
  have h5 : p5 := r2 h0 f24 h26
  have h12 : p12 := r31 h5 h32 h33
  exact h12
#print axioms cogModel_a8e626be427eec1c161a167a2b441acb9c733a5f8bb5031e102c45b5afa4a03f

theorem cogModel_7da6250b9755a6cac724a34428fbf45424c6cb079309efeac96e2aa093f3e092 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 : Prop) (f3 : p3) (f9 : p9) (f20 : p20) (f24 : p24) (f25 : p25) (r0 : p16 → p2) (r1 : p0 → p23) (r2 : p11 → p4) (r3 : p6 → p20 → p24 → p13) (r4 : p3 → p16) (r5 : p12 → p17) (r6 : p1 → p12) (r7 : p10 → p25 → p15) (r8 : p3 → p21 → p7) (r9 : p2 → p0) (r10 : p4 → p27) (r11 : p14 → p24 → p25 → p26) (r12 : p3 → p20 → p14) (r13 : p6 → p20 → p18) (r14 : p9 → p20 → p25 → p5) (r15 : p23 → p11) (r16 : p3 → p19 → p22) (r17 : p13 → p18 → p20 → p8) (r18 : p9 → p24 → p25 → p6) (r19 : p27 → p1) : p17 := by
  have h16 : p16 := r4 f3
  have h2 : p2 := r0 h16
  have h0 : p0 := r9 h2
  have h23 : p23 := r1 h0
  have h11 : p11 := r15 h23
  have h4 : p4 := r2 h11
  have h27 : p27 := r10 h4
  have h1 : p1 := r19 h27
  have h12 : p12 := r6 h1
  have h17 : p17 := r5 h12
  exact h17
#print axioms cogModel_7da6250b9755a6cac724a34428fbf45424c6cb079309efeac96e2aa093f3e092

theorem cogModel_ad8bd838a9c990c6fff42d81e1fb0158e9ecb8df7574a4f4fabd555ffbf648f5 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 : Prop) (f10 : p10) (f11 : p11) (f17 : p17) (r0 : p10 → p17 → p4) (r1 : p11 → p5) (r2 : p6 → p13) (r3 : p13 → p12) (r4 : p17 → p19 → p7) (r5 : p4 → p10 → p15 → p0) (r6 : p18 → p8) (r7 : p10 → p14 → p9) (r8 : p8 → p6) (r9 : p10 → p2) (r10 : p12 → p16) (r11 : p1 → p4 → p10 → p15) (r12 : p5 → p18) (r13 : p4 → p17 → p1) (r14 : p10 → p17 → p3) : p16 := by
  have h5 : p5 := r1 f11
  have h18 : p18 := r12 h5
  have h8 : p8 := r6 h18
  have h6 : p6 := r8 h8
  have h13 : p13 := r2 h6
  have h12 : p12 := r3 h13
  have h16 : p16 := r10 h12
  exact h16
#print axioms cogModel_ad8bd838a9c990c6fff42d81e1fb0158e9ecb8df7574a4f4fabd555ffbf648f5

theorem cogModel_49edd3a74f179bd0edcaddd30a049cd694a3ccf098b5082ec44248a98229a54d (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 : Prop) (f9 : p9) (f10 : p10) (f22 : p22) (f24 : p24) (r0 : p6 → p1) (r1 : p12 → p26 → p4) (r2 : p3 → p17) (r3 : p10 → p27 → p23) (r4 : p24 → p21) (r5 : p9 → p25 → p19) (r6 : p7 → p22 → p11) (r7 : p2 → p22 → p15) (r8 : p9 → p10 → p24 → p7) (r9 : p9 → p16 → p0) (r10 : p20 → p14) (r11 : p11 → p26 → p13) (r12 : p21 → p20) (r13 : p14 → p6) (r14 : p1 → p3) (r15 : p7 → p22 → p12) (r16 : p17 → p5) (r17 : p9 → p26) (r18 : p22 → p24 → p18) (r19 : p5 → p8) : p8 := by
  have h21 : p21 := r4 f24
  have h20 : p20 := r12 h21
  have h14 : p14 := r10 h20
  have h6 : p6 := r13 h14
  have h1 : p1 := r0 h6
  have h3 : p3 := r14 h1
  have h17 : p17 := r2 h3
  have h5 : p5 := r16 h17
  have h8 : p8 := r19 h5
  exact h8
#print axioms cogModel_49edd3a74f179bd0edcaddd30a049cd694a3ccf098b5082ec44248a98229a54d

theorem cogModel_a5367db77555a12fb95e2b93f8fd4a3dac9cccab243d78df78bce4b6ebb9ad62 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 : Prop) (f5 : p5) (f22 : p22) (f27 : p27) (f30 : p30) (r0 : p21 → p29 → p30 → p34) (r1 : p5 → p27 → p31) (r2 : p2 → p14 → p13) (r3 : p5 → p27 → p19) (r4 : p2 → p3 → p4 → p14) (r5 : p5 → p15 → p30 → p26) (r6 : p28 → p34 → p33) (r7 : p7 → p11 → p21 → p25) (r8 : p7 → p31 → p21) (r9 : p14 → p27 → p28) (r10 : p5 → p22 → p36 → p6) (r11 : p2 → p24 → p29 → p1) (r12 : p5 → p27 → p30 → p15) (r13 : p2 → p8 → p16) (r14 : p22 → p29 → p3) (r15 : p5 → p27 → p7) (r16 : p7 → p30 → p31 → p11) (r17 : p17 → p22 → p37) (r18 : p5 → p15 → p22 → p36) (r19 : p9 → p31 → p32) (r20 : p3 → p31 → p4) (r21 : p12 → p22 → p0) (r22 : p1 → p16 → p18 → p35) (r23 : p23 → p27 → p20) (r24 : p10 → p14 → p32 → p8) (r25 : p7 → p30 → p29) (r26 : p4 → p28 → p24) (r27 : p10 → p33 → p18) (r28 : p3 → p21 → p10) (r29 : p2 → p5 → p9) (r30 : p11 → p34 → p2) : p35 := by
  have h7 : p7 := r15 f5 f27
  have h29 : p29 := r25 h7 f30
  have h3 : p3 := r14 f22 h29
  have h31 : p31 := r1 f5 f27
  have h4 : p4 := r20 h3 h31
  have h21 : p21 := r8 h7 h31
  have h10 : p10 := r28 h3 h21
  have h34 : p34 := r0 h21 h29 f30
  have h11 : p11 := r16 h7 f30 h31
  have h2 : p2 := r30 h11 h34
  have h14 : p14 := r4 h2 h3 h4
  have h28 : p28 := r9 h14 f27
  have h33 : p33 := r6 h28 h34
  have h18 : p18 := r27 h10 h33
  have h24 : p24 := r26 h4 h28
  have h1 : p1 := r11 h2 h24 h29
  have h9 : p9 := r29 h2 f5
  have h32 : p32 := r19 h9 h31
  have h8 : p8 := r24 h10 h14 h32
  have h16 : p16 := r13 h2 h8
  have h35 : p35 := r22 h1 h16 h18
  exact h35
#print axioms cogModel_a5367db77555a12fb95e2b93f8fd4a3dac9cccab243d78df78bce4b6ebb9ad62

theorem cogModel_a71ba9ff4810dad62ea43cc217fc6d7fa50bf043ef67c57be4618569ce5d88b9 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 : Prop) (f9 : p9) (f17 : p17) (f18 : p18) (r0 : p21 → p11) (r1 : p1 → p5) (r2 : p6 → p2) (r3 : p7 → p20) (r4 : p9 → p14) (r5 : p17 → p1) (r6 : p10 → p18 → p19) (r7 : p9 → p17 → p18 → p22) (r8 : p9 → p17 → p16) (r9 : p13 → p7) (r10 : p9 → p18 → p22 → p21) (r11 : p14 → p18 → p15) (r12 : p0 → p8) (r13 : p8 → p13) (r14 : p3 → p0) (r15 : p5 → p3) (r16 : p12 → p17 → p4) (r17 : p9 → p15 → p18 → p6) : p20 := by
  have h14 : p14 := r4 f9
  have h15 : p15 := r11 h14 f18
  have h1 : p1 := r5 f17
  have h5 : p5 := r1 h1
  have h3 : p3 := r15 h5
  have h0 : p0 := r14 h3
  have h8 : p8 := r12 h0
  have h13 : p13 := r13 h8
  have h7 : p7 := r9 h13
  have h20 : p20 := r3 h7
  exact h20
#print axioms cogModel_a71ba9ff4810dad62ea43cc217fc6d7fa50bf043ef67c57be4618569ce5d88b9

theorem cogModel_85bf5e0c0c32ecc46a58f105b908b8b385325d9c3af15ebf61757da9e26cc9a5 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 : Prop) (f4 : p4) (f18 : p18) (f26 : p26) (r0 : p23 → p29 → p21) (r1 : p18 → p26 → p6) (r2 : p1 → p30 → p36 → p17) (r3 : p4 → p26 → p34) (r4 : p0 → p7 → p27) (r5 : p1 → p2 → p28) (r6 : p4 → p26 → p2) (r7 : p20 → p0) (r8 : p7 → p14 → p20 → p23) (r9 : p7 → p23 → p29 → p11) (r10 : p2 → p4 → p3) (r11 : p15 → p35 → p12) (r12 : p16 → p18 → p36 → p19) (r13 : p17 → p19 → p28 → p22) (r14 : p10 → p26 → p13) (r15 : p2 → p30 → p7) (r16 : p4 → p34 → p31) (r17 : p0 → p21 → p23 → p1) (r18 : p9 → p18 → p34 → p15) (r19 : p3 → p36 → p29) (r20 : p25 → p26 → p24) (r21 : p15 → p35) (r22 : p6 → p14 → p21 → p16) (r23 : p4 → p26 → p34 → p9) (r24 : p2 → p6 → p30) (r25 : p4 → p15 → p8) (r26 : p6 → p30 → p36) (r27 : p26 → p32) (r28 : p3 → p26 → p20) (r29 : p26 → p33 → p5) (r30 : p2 → p6 → p26 → p14) : p22 := by
  have h2 : p2 := r6 f4 f26
  have h6 : p6 := r1 f18 f26
  have h30 : p30 := r24 h2 h6
  have h36 : p36 := r26 h6 h30
  have h14 : p14 := r30 h2 h6 f26
  have h3 : p3 := r10 h2 f4
  have h20 : p20 := r28 h3 f26
  have h0 : p0 := r7 h20
  have h29 : p29 := r19 h3 h36
  have h7 : p7 := r15 h2 h30
  have h23 : p23 := r8 h7 h14 h20
  have h21 : p21 := r0 h23 h29
  have h1 : p1 := r17 h0 h21 h23
  have h28 : p28 := r5 h1 h2
  have h17 : p17 := r2 h1 h30 h36
  have h16 : p16 := r22 h6 h14 h21
  have h19 : p19 := r12 h16 f18 h36
  have h22 : p22 := r13 h17 h19 h28
  exact h22
#print axioms cogModel_85bf5e0c0c32ecc46a58f105b908b8b385325d9c3af15ebf61757da9e26cc9a5

theorem cogModel_c368f87bdaf01b3d4002db8667f2d88ef185cd3c19c1dd45595b8d55393acbb9 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 p41 : Prop) (f3 : p3) (f5 : p5) (f12 : p12) (f20 : p20) (r0 : p19 → p4) (r1 : p12 → p18 → p40) (r2 : p2 → p12 → p1) (r3 : p3 → p5 → p12 → p18) (r4 : p20 → p30 → p38) (r5 : p4 → p39) (r6 : p3 → p25 → p6) (r7 : p5 → p34 → p35) (r8 : p21 → p28 → p40 → p2) (r9 : p3 → p12 → p7) (r10 : p1 → p12 → p23 → p25) (r11 : p18 → p25 → p16) (r12 : p28 → p21) (r13 : p0 → p1 → p10 → p41) (r14 : p5 → p17 → p21 → p11) (r15 : p20 → p19) (r16 : p24 → p35 → p8) (r17 : p2 → p32 → p40 → p27) (r18 : p12 → p40 → p31) (r19 : p13 → p20 → p36) (r20 : p5 → p27 → p0) (r21 : p2 → p9 → p21 → p17) (r22 : p11 → p20 → p23) (r23 : p21 → p41 → p6) (r24 : p3 → p25 → p16) (r25 : p6 → p17 → p40 → p24) (r26 : p11 → p12 → p10) (r27 : p3 → p9 → p40) (r28 : p3 → p21 → p31) (r29 : p1 → p31 → p0) (r30 : p4 → p14) (r31 : p3 → p18 → p40 → p32) (r32 : p3 → p22 → p29) (r33 : p0 → p20 → p40 → p33) (r34 : p20 → p32 → p17) (r35 : p12 → p21 → p32) (r36 : p20 → p28 → p21) (r37 : p20 → p32 → p37 → p10) (r38 : p11 → p16 → p35) (r39 : p20 → p26 → p15) (r40 : p5 → p28) (r41 : p3 → p23 → p25) (r42 : p9 → p31 → p32 → p1) (r43 : p12 → p37 → p33) (r44 : p21 → p27 → p37) (r45 : p2 → p20 → p27) (r46 : p31 → p40 → p41 → p34) (r47 : p5 → p20 → p9) (r48 : p0 → p27 → p37 → p23) (r49 : p6 → p12 → p24) : p8 := by
  have h18 : p18 := r3 f3 f5 f12
  have h40 : p40 := r1 f12 h18
  have h31 : p31 := r18 f12 h40
  have h28 : p28 := r40 f5
  have h21 : p21 := r36 f20 h28
  have h2 : p2 := r8 h21 h28 h40
  have h1 : p1 := r2 h2 f12
  have h0 : p0 := r29 h1 h31
  have h32 : p32 := r35 f12 h21
  have h17 : p17 := r34 f20 h32
  have h11 : p11 := r14 f5 h17 h21
  have h23 : p23 := r22 h11 f20
  have h25 : p25 := r41 f3 h23
  have h6 : p6 := r6 f3 h25
  have h24 : p24 := r49 h6 f12
  have h16 : p16 := r11 h18 h25
  have h35 : p35 := r38 h11 h16
  have h8 : p8 := r16 h24 h35
  exact h8
#print axioms cogModel_c368f87bdaf01b3d4002db8667f2d88ef185cd3c19c1dd45595b8d55393acbb9

theorem cogModel_084e65788aaeb2cd7ca5c35fb017932e6b63bc3f57290f2dbcd9084c2cbb29b0 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 : Prop) (f11 : p11) (f17 : p17) (f20 : p20) (r0 : p22 → p3) (r1 : p17 → p23 → p25) (r2 : p8 → p11 → p13 → p2) (r3 : p10 → p8) (r4 : p10 → p20 → p13) (r5 : p3 → p24) (r6 : p11 → p17 → p20 → p15) (r7 : p1 → p17 → p6) (r8 : p11 → p20 → p21 → p9) (r9 : p7 → p22) (r10 : p20 → p16) (r11 : p11 → p15 → p17 → p10) (r12 : p24 → p0) (r13 : p5 → p7) (r14 : p0 → p18) (r15 : p11 → p15 → p21) (r16 : p20 → p5) (r17 : p17 → p19 → p4) (r18 : p14 → p17 → p12) : p18 := by
  have h5 : p5 := r16 f20
  have h7 : p7 := r13 h5
  have h22 : p22 := r9 h7
  have h3 : p3 := r0 h22
  have h24 : p24 := r5 h3
  have h0 : p0 := r12 h24
  have h18 : p18 := r14 h0
  exact h18
#print axioms cogModel_084e65788aaeb2cd7ca5c35fb017932e6b63bc3f57290f2dbcd9084c2cbb29b0

theorem cogModel_aadf46bff06bc9abe48e0395b8566afb3ef4d9e093f0b1c85d7c57403498c0aa (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 : Prop) (f14 : p14) (f15 : p15) (f16 : p16) (f34 : p34) (f39 : p39) (r0 : p9 → p17 → p7) (r1 : p36 → p28) (r2 : p14 → p3) (r3 : p14 → p16 → p38 → p17) (r4 : p16 → p26 → p34 → p12) (r5 : p24 → p34 → p1) (r6 : p7 → p15 → p11) (r7 : p17 → p26 → p34 → p9) (r8 : p16 → p18 → p5) (r9 : p3 → p27) (r10 : p13 → p26 → p10) (r11 : p9 → p4) (r12 : p19 → p39 → p32) (r13 : p3 → p21 → p34 → p20) (r14 : p16 → p18) (r15 : p1 → p4 → p13) (r16 : p24 → p40 → p33) (r17 : p14 → p15 → p38) (r18 : p5 → p18 → p25 → p2) (r19 : p17 → p26 → p39 → p37) (r20 : p12 → p8) (r21 : p15 → p25) (r22 : p8 → p17 → p40) (r23 : p25 → p29) (r24 : p4 → p37 → p24) (r25 : p18 → p21 → p30) (r26 : p10 → p35 → p23) (r27 : p3 → p15 → p39 → p36) (r28 : p7 → p12 → p33 → p31) (r29 : p18 → p39 → p6) (r30 : p13 → p26 → p40 → p35) (r31 : p34 → p39 → p21) (r32 : p0 → p39 → p22) (r33 : p34 → p39 → p26) : p23 := by
  have h26 : p26 := r33 f34 f39
  have h38 : p38 := r17 f14 f15
  have h17 : p17 := r3 f14 f16 h38
  have h9 : p9 := r7 h17 h26 f34
  have h4 : p4 := r11 h9
  have h37 : p37 := r19 h17 h26 f39
  have h24 : p24 := r24 h4 h37
  have h1 : p1 := r5 h24 f34
  have h13 : p13 := r15 h1 h4
  have h10 : p10 := r10 h13 h26
  have h12 : p12 := r4 f16 h26 f34
  have h8 : p8 := r20 h12
  have h40 : p40 := r22 h8 h17
  have h35 : p35 := r30 h13 h26 h40
  have h23 : p23 := r26 h10 h35
  exact h23
#print axioms cogModel_aadf46bff06bc9abe48e0395b8566afb3ef4d9e093f0b1c85d7c57403498c0aa

theorem cogModel_a9389d2d2fca8cae7e0d5f44ec66c1a95f9ca4bbc59661b58b0fc82d4c825fc7 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 : Prop) (f8 : p8) (f22 : p22) (f23 : p23) (f31 : p31) (f35 : p35) (r0 : p10 → p28 → p31 → p24) (r1 : p22 → p31 → p10) (r2 : p8 → p35 → p13) (r3 : p18 → p34 → p33) (r4 : p24 → p35 → p1) (r5 : p1 → p8 → p36) (r6 : p6 → p16 → p19 → p7) (r7 : p8 → p18 → p33) (r8 : p31 → p3) (r9 : p5 → p35 → p19) (r10 : p31 → p35 → p10) (r11 : p2 → p26 → p18) (r12 : p23 → p28) (r13 : p4 → p35 → p20) (r14 : p28 → p35 → p15) (r15 : p5 → p36 → p6) (r16 : p5 → p31 → p19) (r17 : p9 → p22 → p0) (r18 : p3 → p8 → p22 → p21) (r19 : p35 → p37) (r20 : p23 → p31 → p13) (r21 : p22 → p26 → p34) (r22 : p14 → p22 → p2) (r23 : p15 → p24 → p2) (r24 : p17 → p22 → p28 → p16) (r25 : p8 → p27 → p29) (r26 : p8 → p23 → p31 → p28) (r27 : p22 → p23 → p30) (r28 : p8 → p18 → p24 → p17) (r29 : p25 → p30 → p12) (r30 : p8 → p30 → p31 → p25) (r31 : p2 → p26 → p34) (r32 : p13 → p28 → p35 → p15) (r33 : p14 → p34 → p5) (r34 : p14 → p22 → p28 → p26) (r35 : p18 → p35 → p5) (r36 : p8 → p24 → p1) (r37 : p11 → p31 → p32) (r38 : p10 → p31 → p14) : p7 := by
  have h28 : p28 := r26 f8 f23 f31
  have h15 : p15 := r14 h28 f35
  have h13 : p13 := r2 f8 f35
  have h10 : p10 := r1 f22 f31
  have h14 : p14 := r38 h10 f31
  have h2 : p2 := r22 h14 f22
  have h24 : p24 := r0 h10 h28 f31
  have h1 : p1 := r4 h24 f35
  have h36 : p36 := r5 h1 f8
  have h26 : p26 := r34 h14 f22 h28
  have h18 : p18 := r11 h2 h26
  have h5 : p5 := r35 h18 f35
  have h6 : p6 := r15 h5 h36
  have h19 : p19 := r9 h5 f35
  have h17 : p17 := r28 f8 h18 h24
  have h16 : p16 := r24 h17 f22 h28
  have h7 : p7 := r6 h6 h16 h19
  exact h7
#print axioms cogModel_a9389d2d2fca8cae7e0d5f44ec66c1a95f9ca4bbc59661b58b0fc82d4c825fc7

theorem cogModel_961823b17bbabd5916d13d6e88bcdceab00a36380cbc340c57da25bdceddafd1 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 : Prop) (f0 : p0) (f1 : p1) (f4 : p4) (f15 : p15) (f21 : p21) (r0 : p19 → p21 → p14) (r1 : p1 → p9 → p12) (r2 : p17 → p13) (r3 : p16 → p7) (r4 : p4 → p15 → p21 → p19) (r5 : p15 → p19 → p9) (r6 : p3 → p22) (r7 : p12 → p15 → p11) (r8 : p7 → p20) (r9 : p1 → p16) (r10 : p2 → p17) (r11 : p1 → p10 → p6) (r12 : p0 → p4 → p18) (r13 : p20 → p3) (r14 : p22 → p2) (r15 : p8 → p21 → p5) : p13 := by
  have h16 : p16 := r9 f1
  have h7 : p7 := r3 h16
  have h20 : p20 := r8 h7
  have h3 : p3 := r13 h20
  have h22 : p22 := r6 h3
  have h2 : p2 := r14 h22
  have h17 : p17 := r10 h2
  have h13 : p13 := r2 h17
  exact h13
#print axioms cogModel_961823b17bbabd5916d13d6e88bcdceab00a36380cbc340c57da25bdceddafd1

theorem cogModel_60b31502abee8d9f5233bcb05305a3278aad956f4016379c42096e9c190563ac (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 : Prop) (f0 : p0) (f3 : p3) (f21 : p21) (f23 : p23) (f27 : p27) (r0 : p13 → p16 → p26 → p18) (r1 : p9 → p16 → p29 → p24) (r2 : p6 → p18 → p10) (r3 : p0 → p31 → p10) (r4 : p3 → p20) (r5 : p3 → p27 → p16) (r6 : p3 → p33 → p1) (r7 : p16 → p9) (r8 : p0 → p20 → p21 → p14) (r9 : p16 → p27 → p35) (r10 : p3 → p16 → p32 → p29) (r11 : p21 → p23 → p30 → p5) (r12 : p3 → p21 → p15) (r13 : p24 → p29 → p36) (r14 : p3 → p21 → p23 → p13) (r15 : p23 → p27 → p30) (r16 : p13 → p36 → p31) (r17 : p5 → p27 → p35 → p32) (r18 : p23 → p31 → p7) (r19 : p10 → p16 → p23 → p8) (r20 : p18 → p23 → p6) (r21 : p21 → p11) (r22 : p29 → p26) (r23 : p22 → p27 → p8) (r24 : p0 → p12 → p2) (r25 : p5 → p35 → p34) (r26 : p10 → p27 → p17) (r27 : p16 → p35) (r28 : p5 → p31 → p7) (r29 : p0 → p29 → p26) (r30 : p26 → p27 → p36) (r31 : p18 → p36 → p6) (r32 : p3 → p5 → p32) (r33 : p3 → p34 → p29) (r34 : p16 → p29 → p28) (r35 : p21 → p34 → p4) (r36 : p10 → p13 → p19) (r37 : p6 → p23 → p22) (r38 : p7 → p9 → p28 → p17) (r39 : p27 → p34 → p4) (r40 : p0 → p27 → p30) (r41 : p21 → p23 → p16) (r42 : p8 → p17 → p19 → p37) (r43 : p21 → p23 → p27 → p25) : p37 := by
  have h13 : p13 := r14 f3 f21 f23
  have h16 : p16 := r41 f21 f23
  have h9 : p9 := r7 h16
  have h35 : p35 := r27 h16
  have h30 : p30 := r15 f23 f27
  have h5 : p5 := r11 f21 f23 h30
  have h32 : p32 := r32 f3 h5
  have h29 : p29 := r10 f3 h16 h32
  have h28 : p28 := r34 h16 h29
  have h26 : p26 := r22 h29
  have h18 : p18 := r0 h13 h16 h26
  have h6 : p6 := r20 h18 f23
  have h22 : p22 := r37 h6 f23
  have h8 : p8 := r23 h22 f27
  have h10 : p10 := r2 h6 h18
  have h19 : p19 := r36 h10 h13
  have h17 : p17 := r26 h10 f27
  have h37 : p37 := r42 h8 h17 h19
  exact h37
#print axioms cogModel_60b31502abee8d9f5233bcb05305a3278aad956f4016379c42096e9c190563ac

theorem cogModel_89cb3470ca287603056c31c834d476413de4c72ef679e1fab252135f673ccd06 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 : Prop) (f3 : p3) (f6 : p6) (f31 : p31) (r0 : p23 → p31 → p13) (r1 : p6 → p5) (r2 : p6 → p26 → p1) (r3 : p3 → p24 → p29) (r4 : p1 → p31 → p20) (r5 : p6 → p21 → p2) (r6 : p6 → p31 → p12) (r7 : p12 → p25 → p7) (r8 : p4 → p33 → p0) (r9 : p3 → p18 → p33 → p21) (r10 : p6 → p36 → p11) (r11 : p4 → p18 → p26) (r12 : p27 → p31 → p24) (r13 : p34 → p38 → p35) (r14 : p2 → p6 → p4) (r15 : p3 → p31 → p33) (r16 : p2 → p31 → p7) (r17 : p21 → p32 → p2) (r18 : p3 → p14 → p27 → p37) (r19 : p6 → p28 → p17) (r20 : p0 → p24 → p29) (r21 : p6 → p7 → p0) (r22 : p6 → p33 → p32) (r23 : p1 → p3 → p20) (r24 : p3 → p20 → p14) (r25 : p15 → p29 → p37 → p10) (r26 : p3 → p31 → p12) (r27 : p14 → p21 → p31 → p15) (r28 : p31 → p33) (r29 : p1 → p11 → p33 → p14) (r30 : p31 → p18) (r31 : p3 → p34 → p8) (r32 : p0 → p6 → p31 → p1) (r33 : p21 → p25 → p36 → p27) (r34 : p18 → p31 → p32) (r35 : p12 → p21 → p26 → p36) (r36 : p6 → p34) (r37 : p34 → p30) (r38 : p6 → p9 → p16) (r39 : p7 → p31 → p26) (r40 : p1 → p31 → p27) (r41 : p14 → p31 → p37) (r42 : p7 → p11 → p24) (r43 : p6 → p31 → p38) (r44 : p18 → p32 → p25) (r45 : p3 → p22 → p19) : p10 := by
  have h33 : p33 := r15 f3 f31
  have h32 : p32 := r22 f6 h33
  have h18 : p18 := r30 f31
  have h21 : p21 := r9 f3 h18 h33
  have h2 : p2 := r17 h21 h32
  have h7 : p7 := r16 h2 f31
  have h0 : p0 := r21 f6 h7
  have h1 : p1 := r32 h0 f6 f31
  have h27 : p27 := r40 h1 f31
  have h24 : p24 := r12 h27 f31
  have h29 : p29 := r20 h0 h24
  have h20 : p20 := r4 h1 f31
  have h14 : p14 := r24 f3 h20
  have h37 : p37 := r41 h14 f31
  have h15 : p15 := r27 h14 h21 f31
  have h10 : p10 := r25 h15 h29 h37
  exact h10
#print axioms cogModel_89cb3470ca287603056c31c834d476413de4c72ef679e1fab252135f673ccd06

theorem cogModel_5982ac5b16307f2ec2ea94b98be414d87960a85a22956f1e5a8d4560d80ea4c5 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 : Prop) (f5 : p5) (f9 : p9) (f25 : p25) (r0 : p30 → p32 → p34 → p7) (r1 : p0 → p26 → p24) (r2 : p24 → p30 → p19) (r3 : p9 → p20 → p25 → p32) (r4 : p9 → p15 → p11) (r5 : p16 → p19 → p33 → p1) (r6 : p7 → p24 → p26 → p16) (r7 : p6 → p31 → p32 → p29) (r8 : p22 → p25 → p21) (r9 : p3 → p30 → p31 → p14) (r10 : p6 → p14 → p30 → p0) (r11 : p5 → p9 → p20) (r12 : p5 → p21 → p28) (r13 : p13 → p27 → p17) (r14 : p6 → p30 → p34 → p31) (r15 : p14 → p25 → p34 → p26) (r16 : p18 → p29 → p34 → p35) (r17 : p8 → p14 → p18) (r18 : p2 → p35 → p33) (r19 : p25 → p30) (r20 : p25 → p29 → p30 → p2) (r21 : p7 → p32 → p3) (r22 : p22 → p25 → p27 → p10) (r23 : p25 → p27) (r24 : p25 → p34) (r25 : p5 → p10 → p28 → p13) (r26 : p5 → p22) (r27 : p4 → p9 → p12) (r28 : p6 → p9 → p20 → p8) (r29 : p22 → p28 → p23) (r30 : p20 → p25 → p6) : p1 := by
  have h30 : p30 := r19 f25
  have h34 : p34 := r24 f25
  have h20 : p20 := r11 f5 f9
  have h6 : p6 := r30 h20 f25
  have h31 : p31 := r14 h6 h30 h34
  have h32 : p32 := r3 f9 h20 f25
  have h7 : p7 := r0 h30 h32 h34
  have h3 : p3 := r21 h7 h32
  have h14 : p14 := r9 h3 h30 h31
  have h26 : p26 := r15 h14 f25 h34
  have h0 : p0 := r10 h6 h14 h30
  have h24 : p24 := r1 h0 h26
  have h19 : p19 := r2 h24 h30
  have h16 : p16 := r6 h7 h24 h26
  have h29 : p29 := r7 h6 h31 h32
  have h2 : p2 := r20 f25 h29 h30
  have h8 : p8 := r28 h6 f9 h20
  have h18 : p18 := r17 h8 h14
  have h35 : p35 := r16 h18 h29 h34
  have h33 : p33 := r18 h2 h35
  have h1 : p1 := r5 h16 h19 h33
  exact h1
#print axioms cogModel_5982ac5b16307f2ec2ea94b98be414d87960a85a22956f1e5a8d4560d80ea4c5

theorem cogModel_0dc403a5e072c32a6adcd6c6c5ec3fc64a69b34589fd5669c798b6edcef3662e (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 p41 p42 : Prop) (f8 : p8) (f13 : p13) (f16 : p16) (f19 : p19) (f36 : p36) (r0 : p0 → p12 → p41) (r1 : p10 → p39 → p17) (r2 : p19 → p23 → p27) (r3 : p6 → p30) (r4 : p19 → p2) (r5 : p3 → p23 → p29) (r6 : p14 → p19 → p26) (r7 : p4 → p15 → p32) (r8 : p12 → p13 → p27 → p5) (r9 : p6 → p24) (r10 : p13 → p36 → p40 → p3) (r11 : p16 → p6) (r12 : p3 → p5 → p40 → p18) (r13 : p11 → p13 → p0) (r14 : p19 → p35) (r15 : p1 → p19 → p37) (r16 : p5 → p19 → p15) (r17 : p0 → p9 → p39 → p34) (r18 : p16 → p33 → p20) (r19 : p8 → p13 → p19 → p10) (r20 : p24 → p36 → p21) (r21 : p15 → p27 → p31) (r22 : p9 → p23 → p12) (r23 : p25 → p31 → p32 → p42) (r24 : p0 → p5 → p4) (r25 : p16 → p7) (r26 : p9 → p13 → p23 → p38) (r27 : p13 → p23 → p40 → p39) (r28 : p0 → p18 → p40 → p25) (r29 : p8 → p11 → p9) (r30 : p8 → p19 → p36 → p23) (r31 : p36 → p28) (r32 : p19 → p22) (r33 : p3 → p23 → p39 → p11) (r34 : p8 → p13 → p16 → p40) : p42 := by
  have h40 : p40 := r34 f8 f13 f16
  have h3 : p3 := r10 f13 f36 h40
  have h23 : p23 := r30 f8 f19 f36
  have h27 : p27 := r2 f19 h23
  have h39 : p39 := r27 f13 h23 h40
  have h11 : p11 := r33 h3 h23 h39
  have h0 : p0 := r13 h11 f13
  have h9 : p9 := r29 f8 h11
  have h12 : p12 := r22 h9 h23
  have h5 : p5 := r8 h12 f13 h27
  have h15 : p15 := r16 h5 f19
  have h31 : p31 := r21 h15 h27
  have h4 : p4 := r24 h0 h5
  have h32 : p32 := r7 h4 h15
  have h18 : p18 := r12 h3 h5 h40
  have h25 : p25 := r28 h0 h18 h40
  have h42 : p42 := r23 h25 h31 h32
  exact h42
#print axioms cogModel_0dc403a5e072c32a6adcd6c6c5ec3fc64a69b34589fd5669c798b6edcef3662e

theorem cogModel_c57ff600499247d056136a661df27ef1acd107eb9eed7f6a41d76986547afbe7 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 p41 p42 : Prop) (f6 : p6) (f10 : p10) (f30 : p30) (r0 : p17 → p37 → p20) (r1 : p4 → p30 → p37) (r2 : p2 → p30 → p5) (r3 : p1 → p23) (r4 : p6 → p10 → p38 → p42) (r5 : p37 → p42 → p17) (r6 : p4 → p10 → p35) (r7 : p6 → p25 → p29) (r8 : p13 → p40 → p42 → p34) (r9 : p37 → p38 → p9) (r10 : p9 → p10 → p13) (r11 : p6 → p10 → p38) (r12 : p13 → p37 → p14) (r13 : p6 → p0) (r14 : p26 → p38 → p11) (r15 : p13 → p30 → p39) (r16 : p13 → p38 → p39 → p2) (r17 : p10 → p30 → p16) (r18 : p31 → p34 → p19) (r19 : p6 → p30 → p4) (r20 : p6 → p10 → p20 → p36) (r21 : p0 → p7) (r22 : p5 → p13 → p12) (r23 : p18 → p30 → p32) (r24 : p6 → p10 → p21) (r25 : p17 → p37 → p39 → p28) (r26 : p0 → p16 → p30 → p22) (r27 : p2 → p36 → p27) (r28 : p5 → p26 → p36 → p40) (r29 : p33 → p37 → p26) (r30 : p16 → p1) (r31 : p14 → p38 → p39 → p33) (r32 : p15 → p30 → p3) (r33 : p10 → p30 → p41) (r34 : p10 → p40 → p31) (r35 : p8 → p30 → p24) : p19 := by
  have h4 : p4 := r19 f6 f30
  have h35 : p35 := r6 h4 f10
  have h38 : p38 := r11 f6 f10
  have h42 : p42 := r4 f6 f10 h38
  have h37 : p37 := r1 h4 f30
  have h9 : p9 := r9 h37 h38
  have h13 : p13 := r10 h9 f10
  have h14 : p14 := r12 h13 h37
  have h17 : p17 := r5 h37 h42
  have h20 : p20 := r0 h17 h37
  have h36 : p36 := r20 f6 f10 h20
  have h39 : p39 := r15 h13 f30
  have h33 : p33 := r31 h14 h38 h39
  have h26 : p26 := r29 h33 h37
  have h2 : p2 := r16 h13 h38 h39
  have h5 : p5 := r2 h2 f30
  have h40 : p40 := r28 h5 h26 h36
  have h31 : p31 := r34 f10 h40
  have h34 : p34 := r8 h13 h40 h42
  have h19 : p19 := r18 h31 h34
  exact h19
#print axioms cogModel_c57ff600499247d056136a661df27ef1acd107eb9eed7f6a41d76986547afbe7

theorem cogModel_c5614e155c194d37adb16180db65554c18daa0e01c0c3764797854e2a2ebec85 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 p41 p42 p43 p44 p45 p46 p47 : Prop) (f14 : p14) (f18 : p18) (f43 : p43) (r0 : p5 → p31 → p37) (r1 : p28 → p43 → p15) (r2 : p43 → p19) (r3 : p19 → p43 → p45 → p12) (r4 : p19 → p43 → p45) (r5 : p17 → p43 → p9) (r6 : p7 → p40 → p25) (r7 : p29 → p32 → p47) (r8 : p20 → p32 → p35) (r9 : p14 → p19 → p43 → p42) (r10 : p18 → p8) (r11 : p3 → p14 → p0) (r12 : p18 → p19 → p26 → p17) (r13 : p44 → p40) (r14 : p14 → p43 → p32) (r15 : p8 → p14 → p1) (r16 : p11 → p12 → p36) (r17 : p18 → p43 → p45 → p6) (r18 : p32 → p39 → p13) (r19 : p9 → p11 → p45 → p30) (r20 : p14 → p24 → p10) (r21 : p2 → p18 → p4) (r22 : p1 → p20 → p32 → p2) (r23 : p1 → p35 → p24) (r24 : p26 → p21) (r25 : p14 → p34 → p27) (r26 : p1 → p43 → p5) (r27 : p14 → p41) (r28 : p17 → p19 → p42 → p46) (r29 : p2 → p37 → p44) (r30 : p29 → p35 → p39) (r31 : p38 → p43 → p23) (r32 : p11 → p43 → p46 → p33) (r33 : p4 → p5 → p8 → p31) (r34 : p9 → p22 → p16) (r35 : p4 → p5 → p32 → p29) (r36 : p18 → p43 → p20) (r37 : p18 → p26) (r38 : p17 → p26 → p11) (r39 : p5 → p13 → p47 → p7) (r40 : p14 → p18 → p36 → p22) : p25 := by
  have h41 : p41 := r27 f14
  have h32 : p32 := r14 f14 f43
  have h20 : p20 := r36 f18 f43
  have h35 : p35 := r8 h20 h32
  have h8 : p8 := r10 f18
  have h1 : p1 := r15 h8 f14
  have h5 : p5 := r26 h1 f43
  have h2 : p2 := r22 h1 h20 h32
  have h4 : p4 := r21 h2 f18
  have h29 : p29 := r35 h4 h5 h32
  have h47 : p47 := r7 h29 h32
  have h39 : p39 := r30 h29 h35
  have h13 : p13 := r18 h32 h39
  have h7 : p7 := r39 h5 h13 h47
  have h31 : p31 := r33 h4 h5 h8
  have h37 : p37 := r0 h5 h31
  have h44 : p44 := r29 h2 h37
  have h40 : p40 := r13 h44
  have h25 : p25 := r6 h7 h40
  exact h25
#print axioms cogModel_c5614e155c194d37adb16180db65554c18daa0e01c0c3764797854e2a2ebec85

theorem cogModel_0de1fdb835132f9e0e1046f4b0d2a3100aa5587570e1b80f1d4157e9d804b4d5 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 : Prop) (f2 : p2) (f9 : p9) (f15 : p15) (f26 : p26) (r0 : p2 → p9 → p26 → p16) (r1 : p26 → p29 → p31) (r2 : p1 → p26 → p10) (r3 : p2 → p15 → p32) (r4 : p2 → p9 → p26 → p8) (r5 : p11 → p15 → p35) (r6 : p1 → p8 → p5) (r7 : p8 → p25 → p38) (r8 : p21 → p26 → p6) (r9 : p1 → p8 → p33 → p3) (r10 : p34 → p36 → p33) (r11 : p15 → p13) (r12 : p7 → p24 → p11) (r13 : p2 → p20 → p38 → p36) (r14 : p13 → p15 → p19 → p0) (r15 : p14 → p28 → p37 → p30) (r16 : p2 → p9 → p25) (r17 : p2 → p26 → p29) (r18 : p9 → p24) (r19 : p2 → p8 → p9 → p20) (r20 : p0 → p13 → p19 → p22) (r21 : p9 → p16 → p26 → p4) (r22 : p8 → p17 → p25 → p14) (r23 : p9 → p17 → p18 → p28) (r24 : p12 → p18 → p17) (r25 : p20 → p35 → p18) (r26 : p2 → p9 → p10 → p34) (r27 : p2 → p24 → p38 → p1) (r28 : p11 → p34 → p12) (r29 : p23 → p26 → p27) (r30 : p2 → p26 → p38 → p7) (r31 : p17 → p35 → p37) (r32 : p15 → p16 → p26 → p19) : p30 := by
  have h25 : p25 := r16 f2 f9
  have h8 : p8 := r4 f2 f9 f26
  have h20 : p20 := r19 f2 h8 f9
  have h24 : p24 := r18 f9
  have h38 : p38 := r7 h8 h25
  have h7 : p7 := r30 f2 f26 h38
  have h11 : p11 := r12 h7 h24
  have h35 : p35 := r5 h11 f15
  have h18 : p18 := r25 h20 h35
  have h1 : p1 := r27 f2 h24 h38
  have h10 : p10 := r2 h1 f26
  have h34 : p34 := r26 f2 f9 h10
  have h12 : p12 := r28 h11 h34
  have h17 : p17 := r24 h12 h18
  have h37 : p37 := r31 h17 h35
  have h14 : p14 := r22 h8 h17 h25
  have h28 : p28 := r23 f9 h17 h18
  have h30 : p30 := r15 h14 h28 h37
  exact h30
#print axioms cogModel_0de1fdb835132f9e0e1046f4b0d2a3100aa5587570e1b80f1d4157e9d804b4d5

theorem cogModel_4458bc22c05a6f329064554b38b8e0b559d9f069d1b81453467a1bccf73540a5 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 : Prop) (f4 : p4) (f11 : p11) (f12 : p12) (f20 : p20) (r0 : p6 → p10 → p16 → p22) (r1 : p2 → p12 → p33) (r2 : p20 → p31 → p17) (r3 : p11 → p30 → p23) (r4 : p4 → p12 → p20 → p27) (r5 : p11 → p14 → p21) (r6 : p10 → p12 → p31 → p26) (r7 : p11 → p13 → p9) (r8 : p2 → p3 → p16 → p6) (r9 : p4 → p12 → p14) (r10 : p11 → p20 → p25 → p16) (r11 : p5 → p31 → p24) (r12 : p3 → p20 → p10) (r13 : p0 → p30 → p2) (r14 : p0 → p25 → p3) (r15 : p11 → p25 → p0) (r16 : p25 → p30 → p33 → p31) (r17 : p24 → p28 → p32) (r18 : p11 → p20 → p29) (r19 : p12 → p21 → p1) (r20 : p0 → p11 → p26 → p28) (r21 : p6 → p10 → p20 → p8) (r22 : p11 → p20 → p7) (r23 : p0 → p20 → p18) (r24 : p4 → p11 → p30) (r25 : p11 → p30 → p25) (r26 : p15 → p20 → p19) (r27 : p4 → p18 → p22 → p5) : p32 := by
  have h30 : p30 := r24 f4 f11
  have h25 : p25 := r25 f11 h30
  have h0 : p0 := r15 f11 h25
  have h18 : p18 := r23 h0 f20
  have h2 : p2 := r13 h0 h30
  have h33 : p33 := r1 h2 f12
  have h31 : p31 := r16 h25 h30 h33
  have h3 : p3 := r14 h0 h25
  have h10 : p10 := r12 h3 f20
  have h26 : p26 := r6 h10 f12 h31
  have h28 : p28 := r20 h0 f11 h26
  have h16 : p16 := r10 f11 f20 h25
  have h6 : p6 := r8 h2 h3 h16
  have h22 : p22 := r0 h6 h10 h16
  have h5 : p5 := r27 f4 h18 h22
  have h24 : p24 := r11 h5 h31
  have h32 : p32 := r17 h24 h28
  exact h32
#print axioms cogModel_4458bc22c05a6f329064554b38b8e0b559d9f069d1b81453467a1bccf73540a5

theorem cogModel_2b96929005d7a42f6b0a4a7ea8e514ecdb51f1953376fddc1fcf9838d34c2c0f (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 : Prop) (f8 : p8) (f18 : p18) (f20 : p20) (f21 : p21) (r0 : p11 → p15) (r1 : p8 → p18 → p21 → p16) (r2 : p21 → p11) (r3 : p9 → p13) (r4 : p8 → p16 → p21 → p6) (r5 : p2 → p19) (r6 : p13 → p4) (r7 : p4 → p3) (r8 : p18 → p20 → p21 → p2) (r9 : p0 → p22) (r10 : p15 → p0) (r11 : p16 → p21 → p10) (r12 : p22 → p9) (r13 : p17 → p18 → p12) (r14 : p7 → p8 → p1) (r15 : p5 → p20 → p14) : p3 := by
  have h11 : p11 := r2 f21
  have h15 : p15 := r0 h11
  have h0 : p0 := r10 h15
  have h22 : p22 := r9 h0
  have h9 : p9 := r12 h22
  have h13 : p13 := r3 h9
  have h4 : p4 := r6 h13
  have h3 : p3 := r7 h4
  exact h3
#print axioms cogModel_2b96929005d7a42f6b0a4a7ea8e514ecdb51f1953376fddc1fcf9838d34c2c0f

theorem cogModel_f615b23f813766f1fa6e5f58fbb67972ceff8e4164761dc051771f2517c32981 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 : Prop) (f13 : p13) (f15 : p15) (f17 : p17) (f37 : p37) (r0 : p12 → p17 → p37 → p24) (r1 : p15 → p31 → p28) (r2 : p1 → p10 → p34) (r3 : p7 → p35) (r4 : p5 → p10 → p17 → p9) (r5 : p12 → p30 → p5) (r6 : p16 → p38 → p6) (r7 : p13 → p27 → p14) (r8 : p9 → p27 → p1) (r9 : p14 → p15 → p0) (r10 : p13 → p15 → p31 → p3) (r11 : p17 → p36 → p2) (r12 : p13 → p37 → p20) (r13 : p17 → p37 → p27) (r14 : p13 → p31 → p19) (r15 : p14 → p15 → p30) (r16 : p17 → p20 → p12) (r17 : p0 → p10 → p21) (r18 : p15 → p33 → p32) (r19 : p11 → p17 → p25) (r20 : p15 → p29 → p4) (r21 : p17 → p37 → p31) (r22 : p13 → p17 → p37 → p10) (r23 : p27 → p34 → p38) (r24 : p13 → p26 → p18) (r25 : p1 → p14 → p30 → p23) (r26 : p2 → p15 → p21 → p8) (r27 : p13 → p20 → p21 → p36) (r28 : p15 → p17 → p7) (r29 : p37 → p22) (r30 : p8 → p34 → p16) : p6 := by
  have h27 : p27 := r13 f17 f37
  have h10 : p10 := r22 f13 f17 f37
  have h20 : p20 := r12 f13 f37
  have h12 : p12 := r16 f17 h20
  have h14 : p14 := r7 f13 h27
  have h0 : p0 := r9 h14 f15
  have h21 : p21 := r17 h0 h10
  have h36 : p36 := r27 f13 h20 h21
  have h2 : p2 := r11 f17 h36
  have h8 : p8 := r26 h2 f15 h21
  have h30 : p30 := r15 h14 f15
  have h5 : p5 := r5 h12 h30
  have h9 : p9 := r4 h5 h10 f17
  have h1 : p1 := r8 h9 h27
  have h34 : p34 := r2 h1 h10
  have h16 : p16 := r30 h8 h34
  have h38 : p38 := r23 h27 h34
  have h6 : p6 := r6 h16 h38
  exact h6
#print axioms cogModel_f615b23f813766f1fa6e5f58fbb67972ceff8e4164761dc051771f2517c32981

theorem cogModel_1a85a460e428111f9077409b36cd4f54c35e5f6eb02c20b1efc378d720634ed1 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 : Prop) (f2 : p2) (f3 : p3) (f20 : p20) (r0 : p5 → p9) (r1 : p9 → p13) (r2 : p16 → p6) (r3 : p0 → p20 → p19) (r4 : p6 → p12) (r5 : p12 → p5) (r6 : p15 → p20 → p10) (r7 : p4 → p7) (r8 : p14 → p18) (r9 : p2 → p3 → p20 → p1) (r10 : p13 → p14) (r11 : p2 → p21) (r12 : p7 → p16) (r13 : p1 → p3 → p20 → p17) (r14 : p3 → p17 → p8) (r15 : p3 → p4) (r16 : p3 → p8 → p17 → p11) : p18 := by
  have h4 : p4 := r15 f3
  have h7 : p7 := r7 h4
  have h16 : p16 := r12 h7
  have h6 : p6 := r2 h16
  have h12 : p12 := r4 h6
  have h5 : p5 := r5 h12
  have h9 : p9 := r0 h5
  have h13 : p13 := r1 h9
  have h14 : p14 := r10 h13
  have h18 : p18 := r8 h14
  exact h18
#print axioms cogModel_1a85a460e428111f9077409b36cd4f54c35e5f6eb02c20b1efc378d720634ed1

theorem cogModel_df5270a25f3e5b5dee135e334b74390df581e0e81172727a0b151f09fe46ae21 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 : Prop) (f5 : p5) (f6 : p6) (f8 : p8) (f9 : p9) (f17 : p17) (r0 : p8 → p12) (r1 : p2 → p20) (r2 : p13 → p28) (r3 : p9 → p16 → p26) (r4 : p7 → p21) (r5 : p9 → p14 → p27) (r6 : p5 → p7) (r7 : p23 → p10) (r8 : p16 → p19) (r9 : p8 → p25) (r10 : p5 → p6 → p17 → p2) (r11 : p22 → p13) (r12 : p8 → p11 → p0) (r13 : p16 → p18 → p19 → p15) (r14 : p17 → p16) (r15 : p3 → p23) (r16 : p5 → p24 → p4) (r17 : p28 → p3) (r18 : p1 → p22) (r19 : p21 → p1) (r20 : p5 → p20 → p18) : p10 := by
  have h7 : p7 := r6 f5
  have h21 : p21 := r4 h7
  have h1 : p1 := r19 h21
  have h22 : p22 := r18 h1
  have h13 : p13 := r11 h22
  have h28 : p28 := r2 h13
  have h3 : p3 := r17 h28
  have h23 : p23 := r15 h3
  have h10 : p10 := r7 h23
  exact h10
#print axioms cogModel_df5270a25f3e5b5dee135e334b74390df581e0e81172727a0b151f09fe46ae21

theorem cogModel_cca96bd0baa89ff4503ec8db05ea7ded1d8079ea78731c0fc64cd338c4a9f52e (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 : Prop) (f0 : p0) (f10 : p10) (f25 : p25) (f28 : p28) (f34 : p34) (r0 : p0 → p25 → p34 → p22) (r1 : p0 → p9 → p23) (r2 : p2 → p36) (r3 : p16 → p25 → p27 → p31) (r4 : p10 → p12) (r5 : p17 → p28 → p8) (r6 : p22 → p13) (r7 : p16 → p34 → p19) (r8 : p7 → p28 → p35) (r9 : p0 → p10 → p34 → p16) (r10 : p1 → p8 → p33 → p15) (r11 : p2 → p3 → p12 → p20) (r12 : p0 → p12 → p3) (r13 : p28 → p29) (r14 : p25 → p34 → p4) (r15 : p34 → p2) (r16 : p16 → p17 → p1) (r17 : p5 → p21 → p31 → p37) (r18 : p19 → p27 → p31 → p21) (r19 : p5 → p10 → p11 → p17) (r20 : p12 → p28 → p29 → p9) (r21 : p0 → p30) (r22 : p19 → p28 → p31 → p5) (r23 : p11 → p28 → p37 → p26) (r24 : p5 → p21 → p28 → p11) (r25 : p4 → p13 → p28 → p32) (r26 : p11 → p17 → p33) (r27 : p0 → p28 → p34 → p27) (r28 : p14 → p28 → p6) (r29 : p25 → p24) (r30 : p2 → p10 → p34 → p18) : p15 := by
  have h16 : p16 := r9 f0 f10 f34
  have h19 : p19 := r7 h16 f34
  have h27 : p27 := r27 f0 f28 f34
  have h31 : p31 := r3 h16 f25 h27
  have h5 : p5 := r22 h19 f28 h31
  have h21 : p21 := r18 h19 h27 h31
  have h11 : p11 := r24 h5 h21 f28
  have h17 : p17 := r19 h5 f10 h11
  have h33 : p33 := r26 h11 h17
  have h1 : p1 := r16 h16 h17
  have h8 : p8 := r5 h17 f28
  have h15 : p15 := r10 h1 h8 h33
  exact h15
#print axioms cogModel_cca96bd0baa89ff4503ec8db05ea7ded1d8079ea78731c0fc64cd338c4a9f52e

theorem cogModel_64d4bc63d3faf37db4ef8ef58905aff0ba4e257a66dfbb96e3966c62d5fb8d18 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 : Prop) (f12 : p12) (f14 : p14) (f22 : p22) (f30 : p30) (r0 : p14 → p22 → p30 → p3) (r1 : p1 → p30 → p26) (r2 : p13 → p25 → p23) (r3 : p5 → p23 → p25 → p15) (r4 : p1 → p30 → p29) (r5 : p12 → p18 → p25 → p10) (r6 : p14 → p4) (r7 : p12 → p22 → p28 → p16) (r8 : p22 → p31 → p21) (r9 : p14 → p27 → p0) (r10 : p12 → p29 → p8) (r11 : p3 → p14 → p22 → p27) (r12 : p12 → p26 → p18) (r13 : p12 → p22 → p25) (r14 : p8 → p14 → p10) (r15 : p12 → p35 → p33) (r16 : p3 → p12 → p30 → p13) (r17 : p3 → p22 → p23 → p9) (r18 : p2 → p10 → p11) (r19 : p3 → p12 → p27) (r20 : p15 → p27 → p26) (r21 : p0 → p8 → p12 → p2) (r22 : p8 → p14 → p2) (r23 : p1 → p15 → p29) (r24 : p12 → p34 → p32) (r25 : p14 → p33 → p1) (r26 : p14 → p28 → p34) (r27 : p0 → p12 → p7) (r28 : p7 → p30 → p5) (r29 : p7 → p23 → p5) (r30 : p6 → p12 → p24) (r31 : p12 → p17 → p19) (r32 : p22 → p30 → p6) (r33 : p0 → p22 → p30 → p7) (r34 : p9 → p13 → p33 → p20) (r35 : p22 → p25) (r36 : p22 → p23 → p35) (r37 : p29 → p30 → p8) (r38 : p14 → p22 → p28) : p11 := by
  have h25 : p25 := r35 f22
  have h4 : p4 := r6 f14
  have h3 : p3 := r0 f14 f22 f30
  have h27 : p27 := r19 h3 f12
  have h0 : p0 := r9 f14 h27
  have h7 : p7 := r27 h0 f12
  have h5 : p5 := r28 h7 f30
  have h13 : p13 := r16 h3 f12 f30
  have h23 : p23 := r2 h13 h25
  have h15 : p15 := r3 h5 h23 h25
  have h26 : p26 := r20 h15 h27
  have h18 : p18 := r12 f12 h26
  have h10 : p10 := r5 f12 h18 h25
  have h35 : p35 := r36 f22 h23
  have h33 : p33 := r15 f12 h35
  have h1 : p1 := r25 f14 h33
  have h29 : p29 := r23 h1 h15
  have h8 : p8 := r37 h29 f30
  have h2 : p2 := r22 h8 f14
  have h11 : p11 := r18 h2 h10
  exact h11
#print axioms cogModel_64d4bc63d3faf37db4ef8ef58905aff0ba4e257a66dfbb96e3966c62d5fb8d18

theorem cogModel_385c2566cb2b5f7edc9b0ab483c2601c006692067d88405e36094760d77b8df8 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 : Prop) (f3 : p3) (f5 : p5) (f22 : p22) (r0 : p12 → p21 → p25 → p4) (r1 : p1 → p32 → p14) (r2 : p0 → p8 → p9) (r3 : p3 → p21 → p0) (r4 : p2 → p5 → p10) (r5 : p9 → p11 → p6) (r6 : p5 → p18 → p22 → p35) (r7 : p7 → p18 → p30 → p25) (r8 : p36 → p27) (r9 : p3 → p24 → p30 → p21) (r10 : p2 → p3 → p26) (r11 : p20 → p22 → p16) (r12 : p5 → p20 → p38) (r13 : p2 → p5 → p23) (r14 : p8 → p18 → p35 → p7) (r15 : p1 → p3 → p8) (r16 : p5 → p18 → p12) (r17 : p9 → p21 → p15) (r18 : p5 → p22 → p18) (r19 : p5 → p17 → p31) (r20 : p12 → p22 → p30) (r21 : p2 → p5 → p13) (r22 : p5 → p22 → p20) (r23 : p5 → p22 → p1) (r24 : p6 → p15 → p19 → p34) (r25 : p5 → p28) (r26 : p10 → p36) (r27 : p3 → p25 → p32) (r28 : p3 → p12 → p35 → p24) (r29 : p3 → p5 → p22 → p29) (r30 : p22 → p33 → p37) (r31 : p3 → p4 → p7 → p11) (r32 : p5 → p8 → p14 → p19) (r33 : p3 → p2) : p34 := by
  have h1 : p1 := r23 f5 f22
  have h8 : p8 := r15 h1 f3
  have h18 : p18 := r18 f5 f22
  have h12 : p12 := r16 f5 h18
  have h30 : p30 := r20 h12 f22
  have h35 : p35 := r6 f5 h18 f22
  have h7 : p7 := r14 h8 h18 h35
  have h25 : p25 := r7 h7 h18 h30
  have h32 : p32 := r27 f3 h25
  have h14 : p14 := r1 h1 h32
  have h19 : p19 := r32 f5 h8 h14
  have h24 : p24 := r28 f3 h12 h35
  have h21 : p21 := r9 f3 h24 h30
  have h0 : p0 := r3 f3 h21
  have h9 : p9 := r2 h0 h8
  have h15 : p15 := r17 h9 h21
  have h4 : p4 := r0 h12 h21 h25
  have h11 : p11 := r31 f3 h4 h7
  have h6 : p6 := r5 h9 h11
  have h34 : p34 := r24 h6 h15 h19
  exact h34
#print axioms cogModel_385c2566cb2b5f7edc9b0ab483c2601c006692067d88405e36094760d77b8df8

theorem cogModel_7ea566e22ce541242dac5ef2b3cb455e775fd9f19f132b692f2f69a090d62f81 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 p41 : Prop) (f12 : p12) (f33 : p33) (f38 : p38) (r0 : p38 → p37) (r1 : p22 → p33 → p13) (r2 : p11 → p16 → p33 → p41) (r3 : p9 → p34 → p24) (r4 : p0 → p5 → p18 → p4) (r5 : p30 → p33 → p38 → p27) (r6 : p24 → p33 → p38 → p8) (r7 : p1 → p4 → p10 → p6) (r8 : p33 → p21) (r9 : p33 → p38 → p17) (r10 : p16 → p29) (r11 : p16 → p37 → p38 → p39) (r12 : p9 → p28 → p18) (r13 : p25 → p38 → p30) (r14 : p33 → p36 → p15) (r15 : p2 → p5 → p38 → p34) (r16 : p23 → p9) (r17 : p7 → p12 → p19) (r18 : p12 → p37 → p11) (r19 : p12 → p33 → p25) (r20 : p5 → p27 → p32 → p28) (r21 : p12 → p13 → p38 → p7) (r22 : p13 → p22 → p37 → p31) (r23 : p5 → p12 → p25 → p2) (r24 : p0 → p9 → p10) (r25 : p7 → p33 → p39 → p40) (r26 : p12 → p33 → p38 → p5) (r27 : p8 → p30 → p0) (r28 : p12 → p33 → p38 → p16) (r29 : p31 → p41 → p3) (r30 : p12 → p18 → p33 → p1) (r31 : p14 → p33 → p20) (r32 : p5 → p8 → p28 → p26) (r33 : p12 → p27 → p38 → p32) (r34 : p16 → p33 → p22) (r35 : p5 → p25 → p23) (r36 : p7 → p33 → p35) : p6 := by
  have h5 : p5 := r26 f12 f33 f38
  have h25 : p25 := r19 f12 f33
  have h30 : p30 := r13 h25 f38
  have h23 : p23 := r35 h5 h25
  have h9 : p9 := r16 h23
  have h27 : p27 := r5 h30 f33 f38
  have h32 : p32 := r33 f12 h27 f38
  have h28 : p28 := r20 h5 h27 h32
  have h18 : p18 := r12 h9 h28
  have h1 : p1 := r30 f12 h18 f33
  have h2 : p2 := r23 h5 f12 h25
  have h34 : p34 := r15 h2 h5 f38
  have h24 : p24 := r3 h9 h34
  have h8 : p8 := r6 h24 f33 f38
  have h0 : p0 := r27 h8 h30
  have h10 : p10 := r24 h0 h9
  have h4 : p4 := r4 h0 h5 h18
  have h6 : p6 := r7 h1 h4 h10
  exact h6
#print axioms cogModel_7ea566e22ce541242dac5ef2b3cb455e775fd9f19f132b692f2f69a090d62f81

theorem cogModel_06eb02a3337a8f0a59253b4ecf4a427f20bb2b738582228597807069036e643a (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 p41 p42 p43 p44 p45 p46 p47 p48 : Prop) (f2 : p2) (f17 : p17) (f24 : p24) (f42 : p42) (r0 : p25 → p39 → p4) (r1 : p1 → p2 → p47) (r2 : p24 → p42 → p43) (r3 : p1 → p5 → p36 → p6) (r4 : p1 → p18 → p48) (r5 : p2 → p23 → p24 → p20) (r6 : p5 → p27 → p36 → p46) (r7 : p2 → p26 → p42 → p41) (r8 : p2 → p7 → p23 → p29) (r9 : p13 → p23 → p3) (r10 : p2 → p14 → p16) (r11 : p2 → p37 → p34) (r12 : p20 → p29 → p11) (r13 : p17 → p21 → p10) (r14 : p24 → p41 → p42 → p32) (r15 : p17 → p36) (r16 : p17 → p35 → p8) (r17 : p26 → p18) (r18 : p12 → p37 → p39) (r19 : p17 → p26) (r20 : p15 → p23 → p33 → p35) (r21 : p1 → p5) (r22 : p1 → p26 → p27 → p22) (r23 : p24 → p35 → p43 → p12) (r24 : p2 → p24 → p40) (r25 : p24 → p40 → p42 → p23) (r26 : p17 → p31) (r27 : p7 → p34 → p13) (r28 : p32 → p42 → p46 → p19) (r29 : p2 → p44 → p7) (r30 : p15 → p37 → p38) (r31 : p2 → p24 → p42 → p44) (r32 : p17 → p41 → p27) (r33 : p20 → p37 → p40 → p9) (r34 : p2 → p41 → p42 → p1) (r35 : p3 → p43 → p30) (r36 : p9 → p30 → p34 → p25) (r37 : p26 → p0) (r38 : p24 → p45 → p28) (r39 : p23 → p43 → p37) (r40 : p9 → p20 → p15) (r41 : p9 → p44 → p33) : p4 := by
  have h43 : p43 := r2 f24 f42
  have h40 : p40 := r24 f2 f24
  have h23 : p23 := r25 f24 h40 f42
  have h37 : p37 := r39 h23 h43
  have h34 : p34 := r11 f2 h37
  have h20 : p20 := r5 f2 h23 f24
  have h9 : p9 := r33 h20 h37 h40
  have h15 : p15 := r40 h9 h20
  have h44 : p44 := r31 f2 f24 f42
  have h33 : p33 := r41 h9 h44
  have h35 : p35 := r20 h15 h23 h33
  have h12 : p12 := r23 f24 h35 h43
  have h39 : p39 := r18 h12 h37
  have h7 : p7 := r29 f2 h44
  have h13 : p13 := r27 h7 h34
  have h3 : p3 := r9 h13 h23
  have h30 : p30 := r35 h3 h43
  have h25 : p25 := r36 h9 h30 h34
  have h4 : p4 := r0 h25 h39
  exact h4
#print axioms cogModel_06eb02a3337a8f0a59253b4ecf4a427f20bb2b738582228597807069036e643a

theorem cogModel_8473f25d7025da91c532013ca89cf56847a968c424dc2fbad20fc70fec8ee650 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 : Prop) (f1 : p1) (f3 : p3) (f5 : p5) (f13 : p13) (f24 : p24) (r0 : p15 → p24 → p4) (r1 : p16 → p23) (r2 : p12 → p18) (r3 : p1 → p5 → p19 → p22) (r4 : p19 → p25) (r5 : p23 → p8) (r6 : p18 → p21) (r7 : p3 → p17) (r8 : p5 → p10 → p14) (r9 : p1 → p10) (r10 : p2 → p6) (r11 : p10 → p20) (r12 : p8 → p12) (r13 : p0 → p1 → p7) (r14 : p3 → p13 → p22 → p11) (r15 : p21 → p2) (r16 : p3 → p16) (r17 : p6 → p9) (r18 : p13 → p19) : p9 := by
  have h16 : p16 := r16 f3
  have h23 : p23 := r1 h16
  have h8 : p8 := r5 h23
  have h12 : p12 := r12 h8
  have h18 : p18 := r2 h12
  have h21 : p21 := r6 h18
  have h2 : p2 := r15 h21
  have h6 : p6 := r10 h2
  have h9 : p9 := r17 h6
  exact h9
#print axioms cogModel_8473f25d7025da91c532013ca89cf56847a968c424dc2fbad20fc70fec8ee650

theorem cogModel_e6f3cb529eea22fb3ab2f22ebacca0eba086bfb7dc2e62bade290c4b8d5d97db (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 p38 p39 p40 : Prop) (f8 : p8) (f19 : p19) (f22 : p22) (f31 : p31) (f37 : p37) (r0 : p8 → p11 → p1) (r1 : p19 → p26 → p27 → p12) (r2 : p1 → p4 → p8 → p28) (r3 : p8 → p24 → p17) (r4 : p14 → p27 → p3) (r5 : p8 → p9 → p11) (r6 : p14 → p24 → p17) (r7 : p20 → p22 → p33 → p15) (r8 : p3 → p10 → p9) (r9 : p8 → p20 → p31 → p38) (r10 : p13 → p19 → p1) (r11 : p2 → p6 → p37 → p5) (r12 : p22 → p31 → p14) (r13 : p19 → p22 → p2) (r14 : p10 → p22 → p12) (r15 : p14 → p26 → p10) (r16 : p22 → p31 → p37 → p24) (r17 : p1 → p36 → p0) (r18 : p29 → p32 → p35) (r19 : p32 → p37 → p35) (r20 : p2 → p8 → p19 → p33) (r21 : p9 → p37 → p11) (r22 : p1 → p22 → p28) (r23 : p9 → p26 → p32) (r24 : p26 → p27 → p36 → p29) (r25 : p19 → p31 → p36) (r26 : p3 → p36 → p4) (r27 : p8 → p19 → p20) (r28 : p17 → p37 → p27) (r29 : p9 → p24 → p13) (r30 : p22 → p26 → p27) (r31 : p2 → p38 → p21) (r32 : p22 → p34 → p23) (r33 : p9 → p37 → p13) (r34 : p8 → p37 → p24) (r35 : p26 → p37 → p10) (r36 : p25 → p31 → p39) (r37 : p14 → p19 → p24 → p26) (r38 : p29 → p37 → p9) (r39 : p18 → p31 → p30) (r40 : p8 → p10 → p29) (r41 : p10 → p19 → p3) (r42 : p8 → p22 → p35 → p7) (r43 : p6 → p8 → p37 → p40) (r44 : p19 → p14) (r45 : p1 → p22 → p0) (r46 : p31 → p6) (r47 : p0 → p7 → p28 → p16) : p16 := by
  have h36 : p36 := r25 f19 f31
  have h24 : p24 := r34 f8 f37
  have h17 : p17 := r3 f8 h24
  have h27 : p27 := r28 h17 f37
  have h14 : p14 := r44 f19
  have h3 : p3 := r4 h14 h27
  have h4 : p4 := r26 h3 h36
  have h26 : p26 := r37 h14 f19 h24
  have h29 : p29 := r24 h26 h27 h36
  have h9 : p9 := r38 h29 f37
  have h13 : p13 := r29 h9 h24
  have h1 : p1 := r10 h13 f19
  have h0 : p0 := r17 h1 h36
  have h28 : p28 := r22 h1 f22
  have h32 : p32 := r23 h9 h26
  have h35 : p35 := r18 h29 h32
  have h7 : p7 := r42 f8 f22 h35
  have h16 : p16 := r47 h0 h7 h28
  exact h16
#print axioms cogModel_e6f3cb529eea22fb3ab2f22ebacca0eba086bfb7dc2e62bade290c4b8d5d97db

theorem cogModel_58a7bef129865e7acbec24ede2c7df1b993cac784d048ee46dd4e5168dcb8930 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 : Prop) (f2 : p2) (f4 : p4) (f22 : p22) (f23 : p23) (f31 : p31) (r0 : p3 → p22 → p32 → p26) (r1 : p10 → p32 → p19) (r2 : p23 → p32 → p24) (r3 : p9 → p24 → p21) (r4 : p10 → p23 → p8) (r5 : p4 → p7 → p29) (r6 : p2 → p8 → p15) (r7 : p12 → p6) (r8 : p2 → p23 → p0) (r9 : p22 → p31 → p32 → p24) (r10 : p2 → p4 → p5) (r11 : p23 → p31 → p25) (r12 : p8 → p22 → p20) (r13 : p2 → p22 → p27) (r14 : p4 → p22 → p13) (r15 : p2 → p13 → p3) (r16 : p9 → p24 → p26 → p10) (r17 : p0 → p22 → p31 → p3) (r18 : p2 → p13 → p11) (r19 : p0 → p4 → p32) (r20 : p19 → p23 → p18) (r21 : p2 → p16 → p32) (r22 : p19 → p22 → p20) (r23 : p15 → p18 → p20 → p1) (r24 : p4 → p14 → p28) (r25 : p2 → p11 → p9) (r26 : p4 → p21 → p23 → p8) (r27 : p4 → p31 → p16) (r28 : p23 → p30 → p17) (r29 : p23 → p12) : p1 := by
  have h16 : p16 := r27 f4 f31
  have h32 : p32 := r21 f2 h16
  have h24 : p24 := r2 f23 h32
  have h13 : p13 := r14 f4 f22
  have h11 : p11 := r18 f2 h13
  have h9 : p9 := r25 f2 h11
  have h21 : p21 := r3 h9 h24
  have h8 : p8 := r26 f4 h21 f23
  have h15 : p15 := r6 f2 h8
  have h20 : p20 := r12 h8 f22
  have h3 : p3 := r15 f2 h13
  have h26 : p26 := r0 h3 f22 h32
  have h10 : p10 := r16 h9 h24 h26
  have h19 : p19 := r1 h10 h32
  have h18 : p18 := r20 h19 f23
  have h1 : p1 := r23 h15 h18 h20
  exact h1
#print axioms cogModel_58a7bef129865e7acbec24ede2c7df1b993cac784d048ee46dd4e5168dcb8930

theorem cogModel_679182a5e26ad041d5e4cc7ca2c60a6c260e5eca11f7d7ace64868ae01590415 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 : Prop) (f13 : p13) (f25 : p25) (f26 : p26) (f30 : p30) (f33 : p33) (r0 : p15 → p28 → p19) (r1 : p13 → p30 → p32) (r2 : p4 → p8 → p23 → p17) (r3 : p4 → p25 → p15) (r4 : p4 → p10 → p23) (r5 : p29 → p9) (r6 : p33 → p2) (r7 : p11 → p24) (r8 : p0 → p2 → p25 → p35) (r9 : p13 → p25 → p33 → p0) (r10 : p9 → p35 → p5) (r11 : p27 → p30 → p6) (r12 : p20 → p26 → p1) (r13 : p26 → p29 → p33 → p11) (r14 : p14 → p34 → p21) (r15 : p19 → p25 → p22) (r16 : p2 → p11 → p30 → p7) (r17 : p25 → p20) (r18 : p1 → p26 → p28) (r19 : p20 → p30 → p4) (r20 : p13 → p29) (r21 : p4 → p17 → p14) (r22 : p13 → p31 → p3) (r23 : p15 → p18 → p8) (r24 : p13 → p25 → p33 → p18) (r25 : p1 → p17 → p18 → p34) (r26 : p0 → p13 → p30 → p12) (r27 : p2 → p35 → p16) (r28 : p4 → p18 → p25 → p10) : p21 := by
  have h18 : p18 := r24 f13 f25 f33
  have h20 : p20 := r17 f25
  have h1 : p1 := r12 h20 f26
  have h4 : p4 := r19 h20 f30
  have h10 : p10 := r28 h4 h18 f25
  have h23 : p23 := r4 h4 h10
  have h15 : p15 := r3 h4 f25
  have h8 : p8 := r23 h15 h18
  have h17 : p17 := r2 h4 h8 h23
  have h14 : p14 := r21 h4 h17
  have h34 : p34 := r25 h1 h17 h18
  have h21 : p21 := r14 h14 h34
  exact h21
#print axioms cogModel_679182a5e26ad041d5e4cc7ca2c60a6c260e5eca11f7d7ace64868ae01590415

theorem cogModel_81c20b67520f951c2af03f75029b7a6904a09506d3117ff5e06a692d16cbc126 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 : Prop) (f1 : p1) (f5 : p5) (f11 : p11) (f22 : p22) (r0 : p13 → p3) (r1 : p1 → p6 → p16) (r2 : p5 → p22 → p2) (r3 : p1 → p22 → p9) (r4 : p14 → p19) (r5 : p8 → p0) (r6 : p19 → p13) (r7 : p5 → p7) (r8 : p1 → p21 → p20) (r9 : p0 → p10) (r10 : p7 → p14) (r11 : p9 → p18) (r12 : p11 → p17) (r13 : p3 → p8) (r14 : p5 → p12) (r15 : p5 → p23 → p4) (r16 : p1 → p15) : p10 := by
  have h7 : p7 := r7 f5
  have h14 : p14 := r10 h7
  have h19 : p19 := r4 h14
  have h13 : p13 := r6 h19
  have h3 : p3 := r0 h13
  have h8 : p8 := r13 h3
  have h0 : p0 := r5 h8
  have h10 : p10 := r9 h0
  exact h10
#print axioms cogModel_81c20b67520f951c2af03f75029b7a6904a09506d3117ff5e06a692d16cbc126

theorem cogModel_f13f18a7fd424f30b23242f515310d820bee3a5de4e286888842bc716e6641be (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 : Prop) (f3 : p3) (f6 : p6) (f8 : p8) (f21 : p21) (r0 : p2 → p8 → p22 → p29) (r1 : p6 → p8 → p21 → p10) (r2 : p3 → p18 → p21 → p25) (r3 : p3 → p21 → p22 → p5) (r4 : p10 → p12 → p13) (r5 : p6 → p23 → p1) (r6 : p0 → p27 → p20) (r7 : p3 → p15 → p27) (r8 : p8 → p12) (r9 : p6 → p8 → p21 → p12) (r10 : p1 → p14 → p20 → p17) (r11 : p12 → p21 → p15) (r12 : p15 → p21 → p26) (r13 : p6 → p8 → p21 → p22) (r14 : p0 → p3 → p1) (r15 : p6 → p15 → p30) (r16 : p3 → p22 → p18) (r17 : p13 → p21 → p27) (r18 : p3 → p12 → p13) (r19 : p13 → p15 → p21 → p30) (r20 : p3 → p11 → p9) (r21 : p3 → p12 → p15) (r22 : p3 → p15 → p26) (r23 : p21 → p28 → p19) (r24 : p18 → p2) (r25 : p8 → p21 → p10) (r26 : p23 → p30 → p14) (r27 : p13 → p27 → p30 → p23) (r28 : p21 → p26 → p0) (r29 : p4 → p8 → p16) (r30 : p3 → p6 → p30 → p24) (r31 : p21 → p22 → p7) (r32 : p12 → p26 → p27 → p0) : p17 := by
  have h12 : p12 := r8 f8
  have h13 : p13 := r18 f3 h12
  have h27 : p27 := r17 h13 f21
  have h15 : p15 := r11 h12 f21
  have h30 : p30 := r15 f6 h15
  have h23 : p23 := r27 h13 h27 h30
  have h14 : p14 := r26 h23 h30
  have h1 : p1 := r5 f6 h23
  have h26 : p26 := r12 h15 f21
  have h0 : p0 := r28 f21 h26
  have h20 : p20 := r6 h0 h27
  have h17 : p17 := r10 h1 h14 h20
  exact h17
#print axioms cogModel_f13f18a7fd424f30b23242f515310d820bee3a5de4e286888842bc716e6641be

theorem cogModel_0469ec360421af035d006ace9bd8e53ecd4a94d74871260e8f27840ae3480464 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 : Prop) (f2 : p2) (f9 : p9) (f19 : p19) (f22 : p22) (r0 : p16 → p19 → p20) (r1 : p3 → p22 → p17) (r2 : p19 → p22 → p26) (r3 : p2 → p3 → p9 → p10) (r4 : p2 → p19 → p15) (r5 : p2 → p9 → p8) (r6 : p5 → p12 → p26 → p23) (r7 : p9 → p22 → p8) (r8 : p9 → p19 → p6) (r9 : p9 → p23 → p18) (r10 : p12 → p24 → p13) (r11 : p8 → p22 → p28) (r12 : p15 → p19 → p26 → p12) (r13 : p2 → p8 → p12) (r14 : p9 → p15 → p5) (r15 : p5 → p9 → p23) (r16 : p2 → p25) (r17 : p9 → p15) (r18 : p2 → p19 → p3) (r19 : p14 → p27) (r20 : p8 → p22 → p24 → p18) (r21 : p13 → p18 → p21) (r22 : p8 → p15 → p28) (r23 : p2 → p9 → p26) (r24 : p7 → p19 → p1) (r25 : p4 → p22 → p0) (r26 : p10 → p14) (r27 : p5 → p8 → p24) (r28 : p9 → p26 → p5) (r29 : p2 → p25 → p11) (r30 : p19 → p23 → p13) : p21 := by
  have h8 : p8 := r5 f2 f9
  have h12 : p12 := r13 f2 h8
  have h26 : p26 := r23 f2 f9
  have h5 : p5 := r28 f9 h26
  have h23 : p23 := r15 h5 f9
  have h13 : p13 := r30 f19 h23
  have h18 : p18 := r9 f9 h23
  have h21 : p21 := r21 h13 h18
  exact h21
#print axioms cogModel_0469ec360421af035d006ace9bd8e53ecd4a94d74871260e8f27840ae3480464

theorem cogModel_bb03b28a9ba8677b273203e957aebdc9dbd60637487f2570d73a3a2e303f4cc2 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 : Prop) (f6 : p6) (f7 : p7) (f10 : p10) (f15 : p15) (f19 : p19) (r0 : p10 → p19 → p2) (r1 : p7 → p15 → p19 → p22) (r2 : p6 → p19 → p20) (r3 : p19 → p1) (r4 : p2 → p17) (r5 : p6 → p10 → p15 → p12) (r6 : p12 → p20 → p9) (r7 : p9 → p17 → p18 → p5) (r8 : p6 → p14 → p11) (r9 : p6 → p19 → p22 → p4) (r10 : p8 → p19 → p0) (r11 : p6 → p10 → p21) (r12 : p4 → p21 → p3) (r13 : p7 → p19 → p14) (r14 : p19 → p20 → p18) (r15 : p7 → p16 → p13) : p5 := by
  have h20 : p20 := r2 f6 f19
  have h18 : p18 := r14 f19 h20
  have h12 : p12 := r5 f6 f10 f15
  have h9 : p9 := r6 h12 h20
  have h2 : p2 := r0 f10 f19
  have h17 : p17 := r4 h2
  have h5 : p5 := r7 h9 h17 h18
  exact h5
#print axioms cogModel_bb03b28a9ba8677b273203e957aebdc9dbd60637487f2570d73a3a2e303f4cc2

theorem cogModel_cc5a1270779606c1be25bd66b100b0f9ad40153fdb40040e106819aa93325af9 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 : Prop) (f2 : p2) (f3 : p3) (f25 : p25) (r0 : p2 → p3 → p1) (r1 : p23 → p26 → p0) (r2 : p3 → p14 → p18) (r3 : p3 → p22 → p25 → p23) (r4 : p8 → p12 → p21) (r5 : p11 → p4) (r6 : p7 → p26) (r7 : p2 → p3 → p22) (r8 : p27 → p6) (r9 : p3 → p9 → p10) (r10 : p1 → p25 → p11) (r11 : p2 → p11 → p15 → p17) (r12 : p3 → p5 → p16) (r13 : p2 → p3 → p22 → p24) (r14 : p2 → p25 → p7) (r15 : p13 → p25 → p8) (r16 : p24 → p13) (r17 : p0 → p13 → p12) (r18 : p2 → p20 → p19) (r19 : p2 → p3 → p27) (r20 : p2 → p25 → p15) : p21 := by
  have h7 : p7 := r14 f2 f25
  have h26 : p26 := r6 h7
  have h22 : p22 := r7 f2 f3
  have h24 : p24 := r13 f2 f3 h22
  have h13 : p13 := r16 h24
  have h8 : p8 := r15 h13 f25
  have h23 : p23 := r3 f3 h22 f25
  have h0 : p0 := r1 h23 h26
  have h12 : p12 := r17 h0 h13
  have h21 : p21 := r4 h8 h12
  exact h21
#print axioms cogModel_cc5a1270779606c1be25bd66b100b0f9ad40153fdb40040e106819aa93325af9

theorem cogModel_1e16e3119714b5da8a3c2debfa04b2a49374a6efa7131d945e80fc5df0d3295c (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 : Prop) (f9 : p9) (f11 : p11) (f18 : p18) (f19 : p19) (f21 : p21) (r0 : p19 → p26 → p12) (r1 : p11 → p18 → p19 → p1) (r2 : p1 → p19 → p24) (r3 : p5 → p21 → p16) (r4 : p11 → p23 → p6) (r5 : p11 → p19 → p26 → p5) (r6 : p11 → p20 → p13) (r7 : p0 → p19 → p17) (r8 : p16 → p25) (r9 : p11 → p19 → p26) (r10 : p9 → p21 → p3) (r11 : p9 → p21 → p8) (r12 : p3 → p23) (r13 : p11 → p21 → p22) (r14 : p2 → p4 → p25 → p15) (r15 : p9 → p12 → p18 → p10) (r16 : p5 → p10 → p27 → p4) (r17 : p5 → p27 → p2) (r18 : p5 → p9 → p22 → p27) (r19 : p11 → p14 → p7) : p15 := by
  have h22 : p22 := r13 f11 f21
  have h26 : p26 := r9 f11 f19
  have h5 : p5 := r5 f11 f19 h26
  have h27 : p27 := r18 h5 f9 h22
  have h2 : p2 := r17 h5 h27
  have h16 : p16 := r3 h5 f21
  have h25 : p25 := r8 h16
  have h12 : p12 := r0 f19 h26
  have h10 : p10 := r15 f9 h12 f18
  have h4 : p4 := r16 h5 h10 h27
  have h15 : p15 := r14 h2 h4 h25
  exact h15
#print axioms cogModel_1e16e3119714b5da8a3c2debfa04b2a49374a6efa7131d945e80fc5df0d3295c

theorem cogModel_070bb8d76a3495ac3c270c6e4720442cadf9025182f4295508d64df2b0b3a780 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 : Prop) (f3 : p3) (f16 : p16) (f18 : p18) (r0 : p12 → p16 → p0) (r1 : p1 → p11 → p16 → p2) (r2 : p3 → p6 → p14) (r3 : p7 → p8) (r4 : p3 → p4 → p9 → p11) (r5 : p1 → p3 → p9) (r6 : p21 → p13) (r7 : p3 → p23) (r8 : p15 → p7) (r9 : p4 → p1) (r10 : p23 → p15) (r11 : p16 → p17 → p10) (r12 : p8 → p21) (r13 : p11 → p19 → p5) (r14 : p16 → p22 → p20) (r15 : p3 → p19) (r16 : p16 → p18 → p4) : p13 := by
  have h23 : p23 := r7 f3
  have h15 : p15 := r10 h23
  have h7 : p7 := r8 h15
  have h8 : p8 := r3 h7
  have h21 : p21 := r12 h8
  have h13 : p13 := r6 h21
  exact h13
#print axioms cogModel_070bb8d76a3495ac3c270c6e4720442cadf9025182f4295508d64df2b0b3a780

theorem cogModel_16116500ac4c481109e27aef38a0b3d4ddeeb4aadd7e6c38c774fedc3eeb0391 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 : Prop) (f8 : p8) (f12 : p12) (f16 : p16) (f23 : p23) (r0 : p11 → p23 → p15) (r1 : p8 → p23 → p14) (r2 : p10 → p19 → p6) (r3 : p7 → p16 → p21) (r4 : p9 → p18 → p24 → p1) (r5 : p9 → p18 → p0) (r6 : p12 → p23 → p9) (r7 : p8 → p12 → p16 → p19) (r8 : p8 → p12 → p16 → p25) (r9 : p8 → p16 → p19 → p10) (r10 : p6 → p2) (r11 : p1 → p9 → p12 → p22) (r12 : p0 → p1 → p7 → p17) (r13 : p12 → p16 → p24) (r14 : p9 → p24 → p7) (r15 : p8 → p23 → p18) (r16 : p17 → p21 → p22 → p3) (r17 : p8 → p23 → p20) (r18 : p4 → p12 → p5) (r19 : p16 → p20 → p13) : p3 := by
  have h9 : p9 := r6 f12 f23
  have h24 : p24 := r13 f12 f16
  have h7 : p7 := r14 h9 h24
  have h21 : p21 := r3 h7 f16
  have h18 : p18 := r15 f8 f23
  have h1 : p1 := r4 h9 h18 h24
  have h22 : p22 := r11 h1 h9 f12
  have h0 : p0 := r5 h9 h18
  have h17 : p17 := r12 h0 h1 h7
  have h3 : p3 := r16 h17 h21 h22
  exact h3
#print axioms cogModel_16116500ac4c481109e27aef38a0b3d4ddeeb4aadd7e6c38c774fedc3eeb0391

theorem cogModel_3f40556241dbe40b3f05d8a6dbb7e9fb125b8312460e9abe1b7de0d39b6c63a9 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 : Prop) (f2 : p2) (f6 : p6) (f11 : p11) (f33 : p33) (r0 : p7 → p11 → p37 → p36) (r1 : p2 → p6 → p28 → p15) (r2 : p2 → p15 → p33 → p10) (r3 : p2 → p11 → p33 → p37) (r4 : p6 → p3) (r5 : p2 → p11 → p28) (r6 : p4 → p0) (r7 : p28 → p27) (r8 : p6 → p20 → p23) (r9 : p1 → p33 → p25) (r10 : p7 → p11 → p35 → p31) (r11 : p2 → p6 → p33 → p13) (r12 : p2 → p6 → p33 → p24) (r13 : p8 → p20 → p35) (r14 : p2 → p11 → p8) (r15 : p6 → p13 → p18) (r16 : p26 → p31 → p19) (r17 : p6 → p14 → p12) (r18 : p3 → p6 → p18 → p29) (r19 : p2 → p22 → p17) (r20 : p4 → p33 → p20) (r21 : p10 → p33 → p9) (r22 : p7 → p8 → p4) (r23 : p6 → p21 → p34) (r24 : p0 → p8 → p35 → p26) (r25 : p6 → p11 → p33 → p7) (r26 : p16 → p27 → p5) (r27 : p0 → p6 → p20 → p32) (r28 : p33 → p30) (r29 : p10 → p24 → p16) : p19 := by
  have h8 : p8 := r14 f2 f11
  have h7 : p7 := r25 f6 f11 f33
  have h4 : p4 := r22 h7 h8
  have h0 : p0 := r6 h4
  have h20 : p20 := r20 h4 f33
  have h35 : p35 := r13 h8 h20
  have h26 : p26 := r24 h0 h8 h35
  have h31 : p31 := r10 h7 f11 h35
  have h19 : p19 := r16 h26 h31
  exact h19
#print axioms cogModel_3f40556241dbe40b3f05d8a6dbb7e9fb125b8312460e9abe1b7de0d39b6c63a9

theorem cogModel_58f286241ca3b527bd69da82ba6e0a060f7c64e699483caeaab54679e91b1944 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 : Prop) (f0 : p0) (f2 : p2) (f4 : p4) (f6 : p6) (f22 : p22) (r0 : p12 → p22 → p21) (r1 : p22 → p13) (r2 : p5 → p9 → p11 → p19) (r3 : p7 → p10) (r4 : p2 → p8 → p15 → p9) (r5 : p22 → p7) (r6 : p0 → p8 → p5) (r7 : p7 → p18 → p23) (r8 : p1 → p22 → p14) (r9 : p0 → p2 → p18) (r10 : p2 → p16 → p3) (r11 : p6 → p7 → p13 → p17) (r12 : p4 → p22 → p15) (r13 : p4 → p15 → p11) (r14 : p0 → p4 → p23 → p20) (r15 : p0 → p4 → p8) (r16 : p22 → p25 → p24) : p19 := by
  have h15 : p15 := r12 f4 f22
  have h11 : p11 := r13 f4 h15
  have h8 : p8 := r15 f0 f4
  have h5 : p5 := r6 f0 h8
  have h9 : p9 := r4 f2 h8 h15
  have h19 : p19 := r2 h5 h9 h11
  exact h19
#print axioms cogModel_58f286241ca3b527bd69da82ba6e0a060f7c64e699483caeaab54679e91b1944

theorem cogModel_47ae1e2695f3f495b67c656887b3c95bf1797e09803698ca63a718085086ef4c (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 : Prop) (f0 : p0) (f6 : p6) (f13 : p13) (f14 : p14) (f18 : p18) (r0 : p6 → p23) (r1 : p13 → p18 → p22 → p26) (r2 : p13 → p18 → p22) (r3 : p4 → p18 → p9) (r4 : p15 → p20 → p16) (r5 : p4 → p11 → p20) (r6 : p12 → p18 → p20) (r7 : p8 → p22 → p3) (r8 : p0 → p24 → p9) (r9 : p10 → p8) (r10 : p5 → p7 → p10) (r11 : p13 → p14 → p18 → p5) (r12 : p18 → p19 → p21) (r13 : p6 → p13 → p24 → p11) (r14 : p4 → p24 → p12) (r15 : p9 → p12 → p18 → p15) (r16 : p13 → p18 → p24) (r17 : p2 → p14 → p1) (r18 : p5 → p13 → p18 → p7) (r19 : p4 → p6 → p12) (r20 : p0 → p6 → p14 → p4) (r21 : p0 → p13 → p18 → p24) (r22 : p4 → p18 → p11) (r23 : p18 → p25 → p17) : p16 := by
  have h4 : p4 := r20 f0 f6 f14
  have h12 : p12 := r19 h4 f6
  have h20 : p20 := r6 h12 f18
  have h9 : p9 := r3 h4 f18
  have h15 : p15 := r15 h9 h12 f18
  have h16 : p16 := r4 h15 h20
  exact h16
#print axioms cogModel_47ae1e2695f3f495b67c656887b3c95bf1797e09803698ca63a718085086ef4c

theorem cogModel_0adcf98403849e4509343958fb65517059ce02d7d169affb16186f8e1f2fe902 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 : Prop) (f1 : p1) (f9 : p9) (f10 : p10) (r0 : p3 → p4) (r1 : p1 → p17 → p11) (r2 : p9 → p10 → p14) (r3 : p2 → p9 → p13 → p18) (r4 : p13 → p14 → p16) (r5 : p5 → p3) (r6 : p10 → p6) (r7 : p9 → p12 → p8) (r8 : p1 → p10 → p14 → p2) (r9 : p1 → p5) (r10 : p1 → p2 → p13) (r11 : p10 → p15 → p0) (r12 : p9 → p10 → p13 → p7) : p4 := by
  have h5 : p5 := r9 f1
  have h3 : p3 := r5 h5
  have h4 : p4 := r0 h3
  exact h4
#print axioms cogModel_0adcf98403849e4509343958fb65517059ce02d7d169affb16186f8e1f2fe902

theorem cogModel_a82819e88e9eda970b847dac3143dfc7255723c2d67b7e62db8513adf185b178 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 : Prop) (f3 : p3) (f5 : p5) (f11 : p11) (f17 : p17) (f20 : p20) (r0 : p17 → p16) (r1 : p17 → p20 → p4) (r2 : p15 → p23 → p26 → p13) (r3 : p3 → p8 → p17 → p27) (r4 : p11 → p18 → p15) (r5 : p2 → p5 → p9) (r6 : p3 → p5 → p12) (r7 : p11 → p17 → p22 → p8) (r8 : p3 → p11 → p18) (r9 : p1 → p20 → p21) (r10 : p3 → p4 → p26) (r11 : p3 → p4 → p15) (r12 : p3 → p17 → p20 → p22) (r13 : p3 → p4) (r14 : p5 → p14 → p16 → p25) (r15 : p5 → p11 → p18) (r16 : p4 → p18 → p23) (r17 : p10 → p17 → p19) (r18 : p3 → p12 → p24 → p7) (r19 : p3 → p5 → p11 → p14) (r20 : p11 → p24) (r21 : p0 → p5 → p6) : p13 := by
  have h18 : p18 := r8 f3 f11
  have h15 : p15 := r4 f11 h18
  have h4 : p4 := r1 f17 f20
  have h23 : p23 := r16 h4 h18
  have h26 : p26 := r10 f3 h4
  have h13 : p13 := r2 h15 h23 h26
  exact h13
#print axioms cogModel_a82819e88e9eda970b847dac3143dfc7255723c2d67b7e62db8513adf185b178

theorem cogModel_8853b5627e0bcd52b64d05f64cc46fe4620112d9bfa6ff62188a6709f93271bb (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 : Prop) (f3 : p3) (f6 : p6) (f21 : p21) (r0 : p3 → p19) (r1 : p1 → p12 → p8) (r2 : p3 → p10 → p16) (r3 : p3 → p13 → p17 → p12) (r4 : p9 → p11) (r5 : p3 → p6 → p21 → p1) (r6 : p6 → p7 → p0) (r7 : p11 → p18) (r8 : p3 → p9) (r9 : p18 → p14) (r10 : p6 → p20) (r11 : p1 → p20 → p21 → p17) (r12 : p19 → p13) (r13 : p4 → p21 → p5) (r14 : p2 → p3 → p15) : p14 := by
  have h9 : p9 := r8 f3
  have h11 : p11 := r4 h9
  have h18 : p18 := r7 h11
  have h14 : p14 := r9 h18
  exact h14
#print axioms cogModel_8853b5627e0bcd52b64d05f64cc46fe4620112d9bfa6ff62188a6709f93271bb

theorem cogModel_af32c3026c4c7793aa196a29cfb6c18c68b53cfc68ee3fb54be5fc82b92b19a8 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 : Prop) (f6 : p6) (f7 : p7) (f15 : p15) (f24 : p24) (f27 : p27) (r0 : p4 → p5 → p24 → p0) (r1 : p6 → p15 → p26) (r2 : p7 → p21 → p22) (r3 : p0 → p2 → p6 → p8) (r4 : p7 → p27 → p12) (r5 : p24 → p27 → p5) (r6 : p6 → p24 → p4) (r7 : p10 → p27 → p18) (r8 : p15 → p9) (r9 : p6 → p8 → p10 → p18) (r10 : p3 → p15 → p11) (r11 : p6 → p14 → p25) (r12 : p15 → p20 → p27 → p13) (r13 : p6 → p7 → p9 → p1) (r14 : p2 → p15 → p24 → p16) (r15 : p6 → p4) (r16 : p0 → p24 → p16) (r17 : p7 → p8 → p17) (r18 : p4 → p5 → p2) (r19 : p10 → p15 → p16 → p17) (r20 : p24 → p12) (r21 : p2 → p7 → p10) (r22 : p17 → p18 → p19) (r23 : p5 → p6 → p2) (r24 : p6 → p24 → p23) (r25 : p1 → p15 → p20) : p19 := by
  have h5 : p5 := r5 f24 f27
  have h2 : p2 := r23 h5 f6
  have h16 : p16 := r14 h2 f15 f24
  have h10 : p10 := r21 h2 f7
  have h18 : p18 := r7 h10 f27
  have h17 : p17 := r19 h10 f15 h16
  have h19 : p19 := r22 h17 h18
  exact h19
#print axioms cogModel_af32c3026c4c7793aa196a29cfb6c18c68b53cfc68ee3fb54be5fc82b92b19a8

theorem cogModel_67db87e5ebdbc5ecd0d184f4e96ab3f9a598225a0e9e33a7a25172d305047272 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 : Prop) (f5 : p5) (f19 : p19) (f20 : p20) (r0 : p4 → p24 → p1) (r1 : p5 → p10 → p12 → p14) (r2 : p0 → p10 → p12 → p11) (r3 : p5 → p19 → p18) (r4 : p0 → p10) (r5 : p1 → p16 → p17 → p15) (r6 : p0 → p10 → p22) (r7 : p5 → p20 → p24) (r8 : p19 → p20 → p12) (r9 : p20 → p23 → p3) (r10 : p5 → p11 → p13) (r11 : p4 → p19 → p17) (r12 : p5 → p10 → p2) (r13 : p8 → p20 → p9) (r14 : p19 → p20 → p4) (r15 : p4 → p18 → p16) (r16 : p20 → p0) (r17 : p10 → p20 → p22 → p7) (r18 : p5 → p21 → p6) : p15 := by
  have h4 : p4 := r14 f19 f20
  have h17 : p17 := r11 h4 f19
  have h18 : p18 := r3 f5 f19
  have h16 : p16 := r15 h4 h18
  have h24 : p24 := r7 f5 f20
  have h1 : p1 := r0 h4 h24
  have h15 : p15 := r5 h1 h16 h17
  exact h15
#print axioms cogModel_67db87e5ebdbc5ecd0d184f4e96ab3f9a598225a0e9e33a7a25172d305047272

theorem cogModel_5f4eaa12620aa80f2a5250e9142f15bd845fc98682de1d45ecd925ba84382f2c (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 : Prop) (f5 : p5) (f10 : p10) (f16 : p16) (f19 : p19) (f22 : p22) (r0 : p18 → p22 → p26 → p20) (r1 : p13 → p25 → p15) (r2 : p19 → p14) (r3 : p19 → p22 → p9) (r4 : p10 → p19 → p26) (r5 : p10 → p13 → p25 → p24) (r6 : p8 → p10 → p7) (r7 : p5 → p10 → p22 → p11) (r8 : p16 → p3) (r9 : p9 → p18 → p22 → p21) (r10 : p10 → p17) (r11 : p5 → p15 → p19 → p12) (r12 : p2 → p5 → p4) (r13 : p0 → p16 → p23) (r14 : p20 → p21 → p27) (r15 : p5 → p10 → p22 → p18) (r16 : p5 → p25) (r17 : p6 → p16 → p1) (r18 : p16 → p13) : p27 := by
  have h18 : p18 := r15 f5 f10 f22
  have h9 : p9 := r3 f19 f22
  have h21 : p21 := r9 h9 h18 f22
  have h26 : p26 := r4 f10 f19
  have h20 : p20 := r0 h18 f22 h26
  have h27 : p27 := r14 h20 h21
  exact h27
#print axioms cogModel_5f4eaa12620aa80f2a5250e9142f15bd845fc98682de1d45ecd925ba84382f2c

theorem cogModel_92fec1ab75b19d3ac56c44519b74920cc65ba021e7c5b90697d9a8de79092d96 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 : Prop) (f13 : p13) (f15 : p15) (f19 : p19) (r0 : p19 → p3) (r1 : p7 → p22 → p25) (r2 : p15 → p19 → p0) (r3 : p9 → p15 → p24) (r4 : p2 → p6 → p13 → p11) (r5 : p13 → p19 → p2) (r6 : p0 → p19 → p22) (r7 : p17 → p19 → p21) (r8 : p13 → p15 → p3) (r9 : p0 → p15 → p19 → p4) (r10 : p8 → p18 → p14) (r11 : p15 → p19 → p26 → p6) (r12 : p10 → p13 → p7) (r13 : p15 → p26) (r14 : p0 → p15 → p22) (r15 : p1 → p13 → p18) (r16 : p13 → p15 → p10) (r17 : p12 → p19 → p16) (r18 : p0 → p7 → p1) (r19 : p13 → p27 → p23) (r20 : p0 → p10 → p7) (r21 : p19 → p20) (r22 : p0 → p1 → p22 → p18) (r23 : p7 → p10 → p19 → p5) (r24 : p19 → p25 → p8) : p14 := by
  have h0 : p0 := r2 f15 f19
  have h22 : p22 := r6 h0 f19
  have h10 : p10 := r16 f13 f15
  have h7 : p7 := r20 h0 h10
  have h1 : p1 := r18 h0 h7
  have h18 : p18 := r15 h1 f13
  have h25 : p25 := r1 h7 h22
  have h8 : p8 := r24 f19 h25
  have h14 : p14 := r10 h8 h18
  exact h14
#print axioms cogModel_92fec1ab75b19d3ac56c44519b74920cc65ba021e7c5b90697d9a8de79092d96

theorem cogModel_7f90ab6d63485a5b35e068f44579d8bae230b879a1586c7902750e7bca9d2ce9 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 : Prop) (f11 : p11) (f15 : p15) (f20 : p20) (f23 : p23) (f26 : p26) (r0 : p9 → p23 → p4) (r1 : p18 → p23 → p13) (r2 : p11 → p26 → p1) (r3 : p11 → p15 → p21 → p12) (r4 : p23 → p24 → p17) (r5 : p1 → p22 → p2) (r6 : p9 → p26 → p22) (r7 : p2 → p19 → p16) (r8 : p1 → p22 → p26 → p19) (r9 : p1 → p9 → p11 → p8) (r10 : p23 → p26 → p5) (r11 : p15 → p27 → p3) (r12 : p20 → p26 → p1) (r13 : p10 → p20 → p6) (r14 : p11 → p15 → p0) (r15 : p11 → p20 → p21) (r16 : p8 → p26 → p2) (r17 : p11 → p9) (r18 : p0 → p5 → p20 → p7) (r19 : p11 → p20 → p14) (r20 : p11 → p14 → p25) (r21 : p9 → p20 → p22) (r22 : p1 → p11 → p20 → p4) : p16 := by
  have h1 : p1 := r2 f11 f26
  have h9 : p9 := r17 f11
  have h22 : p22 := r6 h9 f26
  have h2 : p2 := r5 h1 h22
  have h19 : p19 := r8 h1 h22 f26
  have h16 : p16 := r7 h2 h19
  exact h16
#print axioms cogModel_7f90ab6d63485a5b35e068f44579d8bae230b879a1586c7902750e7bca9d2ce9

theorem cogModel_acc22ce38df6019a999b200d908653f75586227e92a3053c03bf8cac81185d18 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 : Prop) (f2 : p2) (f14 : p14) (f15 : p15) (f16 : p16) (r0 : p1 → p14 → p6) (r1 : p2 → p14 → p17 → p11) (r2 : p0 → p14 → p25 → p7) (r3 : p2 → p16 → p25) (r4 : p22 → p24) (r5 : p2 → p15 → p19) (r6 : p16 → p17) (r7 : p2 → p5 → p23) (r8 : p2 → p3) (r9 : p7 → p8 → p10 → p18) (r10 : p14 → p16 → p0) (r11 : p3 → p16 → p8) (r12 : p15 → p17 → p9) (r13 : p20 → p22 → p12) (r14 : p14 → p16 → p25 → p10) (r15 : p2 → p13 → p22) (r16 : p13 → p22 → p20) (r17 : p17 → p21) (r18 : p2 → p13) (r19 : p16 → p19 → p4) : p18 := by
  have h25 : p25 := r3 f2 f16
  have h10 : p10 := r14 f14 f16 h25
  have h3 : p3 := r8 f2
  have h8 : p8 := r11 h3 f16
  have h0 : p0 := r10 f14 f16
  have h7 : p7 := r2 h0 f14 h25
  have h18 : p18 := r9 h7 h8 h10
  exact h18
#print axioms cogModel_acc22ce38df6019a999b200d908653f75586227e92a3053c03bf8cac81185d18

theorem cogModel_79efe8f69eb45d537bba3a4eeb38d49653ef146e6550fa633970e6dbd0d8fbae (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 : Prop) (f0 : p0) (f22 : p22) (f23 : p23) (r0 : p0 → p10 → p24 → p18) (r1 : p1 → p4 → p8) (r2 : p24 → p6) (r3 : p0 → p22 → p11) (r4 : p4 → p22 → p23 → p5) (r5 : p23 → p24 → p19) (r6 : p22 → p24) (r7 : p10 → p15 → p24 → p7) (r8 : p0 → p5 → p16 → p14) (r9 : p22 → p23 → p13) (r10 : p23 → p10) (r11 : p2 → p23 → p27) (r12 : p0 → p16 → p4) (r13 : p3 → p22 → p12) (r14 : p8 → p14 → p17) (r15 : p15 → p26) (r16 : p0 → p4 → p1) (r17 : p10 → p23 → p15) (r18 : p10 → p22 → p25 → p9) (r19 : p10 → p22 → p25) (r20 : p18 → p20) (r21 : p11 → p23 → p28) (r22 : p22 → p23 → p16) (r23 : p13 → p16 → p23 → p21) : p17 := by
  have h16 : p16 := r22 f22 f23
  have h4 : p4 := r12 f0 h16
  have h1 : p1 := r16 f0 h4
  have h8 : p8 := r1 h1 h4
  have h5 : p5 := r4 h4 f22 f23
  have h14 : p14 := r8 f0 h5 h16
  have h17 : p17 := r14 h8 h14
  exact h17
#print axioms cogModel_79efe8f69eb45d537bba3a4eeb38d49653ef146e6550fa633970e6dbd0d8fbae

theorem cogModel_f4cc14a495285b523dd517f6b4abeb7ac4dba9f821fb2951592a51c81d390df4 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 : Prop) (f3 : p3) (f17 : p17) (f26 : p26) (f30 : p30) (f32 : p32) (r0 : p3 → p11 → p19) (r1 : p26 → p31) (r2 : p1 → p17 → p23) (r3 : p3 → p30 → p22) (r4 : p3 → p31 → p32 → p27) (r5 : p30 → p18) (r6 : p5 → p17 → p32 → p16) (r7 : p30 → p15) (r8 : p3 → p26 → p24) (r9 : p24 → p31 → p7) (r10 : p8 → p17 → p18 → p0) (r11 : p24 → p27 → p28 → p4) (r12 : p16 → p8) (r13 : p2 → p4 → p30 → p20) (r14 : p6 → p20 → p13) (r15 : p26 → p30 → p25) (r16 : p17 → p28) (r17 : p4 → p6 → p9) (r18 : p9 → p26 → p29) (r19 : p13 → p29 → p10) (r20 : p14 → p30 → p12) (r21 : p3 → p4 → p21) (r22 : p7 → p26 → p31 → p2) (r23 : p17 → p26 → p5) (r24 : p3 → p27 → p28 → p6) : p10 := by
  have h28 : p28 := r16 f17
  have h31 : p31 := r1 f26
  have h27 : p27 := r4 f3 h31 f32
  have h6 : p6 := r24 f3 h27 h28
  have h24 : p24 := r8 f3 f26
  have h4 : p4 := r11 h24 h27 h28
  have h9 : p9 := r17 h4 h6
  have h29 : p29 := r18 h9 f26
  have h7 : p7 := r9 h24 h31
  have h2 : p2 := r22 h7 f26 h31
  have h20 : p20 := r13 h2 h4 f30
  have h13 : p13 := r14 h6 h20
  have h10 : p10 := r19 h13 h29
  exact h10
#print axioms cogModel_f4cc14a495285b523dd517f6b4abeb7ac4dba9f821fb2951592a51c81d390df4

theorem cogModel_b3ca0f39f65b4b9e86a9c1e35ba8b1f21fb8828c5bcb340342a8e7332ed75e6c (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 : Prop) (f10 : p10) (f25 : p25) (f29 : p29) (r0 : p2 → p10 → p16) (r1 : p10 → p25 → p3) (r2 : p25 → p11) (r3 : p10 → p29 → p22) (r4 : p10 → p22 → p29 → p7) (r5 : p20 → p26 → p27) (r6 : p15 → p17 → p18 → p20) (r7 : p0 → p4 → p17) (r8 : p10 → p14 → p29 → p28) (r9 : p0 → p9 → p15) (r10 : p8 → p10 → p30) (r11 : p18 → p25 → p26) (r12 : p0 → p10 → p17 → p13) (r13 : p25 → p23) (r14 : p0 → p4 → p9) (r15 : p10 → p25 → p29 → p5) (r16 : p21 → p27 → p28 → p24) (r17 : p10 → p12 → p6) (r18 : p4 → p13 → p25 → p14) (r19 : p10 → p25 → p19) (r20 : p29 → p0) (r21 : p29 → p1) (r22 : p0 → p9 → p18) (r23 : p15 → p20 → p21) (r24 : p25 → p29 → p4) : p24 := by
  have h4 : p4 := r24 f25 f29
  have h0 : p0 := r20 f29
  have h9 : p9 := r14 h0 h4
  have h15 : p15 := r9 h0 h9
  have h18 : p18 := r22 h0 h9
  have h26 : p26 := r11 h18 f25
  have h17 : p17 := r7 h0 h4
  have h20 : p20 := r6 h15 h17 h18
  have h21 : p21 := r23 h15 h20
  have h27 : p27 := r5 h20 h26
  have h13 : p13 := r12 h0 f10 h17
  have h14 : p14 := r18 h4 h13 f25
  have h28 : p28 := r8 f10 h14 f29
  have h24 : p24 := r16 h21 h27 h28
  exact h24
#print axioms cogModel_b3ca0f39f65b4b9e86a9c1e35ba8b1f21fb8828c5bcb340342a8e7332ed75e6c

theorem cogModel_5691ca4204bb01e650e977183c3d5fe4b1956daf6c3c7dac976390f2488aeaaa (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 : Prop) (f5 : p5) (f9 : p9) (f14 : p14) (f21 : p21) (f24 : p24) (r0 : p14 → p21 → p23 → p22) (r1 : p17 → p4) (r2 : p5 → p6 → p8 → p2) (r3 : p4 → p18) (r4 : p9 → p22 → p25 → p20) (r5 : p21 → p27 → p12) (r6 : p14 → p22 → p25 → p27) (r7 : p21 → p26 → p1) (r8 : p11 → p20 → p22 → p3) (r9 : p13 → p24 → p7) (r10 : p14 → p24 → p27 → p10) (r11 : p5 → p14 → p19 → p11) (r12 : p9 → p24 → p19) (r13 : p5 → p14 → p21 → p17) (r14 : p19 → p23 → p25) (r15 : p4 → p17 → p21 → p0) (r16 : p17 → p8) (r17 : p3 → p10 → p12 → p15) (r18 : p0 → p14 → p21 → p6) (r19 : p21 → p23) (r20 : p5 → p16) : p15 := by
  have h23 : p23 := r19 f21
  have h22 : p22 := r0 f14 f21 h23
  have h19 : p19 := r12 f9 f24
  have h11 : p11 := r11 f5 f14 h19
  have h25 : p25 := r14 h19 h23
  have h27 : p27 := r6 f14 h22 h25
  have h12 : p12 := r5 f21 h27
  have h10 : p10 := r10 f14 f24 h27
  have h20 : p20 := r4 f9 h22 h25
  have h3 : p3 := r8 h11 h20 h22
  have h15 : p15 := r17 h3 h10 h12
  exact h15
#print axioms cogModel_5691ca4204bb01e650e977183c3d5fe4b1956daf6c3c7dac976390f2488aeaaa

theorem cogModel_241030357143e9ec17ef7a0c9bc1cbf885bf2ff0779e1a33bca4dbad111c4c9f (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 : Prop) (f6 : p6) (f8 : p8) (f16 : p16) (f17 : p17) (f18 : p18) (r0 : p8 → p16 → p18 → p3) (r1 : p0 → p5 → p2) (r2 : p16 → p20) (r3 : p3 → p6 → p8 → p9) (r4 : p3 → p9 → p11) (r5 : p6 → p12 → p24) (r6 : p6 → p8 → p4) (r7 : p16 → p22 → p15) (r8 : p6 → p8 → p18 → p14) (r9 : p17 → p18 → p21) (r10 : p8 → p19 → p1) (r11 : p4 → p17 → p5) (r12 : p4 → p14 → p21 → p0) (r13 : p3 → p11 → p23 → p13) (r14 : p7 → p8 → p10) (r15 : p8 → p20 → p23) : p2 := by
  have h4 : p4 := r6 f6 f8
  have h5 : p5 := r11 h4 f17
  have h21 : p21 := r9 f17 f18
  have h14 : p14 := r8 f6 f8 f18
  have h0 : p0 := r12 h4 h14 h21
  have h2 : p2 := r1 h0 h5
  exact h2
#print axioms cogModel_241030357143e9ec17ef7a0c9bc1cbf885bf2ff0779e1a33bca4dbad111c4c9f

theorem cogModel_3f2bce04d7ecf524225fdae1a8f7daab4bad9169a9248a1feaaab5bbacc5b183 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 : Prop) (f6 : p6) (f8 : p8) (f12 : p12) (f16 : p16) (f19 : p19) (r0 : p0 → p5 → p22) (r1 : p6 → p8 → p3) (r2 : p4 → p8 → p21) (r3 : p19 → p23 → p2) (r4 : p4 → p9 → p10 → p18) (r5 : p5 → p6 → p20) (r6 : p5 → p6 → p17) (r7 : p12 → p16 → p19 → p23) (r8 : p4 → p12 → p16 → p10) (r9 : p6 → p16 → p19 → p5) (r10 : p4 → p21 → p1) (r11 : p3 → p19 → p9) (r12 : p8 → p16 → p0) (r13 : p6 → p16 → p4) (r14 : p11 → p19 → p15) (r15 : p14 → p16 → p7) (r16 : p17 → p20 → p22 → p13) : p13 := by
  have h5 : p5 := r9 f6 f16 f19
  have h20 : p20 := r5 h5 f6
  have h17 : p17 := r6 h5 f6
  have h0 : p0 := r12 f8 f16
  have h22 : p22 := r0 h0 h5
  have h13 : p13 := r16 h17 h20 h22
  exact h13
#print axioms cogModel_3f2bce04d7ecf524225fdae1a8f7daab4bad9169a9248a1feaaab5bbacc5b183

theorem cogModel_520d27c110e94a0b8cc1b3670ddd7b1a326fa578ef3ea198775dc64a7c0b8521 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 : Prop) (f4 : p4) (f5 : p5) (f9 : p9) (f17 : p17) (f22 : p22) (r0 : p5 → p17 → p20 → p18) (r1 : p9 → p17 → p22 → p8) (r2 : p17 → p21 → p2) (r3 : p7 → p20) (r4 : p4 → p9 → p22 → p14) (r5 : p5 → p23) (r6 : p4 → p22 → p25) (r7 : p9 → p1) (r8 : p5 → p6 → p16) (r9 : p5 → p7) (r10 : p4 → p3) (r11 : p9 → p13 → p12) (r12 : p8 → p0) (r13 : p0 → p16 → p19 → p26) (r14 : p4 → p5 → p17 → p6) (r15 : p5 → p8 → p19) (r16 : p9 → p17 → p10) (r17 : p1 → p15) (r18 : p17 → p24 → p11) : p26 := by
  have h8 : p8 := r1 f9 f17 f22
  have h0 : p0 := r12 h8
  have h19 : p19 := r15 f5 h8
  have h6 : p6 := r14 f4 f5 f17
  have h16 : p16 := r8 f5 h6
  have h26 : p26 := r13 h0 h16 h19
  exact h26
#print axioms cogModel_520d27c110e94a0b8cc1b3670ddd7b1a326fa578ef3ea198775dc64a7c0b8521

theorem cogModel_3d2240f15d8489acd4dae553c8f59837ffe22a38b4f93b7e4f11879dca7242bb (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 : Prop) (f1 : p1) (f9 : p9) (f10 : p10) (r0 : p4 → p9 → p14) (r1 : p9 → p13 → p5) (r2 : p18 → p8) (r3 : p3 → p17 → p16) (r4 : p2 → p6 → p19) (r5 : p1 → p2 → p9 → p15) (r6 : p9 → p10 → p12) (r7 : p2 → p19 → p11) (r8 : p1 → p20 → p3) (r9 : p9 → p10 → p6) (r10 : p9 → p6) (r11 : p9 → p10 → p2) (r12 : p9 → p20 → p3) (r13 : p1 → p11 → p17) (r14 : p1 → p15 → p20) (r15 : p12 → p7) (r16 : p6 → p10 → p15) (r17 : p7 → p10 → p18) (r18 : p1 → p7 → p8 → p0) (r19 : p1 → p20 → p17) (r20 : p10 → p19 → p11) : p16 := by
  have h2 : p2 := r11 f9 f10
  have h15 : p15 := r5 f1 h2 f9
  have h20 : p20 := r14 f1 h15
  have h3 : p3 := r8 f1 h20
  have h17 : p17 := r19 f1 h20
  have h16 : p16 := r3 h3 h17
  exact h16
#print axioms cogModel_3d2240f15d8489acd4dae553c8f59837ffe22a38b4f93b7e4f11879dca7242bb

theorem cogModel_8828383eca2a7fef862928bf52f4b67238ddd454bc623af4025e3783d4172b70 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 : Prop) (f0 : p0) (f12 : p12) (f18 : p18) (f22 : p22) (r0 : p14 → p17 → p6) (r1 : p0 → p18 → p16) (r2 : p16 → p22 → p11) (r3 : p17 → p23) (r4 : p2 → p12 → p13) (r5 : p0 → p22 → p16) (r6 : p12 → p17) (r7 : p2 → p14) (r8 : p12 → p18 → p22 → p2) (r9 : p18 → p22 → p19) (r10 : p0 → p24 → p21) (r11 : p12 → p22 → p19) (r12 : p4 → p12 → p1) (r13 : p15 → p22 → p11) (r14 : p12 → p19 → p7) (r15 : p0 → p17 → p18 → p3) (r16 : p5 → p17 → p9) (r17 : p18 → p20 → p10) (r18 : p0 → p18 → p15) (r19 : p0 → p22 → p5) (r20 : p16 → p18 → p7) (r21 : p18 → p22 → p15) (r22 : p12 → p16 → p8) (r23 : p7 → p8 → p11 → p25) : p25 := by
  have h16 : p16 := r1 f0 f18
  have h11 : p11 := r2 h16 f22
  have h7 : p7 := r20 h16 f18
  have h8 : p8 := r22 f12 h16
  have h25 : p25 := r23 h7 h8 h11
  exact h25
#print axioms cogModel_8828383eca2a7fef862928bf52f4b67238ddd454bc623af4025e3783d4172b70

theorem cogModel_803bd3549daa22c837bddb2fae8b4816e61815b747e298456aa58113ede59b89 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 : Prop) (f1 : p1) (f11 : p11) (f12 : p12) (f13 : p13) (f19 : p19) (r0 : p6 → p12 → p15) (r1 : p19 → p4) (r2 : p0 → p12 → p19 → p14) (r3 : p13 → p19 → p0) (r4 : p11 → p10) (r5 : p9 → p2) (r6 : p7 → p9) (r7 : p8 → p7) (r8 : p10 → p12 → p19 → p17) (r9 : p1 → p16 → p18) (r10 : p1 → p8) (r11 : p5 → p11 → p3) : p2 := by
  have h8 : p8 := r10 f1
  have h7 : p7 := r7 h8
  have h9 : p9 := r6 h7
  have h2 : p2 := r5 h9
  exact h2
#print axioms cogModel_803bd3549daa22c837bddb2fae8b4816e61815b747e298456aa58113ede59b89

theorem cogModel_04fe0057264d00e480f26902603a85111ec48fc2a8c339aa53709a02bc3ee363 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 : Prop) (f8 : p8) (f9 : p9) (f17 : p17) (r0 : p3 → p7) (r1 : p17 → p21 → p13) (r2 : p4 → p26 → p14) (r3 : p8 → p17 → p19) (r4 : p0 → p5 → p24) (r5 : p4 → p8 → p3) (r6 : p8 → p9 → p20) (r7 : p17 → p18 → p5) (r8 : p2 → p17 → p10) (r9 : p9 → p20 → p23) (r10 : p4 → p19 → p20 → p23) (r11 : p4 → p9 → p17 → p3) (r12 : p9 → p14 → p0) (r13 : p9 → p17 → p11) (r14 : p4 → p17 → p19 → p22) (r15 : p8 → p22 → p26) (r16 : p7 → p14 → p26 → p5) (r17 : p1 → p8 → p12) (r18 : p17 → p4) (r19 : p8 → p9 → p25 → p21) (r20 : p6 → p9 → p15) (r21 : p8 → p17 → p25) (r22 : p7 → p17 → p14) (r23 : p4 → p7 → p26 → p18) (r24 : p9 → p16) (r25 : p8 → p18 → p0) : p24 := by
  have h4 : p4 := r18 f17
  have h3 : p3 := r5 h4 f8
  have h7 : p7 := r0 h3
  have h14 : p14 := r22 h7 f17
  have h0 : p0 := r12 f9 h14
  have h19 : p19 := r3 f8 f17
  have h22 : p22 := r14 h4 f17 h19
  have h26 : p26 := r15 f8 h22
  have h5 : p5 := r16 h7 h14 h26
  have h24 : p24 := r4 h0 h5
  exact h24
#print axioms cogModel_04fe0057264d00e480f26902603a85111ec48fc2a8c339aa53709a02bc3ee363

theorem cogModel_94e3c3a2b5f75ae0bae26955a2df7133ac1173271cd3d28456ec7bc66ee49ce6 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 : Prop) (f13 : p13) (f14 : p14) (f23 : p23) (f27 : p27) (r0 : p7 → p23 → p10) (r1 : p7 → p27 → p0) (r2 : p14 → p17 → p23 → p16) (r3 : p10 → p27 → p8) (r4 : p13 → p14 → p7) (r5 : p1 → p13 → p18) (r6 : p14 → p20 → p23 → p22) (r7 : p4 → p10 → p19) (r8 : p0 → p14 → p12) (r9 : p6 → p13 → p19) (r10 : p14 → p27 → p11) (r11 : p0 → p13 → p21) (r12 : p10 → p13 → p21) (r13 : p13 → p21 → p4) (r14 : p0 → p14 → p8) (r15 : p12 → p13 → p4) (r16 : p13 → p14 → p23 → p9) (r17 : p2 → p14 → p0) (r18 : p26 → p27 → p5) (r19 : p6 → p27 → p15) (r20 : p3 → p14 → p24) (r21 : p15 → p19 → p25) (r22 : p14 → p27 → p17) (r23 : p23 → p26) (r24 : p7 → p27 → p10) (r25 : p0 → p10 → p12) (r26 : p8 → p13 → p6) (r27 : p4 → p13 → p15) (r28 : p13 → p23 → p27 → p7) (r29 : p14 → p27 → p2) (r30 : p14 → p20) : p25 := by
  have h7 : p7 := r4 f13 f14
  have h10 : p10 := r0 h7 f23
  have h21 : p21 := r12 h10 f13
  have h4 : p4 := r13 f13 h21
  have h15 : p15 := r27 h4 f13
  have h19 : p19 := r7 h4 h10
  have h25 : p25 := r21 h15 h19
  exact h25
#print axioms cogModel_94e3c3a2b5f75ae0bae26955a2df7133ac1173271cd3d28456ec7bc66ee49ce6

theorem cogModel_4c8e825f321c0fe8fa1a20638532ed342f864812b2329e921879d9c019f82aee (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 : Prop) (f0 : p0) (f10 : p10) (f25 : p25) (r0 : p10 → p13 → p23 → p30) (r1 : p13 → p23 → p20) (r2 : p1 → p5 → p10 → p9) (r3 : p10 → p20 → p25 → p21) (r4 : p0 → p25 → p11) (r5 : p17 → p25 → p22) (r6 : p10 → p25 → p5) (r7 : p13 → p16 → p17 → p28) (r8 : p5 → p1) (r9 : p0 → p10 → p6) (r10 : p25 → p30 → p17) (r11 : p0 → p10 → p25 → p13) (r12 : p10 → p26 → p3) (r13 : p21 → p28 → p12) (r14 : p23 → p28 → p14) (r15 : p18 → p25 → p15) (r16 : p2 → p25 → p19) (r17 : p24 → p25 → p4) (r18 : p27 → p29 → p30 → p16) (r19 : p12 → p14 → p8) (r20 : p0 → p10 → p29) (r21 : p10 → p11 → p25 → p7) (r22 : p13 → p29 → p27) (r23 : p0 → p25 → p23) : p8 := by
  have h23 : p23 := r23 f0 f25
  have h13 : p13 := r11 f0 f10 f25
  have h20 : p20 := r1 h13 h23
  have h21 : p21 := r3 f10 h20 f25
  have h30 : p30 := r0 f10 h13 h23
  have h17 : p17 := r10 f25 h30
  have h29 : p29 := r20 f0 f10
  have h27 : p27 := r22 h13 h29
  have h16 : p16 := r18 h27 h29 h30
  have h28 : p28 := r7 h13 h16 h17
  have h12 : p12 := r13 h21 h28
  have h14 : p14 := r14 h23 h28
  have h8 : p8 := r19 h12 h14
  exact h8
#print axioms cogModel_4c8e825f321c0fe8fa1a20638532ed342f864812b2329e921879d9c019f82aee

theorem cogModel_5916bfeacb350e115ddf8fd0658e00ec94ce9f242a022b66d8ca5c3398b4ef66 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 : Prop) (f6 : p6) (f7 : p7) (f8 : p8) (f16 : p16) (f17 : p17) (r0 : p7 → p5) (r1 : p4 → p18) (r2 : p2 → p7 → p9) (r3 : p13 → p16 → p3) (r4 : p1 → p13 → p14 → p0) (r5 : p18 → p15) (r6 : p14 → p1) (r7 : p7 → p12) (r8 : p6 → p13) (r9 : p8 → p13 → p14) (r10 : p1 → p3 → p14 → p19) (r11 : p10 → p16 → p11) (r12 : p5 → p4) : p15 := by
  have h5 : p5 := r0 f7
  have h4 : p4 := r12 h5
  have h18 : p18 := r1 h4
  have h15 : p15 := r5 h18
  exact h15
#print axioms cogModel_5916bfeacb350e115ddf8fd0658e00ec94ce9f242a022b66d8ca5c3398b4ef66

theorem cogModel_e1a46211e18f67bcc65adc485b428af07442cf24245f09650bdcb949b461145a (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 : Prop) (f2 : p2) (f10 : p10) (f12 : p12) (r0 : p10 → p15) (r1 : p2 → p7 → p12 → p14) (r2 : p4 → p10 → p12 → p18) (r3 : p0 → p2 → p14 → p11) (r4 : p2 → p0) (r5 : p2 → p13 → p17) (r6 : p9 → p10 → p12 → p7) (r7 : p2 → p10 → p12 → p9) (r8 : p15 → p19) (r9 : p12 → p6) (r10 : p6 → p7 → p9 → p4) (r11 : p19 → p1) (r12 : p5 → p12 → p16) (r13 : p3 → p10 → p8) : p1 := by
  have h15 : p15 := r0 f10
  have h19 : p19 := r8 h15
  have h1 : p1 := r11 h19
  exact h1
#print axioms cogModel_e1a46211e18f67bcc65adc485b428af07442cf24245f09650bdcb949b461145a

theorem cogModel_a7bbb52d59214dd1e7d200781b290395a74e952fc0f7ab93db899173f1f399bb (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 : Prop) (f12 : p12) (f13 : p13) (f18 : p18) (r0 : p16 → p17 → p27) (r1 : p9 → p17 → p5) (r2 : p10 → p18 → p11) (r3 : p9 → p18 → p16) (r4 : p0 → p9 → p7) (r5 : p12 → p13 → p18 → p9) (r6 : p10 → p28) (r7 : p13 → p25 → p3) (r8 : p12 → p13 → p10) (r9 : p10 → p21 → p28 → p8) (r10 : p13 → p19 → p22) (r11 : p0 → p14 → p15) (r12 : p11 → p12 → p18 → p20) (r13 : p5 → p24 → p14) (r14 : p12 → p18 → p4) (r15 : p13 → p24 → p1) (r16 : p12 → p24) (r17 : p11 → p12 → p20 → p23) (r18 : p7 → p15 → p6) (r19 : p5 → p13 → p0) (r20 : p10 → p12 → p18 → p21) (r21 : p13 → p26 → p2) (r22 : p9 → p24 → p17) : p6 := by
  have h9 : p9 := r5 f12 f13 f18
  have h24 : p24 := r16 f12
  have h17 : p17 := r22 h9 h24
  have h5 : p5 := r1 h9 h17
  have h0 : p0 := r19 h5 f13
  have h7 : p7 := r4 h0 h9
  have h14 : p14 := r13 h5 h24
  have h15 : p15 := r11 h0 h14
  have h6 : p6 := r18 h7 h15
  exact h6
#print axioms cogModel_a7bbb52d59214dd1e7d200781b290395a74e952fc0f7ab93db899173f1f399bb

theorem cogModel_8a2ddd09917939714400c1e77350f352e0814662a77c80f937b9a84c6da28069 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 : Prop) (f2 : p2) (f12 : p12) (f13 : p13) (f19 : p19) (f20 : p20) (r0 : p3 → p12 → p19 → p28) (r1 : p2 → p20 → p21 → p27) (r2 : p5 → p12 → p15 → p7) (r3 : p9 → p20 → p25) (r4 : p2 → p19 → p20 → p6) (r5 : p7 → p0) (r6 : p0 → p11) (r7 : p3 → p22 → p18) (r8 : p13 → p19 → p20 → p1) (r9 : p12 → p26) (r10 : p1 → p3 → p4) (r11 : p20 → p21 → p22) (r12 : p26 → p5) (r13 : p16 → p20 → p8) (r14 : p12 → p21 → p3) (r15 : p1 → p12 → p29) (r16 : p2 → p13 → p19 → p15) (r17 : p1 → p21) (r18 : p1 → p20 → p23) (r19 : p11 → p13 → p10) (r20 : p24 → p17) (r21 : p4 → p18 → p28 → p14) (r22 : p5 → p24) : p14 := by
  have h1 : p1 := r8 f13 f19 f20
  have h21 : p21 := r17 h1
  have h22 : p22 := r11 f20 h21
  have h3 : p3 := r14 f12 h21
  have h18 : p18 := r7 h3 h22
  have h4 : p4 := r10 h1 h3
  have h28 : p28 := r0 h3 f12 f19
  have h14 : p14 := r21 h4 h18 h28
  exact h14
#print axioms cogModel_8a2ddd09917939714400c1e77350f352e0814662a77c80f937b9a84c6da28069

theorem cogModel_eeb3c1c6c1883a77608e7460eb475ec5daa10905e2ebb074f67b63776d64effc (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 : Prop) (f4 : p4) (f10 : p10) (f22 : p22) (r0 : p14 → p16) (r1 : p6 → p16 → p22 → p1) (r2 : p4 → p15 → p19) (r3 : p4 → p10 → p28) (r4 : p10 → p26 → p14) (r5 : p8 → p28 → p15) (r6 : p8 → p15 → p22 → p17) (r7 : p4 → p22 → p11) (r8 : p10 → p7) (r9 : p4 → p22 → p8) (r10 : p12 → p28 → p13) (r11 : p10 → p20 → p25) (r12 : p13 → p17 → p19 → p24) (r13 : p0 → p4 → p5) (r14 : p4 → p9) (r15 : p10 → p22 → p26) (r16 : p21 → p23 → p6) (r17 : p10 → p28 → p12) (r18 : p10 → p14 → p16 → p27) (r19 : p26 → p23) (r20 : p10 → p21) (r21 : p11 → p27 → p2) (r22 : p10 → p18 → p3) : p24 := by
  have h8 : p8 := r9 f4 f22
  have h28 : p28 := r3 f4 f10
  have h15 : p15 := r5 h8 h28
  have h19 : p19 := r2 f4 h15
  have h17 : p17 := r6 h8 h15 f22
  have h12 : p12 := r17 f10 h28
  have h13 : p13 := r10 h12 h28
  have h24 : p24 := r12 h13 h17 h19
  exact h24
#print axioms cogModel_eeb3c1c6c1883a77608e7460eb475ec5daa10905e2ebb074f67b63776d64effc

theorem cogModel_565c2140189ef7ff0e610f8661beed048214813bcabef3e0c055e94a135d3ff5 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 : Prop) (f6 : p6) (f14 : p14) (f15 : p15) (r0 : p1 → p12 → p20) (r1 : p15 → p16 → p8) (r2 : p1 → p2 → p6 → p12) (r3 : p14 → p1) (r4 : p1 → p15 → p2) (r5 : p12 → p7) (r6 : p6 → p11 → p5) (r7 : p6 → p15 → p16) (r8 : p15 → p9) (r9 : p14 → p21 → p22) (r10 : p15 → p23 → p0) (r11 : p6 → p19 → p17) (r12 : p10 → p14 → p18) (r13 : p12 → p15 → p13) (r14 : p6 → p14 → p23) (r15 : p6 → p14 → p9) (r16 : p2 → p6 → p21 → p3) (r17 : p0 → p8 → p4) (r18 : p6 → p23 → p8) (r19 : p1 → p15 → p21) : p4 := by
  have h23 : p23 := r14 f6 f14
  have h0 : p0 := r10 f15 h23
  have h8 : p8 := r18 f6 h23
  have h4 : p4 := r17 h0 h8
  exact h4
#print axioms cogModel_565c2140189ef7ff0e610f8661beed048214813bcabef3e0c055e94a135d3ff5

theorem cogModel_2efdbf388c7e0a273bc26a158d8c12be3427d6ae5249fdd114b1d9e43c3388da (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 : Prop) (f15 : p15) (f17 : p17) (f18 : p18) (f20 : p20) (f26 : p26) (r0 : p17 → p26 → p2) (r1 : p11 → p15 → p4) (r2 : p1 → p18 → p26 → p6) (r3 : p17 → p26 → p19) (r4 : p18 → p23 → p27) (r5 : p15 → p21) (r6 : p16 → p24) (r7 : p18 → p8) (r8 : p9 → p26 → p5) (r9 : p10 → p16) (r10 : p6 → p17 → p19 → p22) (r11 : p8 → p10) (r12 : p15 → p18 → p1) (r13 : p12 → p7) (r14 : p24 → p12) (r15 : p2 → p15 → p17 → p25) (r16 : p26 → p14) (r17 : p6 → p15 → p0) (r18 : p13 → p20 → p3) : p7 := by
  have h8 : p8 := r7 f18
  have h10 : p10 := r11 h8
  have h16 : p16 := r9 h10
  have h24 : p24 := r6 h16
  have h12 : p12 := r14 h24
  have h7 : p7 := r13 h12
  exact h7
#print axioms cogModel_2efdbf388c7e0a273bc26a158d8c12be3427d6ae5249fdd114b1d9e43c3388da

theorem cogModel_19c4724e39c9be615c471ae1eadf413d00d910552192d6bda5aabe82dcb6a0e5 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 : Prop) (f10 : p10) (f13 : p13) (f16 : p16) (f22 : p22) (f24 : p24) (r0 : p9 → p13 → p24 → p20) (r1 : p13 → p24 → p19) (r2 : p10 → p22 → p24 → p8) (r3 : p2 → p24 → p23) (r4 : p10 → p13 → p16 → p9) (r5 : p19 → p22 → p24 → p0) (r6 : p15 → p16 → p12) (r7 : p1 → p8 → p16 → p5) (r8 : p5 → p7 → p8 → p14) (r9 : p1 → p24 → p7) (r10 : p5 → p10 → p17) (r11 : p13 → p22 → p1) (r12 : p4 → p22 → p3) (r13 : p6 → p13 → p21) (r14 : p14 → p17 → p11) (r15 : p0 → p16 → p20 → p18) : p11 := by
  have h8 : p8 := r2 f10 f22 f24
  have h1 : p1 := r11 f13 f22
  have h5 : p5 := r7 h1 h8 f16
  have h17 : p17 := r10 h5 f10
  have h7 : p7 := r9 h1 f24
  have h14 : p14 := r8 h5 h7 h8
  have h11 : p11 := r14 h14 h17
  exact h11
#print axioms cogModel_19c4724e39c9be615c471ae1eadf413d00d910552192d6bda5aabe82dcb6a0e5

theorem cogModel_9c3ccc2042c6b32510d659a2b2469bbb7d81a20e98788038ea2e21347c56c91f (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 : Prop) (f2 : p2) (f10 : p10) (f19 : p19) (r0 : p10 → p19 → p18) (r1 : p2 → p16 → p12) (r2 : p22 → p24 → p9) (r3 : p10 → p18 → p19 → p6) (r4 : p19 → p22 → p24) (r5 : p8 → p14 → p7) (r6 : p19 → p22 → p15) (r7 : p2 → p10 → p19 → p22) (r8 : p22 → p29 → p4) (r9 : p10 → p19 → p22 → p24) (r10 : p14 → p22 → p29) (r11 : p1 → p4 → p7 → p13) (r12 : p6 → p28 → p27) (r13 : p10 → p14 → p8) (r14 : p14 → p26 → p8) (r15 : p6 → p10 → p21) (r16 : p2 → p15 → p14) (r17 : p21 → p0) (r18 : p18 → p25) (r19 : p15 → p24 → p14) (r20 : p9 → p19 → p29) (r21 : p2 → p10 → p26) (r22 : p8 → p24 → p1) (r23 : p2 → p8 → p1) (r24 : p10 → p23 → p5) (r25 : p21 → p25 → p28 → p11) (r26 : p18 → p21 → p17) (r27 : p2 → p19 → p22) (r28 : p18 → p28) (r29 : p19 → p20 → p3) : p13 := by
  have h22 : p22 := r27 f2 f19
  have h24 : p24 := r4 f19 h22
  have h9 : p9 := r2 h22 h24
  have h29 : p29 := r20 h9 f19
  have h4 : p4 := r8 h22 h29
  have h15 : p15 := r6 f19 h22
  have h14 : p14 := r16 f2 h15
  have h8 : p8 := r13 f10 h14
  have h7 : p7 := r5 h8 h14
  have h1 : p1 := r22 h8 h24
  have h13 : p13 := r11 h1 h4 h7
  exact h13
#print axioms cogModel_9c3ccc2042c6b32510d659a2b2469bbb7d81a20e98788038ea2e21347c56c91f

theorem cogModel_3ebc51b0dd95c179e42066aad9309c8e22929cf9c49236ab4bb9846b5a62954d (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 : Prop) (f5 : p5) (f7 : p7) (f9 : p9) (f20 : p20) (f25 : p25) (r0 : p9 → p14 → p20 → p0) (r1 : p9 → p12) (r2 : p4 → p18 → p16) (r3 : p15 → p21 → p14) (r4 : p10 → p20 → p2) (r5 : p16 → p24 → p27 → p1) (r6 : p7 → p23 → p15) (r7 : p9 → p22) (r8 : p5 → p9 → p18) (r9 : p4 → p18 → p24) (r10 : p7 → p9 → p20 → p21) (r11 : p0 → p21 → p26 → p17) (r12 : p11 → p25 → p3) (r13 : p7 → p8 → p13) (r14 : p5 → p9 → p6) (r15 : p19 → p27) (r16 : p20 → p25 → p19) (r17 : p20 → p25 → p26) (r18 : p7 → p25 → p4) (r19 : p20 → p25 → p23) : p1 := by
  have h18 : p18 := r8 f5 f9
  have h4 : p4 := r18 f7 f25
  have h16 : p16 := r2 h4 h18
  have h24 : p24 := r9 h4 h18
  have h19 : p19 := r16 f20 f25
  have h27 : p27 := r15 h19
  have h1 : p1 := r5 h16 h24 h27
  exact h1
#print axioms cogModel_3ebc51b0dd95c179e42066aad9309c8e22929cf9c49236ab4bb9846b5a62954d

theorem cogModel_d67e0d43b8e533148cf588b32e24ee6dec0226c32b045baee36f3de7ab9ce59f (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 : Prop) (f1 : p1) (f2 : p2) (f10 : p10) (f14 : p14) (r0 : p8 → p4) (r1 : p14 → p15) (r2 : p14 → p19) (r3 : p1 → p2 → p10 → p9) (r4 : p8 → p10 → p14 → p25) (r5 : p12 → p7) (r6 : p14 → p24 → p11) (r7 : p14 → p19 → p25 → p0) (r8 : p2 → p8) (r9 : p14 → p20 → p17) (r10 : p4 → p13) (r11 : p16 → p18) (r12 : p2 → p14 → p15 → p3) (r13 : p18 → p12) (r14 : p7 → p23) (r15 : p5 → p10 → p22) (r16 : p1 → p21 → p6) (r17 : p14 → p16) : p23 := by
  have h16 : p16 := r17 f14
  have h18 : p18 := r11 h16
  have h12 : p12 := r13 h18
  have h7 : p7 := r5 h12
  have h23 : p23 := r14 h7
  exact h23
#print axioms cogModel_d67e0d43b8e533148cf588b32e24ee6dec0226c32b045baee36f3de7ab9ce59f

theorem cogModel_52a7e7d8bef6cdc4ad14b497618dadb820d204fbf494ded8c4406115eff451cc (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 : Prop) (f2 : p2) (f6 : p6) (f11 : p11) (f17 : p17) (f24 : p24) (r0 : p8 → p15 → p21) (r1 : p6 → p24 → p14) (r2 : p2 → p17 → p8) (r3 : p6 → p11 → p17 → p12) (r4 : p2 → p11 → p15 → p0) (r5 : p6 → p21 → p13) (r6 : p12 → p10) (r7 : p2 → p16) (r8 : p21 → p18) (r9 : p6 → p19) (r10 : p2 → p11 → p17 → p1) (r11 : p13 → p18 → p5) (r12 : p1 → p10 → p4) (r13 : p6 → p22 → p26) (r14 : p17 → p25 → p23) (r15 : p11 → p17 → p15) (r16 : p2 → p9 → p3) (r17 : p17 → p7) (r18 : p1 → p11 → p20) : p5 := by
  have h8 : p8 := r2 f2 f17
  have h15 : p15 := r15 f11 f17
  have h21 : p21 := r0 h8 h15
  have h18 : p18 := r8 h21
  have h13 : p13 := r5 f6 h21
  have h5 : p5 := r11 h13 h18
  exact h5
#print axioms cogModel_52a7e7d8bef6cdc4ad14b497618dadb820d204fbf494ded8c4406115eff451cc

theorem cogModel_50b46395947241772040e7d4842750954a505de77a9f511c898695a3fddb92db (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 : Prop) (f0 : p0) (f2 : p2) (f6 : p6) (f7 : p7) (f18 : p18) (r0 : p5 → p7 → p3) (r1 : p15 → p1) (r2 : p2 → p6 → p10) (r3 : p0 → p9) (r4 : p1 → p8) (r5 : p14 → p16) (r6 : p7 → p19 → p12) (r7 : p4 → p20) (r8 : p13 → p11) (r9 : p8 → p4) (r10 : p14 → p17 → p13) (r11 : p18 → p15) (r12 : p10 → p14) (r13 : p2 → p6 → p18 → p17) : p20 := by
  have h15 : p15 := r11 f18
  have h1 : p1 := r1 h15
  have h8 : p8 := r4 h1
  have h4 : p4 := r9 h8
  have h20 : p20 := r7 h4
  exact h20
#print axioms cogModel_50b46395947241772040e7d4842750954a505de77a9f511c898695a3fddb92db

theorem cogModel_a65f1554780a51a19b955ea77e7b1c927770a9687191ededf2e52f05355fdd57 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 : Prop) (f4 : p4) (f6 : p6) (f9 : p9) (f11 : p11) (f19 : p19) (r0 : p7 → p15) (r1 : p18 → p19 → p13) (r2 : p11 → p7) (r3 : p5 → p12) (r4 : p6 → p19 → p2) (r5 : p12 → p17) (r6 : p1 → p11 → p8) (r7 : p17 → p10) (r8 : p9 → p11 → p19 → p1) (r9 : p15 → p5) (r10 : p0 → p16) (r11 : p4 → p11 → p19 → p0) (r12 : p0 → p1 → p4 → p20) (r13 : p3 → p6 → p14) : p10 := by
  have h7 : p7 := r2 f11
  have h15 : p15 := r0 h7
  have h5 : p5 := r9 h15
  have h12 : p12 := r3 h5
  have h17 : p17 := r5 h12
  have h10 : p10 := r7 h17
  exact h10
#print axioms cogModel_a65f1554780a51a19b955ea77e7b1c927770a9687191ededf2e52f05355fdd57

theorem cogModel_3f450e369aecb5c66584ad9f74630d2feda63e4b5baca43f4fc0114ae69e4454 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 : Prop) (f1 : p1) (f6 : p6) (f10 : p10) (f13 : p13) (f27 : p27) (r0 : p27 → p28 → p12) (r1 : p7 → p27 → p3) (r2 : p1 → p13 → p15 → p9) (r3 : p7 → p13 → p15 → p28) (r4 : p12 → p14 → p25 → p18) (r5 : p3 → p27 → p14) (r6 : p10 → p20 → p17) (r7 : p10 → p29 → p4) (r8 : p1 → p28 → p25) (r9 : p5 → p27 → p26) (r10 : p27 → p2) (r11 : p6 → p27 → p15) (r12 : p6 → p13 → p23) (r13 : p8 → p13 → p24) (r14 : p1 → p6 → p16 → p22) (r15 : p10 → p13 → p19) (r16 : p1 → p10 → p27 → p21) (r17 : p2 → p10 → p7) (r18 : p10 → p13 → p16) (r19 : p13 → p19 → p0) (r20 : p13 → p16 → p27 → p11) : p18 := by
  have h15 : p15 := r11 f6 f27
  have h2 : p2 := r10 f27
  have h7 : p7 := r17 h2 f10
  have h28 : p28 := r3 h7 f13 h15
  have h12 : p12 := r0 f27 h28
  have h25 : p25 := r8 f1 h28
  have h3 : p3 := r1 h7 f27
  have h14 : p14 := r5 h3 f27
  have h18 : p18 := r4 h12 h14 h25
  exact h18
#print axioms cogModel_3f450e369aecb5c66584ad9f74630d2feda63e4b5baca43f4fc0114ae69e4454

theorem cogModel_80815cce52f2ad4753ae98a00087113657f0582431e2933e23022a73ef906760 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 : Prop) (f9 : p9) (f13 : p13) (f17 : p17) (r0 : p19 → p20) (r1 : p13 → p18 → p1) (r2 : p2 → p4 → p11) (r3 : p2 → p17 → p4) (r4 : p11 → p13 → p14 → p8) (r5 : p4 → p11 → p21 → p0) (r6 : p13 → p7) (r7 : p7 → p5) (r8 : p14 → p12) (r9 : p13 → p17 → p2) (r10 : p10 → p19) (r11 : p13 → p14) (r12 : p5 → p10) (r13 : p2 → p11 → p17 → p21) (r14 : p11 → p3) (r15 : p20 → p6) (r16 : p9 → p16 → p15) : p6 := by
  have h7 : p7 := r6 f13
  have h5 : p5 := r7 h7
  have h10 : p10 := r12 h5
  have h19 : p19 := r10 h10
  have h20 : p20 := r0 h19
  have h6 : p6 := r15 h20
  exact h6
#print axioms cogModel_80815cce52f2ad4753ae98a00087113657f0582431e2933e23022a73ef906760

theorem cogModel_5949745c40e973eb762aac7929900709c6a721320ff55c9680f224699f38c53c (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 : Prop) (f1 : p1) (f15 : p15) (f28 : p28) (r0 : p1 → p17 → p20) (r1 : p4 → p18 → p23) (r2 : p2 → p10 → p7) (r3 : p11 → p21) (r4 : p1 → p12 → p9) (r5 : p17 → p24 → p28 → p27) (r6 : p1 → p26 → p25) (r7 : p1 → p15 → p28 → p4) (r8 : p8 → p21 → p28 → p13) (r9 : p11 → p16 → p21 → p0) (r10 : p1 → p20 → p5) (r11 : p15 → p18) (r12 : p15 → p28 → p17) (r13 : p1 → p23 → p16) (r14 : p22 → p28 → p10) (r15 : p1 → p6 → p3) (r16 : p5 → p22 → p2) (r17 : p15 → p28 → p8) (r18 : p8 → p15 → p11) (r19 : p1 → p28 → p19) (r20 : p17 → p28 → p14) (r21 : p20 → p24 → p22) (r22 : p17 → p19 → p24) : p7 := by
  have h19 : p19 := r19 f1 f28
  have h17 : p17 := r12 f15 f28
  have h20 : p20 := r0 f1 h17
  have h5 : p5 := r10 f1 h20
  have h24 : p24 := r22 h17 h19
  have h22 : p22 := r21 h20 h24
  have h10 : p10 := r14 h22 f28
  have h2 : p2 := r16 h5 h22
  have h7 : p7 := r2 h2 h10
  exact h7
#print axioms cogModel_5949745c40e973eb762aac7929900709c6a721320ff55c9680f224699f38c53c

theorem cogModel_cd16415239b5dfbe0217ce383e5cac9c4925fca94f129acffc06a86868d0ace9 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 : Prop) (f4 : p4) (f5 : p5) (f7 : p7) (f8 : p8) (f14 : p14) (r0 : p2 → p15) (r1 : p15 → p1) (r2 : p8 → p2) (r3 : p6 → p8 → p11) (r4 : p7 → p10 → p14 → p18) (r5 : p4 → p12) (r6 : p0 → p7 → p9) (r7 : p4 → p10) (r8 : p7 → p16 → p3) (r9 : p8 → p10 → p12 → p17) (r10 : p10 → p13) : p1 := by
  have h2 : p2 := r2 f8
  have h15 : p15 := r0 h2
  have h1 : p1 := r1 h15
  exact h1
#print axioms cogModel_cd16415239b5dfbe0217ce383e5cac9c4925fca94f129acffc06a86868d0ace9

theorem cogModel_ff05c18c653d42d7881020f919b5c8ef41da64b5be146af43203b8d8b740f7e8 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 : Prop) (f3 : p3) (f5 : p5) (f13 : p13) (r0 : p2 → p13 → p0) (r1 : p4 → p16 → p11) (r2 : p5 → p7 → p16 → p12) (r3 : p4 → p7) (r4 : p14 → p9) (r5 : p3 → p7 → p8) (r6 : p5 → p14) (r7 : p9 → p10) (r8 : p3 → p17 → p6) (r9 : p3 → p5 → p13 → p4) (r10 : p3 → p4 → p16) (r11 : p12 → p13 → p1) (r12 : p5 → p15) : p10 := by
  have h14 : p14 := r6 f5
  have h9 : p9 := r4 h14
  have h10 : p10 := r7 h9
  exact h10
#print axioms cogModel_ff05c18c653d42d7881020f919b5c8ef41da64b5be146af43203b8d8b740f7e8

theorem cogModel_40be6a7db5a6636136dd2875f8cf4fa841e623c9789ac1be978b9d32ba83872e (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 : Prop) (f8 : p8) (f16 : p16) (f20 : p20) (r0 : p16 → p11) (r1 : p0 → p8 → p15 → p17) (r2 : p2 → p12 → p19) (r3 : p16 → p14) (r4 : p0 → p15) (r5 : p11 → p16 → p2) (r6 : p4 → p20 → p21) (r7 : p8 → p20 → p5) (r8 : p8 → p16 → p20 → p0) (r9 : p5 → p11 → p16 → p2) (r10 : p8 → p16 → p20 → p11) (r11 : p6 → p16 → p9) (r12 : p0 → p1) (r13 : p1 → p3) (r14 : p11 → p20 → p12) (r15 : p11 → p16 → p12) (r16 : p13 → p20 → p18) (r17 : p8 → p22 → p10) (r18 : p1 → p7) : p19 := by
  have h5 : p5 := r7 f8 f20
  have h11 : p11 := r10 f8 f16 f20
  have h2 : p2 := r5 h11 f16
  have h12 : p12 := r14 h11 f20
  have h19 : p19 := r2 h2 h12
  exact h19
#print axioms cogModel_40be6a7db5a6636136dd2875f8cf4fa841e623c9789ac1be978b9d32ba83872e

theorem cogModel_b316e2b12187d084703da54bdd261bb081f72078251c22d4096bbb0e7ba78207 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 : Prop) (f1 : p1) (f9 : p9) (f13 : p13) (f14 : p14) (f23 : p23) (r0 : p23 → p0) (r1 : p14 → p23 → p6) (r2 : p6 → p9 → p13 → p16) (r3 : p15 → p3) (r4 : p1 → p9 → p15 → p17) (r5 : p0 → p8) (r6 : p17 → p22) (r7 : p12 → p14 → p20) (r8 : p18 → p19) (r9 : p5 → p14 → p10) (r10 : p1 → p7 → p2) (r11 : p17 → p4) (r12 : p8 → p18) (r13 : p17 → p11) (r14 : p1 → p4 → p23 → p21) (r15 : p1 → p9 → p14 → p15) : p19 := by
  have h0 : p0 := r0 f23
  have h8 : p8 := r5 h0
  have h18 : p18 := r12 h8
  have h19 : p19 := r8 h18
  exact h19
#print axioms cogModel_b316e2b12187d084703da54bdd261bb081f72078251c22d4096bbb0e7ba78207

theorem cogModel_c0060f06a7d80136673c53db23d9f0d4d0b8503ad6f3316898092b75c60de036 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 : Prop) (f0 : p0) (f10 : p10) (f12 : p12) (f31 : p31) (r0 : p8 → p11 → p18) (r1 : p20 → p32) (r2 : p4 → p10 → p31 → p6) (r3 : p12 → p22 → p14) (r4 : p33 → p2) (r5 : p10 → p28 → p5) (r6 : p10 → p19 → p32 → p27) (r7 : p12 → p26 → p15) (r8 : p12 → p16 → p34 → p8) (r9 : p12 → p31 → p21) (r10 : p2 → p10 → p33 → p29) (r11 : p10 → p30 → p7) (r12 : p12 → p23 → p35) (r13 : p20 → p24) (r14 : p0 → p10 → p12 → p13) (r15 : p0 → p10 → p12 → p25) (r16 : p2 → p26 → p29 → p11) (r17 : p0 → p26) (r18 : p12 → p13 → p31 → p3) (r19 : p0 → p12 → p31 → p20) (r20 : p0 → p2 → p31 → p16) (r21 : p1 → p12 → p31 → p17) (r22 : p10 → p25 → p4) (r23 : p0 → p26 → p31 → p33) (r24 : p3 → p26 → p31 → p34) (r25 : p19 → p9) (r26 : p12 → p30) (r27 : p10 → p20 → p31 → p1) (r28 : p24 → p30 → p19) : p18 := by
  have h26 : p26 := r17 f0
  have h33 : p33 := r23 f0 h26 f31
  have h2 : p2 := r4 h33
  have h16 : p16 := r20 f0 h2 f31
  have h29 : p29 := r10 h2 f10 h33
  have h11 : p11 := r16 h2 h26 h29
  have h13 : p13 := r14 f0 f10 f12
  have h3 : p3 := r18 f12 h13 f31
  have h34 : p34 := r24 h3 h26 f31
  have h8 : p8 := r8 f12 h16 h34
  have h18 : p18 := r0 h8 h11
  exact h18
#print axioms cogModel_c0060f06a7d80136673c53db23d9f0d4d0b8503ad6f3316898092b75c60de036

theorem cogModel_d3150964724c0f4dd983f39962e77c173d37fc18baf149d5e4a63c5b505e1b17 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 : Prop) (f2 : p2) (f12 : p12) (f23 : p23) (f24 : p24) (r0 : p2 → p24 → p27) (r1 : p5 → p24 → p26) (r2 : p12 → p23 → p17) (r3 : p6 → p20 → p21) (r4 : p3 → p12 → p13) (r5 : p2 → p11 → p24 → p1) (r6 : p12 → p25) (r7 : p2 → p23 → p20) (r8 : p4 → p12 → p14) (r9 : p23 → p18) (r10 : p12 → p20 → p27 → p6) (r11 : p7 → p15) (r12 : p2 → p12 → p20) (r13 : p12 → p11) (r14 : p11 → p12 → p1) (r15 : p1 → p23 → p21) (r16 : p6 → p23 → p22) (r17 : p12 → p15 → p17 → p8) (r18 : p24 → p19) (r19 : p12 → p18 → p24 → p7) (r20 : p23 → p24 → p27) (r21 : p21 → p22 → p10) (r22 : p7 → p0) (r23 : p9 → p23 → p16) (r24 : p11 → p23 → p6) : p10 := by
  have h20 : p20 := r7 f2 f23
  have h11 : p11 := r13 f12
  have h6 : p6 := r24 h11 f23
  have h22 : p22 := r16 h6 f23
  have h21 : p21 := r3 h6 h20
  have h10 : p10 := r21 h21 h22
  exact h10
#print axioms cogModel_d3150964724c0f4dd983f39962e77c173d37fc18baf149d5e4a63c5b505e1b17

theorem cogModel_200c165271418736cf7c538e7e4d2733659b421ae847f4f337c107123419d65c (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 : Prop) (f7 : p7) (f13 : p13) (f21 : p21) (r0 : p6 → p7 → p23 → p22) (r1 : p7 → p13 → p21 → p6) (r2 : p4 → p6 → p13 → p3) (r3 : p0 → p15) (r4 : p7 → p24 → p18) (r5 : p13 → p21 → p23) (r6 : p7 → p13 → p22 → p9) (r7 : p7 → p13 → p19 → p24) (r8 : p9 → p13 → p27 → p26) (r9 : p7 → p22 → p27) (r10 : p12 → p28) (r11 : p19 → p24 → p20) (r12 : p7 → p14 → p16) (r13 : p3 → p10 → p17 → p8) (r14 : p21 → p25 → p10) (r15 : p9 → p11 → p22 → p4) (r16 : p5 → p21 → p1) (r17 : p21 → p12) (r18 : p7 → p21 → p29) (r19 : p7 → p12 → p21 → p0) (r20 : p22 → p29 → p2) (r21 : p21 → p23 → p29 → p11) (r22 : p7 → p13 → p21 → p19) (r23 : p9 → p25 → p27 → p17) (r24 : p11 → p27 → p25) : p8 := by
  have h6 : p6 := r1 f7 f13 f21
  have h23 : p23 := r5 f13 f21
  have h22 : p22 := r0 h6 f7 h23
  have h27 : p27 := r9 f7 h22
  have h9 : p9 := r6 f7 f13 h22
  have h29 : p29 := r18 f7 f21
  have h11 : p11 := r21 f21 h23 h29
  have h25 : p25 := r24 h11 h27
  have h10 : p10 := r14 f21 h25
  have h17 : p17 := r23 h9 h25 h27
  have h4 : p4 := r15 h9 h11 h22
  have h3 : p3 := r2 h4 h6 f13
  have h8 : p8 := r13 h3 h10 h17
  exact h8
#print axioms cogModel_200c165271418736cf7c538e7e4d2733659b421ae847f4f337c107123419d65c

theorem cogModel_5548d211515c10e66a7f47a6f08e3fbf56dca2f3532b59c63bcf71a47228b44a (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 p35 p36 p37 : Prop) (f8 : p8) (f22 : p22) (f24 : p24) (f27 : p27) (f28 : p28) (r0 : p2 → p27 → p9) (r1 : p30 → p26) (r2 : p24 → p27 → p30 → p0) (r3 : p18 → p23 → p33 → p12) (r4 : p11 → p22 → p24 → p19) (r5 : p24 → p28 → p3) (r6 : p8 → p27 → p36 → p14) (r7 : p17 → p32 → p23) (r8 : p1 → p8 → p33) (r9 : p24 → p28 → p11) (r10 : p16 → p21 → p27 → p35) (r11 : p35 → p1) (r12 : p30 → p13) (r13 : p27 → p28 → p37) (r14 : p3 → p27 → p28 → p30) (r15 : p24 → p27 → p6) (r16 : p17 → p22 → p32) (r17 : p20 → p22 → p29) (r18 : p37 → p34) (r19 : p24 → p25 → p31) (r20 : p6 → p16) (r21 : p8 → p17 → p22 → p5) (r22 : p14 → p28 → p10) (r23 : p28 → p15) (r24 : p16 → p19 → p28 → p17) (r25 : p22 → p27 → p36) (r26 : p1 → p21 → p32 → p18) (r27 : p6 → p28 → p21) (r28 : p3 → p10 → p36 → p7) (r29 : p8 → p4) : p12 := by
  have h6 : p6 := r15 f24 f27
  have h21 : p21 := r27 h6 f28
  have h16 : p16 := r20 h6
  have h35 : p35 := r10 h16 h21 f27
  have h1 : p1 := r11 h35
  have h33 : p33 := r8 h1 f8
  have h11 : p11 := r9 f24 f28
  have h19 : p19 := r4 h11 f22 f24
  have h17 : p17 := r24 h16 h19 f28
  have h32 : p32 := r16 h17 f22
  have h23 : p23 := r7 h17 h32
  have h18 : p18 := r26 h1 h21 h32
  have h12 : p12 := r3 h18 h23 h33
  exact h12
#print axioms cogModel_5548d211515c10e66a7f47a6f08e3fbf56dca2f3532b59c63bcf71a47228b44a

theorem cogModel_a3fef154333094a3a6a288b1ca325cfb5bcaff6c52b1b44154165c34cd4c4f43 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 : Prop) (f1 : p1) (f16 : p16) (f18 : p18) (r0 : p9 → p8) (r1 : p16 → p11) (r2 : p21 → p2) (r3 : p1 → p20 → p14) (r4 : p11 → p6) (r5 : p8 → p3) (r6 : p1 → p18 → p0) (r7 : p4 → p18 → p15) (r8 : p1 → p7 → p16 → p21) (r9 : p6 → p9) (r10 : p1 → p13 → p5) (r11 : p3 → p19) (r12 : p1 → p16 → p7) (r13 : p17 → p18 → p12) (r14 : p16 → p18 → p21 → p10) : p19 := by
  have h11 : p11 := r1 f16
  have h6 : p6 := r4 h11
  have h9 : p9 := r9 h6
  have h8 : p8 := r0 h9
  have h3 : p3 := r5 h8
  have h19 : p19 := r11 h3
  exact h19
#print axioms cogModel_a3fef154333094a3a6a288b1ca325cfb5bcaff6c52b1b44154165c34cd4c4f43

theorem cogModel_953f8133c47a6c88ab0edbf064a152843d0cdfa212b34c92939fdc5743db1e2a (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 : Prop) (f2 : p2) (f14 : p14) (f16 : p16) (f19 : p19) (f20 : p20) (r0 : p16 → p10) (r1 : p3 → p5 → p12 → p22) (r2 : p14 → p21 → p18) (r3 : p19 → p9) (r4 : p12 → p19 → p20 → p5) (r5 : p12 → p23) (r6 : p7 → p18 → p1) (r7 : p9 → p3) (r8 : p2 → p9 → p16 → p15) (r9 : p19 → p17) (r10 : p9 → p15 → p8) (r11 : p4 → p20 → p6) (r12 : p13 → p16 → p0) (r13 : p17 → p11) (r14 : p14 → p19 → p20 → p21) (r15 : p10 → p19 → p21 → p7) (r16 : p2 → p16 → p19 → p24) (r17 : p19 → p20 → p12) : p1 := by
  have h21 : p21 := r14 f14 f19 f20
  have h18 : p18 := r2 f14 h21
  have h10 : p10 := r0 f16
  have h7 : p7 := r15 h10 f19 h21
  have h1 : p1 := r6 h7 h18
  exact h1
#print axioms cogModel_953f8133c47a6c88ab0edbf064a152843d0cdfa212b34c92939fdc5743db1e2a

theorem cogModel_705c8d1fc5a7ed9139c8aa69252797ed963a3d6cbda8bce081d69e2e6902c82c (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 p31 p32 p33 p34 : Prop) (f5 : p5) (f10 : p10) (f24 : p24) (f26 : p26) (r0 : p6 → p15 → p23 → p18) (r1 : p1 → p15 → p26 → p9) (r2 : p5 → p20) (r3 : p26 → p27 → p3) (r4 : p22 → p32 → p33 → p4) (r5 : p5 → p20 → p30) (r6 : p10 → p25 → p29) (r7 : p1 → p23) (r8 : p28 → p13) (r9 : p8 → p2) (r10 : p12 → p17 → p22) (r11 : p5 → p30 → p16) (r12 : p15 → p24 → p6) (r13 : p5 → p24 → p31 → p17) (r14 : p10 → p20 → p24 → p31) (r15 : p16 → p17 → p32) (r16 : p14 → p24 → p21) (r17 : p24 → p34 → p33) (r18 : p0 → p24 → p19) (r19 : p15 → p26 → p1) (r20 : p24 → p8) (r21 : p5 → p26 → p15) (r22 : p7 → p10 → p11) (r23 : p1 → p6 → p25) (r24 : p24 → p31 → p34) (r25 : p5 → p26 → p12) (r26 : p6 → p26 → p28) : p4 := by
  have h12 : p12 := r25 f5 f26
  have h20 : p20 := r2 f5
  have h31 : p31 := r14 f10 h20 f24
  have h17 : p17 := r13 f5 f24 h31
  have h22 : p22 := r10 h12 h17
  have h34 : p34 := r24 f24 h31
  have h33 : p33 := r17 f24 h34
  have h30 : p30 := r5 f5 h20
  have h16 : p16 := r11 f5 h30
  have h32 : p32 := r15 h16 h17
  have h4 : p4 := r4 h22 h32 h33
  exact h4
#print axioms cogModel_705c8d1fc5a7ed9139c8aa69252797ed963a3d6cbda8bce081d69e2e6902c82c

theorem cogModel_0439db84a0628590263b157f82f578c8b6f1af5956e901b01533afa4d782d463 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 : Prop) (f5 : p5) (f7 : p7) (f8 : p8) (f14 : p14) (f20 : p20) (r0 : p2 → p4) (r1 : p7 → p21 → p2) (r2 : p5 → p7 → p17) (r3 : p5 → p7 → p20 → p19) (r4 : p19 → p18) (r5 : p17 → p20 → p12) (r6 : p18 → p6) (r7 : p7 → p14 → p20 → p15) (r8 : p5 → p11 → p0) (r9 : p16 → p17 → p9) (r10 : p5 → p22 → p13) (r11 : p14 → p3) (r12 : p18 → p19 → p21) (r13 : p5 → p16) (r14 : p9 → p12 → p10) (r15 : p6 → p7 → p1) : p10 := by
  have h17 : p17 := r2 f5 f7
  have h12 : p12 := r5 h17 f20
  have h16 : p16 := r13 f5
  have h9 : p9 := r9 h16 h17
  have h10 : p10 := r14 h9 h12
  exact h10
#print axioms cogModel_0439db84a0628590263b157f82f578c8b6f1af5956e901b01533afa4d782d463

theorem cogModel_1a08682ede83204dd4c4cc93d32682428da76f198b16bf4fef6ea5630ebd1dc3 (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 : Prop) (f1 : p1) (f3 : p3) (f6 : p6) (f17 : p17) (r0 : p17 → p8) (r1 : p3 → p16 → p12) (r2 : p8 → p15) (r3 : p5 → p9) (r4 : p1 → p6 → p2) (r5 : p3 → p13 → p14) (r6 : p11 → p17 → p7) (r7 : p6 → p0) (r8 : p15 → p10) (r9 : p6 → p17 → p4) (r10 : p3 → p17 → p16) (r11 : p12 → p17 → p5) : p10 := by
  have h8 : p8 := r0 f17
  have h15 : p15 := r2 h8
  have h10 : p10 := r8 h15
  exact h10
#print axioms cogModel_1a08682ede83204dd4c4cc93d32682428da76f198b16bf4fef6ea5630ebd1dc3

theorem cogModel_0d797d5e3ff179c4573d175e36fd14baf166b0881df65c99ade05907dd210fdc (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 : Prop) (f3 : p3) (f6 : p6) (f14 : p14) (f18 : p18) (f20 : p20) (r0 : p3 → p14 → p17 → p4) (r1 : p1 → p8 → p13 → p7) (r2 : p3 → p6 → p23) (r3 : p6 → p15 → p24) (r4 : p18 → p20 → p16) (r5 : p17 → p2) (r6 : p0 → p2 → p4 → p10) (r7 : p14 → p17 → p0) (r8 : p18 → p22 → p11) (r9 : p6 → p14 → p17 → p0) (r10 : p3 → p8 → p13 → p12) (r11 : p3 → p18 → p20 → p23) (r12 : p3 → p21) (r13 : p6 → p18 → p17) (r14 : p20 → p23 → p2) (r15 : p6 → p20 → p17) (r16 : p1 → p16 → p20 → p19) (r17 : p6 → p18 → p8) (r18 : p6 → p21 → p13) (r19 : p3 → p18 → p1) (r20 : p6 → p23 → p4) (r21 : p3 → p9 → p5) : p10 := by
  have h23 : p23 := r2 f3 f6
  have h2 : p2 := r14 f20 h23
  have h4 : p4 := r20 f6 h23
  have h17 : p17 := r13 f6 f18
  have h0 : p0 := r7 f14 h17
  have h10 : p10 := r6 h0 h2 h4
  exact h10
#print axioms cogModel_0d797d5e3ff179c4573d175e36fd14baf166b0881df65c99ade05907dd210fdc

theorem cogModel_368dbb1516e6db872d8bb51d8fb7f5668380abc2ef2d0cbda2749feae87c235b (p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 p19 p20 p21 p22 p23 p24 p25 p26 p27 p28 p29 p30 : Prop) (f7 : p7) (f10 : p10) (f15 : p15) (f19 : p19) (f20 : p20) (r0 : p10 → p20 → p27 → p17) (r1 : p15 → p19 → p3) (r2 : p5 → p19 → p28) (r3 : p7 → p10 → p11 → p6) (r4 : p15 → p20 → p27 → p30) (r5 : p8 → p20 → p5) (r6 : p10 → p15 → p24 → p11) (r7 : p15 → p19 → p20 → p12) (r8 : p2 → p28 → p29 → p4) (r9 : p16 → p19 → p21) (r10 : p19 → p22 → p14) (r11 : p7 → p15 → p26 → p27) (r12 : p15 → p20 → p24) (r13 : p11 → p19 → p25) (r14 : p25 → p29) (r15 : p20 → p13) (r16 : p19 → p20 → p0) (r17 : p6 → p8 → p25 → p2) (r18 : p0 → p24 → p8) (r19 : p7 → p18 → p9) (r20 : p15 → p23 → p1) (r21 : p10 → p15 → p20 → p26) : p4 := by
  have h0 : p0 := r16 f19 f20
  have h24 : p24 := r12 f15 f20
  have h8 : p8 := r18 h0 h24
  have h5 : p5 := r5 h8 f20
  have h28 : p28 := r2 h5 f19
  have h11 : p11 := r6 f10 f15 h24
  have h25 : p25 := r13 h11 f19
  have h29 : p29 := r14 h25
  have h6 : p6 := r3 f7 f10 h11
  have h2 : p2 := r17 h6 h8 h25
  have h4 : p4 := r8 h2 h28 h29
  exact h4
#print axioms cogModel_368dbb1516e6db872d8bb51d8fb7f5668380abc2ef2d0cbda2749feae87c235b
