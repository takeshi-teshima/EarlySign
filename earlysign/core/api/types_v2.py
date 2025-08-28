# Python 3.9+ を想定 (ジェネリクスでのTypeAliasなど)
# Python 3.7+ の場合は from typing import ... で調整が必要
from __future__ import annotations
from typing import (
    TypeVar, Generic, Protocol, List, Tuple, Optional, Any, Sequence
)
from enum import Enum, auto

# --- 1. 基本的な型変数の定義 ---

T_Time = TypeVar('T_Time')              # 時間やサンプルサイズ (e.g., int, float)
T_Observation = TypeVar('T_Observation') # 観測データ (e.g., float, Tuple[bool, bool])
T_StatisticValue = TypeVar('T_StatisticValue') # 統計量の値 (e.g., float for Z-score)

# --- 2. 状態を表現するEnumとデータ構造 ---

class Decision(Enum):
    """試験の決定を表すEnum"""
    CONTINUE_SAMPLING = auto()
    REJECT_NULL = auto()
    ACCEPT_NULL = auto() # 無益性停止などで利用

# --- 3. コアとなるプロトコル（抽象インターフェース）の定義 ---

class SequentialStatistic(Protocol[T_Time, T_Observation, T_StatisticValue]):
    """
    逐次統計量のプロトコル。観測データを元に状態を更新し、値の履歴を保持する。
    """
    @property
    def history(self) -> Sequence[Tuple[T_Time, T_StatisticValue]]:
        """統計量の値の履歴 (時間, 値)"""
        ...

    @property
    def current_value(self) -> Optional[T_StatisticValue]:
        """最新の統計量"""
        ...

    @property
    def current_time(self) -> Optional[T_Time]:
        """最新の時間"""
        ...

    def update(self, time: T_Time, observation: T_Observation) -> None:
        """新しい観測データで統計量を更新する"""
        ...


class StoppingRule(Protocol[T_Time, T_Observation, T_StatisticValue]):
    """
    試験の停止ルールを定義するプロトコル。
    統計量のプロセス全体を監視し、停止すべきかどうかを判断する。
    """
    def check(
        self,
        statistic: SequentialStatistic[T_Time, T_Observation, T_StatisticValue]
    ) -> Optional[Decision]:
        """
        統計量の状態をチェックし、試験を停止すべきならDecisionを、
        継続すべきならNoneを返す。
        """
        ...

# --- 4. プロトコルを束ねるクラス ---

class SequentialTest(Generic[T_Time, T_Observation, T_StatisticValue]):
    """
    逐次検定のプロセス全体を管理する進行役（Runner）。
    統計量と複数の停止ルールを保持し、データを消費して検定を進める。
    """
    def __init__(
        self,
        statistic: SequentialStatistic[T_Time, T_Observation, T_StatisticValue],
        stopping_rules: List[StoppingRule[T_Time, T_Observation, T_StatisticValue]]
    ):
        self.statistic = statistic
        self.stopping_rules = stopping_rules
        self.decision: Decision = Decision.CONTINUE_SAMPLING
        self.stopped_at: Optional[T_Time] = None

    def consume(self, time: T_Time, observation: T_Observation) -> Decision:
        """
        新しい観測データを処理し、試験の状態を更新・判定する。
        すでに停止している場合は現在の決定を返す。
        """
        if self.decision is not Decision.CONTINUE_SAMPLING:
            return self.decision

        # 1. 統計量を更新
        self.statistic.update(time, observation)

        # 2. 各停止ルールをチェック
        for rule in self.stopping_rules:
            decision = rule.check(self.statistic)
            if decision:
                # 停止が決定された
                self.decision = decision
                self.stopped_at = time
                return self.decision

        # どのルールにも抵触しなければ継続
        return Decision.CONTINUE_SAMPLING

# --- 具体的なデータ型を定義 ---
# (サンプルサイズ, 治療群での成功数, 対照群での成功数)
ProportionObservation = Tuple[int, int]


