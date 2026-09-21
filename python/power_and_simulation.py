"""
EVERYTHING in this file is HYPOTHETICAL / SIMULATED. The "ETA Confidence & Delivery
Experience" feature does not exist; no real experiment was run. This script (a) computes
the sample size a real experiment would need (standard two-proportion power analysis --
the formula is real, the inputs are stated assumptions for a not-yet-run test), and
(b) simulates a plausible post-launch trial result using that sample size, with the same
statistical rigor (two-proportion z-test, 95% CI, guardrail checks) as the real A/B test
in the sibling food-delivery-analytics project. See CASE_STUDY.md > Data Assumptions for
the full real-vs-simulated split; nothing computed here should be read as a real result.
"""
import numpy as np
from scipy import stats

rng = np.random.default_rng(2025)

# ---------------------------------------------------------------------------
# Power analysis inputs -- ASSUMPTIONS for a not-yet-run test (MODELING CHOICE, stated
# plainly; there is no published real baseline order-completion rate to cite here, unlike
# the real delay-frequency numbers in the Problem Evidence section, which ARE real).
# ---------------------------------------------------------------------------
BASELINE_COMPLETION_RATE = 0.94   # MODELING CHOICE: plausible baseline order completion rate
MDE_ABSOLUTE_PP = 0.015           # MODELING CHOICE: minimum detectable effect, +1.5pp
ALPHA = 0.05
POWER = 0.80


