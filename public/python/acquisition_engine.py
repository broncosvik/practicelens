#!/usr/bin/env python3
"""Stable, interface-independent business logic for acquisition analysis.

This module performs no prompting and prints no reports. CLI and future web
interfaces should construct its input models and call its pure calculation and
scoring functions.
"""

from __future__ import annotations

from dataclasses import dataclass
import math


DEFAULT_ONGOING_RETENTION = 0.95
DEFAULT_STAFF_VARIABLE_PERCENTAGE = 0.80
OVERALL_FINANCIAL_WEIGHT = 0.70
OVERALL_TRANSITION_WEIGHT = 0.30


@dataclass(frozen=True)
class ServiceCategory:
    name: str
    recurring: bool
    engagements: int | None
    annual_revenue: float
    annual_owner_hours: float | None
    retention_rate: float
    hours_follow_retention: bool = True
    ongoing_retention_rate: float = 0.95

    @property
    def average_revenue_per_engagement(self) -> float:
        return (
            self.annual_revenue / self.engagements
            if self.engagements is not None and self.engagements > 0 else math.inf
        )

    @property
    def revenue_per_owner_hour(self) -> float:
        return (
            self.annual_revenue / self.annual_owner_hours
            if self.annual_owner_hours is not None and self.annual_owner_hours > 0 else math.inf
        )

    @property
    def expected_retained_revenue(self) -> float:
        return self.annual_revenue * self.retention_rate


@dataclass(frozen=True)
class ServiceSummary:
    total_revenue: float
    total_owner_hours: float | None
    recurring_revenue: float
    nonrecurring_revenue: float
    largest_service_share: float
    top_three_share: float
    revenue_per_hour_ranking: tuple[ServiceCategory, ...]


@dataclass(frozen=True)
class RetainedService:
    name: str
    retention_rate: float
    retained_revenue: float
    retained_owner_hours: float | None


DEFAULT_SERVICE_CATEGORIES = (
    ("Individual tax returns", True),
    ("Business tax returns", True),
    ("Nonprofit tax returns", True),
    ("Bookkeeping", True),
    ("Payroll", True),
    ("Tax planning/advisory", True),
    ("Tax representation/notices", False),
    ("Other recurring services", True),
    ("Other nonrecurring services", False),
)

SERVICE_COUNT_LABELS = {
    "Individual tax returns": "Number of individual returns",
    "Business tax returns": "Number of business returns",
    "Nonprofit tax returns": "Number of nonprofit returns",
    "Bookkeeping": "Number of client engagements",
    "Payroll": "Number of client engagements",
    "Tax planning/advisory": "Number of engagements/clients",
    "Tax representation/notices": "Number of engagements",
    "Other recurring services": "Number of client engagements",
    "Other nonrecurring services": "Number of engagements",
}

SERVICE_REVENUE_SHARES = {
    "Individual tax returns": 0.45,
    "Business tax returns": 0.30,
    "Nonprofit tax returns": 0.05,
    "Bookkeeping": 0.35,
    "Payroll": 0.15,
    "Tax planning/advisory": 0.15,
    "Tax representation/notices": 0.05,
    "Other recurring services": 0.10,
    "Other nonrecurring services": 0.05,
}

SERVICE_TYPICAL_REVENUE_PER_ENGAGEMENT = {
    "Individual tax returns": 750,
    "Business tax returns": 2_000,
    "Nonprofit tax returns": 1_800,
    "Bookkeeping": 6_000,
    "Payroll": 3_000,
    "Tax planning/advisory": 2_000,
    "Tax representation/notices": 1_500,
    "Other recurring services": 1_500,
    "Other nonrecurring services": 1_000,
}


@dataclass(frozen=True)
class Practice:
    annual_revenue: float
    asking_price: float
    clients: int | None
    services: tuple[ServiceCategory, ...]
    annual_operating_costs: float
    annual_staff_costs: float
    owner_hourly_value: float
    staff_variable_percentage: float = DEFAULT_STAFF_VARIABLE_PERCENTAGE
    largest_client_revenue_share: float | None = None
    top_5_client_revenue_share: float | None = None
    top_10_client_revenue_share: float | None = None

    @property
    def annual_owner_hours(self) -> float | None:
        active = [service for service in self.services if service.annual_revenue or service.engagements]
        if any(service.annual_owner_hours is None for service in active):
            return None
        return sum(service.annual_owner_hours or 0 for service in active)


@dataclass(frozen=True)
class Financing:
    down_payment: float
    seller_note: float
    annual_interest_rate: float
    note_years: int
    earnout_total: float  # maximum, paid at 100% retention
    earnout_years: int
    bank_loan: float = 0.0
    bank_annual_interest_rate: float = 0.0
    bank_years: int = 0
    bank_variable_rate: bool = False
    bank_fees: float = 0.0


@dataclass(frozen=True)
class DebtPayment:
    year: int
    payment: float
    principal: float
    interest: float
    ending_balance: float


@dataclass(frozen=True)
class YearResult:
    year: int
    retention_rate: float
    retained_revenue: float
    staff_cost: float
    operating_cash_flow: float
    seller_note_payment: float
    seller_principal: float
    seller_interest: float
    seller_balance: float
    bank_payment: float
    bank_principal: float
    bank_interest: float
    bank_balance: float
    earnout_payment: float
    net_cash_flow: float
    target_owner_compensation: float | None
    economic_profit: float | None
    cumulative_cash_flow: float | None
    retained_services: tuple[RetainedService, ...]


