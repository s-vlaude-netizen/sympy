"""Check every "now gives" claim in CHANGELOG-FORK.md against the live code.

Run after merging upstream, alongside the test suites. A fork fix can be
silently invalidated by upstream drift, and this catches the case where the
changelog still promises behaviour the code no longer has. It also catches a
claim that was written down wrongly in the first place, which is how the
Q.extended_nonnegative entry was found to be missing its real-symbol caveat.

    python tools/check_changelog_claims.py

Exits non-zero if any claim fails.
"""
from __future__ import annotations

import mpmath

from sympy import (EulerGamma, I, Identity, Interval, LambertW, MatrixSymbol,
                   N, Q, Rational, S, Symbol, ask, bessely, Ei, elliptic_e,
                   elliptic_k, erfi, exp, expand_func, frac, hn1, jn, latex,
                   li, limit, log, loggamma, pi, refine, sign, simplify,
                   oo, sin, sqrt, symbols, sympify, yn)
from sympy.physics.control import Feedback, Series, StateSpace, TransferFunction
from sympy.stats import E, Kumaraswamy

x, y = symbols('x y', real=True)  # the LRA solver only accepts real symbols
z, s, k = symbols('z s k')

ok, bad = 0, []
def check(label, got, want):
    global ok
    if got == want or (hasattr(got, 'equals') and got.equals(want)):
        ok += 1
    else:
        bad.append(f'{label}: got {got!r}, want {want!r}')

X = MatrixSymbol('X', 3, 3)
nn = Symbol('n')

check('refine sign', refine(sign(x), Q.positive(x)), S.One)
check('LRA ge', ask(Q.ge(x + y, 0),
      Q.extended_nonnegative(x) & Q.extended_nonnegative(y)), True)
check('LRA le mirror', ask(Q.le(x + y, 0),
      Q.extended_nonpositive(x) & Q.extended_nonpositive(y)), True)
check('unitary adjoint ask', ask(Q.unitary(X.adjoint()), Q.unitary(X)), True)
check('refine X*X.H', refine(X*X.adjoint(), Q.unitary(X)), Identity(3))
check('refine X.H*X', refine(X.adjoint()*X, Q.unitary(X)), Identity(3))
check('exp refine even', refine(exp(pi*I*nn), Q.even(nn)), S.One)
check('Ei limit', limit(Ei(-exp(-x)) + x, x, oo), EulerGamma)
check('frac lead', frac(-x).as_leading_term(x), S.One)
check('frac nseries', frac(-x).nseries(x, n=2), 1 - x)
check('Ei two-sided +', limit(Ei(x**2) - log(x**2), x, 0, '+'), EulerGamma)
check('Ei two-sided -', limit(Ei(x**2) - log(x**2), x, 0, '-'), EulerGamma)
check('elliptic_e limit', limit(elliptic_e(1 - x), x, 0, '+'), S.One)
check('elliptic_k still zoo', limit(elliptic_k(1 - x), x, 0, '+'), S.ComplexInfinity)
check('Kumaraswamy support', Kumaraswamy('K', 2, 3).pspace.distribution.set,
      Interval(0, 1))
check('Kumaraswamy mean', simplify(E(Kumaraswamy('K', 2, 3))), Rational(16, 35))
check('pure gain states',
      TransferFunction(k, 1, s).rewrite(StateSpace).num_states, 0)

# numeric ones, against the function's own value
def near(label, a, b, tol=Rational(1, 10**12)):
    global ok
    if abs(N(a - b, 30)) < tol: ok += 1
    else: bad.append(f'{label}: |{a} - {b}| too large')

near('erfi expint', erfi(z).rewrite('expint').subs(z, 1).evalf(25), erfi(1).evalf(25))
near('jn parity', jn(0, -Rational(3, 7)).evalf(25),
     expand_func(jn(0, z)).subs(z, -Rational(3, 7)).evalf(25))
near('hn1 = jn + I*yn', hn1(1, Rational(5, 3)).evalf(25),
     (jn(1, Rational(5, 3)) + I*yn(1, Rational(5, 3))).evalf(25))
near('bessely -1/2 -> 0', bessely(Rational(-1, 2), Rational(1, 10**6)).evalf(25),
     (sqrt(2/(pi*Rational(1, 10**6)))*sin(Rational(1, 10**6))).evalf(25))
near('LambertW(1+x) at 0', LambertW(1 + x).series(x, 0, 3).removeO().subs(x, 0),
     LambertW(1).evalf(25), Rational(1, 10**6))
near('li near 0', li(Rational(1, 10**16)).evalf(25), Rational(-264, 10**20),
     Rational(1, 10**18))

# loggamma branch, against mpmath
mpmath.mp.dps = 25
ser = loggamma(-x).series(x, 0, 3).removeO().subs(x, Rational(1, 1000))
near('loggamma below 0', ser, sympify(str(mpmath.loggamma(-0.001))), Rational(1, 10**6))

# LaTeX Feedback: no tuple in the denominator
tf1 = TransferFunction(1, s - 1, s); tf2 = TransferFunction(s + 1, s + 2, s)
tf3 = TransferFunction(s, s + 3, s)
L = latex(Feedback(Series(tf1, tf2), tf3))
check('latex Feedback no tuple', (',' in L.split('}{')[-1]), False)

print(f'{ok} claims verified, {len(bad)} failed')
for b in bad: print('  FAIL', b)

import sys
sys.exit(1 if bad else 0)
