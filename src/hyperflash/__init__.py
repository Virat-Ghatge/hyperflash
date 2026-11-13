"""
HyperFlash: The Universal Engineering Reliability Runtime & Multi-Agent Verification Guardrails.
"""
from __future__ import annotations

from hyperflash.core import (
    HyperFlashRuntime,
    build_symbol_graph,
    check_for_elision,
    enforce_elision_guard,
    generate_symbol_graph,
    load_contract,
    run_verification,
    save_contract,
)

__version__: str = "1.1.2"

__all__: list[str] = [
    "__version__",
    "HyperFlashRuntime",
    "enforce_elision_guard",
    "build_symbol_graph",
    "check_for_elision",
    "generate_symbol_graph",
    "load_contract",
    "save_contract",
    "run_verification",
]
