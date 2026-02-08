# Stripe Connector Accelerator — Overview

The Stripe Connector Accelerator extends the Stripe Connector for Salesforce and the Flow Tool Kit to let you collect payments, save payment methods, and create subscriptions directly inside Salesforce Flows and Experience Cloud pages — no code required.

**Prerequisites:** The following packages must be installed in order before this package.

### Installation

**Step 1: Flow Tool Kit (Base Package)**
- [Get It Now](https://common-unite.my.site.com/s/latest-release) from the Common Unite site.

**Step 2: Stripe Connector for Salesforce (2 packages)**

Stripe Connector — Package 1:
- [Production & Developer Edition Orgs](https://login.salesforce.com/packaging/installPackage.apexp?p0=04tRN000004ZhkXYAS) | [Sandbox & Scratch Orgs](https://test.salesforce.com/packaging/installPackage.apexp?p0=04tRN000004ZhkXYAS)

Stripe Connector — Package 2:
- [Production & Developer Edition Orgs](https://login.salesforce.com/packaging/installPackage.apexp?p0=04t4x0000003MzaAAE) | [Sandbox & Scratch Orgs](https://test.salesforce.com/packaging/installPackage.apexp?p0=04t4x0000003MzaAAE)

**Step 3: Stripe Connector Accelerator**
- Install the latest release from the [Releases page](https://github.com/common-unite/FlowToolKit_Stripe_Connector_Accelerator_Public/releases).

**Step 4: Configure the Stripe Connector**
- After installing all packages, follow Stripe's [Installation Guide](https://docs.stripe.com/use-stripe-apps/stripe-app-for-salesforce/installation-guide) to connect your Stripe account to Salesforce and complete the setup.

### Pricing

This package is **100% free** to install and use in **sandboxes and scratch orgs** — no activation required. Build, test, and evaluate the full package at no cost.

To use the package in a **production org**, a one-time setup fee is required. There is no recurring payment. Visit the [Stripe Accelerator activation page](https://common-unite.my.site.com/s/stripe-accelerator) to get started.

---

## What's in the Package

| Category | Count | Summary |
|----------|-------|---------|
| **Flow Screen Components** | 3 | Payment form, Setup card, Subscription form |
| **Experience Cloud Components** | 2 | Payment form with field mapping, Express checkout |
| **Flow Actions** | 5 | Account key resolver, subscription item builder, metadata helpers |
| **Pre-Built Screen Flows** | 6 | Payment, setup, subscription, checkout, and invoice flows (+ templates) |
| **Background Automation** | ~25 | Customer sync, product sync, invoice sync, and webhook event handlers |
| **Custom Objects** | 5 | Payment methods, settings, items, custom fields |
| **Custom Fields** | 40+ | On Account, Contact, Lead, User, Opportunity, Product, PricebookEntry, and more |

---

## The Three Flow Screen Components

The heart of this package is three screen components you can drop into any Flow:

| Component | What It Does | When to Use It |
|-----------|-------------|----------------|
| **Stripe Payment** | Displays a Stripe payment form that collects card details, Apple Pay, Google Pay, and Link. Processes the payment and returns the result to your Flow. | Collecting a one-time payment or authorizing a charge for later capture. |
| **Stripe Setup Card** | Displays the same payment form but saves the card for future use without charging it now. Requires a Stripe Customer ID. | Saving a customer's card on file for future invoices, subscriptions, or manual charges. |
| **Stripe Subscription** | Displays the payment form and creates a recurring subscription with the payment method. Requires a Stripe Customer ID and at least one subscription item. | Setting up recurring billing with configurable products, prices, and billing intervals. |

Each component has a **Custom Property Editor** — a point-and-click configuration panel that appears in the Flow Builder when you select the component. No need to manually type API names or values.

### What the Payment Form Supports

- Credit and debit cards (Visa, Mastercard, Amex, Discover, etc.)
- Apple Pay and Google Pay (Express Checkout)
- Stripe Link (email-based fast checkout)

- Address collection
- Pre-filled customer details (name, email, phone, address)
- Custom metadata (key-value pairs attached to the Stripe transaction)

---

## Workflow Groups

### 1. Collect a One-Time Payment

**Use case:** Charge a customer immediately, or authorize a payment for later capture.

![Stripe Collect Payment Component Debug Demo](images/Flow%20%7C%20Stripe%20Collect%20Payment%20Component%20Debug%20Demo.png)

**How to set it up:**
1. In Flow Builder, add a Screen element and drag the **Stripe Payment** component onto it.
2. In the property editor, set the **Amount** (in cents — e.g., 5000 for $50.00) and **Capture Method** (automatic or manual).
3. Optionally set customer details (name, email, phone, address) to pre-fill the form.
4. After the screen, use the output variables to store or display the results.

**What you get back:**
- Whether the payment succeeded
- The Payment Intent ID and Payment Method ID (store these on your records for reference)
- Card details: brand, last 4 digits, expiration, funding type

**Pre-built flow:** The **Stripe Payment (Collect Payment Form)** flow is ready to use out of the box — just pass in the amount, currency, and optional customer details.

**Important:** The amount is always in **cents**. $50.00 = `5000`. The minimum is $0.50 (50 cents).

---

### 2. Save a Payment Method (Setup Card)

**Use case:** Save a customer's card on file for future charges without collecting a payment now.

**How to set it up:**
1. You need a Stripe Customer ID first. Use the **Stripe Create/Update Customer** subflow (included) to create or look up the customer, or pass in an existing ID.
2. Add a Screen element and drag the **Stripe Setup Card** component onto it.
3. Set the **Customer ID** (required) and optionally pre-fill customer details.

**What you get back:**
- The Setup Intent ID and Payment Method ID
- Card details: brand, last 4 digits, expiration, funding type

**Pre-built flow:** The **Stripe Payment (Setup Payment Method)** flow handles everything end-to-end:
- Pass in a record ID (Account, Contact, Lead, User, or Opportunity)
- It automatically looks up or creates the Stripe Customer
- Displays the payment form
- Optionally emails the customer a link to Stripe's billing portal where they can manage their payment methods

---

### 3. Create a Subscription

**Use case:** Set up recurring billing with one or more products.

**How to set it up:**
1. You need a Stripe Customer ID (same as setup card — use the customer sync subflow or pass one in).
2. Use the **Stripe | Build Subscription Item** action (one or more times) to create your line items. Each item needs a Stripe Product ID, unit price, billing interval (day/week/month/year), and quantity.
3. Add a Screen element and drag the **Stripe Subscription** component onto it.
4. Set the **Customer ID** and **Items** collection.
5. Optionally configure: coupon, promotion code, billing cycle anchor, cancellation date, and payment behavior.

**What you get back:**
- The Subscription ID, Setup Intent ID, and Payment Method ID
- Card details
- The full subscription object (for advanced use)

**Pre-built flow:** The **Stripe Payment (New Subscription)** flow accepts subscription items and all billing parameters.

**Tip:** You can build multi-item subscriptions by calling the **Build Subscription Item** action multiple times, passing the growing items collection through each call.

---

### 4. Checkout Session (Opportunity-Based)

**Use case:** Generate a Stripe-hosted checkout page from an Opportunity's line items and send the customer a payment link.

**Pre-built flow:** The **Stripe Payment (Checkout Session Opportunity)** flow:
1. Reads the Opportunity and its line items
2. Resolves each line item's Stripe Product ID (synced via the product sync automation)
3. Creates a Stripe Checkout Session
4. Returns the hosted checkout URL — you can email it, display it, or redirect to it

After the customer completes checkout, the **Checkout Session Completed** webhook handler updates the Opportunity automatically.

---

### 5. Invoice Generation (Opportunity-Based)

**Use case:** Create and manage Stripe invoices tied to Opportunities.

![Generate Stripe Invoices and send to Customers from Opportunity records](images/Generate%20Stripe%20Invoices%20and%20send%20to%20Customers%20from%20Opportunity%20records.png)

**Pre-built flow:** The **Opportunity Generate Invoice** flow creates a Stripe invoice from the Opportunity's line items.

**Background automation handles the rest:**
- When the Opportunity stage progresses, the invoice is finalized automatically
- If line items change, the invoice is replaced
- Stripe webhook events update the Opportunity with: invoice status, PDF link, hosted URL, receipt details, and due dates

**Fields updated on Opportunity:** Invoice ID, status (draft/open/paid/void), PDF URL, hosted URL, effective date, due date, footer, receipt number, receipt URL.

---

### 6. Customer Synchronization

**Use case:** Keep Salesforce records in sync with Stripe Customers automatically.

**How it works:**
- The **Stripe Create/Update Customer** subflow is the central piece. It looks up a Stripe Customer by the stored ID, or creates a new one. It maps: name, email, phone, address, and description.
- A **record-triggered flow on Account** fires when email or key fields change, and publishes a platform event to sync the changes to Stripe asynchronously.
- **Webhook handlers** listen for customer changes in Stripe and update the Salesforce record.

**Supported entities:** Account, Contact, Lead, User, and Opportunity. Each has a `Stripe Customer Id` and `Stripe Default Payment Method` field installed by the package.

**Important:** The Account sync trigger fires on insert and update. It checks whether the email or other mapped fields actually changed before syncing, to avoid unnecessary API calls.

---

### 7. Product & Price Synchronization

**Use case:** Keep Salesforce Products and Pricebook Entries in sync with Stripe Products and Prices.

**How it works:**
- **Record-triggered flows on Product2** fire on insert and update, syncing the product to Stripe.
- The **Stripe Product (Create/Update Price)** utility flow syncs PricebookEntry pricing to Stripe Prices.
- Stripe Product IDs and Price IDs are stored on the Salesforce records for cross-reference.

**Fields used:**
- Product2: `Stripe Product Id`, `Stripe Product Image URL`, `Statement Descriptor`
- PricebookEntry: `Stripe Product Id`, `Stripe Price Id`, `Stripe Lookup Key`

---

### 8. Experience Cloud Components

**Use case:** Embed payment collection directly on Experience Cloud pages without building a Flow.

![Experience Cloud Stripe Payment Flow Component](images/Experience%20Cloud%20%7C%20Stripe%20Payment%20Flow%20Component.png)

#### Stripe Payment Form

Combines a dynamic record form (from the Flow Tool Kit) with the Stripe payment component. Admins configure it through a property editor in Experience Builder:

1. Select the form/object to display
2. Open the **Field Mapping** modal to map form fields to payment inputs:
   - Which Currency field holds the payment amount (or set a fixed amount)
   - Which fields map to customer name, email, phone, and address
   - Which fields should receive the payment results (Payment Intent ID, card details, etc.)
   - For subscriptions: which Lookup field points to the Stripe Product, and which field holds the quantity
3. Optionally configure: payment type routing (one-time vs. subscription based on a field value), capture method, and UI options

The component shows the form first, then a "Continue to Payment" button. After successful payment, results are written back to the form fields and the record is saved.

#### Express Payment

Displays product details (image, name, price) from a PricebookEntry with an inline Express Checkout button. Designed for quick one-click purchases on community pages.

Configure it in Experience Builder by setting:
- The PricebookEntry or Product record ID
- Amount and currency
- Button style (pay, buy, checkout, donate, book, order, subscribe, or plain)

**Note:** For Express Payment, the amount is in **dollars** (not cents like the Flow components). The component handles the conversion.

---

### 9. Flow Actions (Invocable Actions)

These actions appear in Flow Builder under the category **Stripe | (Accelerator)**.

| Action | What It Does | When to Use It |
|--------|-------------|----------------|
| **Get Stripe Account Keys** | Returns the Stripe Account record ID and publishable key. Automatically picks test mode in sandboxes and live mode in production. | At the start of any custom flow that needs Stripe credentials. The pre-built flows already call this for you. |
| **Build Subscription Item** | Creates a subscription line item with product, price, billing interval, and quantity. Call it once per item, passing the growing collection through. | Before the subscription screen component, to build the items list. |
| **Get Metadata** | Reads a value from a Stripe Metadata object by key. | When processing Stripe API responses that include metadata (e.g., extracting a Salesforce Record ID you attached to a payment). |
| **Put Metadata** | Adds or updates a key-value pair on a Stripe Metadata object. | Before creating a payment/subscription, to attach custom data like a Salesforce Record ID. |
| **Get JSON Metadata** | Parses metadata from a raw Stripe webhook event JSON payload. Also extracts the Stripe object ID. | In webhook event handler flows, to pull metadata and IDs from the event body. |

---

## Custom Objects Installed

| Object | What It Stores |
|--------|---------------|
| **Stripe Payment Method** | Saved payment method records (card brand, last 4, expiration, status) linked to Contacts. Used by the setup card flows. |
| **Stripe Payment Accelerator Settings** | Package configuration: test mode toggle, transaction fee settings, Apple Pay domain verification resource. Managed via Setup > Custom Settings. |
| **Stripe Item** | Line item records (product ID, description, quantity, price) for custom payment form configurations. |
| **Stripe Custom Field** | Custom field definitions (key, label, type, default value, validation rules) for payment form customization. |

---

## Background Automation Summary

The package includes flows that run automatically in the background. You don't need to configure these unless you want to customize them.

### Record-Triggered Flows

| Trigger | What It Does |
|---------|-------------|
| **Account insert/update** | When Account email or key fields change, syncs the customer data to Stripe. |
| **Product insert** | Syncs new Products to Stripe. |
| **Product update** | Syncs updated Products to Stripe. |
| **Opportunity update (finalize)** | Finalizes the Stripe invoice when the Opportunity stage progresses. |
| **Opportunity update (replace)** | Replaces the Stripe invoice if the Opportunity changes significantly. |
| **OpportunityLineItem insert/update** | Syncs line item changes to the corresponding Stripe invoice items. |

### Webhook Event Handlers

These flows respond to events sent from Stripe to Salesforce via the Stripe Connector's webhook integration:

| Event | What It Does |
|-------|-------------|
| **Setup Intent succeeded** | Updates the record when a saved payment method is confirmed. |
| **Customer created/updated** | Syncs customer changes from Stripe back to the Salesforce record. |
| **Price created/updated** | Syncs price changes from Stripe back to PricebookEntry. |
| **Checkout session completed** | Updates the Opportunity when the customer completes a hosted checkout. |
| **Invoice events** | Updates Opportunity fields with invoice status, PDF, URL, and payment details. |

---

## Overridable vs. Template Flows

![Over 20 Flow Templates to get you started](images/Over%2020%20Flow%20Templates%20to%20get%20you%20started.png)

The package ships two versions of each core Screen Flow:

- **Overridable** flows (e.g., "Stripe Payment (Collect Payment Form)") — Use these in production. You can modify them, and they'll still receive non-breaking updates from the package.
- **Template** flows (e.g., "Template Stripe Payment (Collect Payment Form)") — Read-only reference copies. Clone them to start your own flows from scratch.

---

## How It All Fits Together

```
  Your Flow                          Stripe
  ┌──────────────────┐              ┌──────────────┐
  │  Screen:         │              │              │
  │  Payment Form    │──── pays ───▶│  Charges     │
  │  Setup Card      │──── saves ──▶│  Cards       │
  │  Subscription    │──── starts ─▶│  Billing     │
  └──────────────────┘              └──────┬───────┘
         │                                 │
         ▼                                 │ webhooks
  ┌──────────────────┐                     │
  │  Output vars:    │◀────────────────────┘
  │  Intent IDs      │
  │  Card details    │
  │  Subscription ID │
  │  ↓               │
  │  Store on records│
  └──────────────────┘

  Background Sync (automatic):
  Account ←→ Stripe Customer
  Product ←→ Stripe Product
  PricebookEntry ←→ Stripe Price
  Opportunity ←→ Stripe Invoice
```

**Key points for admins:**
- The payment form runs inside a secure iframe for PCI compliance. You don't need to worry about credit card data touching your Salesforce org.
- The Stripe account (test vs. live) is resolved automatically based on whether you're in a sandbox or production.