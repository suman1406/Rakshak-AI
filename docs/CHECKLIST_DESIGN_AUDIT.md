# Rakshak AI checklist audit — 0.2.0

Reviewing source, local browser captures of landing, pricing, onboarding and role workspaces, and Flutter-rendered welcome screens. This is a product-design audit, not a claim of device, screen-reader, production-hosting or model-accuracy certification.

Checklist Design v3.2.1 supplies the original item names and descriptions below. Each applicable category is kept separate. The PRD and approved pilot decisions determine whether an optional checklist item is needed. No unverified customer, payment, model or deployment claims were added to satisfy a checklist.

Evidence: local validation API, annual plan preselection in browser, organization portfolio and agronomist queue captures, backend regression tests, Flutter analysis and narrow/large-text widget tests. Native camera controls, haptics, cold launch, VoiceOver and NVDA still require their named environments.

Corrections from this review: dedicated missing-page recovery; readable flexible mobile brand row; mobile support/privacy/version access; camera error recovery; home refresh after capture and pull-to-refresh; organization refresh and clear-filters; annual billing preserved through approval; plan usage visibility; no repeated profile save without changes; pricing cancellation/refund explanations; browser-storage disclosure.

Scope exclusions: carts, checkout, cards, promotions, affiliate/referral, paywalls, messaging, maps, calendar/Gantt, Kanban, public profiles, invitations, social identity, 2FA, API-key management, external integrations, editorial/careers/press/event pages, carousels and sliders are not advertised pilot features. Native selects are audited as inputs rather than custom dropdown menus. The optional introduction uses steps, not a task-completion checklist. No external push-notification channel or live status service is configured. These exclusions do not imply those future features are implemented.

Legend: 🟢 Present; 🟡 partially present or explicitly limited; ⚪ not needed for this pilot; ❔ requires evidence from the stated environment.

## [Landing Page — Website](https://www.checklist.design/website/landing-page)

| | Item | Why |
|---|---|---|
| 🟢 | **Headline** — A single, clear statement of what the product does or the value it delivers | Hero gives the crop-care outcome; subheadline identifies soybean video evidence. |
| 🟢 | **Subheadline** — A supporting line that adds context or specificity to the headline claim | Subheadline connects farmer capture to the team workspace. |
| 🟢 | **Hero visual** — An image, illustration, or product screenshot that reinforces the headline and makes the page feel tangible | Rendered photo and clearly labeled app preview support the product story. |
| 🟢 | **Primary CTA** — One clear action for the visitor to take (sign up, start a trial, book a demo) | Bring your team is the primary filled action. |
| ⚪ | **Social proof** — Customer logos, testimonials, review scores, or user counts that validate the claim. | No verified customer endorsements were supplied; fabricated social proof is excluded. |
| 🟢 | **Key benefits** — A concise breakdown of the main reasons a visitor should care, focused on outcomes not features. | Evidence and expert follow-up sections describe practical benefits. |
| 🟢 | **Objection handling** — Content that addresses the most common reasons a visitor would not convert e.g. price, complexity, commitment | FAQ covers users, uncertainty, connectivity and privacy. |
| 🟢 | **Repeated CTA** — The primary CTA repeated at the bottom of the page for visitors who scroll all the way through | Organization pilot CTA repeats at the bottom. |

## [Pricing — Website](https://www.checklist.design/website/pricing)

| | Item | Why |
|---|---|---|
| 🟢 | **Pricing options** — Subscriptions plans or one-off purchase | Live API supplies three organization offers. |
| 🟢 | **Pricing features** — What the user will get for purchasing the product | Farm and monthly scan allowances and shared capabilities are listed. |
| 🟢 | **A free pathway to sign up** — A way for user to try your product before considering purchase | Free farmer pilot is linked and has no automatic paid conversion. |
| 🟢 | **Refund or return policy** — A user may want to understand this further | Written cancellation and refund terms are required before payment. |
| 🟢 | **Highlighted price as a recommendation** — Showcase a price that most users purchase, or they will get the best value from | Growth has a differentiated surface, without a fabricated popularity claim. |
| ⚪ | **Security logo for payment processing** — Show how you process purchases with a credible vendor for legibility | No payment gateway or card collection is offered. |
| 🟢 | **Frequency of payments (monthly vs yearly)** — You may offer an annual option for long term customers that are rewarded with a discount | Monthly and annual choices update amounts and onboarding links. |

## [Pricing — Web app](https://www.checklist.design/web-app/pricing)

| | Item | Why |
|---|---|---|
| 🟢 | **Plan names, prices and frequency** — The name and cost of each available plan, with billing frequency clearly stated | Plan names, amounts and intervals render from the API. |
| 🟢 | **Billing period toggle** — A switch between monthly and annual billing, with the annual discount shown if applicable | Annual control and derived savings were exercised in browser. |
| 🟢 | **Feature comparison (if price options)** — A side-by-side breakdown of what each plan includes and excludes | Comparable farm and scan allowances show the tier differences. |
| 🟢 | **Call to action** — A button on each plan to start a trial, subscribe, or contact sales | Every plan links to a preselected application. |
| 🟢 | **Free tier or trial details** — What's included, how long it lasts, and what happens when it ends | Free farmer access is described with no automatic conversion. |
| 🟢 | **FAQ section** — Answers to the most common questions about billing, plan limits, cancellation, and payment | Pricing questions explain allowances, billing and cancellation. |
| 🟢 | **Enterprise option** — A prompt for organisations that need a custom arrangement beyond the standard listed plans | Enterprise requests custom scope. |

## [404 — Website](https://www.checklist.design/website/404)

| | Item | Why |
|---|---|---|
| 🟢 | **Logo** — Either your complete logo or a symbol mark | Shared navigation includes the brand. |
| 🟢 | **Title** — Make it clear the user is on the 404 page | A dedicated missing-page title replaces silent redirection. |
| 🟢 | **Description** — Explain why the user has landed on this page | 404 description explains a changed or incomplete address. |
| 🟢 | **Links to other pages** — Offer pathways to stick around | Home and support recovery links are provided. |
| 🟢 | **Illustrations, patterns, visual flair** — This page is a great opportunity to show off your brand's personality | A restrained leaf icon uses the shared identity. |

## [Contact Us — Website](https://www.checklist.design/website/contact-us)

| | Item | Why |
|---|---|---|
| 🟢 | **Personality and branding** — Visual character and tone of voice that align with your brand | Contact uses the shared public shell and practical language. |
| 🟢 | **Clear methods to contact** — Phone number, email or a form to fill in for examples | A persisted support form is available. |
| ⚪ | **Social media accounts** — User may feel more comfortable contacting via a social platform | No verified social support channels were supplied. |
| 🟢 | **Segmenting contact methods** — If you have different contacts for support and sales, showcase that! It shows you have specific support for their issue | The page identifies account, pilot and organization requests. |
| 🟢 | **Easy location to get to** — Make this page available in your header or footer | Contact appears in navigation and footer. |

## [About — Website](https://www.checklist.design/website/about)

| | Item | Why |
|---|---|---|
| 🟢 | **Origin story** — A genuine account of why the company was founded and the problem it set out to solve | The approach page explains the crop-observation problem. |
| 🟢 | **Mission or values** — What the company stands for and how it makes decisions, stated plainly | Evidence and human judgment are the stated principles. |
| ⚪ | **Team** — The people behind the product (names, roles, and faces) making the company feel human | Team biographies and portraits were not supplied; none are fabricated. |
| ⚪ | **Milestones or traction** — Key moments in the company's history (founding year, customer count, notable launches) that establish credibility | No verified traction or founding timeline was supplied. |
| ⚪ | **Investors or backers** — Logos or names of investors, accelerators, or notable backers, where relevant | No investors or backers are claimed. |
| 🟢 | **CTA** — A clear next step e.g. view open roles, read the blog, or try the product | The public shell provides application and contact paths. |

## [Features — Website](https://www.checklist.design/website/features)

| | Item | Why |
|---|---|---|
| 🟢 | **Feature grouping** — Capabilities organised into logical themes or categories so the page is scannable and not a wall of bullet points | Capture, evidence, expert review and organization records are grouped. |
| 🟢 | **Feature descriptions** — Each feature explained in one or two sentences from the user's perspective, what they can do, not what the system does | Descriptions use the farmer and team perspective. |
| 🟡 | **Feature visuals** — Screenshots, GIFs, or short video clips showing each feature in action | The landing page has workflow previews; it does not present every feature as a runtime screenshot. |
| 🟢 | **Benefits framing** — Each feature connected explicitly to an outcome and/or benefit, not just the capability | Each group explains the decision or record-keeping benefit. |
| ⚪ | **Social proof per feature** — A relevant customer quote placed alongside the feature it relates to, making the case more concrete. | No verified feature testimonials are available. |
| 🟢 | **CTA** — A conversion point at the bottom and optionally inline throughout, for visitors who are convinced mid-page | Farmer, organization and agronomist actions lead to real routes. |

## [FAQ — Website](https://www.checklist.design/website/faq)

| | Item | Why |
|---|---|---|
| 🟢 | **Purposeful information** — Ensure the questions and answers shown are providing value to the users to make decisions about your product | Questions address uncertainty, audience, connectivity and privacy. |
| 🟢 | **Contact options** — If a user doesn't have their problem solved or question answered, offer a method for them to directly contact you | Contact is adjacent to the FAQ. |
| ⚪ | **Table of contents** — If you have a large amount of questions, structure your topics so users can navigate between areas easier | Four short questions do not need a contents index. |
| ⚪ | **Search functionality** — Keyword search for users to look up their questions | A four-question accordion does not need keyword search. |
| ⚪ | **Navigate by topic** — Segment your questions into general topics to structure your content and enable an easier search for users | The small FAQ is already a single product-introduction topic. |

## [Privacy — Website](https://www.checklist.design/website/legal-privacy)

