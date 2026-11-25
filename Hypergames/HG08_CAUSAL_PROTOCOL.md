# HG-08: finite-field causal differences, sparse support certificates and intervention query bounds

Prospective companion to GPTStoryworld HG-08 preregistration. Work with binary state x∈F2^d, goal matrix P∈F2^{k×d}, and an intervention mask s. Define Δ_s(x)=P(x+s)+Px=Ps in F2^k. The derivative is independent of x. An odd residual parity on a bucket B after subtracting already verified support has at least one remaining causal variable, so recursive bisection using group queries can identify a true positive. A singleton positive certificate is exact. Under the registered assumption that each target row has weight exactly six, six distinct verified positives form its complete support.

For k=1 and uniform six-sparse prior, the identity of the support contains log2 binom(d,6) bits. Each adaptive yes/no query transmits at most one bit, so exact worst-case identification requires at least ceil(log2 binom(d,6)) group queries. For k independent unconstrained rows, the response is k bits and the overall bound is unchanged. This is a lower bound, not an attainable claim or a comparison with singleton-only actions.

An incompletely observed parity row r remains unpredictable on fresh uniform x whenever r lies outside the observation rowspace. Its ideal accuracy is 1/2. A guessed parity from a known strict subset of true support also has 1/2 accuracy under independent fresh uniform inputs, yielding expected forced-release utility 25/2−15=−5/2. For k outputs, replace the missing-bit rank by h and success by 2^-h. These identities measure the safety cost of unsupported releases.

Independent finite case enumeration, sparse-group peeling invariants, source hashes and exact-rational CI will accompany the experiment. No Lean theorem is claimed until kernel checked.
