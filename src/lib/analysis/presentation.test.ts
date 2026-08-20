import { describe, expect, it } from "vitest";
import {
  consolidateDueDiligence,
  displayWeight,
  displayWeightedPoints,
  fieldLabel,
  humanizeFieldPaths,
  paybackDisplay,
} from "./presentation";

describe("fieldLabel", () => {
  it("translates internal field paths into user-facing labels", () => {
    expect(fieldLabel("practice.staff_retention_sensitive_percentage")).toBe(
      "Retention-sensitive share of staff costs",
    );
    expect(fieldLabel("practice.client_relationships")).toBe("Number of client relationships");
  });

  it("names service fields using the entered service name", () => {
    expect(fieldLabel("practice.services[1].annual_owner_hours", ["Tax", "Bookkeeping"])).toBe(
      "Bookkeeping — owner hours",
    );
  });

  it("falls back to a humanized tail for unmapped fields", () => {
    expect(fieldLabel("practice.some_new_field")).toBe("Some new field");
  });
});

describe("humanizeFieldPaths", () => {
  it("replaces embedded field paths inside sentences", () => {
    const out = humanizeFieldPaths(
      "Confirm practice.staff_retention_sensitive_percentage before closing.",
    );
    expect(out).toBe("Confirm Retention-sensitive share of staff costs before closing.");
    expect(out).not.toMatch(/practice\./);
  });
});

describe("consolidateDueDiligence", () => {
  it("merges sections, deduplicates, and caps the list", () => {
    const items = consolidateDueDiligence(
      [
        ["Confirm client concentration.", "Confirm client concentration."],
        ["confirm client concentration", "Confirm bank terms."],
        ["Review lease."],
      ],
      [],
      8,
    );
    expect(items).toContain("Confirm client concentration.");
    expect(items.filter((item) => item.toLowerCase().startsWith("confirm client"))).toHaveLength(1);
    expect(items.length).toBeLessThanOrEqual(8);
  });

  it("prioritizes material items and humanizes field paths", () => {
    const items = consolidateDueDiligence([
      ["Review practice.staff_retention_sensitive_percentage."],
      ["Verify client concentration detail."],
    ]);
    expect(items[0]).toBe("Verify client concentration detail.");
    expect(items.join(" ")).not.toMatch(/practice\./);
  });
});

describe("paybackDisplay", () => {
  it("reports N/A when owner hours are unknown", () => {
    expect(paybackDisplay(null, false, 5)).toBe("N/A — owner hours unknown");
    expect(paybackDisplay(3.2, false, 5)).toBe("N/A — owner hours unknown");
  });

  it("reports the horizon when payback is not reached", () => {
    expect(paybackDisplay(null, true, 5)).toBe("N/A — not calculated");
    expect(paybackDisplay(Infinity, true, 5)).toBe("Not reached within 5 years");
  });

  it("formats a reached payback to one decimal", () => {
    expect(paybackDisplay(3.25, true, 5)).toBe("3.3 yrs");
  });
});

describe("display weights", () => {
  it("prefers backend rounded display fields", () => {
    expect(displayWeight({ weight: 12.333333, display_weight: 12.3 })).toBe("12.3");
    expect(
      displayWeightedPoints({ weighted_points: 9.87654321, display_weighted_points: 9.9 }),
    ).toBe("9.9");
  });

  it("rounds raw values to one decimal when display fields are absent", () => {
    expect(displayWeight({ weight: 12.3456 })).toBe("12.3");
    expect(displayWeightedPoints({ weighted_points: 9.8765 })).toBe("9.9");
  });
});
