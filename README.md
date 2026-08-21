# Accounting/Tax Practice Acquisition Analyzer

A simple interactive, terminal-based analyzer for evaluating an accounting or
tax practice acquisition. It uses only Python's standard library.

## Architecture

- `acquisition_engine.py` is the stable, interface-independent business layer.
  It owns input/result models, validation, retention and financing calculations,
  owner economics, data-quality assessment, and deterministic scoring.
- `practice_cli.py` owns interactive questions and terminal report formatting.
- `practice_analyzer.py` is the backward-compatible executable/import facade.
  Existing commands and imports continue to work.

A future web application should import `acquisition_engine` directly, construct
`Practice`, `Financing`, and `TransitionAssessment` values, then call `analyze`,
`calculate_quality_score`, `calculate_transition_score`, and
`calculate_overall_score`. It must not reproduce those formulas in web code.

For a JSON/API boundary, use `web_interface.analyze_acquisition(request)`. It
accepts a decoded JSON dictionary and returns a JSON-serializable success result
or structured validation errors. It is framework-neutral and calls
`acquisition_engine` directly; no HTTP server or frontend framework is included.

Run it with:

```bash
python3 practice_analyzer.py
```

Run the tests with:

```bash
python3 run_tests.py
```

The runner discovers both the original regression tests and the structured
business-logic suite in `tests/`, then prints an explicit PASS/FAIL summary.
This includes 1,250 deterministic randomized acquisition scenarios using seed
`20260819`; a failure reports the seed, case number, and complete generated input..

## Calculation assumptions

- Services use a reusable category model containing a name, recurring flag,
  engagement count, revenue, and owner hours. The terminal
  flow includes nine accounting/tax defaults and permits custom categories.
- Engagement counts can overlap across services and are never treated as unique
  client relationships. Tax categories ask for return counts; bookkeeping and
  payroll ask for client engagements; other categories use the appropriate
  engagement/client terminology. Counts may remain Unknown while revenue still
  participates in the analysis, in which case average revenue per engagement is
  omitted. Service revenue must reconcile to total practice revenue, and the
  terminal flow resolves differences by adjusting one selected category rather
  than requiring all categories to be re-entered.
- One expected first-year post-acquisition retention rate represents the
  seller's existing book that successfully transfers. One ongoing annual rate
  begins in year 2 and compounds against the remaining acquired book. Both rates
  apply proportionally across every service category. The blank-input ongoing
  default is 95%, documented as a screening assumption rather than a fact.
- Annual owner hours are optional by service and default to Unknown—never an
  imputed analyzer value. If all active-service hours are entered, retained
  hours decline with retained revenue by default and target compensation equals
  retained hours times hourly value. If any active-service hours are unknown,
  workload, owner compensation, residual ownership profit, labor-adjusted
  returns, and labor-adjusted payback are unavailable.
- The service analysis reports average revenue per engagement, revenue mix,
  revenue per owner hour, retained revenue, recurring/nonrecurring revenue,
  concentration, and the highest-revenue-per-hour services.
- Purchase terms are a four-part capital stack: buyer cash, SBA/other bank debt,
  seller debt, and maximum retention-contingent consideration. Those allocations
  must equal the asking price. Bank fees are additional initial buyer cash and do
  not count as purchase consideration.
- Bank and seller financing use separate equal-annual-payment amortization
  schedules. The report shows principal, interest, and remaining balances by
  year. A variable bank rate is held constant at the entered screening rate; the
  analyzer does not forecast rate changes or determine SBA eligibility.
- Each year's modeled earn-out installment equals its maximum annual installment
  times the remaining acquired-book percentage for that year. This is only a
  screening convention; actual agreement definitions may differ materially.
- Fixed operating costs remain constant. Staff/variable costs are split into a
  retention-sensitive share (80% default) and a fixed share. Operating cash flow
  subtracts both adjusted cost categories.
  Acquisition payments (bank debt, seller note, and earn-out) are displayed separately.
- Return on initial equity is year-one residual ownership profit after target
  owner compensation divided by the down payment.
- Target owner compensation is annual owner hours multiplied by the selected
  hourly value. It values the buyer's worker role and is not an accounting
  expense. Residual profit after this target represents the investor return.
- Effective revenue per owner hour is retained revenue divided by estimated
  annual owner hours.
- Total consideration is buyer cash plus bank and seller principal plus the
  actual earn-out. Total acquisition cash paid also includes bank fees and all
  modeled bank/seller interest.
- Initial equity payback starts with the down payment and accumulates residual
  profit after acquisition payments and target owner compensation. Total
  acquisition payback compares cumulative profit after target compensation but
  before acquisition payments with all acquisition cash paid, including note
  interest.
