import React, { ReactNode } from "react";
import clsx from "clsx";

type ButtonVariant = "primary" | "secondary" | "danger" | "ghost";
type ButtonSize = "sm" | "md" | "lg";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  children: ReactNode;
}

export function Button({
  variant = "primary",
  size = "md",
  isLoading = false,
  disabled = false,
  className,
  children,
  ...props
}: ButtonProps) {
  const baseStyles = clsx(
    "font-medium rounded-lg transition-all duration-200",
    "active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
  );

  const variants = {
    primary: "bg-cg-primary text-white hover:bg-blue-600",
    secondary:
      "bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-300 dark:hover:bg-gray-600",
    danger: "bg-cg-danger text-white hover:bg-red-600",
    ghost:
      "text-cg-primary hover:bg-blue-50 dark:hover:bg-gray-800 amoled:hover:bg-gray-900",
  };

  const sizes = {
    sm: "px-3 py-2 text-sm",
    md: "px-4 py-3 text-base",
    lg: "px-6 py-4 text-lg",
  };

  return (
    <button
      className={clsx(baseStyles, variants[variant], sizes[size], className)}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="flex items-center gap-2">
          <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
          Loading...
        </span>
      ) : (
        children
      )}
    </button>
  );
}