@dataclass(frozen=True)
class Scenario:
    retention_rate: float
    retained_clients: float | None
    retained_revenue: float
    annual_debt_payment: float
    annual_bank_payment: float
    annual_earnout_payment: float
    annual_cash_flow: float
    equity_payback_years: float | None
    operating_cash_flow: float
    actual_earnout: float
    total_consideration: float
    total_acquisition_cash_paid: float
    cash_on_cash_return: float | None
    recovery_years: float | None
    owner_labor_value: float | None
    economic_profit: float | None
    effective_revenue_per_owner_hour: float | None
    cash_on_cash_after_owner_labor: float | None
    retention_rates: tuple[float, float, float]
    total_acquisition_payback_years: float | None
    total_seller_interest: float
    total_bank_interest: float
    years: tuple[YearResult, ...]


@dataclass(frozen=True)
class ScoreComponent:
    name: str
    weight: float
    score: float
    value: str

    def __post_init__(self) -> None:
        if not math.isfinite(self.score):
            raise ValueError("Score component must be finite.")
        object.__setattr__(self, "score", max(0.0, min(100.0, self.score)))

    @property
    def weighted_points(self) -> float:
        return self.weight * self.score / 100


@dataclass(frozen=True)
class QualityScore:
    score: int
    band: str
    components: tuple[ScoreComponent, ...]
    strengths: tuple[str, ...]
    concerns: tuple[str, ...]
    investigation_items: tuple[str, ...]


@dataclass(frozen=True)
class TransitionAssessment:
    seller_transition_months: float
    stays_through_tax_season: bool
    personal_client_introductions: bool
    post_closing_availability_months: float
    expected_key_staff_retention: float | None
    seller_rapport: int
    seller_commitment: int
    cultural_fit: int
    client_desirability: int
    practice_organization: int
    information_confidence: int


@dataclass(frozen=True)
class AssumptionRecord:
    name: str
    source: str  # User entered, Buyer estimate, Context-derived default, Generic screening default, Unknown
    value: str
    important: bool = True
    uncertainty_note: str = ""


@dataclass(frozen=True)
class DataQualityAssessment:
    stated_reliability: str
    user_entered_share: float
    context_default_share: float
    generic_default_share: float
    uncertain_inputs: tuple[AssumptionRecord, ...]
    provisional: bool


def annual_loan_payment(principal: float, annual_rate: float, years: int) -> float:
    """Return the annual payment for a fully amortizing loan."""
    if principal == 0:
        return 0.0
    if years <= 0:
        raise ValueError("Loan term must be greater than zero.")
    if annual_rate < 0:
        raise ValueError("Interest rate cannot be negative.")
    if annual_rate == 0:
        return principal / years
    factor = (1 + annual_rate) ** years
    return principal * annual_rate * factor / (factor - 1)


def amortization_schedule(principal: float, annual_rate: float, years: int) -> tuple[DebtPayment, ...]:
    """Return a conventional annual fully-amortizing debt schedule."""
    if principal == 0:
        return ()
    payment = annual_loan_payment(principal, annual_rate, years)
    balance = principal
    schedule = []
    for year in range(1, years + 1):
        interest = balance * annual_rate
        principal_paid = min(balance, payment - interest)
        actual_payment = principal_paid + interest
        balance = max(0.0, balance - principal_paid)
        schedule.append(DebtPayment(year, actual_payment, principal_paid, interest, balance))
    return tuple(schedule)


def money(value: float) -> str:
    return f"${value:,.0f}"


def validate_terms(practice: Practice, financing: Financing) -> None:
    values = (financing.down_payment, financing.bank_loan, financing.seller_note,
              financing.earnout_total, financing.bank_fees)
    if any(value < 0 for value in values):
        raise ValueError("Purchase term amounts cannot be negative.")
    allocated = (financing.down_payment + financing.bank_loan
                 + financing.seller_note + financing.earnout_total)
    if not math.isclose(allocated, practice.asking_price, abs_tol=0.01):
        raise ValueError(
            "Buyer cash, bank/SBA principal, seller principal, and maximum earn-out must total "
            f"the asking price ({money(allocated)} entered vs. {money(practice.asking_price)})."
        )
    if financing.seller_note and financing.note_years <= 0:
        raise ValueError("Seller note term must be greater than zero.")
    if financing.bank_loan and financing.bank_years <= 0:
        raise ValueError("Bank/SBA loan term must be greater than zero.")
    if financing.annual_interest_rate < 0 or financing.bank_annual_interest_rate < 0:
        raise ValueError("Interest rates cannot be negative.")
    if financing.earnout_total and financing.earnout_years <= 0:
        raise ValueError("Earn-out term must be greater than zero.")


