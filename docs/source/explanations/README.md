# EarlySign

**Catch the early signs, reach faster conclusions.**

EarlySign is a Python library designed to accelerate decision-making in A/B testing and statistical monitoring. Without waiting for experiments to fully complete, it allows you to statistically and correctly interpret the "early signs" in your data to arrive at faster, more confident conclusions.

## Features: Supported Methods & Designs

EarlySign supports a range of sequential analysis approaches, from classic methods to the latest research. You can select the optimal method based on the characteristics and requirements of your experiment. EarlySign also provides a simple interface to execute complex experimental designs.

1. [Group Sequential Tests](./methods/gst.md)
    - Terminate futile experiments early with planned interim analyses.
1. [Anytime-Valid Inference with E-values](./methods/e-values.md)
    - Look anytime, as many times as you want. A cutting-edge approach for real-time monitoring.
1. [Sequential Probability Ratio Test (SPRT)](./methods/sprt.md)
    - The most efficient classic method for making a clear-cut decision.
1. [Stepped-Wedge Design](./methods/stepped-wedge.md)
    - Safely roll out to all users in stages while correctly measuring the impact.
1. [Test and Roll Strategy](./methods/test-and-roll.md)
    - Achieve the fastest tests and the safest rollouts in a single workflow.