| | Item | Why |
|---|---|---|
| 🟢 | **Privacy policy** — A clear document explaining what data is collected, how it is used, how long it is kept, and how users can request deletion | Notice describes records, use, retention and reviewed deletion requests. |
| 🟢 | **Terms of service** — The agreement governing use of the product (user responsibilities, acceptable use, limitation of liability) | Terms cover advisory use, suitable evidence, accounts and availability. |
| 🟢 | **Cookie policy** — A clear explanation of which cookies are used, what they do, and how users can control them | Browser storage and sign-out controls are explicitly described. |
| 🟢 | **Last updated date** — A clear timestamp on every legal document so users know if they are reading the current version | Privacy and terms show the update date. |
| 🟡 | **Version history or changelog** — For products with engaged users, a log of what changed between policy versions — builds trust and reduces enquiries. | Git records changes; no public policy-version browser is included. |
| 🟢 | **Contact for legal queries** — A dedicated email or address for data, privacy, or legal enquiries as required by most regulations. | A contact form accepts privacy and data requests. |

## [Login — Web app](https://www.checklist.design/web-app/login)

| | Item | Why |
|---|---|---|
| 🟢 | **Email and password fields** — The two standard authentication inputs: an email address field and a password field. | Labeled identity and masked password fields retain input on error. |
| 🟢 | **Show/hide password toggle** — A button alongside the password field that reveals or conceals what the user has typed | Show/hide password is available. |
| 🟡 | **Forgot password** — A link that begins the password reset flow for users who cannot remember their credentials | Recovery routes to reviewed support; automated delivery requires configured infrastructure. |
| ⚪ | **Remember me** — A checkbox that persists the user's session across browser closures | Revocable sessions already persist; no misleading remember-me checkbox is added. |
| ⚪ | **SSO or social login** — Alternative authentication via a third-party identity provider (Google, Microsoft, GitHub) that bypasses the email/password form. | The pilot uses first-party credentials only. |
| 🟢 | **Sign up link** — A link to the account creation screen for users who do not yet have an account | Farmer signup and reviewed team access are linked. |
| 🟢 | **Error messages** — Feedback shown when authentication fails, indicating what the user should try next | Failed login messages retain input and allow retry. |

## [Login — Mobile app](https://www.checklist.design/mobile/login)

| | Item | Why |
|---|---|---|
| ⚪ | **Social sign-in** — Sign-in options that connect to an existing Apple or Google account, bypassing manual credential entry. | No social identity providers are configured. |
| 🟢 | **Email field** — The input where users enter the email address associated with their account. | Email or phone input is labeled. |
| 🟢 | **Password field** — A masked text input for the account password, with the option to reveal what has been typed. | Password is masked with reveal control. |
| ⚪ | **Biometric authentication** — Face ID or fingerprint sign-in for returning users who have already authenticated once with a password | Biometric sign-in is outside this credential-based pilot. |
| 🟢 | **Credential autofill** — System-level support for pre-filling saved email and password from the user's password manager. | Autofill hints are present; device password-manager behavior still needs device QA. |
| 🟡 | **Forgot password link** — The link users reach for when they can't recall their password, leading into the reset flow. | Help directs users to reviewed recovery rather than claiming an email was sent. |
| 🟢 | **Error states** — Feedback shown when authentication fails, distinguishing between an unrecognised email address and an incorrect password. | Errors explain recovery without disclosing whether another account exists. |
| ⚪ | **Passwordless sign-in (magic link)** — An alternative sign-in method that sends a one-time link to the user's email, requiring no password | Magic-link delivery is not configured. |

## [Sign up — Website](https://www.checklist.design/website/sign-up)

| | Item | Why |
|---|---|---|
| 🟢 | **Logo** — Either your complete logo or a symbol mark | Shared brand appears in the auth shell. |
| 🟢 | **Title** — Tell the user this is where they create an account | Account-creation heading identifies the task. |
| 🟢 | **Description** — Describe the basic features of creating an account and set their expectations as to what they can achieve | Farmer and reviewed team paths set access expectations. |
| 🟢 | **Account identification** — A unique identifier for the user to log in with | Email identifies the account. |
| 🟡 | **Setting a password** — A secure, private code that allows them to access their account in the future | Password requirements are enforced; signup does not have a strength meter. |
| 🟢 | **Link to login** — A user may already have an account and landed on this page anyway | Sign-in recovery path is visible. |
| ⚪ | **Sign up via third party** — Reduce a few clicks to one, by allowing users to sign up via Facebook or Google | No social provider is enabled. |
| ⚪ | **Current active customer count** — Showcasing how many people are using and enjoying your product can evoke a fear of missing out for potential users | No unverified customer count is displayed. |
| ⚪ | **Testimonial or social proof** — Reinforcing the brand and product never goes out of style | No unverified testimonial is displayed. |
| ⚪ | **Blog post** — An opportunity to show off some amazing content to convert an unsure lead | No editorial blog is required for account creation. |
| 🟢 | **Billing plans and trial period (if payment is involved)** — Clearly define the length of the trial period and when they will be charged | Free farmer access and reviewed commercial applications are distinguished. |

## [Sign up — Mobile app](https://www.checklist.design/mobile/sign-up)

| | Item | Why |
|---|---|---|
| ⚪ | **Third party sign-up** — Account creation through an existing Apple, Google or social media account, removing the need to set a password | No third-party sign-in is offered. |
| 🟢 | **Required fields** — The minimum information needed to create an account (typically email and password, if not social auth) | Name, email, optional phone, password and processing consent form the account. |
| 🟡 | **Password strength** — Visual feedback showing how secure the chosen password is as the user types | Minimum and UTF-8 limits are validated; no speculative strength score is shown. |
| 🟢 | **Terms and privacy** — The acknowledgement that the user accepts the terms of service and privacy policy before creating an account | Consent is explicit; registration opens the in-app privacy and terms before submission. |
| ⚪ | **Email verification** — The step asking users to confirm their email address after the account has been created | Email delivery is not configured; the pilot does not claim email verification. |
| 🟢 | **Welcome state** — The screen shown immediately after account creation, confirming success and pointing toward the first action | Registration signs in and opens the farmer home with first-field guidance. |
| 🟢 | **Already have an account** — A link for returning users who arrived at the sign-up screen instead of login | Returning users can sign in. |
| ⚪ | **Marketing opt-in (if applicable)** — A separate, explicit consent field for users willing to receive marketing emails | No marketing email enrollment is offered. |

## [Dashboard — Mobile app](https://www.checklist.design/mobile/dashboard)

| | Item | Why |
|---|---|---|
| 🟢 | **Thumb-zone layout** — Primary actions and key content placed in the lower two-thirds of the screen where thumbs naturally reach | The central Scan action is permanently reachable in bottom navigation. |
| 🟢 | **Widget-based structure** — Content organised into discrete, scannable cards or widgets rather than long scrolling sections | Capture, field and recent-scan cards separate tasks. |
| 🟢 | **Pull to refresh** — Dragging down refreshes the dashboard data, with a visible indicator and haptic on trigger | Pull-to-refresh now reloads records with the native indicator. |
| 🟢 | **Glanceable metrics** — The most important numbers or status indicators visible without any interaction | Latest scan states are labeled on field and history cards. |
| 🟢 | **Quick actions** — The most common tasks accessible directly from the dashboard, without navigating to another screen. | Capture and add-field actions open their actual workflows. |
| 🟢 | **Personalised content** — Where applicable, content and order reflecting the user's history, preferences, or role | Actual user name and owned fields populate the screen. |
| 🟡 | **Per-widget states** — Each widget handling its own loading skeleton and empty state — the dashboard never partially loads in a confusing way. | Empty/error states exist; the dashboard loads its related records together rather than independently. |
| 🟢 | **Notification surface** — Time-sensitive alerts or action items surfaced on the dashboard so users do not need to hunt for what requires attention | Recent scan status and uncertain evidence surface the next useful action. |

## [Camera — Mobile app](https://www.checklist.design/mobile/camera-media-capture)

| | Item | Why |
|---|---|---|
| 🟢 | **Permission request** — Camera permission requested at the moment capture is triggered (not on app launch or during onboarding) | Camera permissions are requested when capture starts. |
| ❔ | **Viewfinder and capture button** — A full-screen viewfinder with a clearly positioned, large capture button | Native image-picker camera supplies the viewfinder; physical-device appearance is unverified. |
| ❔ | **Flash controls** — Flash toggle accessible without leaving the capture screen, with auto, on, and off states clearly indicated | Native camera flash controls depend on the device camera app. |
| ❔ | **Camera flip** — A clear camera flip button accessible during capture, positioned so it is not accidentally triggered during shooting | Native camera switching depends on the device camera app. |
| ❔ | **Post-capture preview** — A preview shown after capturing, giving the user the chance to retake or confirm before the media is used | Native capture review must be checked on Android and iOS hardware. |
| ⚪ | **Gallery picker of captures** — The option to open photo library containing only photos captured within that series until exit of camera | The pilot captures one video per scan; a series gallery is unnecessary. |

## [Tab Bar Navigation — Mobile app](https://www.checklist.design/mobile/tab-bar-navigation)

| | Item | Why |
|---|---|---|
| 🟢 | **Tab count** — Limited to the most important destinations — 3 to 5 items is the typical range | Five primary destinations include the central capture action. |
| 🟢 | **Icon and label** — Each tab paired with both an icon and a text label | Every destination pairs an icon with a label. |
| 🟢 | **Active and default states** — Active should be visually distinct whether it's colour, border or icon weight | Native selection styling distinguishes the current destination. |
| ⚪ | **Badge counts** — Useful for tabs with unread counts like messages and notifications, updating in real time | There is no unread-message count to display. |
| 🟢 | **Fixed presence** — For the sections the tab bar applies to, tab bar should remain visible, and can be hidden on any page a level deeper | Navigation stays on home sections and gives way to deeper capture/report screens. |
| 🟢 | **Tap target size** — Each tab at least 44×44pt to be reliably tappable with a thumb in any grip position | Material NavigationBar supplies large tap regions. |
| ❔ | **Haptic feedback** — A subtle tap haptic on tab selection confirming the action | Haptic behavior depends on platform settings and requires a physical device. |

## [Settings — Mobile app](https://www.checklist.design/mobile/settings)

