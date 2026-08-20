import { NumericField, ToggleField, WhyThisMatters } from "@/components/form/Fields";
import { Callout, FieldGrid, SectionCard, StepIntro } from "./StepChrome";
import { BACKEND_DEFAULTS, type FormState } from "@/lib/analysis/formState";

export function StepRetentionCosts({
  state,
  updateRetention,
  updateCosts,
  updateHorizon,
}: {
  state: FormState;
  updateRetention: (patch: Partial<FormState["retention"]>) => void;
  updateCosts: (patch: Partial<FormState["costs"]>) => void;
  updateHorizon: (patch: Partial<FormState["horizon"]>) => void;
}) {
  return (
    <div className="space-y-6">
      <StepIntro title="Retention &amp; costs">
        Retention is usually the single most consequential assumption in a practice purchase, and
        the cost structure determines how much of the retained revenue you actually keep. Enter
        retention once here — it applies across the analysis.
      </StepIntro>

      <SectionCard
        title="Client retention"
        description="Your expectation for how much of the acquired revenue stays with you."
      >
        <FieldGrid>
          <NumericField
            label="First-year retention"
            adornment="percent"
            placeholder="90"
            value={state.retention.firstYear}
            onChange={(value) => updateRetention({ firstYear: value })}
            hint={
              <WhyThisMatters>
                The first year after closing is when clients decide whether to stay. A handful of
                percentage points here moves cash flow, debt coverage, and payback more than almost
                any other input.
              </WhyThisMatters>
            }
          />
          <NumericField
            label="Ongoing annual retention"
            adornment="percent"
            value={state.retention.ongoing}
            onChange={(value) => updateRetention({ ongoing: value, overrideOngoing: true })}
            hint={
              state.retention.overrideOngoing
                ? "Your entry replaces the analyzer's default."
                : `Analyzer default of ${BACKEND_DEFAULTS.ongoingRetentionPercent}% shown. Edit to override it.`
            }
          />
        </FieldGrid>
        {!state.retention.overrideOngoing ? (
          <Callout>
            The ongoing retention rate is an analyzer default until you change it. It is reported as
            an assumption on your results.
          </Callout>
        ) : null}
      </SectionCard>

      <SectionCard
        title="Operating and staffing costs"
        description="Annual costs of running the practice, excluding the buyer's own compensation and acquisition debt."
      >
        <FieldGrid>
          <NumericField
            label="Fixed operating costs"
            adornment="currency"
            placeholder="60,000"
            value={state.costs.fixedOperatingCosts}
            onChange={(value) => updateCosts({ fixedOperatingCosts: value })}
            hint="Rent, software, insurance, licensing, and other overhead that does not move with client volume."
          />
          <NumericField
            label="Staff costs"
            adornment="currency"
            placeholder="120,000"
            value={state.costs.staffVariableCosts}
            onChange={(value) => updateCosts({ staffVariableCosts: value })}
            hint={
              <WhyThisMatters>
                Staffing is both a cost and a risk. Experienced staff often hold the client
                relationships and the institutional knowledge; losing them during a transition can
                cost you clients as well as capacity.
              </WhyThisMatters>
            }
          />
        </FieldGrid>

        <ToggleField
          label="Override the retention-sensitive share of staff cost"
          value={state.costs.overrideStaffPercentage}
          onChange={(checked) => updateCosts({ overrideStaffPercentage: checked })}
          hint={`The analyzer assumes ${BACKEND_DEFAULTS.staffVariablePercent}% of staff cost flexes with the work you actually retain. Turn this on only if you have a better figure.`}
        />
        {state.costs.overrideStaffPercentage ? (
          <NumericField
            label="Retention-sensitive share of staff cost"
            adornment="percent"
            value={state.costs.staffRetentionSensitivePercentage}
            onChange={(value) => updateCosts({ staffRetentionSensitivePercentage: value })}
            className="max-w-xs"
          />
        ) : null}
      </SectionCard>

      <SectionCard title="Analysis horizon" description="How many years of projections to produce.">
        <ToggleField
          label="Override the default horizon"
          value={state.horizon.overridden}
          onChange={(checked) => updateHorizon({ overridden: checked })}
          hint={`Defaults to ${BACKEND_DEFAULTS.analysisHorizonYears} years. Permitted range is 3 to 10 years.`}
        />
        {state.horizon.overridden ? (
          <NumericField
            label="Years to project"
            suffix="yrs"
            value={state.horizon.years}
            onChange={(value) => updateHorizon({ years: value })}
            className="max-w-xs"
          />
        ) : null}
      </SectionCard>
    </div>
  );
}
