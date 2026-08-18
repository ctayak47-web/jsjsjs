import React, { ReactNode } from "react";
import clsx from "clsx";

interface CardProps {
  children: ReactNode;
  className?: string;
  interactive?: boolean;
}

export function Card({
  children,
  className,
  interactive = false,
}: CardProps) {
  return (
    <div
      className={clsx(
        "rounded-lg p-4",
        "bg-cg-surface-light dark:bg-cg-surface-dark",
        "border border-cg-border-light dark:border-cg-border-dark",
        interactive && "hover:shadow-md cursor-pointer transition-shadow",
        className
      )}
    >
      {children}
    </div>
  );
}