| | Item | Why |
|---|---|---|
| 🟢 | **Grouped table layout** — Settings organised into clearly labelled sections (Account, Notifications, Privacy, Support) using the native grouped list pattern | Profile, security, support and legal actions are grouped. |
| 🟢 | **Native toggle controls** — Binary settings presented with the platform-native toggle switch (UISwitch on iOS, Material Switch on Android) | Consent uses a native binary control. |
| 🟢 | **Destructive actions grouped** — Log out, delete account, and other irreversible actions in their own section at the bottom, visually distinguished in red | Sign-out is separated below account and help actions. |
| 🟢 | **Account details at top** — The user's avatar, name, and email shown prominently at the top of settings, a clear anchor for whose account is being managed | Account name and role appear at the top. |
| 🟢 | **Deep link to specific settings** — A direct link from relevant in-app prompts to the specific settings screen they reference — notification preferences, privacy, and so on. | Profile directly opens security, help and privacy screens. |
| 🟢 | **Support and feedback access** — A clear path to contact support, submit feedback, or access help documentation, accessible from within settings. | Support form saves to the existing platform inbox. |
| 🟢 | **App version** — The current app version shown at the bottom of settings — essential for support conversations and identifying build-specific issues. | Version 0.2.0 (2) appears in profile. |
| 🟢 | **Legal links** — Links to the Privacy Policy and Terms of Service accessible within settings, as required by app stores. | Privacy and terms are available inside the app. |

## [Settings — Web app](https://www.checklist.design/web-app/settings)

| | Item | Why |
|---|---|---|
| 🟢 | **Structure** — Organising settings controls into logical categories e.g. account, notifications, security, billing. | Profile, organization, updates and security are separate sections. |
| 🟡 | **Account details** — The fields where users update their name, email address, and profile photo | Name is editable; identity changes require reviewed support and no avatar upload is offered. |
| 🟢 | **Security details** — The ability to change the password,  two-factor authentication and other security information | Password change requires the current password and revokes sessions. |
| ⚪ | **Notification preferences** — Controls for which notifications the user receives and through which channel, grouped by type (product updates, reminders, billing) | External notification channels are explicitly disabled, so no dummy preferences appear. |
| 🟢 | **Billing** — Managing payment method, upgrading or cancelling a payment — this could also be a preview of this information with a link directly to the billing page if separate | Organization settings show plan, interval and usage with a support route. |
| ⚪ | **Additional preferences (if applicable)** — Language, timezone, date format, and appearance settings like dark mode | One accessible light theme is deliberate; locale controls are not advertised. |
| 🟢 | **Danger zone** — Destructive actions like account deletion, clearly separated from the rest of settings | Privacy links lead to reviewed data/deletion requests. |

## [Billing — Web app](https://www.checklist.design/web-app/billing)

| | Item | Why |
|---|---|---|
| ⚪ | **Payment method on file** — The current card or payment method linked to the account, shown with masked details | No payment instrument is stored. |
| ⚪ | **Add or update payment method action** — A way to enter a new card or change the current one | Payments are arranged outside the product after review. |
| ⚪ | **Next billing date and amount** — When the next payment will be taken and for how much | No automatic charge schedule is created by applying. |
| ⚪ | **Invoices and receipts** — A list of past charges with the ability to download a PDF invoice for each. | No transactions occur in this pilot UI; invoices belong to the agreed external billing process. |
| ⚪ | **Tax and VAT (if applicable)** — Applicable tax or VAT shown on invoices and billing history | Tax terms are confirmed in the written agreement before payment. |
| ⚪ | **Failed payment recovery** — Clear messaging and recovery instructions when a payment attempt has failed | There is no automated payment attempt to recover. |
| 🟡 | **Billing contact email** — The email address where invoices and billing notifications are sent | The application contact is available; a separate billing-contact field is not included. |

## [Account — Web app](https://www.checklist.design/web-app/account)

| | Item | Why |
|---|---|---|
| ⚪ | **Profile photo** — A way for users to upload or change their profile image | Initials identify accounts; personal-photo collection is unnecessary. |
| 🟢 | **Display name** — The name shown to other users or across the product interface e.g. username, email address, first and last name | Display name is shown and editable. |
| 🟢 | **Account details** — Fields for email address, phone number, job title, or other relevant identifying information based on the product and information collected | Account email and workspace role remain visible. |
| ⚪ | **Linked accounts (if applicable)** — A view of which third-party accounts are connected for sign-in or data access, with ability to disconnect | No third-party accounts are linked. |
| 🟢 | **Save confirmation** — Clear feedback that changes have been saved, either inline or as a toast | Profile save shows a success state; unchanged names cannot be resubmitted. |
| 🟡 | **Delete or deactivate account** — Options to deactivate or permanently delete the account, clearly separated from other settings | Deletion is a reviewed privacy request, not an instant destructive action. |

## [Account — Mobile app](https://www.checklist.design/mobile/account)

| | Item | Why |
|---|---|---|
| 🟡 | **Email** — The current email address displayed with an option to update it | Identity is retained; email updates require reviewed support. |
| 🟢 | **Password change** — A way for users to update their account password. | Security requires the old password before setting a new one. |
| ⚪ | **Linked accounts** — A view of which third-party accounts are connected for sign-in or data access, with ability to disconnect | No linked social accounts exist. |
| 🟢 | **Save confirmation** — Clear feedback that changes have been saved, either inline or as a toast | Name and consent saves provide feedback. |
| 🟡 | **Delete or deactivate account** — Options to deactivate or permanently delete the account, clearly separated from other settings | Privacy screen offers a data/deletion request; actual deletion needs operator review. |

## [Uploading media — Flows](https://www.checklist.design/flows/uploading-media)

| | Item | Why |
|---|---|---|
| 🟢 | **Empty state** — Show a clear visual placeholder with an upload icon and simple text that indicate a file can be dropped into the area to upload. It’s also suitable to offer a click to upload route incase a user prefers that option. | Capture and saved-file actions identify the empty upload state. |
| ⚪ | **Drag and drop interaction** — When a file is across the interaction canvas, there should be a clear visual state change to indicate it has detected a file attempting to be dropped. This lets the user know it’s safe to release the file at this point. | The native/file-picker route is deliberate; drag-and-drop is not advertised. |
| 🟢 | **Progress indicator** — Display progress that updates in real-time so users know their upload is working. If a percentage is not possible to show, a loading indicator can at least show that something is happening. Include file names and show overall progress when uploading multiple files to keep users informed throughout the process. | Upload busy state and actual processing status avoid fabricated percentages. |
| 🟢 | **File restrictions & constraints** — Clearly state limits to what files can be uploaded. This is commonly file size and format, shown in the upload area before users attempt to upload files. If a user tries to upload a file outside the constraints, an error message should show explaining it does follow the constraints. | Video format, size and duration limits are shown and enforced. |
| 🟢 | **Outcome status** — Use visual indicators like green checkmarks for successful uploads and red warning icons for failures. For failures, include an error message explaining what went wrong and what users can do to fix it. | Saved video, quality rejection and upload error states are distinct. |
| 🟢 | **Upload actions** — Ways to interact with an upload. Choose which actions to show by default vs on hover based on available space, aiming to avoid overwhelming users with too many visible options. Common actions include: Retry failed uploads Cancel upload in progress Delete files Rename files | Retry uses the saved video; capture can be cancelled before submission. |
| ⚪ | **Showing multiple uploaded files** — Display files in a clean list or grid with thumbnails when possible, and ensure the layout you choose is scalable. What information you show about each file depends on the context of the upload. A file name or size can be relevant in one case, while seeing the images uploaded can be the relevant detail in another. | One video per assessment avoids ambiguous multi-upload grouping. |

## [Submitting a form — Flows](https://www.checklist.design/flows/submitting-a-form)

| | Item | Why |
|---|---|---|
| 🟢 | **Show button to submit** — Below the form fields, a button to submit the information needs to be present. You can change the copy to fit the form e.g. the button can say “Subscribe” if someone is providing their email address to receive emails. | Forms end with task-specific submit actions. |
| 🟢 | **Show loading state after submission** — The user must see the form is in the process of being submitted. Note: also make sure your hover state is considered before they press the button! | Busy labels and disabled submit actions show work in progress. |
| 🟢 | **Show success message when it submits** — The form was submitted! Let’s communicate that back to the user with a clear success message. | Saved requests return a reference or completion message. |
| 🟢 | **If it doesn't, show an error message** — Sometimes, things don’t work out. If the form can’t submit, because of invalid information or another error, that also needs to be shown. | Request errors preserve entered information. |
| 🟢 | **An error may occur because of the wrong information** — If the criteria for a text field isn’t met, the form can fail to submit due to that error, and must be detailed. | Required, length, email and password constraints provide corrective feedback. |

## [Showing input error — Flows](https://www.checklist.design/flows/showing-input-error)

| | Item | Why |
|---|---|---|
| 🟢 | **Keep the input in default state** — The text field should be checked for errors only after the information has been entered. | Forms begin without errors. |
| 🟢 | **Allow user to enter information** — Let the user type without interruptions and submit the information aka don't assess as changes are made. | Validation runs on submission without blocking typing. |
| 🟡 | **Signal error after loss of focus** — After the input has lost focus (user has clicked another element), the field should be assessed. Looks like we have an error here! In this case, explain why the error happened, and what is required to resolve it. For accessibility, combine the text with a visual icon that indicates an error was found. | Most forms validate on submit rather than blur; native validation identifies the invalid field. |
| 🟢 | **Return to default state upon reattempt** — Once the user focuses on the field again, the error message should disappear. If there is an error again, the process will simply repeat until they are able to continue. | Retry clears request errors and revalidates values. |

## [Contacting support — Flows](https://www.checklist.design/flows/contacting-support)

| | Item | Why |
|---|---|---|
| 🟢 | **Show a link to contact support** — This can be placed in a number of areas, such as: ‍ • footer in a website • settings in a mobile app • a page experiencing an error Use clear copy and easy to recognise visuals to highlight the link. | Public navigation, footer and mobile profile expose support. |
| 🟢 | **Show methods of contact** — If you have one option, showcase it! If you have multiple options (chat, call, FAQ), list them out and represent each of their benefits. Chat is great for a specific, complicated issue that needs an instant response. On the other hand, FAQ is great for standard questions that are easy to explain. Also consider the order of the methods. A FAQ as the first option is great because it lets a user find their own answer without waiting on you to respond. But a direct chat can be seen as more convenient as it's less direct troubleshooting for the user. | A single saved-request channel is clearly described. |
| 🟢 | **Outline how to communicate and what is expected** — Once a method is chosen, make it clear on how the method will work. Illustrate the response time, and what the user will need to provide to receive support. | Receipt copy explains inbox review and absence of automatic email; no unsupported response-time promise is made. |

