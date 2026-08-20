/**
 * Presentation-only helpers for the results report.
 *
 * Nothing here recalculates, rescales, or reinterprets the analyzer's numbers.
 * These functions only decide how existing backend values are *labelled* and
 * whether a value is displayable at all.
 */

import type { AnalysisSuccess } from "./types";

/* ------------------------------------------------------------------ *
 * Internal field paths -> user-facing labels
 * ------------------------------------------------------------------ */

const STATIC_FIELD_LABELS: Record<string, string> = {
  "practice.staff_retention_sensitive_percentage": "Retention-sensitive share of staff costs",
  "practice.client_relationships": "Number of client relationships",
  "practice.largest_client_revenue_percentage": "Largest client revenue share",
  "practice.top_5_client_revenue_percentage": "Top five client revenue share",
  "practice.top_10_client_revenue_percentage": "Top ten client revenue share",
  "practice.annual_revenue": "Annual revenue",
  "practice.asking_price": "Asking price",
  "practice.owner_hourly_value": "Value of an owner hour",
  "practice.fixed_operating_costs": "Fixed operating costs",
  "practice.staff_variable_costs": "Staff costs",
  analysis_horizon: "Analysis horizon (years)",
  "financing.seller_note.amount": "Seller-note principal",
  "financing.bank_loan.amount": "Bank / SBA financing",
  "financing.earnout.maximum_amount": "Maximum earn-out",
};

const SERVICE_FIELD_LABELS: Record<string, string> = {
  annual_owner_hours: "owner hours",
  engagements: "number of engagements",
  annual_revenue: "annual revenue",
};

const FIELD_PATH_PATTERN =
  /\b(?:practice|financing)\.[A-Za-z0-9_]+(?:\[\d+\])?(?:\.[A-Za-z0-9_]+)*|\banalysis_horizon\b/g;

/** Translate one internal field path into a normal user-facing label. */
export function fieldLabel(field: string, serviceNames: string[] = []): string {
  const service = /^practice\.services\[(\d+)\]\.([A-Za-z0-9_]+)$/.exec(field);
  if (service) {
    const name = serviceNames[Number(service[1])] ?? `Service ${Number(service[1]) + 1}`;
    const attribute = SERVICE_FIELD_LABELS[service[2]] ?? service[2].replace(/_/g, " ");
    return `${name} — ${attribute}`;
  }
  if (STATIC_FIELD_LABELS[field]) return STATIC_FIELD_LABELS[field];
  const tail = field.split(".").pop() ?? field;
  const words = tail.replace(/_/g, " ").trim();
  return words.charAt(0).toUpperCase() + words.slice(1);
}

/** Replace any internal field paths embedded in a sentence with plain labels. */
export function humanizeFieldPaths(text: string, serviceNames: string[] = []): string {
  return text.replace(FIELD_PATH_PATTERN, (match) => fieldLabel(match, serviceNames));
}

/* ------------------------------------------------------------------ *
 * Due-diligence consolidation
 * ------------------------------------------------------------------ */

const PRIORITY_KEYWORDS = [
  "concentration",
  "retention",
  "client",
  "staff",
  "earn-out",
  "earnout",
  "owner hours",
  "debt",
  "bank",
  "seller",
  "transition",
];

function normalizeForDedupe(item: string): string {
  return item
    .toLowerCase()
    .replace(/[^a-z0-9 ]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

/**
 * Merge every due-diligence source into a single deduplicated, prioritized list.
 * The wording is the backend's; only ordering and duplicates are handled here.
 */
export function consolidateDueDiligence(
  groups: (string[] | undefined)[],
  serviceNames: string[] = [],
  limit = 8,
): string[] {
  const seen = new Set<string>();
  const items: string[] = [];
  for (const group of groups) {
    for (const raw of group ?? []) {
      const item = humanizeFieldPaths(raw.trim(), serviceNames);
      if (!item) continue;
      const key = normalizeForDedupe(item);
      if (!key || seen.has(key)) continue;
      seen.add(key);
      items.push(item);
    }
  }
  const rank = (item: string) => {
    const lower = item.toLowerCase();
    const index = PRIORITY_KEYWORDS.findIndex((keyword) => lower.includes(keyword));
    return index === -1 ? PRIORITY_KEYWORDS.length : index;
  };
  return items
    .map((item, index) => ({ item, index, rank: rank(item) }))
    .sort((a, b) => a.rank - b.rank || a.index - b.index)
    .slice(0, limit)
    .map((entry) => entry.item);
}

/* ------------------------------------------------------------------ *
 * Metric availability
 * ------------------------------------------------------------------ */

/** Owner-hour-dependent metrics are only meaningful when hours were supplied. */
export function ownerHoursKnown(result: AnalysisSuccess): boolean {
  return result.analysis.owner_labor_value !== null;
}

/**
 * "Not reached" must only be shown for a metric that was actually computed.
 * When owner hours are unknown the payback metrics cannot be computed at all.
 */
export function paybackDisplay(
  value: number | null | undefined,
  hoursKnown: boolean,
  horizonYears: number,
): string {
  if (!hoursKnown) return "N/A — owner hours unknown";
  if (value === null || value === undefined) return "N/A — not calculated";
  if (!Number.isFinite(value)) return `Not reached within ${horizonYears} years`;
  return `${value.toFixed(1)} yrs`;
}

/** One-decimal display of scoring weights and points, from the backend's rounded fields. */
export function displayWeight(component: {
  weight: number;
  display_weight?: number;
}): string {
  return (component.display_weight ?? component.weight).toFixed(1);
}

export function displayWeightedPoints(component: {
  weighted_points: number;
  display_weighted_points?: number;
}): string {
  return (component.display_weighted_points ?? component.weighted_points).toFixed(1);
}
