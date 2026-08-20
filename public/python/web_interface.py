"""Framework-neutral, JSON-friendly interface to :mod:`acquisition_engine`.

This module contains request parsing and response presentation only. It does not
implement acquisition formulas. A future Flask, Django, FastAPI, or other web
handler can pass a decoded JSON dictionary to ``analyze_acquisition`` and return
the resulting dictionary as JSON.
"""

from __future__ import annotations

from dataclasses import asdict
import math
from typing import Any

import acquisition_engine as engine


class RequestValidationError(ValueError):
    """A validation problem tied to a web-request field."""

    def __init__(self, field: str, message: str):
        super().__init__(message)
        self.field = field
        self.message = message


def _required(mapping: dict[str, Any], key: str, path: str) -> Any:
    if key not in mapping:
        raise RequestValidationError(f"{path}.{key}", "This field is required.")
    return mapping[key]


def _number(value: Any, field: str, *, minimum: float | None = None) -> float:
    if isinstance(value, bool):
        raise RequestValidationError(field, "Must be a number.")
    try:
        result = float(value)
    except (TypeError, ValueError):
        raise RequestValidationError(field, "Must be a number.") from None
    if not math.isfinite(result):
        raise RequestValidationError(field, "Must be a finite number.")
    if minimum is not None and result < minimum:
        raise RequestValidationError(field, f"Must be at least {minimum:g}.")
    return result


def _integer_or_none(value: Any, field: str) -> int | None:
    if value is None:
        return None
    number = _number(value, field, minimum=0)
    if not number.is_integer():
        raise RequestValidationError(field, "Must be a whole number or null.")
    return int(number)


def _integer(value: Any, field: str, *, minimum: int = 0) -> int:
    result = _integer_or_none(value, field)
    if result is None:
        raise RequestValidationError(field, "Must be a whole number.")
    if result < minimum:
        raise RequestValidationError(field, f"Must be at least {minimum}.")
    return result


