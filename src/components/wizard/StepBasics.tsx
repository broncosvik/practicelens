import { NumericField, ValueNote, WhyThisMatters } from "@/components/form/Fields";
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
            note={<ValueNote variant="suggested">500,000 — required, nothing is assumed</ValueNote>}
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
            note={<ValueNote variant="suggested">500,000 — required, nothing is assumed</ValueNote>}
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
            label="Number of client relationships"
            placeholder="Leave blank if unknown"
            value={state.practice.clientRelationships}
            onChange={(value) => update({ clientRelationships: value })}
            note={<ValueNote variant="optional">blank stays Unknown, never 0</ValueNote>}
            hint={
              <>
                <p>
                  Count unique client relationships, not total returns or service engagements. One
                  client may have an individual return, a business return, payroll, and other
                  services.
                </p>
                <WhyThisMatters>
                  Revenue per client tells you whether you are buying a few substantial
                  relationships or a high volume of small ones — they demand very different staffing
                  and pricing. Leave blank if you genuinely do not know; unknown is not treated as
                  zero.
                </WhyThisMatters>
              </>
            }
          />
          <NumericField
            label="Owner hourly value"
            adornment="currency"
            suffix="/hr"
            placeholder="90"
            value={state.practice.ownerHourlyValue}
            onChange={(value) => update({ ownerHourlyValue: value })}
            note={<ValueNote variant="suggested">90/hr — required, nothing is assumed</ValueNote>}
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

      <SectionCard
        title="Client concentration (optional)"
        description="Client concentration measures how much of the acquired book's revenue comes from its largest individual client relationships across all services."
      >
        <p className="text-sm leading-relaxed text-muted-foreground">
          These measure unique client relationships, not service categories. The same client may
          generate revenue from several services; all of that revenue counts toward that one
          relationship. Leave any of them blank if you do not have the detail — blank stays Unknown
          and is excluded from scoring rather than treated as 0%.
        </p>
        <div className="grid gap-5 sm:grid-cols-3">
          <NumericField
            label="Largest single client"
            adornment="percent"
            placeholder="Blank if unknown"
            value={state.practice.largestClientPercent}
            onChange={(value) => update({ largestClientPercent: value })}
            note={<ValueNote variant="optional">blank stays Unknown</ValueNote>}
          />
          <NumericField
            label="Top 5 clients"
            adornment="percent"
            placeholder="Blank if unknown"
            value={state.practice.topFiveClientPercent}
            onChange={(value) => update({ topFiveClientPercent: value })}
            note={<ValueNote variant="optional">blank stays Unknown</ValueNote>}
          />
          <NumericField
            label="Top 10 clients"
            adornment="percent"
            placeholder="Blank if unknown"
            value={state.practice.topTenClientPercent}
            onChange={(value) => update({ topTenClientPercent: value })}
            note={<ValueNote variant="optional">blank stays Unknown</ValueNote>}
          />
        </div>
        <p className="text-xs leading-relaxed text-muted-foreground">
          Any values you provide must satisfy largest client ≤ top 5 ≤ top 10 ≤ 100%.
        </p>
      </SectionCard>
    </div>
  );
}