def validate_practice(practice: Practice) -> None:
    if practice.annual_revenue <= 0:
        raise ValueError("Annual practice revenue must be greater than zero.")
    if practice.asking_price < 0:
        raise ValueError("Asking price cannot be negative.")
    if practice.clients is not None and practice.clients < 0:
        raise ValueError("Client relationships cannot be negative.")
    if practice.annual_operating_costs < 0 or practice.annual_staff_costs < 0:
        raise ValueError("Operating and staff costs cannot be negative.")
    category_revenue = sum(service.annual_revenue for service in practice.services)
    if not math.isclose(category_revenue, practice.annual_revenue, abs_tol=0.01):
        raise ValueError(
            "Service-category revenue must total annual practice revenue "
            f"({money(category_revenue)} entered vs. {money(practice.annual_revenue)})."
        )
    if practice.owner_hourly_value < 0:
        raise ValueError("Owner hourly value cannot be negative.")
    if not 0 <= practice.staff_variable_percentage <= 1:
        raise ValueError("Variable staff cost percentage must be between 0% and 100%.")
    concentration_values = (
        practice.largest_client_revenue_share,
        practice.top_5_client_revenue_share,
        practice.top_10_client_revenue_share,
    )
    if any(value is not None and not 0 <= value <= 1 for value in concentration_values):
        raise ValueError("Client concentration percentages must be between 0% and 100%.")
    known_concentrations = [value for value in concentration_values if value is not None]
    if any(left > right for left, right in zip(known_concentrations, known_concentrations[1:])):
        raise ValueError(
            "Client concentration must satisfy largest client <= top 5 clients <= top 10 clients."
        )
    for service in practice.services:
        if ((service.engagements is not None and service.engagements < 0)
                or service.annual_revenue < 0
                or (service.annual_owner_hours is not None and service.annual_owner_hours < 0)):
            raise ValueError("Service counts, revenue, and owner hours cannot be negative.")
        if not 0 <= service.retention_rate <= 1:
            raise ValueError("Service retention must be between 0% and 100%.")
        if not 0 <= service.ongoing_retention_rate <= 1:
            raise ValueError("Ongoing service retention must be between 0% and 100%.")


def summarize_services(practice: Practice) -> ServiceSummary:
    active = [service for service in practice.services if service.annual_revenue or service.engagements]
    by_revenue = sorted(active, key=lambda service: service.annual_revenue, reverse=True)
    recurring = sum(service.annual_revenue for service in practice.services if service.recurring)
    ranking = tuple(sorted(
        (service for service in active
         if service.annual_owner_hours is not None and service.annual_owner_hours > 0),
        key=lambda service: service.revenue_per_owner_hour,
        reverse=True,
    ))
    return ServiceSummary(
        sum(service.annual_revenue for service in practice.services),
        practice.annual_owner_hours,
        recurring,
        practice.annual_revenue - recurring,
        by_revenue[0].annual_revenue / practice.annual_revenue if by_revenue else 0,
        sum(service.annual_revenue for service in by_revenue[:3]) / practice.annual_revenue,
        ranking,
    )


def normalize_retention(retention: float | tuple[float, float, float]) -> tuple[float, float, float]:
    if isinstance(retention, (int, float)):
        rates = (retention, retention, retention)
    else:
        entered = tuple(retention)
        if len(entered) not in (2, 3):
            raise ValueError("Retention requires first-year and ongoing annual percentages.")
        if any(not 0 <= rate <= 1 for rate in entered):
            raise ValueError("First-year and ongoing retention must each be between 0% and 100%.")
        rates = (entered[0], entered[1], entered[1])
    if any(not 0 <= rate <= 1 for rate in rates[:2]):
        raise ValueError("First-year and ongoing retention must each be between 0% and 100%.")
    return rates


def retained_services_for_year(
    practice: Practice,
    retention_rates: tuple[float, float, float],
    year: int,
    use_category_year_1: bool,
) -> tuple[RetainedService, ...]:
    """Return service-level retention; this is the extension point for future paths."""
    retained = []
    for service in practice.services:
        if use_category_year_1:
            rate = service.retention_rate * service.ongoing_retention_rate ** (year - 1)
        else:
            rate = retention_rates[0] * retention_rates[1] ** (year - 1)
        retained.append(RetainedService(
            service.name,
            rate,
            service.annual_revenue * rate,
            (service.annual_owner_hours * rate if service.hours_follow_retention
             else service.annual_owner_hours)
            if service.annual_owner_hours is not None else None,
        ))
    return tuple(retained)


