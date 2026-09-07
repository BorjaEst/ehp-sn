from typing import *

import ehp_sn.contracts.substrates as contracts
from ehp_sn import figures
from ehp_sn.figures import Figure

from .configuration import Configuration
from .inspection import InspectResult, SummaryResult


def summary_figure(result: SummaryResult) -> Figure: ...


def inspection_figure(result: InspectResult) -> Figure: ...


__all__ = ["summary_figure", "inspection_figure"]
