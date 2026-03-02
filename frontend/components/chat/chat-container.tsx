'use client';

import { useEffect } from 'react';
import { createSession, streamChat } from '@/lib/api';
import { useChatStore } from '@/store/chat-store';
import { Card } from '@/components/ui/card';
import { ChatInput } from './chat-input';
import { ThoughtTracePanel } from './thought-trace-panel';
import { SourcePreviewPanel } from './source-preview-panel';
import { ModelConfigDialog } from './model-config-dialog';

export function ChatContainer() {
  const { sessionId, setSessionId, messages, addMessage, upsertAssistant, trace, pushTrace, sources, setSources, streaming, setStreaming } = useChatStore();

  useEffect(() => {
    if (!sessionId) createSession().then(setSessionId);
  }, [sessionId, setSessionId]);

  const send = async (text: string) => {
    if (!sessionId) return;
    addMessage({ id: crypto.randomUUID(), role: 'user', content: text });
    setStreaming(true);
    let assistant = '';
    await streamChat(text, sessionId, (event, payload) => {
      if (event === 'trace' && payload.content) pushTrace(payload);
      if (event === 'retrieval') {
        const content = String(payload.content ?? '');
        setSources([
          ...sources,
          { doc_id: payload.query || 'retrieval', title: payload.query || '检索', snippet: content.slice(0, 400), score: 0 },
        ]);
      }
      if (event === 'token') {
        assistant += payload.content ?? '';
        upsertAssistant(assistant);
      }
      if (event === 'done') {
        const answer = payload.answer ?? payload?.answer ?? '';
        if (answer) upsertAssistant(answer);
      }
    });
    setStreaming(false);
  };

  return (
    <main className="mx-auto grid h-screen max-w-[1400px] grid-cols-1 gap-4 p-6 lg:grid-cols-[2fr_1fr]">
      <Card className="flex flex-col p-4">
        <div className="mb-4 flex items-center justify-between"><h1 className="text-lg font-semibold">DocAdvisor Web Chat</h1><ModelConfigDialog /></div>
        <div className="mb-4 flex-1 space-y-3 overflow-auto rounded-lg border border-border p-3">
          {messages.map((m) => (
            <div key={m.id} className={m.role === 'user' ? 'text-right' : ''}>
              <div className={`inline-block max-w-[85%] whitespace-pre-wrap rounded-xl px-4 py-2 text-sm ${m.role === 'user' ? 'bg-primary text-white' : 'bg-muted'}`}>
                {m.content}
              </div>
            </div>
          ))}
        </div>
        <ChatInput onSend={send} disabled={streaming} />
      </Card>
      <section className="flex flex-col">
        <ThoughtTracePanel trace={trace} />
        <SourcePreviewPanel sources={sources} />
      </section>
    </main>
  );
}
