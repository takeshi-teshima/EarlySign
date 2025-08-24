# API Structure (WIP)

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
