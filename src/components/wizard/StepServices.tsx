import { Checkbox } from "@/components/ui/checkbox";
import { NumericField, WhyThisMatters } from "@/components/form/Fields";
import { Callout, SectionCard, StepIntro } from "./StepChrome";
import { SERVICE_CATEGORIES, num, serviceRevenueTotal, type FormState } from "@/lib/analysis/formState";
import { money } from "@/lib/format";

export function StepServices({
  state,
  update,
}: {
  state: FormState;
  update: (index: number, patch: Partial<FormState["services"][number]>) => void;
}) {
  const entered = serviceRevenueTotal(state);
  const target = num(state.practice.annualRevenue);
  const difference = entered - target;
  const balanced = Math.abs(difference) < 0.01;

  return (
    <div className="space-y-6">
      <StepIntro title="Service mix">
        Select the services this practice actually performs and split its revenue across them.
        Different services behave differently: recurring compliance and bookkeeping work tends to
        stay, while one-off representation or project work usually does not repeat. Fee levels,
        staffing, seasonality, and owner involvement also vary sharply by service.
      </StepIntro>

      <Callout tone={balanced ? "success" : "warning"}>
        {balanced ? (
          <>Service revenue totals {money(entered)} and matches the annual revenue you entered.</>
        ) : (
          <>
            Service revenue currently totals <strong>{money(entered)}</strong> against annual revenue
            of <strong>{money(target)}</strong> — a difference of {money(Math.abs(difference))}. The
            analyzer requires these to match before it will run.
          </>
        )}
      </Callout>

      <div className="space-y-4">
        {state.services.map((service, index) => {
          const meta = SERVICE_CATEGORIES[index];
          return (
            <SectionCard key={service.name} title={service.name}>
              <label className="flex cursor-pointer items-start gap-3">
                <Checkbox
                  checked={service.enabled}
                  onCheckedChange={(checked) => update(index, { enabled: checked === true })}
                  className="mt-0.5 h-5 w-5 shrink-0"
                />
                <span className="min-w-0 text-sm text-muted-foreground">
                  The practice performs this work
                  <span className="ml-2 rounded-full bg-secondary px-2 py-0.5 text-xs font-medium text-secondary-foreground">
                    {service.recurring ? "Recurring" : "Nonrecurring"}
                  </span>
                </span>
              </label>

              {service.enabled ? (
                <div className="grid gap-5 sm:grid-cols-3">
                  <NumericField
                    label="Annual revenue"
                    adornment="currency"
                    value={service.annualRevenue}
                    onChange={(value) => update(index, { annualRevenue: value })}
                  />
                  <NumericField
                    label={meta?.countLabel ?? "Engagements"}
                    placeholder="Blank if unknown"
                    value={service.engagements}
                    onChange={(value) => update(index, { engagements: value })}
                  />
                  <NumericField
                    label="Annual owner hours"
                    suffix="hrs"
                    placeholder="Blank if unknown"
                    value={service.ownerHours}
                    onChange={(value) => update(index, { ownerHours: value })}
                  />
                </div>
              ) : null}
            </SectionCard>
          );
        })}
      </div>

      <SectionCard title="A note on owner hours">
        <p className="text-sm leading-relaxed text-muted-foreground">
          Owner hours are optional. If you leave them blank, the analyzer reports the affected
          metrics as unavailable rather than assuming a value.
        </p>
        <WhyThisMatters label="Why owner hours matter">
          Revenue per owner hour separates work that scales through staff from work that only the
          owner can do. A practice with strong revenue but very high owner hours is often harder to
          transition and harder to grow.
        </WhyThisMatters>
      </SectionCard>
    </div>
  );
}