def analyze(practice: Practice, financing: Financing,
            retention: float | tuple[float, float, float],
            horizon: int | None = None,
            *, use_category_year_1: bool = False) -> Scenario:
    retention_rates = normalize_retention(retention)
    validate_practice(practice)
    validate_terms(practice, financing)
    if horizon is None:
        horizon = min(10, max(5, financing.note_years, financing.bank_years,
                              financing.earnout_years))
    if not 3 <= horizon <= 10:
        raise ValueError("Analysis horizon must be between 3 and 10 years.")

    seller_schedule = amortization_schedule(
        financing.seller_note, financing.annual_interest_rate, financing.note_years
    )
    bank_schedule = amortization_schedule(
        financing.bank_loan, financing.bank_annual_interest_rate, financing.bank_years
    )
    debt_payment = seller_schedule[0].payment if seller_schedule else 0.0
    bank_payment = bank_schedule[0].payment if bank_schedule else 0.0
    maximum_annual_earnout = (
        financing.earnout_total / financing.earnout_years if financing.earnout_total else 0.0
    )
    effective_retention_rates = list(retention_rates)
    if use_category_year_1:
        expected_revenue = sum(service.expected_retained_revenue for service in practice.services)
        effective_retention_rates[0] = expected_revenue / practice.annual_revenue
        effective_retention_rates[1] = sum(
            service.annual_revenue * service.ongoing_retention_rate
            for service in practice.services
        ) / practice.annual_revenue
        effective_retention_rates[2] = effective_retention_rates[1]
    earnout_schedule = []
    for year in range(1, financing.earnout_years + 1):
        service_results = retained_services_for_year(
            practice, retention_rates, year, use_category_year_1
        )
        book_retention = sum(item.retained_revenue for item in service_results) / practice.annual_revenue
        earnout_schedule.append(maximum_annual_earnout * book_retention)
    actual_earnout = sum(earnout_schedule)
    total_note_cash = sum(item.payment for item in seller_schedule)
    total_bank_cash = sum(item.payment for item in bank_schedule)
    total_consideration = financing.down_payment + financing.bank_loan + financing.seller_note + actual_earnout
    total_acquisition_cash = financing.down_payment + financing.bank_fees + total_bank_cash + total_note_cash + actual_earnout
    initial_equity = financing.down_payment + financing.bank_fees

    owner_hours_known = practice.annual_owner_hours is not None and practice.annual_owner_hours > 0
    cumulative_equity = -initial_equity if owner_hours_known else None
    cumulative_ownership_cash = 0.0 if owner_hours_known else None
    equity_recovery_years: float | None = math.inf if owner_hours_known else None
    total_payback_years: float | None = math.inf if owner_hours_known else None
    yearly: list[YearResult] = []
    for year in range(1, horizon + 1):
        retained_services = retained_services_for_year(
            practice, retention_rates, year, use_category_year_1
        )
        retained_revenue = sum(service.retained_revenue for service in retained_services)
        retained_owner_hours = (
            sum(service.retained_owner_hours or 0 for service in retained_services)
            if owner_hours_known else None
        )
        year_retention = retained_revenue / practice.annual_revenue
        staff_cost = practice.annual_staff_costs * (
            (1 - practice.staff_variable_percentage)
            + practice.staff_variable_percentage * year_retention
        )
        operating_cash_flow = retained_revenue - practice.annual_operating_costs - staff_cost
        owner_labor_value = (
            retained_owner_hours * practice.owner_hourly_value
            if retained_owner_hours is not None else None
        )
        seller_row = seller_schedule[year - 1] if year <= len(seller_schedule) else None
        bank_row = bank_schedule[year - 1] if year <= len(bank_schedule) else None
        note_paid = seller_row.payment if seller_row else 0.0
        bank_paid = bank_row.payment if bank_row else 0.0
        earnout_paid = earnout_schedule[year - 1] if year <= financing.earnout_years else 0.0
        net = operating_cash_flow - note_paid - bank_paid - earnout_paid
        economic_profit = net - owner_labor_value if owner_labor_value is not None else None
        if owner_hours_known and economic_profit is not None:
            prior_equity = cumulative_equity
            cumulative_equity += economic_profit
            if math.isinf(equity_recovery_years) and cumulative_equity >= 0 and economic_profit > 0:
                equity_recovery_years = (year - 1) + max(0.0, -prior_equity / economic_profit)

            ownership_cash = operating_cash_flow - owner_labor_value
            prior_ownership_cash = cumulative_ownership_cash
            cumulative_ownership_cash += ownership_cash
            if (math.isinf(total_payback_years)
                    and cumulative_ownership_cash >= total_acquisition_cash
                    and ownership_cash > 0):
                remaining = total_acquisition_cash - prior_ownership_cash
                total_payback_years = (year - 1) + max(0.0, remaining / ownership_cash)
        yearly.append(YearResult(
            year=year, retention_rate=year_retention, retained_revenue=retained_revenue,
            staff_cost=staff_cost, operating_cash_flow=operating_cash_flow,
            seller_note_payment=note_paid, seller_principal=seller_row.principal if seller_row else 0.0,
            seller_interest=seller_row.interest if seller_row else 0.0,
            seller_balance=seller_row.ending_balance if seller_row else 0.0,
            bank_payment=bank_paid, bank_principal=bank_row.principal if bank_row else 0.0,
            bank_interest=bank_row.interest if bank_row else 0.0,
            bank_balance=bank_row.ending_balance if bank_row else 0.0,
            earnout_payment=earnout_paid, net_cash_flow=net,
            target_owner_compensation=owner_labor_value, economic_profit=economic_profit,
            cumulative_cash_flow=cumulative_equity, retained_services=retained_services,
        ))

    first = yearly[0]
    first_year_net = first.net_cash_flow
    cash_on_cash = first_year_net / initial_equity if initial_equity else None
    cash_on_cash_after_labor = (
        first.economic_profit / initial_equity
        if first.economic_profit is not None and initial_equity else None
    )
    retained_hours = (
        sum(s.retained_owner_hours or 0 for s in first.retained_services)
        if owner_hours_known else None
    )
    revenue_per_owner_hour = (
        first.retained_revenue / retained_hours if retained_hours else None
    )
    legacy_payback = equity_recovery_years
    return Scenario(
        retention_rate=effective_retention_rates[0],
        retained_clients=(practice.clients * effective_retention_rates[0]
                          if practice.clients is not None else None),
        retained_revenue=first.retained_revenue, annual_debt_payment=debt_payment,
        annual_bank_payment=bank_payment, annual_earnout_payment=first.earnout_payment,
        annual_cash_flow=first_year_net, equity_payback_years=legacy_payback,
        operating_cash_flow=first.operating_cash_flow, actual_earnout=actual_earnout,
        total_consideration=total_consideration, total_acquisition_cash_paid=total_acquisition_cash,
        cash_on_cash_return=cash_on_cash, recovery_years=equity_recovery_years,
        owner_labor_value=first.target_owner_compensation, economic_profit=first.economic_profit,
        effective_revenue_per_owner_hour=revenue_per_owner_hour,
        cash_on_cash_after_owner_labor=cash_on_cash_after_labor,
        retention_rates=tuple(effective_retention_rates), total_acquisition_payback_years=total_payback_years,
        total_seller_interest=sum(item.interest for item in seller_schedule),
        total_bank_interest=sum(item.interest for item in bank_schedule), years=tuple(yearly),
    )


