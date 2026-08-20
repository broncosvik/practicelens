"""Shared plain-English presentation for CLI and web consumers."""

from __future__ import annotations

import acquisition_engine as engine


def _unique(items: list[str], limit: int) -> list[str]:
    return list(dict.fromkeys(item for item in items if item))[:limit]


def build_acquisition_analysis(
    practice: engine.Practice,
    financing: engine.Financing,
    scenario: engine.Scenario,
    financial: engine.QualityScore,
    transition_input: engine.TransitionAssessment,
    transition: engine.QualityScore,
    overall_score: int,
    *,
    uncertainties: tuple[str, ...] = (),
) -> dict[str, object]:
    """Interpret engine results without recalculating or altering their scores."""
    components = {component.name: component for component in financial.components}
    transition_components = {component.name: component for component in transition.components}
    strengths: list[str] = []
    risks: list[str] = []
    diligence: list[str] = []

    def strong(name: str, threshold: float = 75) -> bool:
        return name in components and components[name].score >= threshold

    def weak(name: str, threshold: float = 40) -> bool:
        return name in components and components[name].score < threshold

    if strong("Purchase price / revenue"):
        strengths.append(f"The {practice.asking_price / practice.annual_revenue:.2f}x purchase multiple is attractive from the buyer's perspective.")
    elif weak("Purchase price / revenue"):
        risks.append(f"The {practice.asking_price / practice.annual_revenue:.2f}x purchase multiple requires unusually strong economics to justify it.")
    if strong("Expected retention"):
        strengths.append(f"Expected first-year retention of {scenario.retention_rate:.0%} supports transfer of the acquired revenue base.")
    elif weak("Expected retention"):
        risks.append(f"Expected first-year retention of {scenario.retention_rate:.0%} puts a meaningful portion of purchased revenue at risk.")
    recurring_share = engine.summarize_services(practice).recurring_revenue / practice.annual_revenue
    if strong("Recurring revenue"):
        strengths.append(f"Recurring or repeat services represent {recurring_share:.0%} of acquired-book revenue.")
    elif weak("Recurring revenue"):
        risks.append(f"Only {recurring_share:.0%} of revenue is classified as recurring or repeat work.")
    if strong("Revenue per owner hour"):
        strengths.append(f"Revenue of {engine.money(scenario.effective_revenue_per_owner_hour or 0)} per retained owner hour indicates favorable labor efficiency under the entered hours.")
    elif weak("Revenue per owner hour"):
        risks.append(f"Revenue per owner hour is low under the entered workload, limiting the economics of the buyer's labor.")
    if strong("Owner workload"):
        strengths.append("The entered owner workload appears manageable relative to retained revenue.")
    elif weak("Owner workload"):
        risks.append("The acquired book appears highly dependent on substantial buyer labor.")
    if strong("Residual ownership margin"):
        strengths.append(f"After target owner compensation, year-one residual ownership profit is {engine.money(scenario.economic_profit or 0)}.")
    elif weak("Residual ownership margin"):
        risks.append("Residual profitability after economically compensating buyer labor is weak.")
    if strong("Return on initial equity"):
        strengths.append("Labor-adjusted return on the buyer's initial equity is favorable under the entered assumptions.")
    elif weak("Return on initial equity"):
        risks.append("Labor-adjusted return on initial buyer equity is weak.")
    if strong("Total acquisition payback"):
        strengths.append(f"Total acquisition payback is projected at {scenario.total_acquisition_payback_years:.1f} years.")
    elif weak("Total acquisition payback"):
        risks.append("The modeled total acquisition payback is long or is not achieved within the analysis horizon.")
    if strong("Actual client concentration", 80):
        strengths.insert(0, "Known client-level revenue data indicate a well-diversified client base with limited dependence on major relationships.")
    elif weak("Actual client concentration"):
        risks.insert(0, "Actual client concentration creates meaningful dependence on one or several major client relationships.")
        diligence.append("Determine whether unusually large clients depend personally on the seller and assess their transfer risk.")
    largest_service_share = engine.summarize_services(practice).largest_service_share
    if strong("Service mix diversification", 85):
        if largest_service_share < 0.5:
            strengths.append(
                f"No single service category represents a majority of acquired-book revenue; "
                f"the largest is {largest_service_share:.1%}. This measures service mix only, not client concentration."
            )
        else:
            strengths.append(
                f"The largest service category represents {largest_service_share:.1%} of acquired-book revenue."
            )
    if strong("Financing structure / risk"):
        strengths.append("Projected operating cash flow provides a favorable cushion for fixed acquisition debt service.")
    elif weak("Financing structure / risk"):
        risks.append("Fixed acquisition obligations place substantial pressure on projected operating cash flow.")
        diligence.append("Confirm final bank and seller-note terms and stress-test debt service at lower retention.")

    contingent_share = financing.earnout_total / practice.asking_price
    if contingent_share >= 0.15:
        strengths.append(f"The seller shares transition risk through retention-contingent consideration equal to {contingent_share:.0%} of the price.")
    elif contingent_share <= 0.05:
        risks.append("Little purchase consideration is tied to actual retention, leaving most transfer risk with the buyer.")
        diligence.append("Confirm whether the purchase agreement can tie more consideration to collected retained revenue.")

    for name, positive, negative in (
        ("Seller transition period", "The seller has committed to a meaningful transition period.", "Seller transition support is limited."),
        ("Personal client introductions", "The seller plans personal introductions to important clients.", "Personal seller introductions to important clients are not confirmed."),
        ("Seller through tax season", "The seller plans to remain through a tax season.", "The seller is not committed to remain through a tax season."),
        ("Expected key staff retention", "Expected key-staff retention supports operating continuity.", "Expected key-staff retention is weak."),
        ("Seller transition commitment", "The buyer rates the seller's transition commitment strongly.", "The buyer rates seller transition commitment poorly."),
        ("Cultural fit", "The buyer reports strong cultural fit with the client base.", "Cultural fit with the acquired client base is a concern."),
        ("Practice organization", "Practice organization and workflow quality are rated strongly.", "Practice organization or workflow quality is rated poorly."),
    ):
        component = transition_components.get(name)
        if component and component.score >= 75:
            strengths.append(positive)
        elif component and component.score < 40:
            risks.append(negative)

    concentration_values = (
        practice.largest_client_revenue_share,
        practice.top_5_client_revenue_share,
        practice.top_10_client_revenue_share,
    )
    if any(value is None for value in concentration_values):
        diligence.append("Obtain client-level revenue detail to verify largest-client, top-five, and top-ten concentration.")
    if practice.annual_owner_hours is None:
        diligence.append("Determine actual owner hours by service before relying on labor-adjusted profitability or payback.")
    if transition_input.expected_key_staff_retention is None:
        diligence.append("Confirm key-staff compensation, intentions, and expected post-closing retention.")
    if not transition_input.personal_client_introductions:
        diligence.append("Identify priority clients for personal seller-to-buyer introductions.")
    if transition_input.seller_transition_months < 3:
        diligence.append("Document the seller's transition responsibilities, timing, availability, and deliverables.")
    if financing.earnout_total:
        diligence.append("Confirm the earn-out definition, measurement periods, collections basis, exclusions, caps, and dispute process.")
    diligence.extend(uncertainties)
    diligence.extend(financial.investigation_items)

    practice_view = (
        "The acquired practice appears economically strong under the entered operating assumptions."
        if financial.score >= 80 else
        "The acquired practice appears viable but has material economic tradeoffs that require validation."
        if financial.score >= 60 else
        "The acquired practice has weak or uncertain operating economics under the entered assumptions."
    )
    deal_view = (
        "The price and financing structure appear broadly supportable by the acquired book."
        if strong("Purchase price / revenue", 60) and not weak("Financing structure / risk") else
        "Practice quality does not by itself resolve concerns about price or acquisition obligations."
    )
    # Only describe information as unresolved when it is genuinely unknown.
    unresolved: list[str] = []
    if practice.annual_owner_hours is None:
        unresolved.append("owner workload")
    if any(value is None for value in concentration_values):
        unresolved.append("client concentration")
    confidence_note = (
        f" {' and '.join(unresolved).capitalize()} information remains unresolved,"
        " so the conclusion should be treated as provisional."
        if unresolved else ""
    )
    overall = [
        f"The combined score is {overall_score}/100. {practice_view} {deal_view}{confidence_note}",
        (f"Year-one retained revenue is {engine.money(scenario.retained_revenue)} and cash available to the owner before owner compensation is {engine.money(scenario.annual_cash_flow)}. "
         + (f"After valuing buyer labor, residual ownership profit is {engine.money(scenario.economic_profit)}."
            if scenario.economic_profit is not None else
            "Labor-adjusted profitability cannot be assessed until reliable owner hours are obtained.")),
    ]
    result = {
        "overall_assessment": overall,
        "strengths": _unique(strengths, 7),
        "weaknesses_risks": _unique(risks, 7),
        "key_due_diligence_questions": _unique(diligence, 6),
    }
    # Preserve the original web-facing names while exposing the more useful,
    # explicitly labelled sections to new consumers.
    result.update({
        "summary": " ".join(overall),
        "attractive_factors": result["strengths"],
        "financial_concerns": result["weaknesses_risks"],
        "priority_due_diligence": result["key_due_diligence_questions"],
    })
    return result


__all__ = ("build_acquisition_analysis",)