- Income taxes, capital expenditures, and changes in working capital are excluded.

## Acquisition quality score

The deterministic 1–100 score uses 13 components whose weights total 100%:
buyer-side valuation multiple (11%), recurring revenue (10%), revenue per client (3%),
revenue per owner hour (9%), residual ownership margin (11%), return on initial
equity (11%), total acquisition payback (9%), service-mix diversification (3%),
expected retention (12%), owner workload (5%), service economics/quality (4%),
low-fee/labor dependence (3%), and financing structure/risk (9%). The terminal report prints each metric, component
score, weight, weighted points, and the linear scoring anchors. Missing revenue-
per-hour or equity-return inputs receive a disclosed neutral score; a payback not
reached within the analysis horizon receives zero for that component.

The service-economics component is revenue-weighted and combines recurring
status (25%), average fee (37.5%), and revenue per owner hour (37.5%). Recurring
status alone cannot classify a service as higher value. The report discloses all
linear anchors and emphasizes that weights and thresholds are screening
heuristics—not objective valuation or appraisal standards.

Purchase multiple, revenue per client, and service-mix diversification use
bounded continuous piecewise-linear curves. Revenue per client is intentionally
a low-weight contextual signal. Service-mix diversification measures broad
service specialization, not actual client concentration.

The financing component blends fixed debt-service capacity, graduated seller
risk-sharing through contingent consideration, and initial buyer cash exposure.
It does not treat leverage as automatically bad or seller financing as
automatically good. The transition score likewise uses a graduated contingent-
consideration heuristic; a 30% earn-out does not receive a perfect score.

When owner hours are unknown, every owner-hours-dependent component is removed,
including revenue per owner hour, residual margin, owner-adjusted return and
payback, workload, service economics/quality, and labor-dependence. The remaining
known component weights are proportionally normalized to 100%. Unknown workload
therefore contributes neither positive nor negative points, and obtaining
reliable owner hours is added to diligence.

The closing acquisition analysis is assembled from fixed rules applied to these
metrics. It does not call an LLM or external API and does not add facts beyond
the entered assumptions.

Actual client concentration is tracked separately from service mix. The three
optional inputs are the largest single client, top five clients, and top ten
clients as percentages of acquired-book revenue, measured across unique client
relationships and all services. Blank values remain Unknown and are excluded
from scoring rather than estimated or penalized. Known values must satisfy
largest client <= top five <= top ten <= 100%.

The Actual client concentration factor has a 6% base weight, compared with 2%
for contextual Service mix diversification. Within the concentration factor,
the largest client is the primary signal (60%), supplemented by top five (25%)
and top ten (15%). If only some measures are known, those internal weights are
normalized over the known measures. Low-concentration anchors flatten near the
top to avoid false precision; risk increases progressively as reliance on a few
relationships becomes material. Financial factor weights remain a 100% base:
purchase multiple 10%, recurring revenue 9%, revenue/client 2%, revenue/owner
hour 9%, residual margin 11%, return on equity 11%, payback 9%, service mix 2%,
actual client concentration 6%, retention 11%, workload 5%, service economics
4%, low-fee/labor dependence 3%, and financing risk 8%. As before, unavailable
factors are removed and known weights are proportionally normalized to 100%.

## Transition and qualitative assessment

The analyzer separately scores seller transition length, tax-season support,
personal client introductions, post-closing availability, expected key-staff
retention, and retention-based consideration. Six
buyer-entered 1–5 ratings cover trust, seller commitment, cultural fit, client
desirability, practice organization, and confidence in seller information.

Transition components total 100% within their separate score. Buyer ratings are
explicitly subjective judgments, not financial
facts. The overall score is 70% Financial/Operational and 30% Transition &
Qualitative. The narrative flags unsupported retention assumptions—for example,
high expected retention combined with weak seller support—without changing the
user's assumption.

## Data quality and base-model scope

Entered values are accepted without repeated source questions. A blank input
first uses a context-derived default based on earlier answers when defensible
(for example, 20% of asking price for down payment, remaining unallocated
service revenue, or revenue-scaled costs). Otherwise it uses a visible generic
screening default. Owner hours are the deliberate exception: blank hours remain
Unknown and are never estimated. One closing question asks whether overall
information reliability is high, medium, or low. The report distinguishes
user-entered values, context-derived defaults, generic defaults, and unknowns;
adds material unknowns to diligence; and marks scores provisional for unknown or
low-reliability information. Missing data lowers confidence but does not
directly lower financial economics or component scores.

The base model includes only the existing book being purchased. It excludes
referrals, cross-selling, new services, unrelated clients, organic growth, fee
increases, and all other buyer-created revenue from cash flow, scoring, and
payback. Any later growth feature should appear separately as Potential Upside.