def assess_data_quality(
    records: tuple[AssumptionRecord, ...], stated_reliability: str
) -> DataQualityAssessment:
    important = [record for record in records if record.important]
    total = len(important) or 1
    entered = sum(
        record.source in ("User entered", "Buyer estimate") for record in important
    ) / total
    context_defaults = sum(record.source == "Context-derived default" for record in important) / total
    generic_defaults = sum(record.source == "Generic screening default" for record in important) / total
    uncertain = tuple(
        record for record in important
        if record.source in ("Context-derived default", "Generic screening default", "Unknown")
    )
    provisional = any(record.source == "Unknown" for record in uncertain) or stated_reliability == "Low"
    return DataQualityAssessment(
        stated_reliability, entered, context_defaults, generic_defaults, uncertain, provisional
    )
def clamp(value: float, minimum: float = 0, maximum: float = 100) -> float:
    return max(minimum, min(maximum, value))


def interpolated_score(value: float, anchors: tuple[tuple[float, float], ...]) -> float:
    """Return a bounded, continuous piecewise-linear score from ordered anchors."""
    if value <= anchors[0][0]:
        return clamp(anchors[0][1])
    for (left_value, left_score), (right_value, right_score) in zip(anchors, anchors[1:]):
        if value <= right_value:
            position = (value - left_value) / (right_value - left_value)
            return clamp(left_score + position * (right_score - left_score))
    return clamp(anchors[-1][1])


def purchase_multiple_score(multiple: float) -> float:
    """Buyer-side valuation attractiveness, with diminishing credit below 0.70x."""
    return interpolated_score(multiple, (
        (0.50, 100), (0.60, 99), (0.70, 98), (0.80, 90), (0.90, 80),
        (1.00, 70), (1.10, 60), (1.20, 50), (1.30, 40), (1.40, 30),
        (1.50, 20), (1.70, 8), (2.00, 0),
    ))


def revenue_per_client_score(revenue_per_client: float) -> float:
    """A deliberately gentle contextual signal, not a standalone quality verdict."""
    return interpolated_score(revenue_per_client, (
        (0, 10), (200, 25), (300, 32), (400, 38), (500, 44), (625, 50),
        (750, 55), (1_000, 64), (1_500, 76), (2_500, 88),
        (5_000, 96), (7_500, 100),
    ))


def service_mix_diversification_score(largest_service_share: float) -> float:
    """Contextual service-mix breadth; this is not client-concentration risk."""
    return interpolated_score(largest_service_share, (
        (0.20, 100), (0.25, 96), (0.40, 90), (0.50, 85), (0.60, 78),
        (0.70, 68), (0.80, 55), (0.90, 35), (1.00, 15),
    ))


def actual_client_concentration_score(
    largest_client_share: float | None,
    top_5_share: float | None,
    top_10_share: float | None,
) -> float | None:
    """Score known unique-client concentration measures, reweighting available signals."""
    measures = (
        (largest_client_share, 0.60, (
            (0.02, 100), (0.05, 95), (0.10, 80), (0.15, 60),
            (0.20, 40), (0.30, 15), (0.40, 0),
        )),
        (top_5_share, 0.25, (
            (0.10, 100), (0.20, 90), (0.30, 75), (0.40, 55),
            (0.55, 30), (0.70, 10), (0.85, 0),
        )),
        (top_10_share, 0.15, (
            (0.15, 100), (0.30, 90), (0.45, 75), (0.60, 55),
            (0.75, 30), (0.90, 10), (1.00, 0),
        )),
    )
    available = [
        (weight, interpolated_score(value, anchors))
        for value, weight, anchors in measures if value is not None
    ]
    if not available:
        return None
    available_weight = sum(weight for weight, _ in available)
    return sum(weight * score for weight, score in available) / available_weight


def retention_contingent_score(share: float) -> float:
    """Graduated heuristic: some risk sharing helps, but no allocation earns perfection."""
    anchors = ((0.0, 35), (0.10, 60), (0.20, 80), (0.30, 90),
               (0.40, 85), (0.60, 60), (1.0, 20))
    share = clamp(share, 0, 1)
    for (left_x, left_y), (right_x, right_y) in zip(anchors, anchors[1:]):
        if share <= right_x:
            return left_y + (right_y - left_y) * (share - left_x) / (right_x - left_x)
    return anchors[-1][1]


