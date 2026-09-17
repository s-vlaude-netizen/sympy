# Working in this repository

This is an independent fork of SymPy carrying AI-generated bug fixes; see
[FORK.md](FORK.md). Upstream declines these patches under its AI-generated code
policy, so they live here instead. Two consequences shape all work here:

- **Do not open pull requests against `sympy/sympy`** and do not post to their
  issues, pull requests, or discussions. Reading their public issue tracker to
  find bugs worth fixing is fine and encouraged; writing to it is not.
- **Upstream is the reference implementation.** When a change here disagrees
  with upstream behaviour, the burden is on the change. Say so in the commit
  message and explain why upstream is wrong.

## Standing workflow

Do these without being asked, every session:

0. **Commit and push to `master` directly.** There is no feature-branch and
   pull-request step here; the owner asked for the merge button to go away.
   What replaces that review gate is the checklist under *Standards for a fix*
   below, so treat it as binding rather than aspirational: on `master` a bad
   push is the published state of the fork, with nothing in front of it.

   Push a fix only once its suites are green. If work has to be left
   half-finished, leave it uncommitted or stash it — never push a broken
   `master` intending to follow up.

1. **Merge upstream before starting new work.**

   ```
   git remote add upstream https://github.com/sympy/sympy.git   # once
   git fetch upstream master
   git merge upstream/master
   ```

   Resolve conflicts in favour of upstream's wording where the two are
   equivalent — a conflict resolved upstream's way will not conflict again next
   time. After merging, re-run the suites covering every file the fork touches
   (`git diff --name-only upstream/master HEAD`), because upstream drift can
   invalidate a fork fix silently.

   Merge at the start of a session and before pushing a batch, not after every
   commit: a merge per commit buys nothing and fills the history with noise.

2. **Regenerate the divergence list after any change to the fork's diff.**

   ```
   python tools/fork_divergence.py > DIVERGENCE.md
   ```

   Commit it with the change that moved it. It is generated — never hand-edit.

3. **Add an entry to [CHANGELOG-FORK.md](CHANGELOG-FORK.md) for every fix**,
   naming the behaviour before and after. `DIVERGENCE.md` is the mechanical
   view; the changelog is the readable one, and it is what tells someone
   whether the fork is worth using.

   Entries go under `## Unreleased`, grouped by subpackage, alphabetically.
   "Unreleased" means no version has been tagged, not that the change is
   unmerged — landing on `master` releases nothing. Entries move under a
   version heading only when a tag is cut, and `## Unreleased` then stays,
   empty, above it. Mark an entry that changes the shape of an existing
   result, as opposed to correcting a wrong one, **Behaviour change**.

4. **Watch for fixes upstream has adopted.** `DIVERGENCE.md` ends with a list
   of fork commits whose lines upstream now has independently. Verify each and
   drop the patch: a smaller fork is a better fork, and a fix upstream reaches
   on its own is a fix that was real.

## Cutting a release

Tags are the fork's only release mechanism; it publishes no packages. To cut
one, on `master` with a clean tree and upstream merged:

1. Set the date in `sympy/release.py`, keeping the shape
   `<upstream base>+fork.<Y>.<M>.<D>`. Write the date the way PEP 440
   normalises it, without leading zeros — `2026.9.17`, not `2026.09.17` — so
   that the string in the file, the installed version and the tag all match.
2. Rename `## Unreleased` in `CHANGELOG-FORK.md` to `## fork-<Y>.<M>.<D>`,
   note the upstream base under it, and open a fresh empty `## Unreleased`
   above.
3. Update the pinned tag in the README's install commands.
4. Commit, then `git tag -a fork-<Y>.<M>.<D>` with a message listing what is in
   it, and `git push origin master --follow-tags`.

Never move or delete a pushed tag: anyone who pinned it gets different code
under the same name. Cut a new one instead.

## Standards for a fix

Every fix needs all of these. They are the only thing standing in for the
upstream review these patches will not get.

- **A regression test verified to fail before the change.** Use
  `git stash push <source files>`, run the new test, confirm it fails, then
  `git stash pop`. A test that passes both ways is not a regression test.
- **The affected subpackages' full suites, run and green.** Not just the new
  test. `python -W ignore -m pytest sympy/<pkg> -q`; slow tests are deselected
  by `pyproject.toml`, so add `-m "slow or not slow"` when they are relevant.
- **`python -m ruff check` on every file touched.**
- **A commit message giving the wrong behaviour and the right one**, with a
  concrete input and both outputs. If a claim is numeric, it was checked
  against `mpmath` at high precision or against an unmodified upstream
  checkout, not reasoned about.

Be wary of the recurring false positives in this codebase: floating-point
sample points that cause legitimate cancellation (use exact `Rational`);
`exp_polar` and `polar_lift` rewrites, which hold only on the principal branch;
and functions whose `series()` already compensates for a branch, where adding a
second correction doubles it.

## Bug-hunting techniques that have worked here

Both of these produced fixes in this fork and are worth rerunning:

- **AST scans for bug smells.** `ask()` calls that drop `assumptions`; mutable
  default arguments that are mutated; duplicate dict keys or set elements;
  `_eval_nseries` with no check on the expansion point; `_eval_evalf` routed
  through a rewrite; duplicated if/elif branches; self-comparisons.
- **Numeric verification of symbolic machinery.** Compare
  `as_leading_term`/`series`/`rewrite`/`evalf` against high-precision
  evaluation of the function itself, at exact `Rational` points, in both
  directions (`cdir=±1`).

Areas already swept without findings, so lower yield: simplification
round-trips, `solve`/`solveset` residuals, `integrate`→`diff` round-trips,
definite integrals against quadrature, `Sum`/`Product` closed forms, set
algebra, printing round-trips, hash-seed determinism, matrix identities, number
theory against brute force, polynomial real-root cross-checks.
