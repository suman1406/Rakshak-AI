# Rakshak AI design system

## Direction and users

Rakshak connects a farmer's observation with an organization's records and an agronomist's independent assessment. The public website should feel immersive, confident and tangible. The working product should feel calm, precise and easy to scan. Farmers use the mobile app outdoors; organization and expert users primarily work at a desk. These environments share the R-and-leaf identity but need different density and visual emphasis.

## Reference direction

The owner requested the presentation quality of [ElevenLabs](https://elevenlabs.io/), [Stripe](https://stripe.com/in), [Razorpay](https://razorpay.com/) and [boAt](https://www.boat-lifestyle.com/). Their live landing pages were inspected on 2026-09-09. The applied principles are a distinctive first impression, generous editorial typography, strong imagery, explorable product stories and deliberate pacing. Brand artwork, commercial claims, logos and customer statistics are not copied.

The landing page opens with a generated soybean landscape, a short outcome statement and an interactive capture / understand / review journey. A separate workspace illustration explains the product. Subsequent sections alternate photographic evidence, role-specific pathways, privacy, questions and pilot access. The working dashboards use quiet navigation and real records rather than marketing imagery.

## Identity and color

Use the custom R monogram with a leaf-shaped aperture and the capitalized Rakshak AI wordmark. The vector master is `frontend/web/public/rakshak-symbol.svg`; the favicon and mobile icons use this same mark. Web semantic tokens are in `frontend/web/src/saas.css`: deep green ink, near-white surfaces, pale sage navigation and restrained green actions. Main product supporting text uses #64725a on near-white. Green, amber and terracotta distinguish clear observations, uncertainty and disease indications; every state also has a text label. Unscanned records remain separate from uncertain results.

Mobile retains forest #143b2c, canvas #f5f8f5, muted text #58685f, pale lime #d4ef86 and borders #dfe7df. Outdoor readability takes priority over decorative density.

## Typography and layout

Web uses locally bundled Geist Variable; mobile uses Roboto. Working web labels are generally 14–16px and body text 16–18px, page headings 27–30px, and summary values 30–37px. Tiny labels belong only to explicitly illustrative product graphics, not primary controls. Marketing headings use a larger scale with short lines. Preserve units, scope and unavailable values in numeric displays.

The desktop shell uses a pale navigation rail, workspace context, page breadcrumb and account controls. Organization summaries use one metric strip, a labeled distribution and actionable next steps above a filterable record table. Agronomist search/status/sort controls stay visible; additional filters expand on demand. Administration separates access requests, plans and decision history. Narrow organization records become stacked rows; dense expert evidence tables may scroll within their own container.

Public pages share a sticky navigation header and footer. Workspace headers also stay visible. Route changes start at the top; explicit section links retain their target below the header. Applications use the existing photo-and-form shell, stacking on narrow screens. Mobile has Home / Fields / Scan / History / Profile destinations, with capture central.

Use 6–10px corners for web controls and panels, subtle borders and little elevation. Marketing depth is reserved for the landscape interaction and workspace illustration. Avoid wrapping every heading or metric in its own card. Shared base styles live in `index.css`; `saas.css` owns the current web design. The superseded `premium.css` is removed.

## Interaction and accessibility

Keep native labels, Radix dialog focus management, visible keyboard focus, meaningful links and explicit loading/error/empty states. Farmer and primary public actions target 44px; compact desktop controls remain at least 32px and expand on phones. Product figures always reflect their filter scope. Never show invented progress, trends, customer activity or diagnostic confidence.

The landscape has one entrance transition. Scrolling reveals sections once without pinning or hijacking scroll. Workflow changes animate briefly after the visitor chooses a step. Reduced-motion preference disables animation and leaves all content visible. No continuous background animation, automatic carousel or autoplay audio is used.

Target WCAG AA and verify rendered contrast, responsive layouts and keyboard operation. Browser geometry checks and source inspection do not establish complete screen-reader compliance. Physical camera, device text scaling and platform accessibility require separate device evidence.

## Truthful data and assets

Never manufacture counts, detections, probabilities, reviews, health scores or discounts. Model results are an unvalidated soybean pilot baseline; an independent expert assessment is a separate record. Processing follows actual server status. Original videos and frames require authorization. Demo fixtures stay outside operational workspaces.

`frontend/web/public/field-landscape.webp` is a generated marketing landscape created on 2026-09-09 and encoded as WebP (about 350 KB). `soybean-field.png` and its mobile counterpart are generated marketing illustrations. They are not customer photos, field evidence or model evaluation data. The interactive website scenes are explicitly labeled illustrations. Reports use only the uploaded scan's actual media.

## Contribution checks

Keep the established brand and role hierarchy. Check loading, errors, empty results, filters, exports, focus, reduced motion and narrow layouts when changing shared components. Run TypeScript, the no-mock contract and a production build. Record browser interactions and screenshots separately from backend tests, Flutter widget renders, device checks and production deployment proof. Update `docs/CHECKLIST_DESIGN_AUDIT.md` when the user-facing flow changes.
