'use client';

import { SourceChunk } from '@/lib/types';
import { Card } from '@/components/ui/card';

export function SourcePreviewPanel({ sources }: { sources: SourceChunk[] }) {
  return (
    <Card className="mt-4 p-4">
      <h3 className="mb-3 text-sm font-semibold">检索片段预览</h3>
      <div className="space-y-3">
        {sources.map((source) => (
          <div key={`${source.doc_id}-${source.score}`} className="rounded-lg border border-border p-3">
            <div className="mb-1 text-xs text-primary">{source.title} · score {source.score}</div>
            <p className="text-sm text-foreground/80 whitespace-pre-wrap line-clamp-5">{source.snippet}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}
