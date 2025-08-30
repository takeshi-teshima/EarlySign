from typing import Tuple, List, Optional, Sequence, Any
from earlysign.core._types import SequentialStatistic, StatisticState, Stateful

ProportionObservation = Tuple[int, int]  # (群1の成功(1/0), 群2の成功(1/0))


class TwoSampleZStatisticApprox(
    SequentialStatistic[int, ProportionObservation, float], Stateful[StatisticState]
):
    """
    2標本比率差のZ統計量（正規近似）。サンプルサイズが大きい場合に適している。
    """

    def __init__(self, max_total_samples: int):
        self.max_samples = max_total_samples
        self._history: List[Tuple[int, float]] = []
        self._n1, self._n2, self._s1, self._s2 = 0, 0, 0, 0

    @property
    def history(self) -> Sequence[Tuple[int, float]]:
        return self._history

    @property
    def current_value(self) -> Optional[float]:
        return self._history[-1][1] if self._history else None

    @property
    def current_info_metric(self) -> float:
        return float(self._n1 + self._n2)

    @property
    def max_info_metric(self) -> float:
        return float(self.max_samples)

    def update(self, time: int, observation: ProportionObservation) -> None:
        obs1, obs2 = observation
        self._n1 += 1
        self._n2 += 1
        self._s1 += obs1
        self._s2 += obs2

        # 統計量の計算
        p1_hat = self._s1 / self._n1
        p2_hat = self._s2 / self._n2
        p_hat = (self._s1 + self._s2) / (self._n1 + self._n2)

        if p_hat <= 0 or p_hat >= 1:
            z_value = 0.0
        else:
            std_err = (p_hat * (1 - p_hat) * (1 / self._n1 + 1 / self._n2)) ** 0.5
            z_value = (p1_hat - p2_hat) / std_err if std_err > 0 else 0.0

        self._history.append((time, z_value))

    def get_state(self) -> StatisticState:
        internal_state = {
            "n1": self._n1,
            "n2": self._n2,
            "s1": self._s1,
            "s2": self._s2,
        }
        return StatisticState(
            history=list(self._history), internal_state=internal_state
        )

    def load_state(self, state: StatisticState) -> None:
        self._history = state.history
        self._n1 = state.internal_state.get("n1", 0)
        self._n2 = state.internal_state.get("n2", 0)
        self._s1 = state.internal_state.get("s1", 0)
        self._s2 = state.internal_state.get("s2", 0)
