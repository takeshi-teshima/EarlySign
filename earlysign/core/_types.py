from __future__ import annotations
from typing import (
    TypeVar,
    Generic,
    Protocol,
    List,
    Tuple,
    Optional,
    Any,
    Sequence,
    Dict,
    Callable,
    runtime_checkable,
)
from enum import Enum, auto
from dataclasses import dataclass, field

# --- Generic Type Variables ---
T_Time = TypeVar("T_Time")
T_Observation = TypeVar("T_Observation", contravariant=True)
T_StatisticValue = TypeVar("T_StatisticValue", covariant=True)

# --- Core Vocabulary (Enums and Dataclasses) ---


class Signal(Enum):
    """A signal emitted when the state of a Condition changes."""

    CONDITION_MET = "A stateful condition has just been met (ON)"
    CONDITION_ENDED = "A stateful condition has just ended (OFF)"


class Recommendation(Enum):
    """A human-readable recommendation for the monitoring committee."""

    CONTINUE_MONITORING = "Continue monitoring as planned"
    CONSIDER_STOPPING = "Consider stopping the trial"


@dataclass(frozen=True)
class SignalEvent:
    """A record of which Condition emitted which Signal at what Time."""

    time: Any
    condition_name: str
    signal: Signal


@dataclass(frozen=True)
class ExperimentStatus:
    """A snapshot of the experiment's state at a single point in time."""

    time: Any
    information_time: float
    statistic_value: Optional[Any]
    condition_states: dict[str, bool] = field(default_factory=dict)
    triggered_signals: list[SignalEvent] = field(default_factory=list)


# --- Protocols for Checkpointing ---

T_State = TypeVar("T_State")


@dataclass
class StatisticState:
    """A serializable representation of a SequentialStatistic's internal state."""

    history: list[Tuple[Any, Any]]
    # container for implementation-specific internal state
    internal_state: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConditionState:
    """A serializable representation of a Condition's internal state."""

    # Add state variables specific to implementations here
    # e.g., has_crossed: bool
    internal_state: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExperimentState:
    """A complete checkpoint of the entire experiment's state."""

    statistic_state: StatisticState
    conditions_state: Dict[str, ConditionState]
    signal_history: List[SignalEvent]
    previous_condition_states: Dict[str, bool]


@runtime_checkable
class Stateful(Protocol[T_State]):
    """An interface for components that support state checkpointing."""

    def get_state(self) -> T_State:
        """Returns the component's internal state as a serializable object."""
        ...

    def load_state(self, state: T_State) -> None:
        """Restores the component's internal state from a state object."""
        ...


# --- Core Component Protocols ---


class SequentialStatistic(Protocol[T_Time, T_Observation, T_StatisticValue]):
    """
    The history of information (Filtration). It processes observations
    and maintains the history of a statistical value.
    """

    @property
    def history(self) -> Sequence[Tuple[T_Time, T_StatisticValue]]: ...

    @property
    def current_value(self) -> Optional[T_StatisticValue]: ...

    @property
    def current_info_metric(self) -> float: ...

    @property
    def max_info_metric(self) -> float: ...

    def update(self, time: T_Time, observation: T_Observation) -> None: ...


T_CondValue = TypeVar("T_CondValue", contravariant=True)


class Condition(Protocol[T_CondValue]):
    """
    An adapted process. It determines if a condition is active (True/False)
    based on the history provided by a SequentialStatistic.
    """

    def is_active(
        self, statistic: SequentialStatistic[Any, Any, T_CondValue]
    ) -> bool: ...


class ExperimentDesign(Protocol):
    """Protocol describing a concrete design object used by the API layer."""

    name: str
    description: str
    max_samples: int
    alpha: float
    spending_function: Callable[[float], float]

    def instantiate(self, experiment_id: str, repository: "StateRepository") -> Any: ...


class ExperimentDesigner(Protocol):
    def create_design(self) -> ExperimentDesign: ...


class StateRepository(Protocol):
    """An interface for abstracting the storage of ExperimentState objects."""

    async def save(self, experiment_id: str, state: ExperimentState) -> None: ...
    async def load(self, experiment_id: str) -> ExperimentState: ...
    async def exists(self, experiment_id: str) -> bool: ...
