import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'DocAdvisor Web',
  description: 'DocAdvisor Next.js 对话前端',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN" className="dark">
      <body>{children}</body>
    </html>
  );
}
