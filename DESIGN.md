# Rakshak AI design system

## Direction

A practical field notebook with the clarity of an expert workspace. Farmers need readable outdoor screens; agronomists need evidence and dense review controls; organizations need honest summaries of their own fields. Warm, calm and grounded in actual observations.

## Identity and color

Use the outlined sprout mark with the lowercase Rakshak AI wordmark. Deep olive ink (#303326), warm stone canvas (#f8f7f2), nearly white surfaces, muted olive text (#656657), sunflower accent (#efd05a), and pale sage borders (#dadbce). Amber means uncertainty; red means a failed action or disease indication requiring attention. Pair every color with a text label. No glow, decorative gradients or glass panels.

## Typography

Web: locally bundled Public Sans Variable. Mobile: platform-compatible Roboto. Body text 16px; supporting labels at least 13px on web, with mobile theme text scaling supported. Product headings 24–32px, sentence case, medium weight. Marketing headlines can be larger, with short readable lines. Numeric data must retain its unit and scope.

## Layout and components

Public pages share navigation, generous content spacing and footer. Authentication and applications share a photo-and-form shell that becomes a single task column on phones. Desktop workspaces use a light navigation rail and compact context bar. On small screens the Radix navigation dialog supports keyboard focus and closing. Mobile has Fields / History / Profile destinations.

Use bordered evidence panels, restrained 8–12px corners, and tables or lists for records. Radix primitives back the navigation dialog, accordion and polymorphic buttons. Public Sans is bundled, not fetched at runtime. Primary actions are olive or sunflower; secondary actions are outlined. Buttons have visible busy/disabled states and at least 44px target height. Keep visible labels, keyboard focus, sensible tab order and reduced-motion support.

## Truthful data and states

Never manufacture counts, leaf detections, probabilities, reviews, health scores or pricing discounts. Unavailable historical values remain unavailable. A generic COCO detector does not verify soybean plants. Current classifier and severity outputs are labeled as an unvalidated pilot baseline; independent expert review is a separate record.

Empty states lead to a real next step. Failed requests retain form input and offer retry. Processing uses actual server state, never a simulated progress percentage. Original video and frame evidence require authorization. Demo fixtures stay out of operational dashboards.

## Asset provenance

`frontend/web/public/soybean-field.png` and the equivalent mobile asset are generated marketing illustrations, created during the 2026-09-09 redesign. They are not field evidence, customer photos or model evaluation data. Keep illustrative labeling in public context. Model reports use only the uploaded scan's actual images.
