import { useMemo } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  ClipboardList,
  Info,
  Printer,
  Pencil,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { BrandLogo } from "@/components/BrandLogo";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Separator } from "@/components/ui/separator";
import { analysisDate, money, number as formatNumber, percent } from "@/lib/format";
import {
  consolidateDueDiligence,
  displayWeight,
  displayWeightedPoints,
  fieldLabel,
  humanizeFieldPaths,
  ownerHoursKnown,
  paybackDisplay,
} from "@/lib/analysis/presentation";
import type { AnalysisSuccess, QualityScore } from "@/lib/analysis/types";

function ScoreDial({
  score,
  label,
  band,
  tone,
  large,
}: {
  score: number;
  label: string;
  band: string;
  tone: "primary" | "accent";
  large?: boolean;
}) {
  const stroke = tone === "primary" ? "var(--color-primary)" : "var(--color-accent)";
  const size = large ? 168 : 128;
  const radius = large ? 74 : 56;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - Math.max(0, Math.min(100, score)) / 100);

  return (
    <div className="flex flex-col items-center gap-3 text-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} role="img" aria-label={`${label}: ${score} out of 100`}>
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="var(--color-border)"
            strokeWidth={large ? 12 : 10}
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={stroke}
            strokeWidth={large ? 12 : 10}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            transform={`rotate(-90 ${size / 2} ${size / 2})`}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={large ? "text-5xl font-semibold" : "text-3xl font-semibold"}>{score}</span>
          <span className="text-xs text-muted-foreground">out of 100</span>
        </div>
      </div>
      <div>
        <p className="text-sm font-medium">{label}</p>
        <p className="text-sm text-muted-foreground">{band}</p>
      </div>
    </div>
  );
}