## [Filtering items — Flows](https://www.checklist.design/flows/filtering-items)

| | Item | Why |
|---|---|---|
| 🟢 | **Show action near item collection** — Place above or beside the collection it affects, using a recognizable icons and/or label. | Filters sit above the affected field or case records. |
| 🟢 | **Show available filter options** — When the action is triggered, filter options can either be shown on the same page for immediate feedback, or on another page. This should be dependent on the amount of filtering that is possible, and whether you think the user is likelier to tweak filters ongoing, or apply several and then view results. It's also worthwhile considering a filtering priority order, with the most common options filtered sitting at the front. | District, assessment, severity and status choices are visible. |
| 🟢 | **Consider different filter types** — The standard filter is a multi-select option picker. But certain properties can benefit from a different way of managing the filtering. There's sliders, checkboxes, dropdowns and others to consider. Each property should be considered, asking yourself what feels like the easiest way to change this value. | Search and select controls match the relevant properties. |
| 🟢 | **Show active filters clearly when applied** — On the item collection page, display which filters are currently applied. You can also choose to have a high level active state applied to the filter action to imply it is in use, if you find showing all applied filters is too cluttered. | Current values remain visible in their controls. |
| 🟢 | **Provide easy filter removal** — Let users clear individual filters or all filters at once to allow easier refining of their results. | Reset/clear-all restores the collection. |
| 🟢 | **Show result count** — Not a must have, but this can be handy where it is meaningful for users to see what the total results value has reduced to. It will help users feel if their result is too narrow or broad, directing them to either add or remove filters. | Field and case counts reflect the active filter. |
| 🟢 | **Empty state** — It's possible that a combination of filters can product no results. Explain this clearly and suggest adjusting or clearing filters to see results. | No-result copy recommends broadening filters. |

## [Saving changes — Flows](https://www.checklist.design/flows/saving-changes)

| | Item | Why |
|---|---|---|
| 🟢 | **Show action that enables change** — There should be an action to enable information to be updated. It may be automatically editable, but that can be riskier for some software. If it is read-only by default, then a button can trigger the editable version to then update and save. | Name and consent controls expose editable values. |
| 🟢 | **Disable save action until changes are made** — An action should be visible as a source of confirming changes to be saved - this is usually a button. Initially, the action can be disabled. It indicates no changes have been made, and there is nothing to save. A common location for this action is in the navigation above the fold, so it's always visible over the content. Another option is after all the content that's editable. | Web name save is disabled when unchanged. |
| 🟢 | **State changes to active once a change is made** — In the example, we've changed the email address, which means a change is waiting to be saved. Changing the button state to active brings the user's attention to the action. | Editing the name enables save. |
| 🟢 | **Action changes to loading state when pressed** — Now that the changes are being saved, you want to show that action is in progress. You can do so with a loading spinner in the action, as the user's view will be on that element. | Busy state prevents repeat submission. |
| 🟢 | **Notify changes have been saved** — The page will reload or update, and this is the critical part. The user should now be informed that their changes have been saved. They can now safely leave the page, knowing the details are locked in until they choose to change them again. | Success feedback confirms saved values. |

## [Accessibility — Design system](https://www.checklist.design/design-system/accessibility)

| | Item | Why |
|---|---|---|
| 🟢 | **Target conformance level** — The WCAG conformance target the team has committed to documented and referenced in contribution guidelines. AA as a baseline for most products, with AAA achievable for specific criteria such as text contrast. | DESIGN.md documents WCAG AA as the contribution target. |
| 🟡 | **Colour contrast standards** — The contrast ratios verified across all text and interactive element colour combinations (4.5:1 for normal text, 3:1 for large text and UI components) | Primary palette contrast is checked; a complete assistive-technology audit remains external. |
| 🟢 | **Focus indicator design** — A visible, high-contrast focus indicator designed for every interactive component | Shared CSS focus-visible and native focus states are defined. |
| 🟢 | **Keyboard navigation patterns** — Standard keyboard interaction patterns documented and applied consistently e.g. arrow keys for menus and listboxes, Enter and Space for activation, Escape for dismissal | Radix navigation and native controls preserve standard keyboard patterns. |
| 🟢 | **ARIA pattern library** — Attributes that make web content accessible to those who use assistive technologies with roles, states, and properties defined for every interactive component pattern | Dialogs, input labels, live error states and selected navigation carry semantics. |
| ❔ | **Screen reader testing** — Components tested with at least VoiceOver on Safari and NVDA on Chrome before shipping | VoiceOver/Safari and NVDA/Chrome require manual assistive-technology sessions. |
| ⚪ | **Accessibility annotations in design** — A shared annotation kit used in design files to specify ARIA labels, roles, reading order, and focus behaviour | Code is the maintained design source; no separate annotation file exists. |
| 🟢 | **Accessibility in contribution guidelines** — Ensuring accessibility requirements are part of the component contribution checklist | DESIGN.md includes accessibility checks for shared-component changes. |

## [Typography — Design system](https://www.checklist.design/design-system/typography)

| | Item | Why |
|---|---|---|
| 🟢 | **Type scale** — A defined set of font sizes with a consistent ratio between them, covering everything from captions to display headings | Public Sans and Roboto scales span captions through display headings. |
| 🟢 | **Semantic text styles** — Named styles that describe role rather than size so usage is driven by meaning, not pixel values e.g. display-large, body-default, label-small, caption | Shared heading/body/label styles describe content roles. |
| 🟢 | **Typeface selection and loading** — The chosen typefaces detailing style and weight e.g. Inclusive Sans Medium | Public Sans is bundled; mobile uses Roboto with explicit button styling. |
| 🟢 | **Line height per style** — Line height defined explicitly for every text style since tightly spaced headings and readable body text require different values | Theme line heights distinguish headings and body copy. |
| 🟢 | **Letter spacing per style** — Letter spacing defined per style where needed | Display headings use restrained tracking. |
| 🟢 | **Responsive type behaviour** — How text styles respond to viewport size, whether through fluid type scaling, breakpoint-based overrides, or fixed sizes with responsive layout compensation | Web breakpoints and Flutter text scaling adapt typography. |
| 🟡 | **Minimum readable size** — The smallest text size in use across the system, and how readability at that size is validated in the actual rendering environment | Farmer body text is generous; dense web metadata still uses small secondary labels. |
| ❔ | **Accessibility responsiveness** — How text styles behave at 200% browser zoom, and whether any style communicates meaning through colour variation alone | Large-text widget tests pass; 200% browser zoom and screen-reader combinations still need manual verification. |

## [Color System — Design system](https://www.checklist.design/design-system/color-system)

| | Item | Why |
|---|---|---|
| 🟢 | **Primitive palette** — A base set of named color ramps (blue-100 through blue-900, neutral-0 through neutral-1000) that serves as the raw material for all semantic decisions | Forest, lime, white, sage and semantic feedback colors define the palette. |
| 🟢 | **Semantic color tokens** — Named tokens that describe purpose rather than appearance so the system can be reskinned without touching components e.g. color-background-primary, color-text-danger, color-border-interactive | Named CSS and RakshakColors values centralize shared colors. |
| 🟢 | **Interactive state colors** — Defined color values for default, hover, pressed, focused, disabled, and selected states applied consistently across all interactive elements | Shared controls define selected, disabled, focus and interaction states. |
| 🟢 | **Feedback colors** — A consistent set of colors for success, warning, error, and informational states — used across alerts, form validation, badges, and status indicators. | Warning, error and healthy surfaces accompany textual status. |
| 🟡 | **Contrast ratios (accessibility)** — A breakdown of text and interactive element color combinations verified to meet WCAG AA contrast minimums — 4.5:1 for normal text, 3:1 for large text and UI components | Primary pairs are calculated; not every legacy utility pair has been measured. |
| ⚪ | **Dark and light mode definition** — A complete parallel set of semantic token values for the opposite mode | One outdoor-readable light content theme is intentional. |
| 🟢 | **Brand color integration** — Brand colors mapped into the semantic system in a way that maintains accessibility | Lime carries forest text and the forest rail carries light text. |
| 🟢 | **Color blindness considerations** — The palette tested against common color vision deficiencies for when color is used to convey state | Every status has a text label; the chart includes a textual legend. |

## [Spacing / Grid — Design system](https://www.checklist.design/design-system/spacing-and-grid)

| | Item | Why |
|---|---|---|
| 🟢 | **Spacing scale** — A defined set of spacing values (typically base-4 or base-8, covering 4, 8, 12, 16, 24, 32, 48, 64, 96) used for all margin, padding, and gap decisions | Components use a 4/8px rhythm with larger public section gaps. |
| 🟡 | **Semantic spacing tokens** — Named tokens for spacing that describe purpose (space-component-padding-sm, space-layout-section-gap) so spacing decisions are intentional, not arbitrary | Spacing is consistent but not every value is a semantic token. |
| 🟢 | **Column grid** — A defined column grid for each major breakpoint (typically 4 columns mobile, 8 tablet, 12 desktop) with gutter and margin values specified | Responsive grids collapse to stacked layouts. |
| 🟢 | **Breakpoints** — A named set of breakpoints (sm, md, lg, xl) that are shared between design and code, so responsive behaviour is described in consistent terms across both disciplines | Shared responsive thresholds adapt public and workspace layouts. |
| 🟢 | **Component vs layout spacing** — A clear distinction between spacing used inside components and spacing used to compose layouts, since different scales often apply to each | Compact control spacing differs from public section spacing. |
| ⚪ | **Density variants** — Where applicable, defined compact and comfortable density modes, common in data-heavy products where users need to choose between information density and breathing room | The pilot has one stable density per surface, not a user density switch. |
| 🟢 | **Baseline grid alignment** — Text baselines and component heights designed to align to the base unit, so stacking elements produces predictable, harmonious vertical rhythm | Controls and panel padding share consistent alignment. |

