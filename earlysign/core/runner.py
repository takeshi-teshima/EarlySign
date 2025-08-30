from earlysign.core.interface import (
    T_Time,
    T_Observation,
    T_StatisticValue,
    Stateful,
    ExperimentState,
    SequentialStatistic,
    Condition,
    StateRepository,
    SignalEvent,
    Signal,
    ExperimentStatus,
    StatisticState,
    ConditionState,
)
from typing import Generic, List, Dict, cast


class SequentialTest(
    Generic[T_Time, T_Observation, T_StatisticValue], Stateful[ExperimentState]
):
    """
    The experiment runner. It observes state changes in Conditions
    and logs them as SignalEvents.
    """

    def __init__(
        self,
        experiment_id: str,
        statistic: SequentialStatistic[T_Time, T_Observation, T_StatisticValue],
        conditions: dict[str, Condition[T_StatisticValue]],
        repository: StateRepository,
    ) -> None:
        self.experiment_id = experiment_id
        self.statistic = statistic
        self.conditions = conditions
        self.repository = repository
        self.signal_history: list[SignalEvent] = []
        self._previous_states: dict[str, bool] = {name: False for name in conditions}

    def consume(self, time: T_Time, observation: T_Observation) -> ExperimentStatus:
        self.statistic.update(time, observation)

        triggered_signals_this_step: List[SignalEvent] = []
        current_condition_states: Dict[str, bool] = {}

        for name, condition in self.conditions.items():
            previous_state = self._previous_states[name]
            current_state = condition.is_active(self.statistic)
            current_condition_states[name] = current_state

            if current_state and not previous_state:  # False -> True
                event = SignalEvent(time, name, Signal.CONDITION_MET)
                self.signal_history.append(event)
                triggered_signals_this_step.append(event)
            elif not current_state and previous_state:  # True -> False
                event = SignalEvent(time, name, Signal.CONDITION_ENDED)
                self.signal_history.append(event)
                triggered_signals_this_step.append(event)

            self._previous_states[name] = current_state

        info_metric = self.statistic.current_info_metric
        max_metric = self.statistic.max_info_metric
        info_time = min(info_metric / max_metric, 1.0) if max_metric > 0 else 0.0

        return ExperimentStatus(
            time,
            info_time,
            self.statistic.current_value,
            current_condition_states,
            triggered_signals_this_step,
        )

    # --- Checkpointing Methods ---
    def get_state(self) -> ExperimentState:
        # Assumes statistic and conditions implement Stateful
        conditions_state: Dict[str, ConditionState] = {}
        for name, cond in self.conditions.items():
            if isinstance(cond, Stateful):
                conditions_state[name] = cast(
                    ConditionState, cast(Stateful[object], cond).get_state()
                )

        if isinstance(self.statistic, Stateful):
            stat_state = cast(Stateful[StatisticState], self.statistic).get_state()
        else:
            stat_state = StatisticState(history=[], internal_state={})

        return ExperimentState(
            stat_state,
            conditions_state,
            list(self.signal_history),
            dict(self._previous_states),
        )

    def load_state(self, state: ExperimentState) -> None:
        if isinstance(self.statistic, Stateful):
            cast(Stateful[object], self.statistic).load_state(state.statistic_state)
        for name, cond_state in state.conditions_state.items():
            if name in self.conditions and isinstance(self.conditions[name], Stateful):
                cast(Stateful[object], self.conditions[name]).load_state(cond_state)
        self.signal_history = state.signal_history
        self._previous_states = state.previous_condition_states

    async def save_checkpoint(self) -> None:
        await self.repository.save(self.experiment_id, self.get_state())

    @classmethod
    async def resume_from(
        cls,
        experiment_id: str,
        statistic: SequentialStatistic[T_Time, T_Observation, T_StatisticValue],
        conditions: dict[str, Condition[T_StatisticValue]],
        repository: StateRepository,
    ) -> "SequentialTest[T_Time, T_Observation, T_StatisticValue]":
        instance = cls(experiment_id, statistic, conditions, repository)
        if await repository.exists(experiment_id):
            state = await repository.load(experiment_id)
            instance.load_state(state)
        return instance
