/**
 * TypeScript mirrors of the request/response contract defined by
 * `public/python/web_interface.py`. These are descriptions of the backend
 * contract only — no logic, defaults, or derived values belong here.
 */

export interface ServiceRequest {
  name: string;
  recurring: boolean;
  engagements: number | null;
  annual_revenue: number;
  annual_owner_hours: number | null;
}

export interface AnalysisRequest {
  practice: {
    annual_revenue: number;
    asking_price: number;
    client_relationships: number | null;
    /** Unique-client concentration measures as 0-1 rates; null means unknown. */
    largest_client_revenue_percentage: number | null;
    top_5_client_revenue_percentage: number | null;
    top_10_client_revenue_percentage: number | null;
    services: ServiceRequest[];
    fixed_operating_costs: number;
    staff_variable_costs: number;
    owner_hourly_value: number;
    staff_retention_sensitive_percentage?: number;
  };
  financing: {
    buyer_cash: number;
    seller_note: { amount: number; annual_interest_rate: number; term_years: number };
    bank_loan: {
      amount: number;
      annual_interest_rate: number;
      term_years: number;
      variable_rate: boolean;
      fees: number;
    };
    earnout: { maximum_amount: number; term_years: number };
  };
  retention: { first_year: number; ongoing: number };
  transition: {
    seller_transition_months: number;
    stays_through_tax_season: boolean;
    personal_client_introductions: boolean;
    post_closing_availability_months: number;
    expected_key_staff_retention: number | null;
    seller_rapport: number;
    seller_commitment: number;
    cultural_fit: number;
    client_desirability: number;
    practice_organization: number;
    information_confidence: number;
  };
  analysis_horizon?: number;
  assumptions?: AssumptionRecord[];
}

export interface AssumptionRecord {
  name: string;
  source: string;
  value: string;
  important?: boolean;
  uncertainty_note?: string;
}

export interface ScoreComponent {
  name: string;
  weight: number;
  score: number;
  value: string;
  weighted_points: number;
}

export interface QualityScore {
  score: number;
  band: string;
  components: ScoreComponent[];
  strengths: string[];
  concerns: string[];
  due_diligence: string[];
}

export interface YearResult {
  year: number;
  retention_rate: number;
  retained_revenue: number;
  staff_cost: number;
  operating_cash_flow: number;
  seller_note_payment: number;
  seller_principal: number;
  seller_interest: number;
  seller_balance: number;
  bank_payment: number;
  bank_principal: number;
  bank_interest: number;
  bank_balance: number;
  earnout_payment: number;
  net_cash_flow: number;
  target_owner_compensation: number | null;
  economic_profit: number | null;
  cumulative_cash_flow: number | null;
}

export interface Scenario {
  retention_rate: number;
  retained_clients: number | null;
  retained_revenue: number;
  annual_debt_payment: number;
  annual_bank_payment: number;
  annual_earnout_payment: number;
  annual_cash_flow: number;
  equity_payback_years: number | null;
  operating_cash_flow: number;
  actual_earnout: number;
  total_consideration: number;
  total_acquisition_cash_paid: number;
  cash_on_cash_return: number | null;
  recovery_years: number | null;
  owner_labor_value: number | null;
  economic_profit: number | null;
  effective_revenue_per_owner_hour: number | null;
  cash_on_cash_after_owner_labor: number | null;
  retention_rates: number[];
  total_acquisition_payback_years: number | null;
  total_seller_interest: number;
  total_bank_interest: number;
  years: YearResult[];
}

export interface ServiceCategoryAnalysis {
  name: string;
  recurring: boolean;
  engagements: number | null;
  annual_revenue: number;
  average_revenue_per_engagement: number | null;
  revenue_percentage: number;
  annual_owner_hours: number | null;
  revenue_per_owner_hour: number | null;
  year_1_retained_revenue: number;
  year_1_retained_owner_hours: number | null;
}

export interface ServiceSummary {
  total_revenue: number;
  total_owner_hours: number | null;
  recurring_revenue: number;
  nonrecurring_revenue: number;
  largest_service_share: number;
  top_three_share: number;
}

export interface AnalysisSuccess {
  ok: true;
  analysis: Scenario;
  scores: {
    financial_operational: QualityScore;
    transition_qualitative: QualityScore;
    overall: {
      score: number;
      weighting: { financial_operational: number; transition_qualitative: number };
    };
  };
  assumptions: {
    provided: AssumptionRecord[];
    applied_defaults: { field: string; value: number; source: string }[];
    unknowns: { field: string; effect: string }[];
  };
  english_analysis: {
    summary: string;
    attractive_factors: string[];
    financial_concerns: string[];
    transition_strengths: string[];
    transition_concerns: string[];
    priority_due_diligence: string[];
    scope_note: string;
  };
  cash_flow_projections: YearResult[];
  service_categories: ServiceCategoryAnalysis[];
  service_summary: ServiceSummary;
  financing: {
    terms: Record<string, number | boolean>;
    purchase_price: number;
    maximum_allocation: number;
    actual_consideration: number;
    actual_earnout: number;
    annual_bank_debt_service: number;
    annual_seller_debt_service: number;
    remaining_balances: { year: number; bank: number; seller: number }[];
  };
  transition: { inputs: Record<string, unknown>; result: QualityScore };
}

export interface AnalysisFailure {
  ok: false;
  errors: { field: string; message: string }[];
}

export type AnalysisResponse = AnalysisSuccess | AnalysisFailure;
