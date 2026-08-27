import type { Metadata } from 'next';
import '../src/index.css';

export const metadata: Metadata = {
  title: 'Rakshak AI | Field Health Intelligence',
  description: 'Evidence-based soybean crop health intelligence for farmers, agronomists, and agricultural organizations.',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}

