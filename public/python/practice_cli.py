#!/usr/bin/env python3
"""Command-line questionnaire and terminal report for the acquisition analyzer."""

from __future__ import annotations

import math

from acquisition_engine import *

def ask_float(prompt: str, *, default: float | None = None, minimum: float = 0) -> float:
    while True:
        suffix = f" [{default:g}]" if default is not None else ""
        raw = input(f"{prompt}{suffix}: ").strip().replace(",", "").replace("$", "")
        if not raw and default is not None:
            return default
        try:
            value = float(raw)
            if value < minimum:
                raise ValueError
            return value
        except ValueError:
            print(f"Please enter a number of at least {minimum:g}.")


def ask_int(prompt: str, *, default: int | None = None, minimum: int = 0) -> int:
    while True:
        value = ask_float(prompt, default=default, minimum=minimum)
        if value.is_integer():
            return int(value)
        print("Please enter a whole number.")


def ask_choice(prompt: str, choices: tuple[int, ...], default: int) -> int:
    while True:
        choice = ask_int(prompt, default=default, minimum=min(choices))
        if choice in choices:
            return choice
        print(f"Please choose one of: {', '.join(map(str, choices))}.")


def ask_tracked_float(
    prompt: str,
    analyzer_default: float,
    records: list[AssumptionRecord],
    *,
    explanation: str = "",
    minimum: float = 0,
    entered_source: str = "User entered",
    default_source: str = "Generic screening default",
) -> float:
    if explanation:
        print(explanation)
    while True:
        raw = input(f"{prompt} [{analyzer_default:g}]: ").strip()
        if not raw or raw.lower() in ("unknown", "n/a", "na", "?"):
            value = analyzer_default
            source = default_source
            break
        try:
            value = float(raw.replace(",", "").replace("$", "").replace("%", ""))
            if value < minimum:
                raise ValueError
            source = entered_source
            break
        except ValueError:
            print(f"Please enter a number of at least {minimum:g}, or leave blank for the default.")
    records.append(AssumptionRecord(
        prompt, source, f"{value:g}", True,
        f"Verify {prompt.lower()} before relying heavily on the analysis."
        if source in ("Context-derived default", "Generic screening default") else "",
    ))
    return value


def ask_optional_unknown_float(
    prompt: str, records: list[AssumptionRecord], *, explanation: str = ""
) -> float | None:
    if explanation:
        print(explanation)
    while True:
        raw = input(f"{prompt} [optional; blank = Unknown]: ").strip()
        if not raw or raw.lower() in ("unknown", "n/a", "na", "?"):
            records.append(AssumptionRecord(
                prompt, "Unknown", "Unknown", True,
                f"Obtain reliable {prompt.lower()} before relying on owner-labor economics.",
            ))
            return None
        try:
            value = float(raw.replace(",", ""))
            if value < 0:
                raise ValueError
            records.append(AssumptionRecord(prompt, "Buyer estimate", f"{value:g}", True))
            return value
        except ValueError:
            print("Please enter a nonnegative number, or leave blank if unknown.")


def ask_optional_unknown_int(
    prompt: str, records: list[AssumptionRecord]
) -> int | None:
    while True:
        raw = input(f"{prompt} [optional; blank = Unknown]: ").strip()
        if not raw or raw.lower() in ("unknown", "n/a", "na", "?"):
            records.append(AssumptionRecord(
                prompt, "Unknown", "Unknown", True,
                f"Obtain the {prompt.lower()} to calculate average revenue per engagement.",
            ))
            return None
        try:
            value = int(raw.replace(",", ""))
            if value < 0:
                raise ValueError
            records.append(AssumptionRecord(prompt, "User entered", str(value), True))
            return value
        except ValueError:
            print("Please enter a nonnegative whole number, or leave blank if unknown.")


def ask_tracked_percent(
    prompt: str,
    analyzer_default: float,
    records: list[AssumptionRecord],
    *, explanation: str = "", default_source: str = "Generic screening default",
) -> float:
    while True:
        value = ask_tracked_float(
            prompt, analyzer_default, records, explanation=explanation,
            entered_source="Buyer estimate", default_source=default_source,
        )
        if value <= 100:
            return value / 100
        records.pop()
        print("Percentage cannot exceed 100%.")


def ask_tracked_yes_no(
    prompt: str, analyzer_default: bool, records: list[AssumptionRecord],
    *, default_source: str = "Generic screening default",
) -> bool:
    while True:
        raw = input(
            f"{prompt} [y/n; blank = default {'yes' if analyzer_default else 'no'}]: "
        ).strip().lower()
        if not raw or raw in ("unknown", "n/a", "na", "?"):
            value = analyzer_default
            source = default_source
            break
        if raw in ("y", "yes", "n", "no"):
            value = raw in ("y", "yes")
            source = "User entered"
            break
        print("Please enter y, n, or leave blank for the default.")
    records.append(AssumptionRecord(
        prompt, source, "Yes" if value else "No", True,
        f"Verify {prompt.lower()} before relying heavily on the analysis."
        if source in ("Context-derived default", "Generic screening default") else "",
    ))
    return value


def ask_information_reliability() -> str:
    print("\nHow reliable is the information provided for this practice?")
    print("  1. High — mostly seller records or verified documents")
    print("  2. Medium — mixture of seller information and buyer estimates")
    print("  3. Low — substantial information is estimated or unavailable")
    return ("High", "Medium", "Low")[ask_choice("Overall information reliability", (1, 2, 3), 2) - 1]


def ask_yes_no(prompt: str, default: bool = False) -> bool:
    suffix = "Y/n" if default else "y/N"
    while True:
        raw = input(f"{prompt} [{suffix}]: ").strip().lower()
        if not raw:
            return default
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("Please enter y or n.")


