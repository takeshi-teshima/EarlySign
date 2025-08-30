import math
from scipy.stats import norm


def obrien_fleming_spending(t: float) -> float:
    """
    O'Brien-Fleming型のα消費関数。
    試験の初期段階では境界値を非常に高く設定し、保守的な判断を促す。

    Args:
        t: 情報時間 (0.0 to 1.0)

    Returns:
        指定された情報時間までに消費されるべきαの割合。
    """
    if t <= 0:
        return 0.0
    if t >= 1:
        return 1.0
    # 両側検定を想定したα=0.05の場合のZ値(1.96)を使用
    z_alpha_half = float(norm.ppf(1 - 0.025))
    return float(2 * (1 - float(norm.cdf(z_alpha_half / math.sqrt(t)))))


def pocock_spending(t: float) -> float:
    """
    Pocock型のα消費関数。
    試験期間を通じて、ほぼ一定の境界値を設定する。

    Args:
        t: 情報時間 (0.0 to 1.0)

    Returns:
        指定された情報時間までに消費されるべきαの割合。
    """
    if t <= 0:
        return 0.0
    if t >= 1:
        return 1.0
    # 両側検定α=0.05を想定
    alpha = 0.025
    return float(alpha * math.log(1 + (math.e - 1) * t))
