import React from 'react';
import * as Primitive from '@radix-ui/react-accordion';
import { Plus } from 'lucide-react';

export function Accordion({ items }: { items: { question: string; answer: string }[] }) {
  return <Primitive.Root type="single" collapsible className="ui-accordion">{items.map((item, index) => <Primitive.Item key={item.question} value={String(index)} className="ui-accordion-item"><Primitive.Header><Primitive.Trigger className="ui-accordion-trigger">{item.question}<Plus size={22} aria-hidden="true" /></Primitive.Trigger></Primitive.Header><Primitive.Content className="ui-accordion-content"><p>{item.answer}</p></Primitive.Content></Primitive.Item>)}</Primitive.Root>;
}