def ask_rating(prompt: str) -> int:
    while True:
        rating = ask_int(prompt, default=3, minimum=1)
        if rating <= 5:
            return rating
        print("Please enter a rating from 1 to 5.")


def ask_tracked_rating(prompt: str, records: list[AssumptionRecord]) -> int:
    while True:
        raw = input(f"{prompt} [3]: ").strip()
        if not raw:
            records.append(AssumptionRecord(
                prompt, "Generic screening default", "3/5", False
            ))
            return 3
        try:
            rating = int(raw)
            if 1 <= rating <= 5:
                records.append(AssumptionRecord(prompt, "Buyer estimate", f"{rating}/5", False))
                return rating
        except ValueError:
            pass
        print("Please enter a rating from 1 to 5, or press Enter for 3.")


def collect_transition_assessment(records: list[AssumptionRecord]) -> TransitionAssessment:
    print("\nTransition & Qualitative Assessment")
    print("Use current evidence and buyer judgment; missing seller information may use disclosed defaults.")
    transition_months = ask_tracked_float("Seller transition period (months)", 1, records)
    through_tax_season = ask_tracked_yes_no("Will seller stay through a tax season?", False, records)
    introductions = ask_tracked_yes_no("Will seller personally introduce key clients?", False, records)
    availability = ask_tracked_float("Seller post-closing availability (months)", 3, records)
    staff_retention = ask_tracked_percent("Expected key staff retention (%)", 50, records)
    print("\nBuyer ratings: 1 = very weak, 3 = neutral/uncertain, 5 = very strong")
    assessment = TransitionAssessment(
        transition_months,
        through_tax_season,
        introductions,
        availability,
        staff_retention,
        ask_tracked_rating("Seller rapport / trust", records),
        ask_tracked_rating("Seller commitment to transition success", records),
        ask_tracked_rating("Cultural fit with client base", records),
        ask_tracked_rating("Desirability of clients for your practice", records),
        ask_tracked_rating("Organization / quality of practice", records),
        ask_tracked_rating("Confidence in seller-provided information", records),
    )
    return assessment


def collect_service(
    name: str, recurring: bool, records: list[AssumptionRecord],
    remaining_unallocated_revenue: float, total_acquired_revenue: float,
) -> ServiceCategory:
    print(f"\n{name} ({'recurring' if recurring else 'nonrecurring'})")
    count_label = SERVICE_COUNT_LABELS.get(name, "Number of engagements/clients")
    print("Service counts may overlap with other categories and are not unique client relationships.")
    engagements = ask_optional_unknown_int(count_label, records)
    if engagements is not None:
        typical_fee = SERVICE_TYPICAL_REVENUE_PER_ENGAGEMENT.get(name, 1_500)
        derived_revenue = engagements * typical_fee
    else:
        share = SERVICE_REVENUE_SHARES.get(name, 0.10)
        derived_revenue = total_acquired_revenue * share
    revenue_default = min(max(0, remaining_unallocated_revenue), derived_revenue)
    revenue = ask_tracked_float(
        f"{name} annual revenue", revenue_default, records,
        default_source="Context-derived default",
    )
    hours = ask_optional_unknown_float(
        f"{name} annual owner hours", records,
        explanation=("Optional: enter owner hours only if you have a reasonable estimate. "
                     "Leave blank if unknown; the analyzer will not impute workload."),
    )
    return ServiceCategory(name, recurring, engagements, revenue, hours, 1.0, True, 1.0)


def reconcile_service_revenue(
    services: list[ServiceCategory], records: list[AssumptionRecord], total_revenue: float
) -> list[ServiceCategory]:
    active_indexes = [
        index for index, service in enumerate(services)
        if service.annual_revenue or service.engagements is not None
    ]
    if not active_indexes:
        active_indexes = [0]
    current_total = sum(service.annual_revenue for service in services)
    difference = total_revenue - current_total
    print(f"Current service revenue: {money(current_total)}; required total: {money(total_revenue)}.")
    print(f"Unallocated difference: {money(difference)}")
    for choice, index in enumerate(active_indexes, 1):
        print(f"  {choice}. {services[index].name}: {money(services[index].annual_revenue)}")
    selected = ask_int(
        "Category to adjust", default=len(active_indexes), minimum=1
    )
    while selected > len(active_indexes):
        print("Please choose a listed category.")
        selected = ask_int("Category to adjust", default=len(active_indexes), minimum=1)
    service_index = active_indexes[selected - 1]
    service = services[service_index]
    revised_default = max(0, service.annual_revenue + difference)
    temporary_records: list[AssumptionRecord] = []
    revised_revenue = ask_tracked_float(
        f"Revised annual revenue - {service.name}", revised_default,
        temporary_records, default_source="Context-derived default",
    )
    record_name = f"{service.name} annual revenue"
    for index in range(len(records) - 1, -1, -1):
        if records[index].name == record_name:
            replacement = temporary_records[0]
            records[index] = AssumptionRecord(
                record_name, replacement.source, replacement.value, True,
                replacement.uncertainty_note,
            )
            break
    services[service_index] = ServiceCategory(
        service.name, service.recurring, service.engagements, revised_revenue,
        service.annual_owner_hours, service.retention_rate,
        service.hours_follow_retention, service.ongoing_retention_rate,
    )
    return services


