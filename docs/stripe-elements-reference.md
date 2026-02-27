# Stripe Elements Reference for Agents

> Curated from Stripe documentation via MCP (2026-02). This file exists so that
> the `stripe-elements-expert` agent can read project-relevant Stripe.js
> documentation without needing MCP access.

---

## Table of Contents
1. [Payment Element](#payment-element)
2. [Express Checkout Element](#express-checkout-element)
3. [Link Authentication Element](#link-authentication-element)
4. [Address Element](#address-element)
5. [Appearance API](#appearance-api)
6. [Client-Side Confirmation](#client-side-confirmation)
7. [Project-Specific Context](#project-specific-context)

---

## Payment Element

The Payment Element renders a dynamic form that lets customers pick a payment
method. It automatically collects all necessary payment details.

### Setup (Vanilla JS — our pattern)

```js
// 1. Load Stripe.js from js.stripe.com (NEVER bundle or self-host)
const stripe = Stripe('pk_...');

// 2. Create Elements instance with mode, amount, currency
const elements = stripe.elements({
  mode: 'payment',          // or 'setup' for SetupIntents
  amount: 1099,             // in minor units (cents)
  currency: 'usd',
  appearance: { theme: 'stripe' }
});

// 3. Create and mount
const paymentElement = elements.create('payment', {
  layout: 'tabs'            // or 'accordion'
});
paymentElement.mount('#payment-element');
```

### Options Reference

| Option | Description |
|--------|-------------|
| `layout` | `'tabs'` (horizontal) or `'accordion'` (vertical). Can also be an object: `{ type: 'tabs', defaultCollapsed: false }` |
| `defaultValues` | Pre-fill customer info: `{ billingDetails: { name, email, phone, address } }` |
| `business` | Display business name: `{ name: 'My Company' }` |
| `paymentMethodOrder` | Array of payment method types to control display order |
| `fields` | Toggle field visibility: `{ billingDetails: { address: 'never' } }` |
| `readOnly` | Boolean — prevent payment detail changes |
| `terms` | Control mandate/legal text display: `{ card: 'auto' }` |
| `wallets` | Control wallet display: `{ applePay: 'auto', googlePay: 'auto' }` |

### Events

```js
paymentElement.on('ready', (event) => {
  // Element is fully loaded and interactive
  // USE THIS instead of setTimeout() for load detection
});

paymentElement.on('change', (event) => {
  // event.complete — true when all required fields filled
  // event.value.type — selected payment method type
});

paymentElement.on('loaderror', (event) => {
  // Handle load failures
});
```

### Auto-Shown Error Messages

Payment Element automatically shows localized error messages for these decline codes:
- `generic_decline`, `insufficient_funds`, `incorrect_zip`
- `incorrect_cvc`, `invalid_cvc`, `invalid_expiry_month`, `invalid_expiry_year`
- `expired_card`, `fraudulent`, `lost_card`, `stolen_card`, `card_velocity_exceeded`

For other errors, use `error.code` from the confirm response.

### Important Warning: Conflicting iFrames

> Avoid placing the Payment Element within another iframe because it conflicts
> with payment methods that require redirecting to another page for payment
> confirmation.

**This is directly relevant to our project** — we embed Elements inside a VF
page iframe. This means redirect-based payment methods (like bank transfers,
iDEAL, etc.) may not work inside our VF iframe. Card payments and wallet
payments work fine.

---

## Express Checkout Element

Shows one-click payment buttons for Apple Pay, Google Pay, Link, and PayPal.

### Setup

```js
const elements = stripe.elements({
  mode: 'payment',
  amount: 1099,
  currency: 'usd'
});

const expressCheckoutElement = elements.create('expressCheckout', {
  // Optional: collect payer info
  emailRequired: true,
  phoneNumberRequired: true,
  // Optional: button styling per method
  buttonTheme: {
    applePay: 'black',
    googlePay: 'black'
  },
  buttonType: {
    applePay: 'buy',
    googlePay: 'checkout'
  },
  // Optional: payment method control
  paymentMethods: {
    applePay: 'always',     // 'always' | 'never' | 'auto'
    googlePay: 'always',
    link: 'auto'
  },
  // Optional: layout
  layout: {
    maxColumns: 3,
    maxRows: 1,
    overflow: 'auto'        // 'auto' | 'never'
  }
});

expressCheckoutElement.mount('#express-checkout-element');
```

### Events

```js
// Ready — fires when buttons are available to display
expressCheckoutElement.on('ready', ({ availablePaymentMethods }) => {
  // availablePaymentMethods = { applePay: true, googlePay: false, link: true }
  // USE THIS to show/hide the express checkout section
});

// Click — fires when customer clicks a payment button
expressCheckoutElement.on('click', (event) => {
  // event.expressPaymentType = 'apple_pay' | 'google_pay' | 'link'
  // Can call event.resolve({ ... }) to update line items, shipping options
});

// Confirm — fires when customer authorizes payment
expressCheckoutElement.on('confirm', async (event) => {
  // event.billingDetails, event.shippingAddress, event.shippingRate
  const { error } = await stripe.confirmPayment({
    elements,
    clientSecret,
    confirmParams: {
      return_url: 'https://example.com/return'
    }
  });
  if (error) {
    // Handle error
  }
});

// Shipping address change
expressCheckoutElement.on('shippingaddresschange', async (event) => {
  // Must call event.resolve({}) or event.reject('reason')
});

// Cancel
expressCheckoutElement.on('cancel', () => {
  // Customer dismissed the payment interface
});
```

### Collecting Customer Details

```js
const expressCheckoutElement = elements.create('expressCheckout', {
  emailRequired: true,
  phoneNumberRequired: true,
  billingAddressRequired: true,     // defaults depend on other options
  shippingAddressRequired: true,
  shippingRates: [
    { id: 'free', amount: 0, displayName: 'Free shipping' },
    { id: 'express', amount: 500, displayName: 'Express (2-3 days)' }
  ],
  lineItems: [
    { name: 'Product', amount: 1099 }
  ]
});
```

---

## Link Authentication Element

Single email input field for email collection AND Link authentication.

```js
const linkAuthElement = elements.create('linkAuthentication', {
  defaultValues: {
    email: 'customer@example.com'   // Pre-fill to start auth flow immediately
  }
});
linkAuthElement.mount('#link-authentication-element');

// Retrieve email
linkAuthElement.on('change', (event) => {
  const email = event.value.email;
});
```

**Key details:**
- Place at the beginning of checkout, before Address Element and Payment Element
- Only show it once — if used on an early page, don't repeat on payment page
- When a Link customer authenticates, their saved payment methods auto-fill in
  the Payment Element
- Must register your domain at: Dashboard > Settings > Payment method domains
- All Elements must be created from the **same `Elements` instance** for
  autofill to work

---

## Address Element

Collects complete billing or shipping addresses with autocomplete.

```js
// Shipping mode — also offers "use as billing" checkbox
const addressElement = elements.create('address', {
  mode: 'shipping',
  allowedCountries: ['US', 'CA', 'GB'],
  fields: {
    phone: 'always'         // 'always' | 'never' | 'auto'
  },
  validation: {
    phone: { required: 'always' }
  },
  autocomplete: {
    mode: 'google_maps_api',
    apiKey: 'YOUR_GOOGLE_KEY'   // Not needed if using with Payment Element
  },
  defaultValues: {
    name: 'Jane Doe',
    address: {
      line1: '123 Main St',
      city: 'San Francisco',
      state: 'CA',
      postal_code: '94111',
      country: 'US'
    }
  }
});
addressElement.mount('#address-element');

// Listen for address changes
addressElement.on('change', (event) => {
  if (event.complete) {
    const address = event.value;
  }
});
```

**Autocomplete supported countries:** AU, BE, BR, CA, CH, DE, ES, FR, GB, IE,
IN, IT, JP, MX, MY, NL, NO, NZ, PH, PL, RU, SE, SG, TR, US, ZA

**Automatic behavior:**
- Shipping mode: address stored in `shipping` field on PaymentIntent
- Billing mode: address stored in `billing_details` on PaymentMethod
- Both auto-combine with Payment Element when created from same `Elements` instance

---

## Appearance API

Customize the look and feel of all Elements.

### Themes

Three built-in themes: `stripe` (default), `night`, `flat`

```js
const elements = stripe.elements({
  appearance: {
    theme: 'stripe'     // 'stripe' | 'night' | 'flat'
  }
});
```

### Inputs and Labels

```js
const elements = stripe.elements({
  appearance: {
    theme: 'stripe',
    inputs: 'spaced',       // 'spaced' (default) | 'condensed'
    labels: 'auto'          // 'auto' | 'above' | 'floating'
  }
});
```

- `spaced`: Each input has space surrounding it
- `condensed`: Related inputs grouped without space
- `auto`: Labels adjust based on input variant (spaced=above, condensed=floating)

### Variables (Global)

Variables broadly customize components across all Elements:

```js
const elements = stripe.elements({
  appearance: {
    theme: 'stripe',
    variables: {
      // Colors
      colorPrimary: '#0570de',
      colorBackground: '#ffffff',
      colorText: '#30313d',
      colorDanger: '#df1b41',
      colorTextSecondary: '#6d6e78',
      colorTextPlaceholder: '#9e9e9e',

      // Typography
      fontFamily: 'Ideal Sans, system-ui, sans-serif',
      fontSizeBase: '16px',
      fontWeightNormal: '400',

      // Spacing & Layout
      spacingUnit: '4px',
      spacingGridRow: '16px',
      spacingGridColumn: '16px',
      borderRadius: '4px',

      // Focus ring
      focusBoxShadow: '0 0 0 3px rgba(5, 112, 222, 0.25)',
      focusOutline: 'none'
    }
  }
});
```

### Rules (Fine-Grained)

Target specific components and states:

```js
const elements = stripe.elements({
  appearance: {
    rules: {
      '.Tab': {
        border: '1px solid #E0E6EB',
        boxShadow: '0px 1px 1px rgba(0, 0, 0, 0.03)',
      },
      '.Tab:hover': {
        color: 'var(--colorText)',
      },
      '.Tab--selected': {
        borderColor: '#E0E6EB',
        boxShadow: '0px 1px 1px rgba(0, 0, 0, 0.03), 0px 3px 6px rgba(18, 42, 66, 0.02)',
      },
      '.Input': {
        padding: '12px',
      },
      '.Input:focus': {
        boxShadow: '0 0 0 3px rgba(5, 112, 222, 0.25)',
      },
      '.Label': {
        fontWeight: '500',
      },
      '.Error': {
        color: 'var(--colorDanger)',
      }
    }
  }
});
```

**Common selectors:** `.Tab`, `.Tab--selected`, `.Tab:hover`, `.Input`,
`.Input:focus`, `.Input--invalid`, `.Label`, `.Error`, `.Block`,
`.CheckboxInput`, `.CheckboxLabel`, `.CodeInput`, `.RedirectText`

---

## Client-Side Confirmation

### stripe.confirmPayment (PaymentIntents)

```js
const { error } = await stripe.confirmPayment({
  elements,
  clientSecret: 'pi_xxx_secret_xxx',
  confirmParams: {
    return_url: 'https://example.com/return',
    payment_method_data: {
      billing_details: {
        name: 'Jane Doe',
        email: 'jane@example.com'
      }
    }
  },
  redirect: 'if_required'  // Only redirect for methods that need it (e.g., bank redirects)
});

if (error) {
  // error.type = 'card_error' | 'validation_error' | ...
  // error.message = human-readable message
  // error.code = specific error code
}
```

### stripe.confirmSetup (SetupIntents)

```js
const { error } = await stripe.confirmSetup({
  elements,
  clientSecret: 'seti_xxx_secret_xxx',
  confirmParams: {
    return_url: 'https://example.com/return'
  },
  redirect: 'if_required'
});
```

### Error Types from Confirmation

| `error.type` | Description |
|---------------|-------------|
| `card_error` | Card declined or failed validation |
| `validation_error` | Client-side validation failed (incomplete form) |
| `invalid_request_error` | Invalid parameters sent to Stripe |
| `api_error` | Something went wrong on Stripe's end |

---

## Project-Specific Context

### Architecture
This project embeds Stripe Elements inside a **Visualforce page iframe** within
a Lightning Web Component. This is an unusual pattern with specific implications:

1. **Stripe.js loads inside the VF iframe** — not in the LWC context
2. **Communication is via `window.postMessage`** between the LWC and the iframe
3. **The static resource `StripePaymentElement.js`** runs inside the iframe and
   manages all Elements lifecycle (create, mount, events, confirmation)
4. **`StripePaymentElementsHTML.component`** provides the HTML mounting points
5. **All Stripe API calls (PaymentIntents, etc.) happen server-side via Apex**
   using `Visualforce.remoting.Manager.invokeAction`

### Key Files
- `force-app/main/default/pages/StripePaymentForm.page` — VF page (iframe content)
- `force-app/main/default/staticresources/StripePaymentElement.js` — Stripe Elements logic
- `force-app/main/default/components/StripePaymentElementsHTML.component` — HTML template
- `force-app/main/default/lwc/flowStripePayment/` — LWC wrapper

### Load Optimization Pattern
- Iframe loads in parallel with Apex calls (not sequential)
- Single `postMessage` sends all config at once
- Uses `paymentElement.on('ready')` / `expressCheckoutElement.on('ready')` instead of `setTimeout`
- HTML sections hidden with `slds-hide`, toggled by JS `showSections()`

### Iframe Limitation
Because Elements are inside an iframe-within-an-iframe (VF page inside LWC
iframe), **redirect-based payment methods** (iDEAL, Bancontact, etc.) may not
work. The `confirmPayment` with `redirect: 'if_required'` approach is essential.
