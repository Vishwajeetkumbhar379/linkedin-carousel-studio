# Selling from buildwithvvish.com: checkout, fees, tax and German rules

Checked 23 Oct 2026. I'm not a lawyer or a tax adviser: this is a researched starting point, so confirm the two legal steps (step 0 and step 1 below) with the offices named there. **No checkout is live.** Product pages show "Coming soon" until Vish approves each product and connects his own account.

## 0. Before the first euro: two permissions (Vish)
1. **Residence permit.** Selling products counts as self-employment. Many student and job-search permits say "Selbständige Tätigkeit nicht erlaubt", and self-employment alongside them needs a separate permission (§ 21 Abs. 6 AufenthG). Working without it can cost the permit.
   - Check the wording on your permit card.
   - Ask the Ausländerbehörde (Offenburg / Ortenaukreis) for "Erlaubnis zur selbständigen Tätigkeit als Nebentätigkeit".
   - Sources: [Hochschule Konstanz info sheet](https://www.htwg-konstanz.de/fileadmin/pub/fk_ws/stg_wdt/Jobs_auslaendische_Studierende.pdf), [Uni Frankfurt](https://www.uni-frankfurt.de/152000463.pdf), [Anwalt Diedrich](https://www.anwalt-diedrich.de/arbeiten-waehrend-des-studiums/).
2. **Tax registration.**
   - Gewerbeanmeldung at the Gewerbeamt (selling digital products is usually a trade).
   - Then the "Fragebogen zur steuerlichen Erfassung" on ELSTER.
   - Tick the Kleinunternehmerregelung (§ 19 UStG): since 2025 it applies up to €25,000 net last year and €100,000 net this year. With it, you charge no German VAT yourself.
   - Sources: [mehrwertsteuerrechner.de](https://www.mehrwertsteuerrechner.de/kleinunternehmerregelung/), [taxtify](https://taxtify.de/kleinunternehmerregelung/).

## 1. The options, per sale

| Option | Who is the seller to the buyer | Fee | VAT and tax abroad | On a €1 sale (EU card, VAT incl.) | On a €7 sale |
|---|---|---|---|---|---|
| **Stripe Managed Payments** (merchant of record) with Payment Links | Stripe | 1.5% + €0.25 (standard EEA card) + 3.5% | Stripe collects and pays VAT/GST in 80+ countries | Vish keeps about **€0.54** (fees €0.30, VAT ~€0.16) | about **€5.28** |
| **Lemon Squeezy** (merchant of record, owned by Stripe) | Lemon Squeezy | 5% + 50¢, +1.5% for buyers outside the US | Included | about **€0.28** | about **€4.9** |
| **Polar** (merchant of record) | Polar | Starter 5% + 50¢ (Pro plan $20/month: 3.8% + 40¢), +1.5% for non-US cards | Included | about **€0.28** | about **€4.9** |
| **Gumroad** | Gumroad | 10% + 50¢ (+ processing, sources disagree) | Included | about **€0.24** or less | about **€4.7** or less |
| **Stripe Payment Links, no MoR** | Vish | 1.5% + €0.25 (EEA), 2.5% + €0.25 UK, 3.15% + €0.25 other | Vish's job: Kleinunternehmer in Germany; EU buyers fine under the €10,000 EU limit; UK, Swiss and other non-EU buyers can create tax duties from the first sale | about **€0.74** | about **€6.65** |

**Sources** (checked 23 Oct 2026):
- [Stripe pricing (DE)](https://stripe.com/en-de/pricing): 1.5% + €0.25 standard EEA, 2.8% premium EEA, 2.5% UK, 3.15% international, +2% currency conversion; Stripe Tax 0.5% per transaction where registered.
- [Stripe Managed Payments](https://stripe.com/managed-payments): +3.5% on top of processing; 80+ countries; digital products only; no setup or monthly fee; Stripe can refund within 60 days.
- [Managed Payments eligibility](https://docs.stripe.com/payments/managed-payments/eligibility): e-books, digital media and online courses are eligible; coaching and services are not.
- [Stripe Tour Berlin 2026](https://stripe.com/newsroom/news/stripe-tour-berlin-2026): Managed Payments generally available for German businesses (June 2026).
- [Lemon Squeezy pricing](https://www.lemonsqueezy.com/pricing).
- [Polar fees](https://docs.polar.sh/merchant-of-record/fees).
- [Gumroad, third-party comparison](https://www.wearefounders.uk/best-platforms-for-selling-digital-products-in-2026/).
- The EU €10,000 limit on cross-border B2C digital sales: [Taxually](https://www.taxually.com/blog/eu-vat-oss-ioss-distance-selling-2026), [AADE FAQ](https://aade.gr/sites/default/files/2026-08/FAQs_one-stop-shop-hlektroniko-emporio-EN.pdf).

The euro figures are estimates. Tax-inclusive pricing assumes German VAT (19%) and a standard EU card. Lemon Squeezy and Polar quote fees in dollars, converted at about par.

## 2. Recommendation
**Stripe Managed Payments + Payment Links.**
- It's the cheapest option that also takes the tax work off Vish: Stripe is the seller of record, so VAT, OSS, UK VAT, invoices, fraud and disputes are Stripe's.
- No monthly fee, and Payment Links need no code: the product page just links to them.
- It keeps one Stripe account for later (bundles, subscriptions).

**Fallback:** Lemon Squeezy, if Stripe's eligibility review says no.

**What it means for the value ladder:**
- **€1 tier.** Fees plus VAT take about 46% of €1. Keep it as a trust step ("pay €1 for the exact file"), not as income. Don't add more €1 products than needed.
- **€5 to €10 tier.** This is the real income step: about 75% reaches Vish at €7.
- **Never fake anchors.** No "was €99" and no fake countdowns. German law (UWG, PAngV) and Instagram's trust both punish them.

## 3. What the product page and checkout must show (Germany)
- **Final price including VAT,** with the seller named. With Managed Payments, Stripe's checkout shows the tax. PAngV: show prices as consumers pay them.
- **The order button.** It must say "zahlungspflichtig bestellen" or the clear English equivalent, "Buy now, payment required" (§ 312j Abs. 3 BGB). Stripe's hosted checkout handles the button; don't add your own "order" step before it.
- **Right of withdrawal for digital downloads.** It ends when the download starts, but only if the buyer:
  1. expressly agreed to immediate delivery;
  2. confirmed they lose the right;
  3. got a confirmation on a durable medium (§ 356 Abs. 5 BGB).

  With a merchant of record, their checkout and terms cover this. Without one, Vish needs the two checkboxes and the confirmation email himself.
- **Impressum** (§ 5 DDG) on the site: full name, a postal address where he can be reached (not a P.O. box), email, and later a VAT ID or tax number note. The site needs one already, because of the newsletter and the partner form. It's waiting for Vish's address (`docs/impressum-template.md`).
- **Privacy policy:** add the payment provider (Stripe) and the email tool (MailerLite) as processors. The current `privacy.html` covers Instagram and the newsletter.

## 4. Delivery flow (once approved)
1. **Product.** Create it in Stripe with tax code `txcd_10302000` (digital books, downloadable) or `txcd_10000000` (electronically supplied services), and turn Managed Payments on for it.
2. **Payment Link** with "After payment: redirect to" `https://buildwithvvish.com/thanks/<product>?session_id={CHECKOUT_SESSION_ID}`.
3. **Delivery:**
   - **Simplest:** attach the file to Stripe's receipt email, or show the download link on the thanks page with a long random path. Change it if it leaks.
   - **Later:** a `/api/deliver` route in the Worker checks the Checkout Session with the Stripe API (secret key in Cloudflare) before it shows the file.
4. **Email.** MailerLite automation "Bought <product>": the delivery email (draft in `buildwithvish/emails/products.md`), then the bundle offer 3 days later, only for people who opted in.
5. **Counting.** Sales get counted in the weekly report, from the Stripe dashboard (`docs/analytics.md` fields: sales, revenue, refunds).

## 5. What Vish needs to do (in order)
1. Ask the Ausländerbehörde about self-employment on his permit.
2. Register the trade and tax (Gewerbeanmeldung, ELSTER questionnaire, Kleinunternehmer).
3. Fill in `docs/impressum-template.md` (address).
4. Create a Stripe account, apply for Managed Payments, and add his bank account.
5. Approve each product and its price on the review page. Claude then creates the Payment Links in Stripe's dashboard with him and switches the button from "Coming soon" to the link.
