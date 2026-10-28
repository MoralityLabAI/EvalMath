# EvalMath research note 01: Intervention-preserving compactification

Status: mathematical derivations and a tested finite-dimensional reference harness.
No real-model experiments and no Lean compilation have been performed.

Repository import status (2026-10-28): the proofs below are handwritten derivations. The accompanying v0.1 Python code uses floating-point arithmetic and gives synthetic sanity checks; its numeric values are not rigorous rounded certificates. See [README.md](README.md) for evidence limits, quotient/closure qualifications, ownership, and replay. Section 8 is a prospective experiment proposal.

## Sources and scope

Primary source: Petersen and Zech, *Mathematical theory of deep learning*, arXiv:2407.18384. The named theorem and proposition numbers below were checked against **v1 (July 2024)**, available at https://arxiv.org/pdf/2407.18384v1 . A later arXiv v4 was posted January 15, 2026; its theorem numbering is not verified here.

* Theorem 8.1: a Barron-class scalar function has a two-layer sigmoid-network approximation with normalized squared L2 error <= c/N for c>4C^2, assuming the stated Fourier-moment condition. This is an L2 existence result, not a uniform or interventional bound.
* Proposition 8.5: compositional low-arity smooth functions admit a uniform ReLU approximation rate of N^(-(q+s)/r), with O(N log N) size, O(log N) depth, and constants depending on the composition graph. Here r is maximal component arity and q+s is component smoothness.
* Proposition 8.7: smooth functions restricted to a smooth compact intrinsic-m-dimensional manifold admit a uniform ReLU approximation rate C ||f||_(C^(q,s)) N^(-(q+s)/m), with O(N log N) size and O(log N) depth. Constants still depend on regularity and manifold geometry.
* Theorems 14.11, 14.14, 14.15: covering-number generalization and weight-bounded network-function covers.
* Theorem 15.2: an alternative Lipschitz-class bound, potentially independent of parameter count when the required Lipschitz assumptions hold.

Related: Geiger et al., *Causal Abstraction: A Theoretical Foundation for Mechanistic Interpretability* (JMLR, 2025), https://www.jmlr.org/papers/v26/23-0058.html . Sutter et al., *The Non-Linear Representation Dilemma* (NeurIPS, 2025), https://papers.nips.cc/paper_files/paper/2025/hash/dbb98528c9870377f3f0d133aae6050b-Abstract-Conference.html . Arbitrary alignment maps can trivialize causal abstraction; restrict representation and transition complexity.

## 1. Formal setup

Fix a normed hidden-state space H (for experiments, a chosen transformer boundary), an **intervention-closed** test domain K subset H, and an operation alphabet A. Every a in A is a deterministic map F_a: K -> K. Define the result of an operation word w=a_1...a_T by F_w = F_(a_T) o ... o F_(a_1). Readouts are g:K -> Y. A proposed representation uses pi:K -> Z and abstract operations G_a:Z -> Z and readout q:Z -> Y.

Measured errors:

  rho_a(h) = ||pi(F_a(h)) - G_a(pi(h))||
  rho_g(h) = ||g(h) - q(pi(h))||.

A complete claim must name K, A, Y, T, the norm, the encoding map, and the required tolerance. If the original model contains non-deterministic sampling, include random choices in the state/action semantics or analyze a coupled random system separately.

## 2. Fiber obstruction and approximate factorization

