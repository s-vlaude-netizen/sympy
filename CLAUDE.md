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

4. **Run the changelog checker after merging upstream.**

   ```
   python tools/check_changelog_claims.py
   ```

   It asserts every "now gives" claim in `CHANGELOG-FORK.md` against the live
   code, so upstream drift cannot quietly leave the changelog promising
   behaviour the fork no longer has. Add a claim to it with each new entry.

5. **Watch for fixes upstream has adopted.** `DIVERGENCE.md` ends with a list
   of fork commits whose lines upstream now has independently. Verify each and
   drop the patch: a smaller fork is a better fork, and a fix upstream reaches
   on its own is a fix that was real.

## Releases and tags

**Do not ask the owner to cut, push, or publish a tag.** Tag pushes are blocked
from the sandboxed session, so every tag becomes manual work for them, and they
have asked for that not to land on their desk. `fork-2026.9.17` exists as the
one worked example; treat it as the exception, not the first of a series.

The fork therefore releases by `master`, not by tag. `@master` is how anyone
gets the current code, the changelog's `## Unreleased` section is the running
record, and `sympy/release.py` stays at plain `1.15.0.dev+fork` with no date —
a date set outside a release would go on claiming that release while master
moved on. None of that needs a tag to work.

Propose a tag only if the owner would plainly want one, for instance before a
change that breaks compatibility so the previous state stays reachable, or
because they asked. Then hand over the whole thing at once — the commands and
an annotated message — rather than a series of steps, and say why this state is
worth naming. If they decline, that is the end of it; nothing in the fork
depends on tags existing.

When a tag is genuinely wanted, on `master` with a clean tree and upstream
merged: date the version in `sympy/release.py` as
`<upstream base>+fork.<Y>.<M>.<D>`, written the way PEP 440 normalises it and
so without leading zeros (`2026.9.17`, not `2026.09.17`), so the file, the
installed version and the tag all read the same; rename `## Unreleased` in
`CHANGELOG-FORK.md` to `## fork-<Y>.<M>.<D>`, note the upstream base under it
and open a fresh empty `## Unreleased` above; update the pinned tag in the
README; then commit, and hand the owner `git tag -a fork-<Y>.<M>.<D>` plus
`git push origin master --follow-tags`. Set the version back to plain `+fork`
in the next commit after the tagged one.

When upstream bumps its own version, say `1.15.0.dev` to `1.16.0.dev`, that
line in `sympy/release.py` conflicts with the fork's `+fork` suffix. Resolve it
by taking upstream's new base and keeping the suffix: `1.16.0.dev+fork`. No tag
is involved, and the string stays true on its own.

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
