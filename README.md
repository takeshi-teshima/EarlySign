# EarlySign

![./docs/logo.png](./docs/logo.png)

Catch the early signs, reach faster conclusions.
Early signs, faster decisions.
A Python library for sequential/safe testing (alpha-spending, e-processes, etc.).

## Install


## Usage

This library supports the following steps in your experimentation.

1. Planning / Designing
1. Executing / Analyzing
1. Reporting / Visualizing
1. (optionally) Educating

### Overview

```python
from earlysign import designs

#
design = designs.GroupSequential(
    name="example-run", variants=["A", "B"],
    kind=["binary"],
    alpha_spending_fn="obrien-fleming",
    max_batches=1000,
    alpha=0.05,
    efficacy=True, futility=False
)

## functional style
from earlysign import factory
handler = factory.get_handler(design)
state = handler.initial_state(design)
state = handler.update(design, state, observation_1)
state = handler.update(design, state, observation_2)
conclusion = handler.conclude(design, state)
report = factory.get_reporter(design).report(conclusion)

## objective style
from earlysign import Experiment
experiment = Experiment(design)
experiment.update(observation_1)
experiment.update(observation_2)
conclusion = experiment.conclude()
report = factory.get_reporter(design).report(conclusion)
```

### Exploring the design

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

### Executing
The execution APIs are designed for the iterative nature of sequential analysis. They support resumed calculations, allowing you to efficiently update your test results as new data arrives in batches. This avoids the need to reprocess the entire dataset each time.

### Reporting
