"""Reporter utilities.

Example (doctest):
>>> from earlysign.core._types import SignalEvent, Signal, Recommendation
>>> from earlysign.core.reporter import Reporter
>>> e = SignalEvent(time=1, condition_name='c1', signal=Signal.CONDITION_MET)
>>> r = Reporter([e])
>>> 'Total Signal Events' in r.generate_summary()
True
>>> r.get_recommendation() == Recommendation.CONSIDER_STOPPING
True
"""

from earlysign.core._types import SignalEvent, Recommendation, Signal


class Reporter:
    """Analyzes the history of SignalEvents to generate summaries."""

    def __init__(self, history: list[SignalEvent]):
        self.history = history

    def generate_summary(self) -> str:
        summary = "--- Monitoring Summary ---\n"
        if not self.history:
            return summary + "No signal events were recorded."

        summary += f"Total Signal Events: {len(self.history)}\n"
        for event in self.history:
            summary += (
                f"  - Time: {event.time}, "
                f"Condition: '{event.condition_name}', "
                f"Signal: {event.signal.name}\n"
            )
        return summary

    def get_recommendation(self) -> Recommendation:
        if any(event.signal == Signal.CONDITION_MET for event in self.history):
            return Recommendation.CONSIDER_STOPPING
        return Recommendation.CONTINUE_MONITORING
