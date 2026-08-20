import { NumericField, WhyThisMatters } from "@/components/form/Fields";
import { FieldGrid, SectionCard, StepIntro } from "./StepChrome";
import type { FormState } from "@/lib/analysis/formState";

export function StepBasics({
  state,
  update,
}: {
  state: FormState;
  update: (patch: Partial<FormState["practice"]>) => void;
}) {
  return (
    <div className="space-y-6">
      <StepIntro title="Practice basics">
        Start with the headline numbers. These anchor everything that follows: pricing relative to
        revenue, cash flow after costs, and how much of the work depends on the current owner.
      </StepIntro>

      <SectionCard
        title="Price and revenue"
        description="Use the seller's stated asking price and the most recent full year of collected revenue."
      >
        <FieldGrid>
          <NumericField
            label="Asking price"
            adornment="currency"
            placeholder="500,000"
            value={state.practice.askingPrice}
            onChange={(value) => update({ askingPrice: value })}
            hint={
              <WhyThisMatters>
                Price alone rarely decides a deal. A higher price can still work with favorable
                terms, while a low price can be painful if retention is weak or the work is heavily
                owner-dependent.
              </WhyThisMatters>
            }
          />
          <NumericField
            label="Annual practice revenue"
            adornment="currency"
            placeholder="500,000"
            value={state.practice.annualRevenue}
            onChange={(value) => update({ annualRevenue: value })}
            hint="Most recent full year. Your service-category revenue must add up to this figure."
          />
        </FieldGrid>
      </SectionCard>

      <SectionCard
        title="Clients and owner time"
        description="Two figures that reveal how concentrated the book is and how much of the value is the owner's own labor."
      >
        <FieldGrid>
          <NumericField
            label="Client relationships"
            placeholder="Leave blank if unknown"
            value={state.practice.clientRelationships}
            onChange={(value) => update({ clientRelationships: value })}
            hint={
              <WhyThisMatters>
                Revenue per client tells you whether you are buying a few substantial relationships
                or a high volume of small ones — they demand very different staffing and pricing.
                Leave blank if you genuinely do not know; unknown is not treated as zero.
              </WhyThisMatters>
            }
          />
          <NumericField
            label="Owner hourly value"
            adornment="currency"
            suffix="/hr"
            placeholder="90"
            value={state.practice.ownerHourlyValue}
            onChange={(value) => update({ ownerHourlyValue: value })}
            hint={
              <WhyThisMatters>
                What your own time is worth. The analysis charges the practice for the hours you
                would personally work, so you can see whether the deal produces real profit or just
                buys you a job.
              </WhyThisMatters>
            }
          />
        </FieldGrid>
      </SectionCard>
    </div>
  );
}
