'use client';

import { create } from 'zustand';
import { SourceChunk, ThoughtStep } from '@/lib/types';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

interface ChatState {
  sessionId: string;
  messages: Message[];
  trace: ThoughtStep[];
  sources: SourceChunk[];
  streaming: boolean;
  setSessionId: (id: string) => void;
  addMessage: (m: Message) => void;
  upsertAssistant: (content: string) => void;
  pushTrace: (step: ThoughtStep) => void;
  setSources: (sources: SourceChunk[]) => void;
  setStreaming: (v: boolean) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  sessionId: '',
  messages: [],
  trace: [],
  sources: [],
  streaming: false,
  setSessionId: (id) => set({ sessionId: id }),
  addMessage: (m) => set((s) => ({ messages: [...s.messages, m] })),
  upsertAssistant: (content) =>
    set((s) => {
      const last = s.messages[s.messages.length - 1];
      if (last?.role === 'assistant') {
        return { messages: [...s.messages.slice(0, -1), { ...last, content }] };
      }
      return { messages: [...s.messages, { id: crypto.randomUUID(), role: 'assistant', content }] };
    }),
  pushTrace: (step) => set((s) => ({ trace: [...s.trace, step] })),
  setSources: (sources) => set({ sources }),
  setStreaming: (v) => set({ streaming: v }),
}));