def financing_structure_score(practice: Practice, financing: Financing, scenario: Scenario) -> float:
    fixed_service = scenario.annual_bank_payment + scenario.annual_debt_payment
    burden_score = (
        clamp((0.70 - fixed_service / scenario.operating_cash_flow) / 0.50 * 100)
        if scenario.operating_cash_flow > 0 else 0
    )
    contingent = retention_contingent_score(financing.earnout_total / practice.asking_price)
    cash_share = (financing.down_payment + financing.bank_fees) / practice.asking_price
    cash_score = 100 - clamp(abs(cash_share - 0.20) / 0.50 * 100)
    return 0.60 * burden_score + 0.25 * contingent + 0.15 * cash_score


def service_economic_quality(service: ServiceCategory) -> float:
    """Return a 0-100 screening score based on recurrence, fees, and labor economics."""
    fee_score = (
        clamp((service.average_revenue_per_engagement - 400) / 1_100 * 100)
        if math.isfinite(service.average_revenue_per_engagement) else 50
    )
    hourly_score = (
        clamp((service.revenue_per_owner_hour - 150) / 250 * 100)
        if math.isfinite(service.revenue_per_owner_hour) else 50
    )
    return (25 if service.recurring else 0) + 0.375 * fee_score + 0.375 * hourly_score


def service_mix_economic_score(practice: Practice) -> float:
    return sum(
        service.annual_revenue * service_economic_quality(service)
        for service in practice.services
    ) / practice.annual_revenue


def quality_band(score: int) -> str:
    if score >= 90:
        return "Exceptional"
    if score >= 80:
        return "Very attractive"
    if score >= 70:
        return "Attractive with some concerns"
    if score >= 60:
        return "Mixed / requires careful review"
    if score >= 50:
        return "Weak"
    return "Poor acquisition economics"


def transition_band(score: int) -> str:
    if score >= 90:
        return "Exceptional transition support"
    if score >= 80:
        return "Strong transition support"
    if score >= 70:
        return "Favorable with some concerns"
    if score >= 60:
        return "Mixed transition support"
    if score >= 50:
        return "Weak transition support"
    return "High transition risk"


