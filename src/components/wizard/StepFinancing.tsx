import { NumericField, SegmentedYesNo, WhyThisMatters } from "@/components/form/Fields";
import { Callout, FieldGrid, SectionCard, StepIntro } from "./StepChrome";
import { financingAllocationTotal, num, type FormState } from "@/lib/analysis/formState";
import { money } from "@/lib/format";

export function StepFinancing({
  state,
  update,
}: {
  state: FormState;
  update: (patch: Partial<FormState["financing"]>) => void;
}) {
  const allocated = financingAllocationTotal(state);
  const price = num(state.practice.askingPrice);
  const difference = allocated - price;
  const balanced = Math.abs(difference) < 0.01;

  return (
    <div className="space-y-6">
      <StepIntro title="Financing &amp; deal structure">
        How you pay matters as much as what you pay. Terms determine your annual debt service, how
        much cash you put at risk, and how much protection you carry if clients leave. Buyer cash,
        bank/SBA principal, seller principal, and the maximum earn-out must together equal the
        asking price.
      </StepIntro>

      <Callout tone={balanced ? "success" : "warning"}>
        {balanced ? (
          <>Your structure allocates {money(allocated)} and matches the asking price.</>
        ) : (
          <>
            Allocated so far: <strong>{money(allocated)}</strong> against an asking price of{" "}
            <strong>{money(price)}</strong> — {difference > 0 ? "over" : "short"} by{" "}
            {money(Math.abs(difference))}.
          </>
        )}
      </Callout>

      <SectionCard
        title="Cash at closing"
        description="The equity you personally put into the deal on day one."
      >
        <NumericField
          label="Buyer cash at closing"
          adornment="currency"
          placeholder="100,000"
          value={state.financing.buyerCash}
          onChange={(value) => update({ buyerCash: value })}
          className="max-w-sm"
          hint={
            <WhyThisMatters>
              Cash at closing is the capital you cannot recover if the transition disappoints. It
              also sets the base for your return on invested equity.
            </WhyThisMatters>
          }
        />
      </SectionCard>

      <SectionCard
        title="Seller financing"
        description="Principal the seller carries, typically repaid over several years."
      >
        <FieldGrid>
          <NumericField
            label="Seller note principal"
            adornment="currency"
            value={state.financing.sellerNoteAmount}
            onChange={(value) => update({ sellerNoteAmount: value })}
          />
          <NumericField
            label="Interest rate"
            adornment="percent"
            placeholder="6"
            value={state.financing.sellerNoteRate}
            onChange={(value) => update({ sellerNoteRate: value })}
          />
          <NumericField
            label="Term"
            suffix="yrs"
            placeholder="5"
            value={state.financing.sellerNoteYears}
            onChange={(value) => update({ sellerNoteYears: value })}
          />
        </FieldGrid>
        <WhyThisMatters label="Why seller financing changes the risk profile">
          A seller who carries paper stays financially interested in your success through the
          transition, and the payments are deferred rather than funded from your own capital.
        </WhyThisMatters>
      </SectionCard>

      <SectionCard title="Bank or SBA loan" description="Third-party acquisition debt, if any.">
        <FieldGrid>
          <NumericField
            label="Loan principal"
            adornment="currency"
            value={state.financing.bankAmount}
            onChange={(value) => update({ bankAmount: value })}
          />
          <NumericField
            label="Interest rate"
            adornment="percent"
            placeholder="9"
            value={state.financing.bankRate}
            onChange={(value) => update({ bankRate: value })}
          />
          <NumericField
            label="Term"
            suffix="yrs"
            placeholder="10"
            value={state.financing.bankYears}
            onChange={(value) => update({ bankYears: value })}
          />
          <NumericField
            label="Loan fees"
            adornment="currency"
            value={state.financing.bankFees}
            onChange={(value) => update({ bankFees: value })}
          />
        </FieldGrid>
        <SegmentedYesNo
          label="Variable interest rate"
          value={state.financing.bankVariableRate}
          onChange={(value) => update({ bankVariableRate: value })}
          hint="Variable-rate acquisition debt adds a second source of cash-flow risk on top of retention."
        />
      </SectionCard>

      <SectionCard
        title="Earn-out"
        description="Contingent consideration tied to retained revenue, paid only to the extent clients stay."
      >
        <FieldGrid>
          <NumericField
            label="Maximum earn-out"
            adornment="currency"
            value={state.financing.earnoutAmount}
            onChange={(value) => update({ earnoutAmount: value })}
          />
          <NumericField
            label="Earn-out term"
            suffix="yrs"
            value={state.financing.earnoutYears}
            onChange={(value) => update({ earnoutYears: value })}
          />
        </FieldGrid>
        <WhyThisMatters label="Why an earn-out shifts retention risk">
          An earn-out ties part of the price to the clients who actually remain, so weaker retention
          reduces what you pay rather than only what you earn.
        </WhyThisMatters>
      </SectionCard>
    </div>
  );
}
