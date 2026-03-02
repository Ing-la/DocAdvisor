import * as React from 'react';
import { cn } from '@/lib/utils';

export function Input(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} className={cn('h-10 w-full rounded-md border border-border bg-muted px-3 text-sm outline-none focus:ring-2 focus:ring-primary', props.className)} />;
}