## [Tokens — Design system](https://www.checklist.design/design-system/tokens)

| | Item | Why |
|---|---|---|
| 🟡 | **Three-tier token architecture** — Tokens organised into primitive, semantic, and component tiers — primitives store raw values, semantic tokens describe purpose, component tokens scope decisions to a specific element | Primitive/theme tokens exist; a separate component-token tier is not universal. |
| 🟢 | **Naming convention** — A consistent, predictable naming pattern so any token name communicates its purpose without needing documentation. | Named field, surface, text and feedback colors are consistent. |
| 🟢 | **Token documentation** — Each semantic token documented with its intended use, example contexts, and what it can and cannot be used for | DESIGN.md records purpose and platform equivalents. |
| 🟢 | **Token governance** — A clear rule for what constitutes a token versus a hardcoded value, and a process for reviewing and approving new tokens before they are added to the system | Contribution rules require shared semantic values and review of new tokens. |
| ⚪ | **Design tool sync** — Tokens maintained in your design tool of choice as variables | Code is authoritative; no external design-tool sync is advertised. |
| 🟢 | **Versioning and changelog** — Token changes versioned and communicated in a way that teams consuming the token system can know when values change and what the impact will be on their surfaces | Theme changes belong to the versioned release and design history. |

## [Button — Design system](https://www.checklist.design/design-system/button)

| | Item | Why |
|---|---|---|
| 🟢 | **Base style** — Your default style, one of the following: fill, outline, underline | Filled primary and outlined secondary actions are shared. |
| 🟢 | **Shape** — Visual properties of a button: padding, border, border radius, shadow | Buttons have consistent padding, radius and minimum height. |
| 🟢 | **Variants** — Each visual type to represent button structure e.g. primary and secondary buttons | Primary, secondary, ghost and icon variants exist. |
| 🟢 | **Copy** — Instructional text that details what will happen if you click the button | Labels describe actions such as record, request review and save. |
| 🟢 | **States** — How the button changes based on the interaction: hover, focused, disabled | Focus, disabled and busy states are visible. |

## [Input Field — Design system](https://www.checklist.design/design-system/input-field)

| | Item | Why |
|---|---|---|
| 🟢 | **Input field** — Interactive text field for user to enter their data into | Native inputs and Flutter form fields collect actual values. |
| 🟢 | **Label** — Stating what information the user is meant to provide | Visible labels identify required information. |
| 🟢 | **Placeholder text** — Text inside the input field acting as an example of what you want the user to enter | Search and optional examples use placeholder text without replacing labels. |
| 🟢 | **Data format** — Set text fields to allow the relevant text values e.g. numeric only for phone number | Email, password, numeric and date controls use matching formats. |
| 🟢 | **Illustration or icon** — A visual cue can help break up a long list of text fields | Field/capture icons clarify context without replacing labels. |
| 🟢 | **Hint** — Elaborate on the title of the text field incase a user struggles to know what to enter | Password, video and application requirements are explained. |

## [Loading — Design system](https://www.checklist.design/design-system/loading)

| | Item | Why |
|---|---|---|
| 🟢 | **Visual indicator** — A clear representation that content is loading or in progress of change | Busy buttons, spinners and processing states reflect real work. |
| 🟡 | **Text** — Explaining the loading state | Most web states are named; some mobile loaders remain uncaptioned. |
| 🟢 | **Time** — Determine how long the time between two actions must be to require a loading component | Loading starts for real asynchronous requests, without artificial delay. |
| 🟢 | **Accessibility** — Ensure your loading state can be clearly seen | Native indicators and web status regions remain visible. |
| ⚪ | **Visuals** — Entertain the user with an illustration during the loading state | Operational loading does not need decorative entertainment. |

## [Card — Design system](https://www.checklist.design/design-system/card)

| | Item | Why |
|---|---|---|
| 🟢 | **Style** — Consider default background, border, shadow | White or semantic surfaces use restrained borders and corners. |
| 🟢 | **Consistency** — Ensure you have one base style for all cards | AppCard and workspace-panel supply shared structure. |
| 🟢 | **Spacing** — A framework to sort your padding levels by | Internal padding follows the documented rhythm. |
| 🟢 | **Responsiveness** — Consider the structure of the content in all various screen sizes | Mobile stacks content; web panels collapse at content breakpoints. |
| 🟢 | **Content hierarchy** — The primary action/s you want users to perform | Titles precede evidence and actions. |

## [Badge — Design system](https://www.checklist.design/design-system/badge)

| | Item | Why |
|---|---|---|
| 🟢 | **Detail** — A badge can have a numeric value, or a basic shape | Text labels identify review and evidence state. |
| 🟢 | **Color** — Badges can represent your standard states - error, success, warning | Shared semantic variants distinguish warning and status. |
| ⚪ | **Offset position** — A badge should sit outside it's relevant element to gain attention easier | These are inline status labels, not unread-count overlays. |

## [Drawer — Design system](https://www.checklist.design/design-system/drawer)

| | Item | Why |
|---|---|---|
| 🟢 | **Placement** — Which edge the drawer slides from - most commonly from left (navigation) or right (details/settings) | Navigation opens from the right edge. |
| 🟢 | **Dimensions** — Typically full height, but width can vary. Should be wide enough for complex content to be shown, without taking over the entire page | Width is bounded by the viewport. |
| 🟢 | **Overlay** — A semi-transparent background for the remaining screen area to bring focus to the drawer | Radix overlay separates navigation from the page. |
| 🟢 | **Header** — Top section with a title describing drawer contents or purpose, along with a close action (optional) | Each dialog has a role-specific title and close button. |
| 🟢 | **Content area** — Main section, which should be scrollable if content exceeds window height | Drawer navigation is a separate content area. |
| 🟢 | **Open and close trigger** — How user activate the drawer — typically a button to open, while closing can have multiple ways: clicking overlay, a close button, or pressing Esc on keyboard should all be active options | Open, close, outside dismissal and Escape use Radix behavior. |
| ⚪ | **Footer** — Fixed area at the bottom for actions, usually a primary and secondary e.g. Save & Cancel | Navigation has destinations rather than a save/cancel footer. |

## [Breadcrumb — Design system](https://www.checklist.design/design-system/breadcrumb)

| | Item | Why |
|---|---|---|
| 🟢 | **Current location** — The current page shown as the final item in the trail, visually distinct from the preceding levels, typically not a link | Detail screens identify the current record in their heading. |
| 🟢 | **Level links** — All preceding levels rendered as active links, each one navigating directly to that level rather than requiring back-button presses | Explicit parent/back links return to the relevant collection. |
| ⚪ | **Separator character** — A consistent visual separator between levels (a slash, chevron, or arrow) distinguishing hierarchy from a list of links | Shallow detail screens use a back link rather than a multi-level trail. |
| ⚪ | **Truncation for long paths** — Deep hierarchies collapsed with an ellipsis, preserving the root and current page while hiding intermediate levels behind a toggle | There is no deep breadcrumb path to truncate. |

## [Alert — Design system](https://www.checklist.design/design-system/alert)

| | Item | Why |
|---|---|---|
| 🟢 | **Descriptive message** — Alert copy that explains what happened and what the user needs to do, rather than generic labels like 'Error' or 'Success' | Errors identify the failed action and recovery. |
| 🟢 | **Placement and stacking** — Where alerts appear in the layout, inline near relevant content, at the top of a form, or in a fixed notification area, and how multiple simultaneous alerts are ordered | Alerts are positioned near the affected form or collection. |
| ⚪ | **Dismissible option** — A close button on alerts that are informational and don't require action, letting the user clear them when they're done | Persistent errors remain until retry; they should not disappear before resolution. |
| 🟡 | **Icon reinforcement** — An icon alongside the message that reinforces the alert type, not as a substitute for colour but as a signal for colour-blind users | Some messages use text without a separate icon; meaning is not color-only. |
| 🟢 | **Semantic variants** — Distinct visual treatments for informational, success, warning, and error states, using colour, iconography, or both | Warning/error/success treatments are distinct. |
| 🟢 | **Inline action (if applicable)** — An optional link or button inside the alert for the most relevant next action, avoiding the need to navigate elsewhere to resolve it | Retry actions are included where a request can be repeated. |

## [Accordion — Design system](https://www.checklist.design/design-system/accordion)

| | Item | Why |
|---|---|---|
| 🟢 | **Header** — The clickable area that triggers expanding and collapsing and has a title | Question headers describe their answer. |
| 🟢 | **Expand/collapse icon** — Visual indicator of the current state — typically a plus/minus, or a caret/chevron that rotates between states | Chevron indicates expanded state. |
| 🟢 | **Content area** — The content that shows or hides when toggled, containing detailed information associated with the header | The answer is in the associated content region. |
| 🟢 | **States** — Default (collapsed), expanded, hover, focused, and disabled | Radix provides focus and expanded states. |
| 🟢 | **Expanding logic** — Decide if users can open multiple sections at once, or one at a time | The FAQ uses a declared expansion model. |

## [Checkbox — Design system](https://www.checklist.design/design-system/checkbox)

| | Item | Why |
|---|---|---|
| 🟢 | **Label** — Text paired with the checkbox to indicate what is enabled if selected | Consent labels state precisely what is agreed to. |
| 🟢 | **Default selection** — Whether the checkbox is selected or not | Processing and training permission are not preselected. |
| 🟢 | **Style** — Make sure checkbox is unique and stands out from other input options, and consider whether it's in a container, how it's grouped, and what colour it uses | Native checkbox shape is distinct from text inputs. |
| 🟢 | **States** — Default, hover, focused, active and disabled (see documentation tab for examples) | Native focus and disabled states are preserved. |

## [Searchbar — Design system](https://www.checklist.design/design-system/searchbar)

