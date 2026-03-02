'use client';

import { useState } from 'react';
import { Settings } from 'lucide-react';
import { Dialog, DialogContent, DialogTrigger } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export function ModelConfigDialog() {
  const [apiBase, setApiBase] = useState(process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000');
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button className="bg-muted text-foreground hover:bg-muted/80"><Settings className="mr-2 h-4 w-4" />模型配置</Button>
      </DialogTrigger>
      <DialogContent>
        <h3 className="mb-3 text-lg font-semibold">模型与网关配置</h3>
        <p className="mb-3 text-sm text-foreground/70">当前前端仅配置 API Base，后端模型参数通过 /api/v1/config 管理。</p>
        <Input value={apiBase} onChange={(e) => setApiBase(e.target.value)} />
      </DialogContent>
    </Dialog>
  );
}
