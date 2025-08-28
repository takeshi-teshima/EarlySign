### Stepped-Wedge Design
**Safely roll out to all users in stages while correctly measuring the impact.**

This design is for situations where a new feature is already planned for a full rollout, but a simultaneous launch is too risky. It involves dividing users into several groups and migrating them to the new feature in a randomized, staggered sequence.

* **EarlySign's Role:**
    * **Automation of Complex Analysis:** This design requires analysis that accounts for time-based trends (e.g., using mixed-effects models). EarlySign handles these complex models internally to sequentially monitor the true effect of the intervention.
    * **Early Anomaly Detection:** If a key metric declines for a group that has been migrated, EarlySign can detect this early, helping you decide whether to pause the rollout.
