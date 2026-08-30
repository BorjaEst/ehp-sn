"""Shared fixtures for figure tests.

These tests render transient Matplotlib Figures through the figure service.
A figure created through the pyplot interface is retained by Matplotlib's
internal registry until explicitly closed; across many rendering tests these
accumulate and trigger a "More than 20 figures" warning. To keep the suite
deterministic and memory-bounded, every test closes all of Matplotlib's
registered Figures after it completes.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import pytest


@pytest.fixture(autouse=True)
def _close_figures_after_each_test():
    """Close every open Matplotlib Figure after each figure test."""
    yield
    # The figure service transfers ownership of the transient Figure to the
    # caller; closing is a test-harness concern here, not figure semantics.
    plt.close("all")
