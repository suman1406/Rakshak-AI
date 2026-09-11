import React from 'react';
import { Link } from 'react-router-dom';
import { Leaf } from 'lucide-react';
import { PublicPage } from '../../components/ui/public-page';
import { Button } from '../../components/ui/button';

export function NotFoundPage() {
  return <PublicPage title="This path doesn't lead to a page." intro="404 · The address may have changed, or the link may be incomplete."><Leaf size={64} aria-hidden="true"/><div className="flex flex-wrap gap-4 mt-8"><Button asChild><Link to="/">Return home</Link></Button><Button variant="secondary" asChild><Link to="/contact">Contact the team</Link></Button></div></PublicPage>;
}