def calculate_quality_score(
    practice: Practice, financing: Financing, scenario: Scenario
) -> QualityScore:
    summary = summarize_services(practice)
    owner_hours_known = (
        practice.annual_owner_hours is not None
        and practice.annual_owner_hours > 0
        and scenario.economic_profit is not None
    )
    multiple = practice.asking_price / practice.annual_revenue
    clients_known = practice.clients is not None and practice.clients > 0
    average_client_revenue = practice.annual_revenue / practice.clients if clients_known else None
    retained_hours = (
        sum(service.retained_owner_hours or 0 for service in scenario.years[0].retained_services)
        if owner_hours_known else None
    )
    residual_margin = (
        scenario.economic_profit / scenario.retained_revenue
        if owner_hours_known and scenario.retained_revenue else None
    )
    return_on_equity = (
        scenario.cash_on_cash_after_owner_labor
        if owner_hours_known and financing.down_payment else None
    )
    hours_per_100k = (
        retained_hours / scenario.retained_revenue * 100_000
        if owner_hours_known and scenario.retained_revenue else None
    )
    service_mix_score = service_mix_economic_score(practice)
    low_quality_revenue = sum(
        service.annual_revenue for service in practice.services
        if service.annual_revenue and (
            (service.annual_owner_hours and service.revenue_per_owner_hour < 175)
            or (service.engagements and service.average_revenue_per_engagement < 400)
        )
    )
    low_quality_share = low_quality_revenue / practice.annual_revenue
    client_concentration_score = actual_client_concentration_score(
        practice.largest_client_revenue_share,
        practice.top_5_client_revenue_share,
        practice.top_10_client_revenue_share,
    )
    concentration_known_count = sum(value is not None for value in (
        practice.largest_client_revenue_share,
        practice.top_5_client_revenue_share,
        practice.top_10_client_revenue_share,
    ))

    revenue_hour_score = (
        clamp((scenario.effective_revenue_per_owner_hour - 150) / 250 * 100)
        if owner_hours_known and scenario.effective_revenue_per_owner_hour is not None else 0
    )
    roe_score = clamp(return_on_equity / 0.50 * 100) if return_on_equity is not None else 0
    payback_score = (
        clamp((10 - scenario.total_acquisition_payback_years) / 7 * 100)
        if scenario.total_acquisition_payback_years is not None
        and math.isfinite(scenario.total_acquisition_payback_years) else 0
    )
    all_components = (
        ScoreComponent("Purchase price / revenue", 10, purchase_multiple_score(multiple), f"{multiple:.2f}x"),
        ScoreComponent("Recurring revenue", 9, summary.recurring_revenue / practice.annual_revenue * 100, f"{summary.recurring_revenue / practice.annual_revenue:.1%}"),
        ScoreComponent("Revenue per client", 2,
                       revenue_per_client_score(average_client_revenue) if average_client_revenue is not None else 0,
                       money(average_client_revenue) if average_client_revenue is not None else "Excluded"),
        ScoreComponent("Revenue per owner hour", 9, revenue_hour_score, money(scenario.effective_revenue_per_owner_hour) if scenario.effective_revenue_per_owner_hour is not None else "Excluded"),
        ScoreComponent("Residual ownership margin", 11, clamp((residual_margin + 0.10) / 0.30 * 100) if residual_margin is not None else 0, f"{residual_margin:.1%}" if residual_margin is not None else "Excluded"),
        ScoreComponent("Return on initial equity", 11, roe_score, f"{return_on_equity:.1%}" if return_on_equity is not None else "Excluded"),
        ScoreComponent("Total acquisition payback", 9, payback_score, f"{scenario.total_acquisition_payback_years:.1f} years" if scenario.total_acquisition_payback_years is not None and math.isfinite(scenario.total_acquisition_payback_years) else "Not recovered in horizon"),
        ScoreComponent("Service mix diversification", 2,
                       service_mix_diversification_score(summary.largest_service_share),
                       f"largest service {summary.largest_service_share:.1%}"),
        ScoreComponent("Actual client concentration", 6,
                       client_concentration_score if client_concentration_score is not None else 0,
                       f"{concentration_known_count}/3 measures known" if client_concentration_score is not None else "Excluded"),
        ScoreComponent("Expected retention", 11, clamp((scenario.retention_rate - 0.75) / 0.20 * 100), f"{scenario.retention_rate:.1%}"),
        ScoreComponent("Owner workload", 5, clamp((700 - hours_per_100k) / 450 * 100) if hours_per_100k is not None else 0, f"{hours_per_100k:,.0f} hrs/$100k" if hours_per_100k is not None else "Excluded"),
        ScoreComponent("Service economics / quality", 4, service_mix_score, f"{service_mix_score:.0f}/100 mix index"),
        ScoreComponent("Low-fee/labor dependence", 3, (1 - low_quality_share) * 100, f"{low_quality_share:.1%} exposed"),
        ScoreComponent("Financing structure / risk", 8,
                       financing_structure_score(practice, financing, scenario),
                       f"fixed DS {(scenario.annual_bank_payment + scenario.annual_debt_payment) / scenario.operating_cash_flow:.1%}" if scenario.operating_cash_flow > 0 else "nonpositive operating CF"),
    )
    excluded_components = set()
    if not owner_hours_known:
        excluded_components.update({
            "Revenue per owner hour", "Residual ownership margin",
            "Return on initial equity", "Total acquisition payback",
            "Owner workload", "Service economics / quality",
            "Low-fee/labor dependence",
        })
    if not clients_known:
        excluded_components.add("Revenue per client")
    if client_concentration_score is None:
        excluded_components.add("Actual client concentration")
    if excluded_components:
        available = [c for c in all_components if c.name not in excluded_components]
        available_weight = sum(c.weight for c in available)
        components = tuple(
            ScoreComponent(c.name, c.weight / available_weight * 100, c.score, c.value)
            for c in available
        )
    else:
        components = all_components
    final_score = max(1, min(100, round(sum(component.weighted_points for component in components))))
    strengths = tuple(f"{component.name} ({component.value})" for component in components if component.score >= 75)[:3]
    concerns = tuple(f"{component.name} ({component.value})" for component in components if component.score < 45)[:3]
    issue_map = {
        "Purchase price / revenue": "Validate the asking-price multiple against normalized, transferable earnings.",
        "Recurring revenue": "Confirm which engagements recur contractually and review cancellation history.",
        "Revenue per client": "Review pricing, realization, and the opportunity to reprice low-fee work.",
        "Revenue per owner hour": "Validate service-level hours and identify work that can be delegated or automated.",
        "Residual ownership margin": "Reconcile normalized costs and target owner compensation to historical results.",
        "Return on initial equity": "Stress-test equity returns under lower retention and higher operating costs.",
        "Total acquisition payback": "Review whether financing terms can shorten the total acquisition payback.",
        "Service mix diversification": "Review whether specialization creates seasonality, workflow, or transferability risk; do not confuse it with client concentration.",
        "Actual client concentration": "Obtain client-level revenue and investigate dependence on unusually large relationships.",
        "Expected retention": "Support retention assumptions with client tenure, transition plans, and attrition history.",
        "Owner workload": "Confirm owner hours by service and seasonal capacity requirements.",
        "Service economics / quality": "Validate service-level fees, recurrence, and owner hours rather than relying on service labels.",
        "Low-fee/labor dependence": "Identify low-fee or labor-intensive engagements that require repricing or exit.",
        "Financing structure / risk": "Stress-test fixed bank and seller debt service against lower retained revenue.",
    }
    weakest = sorted(components, key=lambda component: component.score)
    investigations_list = [issue_map[component.name] for component in weakest[:4]]
    if concentration_known_count < 3:
        investigations_list.insert(
            0, "Obtain complete client-level revenue detail to verify largest-client, top-five, and top-ten concentration."
        )
    if not owner_hours_known:
        investigations_list.insert(
            0, "Obtain reliable owner hours by service before relying on owner-labor economics."
        )
    investigations = tuple(dict.fromkeys(investigations_list))[:4]
    return QualityScore(final_score, quality_band(final_score), components, strengths, concerns, investigations)


