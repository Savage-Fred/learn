# Exercise TIER4_L6: Marketplace Switchback & Cluster Randomization Experimentation Engine

**Objective**: Architect an experimentation platform for two-sided marketplaces that designs, schedules, and analyzes cluster-randomized switchback experiments mitigating SUTVA network spillover.

---

## Problem Statement

Design and implement `MarketplaceExperimentEngine`. Model cities as spatial clusters. Schedule alternating time windows (e.g. 2-hour blocks) randomized between treatment and control. Incorporate a 15-minute washout window at the start of each switchback period to discard transitional data contaminated by prior conditions. Analyze results using cluster-robust standard errors (CRVE) to account for temporal and spatial autocorrelation.

---

## Formal Constraints

- Scale: 100 metropolitan cities, 50,000 rides per hour.
- Interference: Ride-hail driver availability spillovers across adjacent geographic zones and time slots.
- Washout: Configurable washout window between alternating treatment/control blocks.

---

## Starter Code

```python
class MarketplaceExperimentEngine:
    def __init__(self, cities: list, block_duration_hours: int = 2, washout_minutes: int = 15):
        self.cities = cities
        self.block_duration = block_duration_hours
        self.washout = washout_minutes

    def generate_switchback_schedule(self, days: int) -> dict:
        """Generate balanced switchback schedule across cities and time blocks."""
        pass

    def analyze_switchback_results(self, ride_data_df) -> dict:
        """Filter washout windows and compute treatment effect with cluster-robust standard errors."""
        pass
```

---

## Verification Test Cases

- [ ] **Test Case**: Generates balanced schedule ensuring equal treatment/control distribution across morning/evening peaks.
- [ ] **Test Case**: Correctly filters out rides originating within the 15-minute washout window.
- [ ] **Test Case**: Computes cluster-robust standard errors clustering at the (city, day) level, preventing false certainty.

---

## Solution & Invariant Check

Block randomization per city-time block; discard data in [t_start, t_start + washout]; fit OLS with cluster-robust Huber-White covariance matrix clustered on city-day.