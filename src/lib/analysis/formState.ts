/**
 * Wizard form state and its translation into the backend request contract.
 *
 * This file performs no analysis. It only holds raw user entries as strings and
 * converts them into the JSON shape that `web_interface.analyze_acquisition`
 * expects (dollars as numbers, percentages as 0-1 rates, unknowns as null).
 */

import type { AnalysisRequest, AssumptionRecord, ServiceRequest } from "./types";

/** Mirrors DEFAULT_SERVICE_CATEGORIES in acquisition_engine.py. */
export const SERVICE_CATEGORIES: { name: string; recurring: boolean; countLabel: string }[] = [
  { name: "Individual tax returns", recurring: true, countLabel: "Number of individual returns" },
  { name: "Business tax returns", recurring: true, countLabel: "Number of business returns" },
  { name: "Nonprofit tax returns", recurring: true, countLabel: "Number of nonprofit returns" },
  { name: "Bookkeeping", recurring: true, countLabel: "Number of client engagements" },
  { name: "Payroll", recurring: true, countLabel: "Number of client engagements" },
  { name: "Tax planning/advisory", recurring: true, countLabel: "Number of engagements/clients" },
  { name: "Tax representation/notices", recurring: false, countLabel: "Number of engagements" },
  { name: "Other recurring services", recurring: true, countLabel: "Number of client engagements" },
  { name: "Other nonrecurring services", recurring: false, countLabel: "Number of engagements" },
];

/** Backend default values, surfaced in the UI so they are visible and editable. */
export const BACKEND_DEFAULTS = {
  ongoingRetentionPercent: 95, // DEFAULT_ONGOING_RETENTION
  staffVariablePercent: 80, // DEFAULT_STAFF_VARIABLE_PERCENTAGE
  analysisHorizonYears: 7, // web_interface default
};

export interface ServiceRow {
  name: string;
  recurring: boolean;
  enabled: boolean;
  annualRevenue: string;
  engagements: string;
  ownerHours: string;
}

export interface FormState {
  practice: {
    annualRevenue: string;
    askingPrice: string;
    clientRelationships: string;
    ownerHourlyValue: string;
    /** Optional unique-client concentration measures, as percentages. Blank = unknown. */
    largestClientPercent: string;
    topFiveClientPercent: string;
    topTenClientPercent: string;
  };
  services: ServiceRow[];
  costs: {
    fixedOperatingCosts: string;
    staffVariableCosts: string;
    staffRetentionSensitivePercentage: string;
    overrideStaffPercentage: boolean;
  };
  retention: {
    firstYear: string;
    ongoing: string;
    overrideOngoing: boolean;
  };
  horizon: {
    years: string;
    overridden: boolean;
  };
  financing: {
    buyerCash: string;
    sellerNoteAmount: string;
    sellerNoteRate: string;
    sellerNoteYears: string;
    bankAmount: string;
    bankRate: string;
    bankYears: string;
    bankVariableRate: boolean;
    bankFees: string;
    earnoutAmount: string;
    earnoutYears: string;
  };
  transition: {
    sellerTransitionMonths: string;
    staysThroughTaxSeason: boolean;
    personalClientIntroductions: boolean;
    postClosingAvailabilityMonths: string;
    expectedKeyStaffRetention: string;
    keyStaffRetentionUnknown: boolean;
    sellerRapport: number;
    sellerCommitment: number;
    culturalFit: number;
    clientDesirability: number;
    practiceOrganization: number;
    informationConfidence: number;
  };
}

export function createInitialFormState(): FormState {
  return {
    practice: {
      annualRevenue: "",
      askingPrice: "",
      clientRelationships: "",
      ownerHourlyValue: "",
    },
    services: SERVICE_CATEGORIES.map((category) => ({
      name: category.name,
      recurring: category.recurring,
      enabled: false,
      annualRevenue: "",
      engagements: "",
      ownerHours: "",
    })),
    costs: {
      fixedOperatingCosts: "",
      staffVariableCosts: "",
      staffRetentionSensitivePercentage: String(BACKEND_DEFAULTS.staffVariablePercent),
      overrideStaffPercentage: false,
    },
    retention: {
      firstYear: "",
      ongoing: String(BACKEND_DEFAULTS.ongoingRetentionPercent),
      overrideOngoing: false,
    },
    horizon: {
      years: String(BACKEND_DEFAULTS.analysisHorizonYears),
      overridden: false,
    },
    financing: {
      buyerCash: "",
      sellerNoteAmount: "",
      sellerNoteRate: "",
      sellerNoteYears: "",
      bankAmount: "",
      bankRate: "",
      bankYears: "",
      bankVariableRate: false,
      bankFees: "",
      earnoutAmount: "",
      earnoutYears: "",
    },
    transition: {
      sellerTransitionMonths: "",
      staysThroughTaxSeason: false,
      personalClientIntroductions: false,
      postClosingAvailabilityMonths: "",
      expectedKeyStaffRetention: "",
      keyStaffRetentionUnknown: false,
      sellerRapport: 3,
      sellerCommitment: 3,
      culturalFit: 3,
      clientDesirability: 3,
      practiceOrganization: 3,
      informationConfidence: 3,
    },
  };
}

export function num(value: string): number {
  const parsed = Number(String(value).replace(/[$,\s%]/g, ""));
  return Number.isFinite(parsed) ? parsed : 0;
}

export function optionalNum(value: string): number | null {
  return value.trim() === "" ? null : num(value);
}

export function activeServices(state: FormState): ServiceRow[] {
  return state.services.filter((service) => service.enabled);
}