def _boolean(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise RequestValidationError(field, "Must be true or false.")
    return value


def _rate(value: Any, field: str) -> float:
    rate = _number(value, field)
    if not 0 <= rate <= 1:
        raise RequestValidationError(field, "Must be between 0 and 1.")
    return rate


def _parse_services(values: Any) -> tuple[engine.ServiceCategory, ...]:
    if not isinstance(values, list) or not values:
        raise RequestValidationError("practice.services", "Provide at least one service category.")
    services = []
    for index, item in enumerate(values):
        path = f"practice.services[{index}]"
        if not isinstance(item, dict):
            raise RequestValidationError(path, "Must be an object.")
        hours_value = item.get("annual_owner_hours")
        hours = None if hours_value is None else _number(hours_value, f"{path}.annual_owner_hours", minimum=0)
        services.append(engine.ServiceCategory(
            name=str(_required(item, "name", path)).strip(),
            recurring=_boolean(_required(item, "recurring", path), f"{path}.recurring"),
            engagements=_integer_or_none(item.get("engagements"), f"{path}.engagements"),
            annual_revenue=_number(_required(item, "annual_revenue", path), f"{path}.annual_revenue", minimum=0),
            annual_owner_hours=hours,
            # Forecasting is practice-wide; these compatibility fields are not
            # used unless an explicit future category-retention mode is selected.
            retention_rate=1.0,
        ))
    if any(not service.name for service in services):
        raise RequestValidationError("practice.services[].name", "Service names cannot be blank.")
    return tuple(services)


def _parse_practice(payload: dict[str, Any]) -> engine.Practice:
    path = "practice"
    services = _parse_services(_required(payload, "services", path))
    clients = _integer_or_none(payload.get("client_relationships"), f"{path}.client_relationships")
    return engine.Practice(
        annual_revenue=_number(_required(payload, "annual_revenue", path), f"{path}.annual_revenue", minimum=0.01),
        asking_price=_number(_required(payload, "asking_price", path), f"{path}.asking_price", minimum=0.01),
        clients=clients,
        services=services,
        annual_operating_costs=_number(_required(payload, "fixed_operating_costs", path), f"{path}.fixed_operating_costs", minimum=0),
        annual_staff_costs=_number(_required(payload, "staff_variable_costs", path), f"{path}.staff_variable_costs", minimum=0),
        owner_hourly_value=_number(_required(payload, "owner_hourly_value", path), f"{path}.owner_hourly_value", minimum=0),
        staff_variable_percentage=_rate(
            payload.get("staff_retention_sensitive_percentage", engine.DEFAULT_STAFF_VARIABLE_PERCENTAGE),
            f"{path}.staff_retention_sensitive_percentage",
        ),
    )


def _parse_financing(payload: dict[str, Any]) -> engine.Financing:
    path = "financing"
    seller = payload.get("seller_note", {})
    bank = payload.get("bank_loan", {})
    earnout = payload.get("earnout", {})
    if not all(isinstance(item, dict) for item in (seller, bank, earnout)):
        raise RequestValidationError(path, "seller_note, bank_loan, and earnout must be objects.")
    seller_amount = _number(seller.get("amount", 0), f"{path}.seller_note.amount", minimum=0)
    bank_amount = _number(bank.get("amount", 0), f"{path}.bank_loan.amount", minimum=0)
    earnout_amount = _number(earnout.get("maximum_amount", 0), f"{path}.earnout.maximum_amount", minimum=0)
    return engine.Financing(
        down_payment=_number(payload.get("buyer_cash", 0), f"{path}.buyer_cash", minimum=0),
        seller_note=seller_amount,
        annual_interest_rate=_number(seller.get("annual_interest_rate", 0), f"{path}.seller_note.annual_interest_rate", minimum=0),
        note_years=_integer(seller.get("term_years", 0), f"{path}.seller_note.term_years"),
        earnout_total=earnout_amount,
        earnout_years=_integer(earnout.get("term_years", 0), f"{path}.earnout.term_years"),
        bank_loan=bank_amount,
        bank_annual_interest_rate=_number(bank.get("annual_interest_rate", 0), f"{path}.bank_loan.annual_interest_rate", minimum=0),
        bank_years=_integer(bank.get("term_years", 0), f"{path}.bank_loan.term_years"),
        bank_variable_rate=_boolean(bank.get("variable_rate", False), f"{path}.bank_loan.variable_rate"),
        bank_fees=_number(bank.get("fees", 0), f"{path}.bank_loan.fees", minimum=0),
    )


def _parse_transition(payload: dict[str, Any]) -> engine.TransitionAssessment:
    path = "transition"
    staff_retention = _required(payload, "expected_key_staff_retention", path)
    return engine.TransitionAssessment(
        seller_transition_months=_number(_required(payload, "seller_transition_months", path), f"{path}.seller_transition_months", minimum=0),
        stays_through_tax_season=_boolean(_required(payload, "stays_through_tax_season", path), f"{path}.stays_through_tax_season"),
        personal_client_introductions=_boolean(_required(payload, "personal_client_introductions", path), f"{path}.personal_client_introductions"),
        post_closing_availability_months=_number(_required(payload, "post_closing_availability_months", path), f"{path}.post_closing_availability_months", minimum=0),
        expected_key_staff_retention=(None if staff_retention is None else _rate(staff_retention, f"{path}.expected_key_staff_retention")),
        seller_rapport=_integer(_required(payload, "seller_rapport", path), f"{path}.seller_rapport", minimum=1),
        seller_commitment=_integer(_required(payload, "seller_commitment", path), f"{path}.seller_commitment", minimum=1),
        cultural_fit=_integer(_required(payload, "cultural_fit", path), f"{path}.cultural_fit", minimum=1),
        client_desirability=_integer(_required(payload, "client_desirability", path), f"{path}.client_desirability", minimum=1),
        practice_organization=_integer(_required(payload, "practice_organization", path), f"{path}.practice_organization", minimum=1),
        information_confidence=_integer(_required(payload, "information_confidence", path), f"{path}.information_confidence", minimum=1),
    )


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def _score_dict(score: engine.QualityScore) -> dict[str, Any]:
    return {
        "score": score.score,
        "band": score.band,
        "components": [asdict(component) | {"weighted_points": component.weighted_points}
                       for component in score.components],
        "strengths": list(score.strengths),
        "concerns": list(score.concerns),
        "due_diligence": list(score.investigation_items),
    }


def _service_analysis(practice: engine.Practice, scenario: engine.Scenario) -> list[dict[str, Any]]:
    rows = []
    for service, retained in zip(practice.services, scenario.years[0].retained_services):
        rows.append({
            "name": service.name,
            "recurring": service.recurring,
            "engagements": service.engagements,
            "annual_revenue": service.annual_revenue,
            "average_revenue_per_engagement": (
                service.average_revenue_per_engagement
                if math.isfinite(service.average_revenue_per_engagement) else None
            ),
            "revenue_percentage": service.annual_revenue / practice.annual_revenue,
            "annual_owner_hours": service.annual_owner_hours,
            "revenue_per_owner_hour": (
                service.revenue_per_owner_hour
                if math.isfinite(service.revenue_per_owner_hour) else None
            ),
            "year_1_retained_revenue": retained.retained_revenue,
            "year_1_retained_owner_hours": retained.retained_owner_hours,
        })
    return rows


def _english_analysis(financial: engine.QualityScore, transition: engine.QualityScore,
                      overall: int, scenario: engine.Scenario) -> dict[str, Any]:
    owner_note = (
        "Owner-labor economics are unavailable because reliable owner hours were not provided."
        if scenario.owner_labor_value is None
        else (f"Year-one target owner compensation is {engine.money(scenario.owner_labor_value)}; "
              f"residual ownership profit is {engine.money(scenario.economic_profit or 0)}.")
    )
    return {
        "summary": (
            f"Overall acquisition score: {overall}/100. Financial/operational assessment: "
            f"{financial.band}. Transition assessment: {transition.band}. {owner_note}"
        ),
        "attractive_factors": list(financial.strengths),
        "financial_concerns": list(financial.concerns),
        "transition_strengths": list(transition.strengths),
        "transition_concerns": list(transition.concerns),
        "priority_due_diligence": list(dict.fromkeys(
            financial.investigation_items[:2] + transition.investigation_items[:2]
        )),
        "scope_note": (
            "The base analysis evaluates only the existing acquired book and gives no credit "
            "for referrals, cross-selling, new services, fee increases, or buyer-created growth."
        ),
    }


def analyze_acquisition(request: dict[str, Any]) -> dict[str, Any]:
    """Validate and analyze one decoded JSON request.

    Returns ``{"ok": False, "errors": [...]}`` for user-correctable validation
    problems and a fully JSON-serializable analysis response on success.
    """
    try:
        if not isinstance(request, dict):
            raise RequestValidationError("request", "Request body must be an object.")
        practice_payload = _required(request, "practice", "request")
        financing_payload = _required(request, "financing", "request")
        retention_payload = _required(request, "retention", "request")
        if not all(isinstance(item, dict)
                   for item in (practice_payload, financing_payload, retention_payload)):
            raise RequestValidationError("request", "practice, financing, and retention must be objects.")
        practice = _parse_practice(practice_payload)
        financing = _parse_financing(financing_payload)
        retention = (
            _rate(_required(retention_payload, "first_year", "retention"), "retention.first_year"),
            _rate(_required(retention_payload, "ongoing", "retention"), "retention.ongoing"),
        )
        horizon = _integer(request.get("analysis_horizon", 7), "analysis_horizon", minimum=3)
        if horizon > 10:
            raise RequestValidationError("analysis_horizon", "Must be between 3 and 10 years.")
        transition_payload = _required(request, "transition", "request")
        if not isinstance(transition_payload, dict):
            raise RequestValidationError("transition", "Must be an object.")
        transition = _parse_transition(transition_payload)

        scenario = engine.analyze(practice, financing, retention, horizon)
        financial_score = engine.calculate_quality_score(practice, financing, scenario)
        transition_score = engine.calculate_transition_score(practice, financing, transition)
        overall_score = engine.calculate_overall_score(financial_score.score, transition_score.score)
        summary = engine.summarize_services(practice)
        assumptions = request.get("assumptions", [])
        if not isinstance(assumptions, list):
            raise RequestValidationError("assumptions", "Must be a list.")

        applied_defaults = []
        if "staff_retention_sensitive_percentage" not in practice_payload:
            applied_defaults.append({
                "field": "practice.staff_retention_sensitive_percentage",
                "value": engine.DEFAULT_STAFF_VARIABLE_PERCENTAGE,
                "source": "analyzer_default",
            })
        if "analysis_horizon" not in request:
            applied_defaults.append({
                "field": "analysis_horizon", "value": 7,
                "source": "analyzer_default",
            })
        for section, field in (("seller_note", "amount"), ("bank_loan", "amount"),
                               ("earnout", "maximum_amount")):
            section_payload = financing_payload.get(section)
            if not isinstance(section_payload, dict) or field not in section_payload:
                applied_defaults.append({
                    "field": f"financing.{section}.{field}", "value": 0,
                    "source": "analyzer_default",
                })
        unknowns = [
            {"field": f"practice.services[{index}].annual_owner_hours",
             "effect": "Owner-hours-dependent metrics are unavailable."}
            for index, service in enumerate(practice.services)
            if service.annual_owner_hours is None
        ]
        unknowns.extend(
            {"field": f"practice.services[{index}].engagements",
             "effect": "Average revenue per engagement is unavailable for this service."}
            for index, service in enumerate(practice.services)
            if service.engagements is None
        )
        if practice.clients is None:
            unknowns.append({
                "field": "practice.client_relationships",
                "effect": "Revenue-per-client analysis is unavailable.",
            })

        response = {
            "ok": True,
            "analysis": asdict(scenario),
            "scores": {
                "financial_operational": _score_dict(financial_score),
                "transition_qualitative": _score_dict(transition_score),
                "overall": {"score": overall_score,
                            "weighting": {
                                "financial_operational": engine.OVERALL_FINANCIAL_WEIGHT,
                                "transition_qualitative": engine.OVERALL_TRANSITION_WEIGHT,
                            }},
            },
            "assumptions": {
                "provided": assumptions,
                "applied_defaults": applied_defaults,
                "unknowns": unknowns,
            },
            "english_analysis": _english_analysis(
                financial_score, transition_score, overall_score, scenario
            ),
            "cash_flow_projections": [asdict(year) for year in scenario.years],
            "service_categories": _service_analysis(practice, scenario),
            "service_summary": asdict(summary),
            "financing": {
                "terms": asdict(financing),
                "purchase_price": practice.asking_price,
                "maximum_allocation": (financing.down_payment + financing.bank_loan
                                       + financing.seller_note + financing.earnout_total),
                "actual_consideration": scenario.total_consideration,
                "actual_earnout": scenario.actual_earnout,
                "annual_bank_debt_service": scenario.annual_bank_payment,
                "annual_seller_debt_service": scenario.annual_debt_payment,
                "remaining_balances": [
                    {"year": year.year, "bank": year.bank_balance,
                     "seller": year.seller_balance}
                    for year in scenario.years
                ],
            },
            "transition": {
                "inputs": asdict(transition),
                "result": _score_dict(transition_score),
            },
        }
        return _json_safe(response)
    except RequestValidationError as error:
        return {"ok": False, "errors": [{"field": error.field, "message": error.message}]}
    except (ValueError, TypeError, ZeroDivisionError) as error:
        return {"ok": False, "errors": [{"field": "scenario", "message": str(error)}]}


__all__ = ("RequestValidationError", "analyze_acquisition")
