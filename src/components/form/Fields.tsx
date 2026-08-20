import { type ReactNode, useId } from "react";
import { HelpCircle } from "lucide-react";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { cn } from "@/lib/utils";

/** Short, expandable buyer education. Explanatory only — no analysis logic. */
export function WhyThisMatters({ children, label = "Why this matters" }: { children: ReactNode; label?: string }) {
  return (
    <Collapsible className="mt-1">
      <CollapsibleTrigger className="inline-flex items-center gap-1.5 text-xs font-medium text-primary underline-offset-4 hover:underline">
        <HelpCircle className="h-3.5 w-3.5" aria-hidden />
        {label}
      </CollapsibleTrigger>
      <CollapsibleContent>
        <p className="mt-2 rounded-md border-l-2 border-accent bg-surface px-3 py-2 text-xs leading-relaxed text-muted-foreground">
          {children}
        </p>
      </CollapsibleContent>
    </Collapsible>
  );
}

export function FieldShell({
  label,
  htmlFor,
  hint,
  children,
  className,
}: {
  label: string;
  htmlFor?: string | undefined;
  hint?: ReactNode | undefined;
  children: ReactNode;
  className?: string | undefined;
}) {
  return (
    <div className={cn("space-y-1.5", className)}>
      <Label htmlFor={htmlFor} className="text-sm font-medium">
        {label}
      </Label>
      {children}
      {hint ? <div className="text-xs leading-relaxed text-muted-foreground">{hint}</div> : null}
    </div>
  );
}

interface NumericFieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  hint?: ReactNode | undefined;
  placeholder?: string | undefined;
  adornment?: "currency" | "percent" | "none";
  suffix?: string | undefined;
  className?: string | undefined;
}

export function NumericField({
  label,
  value,
  onChange,
  hint,
  placeholder,
  adornment = "none",
  suffix,
  className,
}: NumericFieldProps) {
  const id = useId();
  return (
    <FieldShell label={label} htmlFor={id} hint={hint} className={className}>
      <div className="relative">
        {adornment === "currency" ? (
          <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-sm text-muted-foreground">
            $
          </span>
        ) : null}
        <Input
          id={id}
          inputMode="decimal"
          value={value}
          placeholder={placeholder}
          onChange={(event) => onChange(event.target.value.replace(/[^0-9.]/g, ""))}
          className={cn(
            "h-11 text-base",
            adornment === "currency" && "pl-7",
            (adornment === "percent" || suffix) && "pr-12",
          )}
        />
        {adornment === "percent" || suffix ? (
          <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-sm text-muted-foreground">
            {suffix ?? "%"}
          </span>
        ) : null}
      </div>
    </FieldShell>
  );
}

export function ToggleField({
  label,
  value,
  onChange,
  hint,
}: {
  label: string;
  value: boolean;
  onChange: (value: boolean) => void;
  hint?: ReactNode | undefined;
}) {
  const id = useId();
  return (
    <div className="flex items-start justify-between gap-4 rounded-lg border border-border bg-card p-4">
      <div className="min-w-0 space-y-1">
        <Label htmlFor={id} className="text-sm font-medium">
          {label}
        </Label>
        {hint ? <div className="text-xs leading-relaxed text-muted-foreground">{hint}</div> : null}
      </div>
      <Switch id={id} checked={value} onCheckedChange={onChange} className="mt-0.5 shrink-0" />
    </div>
  );
}

export function SegmentedYesNo({
  label,
  value,
  onChange,
  hint,
}: {
  label: string;
  value: boolean;
  onChange: (value: boolean) => void;
  hint?: ReactNode | undefined;
}) {
  return (
    <FieldShell label={label} hint={hint}>
      <div className="inline-flex w-full max-w-xs rounded-lg border border-input bg-surface p-1">
        {[
          { label: "Yes", selected: value === true, next: true },
          { label: "No", selected: value === false, next: false },
        ].map((option) => (
          <button
            key={option.label}
            type="button"
            onClick={() => onChange(option.next)}
            aria-pressed={option.selected}
            className={cn(
              "min-h-11 flex-1 rounded-md px-4 text-sm font-medium transition-colors",
              option.selected
                ? "bg-primary text-primary-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground",
            )}
          >
            {option.label}
          </button>
        ))}
      </div>
    </FieldShell>
  );
}

const RATING_LABELS = ["Poor", "Fair", "Adequate", "Good", "Excellent"];

export function RatingField({
  label,
  value,
  onChange,
  hint,
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
  hint?: ReactNode | undefined;
}) {
  return (
    <FieldShell label={label} hint={hint}>
      <div className="grid grid-cols-5 gap-1.5 rounded-lg border border-input bg-surface p-1">
        {RATING_LABELS.map((ratingLabel, index) => {
          const rating = index + 1;
          const selected = value === rating;
          return (
            <button
              key={ratingLabel}
              type="button"
              onClick={() => onChange(rating)}
              aria-pressed={selected}
              className={cn(
                "flex min-h-12 flex-col items-center justify-center rounded-md px-1 py-1.5 text-xs font-medium transition-colors",
                selected
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "text-muted-foreground hover:bg-secondary hover:text-foreground",
              )}
            >
              <span className="text-sm font-semibold">{rating}</span>
              <span className="hidden text-[10px] leading-tight sm:block">{ratingLabel}</span>
            </button>
          );
        })}
      </div>
    </FieldShell>
  );
}
