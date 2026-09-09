# Rakshak AI design system

## Direction

A practical field notebook with the clarity of an expert workspace. Farmers need readable outdoor screens; agronomists need evidence and dense review controls; organizations need honest summaries of their own fields. Warm, calm and grounded in actual observations.

## Identity and color

Use the outlined sprout mark with the lowercase Rakshak AI wordmark. Forest ink (#143b2c), mineral canvas (#f5f8f5), white surfaces, muted green text (#58685f), pale lime accent (#d4ef86), and sage borders (#dfe7df). Amber means uncertainty; red means a failed action or disease indication requiring attention. Pair every color with a text label. No glow, decorative gradients or glass panels.

## Typography

Web: locally bundled Public Sans Variable. Mobile: platform-compatible Roboto. Body text 16px; supporting labels at least 13px on web, with mobile theme text scaling supported. Product headings 24–32px, sentence case, medium weight. Marketing headlines can be larger, with short readable lines. Numeric data must retain its unit and scope.

## Layout and components

Public pages share navigation, generous content spacing and footer. Authentication and applications share a photo-and-form shell that becomes a single task column on phones. Desktop workspaces use a forest navigation rail and compact context bar. On small screens the Radix navigation dialog supports keyboard focus and closing. Mobile has Home / Fields / Scan / History / Profile destinations.

Use bordered evidence panels, 12px controls and 18–24px panels, and tables or lists for records. Radix primitives back the navigation dialog, accordion and polymorphic buttons. Public Sans is bundled, not fetched at runtime. Primary actions are forest or lime; secondary actions are outlined. Buttons have visible busy/disabled states and at least 44px target height. Keep visible labels, keyboard focus, sensible tab order and reduced-motion support.

## Truthful data and states

Never manufacture counts, leaf detections, probabilities, reviews, health scores or pricing discounts. Unavailable historical values remain unavailable. A generic COCO detector does not verify soybean plants. Current classifier and severity outputs are labeled as an unvalidated pilot baseline; independent expert review is a separate record.

Empty states lead to a real next step. Failed requests retain form input and offer retry. Processing uses actual server state, never a simulated progress percentage. Original video and frame evidence require authorization. Demo fixtures stay out of operational dashboards.

## Asset provenance

`frontend/web/public/soybean-field.png` and the equivalent mobile asset are generated marketing illustrations, created during the 2026-09-09 redesign. They are not field evidence, customer photos or model evaluation data. Keep illustrative labeling in public context. Model reports use only the uploaded scan's actual images.

## Reference direction and revision

Revision 0.2.0 replaces the initial olive/sunflower direction with forest, mineral white and lime. Farmer mobile capture is primary; web prioritizes organization portfolios, agronomist evidence review and platform administration. The photographic hero and strong hierarchy were informed by [Cansaas Agra](https://dribbble.com/shots/27322745-Agra-Agriculture-Landing-Page). The evidence-led workspace hierarchy was informed by [RonDesignLab Farm Management](https://dribbble.com/shots/25188771-Farm-Management-SaaS-Dashboard). Their artwork, customer claims and data were not copied. A generated three-screen mobile concept served as direction, not runtime proof.

## Contribution checks

Target WCAG AA. Use semantic tokens for repeated colors and state labels alongside color; use 4/8px spacing increments and 44px minimum action targets. Keep Public Sans on web and Roboto on mobile. Native controls and Radix dialogs retain keyboard semantics and focus management. Verify narrow layouts, large text, form errors, empty records, loading and reduced motion before changing shared components. Screen-reader/device testing must be recorded separately from source and widget checks. Dense web tables may scroll horizontally; farmer screens stack content. Avoid inventing alternate themes or density switches without a product need. Token changes belong in the release changelog and both platform themes.
