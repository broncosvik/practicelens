import { createFileRoute, Link } from "@tanstack/react-router";

import { SiteFooter, SiteHeader } from "@/components/SiteHeader";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export const Route = createFileRoute("/about")({
  head: () => ({
    meta: [
      { title: "How the Analyzer Works | Trio Tax Practice Analyzer" },
      {
        name: "description",
        content:
          "What the Accounting Practice Acquisition Analyzer measures, the assumptions it makes explicit, and the limits of a screening analysis.",
      },
      { property: "og:title", content: "How the Analyzer Works | Trio Tax Practice Analyzer" },
      {
        property: "og:description",
        content:
          "What the analyzer measures, how it scores an opportunity, and what it deliberately leaves to your own due diligence.",
      },
    ],
  }),
  component: AboutPage,
});

const SECTIONS = [
  {
    title: "What it measures",
    body: "The analyzer projects retained revenue over your chosen horizon, subtracts operating and staffing costs, then applies acquisition debt and any earn-out. It reports operating cash flow, net cash flow, cash-on-cash return, payback, and the residual profit left after paying you fairly for the hours you would personally work.",
  },
  {
    title: "Two scores, kept separate",
    body: "A financial and operational score covers pricing, cash flow, service mix, and financing structure. A transition and qualitative score covers seller involvement, staff, fit, and the confidence you have in the information you were given. They are reported separately because strong economics do not cure a bad handoff, and a generous seller cannot fix a price that does not work.",
  },
  {
    title: "Unknowns stay unknown",
    body: "Where you do not have a figure, the analyzer records it as unknown rather than assuming zero. Metrics that depend on it are simply not reported, and the assumptions section shows exactly which conclusions rest on defaults rather than on your own numbers.",
  },
  {
    title: "Owner labor is priced",
    body: "Many acquisition analyses quietly treat the buyer's own time as free. This one asks what an hour of your time is worth and charges the practice for the hours you would work, so you can see whether the business earns anything beyond buying yourself a job.",
  },
  {
    title: "Where it stops",
    body: "This is a screening tool. It does not value goodwill for tax purposes, review engagement letters, test the quality of the underlying files, assess malpractice exposure, or replace a conversation with your attorney, lender, and tax adviser. It is a structured way to decide whether an opportunity deserves deeper work.",
  },
  {
    title: "Your data",
    body: "The analysis runs entirely in your browser. Nothing you enter is transmitted to a server or stored, and closing the tab discards it. Print or save the results if you want a record.",
  },
];

function AboutPage() {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <SiteHeader />
      <main className="mx-auto w-full max-w-3xl flex-1 px-4 py-12 sm:px-6">
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
          How this analyzer works
        </h1>
        <p className="mt-4 text-base leading-relaxed text-muted-foreground">
          Buying an accounting or tax practice is one of the largest financial decisions a firm
          owner makes, and the numbers presented by a seller rarely answer the question that
          matters: after clients leave, staff turn over, and the debt is serviced, what is actually
          left for you?
        </p>

        <div className="mt-10 space-y-5">
          {SECTIONS.map((section) => (
            <Card key={section.title} className="border-border/80 shadow-card">
              <CardHeader className="pb-2">
                <CardTitle className="text-base sm:text-lg">{section.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm leading-relaxed text-muted-foreground">{section.body}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="mt-10 rounded-xl border border-border bg-surface p-6">
          <h2 className="text-lg font-semibold">Ready to evaluate a practice?</h2>
          <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
            The questionnaire takes about fifteen minutes with the seller's figures in front of you.
          </p>
          <Button asChild className="mt-4 min-h-11">
            <Link to="/analyzer">Start an analysis</Link>
          </Button>
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