| | Item | Why |
|---|---|---|
| 🟢 | **Input field** — A clear container for a user to start typing in | Search inputs have visible boundaries. |
| 🟢 | **Label or placeholder text** — Identify the purpose of the field is for them to search | Labels identify fields or review queue scope. |
| ⚪ | **Quick links, autocomplete and suggestions** — As the user is typing, offer available links and phrases based on what they have entered so far | Small scoped record lists do not require autocomplete. |
| ⚪ | **Submit search button** — A visible link to submit search and view results | Filtering is immediate, so an extra submit button is unnecessary. |
| ⚪ | **Previous searches** — Showing what a user has searched before can speed up their experience if they frequently search the same queries | Search history storage is unnecessary for this pilot. |
| 🟢 | **Appropriate visibility** — Search should be directly linked to what you are looking for, whether it's searching across the entire platform or in a specific area | Filters appear with their affected collection. |

## [Modal — Design system](https://www.checklist.design/design-system/modal)

| | Item | Why |
|---|---|---|
| 🟢 | **Title** — Clear, simple text explaining the action of the modal | Navigation and confirmation dialogs identify their purpose. |
| 🟢 | **Actionable item** — A button or link to continue or close the event | Destination or confirmation controls state their action. |
| 🟢 | **Close action** — A way to exit the modal | Visible close controls and platform back/Escape are available. |
| 🟢 | **Responsiveness** — Consider the size of the modal on different device sizes, and whether a modal is suitable on all | Dialogs are bounded to the viewport. |
| 🟢 | **Background change behind modal** — Darken, blur or lighten - change the background behind the modal to bring focus to it | The backdrop separates the active dialog. |
| 🟢 | **Description** — Incase they require more information to understand how to make their decision | Dialog descriptions explain their scope. |

## [Icon — Design system](https://www.checklist.design/design-system/icon)

| | Item | Why |
|---|---|---|
| 🟢 | **Responsiveness** — The flexibility in detail of the icons at varying sizes | Lucide and Material icons retain simple shapes at control size. |
| 🟢 | **Visual style consistency** — All icons share the same stroke weight, corner radius, and optical sizing approach | Each platform uses one established icon family. |
| 🟢 | **Color** — Black and white, flat colors or gradients | Icons use the shared palette. |
| 🟢 | **Naming** — Name an icon by what it literally is so it can be used flexibly | Library names describe the icon shapes. |

## [Table — Design system](https://www.checklist.design/design-system/table)

| | Item | Why |
|---|---|---|
| 🟢 | **Table header** — The value of each column to provide structure for the row content | Review tables have labeled column headers. |
| 🟢 | **Row style** — Borders and contrasting background colours can be explored to differentiate | Borders and surfaces separate rows. |
| 🟢 | **Spacing** — Define the consistent padding of each row and the header | Header and row padding are consistent. |
| 🟢 | **Search** — The ability to find a specific keyword or row | Search narrows the visible review records. |
| 🟢 | **Actions** — Performing a task based on the row and information seen e.g. view, edit, delete | A visible review action opens each case. |
| 🟢 | **Filter and sort** — Allow users to customise what they want to see in the table and in which order | Status/severity filters and sort controls are available. |
| 🟢 | **Responsiveness** — Determine the structure on significantly smaller devices - whether the information collapses into an accordion for example | Overflow tables scroll within their container. |
| 🟡 | **Pagination** — Breakpoints in the table for digesting information in parts | Records are fetched across API pages; the UI does not yet offer page-size controls. |

## [Tabs — Design system](https://www.checklist.design/design-system/tabs)

| | Item | Why |
|---|---|---|
| 🟢 | **Labels** — Name of each tab | Settings and mobile destinations have concise labels. |
| 🟢 | **Content area** — Where the content for the active tab is displayed | The active section has a dedicated content area. |
| 🟢 | **Style** — How the active tab and inactive tabs differentiate visually, as well as the tab container overall | Current-page styling differentiates navigation. |
| 🟢 | **Item order** — Consider the arrangement of tabs to be ordered by popularity or familiarity | Farmer navigation puts Home, Fields and Scan before account controls. |
| 🟢 | **States** — Default, active, hover are the key states | Native selection and web focus states remain visible. |

## [Avatar — Design system](https://www.checklist.design/design-system/avatar)

| | Item | Why |
|---|---|---|
| ⚪ | **Visualiser** — Show what the avatar looks like before posting or updating | Accounts use initials, not editable image previews. |
| ⚪ | **Link to upload or select avatar** — Accessible link for a user to select | No profile-image upload is offered. |
| 🟢 | **Placeholder image** — If a user hasn't uploaded or added an avatar yet there should be a placeholder e.g. a default icon, or the user's initials | Initials identify the current account. |
| ⚪ | **Acceptable file types** — Tell the user what file types are allowed (JPEG, PNG, SVG) | No avatar file upload requires format instructions. |
| ⚪ | **Status change updating avatar** — This doesn't have to be apart of the avatar component (it can be a banner or toast for example), but it is possible to incorporate it | No avatar upload operation exists. |
| 🟢 | **Alternatives** — If a user doesn't want to upload an image, offer an illustrative alternative, as it's better than nothing and can still convey their personality | Initials provide a readable identity without a photograph. |
| ⚪ | **Editing uploaded avatar** — Allow a user to crop and resize their avatar before saving it | No photo editor is required for initials. |

## [Toast — Design system](https://www.checklist.design/design-system/toast)

| | Item | Why |
|---|---|---|
| 🟢 | **Copy** — The text in the toast | Snackbars describe saved actions or recoverable failures. |
| 🟢 | **Placement** — Toast should appear on the corners of the viewport, not as the focus | Mobile snackbars appear along the lower edge. |
| 🟢 | **Usage** — Toasts are triggered to appear after an action or event | Messages follow user actions. |
| 🟢 | **Variants** — Dictated by colour usually, variants affects the emotion of a message | Text communicates meaning independently of color. |
| ❔ | **Length of appearance** — Toasts should be visible long enough to read but short enough to not obstruct other information for too long | Reading duration with accessibility settings needs device verification. |
| 🟢 | **Dismissable** — Depending on the amount of content, a toast can be closed by a user (it should fade away shortly after appearing if it cannot be manually dismissed) | Native snackbar behavior supports timed dismissal. |

## [Date Picker — Design system](https://www.checklist.design/design-system/date-picker)

| | Item | Why |
|---|---|---|
| 🟢 | **Calendar grid** — A month view with days arranged in a weekly grid, navigable forward and backward by month, as the primary date selection surface | Native date inputs provide calendar selection. |
| 🟢 | **Text input alongside** — A free-text date field paired with the calendar, so users who know the date can type it rather than relying on clicking only | Users can type dates directly. |
| 🟢 | **Date range selection (if applicable)** — The ability to select a start and end date, with the range highlighted across the calendar grid and both values independently editable | Report filters provide independently editable range ends. |
| ⚪ | **Disabled dates** — Past dates, unavailable dates, or out-of-range dates visually distinct from selectable ones | Historical reports do not require unavailable-day constraints. |
| ❔ | **Today shortcut** — A clearly labelled button or link to jump to today's date | Native picker shortcuts vary by browser and device. |
| 🟢 | **Locale and format** — The calendar respecting regional conventions e.g. week starting on Monday or Sunday, date format in the text input matching the user's locale (DD/MM or MM/DD) | Native controls follow platform locale conventions. |
| ⚪ | **Time selection (if applicable)** — When a time is also required, a time picker integrated with or accessible directly from the date picker (not a separate, disconnected control) | Report date filtering does not require a separate time picker. |

## [Banner — Design system](https://www.checklist.design/design-system/banner)

| | Item | Why |
|---|---|---|
| 🟢 | **Style** — How the banner types look (fill, text colour, border radius etc) | Shared feedback surfaces use readable semantic colors. |
| 🟢 | **Content** — A title is a must but you can consider a description if you feel a title does not convey enough information | Messages identify what happened. |
| 🟢 | **Types** — Banners typically appear as 5 options: information, success, warning, error, neutral. This helps visually establish context and level of importance. | Error, warning and neutral notices have defined styles. |
| 🟢 | **Call to action button** — A banner may call for the user to do something, like fix the error it is calling out, or viewing the successful outcome of an event. | Retry or follow-up is present when actionable. |
| 🟢 | **Placement** — Where the banner sits on the page, dependent on context and importance | Messages appear near affected content. |
| ⚪ | **Dismissable** — Whether the banner can be dismissed. Positive/neutral banners (info and success) would suit this, but not warning/error banners as they are too critical. | Important consent and failure notices remain until resolved. |

## [Toggle — Design system](https://www.checklist.design/design-system/toggle)

| | Item | Why |
|---|---|---|
| 🟢 | **Context** — Explaining what the toggle will do | Consent controls explain their purpose. |
| 🟢 | **Transition** — A clear visual change of the toggle switching between different states | Native selection state changes visibly. |
| 🟢 | **State** — How the button changes based on the interaction, examples below | Checked and unchecked states are distinct. |

## [Admin Panel — Web app](https://www.checklist.design/web-app/admin-panel)

| | Item | Why |
|---|---|---|
| 🟢 | **Role-based access** — The admin panel visible and accessible only to users with the appropriate permissions | Routes and APIs enforce administrator access. |
| 🟡 | **User management** — A view of all users in the organisation with the ability to invite, edit roles, and remove members | The panel manages reviewed applications; full member lifecycle remains operator-managed. |
| ⚪ | **Organisation settings** — Controls for configuring the product at an account level — name, logo, SSO, domains | SSO, custom domains and white-label settings are outside this pilot. |
| 🟡 | **Usage overview** — High-level metrics on how the product is being used across the organisation, with ability to export information for reporting | Field overview is available; no invented platform-usage totals are shown. |
| 🟢 | **Billing and plan management** — Access to subscription details, seat counts, and invoices at the account level | Admin publishes plans and approves requests; billing stays manual. |
| 🟢 | **Audit log** — A record of account related actions taken by users e.g. logins, permission changes, deletions | Onboarding decisions appear in a chronological audit history. |
| ⚪ | **Danger zone** — Destructive account-level actions e.g. deleting the workspace, transferring ownership | Workspace destruction is deliberately not exposed as a casual UI action. |

## [User Management — Web app](https://www.checklist.design/web-app/user-management)

