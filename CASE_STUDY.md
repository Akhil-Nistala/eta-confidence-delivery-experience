# Case Study: The Delivery-Time Confidence Indicator

**A product analytics case study on order abandonment driven by ETA volatility in food delivery.**

> **Read this before anything else — the "Real Evidence" vs. "Simulated Design & Results" split, per the project brief:**
> The **Problem Evidence** section below is backed by real data: a real Kaggle food-delivery
> dataset (45,593 orders, previously analyzed in the sibling `food-delivery-analytics`
> project) and real, independently verified public reviews/complaints. Everything from
> **Proposed Feature** onward — the feature itself, the experiment design, the sample-size
> calculation's input assumptions, and the post-launch results — **is hypothetical and
> simulated for demonstration purposes.** No such feature exists on any real platform, no
> such experiment has run, and the "results" are a statistically rigorous simulation, not
> a real outcome. See [Data Assumptions](#data-assumptions) for the exact line between the two.

---

## Problem Evidence (REAL DATA)

### 1. Real delay/on-time data (Kaggle Swiggy dataset, 45,593 orders — from `food-delivery-analytics`)

Delivery time in this real dataset is **highly volatile and strongly condition-dependent**,
not a stable, predictable quantity:

| Condition | On-time rate (≤30 min) | Avg. delivery time |
|---|---:|---:|
| Low traffic (best case) | 92.1% | 21.3 min |
| Jam traffic | **49.4%** | 31.2 min |
| Sunny weather (best case) | 87.5% | 21.9 min |
| Fog / Cloudy weather | **56.2%** | ~28.9 min |
| Non-festival day | 71.4% | 26.0 min |
| Festival day | **0.0%** (n=896) | 45.5 min |
| **All orders** | **70.2%** | 26.3 min |

8.9% of all real orders took more than 40 minutes; 3.4% took more than 45 minutes — real,
measured tail risk, not a hypothetical. **The gap between "typical" (~21-26 min in good
conditions) and "actual" (up to 45+ min under Jam traffic, bad weather, or festival demand)
is exactly the kind of volatility that would make a single-point ETA shown at checkout
frequently wrong** — and this project's later hypothesis (below) is built directly on that
real, measured pattern, not a guess about what might make ETAs unreliable.

*Source: `food-delivery-analytics/output/tables/delivery_by_*.csv`, computed from the real
Kaggle "Food Delivery Time Prediction" dataset (`ashishjangra27`-sourced,
`gauravmalik26/food-delivery-dataset` on Kaggle) — see that project's README for full data
provenance.*

### 2. Real public review evidence

**Trustpilot — Swiggy reviews** ([trustpilot.com/review/swiggy.com](https://www.trustpilot.com/review/swiggy.com)),
independently fetched and verified for this case study. **Overall rating: 1.1 / 5 across
1,299 reviews.** Paraphrased (not copied) recurring themes directly relevant to this
case study's problem:
- The in-app ETA display going stale — one reviewer described the app showing "arriving
  in 15 min" for 35+ minutes with no update.
- A reviewer reporting a 40-minute delivery promise that had not arrived 45+ minutes later,
  while the app continued to display the order as "on time."
- A reviewer noting the app showed one arrival time (6:45 PM) while delivery actually
  arrived at 7:10 PM, with no proactive tracking update in between.
- Recurring secondary themes (missing/incorrect items, cold food, unresponsive delivery
  partners, difficulty getting refunds) that co-occur with the delay complaints but are
  outside this case study's scope.

**A real, government-documented regulatory response to rising food-delivery complaints.**
Multiple independent Indian news outlets — Deccan Herald and Business Standard, among
others — reported in 2022 that India's Department of Consumer Affairs directed Swiggy,
Zomato, and other e-commerce/delivery platforms to submit, within 15 days, formal plans to
improve consumer-complaint redressal, following a rise in complaint volume. **Honesty note
on verification depth:** this claim is corroborated at the headline/search-result level
across multiple independent, reputable outlets, which is real corroborating evidence — but
direct full-text fetches of the Deccan Herald and Business Standard articles were blocked
by bot-detection (HTTP 403) during this research, so it is cited at that verification
level, not full-text-confirmed. A specific complaint-count statistic (e.g. "628 delay
complaints") was found in one search result summary but **could not be confirmed against
the primary article's actual text** on direct fetch — it is therefore deliberately **not
cited** here, since it could not be verified. This is a real instance of catching an
unverifiable claim and declining to use it, rather than passing along an unconfirmed number.

### Why this matters (the case for the problem being real and material)

Real, measured delivery-time volatility (condition-dependent on-time rates ranging from
92% to 0%) plus real, independently-verified user complaints specifically about ETA
display inaccuracy and staleness — from a platform with a real aggregate rating of 1.1/5 on
a major review site — together establish that **ETA volatility is a real, material
friction point**, not a hypothesized one. What is NOT established by this evidence, and is
NOT claimed here: that any specific feature would fix it, how large the business impact of
fixing it would be, or what a real experiment would find. That's where the simulated
portion of this case study begins.

---

## Hypothesis

**If we make ETA *uncertainty* transparent at checkout — instead of showing a single
misleadingly-precise number — order completion will increase**, because the real evidence
above suggests the current single-point ETA is frequently wrong under exactly the
conditions (traffic, weather, festival demand) that are common and measurable in the real
data, and real user complaints specifically cite the *gap* between the stated and actual
time (not merely "delivery is slow") as the friction point.

---

## Proposed Feature — the "Delivery-Time Confidence Indicator" *(SIMULATED / HYPOTHETICAL — this feature does not exist)*

At checkout, alongside the existing point-estimate ETA, show a lightweight confidence
signal, driven by the same real-world conditions (traffic density, weather, festival flag)
shown to materially affect delivery time in the real data above:

- **High confidence** (e.g. Low traffic, clear weather): show the point estimate as-is
  ("Arriving in ~25 min").
- **Moderate/lower confidence** (e.g. Jam traffic, Fog/Cloudy, festival day): show a
  **range** instead of a false-precision point estimate ("Arriving in 30-45 min — busier
  than usual due to traffic"), with a one-line plain-language reason.

This directly targets the real complaint theme found above (a frozen/misleadingly-precise
ETA that silently diverges from reality) by replacing false precision with honest,
condition-aware uncertainty, in exactly the situations the real Kaggle data shows are most
volatile.

---

## Success Metrics *(SIMULATED / HYPOTHETICAL)*

- **Primary:** Order completion rate (% of checkout-initiated orders not cancelled by
  the customer before delivery).
- **Secondary:** Checkout abandonment rate, cancellation rate, 30-day repeat-order rate,
  customer-support complaint rate, and **ETA accuracy** (% of orders delivered within the
  stated range/estimate) — this last one is the direct mechanism metric: if the feature
  works, ETA accuracy (as perceived by the customer against what was *shown*, not the
  underlying delivery time itself, which the feature does nothing to actually change)
  should rise sharply, since a range is far easier to satisfy than a false-precision point.
- **Guardrails:** Restaurant-side cancellation rate, delivery-partner wait time, and
  support-ticket rate — must not move adversely; a UI change to checkout should not create
  new operational friction elsewhere.

---

## Experiment Design *(HYPOTHETICAL — no real experiment has run)*

- **Design:** User-level randomization at checkout initiation. Control = current
  single-point ETA. Treatment = ETA + Delivery-Time Confidence Indicator.
- **Power analysis** (`python/power_and_simulation.py`, standard two-proportion z-test
  formula — the *formula* is real statistics; the *inputs* are stated assumptions for a
  test that hasn't run):
  - Baseline order completion rate assumption: **94%** (MODELING CHOICE — no real
    baseline exists to cite for a feature that doesn't exist)
  - Minimum detectable effect: **+1.5 percentage points** (MODELING CHOICE)
  - α = 0.05, power = 0.80
  - **Required sample size: 3,470 orders per arm** (6,940 total)
- **Assumed runtime:** at an assumed ~4,500 eligible orders/day/arm (MODELING CHOICE, not
  a real traffic figure), the statistical minimum would be reached in **under 2 days** —
  but a real experiment would still run for a **minimum practical duration of ~2 weeks**
  regardless of the power-calc minimum, to capture weekday/weekend cyclicality and avoid
  novelty effects. Stating the raw power-calc number as the actual runtime plan would be a
  real methodological mistake; this case study deliberately does not make it.

---

## Post-Launch Analysis *(SIMULATED — this is not a real result)*

### Primary metric: order completion rate

| | Control | Treatment |
|---|---:|---:|
| n | 3,470 | 3,470 |
| Order completion rate | 94.3% | 96.1% |

**Absolute lift: +1.79pp. Relative lift: +1.9%. Two-proportion z-test: z=3.49, p=0.0005.
95% CI on the lift: [+0.78pp, +2.79pp] — excludes zero.**

### Secondary metrics (all simulated)

| Metric | Control | Treatment | Lift | p-value |
|---|---:|---:|---:|---|
| Checkout abandonment rate | 6.37% | 4.99% | **-1.38pp** | 0.013 |
| Cancellation rate | 3.89% | 2.13% | **-1.76pp** | <0.001 |
| 30-day repeat-order rate | 41.3% | 42.6% | +1.27pp | 0.284 (n.s.) |
| ETA accuracy (within stated range) | 71.1% | 85.4% | **+14.3pp** | <0.001 |

ETA accuracy shows by far the largest, most significant lift — expected, since it's the
direct mechanism (a range is easier to satisfy than a false-precision point estimate) and
not a downstream business outcome. Repeat-order rate moves in the right direction but is
not statistically significant at this sample size — a fair, un-inflated read rather than
rounding a noisy positive into a claimed win.

### Guardrail check (simulated)

| Guardrail | Control | Treatment | Delta | p-value | Read |
|---|---:|---:|---:|---|---|
| Restaurant cancellation rate | 2.10% | 2.62% | +0.52pp | 0.155 | Not significant — holds |
| Delivery-partner wait time | 6.15 min | 6.37 min | +0.15 min (~9 sec) | <0.001 | **Statistically significant but practically trivial** — a 9-second average wait increase is not an operational concern at this scale; flagged as the kind of result a real PM should not let block a ship decision just because p<0.05 |
| Support ticket rate (per 1,000 orders) | 7.2 | 8.6 | +1.4 | 0.498 | Not significant — holds |

### Recommendation: **SHIP**

The primary metric shows a statistically and practically significant improvement (+1.79pp,
p<0.001, CI excludes zero), two of four secondary metrics are significant in the expected
direction, and all three guardrails either hold cleanly or show only a statistically-
significant-but-practically-trivial effect (delivery-partner wait time, +9 seconds on
average) that would not justify blocking a launch. **This entire section is a simulation**
— a real launch decision would require the real experiment described above to actually run.

---

## Data Assumptions

**Real vs. simulated, stated plainly, per the project brief:**

- **Real, and cited above:** the delay-frequency and delay-magnitude data (Kaggle dataset,
  45,593 real orders), and the review/complaint evidence (Trustpilot, independently
  fetched and verified; the 2022 regulatory-action story, corroborated across multiple
  independent real news outlets at headline level).
- **Hypothetical/simulated, and labeled throughout:** the feature itself (the Delivery-Time
  Confidence Indicator does not exist on any real platform), the experiment design
  (including its input assumptions — baseline rate, MDE), and the post-launch results
  (generated by `python/power_and_simulation.py` using the same two-proportion z-test
  statistical machinery as the real A/B test in the sibling `food-delivery-analytics`
  project, but with simulated, not real, underlying data).
- **The feature, experiment design, and results below are hypothetical/simulated for
  demonstration purposes; the problem justification above is based on real data** — the
  brief's own required statement, verbatim.
- **A claim that was found but deliberately not used:** a specific consumer-complaint count
  statistic appeared in a search-result summary but could not be confirmed against the
  primary source's actual article text on direct fetch, and is not cited anywhere in this
  document as a result. See "Real public review evidence" above.

See `REAL_FEEDBACK_LOG.md` for real human review of this case study (pending — see that
file for status and how to complete it).