function ComponentTable({ score }: { score: QualityScore }) {
  return (
    <div className="overflow-hidden rounded-lg border border-border">
      <table className="w-full text-sm">
        <thead className="bg-surface text-left text-xs uppercase tracking-wide text-muted-foreground">
          <tr>
            <th className="px-3 py-2 font-medium">Factor</th>
            <th className="px-3 py-2 font-medium">Measured</th>
            <th className="px-3 py-2 text-right font-medium">Weight</th>
            <th className="px-3 py-2 text-right font-medium">Points</th>
          </tr>
        </thead>
        <tbody>
          {score.components.map((component) => (
            <tr key={component.name} className="border-t border-border align-top">
              <td className="px-3 py-2 font-medium">{component.name}</td>
              <td className="px-3 py-2 text-muted-foreground">{component.value}</td>
              <td className="px-3 py-2 text-right tabular-nums text-muted-foreground">
                {displayWeight(component)}
              </td>
              <td className="px-3 py-2 text-right tabular-nums">
                {displayWeightedPoints(component)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function PointList({
  title,
  items,
  tone,
}: {
  title: string;
  items: string[];
  tone: "positive" | "negative" | "neutral";
}) {
  if (items.length === 0) return null;
  const Icon = tone === "positive" ? CheckCircle2 : tone === "negative" ? AlertTriangle : ClipboardList;
  const iconClass =
    tone === "positive" ? "text-success" : tone === "negative" ? "text-warning" : "text-primary";
  return (
    <div className="print-block space-y-2">
      <h4 className="text-sm font-semibold">{title}</h4>
      <ul className="space-y-2">
        {items.map((item) => (
          <li key={item} className="flex gap-2 text-sm leading-relaxed">
            <Icon className={`mt-0.5 h-4 w-4 shrink-0 ${iconClass}`} aria-hidden />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function Metric({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="print-block rounded-lg border border-border bg-card p-4">
      <p className="text-xs uppercase tracking-wide text-muted-foreground">{label}</p>
      <p className="mt-1 text-xl font-semibold tabular-nums">{value}</p>
      {hint ? <p className="mt-1 text-xs leading-relaxed text-muted-foreground">{hint}</p> : null}
    </div>
  );
}

function Section({
  id,
  title,
  description,
  children,
  breakBefore,
}: {
  id: string;
  title: string;
  description?: string;
  children: React.ReactNode;
  breakBefore?: boolean;
}) {
  return (
    <section id={id} className={breakBefore ? "print-page-break scroll-mt-24" : "scroll-mt-24"}>
      <Card className="border-border/80 shadow-card print-block">
        <CardHeader>
          <CardTitle className="text-lg sm:text-xl">{title}</CardTitle>
          {description ? <CardDescription>{description}</CardDescription> : null}
        </CardHeader>
        <CardContent className="space-y-5">{children}</CardContent>
      </Card>
    </section>
  );
}

const SOURCE_TONE: Record<string, string> = {
  "User entered": "bg-success/15 text-foreground border-success/40",
  "Buyer estimate": "bg-primary/10 text-foreground border-primary/30",
  "Context-derived default": "bg-warning/15 text-foreground border-warning/40",
  "Generic screening default": "bg-warning/15 text-foreground border-warning/40",
  Unknown: "bg-muted text-muted-foreground border-border",
};

export function ResultsView({
  result,
  onEdit,
}: {
  result: AnalysisSuccess;
  onEdit: () => void;
}) {
  const { scores, analysis, english_analysis: narrative, financing, service_summary: summary } = result;

  // The backend is authoritative for every sentence below; nothing is generated here.
  const overallAssessment =
    narrative.overall_assessment && narrative.overall_assessment.length > 0
      ? narrative.overall_assessment
      : [narrative.summary];
  const serviceNames = result.service_categories.map((service) => service.name);
  const strengths = (narrative.strengths ?? narrative.attractive_factors).map((item) =>
    humanizeFieldPaths(item, serviceNames),
  );
  const risks = (narrative.weaknesses_risks ?? narrative.financial_concerns).map((item) =>
    humanizeFieldPaths(item, serviceNames),
  );
  // One consolidated, deduplicated diligence list across narrative and both score sections.
  const dueDiligence = consolidateDueDiligence(
    [
      narrative.key_due_diligence_questions ?? narrative.priority_due_diligence,
      scores.financial_operational.due_diligence,
      scores.transition_qualitative.due_diligence,
    ],
    serviceNames,
  );

  const hoursKnown = ownerHoursKnown(result);
  const horizonYears = result.cash_flow_projections.length;

  const concentrationComponent = scores.financial_operational.components.find(
    (component) => component.name === "Actual client concentration",
  );
  const concentrationKnown = Boolean(
    concentrationComponent && concentrationComponent.value !== "Excluded",
  );
  const serviceMixComponent = scores.financial_operational.components.find(
    (component) => component.name === "Service mix diversification",
  );

  const cashFlowData = useMemo(
    () =>
      result.cash_flow_projections.map((year) => ({
        name: `Yr ${year.year}`,
        operating: Math.round(year.operating_cash_flow),
        net: Math.round(year.net_cash_flow),
      })),
    [result.cash_flow_projections],
  );

  const serviceData = useMemo(
    () =>
      result.service_categories.map((service) => ({
        name: service.name,
        share: Number((service.revenue_percentage * 100).toFixed(1)),
        revenue: service.annual_revenue,
        recurring: service.recurring,
      })),
    [result.service_categories],
  );

  return (
    <div className="space-y-8">
      {/* Print-only report header */}
      <div className="print-only mb-6 border-b border-border pb-4">
        <div className="flex items-center justify-between gap-6">
          <BrandLogo className="h-12 w-auto" />
          <div className="text-right">
            <p className="text-lg font-semibold">Accounting Practice Acquisition Analyzer</p>
            <p className="text-sm text-muted-foreground">Analysis prepared {analysisDate()}</p>
          </div>
        </div>
      </div>

      <div className="no-print flex flex-col gap-3 rounded-xl border border-border bg-surface p-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0">
          <h3 className="text-base font-semibold">Save your analysis</h3>
          <p className="text-sm leading-relaxed text-muted-foreground">
            Download or save a copy of this analysis for your records. You can return to an earlier
            section, revise your assumptions, and regenerate the results.
          </p>
        </div>
        <div className="flex shrink-0 flex-wrap gap-2">
          <Button variant="outline" onClick={onEdit} className="min-h-11">
            <Pencil className="mr-2 h-4 w-4" aria-hidden />
            Revise answers
          </Button>
          <Button onClick={() => window.print()} className="min-h-11">
            <Printer className="mr-2 h-4 w-4" aria-hidden />
            Print / Save as PDF
          </Button>
        </div>
      </div>

      {/* Overall + component scores */}
      <Section
        id="overall"
        title="Overall assessment"
        description={`Weighted ${percent(scores.overall.weighting.financial_operational, 0)} financial/operational and ${percent(scores.overall.weighting.transition_qualitative, 0)} transition/qualitative.`}
      >
        <div className="grid gap-8 md:grid-cols-[auto_1fr] md:items-center">
          <ScoreDial
            score={scores.overall.score}
            label="Overall acquisition score"
            band={`${scores.financial_operational.band} · ${scores.transition_qualitative.band}`}
            tone="primary"
            large
          />
          <div className="prose-report space-y-3 text-sm leading-relaxed sm:text-base">
            {overallAssessment.map((paragraph) => (
              <p key={paragraph}>{paragraph}</p>
            ))}
          </div>
        </div>

        <Separator />

        <div className="grid gap-6 sm:grid-cols-2">
          <div className="print-block rounded-xl border border-primary/25 bg-primary/5 p-5">
            <ScoreDial
              score={scores.financial_operational.score}
              label="Financial / operational"
              band={scores.financial_operational.band}
              tone="primary"
            />
          </div>
          <div className="print-block rounded-xl border border-accent/30 bg-accent/5 p-5">
            <ScoreDial
              score={scores.transition_qualitative.score}
              label="Transition / qualitative"
              band={scores.transition_qualitative.band}
              tone="accent"
            />
          </div>
        </div>
        <p className="text-xs leading-relaxed text-muted-foreground">
          These two scores are deliberately separate. A financially attractive practice can still
          carry serious transition or fit risk, and a well-supported handoff cannot rescue economics
          that do not work.
        </p>

        <Accordion type="multiple" className="no-print">
          <AccordionItem value="financial">
            <AccordionTrigger className="text-sm">
              Financial / operational score detail
            </AccordionTrigger>
            <AccordionContent>
              <ComponentTable score={scores.financial_operational} />
            </AccordionContent>
          </AccordionItem>
          <AccordionItem value="transition">
            <AccordionTrigger className="text-sm">
              Transition / qualitative score detail
            </AccordionTrigger>
            <AccordionContent>
              <ComponentTable score={scores.transition_qualitative} />
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </Section>

      {/* Cash flow */}
      <Section
        id="cash-flow"
        title="Cash flow"
        description="Retained revenue less operating and staffing costs, then acquisition debt and earn-out payments."
      >
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Metric label="Year 1 operating cash flow" value={money(analysis.operating_cash_flow)} />
          <Metric label="Year 1 net cash flow" value={money(analysis.annual_cash_flow)} hint="After debt service and earn-out." />
          <Metric
            label="Target owner compensation"
            value={money(analysis.owner_labor_value)}
            hint="Value of the hours you would personally work."
          />
          <Metric
            label="Residual ownership profit"
            value={money(analysis.economic_profit)}
            hint="What the practice earns beyond paying you for your time."
          />
          <Metric label="Retained revenue (year 1)" value={money(analysis.retained_revenue)} />
          <Metric
            label="Year 1 cash return on buyer equity, before owner labor"
            value={percent(analysis.cash_on_cash_return)}
            hint={
              hoursKnown
                ? "Year 1 net cash flow divided by buyer cash at closing. Owner labor is not deducted here; see residual ownership profit."
                : "Year 1 net cash flow divided by buyer cash at closing. Owner labor has not been valued because owner hours are unknown, so this is not a labor-adjusted investment return."
            }
          />
          <Metric
            label="Equity payback"
            value={paybackDisplay(analysis.equity_payback_years, hoursKnown, horizonYears)}
            hint="Years for residual ownership profit to repay buyer cash at closing."
          />
          <Metric
            label="Total acquisition payback"
            value={paybackDisplay(
              analysis.total_acquisition_payback_years,
              hoursKnown,
              horizonYears,
            )}
            hint="Years for ownership cash flow to repay total acquisition cash outflows."
          />
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={cashFlowData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
              <XAxis dataKey="name" tickLine={false} axisLine={false} fontSize={12} />
              <YAxis
                tickFormatter={(value: number) => `$${Math.round(value / 1000)}k`}
                tickLine={false}
                axisLine={false}
                fontSize={12}
                width={56}
              />
              <Tooltip
                formatter={(value: number, name: string) => [
                  money(value),
                  name === "operating" ? "Operating cash flow" : "Net cash flow",
                ]}
                contentStyle={{
                  background: "var(--color-card)",
                  border: "1px solid var(--color-border)",
                  borderRadius: 8,
                  fontSize: 12,
                }}
              />
              <Bar dataKey="operating" fill="var(--color-chart-1)" radius={[4, 4, 0, 0]} />
              <Bar dataKey="net" fill="var(--color-chart-2)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="-mx-2 overflow-x-auto px-2">
          <table className="w-full min-w-[640px] text-sm">
            <thead className="bg-surface text-left text-xs uppercase tracking-wide text-muted-foreground">
              <tr>
                <th className="px-3 py-2 font-medium">Year</th>
                <th className="px-3 py-2 font-medium">Retention</th>
                <th className="px-3 py-2 text-right font-medium">Retained revenue</th>
                <th className="px-3 py-2 text-right font-medium">Operating CF</th>
                <th className="px-3 py-2 text-right font-medium">Debt service</th>
                <th className="px-3 py-2 text-right font-medium">Earn-out</th>
                <th className="px-3 py-2 text-right font-medium">Net cash flow</th>
              </tr>
            </thead>
            <tbody>
              {result.cash_flow_projections.map((year) => (
                <tr key={year.year} className="border-t border-border">
                  <td className="px-3 py-2 font-medium">{year.year}</td>
                  <td className="px-3 py-2 text-muted-foreground">{percent(year.retention_rate)}</td>
                  <td className="px-3 py-2 text-right tabular-nums">{money(year.retained_revenue)}</td>
                  <td className="px-3 py-2 text-right tabular-nums">{money(year.operating_cash_flow)}</td>
                  <td className="px-3 py-2 text-right tabular-nums">
                    {money(year.seller_note_payment + year.bank_payment)}
                  </td>
                  <td className="px-3 py-2 text-right tabular-nums">{money(year.earnout_payment)}</td>
                  <td className="px-3 py-2 text-right font-medium tabular-nums">
                    {money(year.net_cash_flow)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>

      {/* Financing risk */}
      <Section
        id="financing"
        title="Financing risk"
        description="How the deal structure converts the purchase price into obligations."
        breakBefore
      >
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Metric label="Purchase price" value={money(financing.purchase_price)} />
          <Metric
            label="Buyer cash paid at closing"
            value={money(Number(financing.terms['down_payment'] ?? 0))}
            hint="Your own equity funded at closing. Excludes borrowed funds and future payments."
          />
          <Metric
            label="Bank / SBA financing"
            value={money(Number(financing.terms['bank_loan'] ?? 0))}
            hint="Borrowed at closing and repaid over time; not buyer cash."
          />
          <Metric
            label="Seller-note principal"
            value={money(Number(financing.terms['seller_note'] ?? 0))}
            hint="Deferred principal owed to the seller; not paid at closing."
          />
          <Metric
            label="Maximum earn-out"
            value={money(Number(financing.terms['earnout_total'] ?? 0))}
            hint="Payable only at full retention; contingent, not paid at closing."
          />
          <Metric
            label="Expected earn-out"
            value={money(financing.actual_earnout)}
            hint="Earn-out expected to be earned at your retention assumption."
          />
          <Metric
            label="Expected total consideration"
            value={money(financing.actual_consideration)}
            hint="Purchase price adjusted for the earn-out expected to be earned. Excludes interest."
          />
          <Metric label="Annual bank debt service" value={money(financing.annual_bank_debt_service)} />
          <Metric label="Annual seller debt service" value={money(financing.annual_seller_debt_service)} />
          <Metric
            label="Total acquisition cash outflows over time"
            value={money(analysis.total_acquisition_cash_paid)}
            hint="Buyer cash at closing plus all debt service, fees, and expected earn-out payments across the analysis horizon."
          />
          <Metric label="Total seller interest" value={money(analysis.total_seller_interest)} />
          <Metric label="Total bank interest" value={money(analysis.total_bank_interest)} />
        </div>

        <div className="-mx-2 overflow-x-auto px-2">
          <table className="w-full min-w-[420px] text-sm">
            <thead className="bg-surface text-left text-xs uppercase tracking-wide text-muted-foreground">
              <tr>
                <th className="px-3 py-2 font-medium">Year</th>
                <th className="px-3 py-2 text-right font-medium">Bank balance</th>
                <th className="px-3 py-2 text-right font-medium">Seller balance</th>
              </tr>
            </thead>
            <tbody>
              {financing.remaining_balances.map((balance) => (
                <tr key={balance.year} className="border-t border-border">
                  <td className="px-3 py-2 font-medium">{balance.year}</td>
                  <td className="px-3 py-2 text-right tabular-nums">{money(balance.bank)}</td>
                  <td className="px-3 py-2 text-right tabular-nums">{money(balance.seller)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>

      {/* Client concentration — dependence on individual client relationships */}
      <Section
        id="client-concentration"
        title="Client concentration"
        description="Dependence on particular client relationships, measured across all services. This is not the same as service mix diversification."
      >
        {concentrationKnown && concentrationComponent ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <Metric
              label="Concentration data supplied"
              value={concentrationComponent.value}
              hint="Largest single client, top 5, and top 10 shares of acquired-book revenue."
            />
            <Metric
              label="Concentration score"
              value={`${Math.round(concentrationComponent.score)} / 100`}
              hint="Scored by the analyzer from the measures you provided."
            />
            <Metric
              label="Weight in the financial score"
              value={String(concentrationComponent.display_weight ?? concentrationComponent.weight)}
              hint={`Contributed ${(concentrationComponent.display_weighted_points ?? concentrationComponent.weighted_points).toFixed(1)} points.`}
            />
          </div>
        ) : (
          <div className="print-block rounded-lg border border-border bg-surface p-4 text-sm leading-relaxed text-muted-foreground">
            Client concentration not provided. The analyzer excluded it from scoring rather than
            assuming a value — it is not treated as 0% or as low risk.
          </div>
        )}
        <p className="text-xs leading-relaxed text-muted-foreground">
          Client concentration measures dependence on particular client relationships. Service mix
          diversification, shown below, measures dependence on particular types of work. One client
          may buy several services; all of that revenue belongs to the single relationship.
        </p>
      </Section>

      {/* Service mix */}
      <Section
        id="service-mix"
        title="Service mix analysis"
        description="Dependence on particular types of services, and how each category carries into year one. This is not client concentration."
      >
        {serviceMixComponent ? (
          <p className="text-xs leading-relaxed text-muted-foreground">
            Analyzer service mix diversification: {serviceMixComponent.value} —{" "}
            {Math.round(serviceMixComponent.score)} / 100.
          </p>
        ) : null}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Metric label="Recurring revenue" value={money(summary.recurring_revenue)} />
          <Metric label="Nonrecurring revenue" value={money(summary.nonrecurring_revenue)} />
          <Metric label="Largest service share" value={percent(summary.largest_service_share)} />
          <Metric label="Top three share" value={percent(summary.top_three_share)} />
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={serviceData} layout="vertical" margin={{ top: 4, right: 16, left: 8, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" horizontal={false} />
              <XAxis type="number" unit="%" tickLine={false} axisLine={false} fontSize={12} />
              <YAxis
                type="category"
                dataKey="name"
                width={120}
                tickLine={false}
                axisLine={false}
                fontSize={11}
              />
              <Tooltip
                formatter={(value: number) => [`${value}% of revenue`, "Share"]}
                contentStyle={{
                  background: "var(--color-card)",
                  border: "1px solid var(--color-border)",
                  borderRadius: 8,
                  fontSize: 12,
                }}
              />
              <Bar dataKey="share" radius={[0, 4, 4, 0]}>
                {serviceData.map((entry) => (
                  <Cell
                    key={entry.name}
                    fill={entry.recurring ? "var(--color-chart-2)" : "var(--color-chart-3)"}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="-mx-2 overflow-x-auto px-2">
          <table className="w-full min-w-[720px] text-sm">
            <thead className="bg-surface text-left text-xs uppercase tracking-wide text-muted-foreground">
              <tr>
                <th className="px-3 py-2 font-medium">Service</th>
                <th className="px-3 py-2 text-right font-medium">Revenue</th>
                <th className="px-3 py-2 text-right font-medium">Share</th>
                <th className="px-3 py-2 text-right font-medium">Engagements</th>
                <th className="px-3 py-2 text-right font-medium">Avg fee</th>
                <th className="px-3 py-2 text-right font-medium">Rev / owner hr</th>
                <th className="px-3 py-2 text-right font-medium">Yr 1 retained</th>
              </tr>
            </thead>
            <tbody>
              {result.service_categories.map((service) => (
                <tr key={service.name} className="border-t border-border">
                  <td className="px-3 py-2">
                    <span className="font-medium">{service.name}</span>
                    <Badge variant="outline" className="ml-2 text-[10px]">
                      {service.recurring ? "Recurring" : "One-off"}
                    </Badge>
                  </td>
                  <td className="px-3 py-2 text-right tabular-nums">{money(service.annual_revenue)}</td>
                  <td className="px-3 py-2 text-right tabular-nums">
                    {percent(service.revenue_percentage)}
                  </td>
                  <td className="px-3 py-2 text-right tabular-nums">
                    {service.engagements === null ? "—" : formatNumber(service.engagements)}
                  </td>
                  <td className="px-3 py-2 text-right tabular-nums">
                    {money(service.average_revenue_per_engagement)}
                  </td>
                  <td className="px-3 py-2 text-right tabular-nums">
                    {money(service.revenue_per_owner_hour)}
                  </td>
                  <td className="px-3 py-2 text-right tabular-nums">
                    {money(service.year_1_retained_revenue)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>

      {/* Assumptions */}
      <Section
        id="assumptions"
        title="Assumptions used"
        description="Which figures you supplied, which were estimates, and which the analyzer defaulted or treated as unknown."
        breakBefore
      >
        <div className="space-y-3">
          {result.assumptions.provided.map((assumption) => (
            <div
              key={`${assumption.name}-${assumption.value}`}
              className="print-block grid gap-2 rounded-lg border border-border bg-card p-4 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-start"
            >
              <div className="min-w-0">
                <p className="text-sm font-medium">{assumption.name}</p>
                <p className="text-sm text-muted-foreground">{assumption.value}</p>
                {assumption.uncertainty_note ? (
                  <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
                    {assumption.uncertainty_note}
                  </p>
                ) : null}
              </div>
              <span
                className={`shrink-0 rounded-full border px-2.5 py-1 text-xs font-medium ${
                  SOURCE_TONE[assumption.source] ?? "border-border bg-muted text-muted-foreground"
                }`}
              >
                {assumption.source}
              </span>
            </div>
          ))}
        </div>

        {result.assumptions.applied_defaults.length > 0 ? (
          <div className="print-block rounded-lg border border-warning/40 bg-warning/10 p-4">
            <h4 className="flex items-center gap-2 text-sm font-semibold">
              <Info className="h-4 w-4" aria-hidden />
              Analyzer defaults applied
            </h4>
            <ul className="mt-2 space-y-1 text-sm text-muted-foreground">
              {result.assumptions.applied_defaults.map((item) => (
                <li key={item.field}>
                  <span className="font-mono text-xs">{item.field}</span> — {String(item.value)}
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        {result.assumptions.unknowns.length > 0 ? (
          <div className="print-block rounded-lg border border-border bg-surface p-4">
            <h4 className="text-sm font-semibold">Information left unknown</h4>
            <p className="mt-1 text-xs text-muted-foreground">
              These were not treated as zero. The related metrics are simply unavailable.
            </p>
            <ul className="mt-2 space-y-1 text-sm text-muted-foreground">
              {result.assumptions.unknowns.map((item) => (
                <li key={item.field}>
                  <span className="font-mono text-xs">{item.field}</span> — {item.effect}
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </Section>

      {/* Narrative */}
      <Section
        id="narrative"
        title="Plain-English acquisition analysis"
        description="The analyzer's written review of this opportunity."
        breakBefore
      >
        <div className="prose-report space-y-3 border-l-2 border-primary pl-4 text-base leading-relaxed">
          <h4 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
            Overall assessment
          </h4>
          {overallAssessment.map((paragraph) => (
            <p key={paragraph}>{paragraph}</p>
          ))}
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <PointList title="Strengths" items={strengths} tone="positive" />
          <PointList title="Weaknesses / risks" items={risks} tone="negative" />
          <PointList
            title="Transition strengths"
            items={narrative.transition_strengths ?? []}
            tone="positive"
          />
          <PointList
            title="Transition concerns"
            items={narrative.transition_concerns ?? []}
            tone="negative"
          />
        </div>

        <Separator />

        <PointList title="Key due-diligence questions" items={dueDiligence} tone="neutral" />

        <div className="grid gap-6 md:grid-cols-2">
          <PointList
            title="Additional financial due diligence"
            items={scores.financial_operational.due_diligence}
            tone="neutral"
          />
          <PointList
            title="Additional transition due diligence"
            items={scores.transition_qualitative.due_diligence}
            tone="neutral"
          />
        </div>

        {narrative.scope_note ? (
          <div className="print-block rounded-lg border border-border bg-surface p-4 text-sm leading-relaxed text-muted-foreground">
            {narrative.scope_note}
          </div>
        ) : null}
      </Section>

      <p className="print-block text-xs leading-relaxed text-muted-foreground">
        Prepared {analysisDate()} using the Accounting Practice Acquisition Analyzer by Trio Tax.
        This analysis reflects the inputs and assumptions above and is not legal, tax, accounting,
        valuation, or investment advice.
      </p>
    </div>
  );
}