| | Item | Why |
|---|---|---|
| 🟡 | **User list** — A table of all users showing name, email, role, and account status | Pending applicants are listed; a comprehensive member table is not part of this pilot panel. |
| ⚪ | **Invite user action** — A clear way to add new members by email, with an option to set their role before sending | Users apply through reviewed access instead of receiving invitations. |
| 🟢 | **Roles and permissions** — The ability to assign and change what each user can see and do within the product | Application type determines the approved role; server RBAC controls scope. |
| ⚪ | **Pending invitation status** — A view of invitations sent but not yet accepted, with the option to resend or revoke | Pending applications replace invitation lifecycle. |
| 🟡 | **Search and filter** — The ability to find users quickly by name, email, role or other additional user information that applies | Pending requests are visible; large-scale member filtering is not included. |
| 🟡 | **Remove or deactivate user** — A clear way to revoke access, with a distinction between temporary deactivation and permanent removal | Credential/session revocation exists; organization member lifecycle is operator-managed. |

## [Data Table — Web app](https://www.checklist.design/web-app/data-table)

| | Item | Why |
|---|---|---|
| 🟢 | **Sortable columns** — Column headers that sort rows by that value on click, toggling ascending and descending | Review queue exposes explicit priority/date sort selection. |
| ⚪ | **Column visibility and order** — Controls to show or hide individual columns and drag to reorder them | A fixed evidence schema avoids unnecessary column configuration. |
| ⚪ | **Row selection and bulk actions** — Checkboxes on each row and a persistent action bar appearing when rows are selected | Independent expert judgments are not bulk-approved. |
| 🟢 | **Row actions on hover** — Contextual actions (edit, delete, view) appearing when hovering over a row | Review actions remain visible rather than relying on hover. |
| 🟢 | **Search and filter** — A search input for quick lookup alongside filter controls for narrowing by specific attributes. | Search and current filter selections are visible. |
| 🟡 | **Pagination** — Controls to navigate between pages of results, with an option to choose how many rows show per page | All API pages are read; browser page-size controls are not supplied. |
| 🟡 | **Frozen columns** — The first column pinned so it remains visible when the user scrolls horizontally | Tables scroll on narrow screens; the first column is not frozen. |
| 🟢 | **Export action** — A way to download the visible or selected rows as CSV, spreadsheet, or another format | Reports and organization fields export the visible records. |
| 🟢 | **Empty and loading states** — The states shown when the table has no rows or when data is being fetched | Loading, failed request and empty collection are distinct. |

## [Single Item Detail — Web app](https://www.checklist.design/web-app/single-item-detail)

| | Item | Why |
|---|---|---|
| 🟢 | **Clear title or identifier** — The name, ID, or primary label of the item, shown prominently at the top of the screen | Field and case headings identify the record. |
| 🟢 | **Status indicator (if applicable)** — A clear signal of the item's current state (active, pending, completed, archived) | Labeled states distinguish uncertainty and review progress. |
| 🟢 | **Key details section** — The most important attributes of the item surfaced prominently, with secondary details available below or in a sidebar | Assessment, evidence and human review are grouped. |
| 🟢 | **Edit action** — A clear way to modify the item's details, either inline or via an edit mode | Eligible experts can claim and submit their independent review. |
| 🟢 | **Related items or activity** — Associated records, linked content, or a history of changes related to this item | Frames, original video and review history stay with the record. |
| 🟢 | **Breadcrumb or back navigation** — A way to return to the list or parent context | Parent links return to the relevant list. |
| ⚪ | **Destructive actions** — Delete or archive options, available on the detail screen but kept visually separate from the primary actions | Evidence is retained and governed; casual record deletion is not offered. |

## [Empty State — Web app](https://www.checklist.design/web-app/empty-state)

| | Item | Why |
|---|---|---|
| 🟡 | **Illustration or icon** — A visual that signals the empty state and gives the screen some personality, rather than feeling broken | Some sparse administrative lists use text only; farmer states include contextual icons. |
| 🟢 | **Clear heading** — A short, plain-language title naming what's missing | Empty headings name the missing records. |
| 🟢 | **Supporting description** — A brief explanation of what belongs in this space, most useful for first-time users | Descriptions distinguish first use from filtering. |
| 🟢 | **Primary action** — A CTA pointing toward the next step: creating, importing, connecting etc | Farmer and organization empty states lead to field setup. |
| 🟢 | **Zero state vs. no-results state** — A distinction between a screen that is empty because nothing has been created versus one that returned no search or filter results | No-results filters can be cleared; new workspaces prompt setup. |
| 🟢 | **Error state variant** — A separate variant for when content failed to load, as opposed to genuinely being empty | Request failures show an error and retry rather than pretending records are absent. |

## [Analytics — Web app](https://www.checklist.design/web-app/analytics)

| | Item | Why |
|---|---|---|
| ⚪ | **Date range selector** — A date picker with shortcuts for today, last 7 days, last 30 days, this month, and custom range | The overview explicitly shows latest field indications; report pages provide historical date filters. |
| 🟢 | **Headline metrics** — The most important numbers displayed as prominent headline figures | Counts summarize actual filtered fields. |
| 🟢 | **Charts with labels and axes** — Visualisations with clearly labelled axes, a legend where needed, and readable tick marks | The donut has a full text legend and counts; axes do not apply. |
| ⚪ | **Period comparison** — A percentage or absolute change indicator showing how each metric has moved relative to the prior period | No validated trend comparison is claimed from a latest-scan snapshot. |
| 🟢 | **Segment breakdown** — The ability to slice a metric by properties e.g. channel, device, geography, or another attribute | District and assessment filters scope the same chart and export. |
| 🟢 | **Last updated indicator** — A visible timestamp or refresh button showing when the data was last updated (if it is not automatically refreshing) | Refresh records explicitly reloads the dataset. |
| 🟢 | **Loading and empty states** — Skeleton loaders while data is fetching, and a contextual message when no data exists for the selected range | Loading and empty states identify unavailable content. |

## [Audit Log — Web app](https://www.checklist.design/web-app/audit-log)

| | Item | Why |
|---|---|---|
| 🟢 | **Event list** — A table of logged events showing the action performed, the user who performed it, and a timestamp | Latest onboarding events show action, reference and timestamp. |
| 🟡 | **Actor identification** — The name and identifier of the user who triggered each event, including system-generated actions | Actors are stored in the backend audit log; the compact UI shows application references. |
| 🟢 | **Event type** — A categorised label for what kind of action was taken (login, permission change, deletion, export) | Event names distinguish submission and approval/rejection. |
| 🟢 | **Affected resource** — The specific record, file, or setting that was changed and what had been changed | Application references identify affected requests. |
| 🟡 | **Date range filter** — The ability to narrow the log to a specific time period. | The compact recent-history view has no date picker. |
| 🟡 | **Search and filter** — The ability to filter by user, event type, or affected resource to narrow down | No search controls are provided for the recent onboarding feed. |
| 🟡 | **Export** — The ability to download the audit log as a CSV for compliance reporting or external review | The operator can query audit records; this view has no CSV action. |

## [Search Results — Web app](https://www.checklist.design/web-app/search-results)

| | Item | Why |
|---|---|---|
| 🟢 | **Search input** — A search field at the top of the results, pre-filled with the current query so it can be refined without starting over | Current search text remains editable above results. |
| 🟢 | **Result count** — How many results were found for the query | Counts reflect filtered fields or cases. |
| 🟢 | **Result items** — Each result shown with enough to identify it — title, type, image, and a snippet of the matching content | Results include farm, field, status and date context. |
| 🟢 | **Result type indicators** — A label or icon marking what kind of item each result is (document, person, project, message) | The surrounding collection identifies whether items are fields or cases. |
| 🟢 | **Filters** — The ability to narrow results by category, date, status, or other relevant values | Domain filters narrow results. |
| 🟢 | **No results state** — The state shown when a query returns no matches, ideally with suggestions for what to try instead | No-match states suggest clearing filters. |
| ⚪ | **Recent searches** — A list of the user's previous queries, shown when the search field is focused but empty | Recent-query storage is unnecessary for this scoped pilot. |

## [Onboarding — Mobile app](https://www.checklist.design/mobile/onboarding)

| | Item | Why |
|---|---|---|
| 🟢 | **Steps** — The number of steps in the onboarding flow, limited to what is genuinely required before the app can be used | The introduction is a short optional sequence. |
| 🟢 | **Progress indicator** — A clear indication of how many steps remain and where in the sequence the user currently is | The sequence indicates its current step. |
| 🟢 | **Step navigation** — A clear mechanism for advancing through steps e.g. a 'next' button or a horizontal swipe gesture | Next/back controls navigate the sequence. |
| 🟢 | **Contextual permissions** — Permissions surfaced at their contextually relevant moment within onboarding, rather than grouped at the start | Camera permission is deferred until recording. |
| 🟢 | **Skip option** — A visible way to exit onboarding early and explore the app, with setup available to complete later | Users can proceed directly to sign-in or account creation. |
| 🟢 | **Personalisation step** — One or two choices that make the app feel tailored from the start e.g. your name, interests, a key piece of information that applies to the product | Account name and field setup personalize the experience. |
| ❔ | **Keyboard handling** — Views that adjust correctly when the keyboard appears, appropriate keyboard types per field, and Next advancing to the following input | Large-text widget checks pass; physical keyboard and autofill behavior need device QA. |

## [Onboarding — Web app](https://www.checklist.design/web-app/onboarding)

| | Item | Why |
|---|---|---|
| ⚪ | **Progress indicator** — An indication of how many steps are involved and where the user currently is in the sequence | The application is a single form, not an artificial multistep wizard. |
| 🟢 | **Welcome message** — A brief message acknowledging this is a new experience and orienting the user toward what the product does. | Role-specific descriptions explain the workspace. |
| 🟢 | **Account setup** — The minimum information needed to personalise the experience, gathered at the start | Only identity, organization context, plan and consent are collected. |
| 🟢 | **Product highlights** — Key features introduced through short contextual tips or a visual walkthrough | Optional public how-it-works content explains capture and review. |
| 🟢 | **First action prompt** — A clear prompt directing the user to an action or feature | Farmer empty states point to the first field; team applications point to review. |
| 🟢 | **Completion confirmation** — A clear acknowledgement that setup is complete, transitioning the user into the main product | Application receipts and farmer account confirmation state what happens next. |

