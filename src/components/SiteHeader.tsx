import { Link } from "@tanstack/react-router";
import { BrandLogo } from "./BrandLogo";

export function SiteHeader() {
  return (
    <header className="no-print sticky top-0 z-30 border-b border-border/80 bg-background/90 backdrop-blur">
      <div className="mx-auto grid max-w-6xl grid-cols-[minmax(0,1fr)_auto] items-center gap-4 px-4 py-3 sm:px-6">
        <Link to="/" className="flex min-w-0 items-center gap-3">
          <BrandLogo className="h-8 w-auto shrink-0 sm:h-9" />
          <span className="min-w-0 border-l border-border pl-3 text-sm leading-tight text-muted-foreground">
            <span className="block truncate font-medium text-foreground">
              Practice Acquisition Analyzer
            </span>
            <span className="hidden truncate sm:block">For buyers of accounting &amp; tax practices</span>
          </span>
        </Link>
        <nav className="flex shrink-0 items-center gap-1 text-sm">
          <Link
            to="/about"
            className="rounded-md px-3 py-2 text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
            activeProps={{ className: "text-foreground font-medium" }}
          >
            About
          </Link>
          <Link
            to="/analyzer"
            className="rounded-md bg-primary px-3 py-2 font-medium text-primary-foreground transition-colors hover:bg-primary/90"
          >
            Analyze
          </Link>
        </nav>
      </div>
    </header>
  );
}

export function SiteFooter() {
  return (
    <footer className="no-print mt-16 border-t border-border bg-surface">
      <div className="mx-auto flex max-w-6xl flex-col gap-4 px-4 py-8 text-sm text-muted-foreground sm:px-6 md:flex-row md:items-center md:justify-between">
        <div className="flex items-center gap-3">
          <BrandLogo className="h-7 w-auto" />
          <span>Accounting Practice Acquisition Analyzer</span>
        </div>
        <p className="max-w-xl text-xs leading-relaxed">
          This tool supports your own evaluation. It is not legal, tax, accounting, valuation, or
          investment advice, and it does not replace professional due diligence.
        </p>
      </div>
    </footer>
  );
}
