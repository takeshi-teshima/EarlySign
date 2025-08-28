# API Structure (WIP)

We take a compositional approach that facilitates the process of choosing and designing the test.
The API consists of the following types/classes.

1. the statistic
1. the criteria
    e-value significance test criterion
        advice: stop
    asymptotic normal test criterion
        advice: continue
        status: signal detected

```
# Set the criteria
Data (and relevant context) are Observation(s)

Statistic ingests Observations and its Values get updated.
(as well as maintaining the history of values)

Explicator (Signalizer) looks at Values through the lens of Criteria and produces a Signal

Signalizers are partly defined by Criteria.
For example, a FutilitySignalizer may be defined by an AsymptoticNormalFutilityBoundary(Criterion).
The Criteria is usually a function that can change dynamically depending on the observations (e.g., the information time can be stochastic).

FutilitySignalizer(criteria=AsymptoticNormalFutilityBoundaryCriterion)
observes Statistic and finds that the criteria are met.
-> FutilitySignal becomes active

Many Criteria are Boundaries. Others can be staying time, etc.

Explicator interprets the Values through the Lens
Display
Qualifier
Evaluation
Assessment

DecisionPolicy interprets those Signals and draws a Conclusion.

Reporter summarizes and visualizes the sequence of events in the Experiment and the Conclusion.
```

from_config()
from_problem_setup(ProblemSetup(metric='conversion_rate', kind='two_sample'))

## Statistic

The Statistic type is the


## Exploring the design

```python
from earlysign import designs

design_choices = {}
sample_size: dict = designs.GroupSequential.from_power_analysis(
    mde=0.01,
    power=0.8,
    alpha=0.05,
    metric_type="conversion",
    num_interims=4 # analyze 4 times
)
design_choices.update(sample_size)
# Internally...
# 1. The required total sample size (e.g., 21,500) is calculated.
# 2. The interim analysis schedule (e.g., [5375, 10750, 16125, 21500]) is automatically derived.
```

## Executing
The execution APIs are designed for the iterative nature of sequential analysis. They support resumed calculations, allowing you to efficiently update your test results as new data arrives in batches. This avoids the need to reprocess the entire dataset each time.

## Reporting
