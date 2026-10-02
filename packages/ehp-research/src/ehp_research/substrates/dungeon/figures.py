from __future__ import annotations

from ehp_sn.figures import Figure

from .inspection import InspectResult, SummaryResult


def summary_figure(result: SummaryResult) -> Figure: ...


def inspection_figure(result: InspectResult) -> Figure: ...


__all__ = ["summary_figure", "inspection_figure"]
