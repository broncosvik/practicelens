import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useMemo, useRef, useState } from "react";
import { AlertCircle, ArrowLeft, ArrowRight, Loader2 } from "lucide-react";

import { SiteFooter, SiteHeader } from "@/components/SiteHeader";
import { Button } from "@/components/ui/button";
import { Callout } from "@/components/wizard/StepChrome";
import { StepBasics } from "@/components/wizard/StepBasics";
import { StepServices } from "@/components/wizard/StepServices";
import { StepRetentionCosts } from "@/components/wizard/StepRetentionCosts";
import { StepFinancing } from "@/components/wizard/StepFinancing";
import { StepTransition } from "@/components/wizard/StepTransition";
import { ResultsView } from "@/components/results/ResultsView";
import {
  activeServices,
  createInitialFormState,
  financingAllocationTotal,
  num,
  serviceRevenueTotal,
  toAnalysisRequest,
  type FormState,
} from "@/lib/analysis/formState";
import { analyzeAcquisition, preloadAnalysisRuntime } from "@/lib/analysis/pythonRuntime";
import type { AnalysisSuccess } from "@/lib/analysis/types";
import { money } from "@/lib/format";

export const Route = createFileRoute("/analyzer")({
  head: () => ({
    meta: [
      { title: "Run an Acquisition Analysis | Trio Tax Practice Analyzer" },
      {
        name: "description",
        content:
          "Work through a guided questionnaire covering price, service mix, retention, costs, financing, and transition to evaluate an accounting practice acquisition.",
      },
      { property: "og:title", content: "Run an Acquisition Analysis | Trio Tax Practice Analyzer" },
      {
        property: "og:description",
        content:
          "A guided evaluation of an accounting or tax practice acquisition: cash flow, financing risk, service mix, and transition quality.",
      },
    ],
  }),
  component: AnalyzerPage,
});

const STEPS = [
  { id: "basics", label: "Practice basics" },
  { id: "services", label: "Service mix" },
  { id: "retention", label: "Retention & costs" },
  { id: "financing", label: "Financing" },
  { id: "transition", label: "Transition & fit" },
] as const;

function validateStep(step: number, state: FormState): string[] {
  const errors: string[] = [];
  if (step === 0) {
    if (num(state.practice.annualRevenue) <= 0) errors.push("Enter the practice's annual revenue.");
    if (num(state.practice.askingPrice) <= 0) errors.push("Enter the asking price.");
    if (num(state.practice.ownerHourlyValue) <= 0)
      errors.push("Enter what an hour of your own time is worth.");
  }
  if (step === 1) {
    const services = activeServices(state);
    if (services.length === 0) errors.push("Select at least one service category.");
    const total = serviceRevenueTotal(state);
    const revenue = num(state.practice.annualRevenue);
    if (services.length > 0 && Math.abs(total - revenue) >= 0.01) {
      errors.push(
        `Service revenue totals ${money(total)} but annual revenue is ${money(revenue)}. These must match exactly.`,
      );
    }
  }
  if (step === 2) {
    const firstYear = num(state.retention.firstYear);
    if (firstYear <= 0 || firstYear > 100)
      errors.push("Enter an expected first-year retention rate between 1 and 100 percent.");
    if (num(state.horizon.years) < 1) errors.push("The analysis horizon must be at least one year.");
  }
  if (step === 3) {
    const allocated = financingAllocationTotal(state);
    const price = num(state.practice.askingPrice);
    if (Math.abs(allocated - price) >= 0.01) {
      errors.push(
        `Financing allocates ${money(allocated)} but the asking price is ${money(price)}. Buyer cash, bank principal, seller principal, and the maximum earn-out must total the asking price.`,
      );
    }
  }
  if (step === 4) {
    if (
      !state.transition.keyStaffRetentionUnknown &&
      state.transition.expectedKeyStaffRetention.trim() === ""
    ) {
      errors.push("Enter expected key staff retention, or mark it unknown.");
    }
  }
  return errors;
}

