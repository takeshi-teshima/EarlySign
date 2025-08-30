# Sequential Probability Ratio Test (SPRT)
**The most efficient classic method for making a clear-cut decision.**

SPRT is a fundamental sequential test for deciding between two simple hypotheses (e.g., "CVR is 3%" vs. "CVR is 5% "). On average, it often reaches a conclusion with fewer samples than fixed-sample tests or other sequential methods.

* **Use Cases:**
    * A/B tests with a clear target for the improvement metric.
    * Quality control processes for pass/fail decisions.
* **Key Features:**
    * **Simple Boundary Setting:** Automatically calculates the boundaries for continuing, accepting, or rejecting a hypothesis based on the two hypotheses and acceptable error rates (α, β).