def calculate_transition_score(
    practice: Practice, financing: Financing, assessment: TransitionAssessment
) -> QualityScore:
    ratings = (
        assessment.seller_rapport, assessment.seller_commitment, assessment.cultural_fit,
        assessment.client_desirability, assessment.practice_organization,
        assessment.information_confidence,
    )
    if any(not 1 <= rating <= 5 for rating in ratings):
        raise ValueError("Qualitative ratings must be between 1 and 5.")
    if assessment.seller_transition_months < 0 or assessment.post_closing_availability_months < 0:
        raise ValueError("Transition and availability periods cannot be negative.")
    if (assessment.expected_key_staff_retention is not None
            and not 0 <= assessment.expected_key_staff_retention <= 1):
        raise ValueError("Expected key staff retention must be between 0% and 100%.")
    retention_consideration_share = financing.earnout_total / practice.asking_price
    staff_score = (
        assessment.expected_key_staff_retention * 100
        if assessment.expected_key_staff_retention is not None else 50
    )
    rating = lambda value: (value - 1) / 4 * 100
    components = (
        ScoreComponent("Seller transition period", 20, clamp(assessment.seller_transition_months / 6 * 100), f"{assessment.seller_transition_months:g} months"),
        ScoreComponent("Seller through tax season", 10, 100 if assessment.stays_through_tax_season else 0, "Yes" if assessment.stays_through_tax_season else "No"),
        ScoreComponent("Personal client introductions", 10, 100 if assessment.personal_client_introductions else 0, "Yes" if assessment.personal_client_introductions else "No"),
        ScoreComponent("Post-closing availability", 10, clamp(assessment.post_closing_availability_months / 12 * 100), f"{assessment.post_closing_availability_months:g} months"),
        ScoreComponent("Expected key staff retention", 10, staff_score, f"{assessment.expected_key_staff_retention:.1%}" if assessment.expected_key_staff_retention is not None else "Unknown (neutral score)"),
        ScoreComponent("Retention-based consideration", 10, retention_contingent_score(retention_consideration_share), f"{retention_consideration_share:.1%} of price"),
        ScoreComponent("Seller rapport / trust", 5, rating(assessment.seller_rapport), f"{assessment.seller_rapport}/5 buyer rating"),
        ScoreComponent("Seller transition commitment", 5, rating(assessment.seller_commitment), f"{assessment.seller_commitment}/5 buyer rating"),
        ScoreComponent("Cultural fit", 5, rating(assessment.cultural_fit), f"{assessment.cultural_fit}/5 buyer rating"),
        ScoreComponent("Client desirability", 5, rating(assessment.client_desirability), f"{assessment.client_desirability}/5 buyer rating"),
        ScoreComponent("Practice organization", 5, rating(assessment.practice_organization), f"{assessment.practice_organization}/5 buyer rating"),
        ScoreComponent("Information confidence", 5, rating(assessment.information_confidence), f"{assessment.information_confidence}/5 buyer rating"),
    )
    final_score = max(1, min(100, round(sum(component.weighted_points for component in components))))
    strengths = tuple(f"{component.name} ({component.value})" for component in components if component.score >= 75)[:3]
    concerns = tuple(f"{component.name} ({component.value})" for component in components if component.score < 45)[:3]
    issue_map = {
        "Seller transition period": "Negotiate a documented transition period with specific seller responsibilities.",
        "Seller through tax season": "Determine who will manage client communication and delivery through tax season.",
        "Personal client introductions": "Identify priority relationships for personal seller-to-buyer introductions.",
        "Post-closing availability": "Document seller availability, response times, and compensation after closing.",
        "Expected key staff retention": "Confirm key employee intentions, incentives, and employment terms.",
        "Retention-based consideration": "Consider aligning more purchase consideration with actual retained revenue.",
        "Seller rapport / trust": "Resolve trust concerns through verification and specific representations.",
        "Seller transition commitment": "Convert transition promises into measurable closing obligations.",
        "Cultural fit": "Test cultural fit through selected client and staff interactions.",
        "Client desirability": "Review the client list for fit, risk, pricing, and service expectations.",
        "Practice organization": "Inspect files, workflows, deadlines, technology, and documentation quality.",
        "Information confidence": "Independently verify financial, client, and operational information.",
    }
    weakest = sorted(components, key=lambda component: component.score)
    investigations = tuple(issue_map[component.name] for component in weakest[:4])
    return QualityScore(final_score, transition_band(final_score), components, strengths, concerns, investigations)


def calculate_overall_score(financial_score: int, transition_score: int) -> int:
    return max(1, min(100, round(
        financial_score * OVERALL_FINANCIAL_WEIGHT
        + transition_score * OVERALL_TRANSITION_WEIGHT
    )))


__all__ = (
    "DEFAULT_ONGOING_RETENTION", "DEFAULT_STAFF_VARIABLE_PERCENTAGE",
    "OVERALL_FINANCIAL_WEIGHT", "OVERALL_TRANSITION_WEIGHT",
    "DEFAULT_SERVICE_CATEGORIES", "SERVICE_COUNT_LABELS", "SERVICE_REVENUE_SHARES",
    "SERVICE_TYPICAL_REVENUE_PER_ENGAGEMENT", "ServiceCategory", "ServiceSummary",
    "RetainedService", "Practice", "Financing", "DebtPayment", "YearResult", "Scenario",
    "ScoreComponent", "QualityScore", "TransitionAssessment", "AssumptionRecord",
    "DataQualityAssessment", "annual_loan_payment", "amortization_schedule", "money",
    "validate_terms", "validate_practice", "summarize_services", "normalize_retention",
    "retained_services_for_year", "analyze", "assess_data_quality", "clamp",
    "interpolated_score", "purchase_multiple_score", "revenue_per_client_score",
    "service_mix_diversification_score", "actual_client_concentration_score",
    "retention_contingent_score", "financing_structure_score", "service_economic_quality",
    "service_mix_economic_score", "quality_band", "transition_band",
    "calculate_quality_score", "calculate_transition_score", "calculate_overall_score",
)