def two_proportion_sample_size(p1: float, mde: float, alpha: float, power: float) -> int:
    """Standard two-proportion z-test sample size formula (per arm), normal approximation."""
    p2 = p1 + mde
    p_bar = (p1 + p2) / 2
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    numerator = (z_alpha * np.sqrt(2 * p_bar * (1 - p_bar)) + z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    n = numerator / (mde ** 2)
    return int(np.ceil(n))


def two_prop_ztest(x1, n1, x2, n2):
    p1, p2 = x1 / n1, x2 / n2
    p_pool = (x1 + x2) / (n1 + n2)
    se_pool = np.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    z = (p2 - p1) / se_pool
    p_value = 2 * stats.norm.sf(abs(z))
    se_diff = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    ci_low, ci_high = (p2 - p1) - 1.96 * se_diff, (p2 - p1) + 1.96 * se_diff
    return dict(p1=p1, p2=p2, z=z, p_value=p_value, abs_lift=p2 - p1,
                rel_lift=(p2 - p1) / p1, ci_low=ci_low, ci_high=ci_high)


if __name__ == "__main__":
    n_per_arm = two_proportion_sample_size(BASELINE_COMPLETION_RATE, MDE_ABSOLUTE_PP, ALPHA, POWER)
    print(f"HYPOTHETICAL power analysis: baseline={BASELINE_COMPLETION_RATE:.0%}, "
          f"MDE=+{MDE_ABSOLUTE_PP*100:.1f}pp, alpha={ALPHA}, power={POWER:.0%}")
    print(f"Required sample size per arm: {n_per_arm:,}")

    # Assume ~9,000 daily checkout-initiated orders eligible for the test (MODELING CHOICE,
    # order-of-magnitude consistent with the ~45,593 orders / 31-day real dataset in
    # food-delivery-analytics, i.e. ~1,470/day city-wide -- scaled up here for a
    # hypothetical larger multi-city rollout; stated as an assumption, not a real figure).
    DAILY_ELIGIBLE_ORDERS_PER_ARM = 4500
    runtime_days = int(np.ceil(n_per_arm / DAILY_ELIGIBLE_ORDERS_PER_ARM))
    print(f"Assumed ~{DAILY_ELIGIBLE_ORDERS_PER_ARM:,} eligible orders/day/arm -> "
          f"expected runtime: ~{runtime_days} days")

    # --- SIMULATED post-launch trial result ---
    n_control = n_per_arm
    n_treatment = n_per_arm
    true_treatment_rate = BASELINE_COMPLETION_RATE + 0.018  # SIMULATED realized effect, close to MDE
    x_control = rng.binomial(n_control, BASELINE_COMPLETION_RATE)
    x_treatment = rng.binomial(n_treatment, true_treatment_rate)

    primary = two_prop_ztest(x_control, n_control, x_treatment, n_treatment)
    print("\n=== SIMULATED primary metric: order completion rate ===")
    for k, v in primary.items():
        print(f"  {k}: {v}")

    decision = "SHIP" if primary["p_value"] < ALPHA and primary["ci_low"] > 0 else "NO-SHIP"
    print(f"  DECISION: {decision}")

    # --- SIMULATED secondary metrics (directionally consistent with the primary result) ---
    secondary_defs = {
        "checkout_abandonment_rate": (0.061, -0.012),   # lower is better; simulate a reduction
        "cancellation_rate": (0.032, -0.009),            # lower is better
        "repeat_order_rate_30d": (0.41, 0.021),          # higher is better
        "eta_accuracy_within_stated_range_pct": (0.71, 0.14),  # higher is better -- the mechanism
    }
    print("\n=== SIMULATED secondary metrics ===")
    secondary_rows = []
    for name, (base, delta) in secondary_defs.items():
        x_c = rng.binomial(n_control, base)
        x_t = rng.binomial(n_treatment, base + delta)
        r = two_prop_ztest(x_c, n_control, x_t, n_treatment)
        secondary_rows.append((name, r))
        print(f"  {name}: control={r['p1']:.4f} treatment={r['p2']:.4f} "
              f"lift={r['abs_lift']*100:+.2f}pp p={r['p_value']:.2e}")

    # --- SIMULATED guardrails: should show NO material harm ---
    guardrail_defs = {
        "restaurant_cancellation_rate": (0.021, 0.0009),        # tiny, non-significant nudge
        "delivery_partner_wait_time_min": (6.2, 0.15),          # tiny, treated as a rate proxy below
        "support_ticket_rate_per_1000_orders": (0.0084, -0.0006),  # slightly fewer tickets (fewer confused customers)
    }
    print("\n=== SIMULATED guardrails ===")
    guardrail_rows = []
    for name, (base, delta) in guardrail_defs.items():
        if name == "delivery_partner_wait_time_min":
            # continuous metric -- simulate via normal approx t-test instead of a proportion
            c = rng.normal(base, 1.8, size=2000)
            t = rng.normal(base + delta, 1.8, size=2000)
            tstat, p = stats.ttest_ind(c, t)
            guardrail_rows.append((name, base, base + delta, delta, p))
            print(f"  {name}: control={c.mean():.2f} treatment={t.mean():.2f} delta={delta:+.2f} p={p:.3f}")
        else:
            x_c = rng.binomial(n_control, base)
            x_t = rng.binomial(n_treatment, base + delta)
            r = two_prop_ztest(x_c, n_control, x_t, n_treatment)
            guardrail_rows.append((name, r["p1"], r["p2"], r["abs_lift"], r["p_value"]))
            print(f"  {name}: control={r['p1']:.4f} treatment={r['p2']:.4f} "
                  f"delta={r['abs_lift']:+.4f} p={r['p_value']:.3f}")

    import csv
    with open("output/tables/power_analysis.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["baseline_completion_rate", "mde_pp", "alpha", "power", "n_per_arm", "assumed_runtime_days"])
        w.writerow([BASELINE_COMPLETION_RATE, MDE_ABSOLUTE_PP, ALPHA, POWER, n_per_arm, runtime_days])

    with open("output/tables/primary_metric_result.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n_control", "n_treatment", "control_rate", "treatment_rate", "abs_lift_pp",
                     "rel_lift_pct", "z_statistic", "p_value", "ci95_low_pp", "ci95_high_pp", "decision"])
        w.writerow([n_control, n_treatment, round(primary["p1"], 4), round(primary["p2"], 4),
                     round(primary["abs_lift"] * 100, 3), round(primary["rel_lift"] * 100, 2),
                     round(primary["z"], 3), primary["p_value"], round(primary["ci_low"] * 100, 3),
                     round(primary["ci_high"] * 100, 3), decision])

    with open("output/tables/secondary_metrics.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "control_rate", "treatment_rate", "abs_lift_pp", "rel_lift_pct", "p_value"])
        for name, r in secondary_rows:
            w.writerow([name, round(r["p1"], 4), round(r["p2"], 4), round(r["abs_lift"] * 100, 3),
                         round(r["rel_lift"] * 100, 2), r["p_value"]])

    with open("output/tables/guardrail_metrics.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "control", "treatment", "delta", "p_value"])
        for row in guardrail_rows:
            w.writerow(row)

    print(f"\nFinal decision: {decision}")
