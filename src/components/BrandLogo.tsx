import logoAsset from "@/assets/triotax-logo.png.asset.json";
import { cn } from "@/lib/utils";

export function BrandLogo({ className }: { className?: string }) {
  return (
    <img
      src={logoAsset.url}
      alt="Trio Tax"
      className={cn("h-9 w-auto", className)}
      width={192}
      height={108}
    />
  );
}
