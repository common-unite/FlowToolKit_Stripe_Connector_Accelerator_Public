# Stripe API Reference for Agents

> Curated from Stripe documentation via MCP (2026-02). This file exists so that
> the `stripe-api-expert` agent can read project-relevant Stripe REST API
> documentation without needing MCP access.

---

## Table of Contents
1. [PaymentIntents](#paymentintents)
2. [SetupIntents](#setupintents)
3. [Subscriptions](#subscriptions)
4. [Metadata](#metadata)
5. [Error Handling](#error-handling)
6. [Project-Specific Context](#project-specific-context)

---

## PaymentIntents

PaymentIntents track the lifecycle of a customer checkout flow. They handle
authentication (3DS), redirect-based methods, and more.

### Create a PaymentIntent (Server-Side)

```
POST /v1/payment_intents
```

Key parameters:
| Parameter | Type | Description |
|-----------|------|-------------|
| `amount` | integer | Amount in **minor units** (cents for USD, yen for JPY) |
| `currency` | string | Three-letter ISO currency code |
| `customer` | string | Customer ID to associate payment with |
| `payment_method` | string | Attach a specific PaymentMethod |
| `payment_method_types` | array | Explicit list, OR omit to use automatic payment methods |
| `automatic_payment_methods.enabled` | boolean | Let Stripe choose eligible methods from Dashboard settings |
| `metadata` | hash | Up to 50 key-value pairs (key max 40 chars, value max 500 chars) |
| `description` | string | Statement descriptor supplement |
| `receipt_email` | string | Email for Stripe receipt |
| `setup_future_usage` | string | `'off_session'` to save payment method for later |
| `confirm` | boolean | Confirm immediately on creation |
| `return_url` | string | Required if confirming server-side with redirect-based methods |
| `capture_method` | string | `'automatic'` (default) or `'manual'` for auth-then-capture |

### PaymentIntent Lifecycle

```
requires_payment_method → requires_confirmation → requires_action → processing → succeeded
                                                                                → requires_capture (manual)
                                                                                → canceled
```

### Deferred Intent Pattern (No Server-Side Intent Creation)

The Payment Element can render **before** creating a PaymentIntent. Pass `mode`,
`amount`, and `currency` to the Elements constructor instead of `clientSecret`:

```js
const elements = stripe.elements({
  mode: 'payment',
  amount: 1099,
  currency: 'usd'
});
```

Then create the PaymentIntent server-side only when the customer submits, and
confirm from the client using `stripe.confirmPayment()`.

### Confirm a PaymentIntent

```
POST /v1/payment_intents/{id}/confirm
```

Key parameters:
| Parameter | Type | Description |
|-----------|------|-------------|
| `payment_method` | string | PaymentMethod to use |
| `return_url` | string | Where to redirect after authentication |
| `payment_method_data` | hash | Create PaymentMethod inline |
| `mandate_data` | hash | Mandate information for certain payment methods |

### Capture a PaymentIntent (Manual Capture)

```
POST /v1/payment_intents/{id}/capture
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `amount_to_capture` | integer | Amount to capture (can be less than authorized) |

---

## SetupIntents

SetupIntents collect payment method details for **future payments** without
charging immediately.

### Create a SetupIntent

```
POST /v1/setup_intents
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `customer` | string | Customer to attach the PaymentMethod to |
| `payment_method_types` | array | Allowed payment method types |
| `automatic_payment_methods.enabled` | boolean | Auto-detect eligible methods |
| `usage` | string | `'off_session'` (default) or `'on_session'` |
| `metadata` | hash | Custom key-value pairs |

### SetupIntent Lifecycle

```
requires_payment_method → requires_confirmation → requires_action → processing → succeeded
```

After success, the PaymentMethod is attached to the Customer and can be used
for future PaymentIntents with `off_session: true`.

---

## Subscriptions

Subscriptions represent recurring billing relationships.

### Create a Subscription

```
POST /v1/subscriptions
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `customer` | string | **Required** — the Customer ID |
| `items` | array | Array of `{ price: 'price_xxx', quantity: 1 }` |
| `default_payment_method` | string | PaymentMethod to charge |
| `payment_behavior` | string | `'default_incomplete'` (recommended), `'allow_incomplete'`, `'error_if_incomplete'` |
| `metadata` | hash | Custom key-value pairs |
| `trial_period_days` | integer | Days of free trial |
| `cancel_at_period_end` | boolean | Schedule cancellation at period end |
| `proration_behavior` | string | `'create_prorations'`, `'none'`, `'always_invoice'` |
| `collection_method` | string | `'charge_automatically'` or `'send_invoice'` |

### Subscription Statuses

| Status | Description |
|--------|-------------|
| `trialing` | In trial period |
| `active` | Current period paid, service should be provided |
| `incomplete` | First payment attempt failed |
| `incomplete_expired` | First invoice not paid within 23 hours |
| `past_due` | Latest invoice not paid, retrying |
| `unpaid` | All retry attempts exhausted |
| `canceled` | Canceled (terminal) |
| `paused` | Payment collection paused |

### Update a Subscription (Proration)

```
POST /v1/subscriptions/{id}
```

When changing prices or quantities, use `proration_behavior`:
- `create_prorations` — Generate proration invoice items (default)
- `none` — No proration adjustment
- `always_invoice` — Generate and immediately invoice prorations

**What triggers prorations:**
- Changing price on a subscription item
- Changing quantity
- Adding/removing subscription items

**What does NOT trigger prorations:**
- Changing `metadata`, `default_payment_method`, `collection_method`
- Changing `cancel_at_period_end`, `pause_collection`
- Adding discounts (applies to future invoices only)

### Cancel a Subscription

```
DELETE /v1/subscriptions/{id}
```

Options:
- **Immediate cancellation**: Default behavior
- **Cancel at period end**: `POST /v1/subscriptions/{id}` with `cancel_at_period_end: true`
- **With proration**: Pass `prorate: true` for partial period refund
- **Final invoice**: Pass `invoice_now: true` to generate final invoice immediately

### Subscription Items

```
POST /v1/subscription_items/{id}
```

Each subscription can have multiple items (multiple prices). Use subscription
items to manage individual line items within a subscription.

---

## Metadata

Metadata allows storing up to **50 key-value pairs** on most Stripe objects.

### Constraints
- Max 50 keys per object
- Key: max 40 characters
- Value: max 500 characters

### Supported Objects
PaymentIntents, SetupIntents, Customers, Subscriptions, Products, Prices,
Invoices, Charges, PaymentMethods, Checkout Sessions, and more.

### Setting Metadata

```
POST /v1/payment_intents
  metadata[order_id]: "12345"
  metadata[salesforce_record_id]: "a0B5f00000xyz"
```

### Indirect Metadata (via Checkout Sessions)

| Source Object | Target via | Description |
|--------------|------------|-------------|
| Checkout Session | `payment_intent_data.metadata` | Flows to underlying PaymentIntent |
| Checkout Session | `subscription_data.metadata` | Flows to underlying Subscription |
| Payment Link | `payment_intent_data.metadata` | Flows to each PaymentIntent created |
| Price | `product_data.metadata` | Flows to associated Product |

### Searching Metadata

Supported objects for search: customers, payment_intents, charges, invoices,
prices, products, subscriptions.

```
# Search by metadata key/value
GET /v1/customers/search?query=metadata['salesforce_id']:'001xxx'

# Search by metadata key existence
GET /v1/payment_intents/search?query=metadata['order_id']:null
```

### Webhooks and Metadata

When Stripe sends events to webhook endpoints, the event payload includes the
object with all its metadata. This enables downstream processing:

```json
{
  "type": "payment_intent.succeeded",
  "data": {
    "object": {
      "id": "pi_xxx",
      "metadata": {
        "salesforce_record_id": "a0B5f00000xyz",
        "flow_interview_id": "300xxx"
      }
    }
  }
}
```

---

## Error Handling

### Error Response Structure

```json
{
  "error": {
    "type": "card_error",
    "code": "card_declined",
    "decline_code": "insufficient_funds",
    "message": "Your card has insufficient funds.",
    "param": "payment_method",
    "doc_url": "https://docs.stripe.com/error-codes/card-declined"
  }
}
```

### Error Types

| Type | Description | Action |
|------|-------------|--------|
| `card_error` | Card declined or failed validation | Show message to customer |
| `invalid_request_error` | Invalid parameters in API call | Fix the request (developer error) |
| `api_error` | Something went wrong on Stripe's end | Retry with exponential backoff |
| `idempotency_error` | Idempotency key reuse conflict | Use a new idempotency key |
| `authentication_error` | Invalid API key | Check API key configuration |
| `rate_limit_error` | Too many requests | Back off and retry |

### Common Decline Codes

| Code | Description | Customer Message |
|------|-------------|-----------------|
| `insufficient_funds` | Not enough funds | "Your card has insufficient funds." |
| `lost_card` | Card reported lost | "Your card has been declined." |
| `stolen_card` | Card reported stolen | "Your card has been declined." |
| `expired_card` | Card expired | "Your card has expired." |
| `incorrect_cvc` | CVC check failed | "Your card's security code is incorrect." |
| `incorrect_zip` | Postal code check failed | "Your card's zip code failed validation." |
| `card_velocity_exceeded` | Too many transactions | "Your card has been declined." |
| `generic_decline` | General decline | "Your card has been declined." |
| `fraudulent` | Suspected fraud | "Your card has been declined." |
| `do_not_honor` | Issuer won't authorize | "Your card has been declined." |

### Idempotency

Use idempotency keys for safe retries on create/confirm operations:

```
POST /v1/payment_intents
Idempotency-Key: unique-request-id-123
```

- Keys expire after 24 hours
- Same key + same parameters = cached response returned
- Same key + different parameters = `idempotency_error`

---

## Project-Specific Context

### Architecture Overview

This project is a **Salesforce managed package** (namespace: `FlowToolKit`)
that integrates Stripe payments into Salesforce Flows and Experience Cloud.

**Server-side pattern (Apex):**
- All Stripe API calls are made from Apex classes via HTTP callouts
- `StripePaymentForm_Controller` is the main VF controller
- Invocable Actions (GetAccount, GetMetadata, PutMetadata, SubscriptionItem)
  expose Stripe operations to Flow builders
- PaymentIntents are created server-side, `client_secret` passed to the frontend

**Client-side pattern:**
- VF page loads Stripe.js and mounts Elements
- `stripe.confirmPayment()` / `stripe.confirmSetup()` called from within the
  VF iframe
- Results communicated back to LWC via `window.postMessage`

### Key Integration Points

1. **PaymentIntent creation**: Apex creates PI with amount/currency/metadata,
   passes `client_secret` to frontend
2. **Metadata**: Used extensively to link Stripe objects to Salesforce records
   (e.g., `salesforce_record_id`, `flow_interview_id`)
3. **Subscriptions**: Managed via Invocable Actions so Flow builders can
   create/update subscription items declaratively
4. **Error handling**: Errors from `confirmPayment()` are caught in the static
   resource JS and posted back to the LWC via `postMessage`

### Key Files
- `force-app/main/default/classes/StripePaymentForm_Controller.cls` — Main Apex controller
- `force-app/main/default/classes/Stripe_*.cls` — Invocable Action classes
- `force-app/main/default/pages/StripePaymentForm.page` — VF page
- `force-app/main/default/staticresources/StripePaymentElement.js` — Client-side Stripe logic

### Known Issues

**Overridable Flows + Managed Package Upgrades:**
Overridden flows hold stale references to Invocable Action metadata. When the
managed package upgrades and Apex classes change, overridden flows crash at
runtime with "The 'X' element in your flow has validation errors." Fix: users
must delete and recreate overridden flows after upgrade.

**VF Iframe Blocked in Older Orgs:**
Older orgs (~10+ years old) need Trusted Domains for Inline Frames configured:
`*.my.salesforce.com` and `*.lightning.force.com` as `Visualforce Pages` type.
