import {
  NumericField,
  RatingField,
  SegmentedYesNo,
  ToggleField,
  WhyThisMatters,
} from "@/components/form/Fields";
import { FieldGrid, SectionCard, StepIntro } from "./StepChrome";
import type { FormState } from "@/lib/analysis/formState";

export function StepTransition({
  state,
  update,
}: {
  state: FormState;
  update: (patch: Partial<FormState["transition"]>) => void;
}) {
  return (
    <div className="space-y-6">
      <StepIntro title="Transition &amp; fit">
        A practice can look good on paper and still go badly. This section captures how the handoff
        is expected to work and your own read on the seller, the staff, and the clients. Answer as
        the buyer you are, not as the buyer you wish you were.
      </StepIntro>

      <SectionCard
        title="Seller involvement"
        description="What the seller has actually committed to after closing."
      >
        <FieldGrid>
          <NumericField
            label="Seller transition period"
            suffix="mos"
            placeholder="6"
            value={state.transition.sellerTransitionMonths}
            onChange={(value) => update({ sellerTransitionMonths: value })}
            hint={
              <WhyThisMatters>
                Clients follow relationships. A seller who works alongside you for a full cycle
                gives clients a reason to stay and gives you time to learn the files.
              </WhyThisMatters>
            }
          />
          <NumericField
            label="Post-closing availability"
            suffix="mos"
            placeholder="12"
            value={state.transition.postClosingAvailabilityMonths}
            onChange={(value) => update({ postClosingAvailabilityMonths: value })}
            hint="Months the seller remains reachable for questions after the formal transition ends."
          />
        </FieldGrid>
        <div className="grid gap-5 sm:grid-cols-2">
          <SegmentedYesNo
            label="Seller stays through a full tax season"
            value={state.transition.staysThroughTaxSeason}
            onChange={(value) => update({ staysThroughTaxSeason: value })}
            hint="A complete busy season is the real test of a handoff in a tax-heavy practice."
          />
          <SegmentedYesNo
            label="Seller makes personal client introductions"
            value={state.transition.personalClientIntroductions}
            onChange={(value) => update({ personalClientIntroductions: value })}
            hint="A personal endorsement is far more effective than a transition letter."
          />
        </div>
      </SectionCard>

      <SectionCard title="Staff" description="Your expectation for the people who do the work.">
        <ToggleField
          label="Key staff retention is unknown"
          value={state.transition.keyStaffRetentionUnknown}
          onChange={(checked) => update({ keyStaffRetentionUnknown: checked })}
          hint="If you have not spoken with staff yet, mark it unknown. It will not be treated as zero."
        />
        {!state.transition.keyStaffRetentionUnknown ? (
          <NumericField
            label="Expected key staff retention"
            adornment="percent"
            placeholder="80"
            value={state.transition.expectedKeyStaffRetention}
            onChange={(value) => update({ expectedKeyStaffRetention: value })}
            className="max-w-xs"
          />
        ) : null}
      </SectionCard>

      <SectionCard
        title="Your judgment"
        description="Rate each factor from 1 (poor) to 5 (excellent) based on what you have seen so far."
      >
        <div className="grid gap-6 sm:grid-cols-2">
          <RatingField
            label="Rapport and trust with the seller"
            value={state.transition.sellerRapport}
            onChange={(value) => update({ sellerRapport: value })}
            hint="Deals live or die on candor during diligence and the months after closing."
          />
          <RatingField
            label="Seller's commitment to the transition"
            value={state.transition.sellerCommitment}
            onChange={(value) => update({ sellerCommitment: value })}
            hint="Enthusiasm in a meeting is not the same as obligations written into the agreement."
          />
          <RatingField
            label="Cultural and operational fit"
            value={state.transition.culturalFit}
            onChange={(value) => update({ culturalFit: value })}
            hint="Service standards, pricing posture, technology, and pace of work."
          />
          <RatingField
            label="Client desirability"
            value={state.transition.clientDesirability}
            onChange={(value) => update({ clientDesirability: value })}
            hint="Are these the clients you want: responsive, appropriately priced, and a fit for your services?"
          />
          <RatingField
            label="Practice organization"
            value={state.transition.practiceOrganization}
            onChange={(value) => update({ practiceOrganization: value })}
            hint="File quality, documented workflows, deadline tracking, and technology."
          />
          <RatingField
            label="Confidence in the information provided"
            value={state.transition.informationConfidence}
            onChange={(value) => update({ informationConfidence: value })}
            hint="How verifiable is what you have been told? Low confidence makes every other conclusion provisional."
          />
        </div>
      </SectionCard>
    </div>
  );
}
