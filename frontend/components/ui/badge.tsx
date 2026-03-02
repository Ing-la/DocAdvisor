import * as React from 'react';
import { cn } from '@/lib/utils';

export function Badge({ className, ...props }: React.HTMLAttributes<HTMLSpanElement>) {
  return <span className={cn('inline-flex rounded-md bg-muted px-2 py-1 text-xs text-foreground/80', className)} {...props} />;
}
