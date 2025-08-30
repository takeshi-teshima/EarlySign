from typing import Any, Callable
import math

try:
    from scipy.stats import norm
except Exception:
    # Minimal fallback implementing norm.cdf and norm.ppf using math.erf and
    # an approximate inverse CDF (Acklam). These are good enough for tests
    # that only need typical alpha quantiles.
    class _Norm:
        @staticmethod
        def cdf(x: float) -> float:
            return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

        @staticmethod
        def ppf(p: float) -> float:
            # approximate inverse normal via Acklam's method (simplified)
            if not 0.0 < p < 1.0:
                raise ValueError("p must be in (0,1)")
            # coefficients
            a = [
                -3.969683028665376e01,
                2.209460984245205e02,
                -2.759285104469687e02,
                1.383577518672690e02,
                -3.066479806614716e01,
                2.506628277459239e00,
            ]
            b = [
                -5.447609879822406e01,
                1.615858368580409e02,
                -1.556989798598866e02,
                6.680131188771972e01,
                -1.328068155288572e01,
            ]
            c = [
                -7.784894002430293e-03,
                -3.223964580411365e-01,
                -2.400758277161838e00,
                -2.549732539343734e00,
                4.374664141464968e00,
                2.938163982698783e00,
            ]
            d = [
                7.784695709041462e-03,
                3.224671290700398e-01,
                2.445134137142996e00,
                3.754408661907416e00,
            ]
            plow = 0.02425
            phigh = 1.0 - plow
            if p < plow:
                q = math.sqrt(-2 * math.log(p))
                num = (((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]
                num = num * q + c[5]
                den = (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0
                return float(num / den)
            if p > phigh:
                q = math.sqrt(-2 * math.log(1.0 - p))
                num = (((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]
                num = num * q + c[5]
                den = (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0
                return float(-(num / den))
            q = p - 0.5
            r = q * q
            num = ((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]
            num = num * q
            den = (((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]
            den = den * r + 1.0
            return float(num / den)

    norm = _Norm()

from earlysign.core.interface import (
    ConditionState,
    Condition,
    Stateful,
    SequentialStatistic,
)


class AlphaSpendingCondition(Condition[float], Stateful[ConditionState]):
    """
    α消費関数に基づきZ値やt値の有効性境界を計算するトリガー型Condition。
    一度でも境界を越えれば、永続的にactiveになる。
    """

    def __init__(self, total_alpha: float, spending_function: Callable[[float], float]):
        self.total_alpha = total_alpha
        self.spending_function = spending_function
        self._has_crossed: bool = False

    def is_active(self, statistic: SequentialStatistic[Any, Any, float]) -> bool:
        if self._has_crossed:
            return True

        z_value = statistic.current_value
        max_info = statistic.max_info_metric
        if z_value is None or max_info <= 0:
            return False

        info_time = min(statistic.current_info_metric / max_info, 1.0)
        if info_time <= 0:
            return False

        cumulative_alpha = self.total_alpha * self.spending_function(info_time)
        if cumulative_alpha <= 0:
            return False

        # 両側検定の境界Z値を計算
        boundary = norm.ppf(1 - cumulative_alpha / 2)

        if abs(z_value) >= boundary:
            self._has_crossed = True
            return True

        return False

    def get_state(self) -> ConditionState:
        return ConditionState(internal_state={"has_crossed": self._has_crossed})

    def load_state(self, state: ConditionState) -> None:
        self._has_crossed = state.internal_state.get("has_crossed", False)


class EValueThresholdCondition(Condition[float], Stateful[ConditionState]):
    """
    E-valueが閾値(1/alpha)に一度でも達したら、永続的にactiveになる
    トリガー型Condition。
    """

    def __init__(self, alpha: float = 0.05):
        if not (0 < alpha < 1):
            raise ValueError("alpha must be between 0 and 1")
        self.threshold = 1 / alpha
        self._has_crossed: bool = False

    def is_active(self, statistic: SequentialStatistic[Any, Any, float]) -> bool:
        if self._has_crossed:
            return True

        e_value = statistic.current_value
        if e_value is not None and e_value >= self.threshold:
            self._has_crossed = True
            return True

        return False

    def get_state(self) -> ConditionState:
        return ConditionState(internal_state={"has_crossed": self._has_crossed})

    def load_state(self, state: ConditionState) -> None:
        self._has_crossed = state.internal_state.get("has_crossed", False)