## [Gesture navigation — Mobile app](https://www.checklist.design/mobile/gesture-navigation)

| | Item | Why |
|---|---|---|
| ❔ | **Swipe to go back** — The standard action to allow a user to go back without tapping a button | Native route back gestures depend on platform and device settings. |
| ⚪ | **List item swipe actions** — Revealing quick actions such as delete, archive, mark as read on an item without opening it | Evidence records have no swipe-to-delete action. |
| 🟢 | **Pull to refresh** — For scrollable content lists with a visible indicator and haptic confirmation when triggered | Home supports pull-to-refresh after the audit correction. |
| ⚪ | **Long press menus** — Triggered by long pressing, an item reveals actions relevant to that specific element | No hidden long-press actions are required. |
| 🟡 | **Pinch to zoom** — Image and map content supporting standard pinch-to-zoom, with zoom level reset logically on navigation away | Evidence thumbnails are available; native pinch-zoom behavior is not supplied by the thumbnail strip. |
| ⚪ | **Drag to reorder** — Lists or cards that can be reordered supporting long-press-to-lift and drag, with clear visual feedback during the drag state | Field record order is data-driven rather than user-reorderable. |
| ⚪ | **Gesture hints** — A subtle animation or tooltip on first encounter with a key gesture, hinting at its existence | Primary actions have visible buttons and do not depend on gesture discovery. |
| ❔ | **Haptic feedback** — Beneficial for key gesture moments where your finger may cover the screen and therefore it's not clear whether you have engaged with the gesture e.g. the pull-to-refresh, long press or drag actions | Haptics need physical-device verification. |

## [Splash Screen — Mobile app](https://www.checklist.design/mobile/splash-screen)

| | Item | Why |
|---|---|---|
| 🟡 | **Logo or wordmark** — The app brand mark centred on a clean background | Session initialization uses a loading indicator rather than a separate branded splash animation. |
| 🟢 | **Brand background** — A solid or subtly branded background that makes the transition from the  mobile home screen clear | The app theme supplies the neutral background. |
| 🟢 | **Launch duration** — The splash visible only for as long as the app genuinely needs to initialise (not used as decorative padding) | No decorative delay is introduced. |
| ❔ | **Transition to first screen** — A smooth, intentional animation into the first real screen, ideally not a hard cut or jarring flash | Cold-launch animation must be assessed on a physical device. |
| 🟢 | **No interactive elements** — The splash screen contains no buttons, inputs, or tappable areas, it is purely for transition | Initialization has no interactive controls. |
| 🟢 | **Loading indicator** — For any initialisation taking more than a second so the user knows something is happening | A spinner remains visible while restoring a session. |

## [Resetting password — Flows](https://www.checklist.design/flows/resetting-password)

| | Item | Why |
|---|---|---|
| 🟢 | **Place reset link close to password field** — Style it as a link to show it is clickable | Sign-in help is adjacent to credentials. |
| 🟡 | **Ask for account details to verify** — In this case it's usually the email address that's requested, because it can recognise your account and be the channel the link is securely sent to. Note: If the user already entered their email address on the previous login page, that can be prefill this field and speed up the flow! | Recovery is a reviewed support request, not automated email verification. |
| ⚪ | **Show information has been sent** — Based on the account information provided in Step 2, explain how they can continue. If an email was provided, send an email for the next step. If a mobile number was provided, send a code or link to open. | The app does not falsely claim a reset message was sent. |
| ⚪ | **The message sent explains next steps** — This could be a link to a page that allows the user to reset their password. It could also be a code for the user to provide on a page to verify their account, to then reset their password. | No configured outbound recovery channel exists. |
| 🟡 | **Reset the password!** — Whether it's a verification code or a link to click behind an email address, the next page should be a clear text field to enter a new password. You can provide guidelines if you have requirements for the password to pass a threshold of strength to be accepted. | A verified operator can reset access; authenticated users can change their password themselves. |
| 🟡 | **Password successfully reset** — After the password has been reset, indicate the successful and push their momentum to their initial intent: logging in. | The operator-managed recovery process must confirm completion with the requester. |

## [Deleting account — Flows](https://www.checklist.design/flows/deleting-account)

| | Item | Why |
|---|---|---|
| 🟢 | **Show a link to delete account** — Don't make this difficult. This link should be visible in the profile or settings of a product. It should also be available in the support area. | Web privacy and mobile profile provide a deletion-request route. |
| ⚪ | **Politely ask for feedback** — It helps to know why somebody is choosing to leave. But, it should not be pressured or forcefully asked. Convey the request feedback to improve other people's experience and to also consider their personal reasons. | Feedback is not forced before a privacy request. |
| 🟢 | **Explain what it means to delete the account before confirming** — Be clear with what happens to the account and the information in it should a user close. Is all the data permanently deleted? Can they come back and restore their account? Is the deletion immediate, or can they use their account until a certain date? | Retention and operator review are explained before the request. |
| 🟡 | **Confirm account has been deleted** — Now that their account is deleted and it's finally complete, embrace that! Be comfortable acknowledging they have left. Do not show any passive aggressiveness. | The UI confirms the request only; the operator must confirm completed deletion separately. |

## [Canceling subscription — Flows](https://www.checklist.design/flows/canceling-subscription)

| | Item | Why |
|---|---|---|
| 🟢 | **Show a link in account details** — This doesn't have to be the first or most prominent link, but it should be clearly visible. If you're unsure about including it on the account page, it's suitable to place on the billing settings. | Organization usage and pricing offer contact paths for plan changes. |
| 🟢 | **Confirm intent to cancel** — Sometimes, a user misclicks. So it's okay to ask if they're sure they want to make this choice, and not just automatically canceling their subscription. But... while the user is there, you can attempt a last ditch effort to reel them back (it cannot be pressuring or manipulative). If the product can only be access with a subscription, you can remind them of the product's value. If the product can be access in a free version, you can remind them of that specific subscription's value. | Submitting a request does not automatically cancel a contract. |
| ⚪ | **Request a reason for canceling (optional)** — It can be helpful to receive feedback on why a user is canceling. Too expensive? Competitor preferred? Just don't need it anymore? It's an easy way to start identifying the key factors affecting churn. | A reason is optional in the request message. |
| 🟡 | **Confirm subscription has been canceled** — Now that it's canceled, make sure you tell the user when their subscription is active until. | Manual billing requires the operator to confirm the cancellation and effective date. |

## [Verifying account — Flows](https://www.checklist.design/flows/verifying-account)

| | Item | Why |
|---|---|---|
| 🟢 | **Establish a trigger point** — Clearly indicate when verification is required, giving context as to why verification is necessary. It is common to verify the email or phone number used for account creation, because this is ensuring the person with access to those details is the same person creating the account. | Expert and organization applicants are told access needs review. |
| ⚪ | **Method selection (optional)** — Depending on the level of sophistication you want to offer, you can make multiple verification methods available (email, SMS, authenticator). The common default is what the user is using to sign up with e.g. if signing up with email address, send code to email. | Administrator review replaces automated code verification in the pilot. |
| ⚪ | **Confirm delivery and contact information used** — Display the email address or phone number where the verification will be sent so the user can see it is the correct destination. That way if they have not received a code and the contact information provided was incorrect, they can see this, go back, and enter the correct value. | No outbound verification delivery is claimed. |
| ⚪ | **Ability to input verification code** — The input field can be intuitive to show a field per digit, but the default input field is perfectly accessible. | No one-time verification code is used. |
| ⚪ | **Incorrect value (and resend option)** — Provide specific error messages for different failure scenarios and clear next steps: Expired code: offer link to send a new code Incorrect code: ask to check email/SMS again or offer link to send new code Too many incorrect attempts: contact support team or wait for defined time period before trying again | There is no code-expiry or resend interaction to expose. |
| 🟢 | **Verification success state** — Display clear confirmation when verification succeeds and continue to next step of interface. | Approved users can sign in; pending users receive an explanatory refusal. |

## [Notification Settings — Web app](https://www.checklist.design/web-app/notification-settings)

| | Item | Why |
|---|---|---|
| ⚪ | **Categories** — Notification types organised into logical groups e.g. product activity, mentions, billing, security, marketing | Only in-workspace status updates are supported; no subscription categories are advertised. |
| ⚪ | **Channel selection** — Controls for which channel each notification type comes through e.g. in-app, email, push, or SMS | SMS, WhatsApp and push delivery are explicitly disabled. |
| ⚪ | **Frequency controls** — Where applicable, controls for how often notifications arrive e.g. immediately, daily digest, or weekly summary. | There is no scheduled outbound notification frequency. |
| ⚪ | **Global mute** — A way to temporarily silence all notifications without having to turn each one off individually | No external notification stream requires a mute control. |
| ⚪ | **Save confirmation** — A clear indication that preference changes have been saved. | No dummy preferences are offered to save. |

## [Maintenance — Web app](https://www.checklist.design/web-app/maintenance)

| | Item | Why |
|---|---|---|
| 🟢 | **Clear status message** — A plain-language explanation that the product is currently unavailable and why | Failed API requests identify unavailable data and offer retry. |
| ⚪ | **Estimated return time** — When the product is expected to be back online, as specifically as possible | An unknown outage duration is not invented. |
| ⚪ | **Status page link** — A link to a live status page where users can monitor progress and see real-time updates | No externally operated status service was supplied. |
| 🟢 | **Contact or support link** — A way to reach support for urgent issues that cannot wait for the maintenance window to end | Support remains reachable through public navigation. |
| 🟢 | **Brand consistency** — A maintenance page styled consistently with the product, even if the content is minimal | Error states use the same product identity. |

## Remaining validation boundaries

Native camera/preview/flash/flip, haptics, cold launch and assistive-technology behavior need real Android/iOS and NVDA/VoiceOver runs. Reviewed recovery, deletion and commercial cancellation need an accountable operator; the interface confirms requests rather than pretending those operations have completed. Future self-service administration and extensive audit-query tooling are recorded as partial, not represented as shipped.
