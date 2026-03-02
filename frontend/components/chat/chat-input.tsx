'use client';

import { useState } from 'react';
import { SendHorizontal } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export function ChatInput({ onSend, disabled }: { onSend: (text: string) => void; disabled?: boolean }) {
  const [value, setValue] = useState('');
  return (
    <div className="flex gap-2">
      <Input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (value.trim()) {
              onSend(value.trim());
              setValue('');
            }
          }
        }}
        placeholder="输入需求并回车发送..."
      />
      <Button
        disabled={disabled || !value.trim()}
        onClick={() => {
          onSend(value.trim());
          setValue('');
        }}
      >
        <SendHorizontal className="h-4 w-4" />
      </Button>
    </div>
  );
}
