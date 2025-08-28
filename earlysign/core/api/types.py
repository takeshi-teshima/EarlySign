from typing import Protocol, TypeVar, Any, Callable, TypeAlias, Tuple
from enum import Enum

Observation = TypeVar('Observation')
Time = TypeVar('Time')
Data = TypeVar('Data')
RealizedValue = TypeVar('RealizedValue')
RealizedSequentialValue = Tuple[Time, RealizedValue]
SamplePath: TypeAlias = Callable[[Time], RealizedValue]

class Statistic(Protocol):
    """A sequential statistic protocol.
    """
    value: RealizedValue

    def update(self, data: Data, context: object) -> None:
        ...

class SequentialStatistic(Protocol):
    pass

class Criteria(Protocol):
    def __call__(self, value: RealizedValue) -> bool:
        ...

class Signalizer(Protocol):
    criteria: Criteria

    def evaluate(self, value: RealizedValue) -> bool:
        return self.criteria(value)

class Decision(Enum):
    CONTINUE = "continue"
    REJECT = "reject"
    ACCEPT = "accept"

Advice: TypeAlias = Decision

class StatisticalTest(Protocol):
    statistic: Statistic
    signalizer: Signalizer

    @property
    def conclusion(self) -> Decision:
        if self.signalizer.evaluate(self.statistic.value):
            return Decision.REJECT

class TwoSampleWaldZ:
    pass

class OneSampleWaldZ:
    pass

class TwoSampleProportions:
    pass

class FutilitySignalizer:
    pass
