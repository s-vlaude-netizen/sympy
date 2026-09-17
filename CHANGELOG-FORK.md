# Changelog for this fork

Changes in this fork relative to upstream SymPy, grouped by subpackage. Every
entry names the behaviour before the change as well as after, so you can tell
whether it affects you.

All of these are bug fixes. One changes the shape of an existing result and is
marked **Behaviour change** below; nothing else adds, removes, or renames an
API. See [`FORK.md`](FORK.md) for how they were produced and reviewed, and
[`DIVERGENCE.md`](DIVERGENCE.md) for the corresponding diff against upstream.

## Unreleased

What is on `master` now. Since this fork releases by `master` rather than by
tag, this is the section to read: it is the running record, not a staging area,
and entries stay here unless a tag is cut.

## fork-2026.9.17

Tracking upstream `1.15.0.dev`; installs as version
`1.15.0.dev+fork.2026.9.17`. First tagged release of the fork, so this covers
every change made since forking.

* assumptions
  * `refine_sign` now forwards its assumptions to `ask`, so a refinement whose
    realness follows from the assumptions rather than from the symbol is picked
    up. Formerly `refine(sign(x), Q.positive(x))` gave `sign(x)` unchanged,
    although `Q.positive(x)` implies `Q.real(x)`; it now gives `1`.
  * The LRA satisfiability solver now handles `Q.extended_nonnegative`, which
    was missing from its predicate white list and from the table translating an
    `extended_*` predicate to its plain counterpart. Formerly, for real `x` and
    `y`,
    `ask(Q.ge(x + y, 0), Q.extended_nonnegative(x) & Q.extended_nonnegative(y))`
    gave `None` while the mirrored question about `Q.extended_nonpositive` gave
    `True`. Both give `True` now. (The LRA solver only accepts real symbols, so
    with a bare `Symbol('x')` both questions still give `None`.)
  * `Q.unitary` and `Q.orthogonal` now have a handler for `Adjoint`, so
    `ask(Q.unitary(X.adjoint()), Q.unitary(X))` gives `True` instead of `None`.

* core
  * `evalf` no longer lets an imaginary part that has cancelled down to
    rounding noise decide which side of a branch cut a result falls on, in
    either `evalf_pow` or `evalf_log`. The consequence was a wrong value, not
    an imprecise one: for the roots of `5*x**4 + 3*x + 2` the imaginary part of
    a root flipped sign between `evalf(30)` and `evalf(40)`, so two of the four
    roots collapsed onto the same value at some precisions and substituting a
    root back into the polynomial gave `4.64*I` instead of `0`. An imaginary
    part with no correct bits is now treated as the exact zero it cannot be
    distinguished from, giving the principal branch.

* functions
  * `exp._eval_refine` now forwards its assumptions to `ask`, so assumptions
    passed explicitly to `refine` are no longer ignored in favour of the
    symbol's own assumptions and the global context. Formerly, inside
    `assuming(Q.odd(n))`, `refine(exp(pi*I*n), Q.even(n))` gave `-1`, the
    global assumption silently winning over the explicit one; that
    contradictory input now raises `ValueError`, as the other `refine` paths
    already did, while `refine(exp(pi*I*n), Q.even(n))` on its own gives `1`.
  * Fixed the leading term of `Ei` at zero, which ignored an unspecified
    direction and so never applied its branch correction. Formerly
    `limit(Ei(-exp(-x)) + x, x, oo)` gave `EulerGamma + I*pi`, and the mean of
    a Gumbel distribution, `integrate(x*exp(-x - exp(-x)), (x, -oo, oo))`, came
    back complex; both now give `EulerGamma`.
  * Fixed the leading term and series of `frac` at an integer approached from
    below. Formerly `frac(-x).as_leading_term(x)` gave `-x` and
    `frac(-x).nseries(x, n=2)` gave `-x`; they now give `1` and `1 - x`.
  * Fixed the leading terms of `Ei`, `Ci` and `Chi` at zero, which built their
    logarithm by hand and so dropped the branch correction for a negative
    argument. Formerly the two one-sided limits of the even function
    `Ei(x**2) - log(x**2)` disagreed, giving `EulerGamma` from the right and
    `EulerGamma + 2*I*pi` from the left.
  * Fixed the leading term of `bessely` at a negative non-integer order, which
    used a form valid only for integer orders. Formerly
    `bessely(Rational(-1, 2), x).as_leading_term(x)` diverged at zero, although
    `bessely(-1/2, z)` is `sqrt(2/(pi*z))*sin(z)` and tends to zero there.
  * `bessely` and `besselk` now pass `cdir` on to the inner `as_leading_term`
    call, so the logarithm in those expansions is no longer always taken as if
    `x` were positive. Formerly `besselk(0, x**2).as_leading_term(x, cdir=-1)`
    was short of the `2*I*pi` that `log(x**2)` carries for negative `x`.
  * Fixed the series of `li` away from `z = 1`, which always summed the
    expansion of `Ei(log(z))` about zero. Formerly `li(z).series(z)` gave a
    divergent complex answer near `z = 0`, evaluating to `-96398 + 3.14*I` at
    `z = 1e-16` where `li(1e-16)` is `-2.64e-18`. The expansion around `z = 1`
    also picks up the `I*pi` that `Ei` sheds below zero.
  * Fixed the series of `LambertW` away from zero, which always summed the
    Taylor series of `W` about its branch point. Formerly
    `LambertW(1 + x).series(x, 0, 3)` gave `-x - x**2 + O(x**3)`, which tends to
    `0` rather than to the omega constant `LambertW(1) = 0.5671...`.
  * Fixed the series of `loggamma` at zero approached from below, which
    expanded through the rewrite to `log(gamma(z))`. That rewrite is an
    identity only where `gamma` is positive, so the series was `2*I*pi` away
    from `loggamma`'s own value: `loggamma(-x).series(x, 0, 3)` gave
    `+I*pi - log(x) + ...` while `loggamma(-0.001)` is
    `6.90833331751503 - 3.14159265358979*I`.
  * `elliptic_k` and `elliptic_e` no longer expand through a hypergeometric
    series at `m = 1`, where it does not converge. Formerly
    `elliptic_e(1 - x).series(x, 0, 2)` gave `nan` and
    `limit(elliptic_e(1 - x), x, 0, '+')` gave `zoo`, although `elliptic_e` is
    continuous there with `elliptic_e(1) = 1`. `elliptic_k`, which really does
    diverge, still gives `zoo`.
  * Fixed the sign of the standalone term in `erfi(z).rewrite('expint')`, which
    was `2*I*sign(z)` away from `erfi` at every real point. Formerly
    `erfi(z).rewrite('expint').subs(z, 1).evalf()` gave
    `1.65042575879754 + 2.0*I` instead of `1.65042575879754`. *Upstream has
    since made the same fix independently, so the fork no longer diverges
    here.*
  * `jn`, `yn`, `hn1` and `hn2` now evaluate numerically through their closed
    forms rather than through a Bessel function rewrite, which was negated on
    the negative real axis. Formerly `jn(0, -Rational(3, 7)).evalf()` gave
    `-0.969667661650455` although `sin(z)/z` is even, breaking the parity
    relation `j_nu(-z) == (-1)**nu*j_nu(z)` and leaving `hn1` differing from
    `jn + I*yn`.

