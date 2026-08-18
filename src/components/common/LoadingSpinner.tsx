import React from "react";
import clsx from "clsx";

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg";
  fullScreen?: boolean;
}

export function LoadingSpinner({
  size = "md",
  fullScreen = false,
}: LoadingSpinnerProps) {
  const sizeMap = {
    sm: "w-4 h-4",
    md: "w-8 h-8",
    lg: "w-12 h-12",
  };

  const spinner = (
    <div
      className={clsx(
        sizeMap[size],
        "border-2 border-cg-primary border-t-transparent rounded-full animate-spin"
      )}
    />
  );

  if (fullScreen) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        {spinner}
      </div>
    );
  }

  return spinner;
}