def collect_inputs() -> tuple[
    Practice, Financing, tuple[float, float, float], int, TransitionAssessment,
    tuple[AssumptionRecord, ...], str
]:
    print("\nPractice details")
    records: list[AssumptionRecord] = []
    revenue = ask_tracked_float(
        "Annual acquired-book revenue", 200_000, records, minimum=0.01,
        explanation="Enter only revenue from the existing book being purchased; exclude buyer-created growth.",
    )
    price = ask_tracked_float(
        "Asking price", revenue * 0.9, records, minimum=0.01,
        default_source="Context-derived default",
    )
    clients = int(ask_tracked_float(
        "Total client relationships", max(1, round(revenue / 1_000)), records, minimum=1,
        explanation="Relationships are unique clients; service engagement counts may overlap.",
        default_source="Context-derived default",
    ))

    print("\nService categories")
    print("Engagement counts may overlap across services and are not unique client counts.")
    services: list[ServiceCategory] = []
    for name, recurring in DEFAULT_SERVICE_CATEGORIES:
        if ask_yes_no(f"Enter {name}?"):
            remaining = revenue - sum(service.annual_revenue for service in services)
            services.append(collect_service(name, recurring, records, remaining, revenue))
        else:
            services.append(ServiceCategory(name, recurring, None, 0, None, 0))
    while ask_yes_no("Add a custom service category?"):
        name = input("Custom service name: ").strip()
        while not name:
            print("Service name cannot be blank.")
            name = input("Custom service name: ").strip()
        recurring = ask_yes_no("Is this service recurring?")
        remaining = revenue - sum(service.annual_revenue for service in services)
        services.append(collect_service(name, recurring, records, remaining, revenue))

    while not math.isclose(sum(service.annual_revenue for service in services), revenue, abs_tol=0.01):
        category_total = sum(service.annual_revenue for service in services)
        print(
            f"Service revenue totals {money(category_total)}; it must equal total practice "
            f"revenue of {money(revenue)}. Please revise the category revenues."
        )
        services = reconcile_service_revenue(services, records, revenue)

    print("\nPost-acquisition retention")
    retention_1 = ask_tracked_percent(
        "Expected first-year post-acquisition retention for the acquired book (%)", 85, records,
        explanation=("What percentage of the seller's existing book do you expect to successfully "
                     "transfer and retain during your first year of ownership? Consider seller transition "
                     "support, client loyalty, staff continuity, pricing differences, and client fit."),
    )
    ongoing_retention = ask_tracked_percent(
        "Ongoing annual acquired-book retention (%)", DEFAULT_ONGOING_RETENTION * 100, records,
        explanation=("Beginning after the initial ownership transition, what percentage of the remaining "
                     "acquired book do you expect to retain each year? This applies to the remaining book, "
                     "not original purchase-year revenue. The 95% blank-input default is a general "
                     "screening assumption, not a verified practice-specific fact."),
    )
    operating = ask_tracked_float(
        "Annual operating costs excluding staff and acquisition payments",
        revenue * 0.15, records, default_source="Context-derived default",
    )
    staff = ask_tracked_float(
        "Expected annual staff costs", revenue * 0.20, records,
        default_source="Context-derived default",
    )
    staff_variable_percentage = ask_tracked_percent(
        "Portion of staff/variable costs that declines with retained revenue (%)",
        DEFAULT_STAFF_VARIABLE_PERCENTAGE * 100, records,
        explanation=("The remaining portion is treated as fixed. The 80% screening default assumes most "
                     "staff workload adjusts with the acquired book, while some staffing cost remains fixed."),
    )
    owner_hourly_value = ask_tracked_float(
        "Hourly value of owner time", 75, records,
        explanation="This is target economic compensation for buyer labor, not an accounting expense.",
    )

    print("\nPurchase terms — capital stack")
    print("Allocate the maximum purchase price among buyer cash, bank/SBA debt, seller debt,")
    print("and retention-contingent consideration. Loan fees are outside the purchase-price allocation.")
    down = ask_tracked_float(
        "Down payment", price * 0.2, records,
        default_source="Context-derived default",
    )
    while down > price:
        print("Down payment cannot exceed the asking price.")
        down = ask_float("Down payment", default=price * 0.2)
    remaining = price - down
    bank = note = earnout = 0.0
    bank_rate = 0.0
    bank_years = 0
    bank_variable = False
    bank_fees = 0.0
    rate = 0.0
    note_years = earnout_years = 0
    if remaining:
        print(f"Remaining purchase price to allocate: {money(remaining)}")
        bank = ask_tracked_float(
            "SBA/bank loan amount", remaining * 0.60, records,
            default_source="Context-derived default",
        )
        while bank > remaining:
            print(f"Bank financing cannot exceed the {money(remaining)} unallocated amount.")
            bank = ask_float("SBA/bank loan amount", default=remaining * 0.60)
        remaining -= bank
        if bank:
            bank_rate = ask_tracked_float("Bank loan annual interest rate (%)", 8.5, records)
            bank_years = int(ask_tracked_float("Bank loan amortization term (years)", 10, records, minimum=1))
            bank_variable = ask_yes_no("Is the bank loan rate variable?", default=False)
            records.append(AssumptionRecord(
                "Bank loan rate type", "User entered", "Variable" if bank_variable else "Fixed", True
            ))
            bank_fees = ask_tracked_float(
                "Bank loan fees / closing costs", bank * 0.02, records,
                default_source="Context-derived default",
                explanation="These costs are added to initial buyer cash, not to purchase consideration.",
            )
        print(f"Remaining purchase price to allocate: {money(remaining)}")
        note = ask_tracked_float(
            "Seller-financed principal", remaining * 0.50, records,
            default_source="Context-derived default",
        )
        while note > remaining:
            print(f"Seller financing cannot exceed the {money(remaining)} unallocated amount.")
            note = ask_float("Seller-financed principal", default=remaining * 0.50)
        remaining -= note
        if note:
            rate = ask_tracked_float("Seller note annual interest rate (%)", 6, records)
            note_years = int(ask_tracked_float("Seller note term (years)", 5, records, minimum=1))
        earnout = ask_tracked_float(
            "Maximum retention-based earn-out", remaining, records,
            default_source="Context-derived default",
        )
        while earnout > remaining:
            print(f"Earn-out cannot exceed the {money(remaining)} unallocated amount.")
            earnout = ask_float("Maximum retention-based earn-out", default=remaining)
        remaining -= earnout
        if not math.isclose(remaining, 0, abs_tol=0.01):
            print(f"Unallocated consideration of {money(remaining)} is assigned to the earn-out.")
            earnout += remaining
        if earnout:
            print("The actual earn-out declines in direct proportion to retained revenue.")
            earnout_years = int(ask_tracked_float(
                "Earn-out measurement/payment term (years)", 3, records, minimum=1
            ))

    while True:
        horizon_value = ask_tracked_float(
            "Forward analysis horizon, 3-10 years", 7, records, minimum=3
        )
        if horizon_value.is_integer() and horizon_value <= 10:
            horizon = int(horizon_value)
            break
        records.pop()
        print("Analysis horizon must be a whole number from 3 to 10.")
    practice = Practice(
        revenue, price, clients, tuple(services), operating, staff, owner_hourly_value,
        staff_variable_percentage,
    )
    if practice.annual_owner_hours is None:
        for index, record in enumerate(records):
            if record.name == "Hourly value of owner time":
                records[index] = AssumptionRecord(
                    record.name, record.source, record.value, False, record.uncertainty_note
                )
                break
    financing = Financing(
        down, note, rate / 100, note_years, earnout, earnout_years,
        bank, bank_rate / 100, bank_years, bank_variable, bank_fees,
    )
    validate_terms(practice, financing)
    transition = collect_transition_assessment(records)
    information_reliability = ask_information_reliability()
    return (
        practice, financing, (retention_1, ongoing_retention, ongoing_retention),
        horizon, transition, tuple(records), information_reliability,
    )


