import { createFileRoute, Link } from "@tanstack/react-router";
import { Calculator, LineChart, ShieldCheck, Users } from "lucide-react";

import heroImage from "@/assets/hero-practice.jpg";
import { SiteFooter, SiteHeader } from "@/components/SiteHeader";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Accounting Practice Acquisition Analyzer | Trio Tax" },
      {
        name: "description",
        content:
          "Evaluate an accounting or tax practice acquisition: cash flow after debt service, retention risk, service mix, financing structure, and transition quality.",
      },
      { property: "og:title", content: "Accounting Practice Acquisition Analyzer | Trio Tax" },
      {
        property: "og:description",
        content:
          "A structured, buyer-side analysis of an accounting practice acquisition — cash flow, retention, financing, and transition risk in one report.",
      },
    ],
  }),
  component: Index,
});

const HIGHLIGHTS = [
  {
    icon: Calculator,
    title: "Cash flow after everything",
    body: "Retained revenue less operating and staffing costs, then debt service and earn-out — year by year across your horizon.",
  },
  {
    icon: Users,
    title: "Retention modeled honestly",
    body: "First-year and ongoing retention drive revenue, staffing, and the portion of an earn-out you would actually pay.",
  },
  {
    icon: LineChart,
    title: "Service mix and concentration",
    body: "Revenue per engagement, revenue per owner hour, and how much of the practice rests on a single service line.",
  },
  {
    icon: ShieldCheck,
    title: "Transition risk scored separately",
    body: "Seller involvement, staff continuity, and fit are reported on their own so strong economics cannot hide a weak handoff.",
  },
];

function Index() {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <SiteHeader />
      <main className="flex-1">
        <section className="border-b border-border bg-surface">
          <div className="mx-auto grid max-w-6xl gap-10 px-4 py-14 sm:px-6 sm:py-20 lg:grid-cols-2 lg:items-center">
            <div className="min-w-0">
              <p className="text-sm font-medium uppercase tracking-wide text-accent">
                For buyers of accounting &amp; tax practices
              </p>
              <h1 className="mt-3 text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
                Know what the practice is really worth to you
              </h1>
              <p className="mt-5 max-w-xl text-base leading-relaxed text-muted-foreground sm:text-lg">
                A seller's revenue figure is the beginning of the analysis, not the end. Work
                through a guided questionnaire and receive a full written assessment: cash flow
                after debt service, retention and concentration risk, financing structure, and the
                quality of the transition you have actually been offered.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <Button asChild size="lg" className="min-h-12">
                  <Link to="/analyzer">Start an analysis</Link>
                </Button>
                <Button asChild variant="outline" size="lg" className="min-h-12">
                  <Link to="/about">How it works</Link>
                </Button>
              </div>
              <p className="mt-4 text-xs text-muted-foreground">
                About fifteen minutes. Runs entirely in your browser — nothing you enter is stored
                or transmitted.
              </p>
            </div>
            <div className="overflow-hidden rounded-2xl border border-border shadow-card">
              <img
                src={heroImage}
                alt="An accounting practice office desk with client files, a laptop, and a calculator in evening light"
                width={1600}
                height={1008}
                className="h-full w-full object-cover"
              />
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
          <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">
            What the analysis covers
          </h2>
          <div className="mt-8 grid gap-5 sm:grid-cols-2">
            {HIGHLIGHTS.map((highlight) => (
              <div
                key={highlight.title}
                className="rounded-xl border border-border bg-card p-6 shadow-card"
              >
                <highlight.icon className="h-6 w-6 text-primary" aria-hidden />
                <h3 className="mt-3 text-base font-semibold">{highlight.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                  {highlight.body}
                </p>
              </div>
            ))}
          </div>
        </section>

        <section className="border-t border-border bg-surface">
          <div className="mx-auto max-w-3xl px-4 py-16 text-center sm:px-6">
            <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">
              Bring the seller's numbers. Leave with a decision you can defend.
            </h2>
            <p className="mt-4 text-base leading-relaxed text-muted-foreground">
              Every assumption is labeled as yours or the analyzer's, and anything you do not know
              stays unknown rather than being quietly assumed.
            </p>
            <Button asChild size="lg" className="mt-8 min-h-12">
              <Link to="/analyzer">Start an analysis</Link>
            </Button>
          </div>
        </section>
      </main>
      <SiteFooter />
    </div>
  );
}
