'use client';

import dynamic from 'next/dynamic';

const LegacyApp = dynamic(() => import('../../src/App'), { ssr: false });

export default function CatchAllPage() {
  return <LegacyApp />;
}

