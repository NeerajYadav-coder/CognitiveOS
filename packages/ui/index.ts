import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import React from "react";

/**
 * Merges class names safely with Tailwind CSS precedence.
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "glass" | "bordered";
}

export const Card: React.FC<CardProps> = ({
  children,
  className,
  variant = "default",
  ...props
}) => {
  const variantStyles = {
    default: "bg-white dark:bg-[#0a0c10] border border-slate-200 dark:border-white/5 shadow-sm",
    glass: "bg-white/70 dark:bg-slate-900/70 backdrop-blur-md border border-slate-200/50 dark:border-white/10 shadow-lg",
    bordered: "bg-transparent border border-slate-300 dark:border-white/15",
  };

  return React.createElement(
    "div",
    {
      className: cn("rounded-2xl transition-all", variantStyles[variant], className),
      ...props,
    },
    children
  );
};

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "primary" | "success" | "warning" | "neutral";
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  className,
  variant = "neutral",
  ...props
}) => {
  const variantStyles = {
    primary: "bg-primary/10 text-primary border-primary/20",
    success: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20",
    warning: "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20",
    neutral: "bg-slate-100 dark:bg-white/5 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-white/5",
  };

  return React.createElement(
    "span",
    {
      className: cn(
        "inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border",
        variantStyles[variant],
        className
      ),
      ...props,
    },
    children
  );
};
