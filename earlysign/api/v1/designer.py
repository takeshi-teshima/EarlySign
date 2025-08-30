from dataclasses import dataclass
from typing import Callable, Mapping, Any, Dict

from earlysign.core._types import (
    ExperimentDesign,
    ExperimentDesigner,
    StateRepository,
    Condition,
)
from earlysign.core.runner import SequentialTest
from earlysign.stats.proportions.proportion_statistics import TwoSampleZStatisticApprox
from earlysign.stats.common.condition import AlphaSpendingCondition
from earlysign.stats.common.group_sequential.helpers import obrien_fleming_spending


@dataclass(frozen=True)
class GroupSequentialDesign(ExperimentDesign):
    """A concrete design specification for a group sequential test."""

    name: str
    description: str
    max_samples: int
    alpha: float
    spending_function: Callable[[float], float]

    def instantiate(
        self, experiment_id: str, repository: StateRepository
    ) -> SequentialTest[Any, Any, Any]:
        statistic = TwoSampleZStatisticApprox(max_total_samples=self.max_samples)
        conditions: Dict[str, "Condition[float]"] = {
            "efficacy_boundary": AlphaSpendingCondition(
                total_alpha=self.alpha, spending_function=self.spending_function
            )
        }
        return SequentialTest(experiment_id, statistic, conditions, repository)


class OBFDesigner(ExperimentDesigner):
    """Designs a two-sample test using O'Brien-Fleming boundaries."""

    def __init__(self, max_samples: int, alpha: float = 0.05):
        if not 0 < alpha < 1:
            raise ValueError("Alpha must be between 0 and 1.")
        self.max_samples = max_samples
        self.alpha = alpha

    def create_design(self) -> ExperimentDesign:
        description = (
            f"Group sequential design for up to {self.max_samples} samples "
            f"with alpha={self.alpha} using an O'Brien-Fleming spending function."
        )
        return GroupSequentialDesign(
            name="Two-Sample Proportion (O'Brien-Fleming)",
            description=description,
            max_samples=self.max_samples,
            alpha=self.alpha,
            spending_function=obrien_fleming_spending,
        )
