"""Regression tests for narrative presentation fixes (no scoring changes)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "public" / "python"))

import web_interface as wi  # noqa: E402


def build_request(owner_hours=2000, concentration=True):
    return {
        "practice": {
            "annual_revenue": 1000000,
            "asking_price": 1000000,
            "client_relationships": 200,
            "largest_client_revenue_percentage": 0.05 if concentration else None,
            "top_5_client_revenue_percentage": 0.15 if concentration else None,
            "top_10_client_revenue_percentage": 0.25 if concentration else None,
            "services": [
                {"name": "Tax", "recurring": True, "engagements": 300,
                 "annual_revenue": 600000,
                 "annual_owner_hours": owner_hours},
                {"name": "Bookkeeping", "recurring": True, "engagements": 100,
                 "annual_revenue": 400000,
                 "annual_owner_hours": None if owner_hours is None else 1000},
            ],
            "fixed_operating_costs": 100000,
            "staff_variable_costs": 300000,
            "owner_hourly_value": 100,
        },
        "financing": {
            "buyer_cash": 300000,
            "seller_note": {"amount": 400000, "annual_interest_rate": 0.06, "term_years": 5},
            "bank_loan": {"amount": 200000, "annual_interest_rate": 0.09, "term_years": 10,
                          "variable_rate": False, "fees": 5000},
            "earnout": {"maximum_amount": 100000, "term_years": 3},
        },
        "retention": {"first_year": 0.9, "ongoing": 0.95},
        "transition": {
            "seller_transition_months": 6,
            "stays_through_tax_season": True,
            "personal_client_introductions": True,
            "post_closing_availability_months": 6,
            "expected_key_staff_retention": 0.9,
            "seller_rapport": 4,
            "seller_commitment": 4,
            "cultural_fit": 4,
            "client_desirability": 4,
            "practice_organization": 4,
            "information_confidence": 4,
        },
    }


def overall(result):
    return " ".join(result["english_analysis"]["overall_assessment"])


def test_no_unresolved_claim_when_everything_is_known():
    result = wi.analyze_acquisition(build_request())
    assert result["ok"], result
    assert "unresolved" not in overall(result)


def test_owner_hours_unknown_names_only_owner_workload():
    result = wi.analyze_acquisition(build_request(owner_hours=None))
    assert result["ok"], result
    text = overall(result)
    assert "Owner workload information remains unresolved" in text
    assert "client concentration" not in text.lower()


def test_concentration_unknown_names_only_concentration():
    result = wi.analyze_acquisition(build_request(concentration=False))
    assert result["ok"], result
    text = overall(result)
    assert "Client concentration information remains unresolved" in text
    assert "owner workload" not in text.lower()


def test_both_unknown_names_both():
    result = wi.analyze_acquisition(build_request(owner_hours=None, concentration=False))
    assert result["ok"], result
    text = overall(result)
    assert "Owner workload and client concentration information remains unresolved" in text


def test_service_mix_language_is_objective():
    result = wi.analyze_acquisition(build_request())
    assert result["ok"], result
    service_lines = [s for s in result["english_analysis"]["strengths"] if "service" in s.lower()]
    for line in service_lines:
        assert "excessive dependence" not in line
        assert "well-diversified" not in line
