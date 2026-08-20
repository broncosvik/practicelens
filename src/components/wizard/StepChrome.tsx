import type { ReactNode } from "react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export function StepIntro({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="mb-6 max-w-3xl">
      <h2 className="text-2xl font-semibold sm:text-3xl">{title}</h2>
      <p className="mt-2 text-sm leading-relaxed text-muted-foreground sm:text-base">{children}</p>
    </div>
  );
}

export function SectionCard({
  title,
  description,
  children,
}: {
  title: string;
  description?: string;
  children: ReactNode;
}) {
  return (
    <Card className="border-border/80 shadow-card">
      <CardHeader className="pb-3">
        <CardTitle className="text-base font-semibold sm:text-lg">{title}</CardTitle>
        {description ? (
          <CardDescription className="text-sm leading-relaxed">{description}</CardDescription>
        ) : null}
      </CardHeader>
      <CardContent className="space-y-5">{children}</CardContent>
    </Card>
  );
}

export function FieldGrid({ children }: { children: ReactNode }) {
  return <div className="grid gap-5 sm:grid-cols-2">{children}</div>;
}

export function Callout({ tone = "neutral", children }: { tone?: "neutral" | "warning" | "success"; children: ReactNode }) {
  const toneClass =
    tone === "warning"
      ? "border-warning/50 bg-warning/10 text-foreground"
      : tone === "success"
        ? "border-success/40 bg-success/10 text-foreground"
        : "border-border bg-surface text-muted-foreground";
  return (
    <div className={`rounded-lg border px-4 py-3 text-sm leading-relaxed ${toneClass}`}>
      {children}
    </div>
  );
}