# --- 具体的な統計量の実装 ---
class TwoSampleProportionZ(SequentialStatistic[int, ProportionObservation, float]):
    """2標本比率のZ統計量"""
    def __init__(self) -> None:
        self._history: List[Tuple[int, float]] = []
        self._n1, self._n2 = 0, 0 # 治療群、対照群の累積サンプルサイズ
        self._p1, self._p2 = 0, 0 # 治療群、対照群の累積成功数

    @property
    def history(self) -> Sequence[Tuple[int, float]]:
        return self._history

    @property
    def current_value(self) -> Optional[float]:
        return self._history[-1][1] if self._history else None

    @property
    def current_time(self) -> Optional[int]:
        return self._history[-1][0] if self._history else None

    def update(self, time: int, observation: ProportionObservation) -> None:
        # 簡単のため、timeは観測回数(1, 2, 3...)とする
        s1, s2 = observation # 今回の観測での成功数
        # ここでは1回の観測で1サンプルずつ増えると仮定
        self._n1 += 1
        self._n2 += 1
        self._p1 += s1
        self._p2 += s2

        if self._n1 == 0 or self._n2 == 0:
            return

        p1_hat = self._p1 / self._n1
        p2_hat = self._p2 / self._n2
        p_hat = (self._p1 + self._p2) / (self._n1 + self._n2)

        # ゼロ割を避ける
        if p_hat == 0 or p_hat == 1:
            z_value = 0.0
        else:
            denominator = (p_hat * (1 - p_hat) * (1/self._n1 + 1/self._n2)) ** 0.5
            z_value = (p1_hat - p2_hat) / denominator if denominator > 0 else 0.0

        self._history.append((self._n1 + self._n2, z_value))

# --- 具体的な停止ルールの実装 ---
class EfficacyRule(StoppingRule[int, Any, float]):
    """有効性（H0を棄却）を判断するルール"""
    def __init__(self, threshold: float):
        self.threshold = threshold

    def check(self, statistic: SequentialStatistic[int, Any, float]) -> Optional[Decision]:
        if statistic.current_value and statistic.current_value >= self.threshold:
            return Decision.REJECT_NULL
        return None

class FutilityRule(StoppingRule[int, Any, float]):
    """無益性（H0を受容）を判断するルール"""
    def __init__(self, threshold: float):
        self.threshold = threshold

    def check(self, statistic: SequentialStatistic[int, Any, float]) -> Optional[Decision]:
        if statistic.current_value and statistic.current_value <= self.threshold:
            return Decision.ACCEPT_NULL
        return None

# --- シミュレーションの実行 ---
def run_simulation():
    # 1. 検定のコンポーネントを組み立てる
    z_statistic = TwoSampleProportionZ()
    efficacy_boundary = EfficacyRule(threshold=2.5)   # Z > 2.5 で棄却
    futility_boundary = FutilityRule(threshold=0.1)   # Z < 0.1 で受容（無益）

    test = SequentialTest(
        statistic=z_statistic,
        stopping_rules=[efficacy_boundary, futility_boundary]
    )

    # 2. データを逐次的に流し込む
    # 例: 治療群がやや優れているデータストリーム
    data_stream = [(1, 0), (1, 1), (0, 0), (1, 0), (1, 0), (1, 1), (1, 0), (1, 0)]

    print("--- Simulation Start ---")
    for i, observation in enumerate(data_stream, start=1):
        decision = test.consume(i, observation)
        print(f"Time: {test.statistic.current_time}, Z-value: {test.statistic.current_value:.2f}, Decision: {decision.name}")

        if decision is not Decision.CONTINUE_SAMPLING:
            print(f"\n--- Test Stopped at time {test.stopped_at} ---")
            print(f"Final Decision: {test.decision.name}")
            break

    if test.decision is Decision.CONTINUE_SAMPLING:
        print("\n--- Test finished without a stop decision ---")

# 実行
run_simulation()