function AnalyzerPage() {
  const [state, setState] = useState<FormState>(createInitialFormState);
  const [step, setStep] = useState(0);
  const [errors, setErrors] = useState<string[]>([]);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<AnalysisSuccess | null>(null);
  const topRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    preloadAnalysisRuntime();
  }, []);

  useEffect(() => {
    topRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, [step, result]);

  const progress = useMemo(() => ((step + 1) / STEPS.length) * 100, [step]);

  function goNext() {
    const stepErrors = validateStep(step, state);
    setErrors(stepErrors);
    if (stepErrors.length > 0) return;
    if (step < STEPS.length - 1) {
      setStep(step + 1);
      return;
    }
    void runAnalysis();
  }

  async function runAnalysis() {
    setRunning(true);
    setErrors([]);
    try {
      const response = await analyzeAcquisition(toAnalysisRequest(state));
      if (response.ok) {
        setResult(response);
      } else {
        setErrors(response.errors.map((error) => error.message));
      }
    } catch (error) {
      setErrors([
        error instanceof Error
          ? `The analysis could not be completed: ${error.message}`
          : "The analysis could not be completed.",
      ]);
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <SiteHeader />
      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-8 sm:px-6 sm:py-12">
        <div ref={topRef} />

        {result ? (
          <ResultsView
            result={result}
            onEdit={() => {
              setResult(null);
              setStep(0);
            }}
          />
        ) : (
          <div className="space-y-6">
            <div className="no-print">
              <div className="flex items-baseline justify-between gap-4">
                <p className="text-sm font-medium text-muted-foreground">
                  Step {step + 1} of {STEPS.length}
                </p>
                <p className="truncate text-sm text-muted-foreground">{STEPS[step]?.label}</p>
              </div>
              <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-secondary">
                <div
                  className="h-full rounded-full bg-primary transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>

            {step === 0 ? (
              <StepBasics
                state={state}
                update={(patch) =>
                  setState({ ...state, practice: { ...state.practice, ...patch } })
                }
              />
            ) : null}
            {step === 1 ? (
              <StepServices
                state={state}
                update={(index, patch) =>
                  setState({
                    ...state,
                    services: state.services.map((service, position) =>
                      position === index ? { ...service, ...patch } : service,
                    ),
                  })
                }
              />
            ) : null}
            {step === 2 ? (
              <StepRetentionCosts
                state={state}
                updateRetention={(patch) =>
                  setState({ ...state, retention: { ...state.retention, ...patch } })
                }
                updateCosts={(patch) => setState({ ...state, costs: { ...state.costs, ...patch } })}
                updateHorizon={(patch) =>
                  setState({ ...state, horizon: { ...state.horizon, ...patch } })
                }
              />
            ) : null}
            {step === 3 ? (
              <StepFinancing
                state={state}
                update={(patch) =>
                  setState({ ...state, financing: { ...state.financing, ...patch } })
                }
              />
            ) : null}
            {step === 4 ? (
              <StepTransition
                state={state}
                update={(patch) =>
                  setState({ ...state, transition: { ...state.transition, ...patch } })
                }
              />
            ) : null}

            {errors.length > 0 ? (
              <Callout tone="warning">
                <div className="flex gap-2">
                  <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden />
                  <div>
                    <p className="font-medium">Before continuing, please resolve the following:</p>
                    <ul className="mt-1 list-disc space-y-1 pl-4">
                      {errors.map((error) => (
                        <li key={error}>{error}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </Callout>
            ) : null}

            <div className="flex flex-col-reverse gap-3 border-t border-border pt-6 sm:flex-row sm:justify-between">
              <Button
                variant="outline"
                className="min-h-11"
                disabled={step === 0 || running}
                onClick={() => {
                  setErrors([]);
                  setStep(Math.max(0, step - 1));
                }}
              >
                <ArrowLeft className="mr-2 h-4 w-4" aria-hidden />
                Back
              </Button>
              <Button className="min-h-11" onClick={goNext} disabled={running}>
                {running ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden />
                    Running the analysis…
                  </>
                ) : step === STEPS.length - 1 ? (
                  <>Run the analysis</>
                ) : (
                  <>
                    Continue
                    <ArrowRight className="ml-2 h-4 w-4" aria-hidden />
                  </>
                )}
              </Button>
            </div>
          </div>
        )}
      </main>
      <SiteFooter />
    </div>
  );
}