Define

  Omega_a(pi) = sup{||pi(F_a(h))-pi(F_a(h'))|| : h,h' in K, pi(h)=pi(h')}
  Omega_g(pi) = sup{||g(h)-g(h')|| : h,h' in K, pi(h)=pi(h')}.

LEMMA A (necessary condition): If sup_h rho_a(h) <= eps, then Omega_a(pi) <= 2 eps. If sup_h rho_g(h) <= eta, then Omega_g(pi) <= 2 eta.

Proof: For each pair on the same pi-fiber, insert the common G_a(pi(h)) or q(pi(h)) and apply the triangle inequality.

LEMMA B (constructive sufficiency at one step): Given a selection s:pi(K)->K with pi(s(z))=z, setting G_a(z)=pi(F_a(s(z))) and q(z)=g(s(z)) achieves errors at most Omega_a(pi) and Omega_g(pi), respectively. This construction need not be continuous, Lipschitz, computable, or simple.

COROLLARY (near-fiber lower bound): For a candidate abstract G_a that is L-Lipschitz, any pair h,h' satisfies

  2 eps >= ||pi(F_a(h))-pi(F_a(h'))|| - L ||pi(h)-pi(h')||.

Hence the empirical maximum of the positive part of the RHS divided by two is a **lower bound on the best possible uniform commutation error** for any L-Lipschitz abstract map. It is useful as a falsifier even when exact matching fibers are rare.

CAUTION: The scale and metric on Z must be fixed. Normalizing/whitening the encoding and separately checking readout error prevent trivial collapse of distances. L, encoder description length, and the intervention domain should be documented.

## 3. Exact quotient theorem (all operation words)

Let h ~ h' iff g(F_w(h))=g(F_w(h')) for every finite word w in A*, including the empty word. Then ~ is an equivalence relation and a right congruence: h~h' entails F_a(h) ~ F_a(h') for all a. Proof: prefix any word w by a. Thus each operation induces a well-defined map on Q=K/~, and g induces a readout on Q. Q merges exactly the states observationally indistinguishable under all the specified experiments. When A and observables are rich, the quotient may retain as much complexity as K. A finite horizon T yields a weaker, horizon-dependent notion.

For EvalLang, a proposition P:K->{false,true} descends to Q only if it is constant on ~-classes. Its truth can then be expressed on the quotient state.

## 4. Uniform finite-horizon simulation theorem

Assume for every a,h: rho_a(h)<=eps; all G_a are L-Lipschitz on a region containing the trajectories; rho_g(h)<=eta; and q is D-Lipschitz. Start z_0=pi(h_0). For an **identical externally supplied action sequence** on the original and abstract systems,

  ||g(h_T)-q(z_T)|| <= eta + D * eps * sum_{j=0}^{T-1} L^j.

Proof: If e_t=||pi(h_t)-z_t||, then e_0=0 and

  e_(t+1) <= ||pi(F_a(h_t))-G_a(pi(h_t))|| + ||G_a(pi(h_t))-G_a(z_t)||
          <= eps + L e_t.

Induction gives e_T <= eps sum_j L^j. The final result follows from readout error eta and the D-Lipschitz property of q.

Extensions: per-step eps_a and L_a give e_T <= sum_(j=0)^(T-1) eps_(a_j) prod_(i=j+1)^(T-1) L_(a_i). If L<1, the sum is bounded by 1/(1-L); if L=1, it is T. If logits have max-coordinate error <=Delta, a top-two margin >2Delta preserves argmax. In closed-loop control, establish this margin condition at each decision before concluding that action sequences agree.

## 5. Approximation rates transferred from Petersen–Zech

Suppose an exact quotient exists and its scalar coordinate transition/readout functions, defined on a compact intrinsic-m-dimensional manifold, belong to the appropriate C^(q,s) class. Proposition 8.7 supplies component approximants with uniform error alpha_N <= C N^(-(q+s)/m). A finite set of actions and output coordinates gives an implementation whose total size is O(number_of_components*N*log(N)), with constants and regularity conditions inherited from the proposition. If component functions have bounded input arity r, Proposition 8.5 can replace m by r under its compositional assumptions, with graph-dependent constants.

Approximant images must remain in a domain where the required error and Lipschitz bounds hold. A compact box with a smooth extension, or a suitable retraction/projection with proven bounds, is one way to specify this. Universal approximation by itself supplies no quotient pi and no operational guarantee. Theorem 8.1 has average squared error and therefore requires an additional distribution-to-uniform argument for deterministic worst-case simulation.

## 6. A covering-number generalization certificate

Let X be the space of sampled state-action cases and C be a **fixed, predeclared** class of measurable losses ell_theta:X->[0,1], such as a clipped normalized commutation residual. Write N_inf(alpha,C) for the sup-norm alpha-cover size. If X_1,...,X_n are i.i.d. from a distribution D, then with probability at least 1-delta, simultaneously for all theta in C,

  |E_D ell_theta - (1/n)sum_i ell_theta(X_i)|
    <= 2 alpha + sqrt(log(2 N_inf(alpha,C)/delta)/(2n)).

Proof: Apply Hoeffding and a union bound to the finite alpha-net. Moving from any hypothesis to its net representative costs alpha in expected loss and alpha in empirical loss. This follows the covering-number strategy of Petersen–Zech Theorem 14.11; the explicit normalized-loss bound here is our adaptation.

For a parametric family with effective p bounded parameters and a suitably Lipschitz parameter-to-loss realization map, log N_inf(alpha,C) can scale as O(p log(C/alpha)). Then the statistical term scales roughly as sqrt((p log n + log(1/delta))/n). Here p **includes learned encoder complexity** if pi is trained/selected on the evaluation sample. With a frozen independently fitted encoder and independently held-out data, one may evaluate a single fixed hypothesis using the simpler pointwise Hoeffding bound.

An average distributional bound covers D, not every legal intervention. For a robust sup certificate, assume K has an r-net {h_i} and each rho_a is K_rho-Lipschitz. Then

  sup_(a,h in K) rho_a(h) <= max_(a,i) rho_a(h_i) + K_rho*r.

A compact intrinsic-m-dimensional manifold under appropriate geometric regularity can have covering costs scaling with m rather than ambient d. Interventions can move states off the original observational manifold, so build the net over the intervention-closed K, rather than baseline activations alone.

## 7. Explicit counterexample

H=R^2, pi(x,y)=x, g(x,y)=x. Baseline observational states lie on y=x. Let I(x,y)=(x,-y) and F(x,y)=(y,y). On baseline states, pi(F(x,x))=x and q(pi(x,x))=g(x,x)=x. The intervention I is invisible to pi at the moment it occurs. Yet

  pi(F(1,1))=1, pi(F(I(1,1)))=-1.

The pair (1,1),(1,-1) has identical compressed representation and a successor separation of 2. Every abstract one-step transition for F incurs worst-case commutation error at least 1 on that pair. A representation trained only on the baseline diagonal misses this distinction.

## 8. Proposed experiment (Qwen SAE/VPD/percolation, read-only plan)

1. Freeze the checkpoint, tokenizer, layer boundary, model hooks, readout definition, code hashes, seeds, and the admissible action grammar. Cache original activations before fitting compressors. Record whether the interventions are realistic or synthetic.
2. Split prompt families and intervention templates before tuning. Construct an intervention-closed evaluation pool by caching reachable post-patch, post-ablation, and post-steering states. Hold out prompt families and at least one intervention family.
3. Candidate pi: PCA, dimension-matched random projection, SAE features (with explicit feature selection and scaling), VPD coordinates, and percolation-selected components. Compare at matched k, matched alive-component quota, matched readout/transition expressiveness, and measured runtime. Include degree, weighted-degree, causal-importance, attribution-mass, firing-rate, and frequency-matched random selectors when assessing percolation's incremental value.
4. Fit simple abstract G_a and readout q on training partitions only. Start with affine maps, then a fixed-budget small nonlinear model. Report encoder+transition+readout parameter count and spectral/Lipschitz estimates.
5. Evaluate held-out one-step commutation residuals, readout error, empirical near-fiber lower bounds, operation-sequence errors for T=1,2,4,8, and decision agreement conditional on observed logit margin. Bootstrap or otherwise account for prompt-family correlation; do not pretend token-level repeats are independent.
6. Publish coverage statistics for each intervention-closed K; report r-net claims only when a valid geometric certificate is available. Ordinary held-out sampling supports distributional estimates.
7. Run explicit falsifiers: hidden-y style dormant-feature interventions, composition-order changes, adversarial near-collision searches, shuffled-feature controls, learned alignment on a randomly initialized model, and a compressor with deliberately excessive capacity.

Recommended gates:
* Exact claim fails upon any reproducible pair of equal encoded states with distinct observable futures.
* Uniform eps claim fails when a measured residual or near-fiber lower bound exceeds eps on the specified K.
* Finite-horizon guarantee passes only when numerical assumptions are certified and measured errors respect the derived bound; distributional performance should be reported independently.
* Percolation-specific benefit requires improvement over matched selection and modeling baselines on untouched tasks and intervention families.
* If an ordinary experiment has insufficient geometric coverage, the result is distributional rather than a uniform mechanistic certificate.

## 9. Lean handoff

The clean first formal targets are (1) the fiber obstruction from `norm_sub_le`, (2) a normed-group recursion e_(t+1)<=eps+L*e_t, (3) state-word equivalence and the induced quotient transition, (4) the finite-net Hoeffding union-bound separately in probabilistic infrastructure. Prove the deterministic results before introducing any transformer implementation. A Lean build was not available in this runtime, so Lean proof compilation is not claimed.
