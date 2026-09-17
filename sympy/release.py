from __future__ import annotations
# The PEP 440 local version segment after "+" marks this as the fork, not
# upstream SymPy; the part before it is the upstream base the fork tracks.
# Plain "+fork" means an untagged master. A tagged release carries the date
# as well, as in "+fork.2026.9.17"; see "Cutting a release" in CLAUDE.md.
# Do not date this on master: tags are rare here, so a date set outside a
# release would keep claiming that release long after master moved on.
__version__ = "1.15.0.dev+fork"
