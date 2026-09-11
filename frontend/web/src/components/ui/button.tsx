import React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { LoaderCircle } from 'lucide-react';

export function cn(...inputs: ClassValue[]) { return twMerge(clsx(inputs)); }
const variants = cva('ui-button', { variants: { variant: { default: 'ui-button-primary', secondary: 'ui-button-secondary', ghost: 'ui-button-ghost', accent: 'ui-button-accent', danger: 'ui-button-danger' }, size: { default: '', small: 'ui-button-small', icon: 'ui-button-icon' } }, defaultVariants: { variant: 'default', size: 'default' } });
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof variants> { asChild?: boolean; busy?: boolean }
export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(({ className, variant, size, asChild, busy, children, disabled, ...props }, ref) => {
  const Component = asChild ? Slot : 'button';
  return <Component ref={ref} className={cn(variants({ variant, size }), className)} disabled={disabled || busy} aria-busy={busy || undefined} {...props}>{asChild ? children : <>{busy && <LoaderCircle size={18} className="ui-spinner" aria-hidden="true" />}{children}</>}</Component>;
});
Button.displayName = 'Button';
