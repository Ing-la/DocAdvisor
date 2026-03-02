'use client';

import { motion } from 'framer-motion';
import { ThoughtStep } from '@/lib/types';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export function ThoughtTracePanel({ trace }: { trace: ThoughtStep[] }) {
  return (
    <Card className="h-full p-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold">Thought Trace</h3>
        <Badge>{trace.length} steps</Badge>
      </div>
      <div className="space-y-2 overflow-auto pr-2 max-h-[70vh]">
        {trace.map((step, idx) => (
          <motion.div
            key={`${step.ts}-${idx}`}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-lg border border-border bg-muted/40 p-3"
          >
            <div className="mb-1 text-xs text-foreground/60">{step.type}</div>
            <div className="text-sm whitespace-pre-wrap">{step.content}</div>
          </motion.div>
        ))}
      </div>
    </Card>
  );
}
