from abc import ABC, abstractmethod
import math
from typing import Optional


# (phi helpers moved into OBrienFlemingSpending class)


class BaseSpendingFunction(ABC):
    """Minimal base class for alpha-spending functions.

    Subclasses implement `cumulative(t)` returning the cumulative alpha spent
    at information fraction t in [0, 1]. The base class enforces a simple alpha
    check and provides `incremental` and `__call__` helpers.
    """

    def __init__(self, alpha: float):
        if not isinstance(alpha, (int, float)):
            raise TypeError("alpha must be numeric")
        alpha = float(alpha)
        if not (0.0 < alpha <= 1.0):
            raise ValueError("alpha must be in (0, 1]")
        self.alpha = alpha

    @abstractmethod
    def _cumulative(self, t: float) -> float:
        """Compute the raw cumulative spending at t (no checking/clipping).

        Subclasses implement this. `cumulative` wrapper will validate t and
        clip the result to [0, self.alpha].
        """

    def cumulative(self, t: float) -> float:
        """Validate t, call subclass `_cumulative`, and clip to valid range."""
        t = self._check_t(t)
        val = float(self._cumulative(t))
        # clip to [0, alpha] succinctly
        return min(max(val, 0.0), float(self.alpha))

    def incremental(self, t_prev: float, t: float) -> float:
        """Alpha spent between t_prev and t (t_prev <= t)."""
        t_prev = self._check_t(t_prev)
        t = self._check_t(t)
        if t < t_prev:
            raise ValueError("t must be >= t_prev")
        return self.cumulative(t) - self.cumulative(t_prev)

    def __call__(self, t: float) -> float:
        return self.cumulative(t)

    @staticmethod
    def _check_t(t: float) -> float:
        if not isinstance(t, (int, float)):
            raise TypeError("t must be numeric")
        t = float(t)
        if not (0.0 <= t <= 1.0):
            raise ValueError("t must be in [0, 1]")
        return t


class OBrienFlemingSpending(BaseSpendingFunction):
    """O'Brien-Fleming type spending function.

    cumulative(t) = 2 * (1 - Phi(z_{1-alpha/2} / sqrt(t)))  for t>0, else 0
    where Phi is the standard normal CDF and z_{1-alpha/2} is its quantile.
    """

    @staticmethod
    def _phi(x: float) -> float:
        """Standard normal CDF using math.erf."""
        return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

    @staticmethod
    def _phi_ppf(p: float) -> float:
        """Inverse of the standard normal CDF (approximation by Acklam).

        Accurate enough for typical alpha values used in testing.
        """
        if not 0.0 < p < 1.0:
            raise ValueError("p must be in (0,1)")

        # Coefficients in rational approximations
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

        # Define break-points.
        plow = 0.02425
        phigh = 1 - plow

        if p < plow:
            q = math.sqrt(-2 * math.log(p))
            num = ((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]
            den = (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1
            return num / den

        if p > phigh:
            q = math.sqrt(-2 * math.log(1 - p))
            num = ((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]
            den = (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1
            return -(num / den)

        q = p - 0.5
        r = q * q
        num = (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q
        den = ((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1
        return num / den

    def _cumulative(self, t: float) -> float:
        if t == 0.0:
            return 0.0
        z = type(self)._phi_ppf(1.0 - self.alpha / 2.0)
        val = 2.0 * (1.0 - type(self)._phi(z / math.sqrt(t)))
        return val


class HwangShihDeCaniSpending(BaseSpendingFunction):
    """Hwang-Shih-DeCani spending function with parameter gamma.

    alpha*(t) = alpha * (1 - exp(-gamma * t)) / (1 - exp(-gamma))
    For gamma -> 0 this reduces to linear spending alpha * t.
    """

    def __init__(self, alpha: float, gamma: Optional[float] = None):
        super().__init__(alpha)
        self.gamma = 0.0 if gamma is None else float(gamma)

    def _cumulative(self, t: float) -> float:
        g = self.gamma
        # If gamma is exactly zero, this reduces to linear spending
        if g == 0.0:
            return self.alpha * t
        denom = 1.0 - math.exp(-g)
        return self.alpha * (1.0 - math.exp(-g * t)) / denom


class KimDeMetsSpending(BaseSpendingFunction):
    """Kim & DeMets power family: alpha * t^rho, with rho > 0."""

    def __init__(self, alpha: float, rho: float = 1.0):
        super().__init__(alpha)
        if not isinstance(rho, (int, float)):
            raise TypeError("rho must be numeric")
        self.rho = float(rho)

    def _cumulative(self, t: float) -> float:
        return self.alpha * (t**self.rho)