def format_recovery(years: float | None, horizon: int) -> str:
    if years is None:
        return "Unavailable (owner hours unknown)"
    return f"{years:.1f} years" if math.isfinite(years) else f"Not recovered within {horizon} years"
def print_report(practice: Practice, financing: Financing,
                 expected: tuple[float, float, float], horizon: int,
                 transition: TransitionAssessment,
                 assumption_records: tuple[AssumptionRecord, ...],
                 information_reliability: str) -> None:
    revenue_multiple = practice.asking_price / practice.annual_revenue
    revenue_per_client = (
        practice.annual_revenue / practice.clients
        if practice.clients is not None and practice.clients > 0 else None
    )
    owner_hours_known = practice.annual_owner_hours is not None and practice.annual_owner_hours > 0

    print("\n" + "=" * 108)
    print("ACQUISITION SUMMARY")
    print("=" * 108)
    print(f"Purchase price / revenue       {revenue_multiple:.2f}x")
    print(f"Average revenue per client     {money(revenue_per_client) if revenue_per_client is not None else 'Unavailable (client count unknown)'}")
    print(f"Down payment                   {money(financing.down_payment)}")
    print(f"SBA/bank loan principal       {money(financing.bank_loan)}")
    print(f"Seller-financed principal      {money(financing.seller_note)}")
    print(f"Maximum earn-out               {money(financing.earnout_total)}")
    allocated = financing.down_payment + financing.bank_loan + financing.seller_note + financing.earnout_total
    print(f"Maximum stated consideration   {money(allocated)}")
    print(f"Capital-stack reconciliation   {money(allocated)} / {money(practice.asking_price)}")
    print(f"Allocation percentages         cash {financing.down_payment / practice.asking_price:.1%} | bank {financing.bank_loan / practice.asking_price:.1%} | seller {financing.seller_note / practice.asking_price:.1%} | contingent {financing.earnout_total / practice.asking_price:.1%}")
    print(f"Client relationships           {practice.clients if practice.clients is not None else 'Unknown'}")
    print("Base model scope               Existing acquired book only; no buyer-created growth")
    active_services = [service for service in practice.services if service.annual_revenue or service.engagements]
    print("\nSERVICE ANALYSIS")
    print("-" * 108)
    print(f"{'Service':<27} {'Returns/eng.':>12} {'Revenue':>12} {'Avg./eng.':>11} {'Rev. %':>7} {'Hours':>8} {'Ret.hrs':>8} {'Rev./hr':>10} {'Retained':>12}")
    for service in active_services:
        average_fee = money(service.average_revenue_per_engagement) if math.isfinite(service.average_revenue_per_engagement) else "N/A"
        revenue_per_hour = money(service.revenue_per_owner_hour) if math.isfinite(service.revenue_per_owner_hour) else "N/A"
        retained_hours = service.annual_owner_hours * expected[0] if service.annual_owner_hours is not None else None
        retained_revenue = service.annual_revenue * expected[0]
        hours_text = f"{service.annual_owner_hours:,.0f}" if service.annual_owner_hours is not None else "Unknown"
        retained_hours_text = f"{retained_hours:,.0f}" if retained_hours is not None else "Unknown"
        count_text = f"{service.engagements:,}" if service.engagements is not None else "Unknown"
        print(f"{service.name:<27.27} {count_text:>12} {money(service.annual_revenue):>12} {average_fee:>11} {service.annual_revenue / practice.annual_revenue:>6.1%} {hours_text:>8} {retained_hours_text:>8} {revenue_per_hour:>10} {money(retained_revenue):>12}")

    service_summary = summarize_services(practice)
    print("\nSERVICE MIX SUMMARY")
    print(f"Total service revenue          {money(service_summary.total_revenue)}")
    total_hours_text = f"{service_summary.total_owner_hours:,.0f}" if service_summary.total_owner_hours is not None else "Unknown"
    print(f"Total estimated owner hours   {total_hours_text}")
    print(f"Recurring revenue              {money(service_summary.recurring_revenue)} ({service_summary.recurring_revenue / practice.annual_revenue:.1%})")
    print(f"Nonrecurring revenue           {money(service_summary.nonrecurring_revenue)} ({service_summary.nonrecurring_revenue / practice.annual_revenue:.1%})")
    print(f"Largest service concentration  {service_summary.largest_service_share:.1%}")
    print(f"Top-three concentration        {service_summary.top_three_share:.1%}")
    print("Service counts are not summed; one client relationship may appear in multiple categories.")
    if service_summary.revenue_per_hour_ranking:
        ranking = ", ".join(
            f"{service.name} ({money(service.revenue_per_owner_hour)}/hr)"
            for service in service_summary.revenue_per_hour_ranking[:3]
        )
        print(f"Highest revenue per owner hour {ranking}")

    primary = analyze(practice, financing, expected, horizon)
    benchmark_inputs = list(dict.fromkeys([(0.90, 0.90, 0.90), (0.80, 0.80, 0.80), (0.70, 0.70, 0.70)]))
    scenarios = [primary] + [analyze(practice, financing, rates, horizon) for rates in benchmark_inputs]
    print("\nRETENTION SCENARIOS (year 1)")
    print("-" * 108)
    print(f"{'Retention':>9} {'Revenue':>13} {'Operating CF':>14} {'Acq. payments':>15} {'Net CF':>13} {'Consideration':>15}")
    for index, item in enumerate(scenarios):
        payments = item.annual_bank_payment + item.annual_debt_payment + item.annual_earnout_payment
        marker = "*" if index == 0 else " "
        print(f"{item.retention_rate:>8.0%}{marker} {money(item.retained_revenue):>13} {money(item.operating_cash_flow):>14} {money(payments):>15} {money(item.annual_cash_flow):>13} {money(item.total_consideration):>15}")

    print("\nEXPECTED CASE DETAILS (*)")
    print(f"Retention assumptions          {primary.retention_rate:.1%} year-1 transfer / {expected[1]:.1%} ongoing annually")
    print(f"Actual earn-out                {money(primary.actual_earnout)}")
    print(f"Total consideration paid      {money(primary.total_consideration)}")
    print(f"Bank interest, full term       {money(primary.total_bank_interest)}")
    print(f"Seller-note interest, full term {money(primary.total_seller_interest)}")
    print(f"Bank fees / closing costs      {money(financing.bank_fees)}")
    print(f"Total acquisition cash paid    {money(primary.total_acquisition_cash_paid)}")
    if owner_hours_known:
        print(f"Target owner compensation      {money(primary.owner_labor_value)}")
        print(f"Effective revenue/owner hour   {money(primary.effective_revenue_per_owner_hour)}")
    else:
        print("Target owner compensation      Unavailable (owner hours unknown)")
        print("Effective revenue/owner hour   Unavailable (owner hours unknown)")
    print(f"Operating CF before acq. pay.  {money(primary.operating_cash_flow)}")
    print(f"Fixed annual operating costs   {money(practice.annual_operating_costs)}")
    print(f"Base annual staff/variable cost {money(practice.annual_staff_costs)}")
    print(f"Retention-sensitive staff cost {practice.staff_variable_percentage:.0%}")
    print(f"Year 1 adjusted staff cost     {money(primary.years[0].staff_cost)}")
    print(f"Year 1 fixed debt service      {money(primary.annual_bank_payment + primary.annual_debt_payment)}")
    print(f"Year 1 acquisition payments    {money(primary.annual_bank_payment + primary.annual_debt_payment + primary.annual_earnout_payment)}")
    print(f"Cash available to owner        {money(primary.annual_cash_flow)}")
    initial_cash = financing.down_payment + financing.bank_fees
    coc_before = "N/A (no initial cash)" if not initial_cash else f"{primary.cash_on_cash_return:.1%}"
    print(f"Cash-on-cash before owner pay  {coc_before}")
    print(f"Residual ownership profit      {money(primary.economic_profit) if primary.economic_profit is not None else 'Unavailable (owner hours unknown)'}")
    coc_after = (
        "Unavailable (owner hours unknown)" if primary.cash_on_cash_after_owner_labor is None
        else "N/A (no initial cash)" if not initial_cash
        else f"{primary.cash_on_cash_after_owner_labor:.1%}"
    )
    print(f"Return on initial equity       {coc_after}")
    print(f"Initial equity payback         {format_recovery(primary.recovery_years, horizon)}")
    print(f"Total acquisition payback      {format_recovery(primary.total_acquisition_payback_years, horizon)}")

    if financing.earnout_total:
        maximum_installment = financing.earnout_total / financing.earnout_years
        print("\nRETENTION-BASED EARN-OUT METHOD")
        print("-" * 108)
        print(f"Maximum annual installment     {money(maximum_installment)}")
        print("Modeled payment each year = maximum annual installment × that year's remaining")
        print("acquired-book revenue as a percentage of original acquired-book revenue.")
        for year in range(1, financing.earnout_years + 1):
            retained = retained_services_for_year(practice, expected, year, False)
            year_retention = sum(item.retained_revenue for item in retained) / practice.annual_revenue
            payment = maximum_installment * year_retention
            print(f"Year {year}: {money(maximum_installment)} × {year_retention:.1%} = {money(payment)}")
        print("This is a screening convention only. Actual agreements may use different measurement")
        print("periods, floors, caps, exclusions, collection rules, or client-level calculations.")

    if financing.bank_loan or financing.seller_note:
        print("\nFIXED ACQUISITION DEBT SCHEDULE")
        print("-" * 108)
        print(f"{'Year':>4} {'Bank principal':>15} {'Bank interest':>14} {'Bank balance':>14} {'Seller principal':>17} {'Seller interest':>15} {'Seller balance':>15}")
        for year in primary.years:
            print(f"{year.year:>4} {money(year.bank_principal):>15} {money(year.bank_interest):>14} {money(year.bank_balance):>14} {money(year.seller_principal):>17} {money(year.seller_interest):>15} {money(year.seller_balance):>15}")
        print(f"Interest within {horizon}-year horizon: bank {money(sum(y.bank_interest for y in primary.years))}; seller {money(sum(y.seller_interest for y in primary.years))}.")
        if financing.bank_loan:
            rate_type = "variable" if financing.bank_variable_rate else "fixed"
            print(f"Bank loan modeled at {financing.bank_annual_interest_rate:.2%}, {rate_type}, over {financing.bank_years} years.")
            if financing.bank_variable_rate:
                print("Variable-rate payments are held at the entered screening rate; future rate changes are not forecast.")
        print("Bank/SBA and seller debt are modeled as fixed obligations payable despite lower retention.")
        print("This analyzer does not determine SBA eligibility or model lender underwriting requirements.")

    checkpoint_years = [year for year in (1, 3, 5, 7, 10) if year <= horizon]
    print("\nREMAINING ACQUIRED-BOOK REVENUE")
    print("-" * 108)
    for year in checkpoint_years:
        result = primary.years[year - 1]
        print(f"Year {year:<2}                         {money(result.retained_revenue):>14} ({result.retention_rate:.1%} of purchased book)")

    print("\nEXPECTED CASE CASH FLOW")
    print("-" * (156 if owner_hours_known else 94))
    if owner_hours_known:
        print(f"{'Year':>4} {'Retention':>9} {'Revenue':>13} {'Operating cash flow':>20} {'Acquisition payments':>21} {'Cash available to owner':>24} {'Target owner compensation':>27} {'Residual ownership profit':>27} {'Cumulative equity*':>20}")
        for year in primary.years:
            acquisition_payments = year.bank_payment + year.seller_note_payment + year.earnout_payment
            print(f"{year.year:>4} {year.retention_rate:>9.0%} {money(year.retained_revenue):>13} {money(year.operating_cash_flow):>20} {money(acquisition_payments):>21} {money(year.net_cash_flow):>24} {money(year.target_owner_compensation):>27} {money(year.economic_profit):>27} {money(year.cumulative_cash_flow):>20}")
    else:
        print(f"{'Year':>4} {'Retention':>9} {'Revenue':>13} {'Operating cash flow':>20} {'Acquisition payments':>21} {'Cash Available to Owner':>24}")
        for year in primary.years:
            acquisition_payments = year.bank_payment + year.seller_note_payment + year.earnout_payment
            print(f"{year.year:>4} {year.retention_rate:>9.0%} {money(year.retained_revenue):>13} {money(year.operating_cash_flow):>20} {money(acquisition_payments):>21} {money(year.net_cash_flow):>24}")

    print("\nOWNER WORKLOAD")
    print("-" * 108)
    if owner_hours_known:
        print(f"{'Service':<31}" + "".join(f"{'Year ' + str(year.year):>12}" for year in primary.years))
        for service_index, service in enumerate(practice.services):
            if service.annual_revenue or service.annual_owner_hours:
                values = [year.retained_services[service_index].retained_owner_hours for year in primary.years]
                print(f"{service.name:<31.31}" + "".join(f"{value:>12,.0f}" for value in values))
        totals = [sum(service.retained_owner_hours or 0 for service in year.retained_services) for year in primary.years]
        print(f"{'TOTAL RETAINED OWNER HOURS':<31}" + "".join(f"{value:>12,.0f}" for value in totals))
        print("Entered owner hours may be estimates and should be validated during diligence.")
    else:
        print("Owner hours: Unknown")
        print("The seller did not provide reliable owner-hour information. Owner-labor economics are")
        print("therefore excluded from this analysis; no workload or compensation estimate was imputed.")

    if owner_hours_known:
        print("\nOWNER-LABOR ECONOMICS EXPLAINED")
        print("-" * 108)
        print("Target Owner Compensation is the estimated economic value of the buyer's labor:")
        print("owner hours × the buyer's stated hourly value. It is not necessarily an actual salary")
        print("or accounting expense. It separates compensation for working from profit from owning.")
        print("Example: 600 hours × $100/hour = $60,000 of Target Owner Compensation.")
        print("\nResidual Ownership Profit is cash remaining after operating costs, acquisition payments,")
        print("and Target Owner Compensation. Example: $90,000 Cash Available to Owner less $60,000")
        print("of Target Owner Compensation leaves $30,000 of economic profit attributable to ownership.")
        print("\nCumulative Equity begins with the buyer's initial cash investment as a negative amount and")
        print("adds Residual Ownership Profit each year. For example, -$80,000 plus three annual residual")
        print("profits of $30,000 produces -$50,000, -$20,000, then +$10,000. Crossing zero indicates")
        print("that initial cash has been economically recovered after compensating the buyer's labor.")
        print("\n* Cumulative Equity begins with buyer cash plus bank fees and adds Residual Ownership Profit.")
        print("Initial equity payback uses residual profit after acquisition payments and target compensation.")
        print("Total acquisition payback compares cumulative profit before acquisition payments, but after target")
        print("owner compensation, with all acquisition cash paid (including seller-note interest).")
        print("Target owner compensation values the buyer's labor; it is not an accounting expense.")
        print("Entered owner hours decline proportionally with each service's retained revenue by default.")
        print("This assumption can be changed later if workload does not decline proportionally.")
    else:
        print("\nOwner labor economics were not calculated because reliable owner hours were not provided.")
        print("Cash Available to Owner represents cash flow after operating costs and acquisition payments,")
        print("but before assigning an economic cost to the buyer's labor.")
        print("\nIf owner hours are entered, the analyzer can additionally estimate:")
        print("  - Target Owner Compensation — the economic value of the buyer's work")
        print("  - Residual Ownership Profit — profit remaining after compensating the buyer for that work")
        print("  - Cumulative Equity — cumulative residual profit compared with initial buyer cash")
        print("  - Labor-adjusted returns and initial equity payback")
    print("Income taxes are excluded, as are capex and working capital.")
    print("Fixed operating costs remain constant. The selected variable portion of staff costs declines")
    print("with retained acquired-book revenue; the remaining staff cost stays fixed.")
    print("Operating/staff costs are shown separately from bank debt, seller-note, and earn-out payments.")
    print("Ongoing retention compounds against the remaining acquired book each year.")
    print("The base acquisition analysis evaluates only the existing book being purchased.")
    print("It gives no credit for referrals, cross-selling, new services, fee increases, organic growth,")
    print("unrelated new clients, or other buyer-created revenue. Any future upside belongs in a separate")
    print("Potential Upside analysis and is excluded from cash flow, scores, and payback calculations.")

    data_quality = assess_data_quality(assumption_records, information_reliability)
    print("\nDATA QUALITY / ASSUMPTION CONFIDENCE")
    print("-" * 108)
    print(f"Overall information reliability {data_quality.stated_reliability}")
    print("The reliability rating is the buyer's overall assessment, not an independently verified result.")
    print("Shares below are count-weighted across tracked important inputs, not financial sensitivity.")
    print(f"Values entered by user         {data_quality.user_entered_share:.1%}")
    print(f"Context-derived defaults       {data_quality.context_default_share:.1%}")
    print(f"Generic screening defaults     {data_quality.generic_default_share:.1%}")
    print("\nASSUMPTIONS USED / MISSING INFORMATION")
    important_estimates = tuple(
        record for record in assumption_records
        if record.important and record.source == "Buyer estimate"
    )
    if data_quality.uncertain_inputs:
        for record in data_quality.uncertain_inputs:
            if record.source == "Unknown":
                print(f"  - {record.name} was not provided and remains Unknown; no value was imputed.")
            elif record.source == "Context-derived default":
                print(f"  - {record.name}: {record.value} context-derived default.")
            else:
                print(f"  - {record.name}: {record.value} generic screening default.")
    for record in important_estimates:
        print(f"  - {record.name}: {record.value} is a forward-looking buyer estimate.")
    if not data_quality.uncertain_inputs and not important_estimates:
        print("  - No tracked important input required a default.")
    if data_quality.provisional:
        print("Acquisition scores are provisional because important information is missing or reliability is low.")
    print("Missing information reduces confidence only; it does not directly reduce the financial score.")
    if data_quality.context_default_share + data_quality.generic_default_share >= 0.50:
        print("Confidence note: this screening depends substantially on defaults; replace them as facts become available.")

    quality = calculate_quality_score(practice, financing, primary)
    print("\nFINANCIAL / OPERATIONAL SCORE")
    print("-" * 108)
    print(f"Overall score: {quality.score}/100 — {quality.band}")
    print(f"{'Component':<33} {'Weight':>8} {'Metric':>25} {'Score':>8} {'Points':>9}")
    for component in quality.components:
        print(f"{component.name:<33.33} {component.weight:>7.0f}% {component.value:>25.25} {component.score:>7.0f} {component.weighted_points:>9.1f}")
    print("Scoring anchors (linear between endpoints): multiple 0.65x=100/1.35x=0; revenue/client")
    print("$750=0/$2,500=100; revenue/hour $150=0/$400=100; residual margin -10%=0/20%=100;")
    print("equity return 0%=0/50%=100; payback 3yr=100/10yr=0; largest service 20%=100/70%=0;")
    print("retention 75%=0/95%=100; workload 250=100/700=0 hours per $100k. Service quality is a")
    print("revenue-weighted blend of recurrence (25%), average fee (37.5%), and revenue/hour (37.5%);")
    print("recurring status alone cannot produce a high score. Low-fee/labor exposure uses $400/engagement")
    print("and $175/owner-hour screening thresholds. Values outside anchors are capped.")
    print("Financing risk is 60% fixed-debt capacity (20% operating-CF burden=100, 70%=0), 25%")
    print("graduated contingent-risk sharing, and 15% initial-cash exposure. About 30% contingent")
    print("consideration scores 90—not 100—and excessive contingency also declines under this heuristic.")
    print("All weights, anchors, and thresholds are screening heuristics—not objective valuation standards,")
    print("market rules, appraisal conclusions, or substitutes for diligence and buyer judgment.")
    if not owner_hours_known:
        print("SCORING NOTE")
        print("Owner workload, revenue per owner hour, owner-labor-adjusted profitability and returns,")
        print("labor-adjusted payback, and labor-dependent service factors were excluded because reliable")
        print("owner-hour information was unavailable. Remaining financial factors were proportionally")
        print("reweighted to 100%; unknown hours received neither a positive nor negative score.")

    transition_quality = calculate_transition_score(practice, financing, transition)
    print("\nTRANSITION & QUALITATIVE SCORE")
    print("-" * 108)
    print(f"Transition score: {transition_quality.score}/100 — {transition_quality.band}")
    print(f"{'Component':<33} {'Weight':>8} {'Input':>25} {'Score':>8} {'Points':>9}")
    for component in transition_quality.components:
        print(f"{component.name:<33.33} {component.weight:>7.0f}% {component.value:>25.25} {component.score:>7.0f} {component.weighted_points:>9.1f}")
    print("Objective transition inputs and buyer ratings are scored separately from financial facts.")
    print("The 1–5 ratings reflect buyer judgment and should not be read as measured financial data.")

    overall_score = calculate_overall_score(quality.score, transition_quality.score)
    print("\nOVERALL ACQUISITION SCORE")
    print("-" * 108)
    print("Weighting: 70% Financial / Operational + 30% Transition & Qualitative")
    print(f"Calculation: ({quality.score} × 70%) + ({transition_quality.score} × 30%) = {overall_score}/100")
    print(f"Overall interpretation: {quality_band(overall_score)}")
    if data_quality.provisional:
        print("Status: PROVISIONAL — important inputs rely on disclosed analyzer defaults.")

    print("\nACQUISITION ANALYSIS")
    print("-" * 108)
    if quality.strengths:
        print("Attractive: " + "; ".join(quality.strengths) + ".")
    else:
        print("Attractive: No scoring component is clearly strong based on the entered assumptions.")
    if quality.concerns:
        print("Concerning: " + "; ".join(quality.concerns) + ".")
    else:
        print("Concerning: No scoring component falls in the weakest range, though diligence is still required.")
    if transition_quality.strengths:
        print("Transition support: " + "; ".join(transition_quality.strengths) + ".")
    if transition_quality.concerns:
        print("Transition concerns: " + "; ".join(transition_quality.concerns) + ".")
    if owner_hours_known:
        retained_hours = sum(service.retained_owner_hours or 0 for service in primary.years[0].retained_services)
        print(f"Economics: year 1 provides {money(primary.annual_cash_flow)} before target owner compensation and {money(primary.economic_profit)} of residual ownership profit after valuing {retained_hours:,.0f} retained owner hours at {money(practice.owner_hourly_value)}/hour.")
    else:
        print(f"Economics: year 1 provides {money(primary.annual_cash_flow)} before owner compensation. Residual ownership profit and labor-adjusted returns are unavailable because owner hours are unknown.")
    recurring_share = summarize_services(practice).recurring_revenue / practice.annual_revenue
    print(f"Service mix and retention: recurring services are {recurring_share:.1%} of revenue; practice-wide year-1 retention is {primary.retention_rate:.1%} and is applied proportionally across services. Engagement overlap means this is not a unique-client retention measure.")
    transition_support_score = sum(
        component.weighted_points for component in transition_quality.components[:6]
    ) / sum(component.weight for component in transition_quality.components[:6]) * 100
    if primary.retention_rate >= 0.90 and transition_support_score < 60:
        print("Retention consistency warning: expected year-1 retention is very high, but objective transition support scores below 60. The retention assumption has not been changed; validate the gap.")
    if primary.retention_rate >= 0.90 and transition.seller_commitment <= 2:
        print("Retention consistency warning: very high expected retention conflicts with a weak seller-transition commitment rating.")
    fixed_debt_service = primary.annual_bank_payment + primary.annual_debt_payment
    financing_burden = (fixed_debt_service + primary.annual_earnout_payment) / primary.operating_cash_flow if primary.operating_cash_flow > 0 else math.inf
    burden_text = f"{financing_burden:.1%} of year-1 operating cash flow" if math.isfinite(financing_burden) else "not measurable because operating cash flow is nonpositive"
    fixed_share = (financing.bank_loan + financing.seller_note) / practice.asking_price
    contingent_share = financing.earnout_total / practice.asking_price
    if contingent_share >= 0.20:
        risk_text = "Meaningful consideration is retention-contingent, so the seller shares some transfer risk."
    elif fixed_share >= 0.60:
        risk_text = "Most deferred consideration is fixed debt, placing substantial retention risk on the buyer."
    else:
        risk_text = "The structure provides limited retention-contingent downside protection."
    print(f"Financing: fixed annual debt service is {money(fixed_debt_service)}; total year-1 acquisition payments consume {burden_text}. {risk_text}")
    print(f"Fixed obligations are {fixed_share:.1%} of price and retention-contingent consideration is {contingent_share:.1%}; total acquisition payback is {format_recovery(primary.total_acquisition_payback_years, horizon)}.")
    if primary.economic_profit is None:
        price_view = "The asking price cannot be fully assessed against owner-labor-adjusted economics until reliable owner hours are obtained."
    elif quality.score >= 70 and primary.economic_profit > 0:
        price_view = "The asking price appears supportable under the entered assumptions, but only if retention, hours, and normalized costs are validated."
    elif primary.economic_profit <= 0:
        price_view = "The asking price is not supported by positive residual ownership profit under the entered assumptions."
    else:
        price_view = "The asking price has mixed support from the entered economics and should be negotiated or validated with stronger evidence."
    print("Price: " + price_view)
    print("Priority diligence:")
    priority_items = quality.investigation_items[:2] + transition_quality.investigation_items[:2]
    ordered_uncertainties = sorted(
        data_quality.uncertain_inputs, key=lambda record: record.source != "Unknown"
    )
    default_items = tuple(
        record.uncertainty_note for record in ordered_uncertainties if record.uncertainty_note
    )
    if not owner_hours_known:
        priority_items = tuple(
            item for item in priority_items if "owner hours" not in item.lower()
        )
    combined_items = list(dict.fromkeys(default_items + priority_items))[:4]
    for item in combined_items:
        print(f"  - {item}")


def main() -> None:
    print("Accounting/Tax Practice Acquisition Analyzer")
    print("Core question: What are the economics of the book of business I am actually paying")
    print("to acquire, before giving myself credit for growth I may create afterward?")
    practice, financing, expected, horizon, transition, records, reliability = collect_inputs()
    print_report(practice, financing, expected, horizon, transition, records, reliability)


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")

