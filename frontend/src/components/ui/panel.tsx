import { cn } from "@/lib/utils";

export function Panel({
  title,
  children,
  className,
  action,
}: {
  title: string;
  children: React.ReactNode;
  className?: string;
  action?: React.ReactNode;
}) {
  return (
    <div
      className={cn(
        "flex flex-col rounded-md border border-border bg-card panel-glow",
        className
      )}
    >
      <div className="flex items-center justify-between border-b border-border px-3 py-2">
        <span className="font-terminal text-xs uppercase tracking-widest text-rudra-gold">
          {title}
        </span>
        {action}
      </div>
      <div className="flex-1 overflow-auto p-3">{children}</div>
    </div>
  );
}