export function serviceRevenueTotal(state: FormState): number {
  return activeServices(state).reduce((total, service) => total + num(service.annualRevenue), 0);
}

export function financingAllocationTotal(state: FormState): number {
  const { buyerCash, sellerNoteAmount, bankAmount, earnoutAmount } = state.financing;
  return num(buyerCash) + num(sellerNoteAmount) + num(bankAmount) + num(earnoutAmount);
}

function record(
  name: string,
  value: string,
  source: string,
  uncertaintyNote = "",
): AssumptionRecord {
  return { name, source, value, important: true, uncertainty_note: uncertaintyNote };
}

/**
 * Assumption records passed through to the backend response so the Results page
 * can distinguish user-entered values from retained analyzer defaults.
 * These are labels only; they do not influence any calculation.
 */
function buildAssumptionRecords(state: FormState): AssumptionRecord[] {
  const records: AssumptionRecord[] = [
    record("First-year client retention", `${num(state.retention.firstYear)}%`, "User entered"),
    record(
      "Ongoing annual retention",
      `${num(state.retention.ongoing)}%`,
      state.retention.overrideOngoing ? "User entered" : "Generic screening default",
      state.retention.overrideOngoing
        ? ""
        : "Retained the analyzer's ongoing retention default; confirm against the practice's history.",
    ),
    record(
      "Retention-sensitive share of staff cost",
      `${num(state.costs.staffRetentionSensitivePercentage)}%`,
      state.costs.overrideStaffPercentage ? "User entered" : "Generic screening default",
      state.costs.overrideStaffPercentage
        ? ""
        : "Retained the analyzer default for how much staff cost flexes with retained work.",
    ),
    record(
      "Analysis horizon",
      `${num(state.horizon.years)} years`,
      state.horizon.overridden ? "User entered" : "Generic screening default",
    ),
    record(
      "Owner hourly value",
      `$${num(state.practice.ownerHourlyValue)}`,
      "Buyer estimate",
      "Owner labor value is a buyer judgment and materially affects residual profit.",
    ),
  ];

  if (state.practice.clientRelationships.trim() === "") {
    records.push(
      record(
        "Client relationships",
        "Unknown",
        "Unknown",
        "Revenue-per-client analysis is unavailable without a client count.",
      ),
    );
  }
  if (state.transition.keyStaffRetentionUnknown) {
    records.push(
      record("Expected key staff retention", "Unknown", "Unknown", "Treated as unknown, not zero."),
    );
  }
  for (const service of activeServices(state)) {
    if (service.ownerHours.trim() === "") {
      records.push(
        record(`${service.name} — annual owner hours`, "Unknown", "Unknown", "Owner-hour metrics are unavailable for this service."),
      );
    }
  }
  return records;
}

/** Translate wizard state into the backend request contract. */
export function toAnalysisRequest(state: FormState): AnalysisRequest {
  const services: ServiceRequest[] = activeServices(state).map((service) => ({
    name: service.name,
    recurring: service.recurring,
    engagements: optionalNum(service.engagements),
    annual_revenue: num(service.annualRevenue),
    annual_owner_hours: optionalNum(service.ownerHours),
  }));

  const request: AnalysisRequest = {
    practice: {
      annual_revenue: num(state.practice.annualRevenue),
      asking_price: num(state.practice.askingPrice),
      client_relationships: optionalNum(state.practice.clientRelationships),
      services,
      fixed_operating_costs: num(state.costs.fixedOperatingCosts),
      staff_variable_costs: num(state.costs.staffVariableCosts),
      owner_hourly_value: num(state.practice.ownerHourlyValue),
    },
    financing: {
      buyer_cash: num(state.financing.buyerCash),
      seller_note: {
        amount: num(state.financing.sellerNoteAmount),
        annual_interest_rate: num(state.financing.sellerNoteRate) / 100,
        term_years: num(state.financing.sellerNoteYears),
      },
      bank_loan: {
        amount: num(state.financing.bankAmount),
        annual_interest_rate: num(state.financing.bankRate) / 100,
        term_years: num(state.financing.bankYears),
        variable_rate: state.financing.bankVariableRate,
        fees: num(state.financing.bankFees),
      },
      earnout: {
        maximum_amount: num(state.financing.earnoutAmount),
        term_years: num(state.financing.earnoutYears),
      },
    },
    retention: {
      first_year: num(state.retention.firstYear) / 100,
      ongoing: num(state.retention.ongoing) / 100,
    },
    transition: {
      seller_transition_months: num(state.transition.sellerTransitionMonths),
      stays_through_tax_season: state.transition.staysThroughTaxSeason,
      personal_client_introductions: state.transition.personalClientIntroductions,
      post_closing_availability_months: num(state.transition.postClosingAvailabilityMonths),
      expected_key_staff_retention: state.transition.keyStaffRetentionUnknown
        ? null
        : num(state.transition.expectedKeyStaffRetention) / 100,
      seller_rapport: state.transition.sellerRapport,
      seller_commitment: state.transition.sellerCommitment,
      cultural_fit: state.transition.culturalFit,
      client_desirability: state.transition.clientDesirability,
      practice_organization: state.transition.practiceOrganization,
      information_confidence: state.transition.informationConfidence,
    },
    assumptions: buildAssumptionRecords(state),
  };

  // Only send overrides so the backend can report which defaults it applied.
  if (state.costs.overrideStaffPercentage) {
    request.practice.staff_retention_sensitive_percentage =
      num(state.costs.staffRetentionSensitivePercentage) / 100;
  }
  if (state.horizon.overridden) {
    request.analysis_horizon = num(state.horizon.years);
  }
  return request;
}
