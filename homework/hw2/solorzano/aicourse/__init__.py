"""CMP-4004 course harness.

Three things live here, and you will use all of them every week:

    llm     — a cached, multi-backend LLM client (week 0 builds this)
    cache   — content-addressed response storage; your audit trail
    doctor  — environment check; run it before you ask for help

Design constraint for the whole package: it must work on a laptop with no GPU,
no paid API key, and no network. Every backend below is optional except the
manual one, which always works.
"""

__version__ = "1.0.0"

# Submodules are imported lazily. Importing .llm eagerly here would make
# `python -m aicourse.llm` emit a RuntimeWarning, because the module would
# already be in sys.modules before runpy executes it as __main__.
__all__ = ["Cache", "LLM", "LLMResponse", "backends_available", "__version__"]


def __getattr__(name):
    if name == "Cache":
        from .cache import Cache
        return Cache
    if name in ("LLM", "LLMResponse", "backends_available"):
        from . import llm as _llm
        return getattr(_llm, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