* matrices
  * `refine` now cancels a unitary matrix against its adjoint. Formerly
    `refine(X*X.adjoint(), Q.unitary(X))` was left unchanged; it now gives `I`,
    as does `refine(X.adjoint()*X, Q.unitary(X))`. The test was written against
    the elementwise conjugate, for which the identity does not hold.

* physics.control
  * **Behaviour change.** A transfer function with a constant denominator is
    now realised with no states rather than one dead state, fixing
    [sympy/sympy#29179](https://github.com/sympy/sympy/issues/29179). Formerly
    the unreachable, unobservable state a pure gain contributed was carried
    into every series and parallel connection it took part in, so the sum of a
    gain and a fourth-order transfer function came out with a 5×5 rather than
    a 4×4 state matrix. `TransferFunction(k, 1, s).rewrite(StateSpace)` now has
    empty `A`, `B` and `C`, so code asserting the old one-state form needs
    updating.

* printing
  * Fixed the LaTeX of a `Feedback` whose numerator is a `Series` and whose
    feedback path is an ordinary `TransferFunction`. A stray comma made the
    second denominator term a tuple, so `latex(Feedback(Series(tf1, tf2), tf3))`
    typeset that denominator as `\left( \frac{1}{1}, \ ... \right)` instead of
    as a product. The pretty printer was already correct.

* solvers
  * `ode_2nd_power_series_ordinary` now returns as many terms as asked for,
    deriving the iteration count from the recurrence instead of using a
    constant. Formerly `f'' + f` came back as
    `C2*(x**4/24 - x**2/2 + 1) + C1*x*(1 - x**2/6) + O(x**6)`, missing the
    `x**5/120` of the sine, so substituting the series back into the equation
    left a residual of order `x**3` rather than `x**4`.
  * `ode_2nd_power_series_ordinary` also solves the equations pinning down the
    leading coefficients one at a time rather than summing them. They belong to
    different powers of `x`, so adding them together lost some: for
    `f'' + x**2*f`, where the recurrence steps by four, `a3` was left
    undetermined and escaped into the answer as a bare `r(3)`.
  * `_get_trial_set` no longer leaks trial terms between summands of an ODE's
    right-hand side, having collected them into a mutable default argument that
    persisted across calls. For `f'' - f = x*(x + 2) + exp(-x)` the leaked
    terms produced `{1, x, x**2, x**3, x*exp(-x)}`, with a spurious `x**3`,
    instead of `{1, x, x**2, x*exp(-x)}`.

* stats
  * The `Kumaraswamy` distribution now has support `Interval(0, 1)` rather than
    `Interval(0, oo)`, matching its own documented density. Formerly every
    quantity computed by integrating the density picked up a divergent tail, so
    `E(Kumaraswamy('K', 2, 3))` and `variance(Kumaraswamy('K', 2, 3))` both gave
    `oo`. The mean is now `16/35`, and `b*beta(1 + 1/a, b)` in general.
