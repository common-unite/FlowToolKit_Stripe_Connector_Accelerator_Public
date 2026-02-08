# Stripe Connector Accelerator — Implementation Guide

Detailed reference for admins implementing the Stripe Connector Accelerator. Covers component inputs and outputs, Flow action parameters, custom fields and objects, configuration settings, and important considerations.

---

## Table of Contents

1. [Flow Screen Components — Inputs & Outputs](#1-flow-screen-components--inputs--outputs)
2. [Experience Cloud Components](#2-experience-cloud-components)
3. [Flow Actions (Invocable Actions)](#3-flow-actions-invocable-actions)
4. [Custom Objects & Settings](#4-custom-objects--settings)
5. [Custom Fields on Standard Objects](#5-custom-fields-on-standard-objects)
6. [Platform Events](#6-platform-events)
7. [Pre-Built Flows Reference](#7-pre-built-flows-reference)
8. [Important Considerations](#8-important-considerations)

---

## 1. Flow Screen Components — Inputs & Outputs

### 1.1 Stripe Payment

Collects a one-time payment or authorized charge. This is the primary payment component.

#### Inputs (what you configure in the property editor)

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| Amount | Number | Yes | Payment amount in **cents**. Example: 5000 = $50.00. Minimum: 50 ($0.50). |
| Capture Method | Text | Yes | How funds are captured: `automatic` (charge immediately), `manual` (authorize now, capture later), or `async`. |
| Currency | Text | No | 3-letter currency code (e.g., `usd`, `eur`, `gbp`). Defaults to `usd`. |
| Description | Text | No | Description that appears on the payment in Stripe. |
| Customer ID | Text | No | Stripe Customer ID (starts with `cus_`). Optional for payments, but useful for tracking. |
| Metadata | Stripe Metadata | No | Key-value pairs attached to the payment. Use the **Put Metadata** action to build this. In the property editor, select a Flow variable of type `Stripe Metadata`. |
| Name | Text | No | Customer's name. Pre-fills the payment form. |
| Email | Text | No | Customer's email. Used for receipts and pre-fills the form. |
| Phone | Text | No | Customer's phone number. Pre-fills the form. |
| Address Line 1 | Text | No | Billing address line 1. |
| Address Line 2 | Text | No | Billing address line 2. |
| Address City | Text | No | Billing city. |
| Address State | Text | No | Billing state/province. |
| Address Country | Text | No | Billing country code (e.g., `US`, `GB`). |
| Address Postal Code | Text | No | Billing postal/ZIP code. |
| Enable Link | Boolean | No | Show Stripe Link — lets returning customers pay with just their email. |
| Enable Address | Boolean | No | Show an address collection form built into the payment element. |
| Enable Express Checkout | Boolean | No | Show Apple Pay / Google Pay buttons instead of the standard card form. |
| Express Checkout Button Type | Text | No | Label on the express checkout button: `pay`, `buy`, `checkout`, `donate`, `book`, `order`, `subscribe`, or `plain`. |
| Hide Header | Boolean | No | Hides the "Payment Details" header above the form. |
| Publishable Key | Text | No | Override the auto-detected Stripe publishable key. Usually not needed. |
| Stripe Account Id | Text | No | Override the auto-detected Stripe Account record. Usually not needed. |

#### Outputs (what you get back after the user pays)

| Output | Type | Description |
|--------|------|-------------|
| Success | Boolean | `true` if the payment was confirmed successfully. |
| Payment Intent Id | Text | The Stripe PaymentIntent ID (starts with `pi_`). Store this on your records. |
| Payment Method Id | Text | The Stripe PaymentMethod ID (starts with `pm_`). |
| Payment Method Type | Text | The type of payment method used (e.g., `card`, `us_bank_account`). |
| Card Brand | Text | Card brand: `visa`, `mastercard`, `amex`, `discover`, etc. |
| Card Last 4 | Text | Last 4 digits of the card number. |
| Card Expiration Month | Number | Card expiration month (1-12). |
| Card Expiration Year | Number | Card expiration year (e.g., 2027). |
| Card Country | Text | Country where the card was issued. |
| Card Funding | Text | Card funding type: `credit`, `debit`, or `prepaid`. |

#### Behavior

- After a successful payment, the Flow **automatically advances** to the next screen. You don't need to add navigation logic.
- If the user is on the last screen of the Flow, it finishes the Flow instead.
- The property editor validates that Amount and Capture Method are set before the Flow can be saved.

---

### 1.2 Stripe Setup Card

Saves a customer's payment method for future use without charging them.

#### Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| Customer ID | Text | **Yes** | Stripe Customer ID. The saved payment method is attached to this customer. |
| Currency | Text | No | 3-letter currency code. |
| Description | Text | No | Description for the setup. |
| Metadata | Stripe Metadata | No | Key-value pairs attached to the setup intent. |
| Name | Text | No | Customer's name (pre-fills form). |
| Phone | Text | No | Customer's phone (pre-fills form). |
| Enable Address | Boolean | No | Show address collection. |
| Hide Header | Boolean | No | Hide the form header. |
| Address fields | Text | No | Pre-fill billing address (Line 1, Line 2, City, State, Country, Postal Code). |
| Publishable Key | Text | No | Override auto-detected key. |
| Stripe Account Id | Text | No | Override auto-detected account. |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| Success | Boolean | `true` if the card was saved successfully. |
| Setup Intent Id | Text | The Stripe SetupIntent ID (starts with `seti_`). |
| Payment Method Id | Text | The Stripe PaymentMethod ID for the saved card. |
| Card Brand | Text | Card brand. |
| Card Last 4 | Text | Last 4 digits. |
| Card Expiration Month | Number | Expiration month. |
| Card Expiration Year | Number | Expiration year. |
| Card Country | Text | Card country. |
| Card Funding | Text | Funding type. |

#### Behavior

- **Customer ID is required.** The property editor enforces this. Use the **Stripe Create/Update Customer** subflow to get one if you don't have it.
- After success, the Flow auto-advances just like the payment component.

---

### 1.3 Stripe Subscription

Creates a recurring subscription and collects the initial payment method.

#### Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| Customer ID | Text | **Yes** | Stripe Customer ID. |
| Items | Collection (Subscription Items) | **Yes** | One or more subscription line items. Build these using the **Build Subscription Item** action. In the property editor, select a Flow collection variable. |
| Currency | Text | No | 3-letter currency code. Defaults to `usd`. |
| Description | Text | No | Subscription description. |
| Metadata | Stripe Metadata | No | Key-value pairs. |
| Payment Behavior | Text | No | What happens if the initial payment fails: `default_incomplete`, `allow_incomplete`, `error_if_incomplete`, or `pending_if_incomplete`. |
| Cancel at Period End | Boolean | No | If checked, the subscription will cancel at the end of the current billing period instead of immediately. |
| Coupon | Text | No | Stripe Coupon ID for a discount. |
| Promotion Code | Text | No | Stripe Promotion Code ID. |
| Cancel At | DateTime | No | Specific date/time to automatically cancel the subscription. |
| Billing Cycle Anchor | DateTime | No | Date/time to anchor billing cycles (e.g., always bill on the 1st of the month). |
| Backdate Start Date | DateTime | No | Start the subscription as of a past date. |
| Name, Email, Phone | Text | No | Customer details (pre-fills form). |
| Enable Address, Hide Header | Boolean | No | UI options. |
| Address fields | Text | No | Pre-fill billing address. |
| Publishable Key, Stripe Account Id | Text | No | Override auto-detected values. |

#### Outputs

| Output | Type | Description |
|--------|------|-------------|
| Success | Boolean | `true` if the subscription was created. |
| Subscription Id | Text | The Stripe Subscription ID (starts with `sub_`). |
| Setup Intent Id | Text | The SetupIntent used to collect the payment method. |
| Payment Method Id | Text | The payment method attached to the subscription. |
| Card Brand, Last 4, Expiration, Country, Funding | Various | Card details (same as other components). |

#### Behavior

- **Both Customer ID and Items are required.** The property editor enforces this.
- DateTime inputs (Cancel At, Billing Cycle Anchor, Backdate Start Date) are standard Salesforce DateTime variables. The component converts them to the format Stripe expects automatically.
- After success, the Flow auto-advances.

---

## 2. Experience Cloud Components

### 2.1 Stripe Payment Form

Available on Experience Cloud pages. Combines a record form with payment collection.

**Configuration** is done through the property editor in Experience Builder, which includes a **Field Mapping** modal.

#### Field Mapping Options

The modal organizes mappings into sections:

**Payment Details:**
- **Amount** — Map a Currency field from your object, or set a fixed amount
- **Description** — Map a Text field
- **Payment Type** — Map a field whose value determines one-time payment vs. subscription (e.g., a picklist with "Payment" and "Subscription" values)

**Subscription Schedule** (only used when payment type routes to subscription):
- **Subscription Product** — Map a Lookup field to Product2 (the Stripe Product ID is pulled from the Product's `Stripe Product Id` field)
- **Subscription Quantity** — Map a Number field

**Customer Details:**
- **Name, Email, Phone** — Map the corresponding fields from your object

**Billing Address:**
- **Address Line 1, Line 2, City, State, Country, Postal Code** — Map address fields

**Payment Outputs** (where to store results after payment):
- **Payment Intent ID, Payment Method ID** — Map Text fields
- **Card Brand, Last 4, Expiration Month/Year, Funding, Country** — Map Text/Number fields

#### Other Settings

- **Currency** — ISO currency code
- **Capture Method** — automatic or manual
- **Enable Link** — Stripe Link fast checkout
- **Enable Address** — Address collection in the payment form
- **Hide Header** — Hide the payment form header

#### Behavior

- The form displays first. The payment component appears after the user clicks "Continue to Payment."
- If the **Payment Type** field routes to "subscription", the component creates a subscription instead of a one-time payment.
- After payment, the results are written back to the mapped output fields and the record is saved automatically.

---

### 2.2 Express Payment

Available on Experience Cloud pages. Shows product details with a one-click checkout button.

#### Configuration (in Experience Builder)

| Setting | Description |
|---------|-------------|
| Record Id | The PricebookEntry or Product2 record ID. Product image, name, and description are pulled from the record. |
| Amount | Payment amount in **dollars** (not cents). Example: 50 = $50.00. |
| Currency | 3-letter currency code. |
| Description | Payment description. |
| Label | Display label for the product name. |
| Button Type | Express checkout button style: `pay`, `buy`, `checkout`, `donate`, `book`, `order`, `subscribe`, or `plain`. |
| Padding | Top, bottom, left, right padding for the container. |

**Important:** Unlike the Flow components, the Express Payment amount is in **dollars**. The component converts to cents automatically.

---

## 3. Flow Actions (Invocable Actions)

These appear in Flow Builder under **Stripe | (Accelerator)** when you add an Action element.

### 3.1 Get Stripe Account Keys

Returns the correct Stripe Account credentials based on your org type.

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| Test Mode | Boolean | No | Force test mode. If not set, the action auto-detects: sandboxes use test mode, production uses live mode. |

| Output | Type | Description |
|--------|------|-------------|
| Stripe Account Id | Record ID | The Salesforce record ID for the Stripe Account. Pass this to payment components if you need to override auto-detection. |
| Publishable Key | Text | The Stripe publishable API key. Pass this to payment components if needed. |

**When you need it:** The pre-built flows already call this action. You only need it in custom flows where you want explicit control over which Stripe account to use, or when you need the publishable key for other purposes.

---

### 3.2 Build Subscription Item

Creates one subscription line item. Call this action multiple times to build a multi-item subscription, passing the `Items` collection from the previous call into the next one.

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| Product | Text | Yes | Stripe Product ID (e.g., `prod_abc123`). |
| Unit Amount Decimal | Number | Yes | Unit price in **cents** (e.g., 999 = $9.99). Minimum: 50 ($0.50). |
| Currency | Text | Yes | 3-letter currency code. Defaults to `usd`. |
| Interval | Text | Yes | Billing frequency: `day`, `week`, `month`, or `year`. Must be one of these exact values. |
| Interval Count | Number | Yes | Number of intervals between billings. Example: `3` with interval `month` = bill every 3 months. Minimum: 1. |
| Quantity | Number | Yes | How many of this item. Minimum: 1. |
| Tax Rates | Text Collection | No | Stripe Tax Rate IDs to apply to this item. |
| Metadata | Stripe Metadata | No | Key-value pairs for this specific item. |
| Items | Subscription Item Collection | No | Existing items from a previous call. Pass this to build up a multi-item list. Leave empty for the first item. |

| Output | Type | Description |
|--------|------|-------------|
| Items | Subscription Item Collection | The updated collection with the new item added. Pass this to the next Build Subscription Item call, or to the Stripe Subscription screen component. |

**Example — Building a 2-item subscription:**
1. First action call: Product = `prod_abc`, Amount = 2999, Interval = `month`, Quantity = 1 → outputs `Items` (1 item)
2. Second action call: Product = `prod_xyz`, Amount = 999, Interval = `month`, Quantity = 2, Items = `{!Items}` from step 1 → outputs `Items` (2 items)
3. Pass the final `Items` collection to the Stripe Subscription screen component.

---

### 3.3 Get Metadata

Reads a single value from a Stripe Metadata object.

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| Metadata | Stripe Metadata | Yes | The metadata object from a Stripe API response or a previous Put Metadata call. |
| Key | Text | Yes | The key to look up. |

| Output | Type | Description |
|--------|------|-------------|
| Value | Text | The value for that key, or blank if not found. |

---

### 3.4 Put Metadata

Adds or updates a key-value pair in a Stripe Metadata object.

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| Metadata | Stripe Metadata | No | Existing metadata to update. If blank, a new metadata object is created. |
| Key | Text | No | The key to add or update. |
| Value | Text | No | The value to set. |

| Output | Type | Description |
|--------|------|-------------|
| Metadata | Stripe Metadata | The updated metadata object. Pass this to the payment component's Metadata input or to another Put Metadata call. |

**Example — Attaching a Salesforce Record ID to a payment:**
1. Put Metadata: Key = `salesforce_record_id`, Value = `{!recordId}` → outputs Metadata
2. Stripe Payment component: Metadata = `{!Metadata}` from step 1

Now when you view the payment in Stripe, you'll see the Salesforce Record ID in the metadata.

---

### 3.5 Get JSON Metadata

Parses metadata from a raw Stripe webhook event JSON string. Used in webhook event handler flows.

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| JSON String | Text | Yes | The raw JSON from the Stripe Event's Request Body field. |
| Key | Text | Yes | The metadata key to extract. |

| Output | Type | Description |
|--------|------|-------------|
| Value | Text | The metadata value. |
| Id | Text | The Stripe object ID from the event (e.g., the PaymentIntent ID or Customer ID). |

**When you need it:** In flows that handle Stripe webhook events (platform event-triggered flows), the event body is a raw JSON string. This action lets you pull out metadata values and the Stripe object ID without parsing JSON manually.

---

## 4. Custom Objects & Settings

### Custom Objects

| Object | Purpose | Where to Find It |
|--------|---------|-------------------|
| **Stripe Payment Method** (`Stripe_Payment_Method__c`) | Stores saved payment method records linked to Contacts. Fields include card brand, last 4, expiration, funding type, status, and whether it's the default. | App Launcher > Stripe Payment Methods, or related list on Contact |
| **Stripe Item** (`Stripe_Item__c`) | Line item records for payment forms. Fields include description, quantity, Stripe Product ID, and unit amount. | App Launcher > Stripe Items |
| **Stripe Custom Field** (`Stripe_Custom_Field__c`) | Defines custom input fields on payment forms. Fields include key, label, type, default value, and validation (optional, min/max length). | App Launcher > Stripe Custom Fields |

### Custom Settings (Hierarchy)

Access these via **Setup > Custom Settings**.

#### Stripe Payment Accelerator Settings

| Field | What It Controls |
|-------|-----------------|
| **Test Mode** | When checked, forces test mode even in production. Useful for testing before going live. |
| **Transaction Fee** | Flat fee added to transactions (if your org charges processing fees). |
| **Processing Fee Multiplier** | Percentage-based processing fee multiplier. |
| **Apple Developer Domain Resource** | Name of the static resource containing the Apple Pay domain verification file. Required only if you're enabling Apple Pay on a custom domain. |

#### Stripe Payment Settings

This setting stores encryption keys used internally for securing payment data in transit. **No admin action is needed** — keys are generated and rotated automatically every hour.

---

## 5. Custom Fields on Standard Objects

The package installs custom fields on several standard objects to store Stripe IDs and sync data. All field names are prefixed with the package namespace.

### Account

| Field | What It Stores |
|-------|---------------|
| Stripe Customer Id | The Stripe Customer ID linked to this Account. Populated by the customer sync flows. |
| Stripe Customer Email | Email address used for Stripe sync. The Account trigger watches this field for changes. |
| Stripe Default Payment Method | The default Stripe PaymentMethod ID on file. |
| Stripe Event Last Triggered | Timestamp of the last sync event. Prevents sync loops. |
| Stripe Tax Exempt Status | Tax exempt status sent to Stripe (e.g., `exempt`, `reverse`). |

### Contact

| Field | What It Stores |
|-------|---------------|
| Stripe Customer Id | Stripe Customer ID for this Contact. |
| Stripe Default Payment Method | Default payment method on file. |
| Stripe Event Last Triggered | Last sync timestamp. |

### Lead

| Field | What It Stores |
|-------|---------------|
| Stripe Customer Id | Stripe Customer ID for this Lead. |
| Stripe Default Payment Method | Default payment method on file. |

### User

| Field | What It Stores |
|-------|---------------|
| Stripe Customer Id | Stripe Customer ID for this User. |
| Stripe Default Payment Method | Default payment method on file. |

### Opportunity

| Field | What It Stores |
|-------|---------------|
| Stripe Checkout Session Id | Checkout Session ID when using the hosted checkout flow. |
| Stripe Checkout Session URL | URL of the Stripe-hosted checkout page. |
| Stripe Invoice Id | Stripe Invoice ID for this Opportunity. |
| Stripe Invoice Status | Current invoice status: `draft`, `open`, `paid`, `uncollectible`, or `void`. |
| Stripe Invoice PDF | URL to download the invoice PDF. |
| Stripe Invoice URL | URL of the hosted invoice page (shareable with customers). |
| Stripe Invoice Effective Date | Invoice effective date. |
| Stripe Invoice Due Date | Invoice due date. |
| Stripe Invoice Footer | Footer text on the invoice. |
| Stripe Charge Receipt | Indicates a payment receipt exists. |
| Stripe Charge Receipt Number | Receipt number from Stripe. |
| Stripe Charge Receipt URL | URL of the payment receipt. |
| Stripe Payment Method Id | Payment method used for this Opportunity. |
| Stripe Event Last Triggered | Last sync timestamp. |

### Opportunity Line Item (OpportunityLineItem)

| Field | What It Stores |
|-------|---------------|
| Stripe Product Id | The Stripe Product ID for this line item. |
| Stripe Product Name | Product name from Stripe. |
| Stripe Product Description | Product description from Stripe. |
| Stripe Currency | Currency code for this line item. |
| Stripe Invoice Item Id | The Stripe Invoice Item ID (when synced to an invoice). |
| Stripe Event Last Triggered | Last sync timestamp. |

### Product

| Field | What It Stores |
|-------|---------------|
| Stripe Product Id | The Stripe Product ID synced from this Product. |
| Stripe Product Image URL | URL of the product image in Stripe. Used by the Express Payment component. |
| Stripe Product Image Display | Whether to display the product image. |
| Stripe Statement Descriptor | Statement descriptor that appears on the customer's card statement. |

### Pricebook Entry

| Field | What It Stores |
|-------|---------------|
| Stripe Product Id | The Stripe Product ID associated with this price. |
| Stripe Price Id | The Stripe Price ID synced from this Pricebook Entry. |
| Stripe Lookup Key | An idempotency key used to prevent duplicate price creation. |

### Form Submission (Form_Submission__c)

If you use the FlowToolKit Form Builder with payment forms, these fields store payment results:

| Field | What It Stores |
|-------|---------------|
| Customer Id | Stripe Customer ID |
| Payment Intent Id | Stripe Payment Intent ID |
| Setup Intent Id | Stripe Setup Intent ID |
| Subscription Id | Stripe Subscription ID |
| Invoice Id | Stripe Invoice ID |
| Payment Method Id | Stripe Payment Method ID |
| Card Brand, Last 4, Exp Month, Exp Year, Funding, Country | Card details from the payment |

---

## 6. Platform Events

The package uses platform events for asynchronous communication between Salesforce and Stripe. You generally don't need to interact with these directly, but it's helpful to understand them for troubleshooting.

| Event | Direction | What It Does |
|-------|-----------|-------------|
| **Stripe Customer Insert/Update** | Salesforce → Stripe | Published when Account fields change. Carries customer data (name, email, phone, address) to be synced to Stripe. |
| **Stripe Customer** | Stripe → Salesforce | Published from Stripe webhooks when a customer is created or updated externally. Updates the Salesforce record. |
| **Stripe Invoice** | Stripe → Salesforce | Published from Stripe webhooks for invoice events. Updates Opportunity fields. |
| **Stripe Invoice Item** | Stripe → Salesforce | Published from Stripe webhooks for invoice line item events. Updates OpportunityLineItem fields. |

**Why platform events?** Salesforce doesn't allow direct API callouts from record triggers. Platform events let the system make the Stripe API call asynchronously in a separate transaction, avoiding governor limit issues.

---

## 7. Pre-Built Flows Reference

### Screen Flows

| Flow | What It Does | Key Inputs |
|------|-------------|------------|
| **Stripe Payment (Collect Payment Form)** | Collects a one-time payment. | Amount, Currency, Customer details |
| **Stripe Payment (Setup Payment Method)** | Saves a payment method. Entity-aware — works with Account, Contact, Lead, User, or Opportunity. | Record ID |
| **Stripe Payment (New Subscription)** | Creates a subscription. | Customer ID, Items, Billing parameters |
| **Stripe Payment (Checkout Session Opportunity)** | Creates a Stripe-hosted checkout page from an Opportunity. | Opportunity record |
| **Opportunity Generate Invoice** | Creates a Stripe invoice from an Opportunity. | Opportunity record |

### Template Flows (Read-Only References)

| Flow | Corresponds To |
|------|---------------|
| Template Stripe Payment (Collect Payment Form) | Collect Payment Form |
| Template Stripe Payment (Setup Payment Method) | Setup Payment Method |
| Template Stripe Payment (New Subscription) | New Subscription |
| Stripe Payment (Checkout Session Template) | Checkout Session |

### Utility Subflows (Called by Other Flows)

| Flow | What It Does |
|------|-------------|
| **Stripe Create/Update Customer** | Looks up or creates a Stripe Customer. Maps name, email, phone, address. Overridable — you can customize the field mapping. |
| **Stripe Product (Create/Update Price)** | Syncs a PricebookEntry to a Stripe Price. |
| **Stripe Utility (Sync Product)** | Syncs a Product2 to a Stripe Product. |
| **Stripe Utility (Sync Pricebook Entry)** | Syncs a PricebookEntry to Stripe. |
| **Stripe Utility (Get Product)** | Retrieves a Stripe Product by ID. |
| **Stripe Utility (Create Invoices)** | Creates a Stripe invoice. |
| **Stripe Utility (Create Invoice Items)** | Creates line items on a Stripe invoice. |

---

## 8. Important Considerations

### Amount Format

This is the most common source of confusion:

| Where | Format | Example for $50.00 |
|-------|--------|-------------------|
| Flow screen components (Payment, Setup, Subscription) | **Cents** (Integer) | `5000` |
| Build Subscription Item action | **Cents** (Decimal) | `5000` |
| Express Payment (Experience Cloud) | **Dollars** (Number) | `50` |

The minimum payment amount is **$0.50** (50 cents). This is enforced by both the screen components and the Build Subscription Item action.

### Stripe Account Auto-Detection

The payment components and pre-built flows automatically detect which Stripe account to use:
- **Sandbox orgs** → Test mode account
- **Production orgs** → Live mode account

You can override this by:
- Passing the `Publishable Key` and `Stripe Account Id` inputs explicitly on the screen component
- Checking **Test Mode** in the Stripe Payment Accelerator Settings custom setting (forces test mode everywhere)

### Customer ID Requirements

- **Stripe Payment** (one-time): Customer ID is **optional**. You can collect payments without a Stripe Customer.
- **Stripe Setup Card**: Customer ID is **required**. You must have a customer to save a payment method to.
- **Stripe Subscription**: Customer ID is **required**. Subscriptions must be attached to a customer.

Use the **Stripe Create/Update Customer** subflow to create a customer from an Account, Contact, Lead, or User record.

### Subscription Item Billing Intervals

The **Build Subscription Item** action validates the interval value. It must be exactly one of:
- `day`
- `week`
- `month`
- `year`

Any other value will cause an error. The interval count multiplies the interval (e.g., interval = `month`, interval count = `3` means bill every 3 months).

### DateTime Fields for Subscriptions

The Stripe Subscription component accepts DateTime inputs for Cancel At, Billing Cycle Anchor, and Backdate Start Date. These are standard Salesforce DateTime variables. The component converts them to the format Stripe expects automatically — you don't need to do any conversion.

### Express Checkout (Apple Pay / Google Pay)

When **Enable Express Checkout** is turned on:
- The standard card form is replaced with Apple Pay and/or Google Pay buttons
- Which buttons appear depends on the user's device and browser (Apple Pay only shows on Safari/iOS, Google Pay only on Chrome/Android)
- If no express checkout methods are available for the user, the form falls back gracefully

**Apple Pay setup:** If you're using Apple Pay on a custom domain (Experience Cloud), you need to upload the Apple domain verification file as a static resource and set the resource name in the **Stripe Payment Accelerator Settings** custom setting.

### PCI Compliance

The payment form runs inside a **secure iframe**. Credit card numbers, CVVs, and other sensitive payment data never touch your Salesforce org. The data goes directly from the user's browser to Stripe's servers. This means:
- No PCI scope added to your Salesforce org
- No sensitive payment data stored in Salesforce
- The Stripe Payment Intent ID and last 4 digits are safe to store (they're not sensitive)

### Sync Loop Prevention

The `Stripe Event Last Triggered` field on Account, Contact, Opportunity, OpportunityLineItem, and Product records prevents infinite sync loops. When a record is updated by a Stripe webhook handler, this timestamp is set. The record-triggered flows check this timestamp and skip the sync if the change was just made by a webhook — preventing a back-and-forth loop.

### Overridable Flow Customization

When you modify an overridable flow:
- Your customizations are preserved across package upgrades
- Non-breaking additions from the package (new variables, new paths) are merged in
- If you want to see what the unmodified flow looks like after an upgrade, check the corresponding Template flow
- If you need to start over, you can deactivate your customized flow and create a new one from the template

### Field-Level Security

The package installs custom fields on standard objects. Make sure the appropriate profiles and permission sets have access to these fields if users or flows need to read or write them. Key fields to check:
- `Stripe Customer Id` on Account, Contact, Lead, User
- `Stripe Invoice Id` and related fields on Opportunity
- `Stripe Product Id` on Product2 and PricebookEntry

### API Callout Limits

Stripe API calls count toward Salesforce's callout limits. Each payment, setup, or subscription creation uses 2-3 callouts. The background sync flows (customer, product, invoice) each use 1-2 callouts per record. Platform events handle these asynchronously to avoid hitting limits during record triggers.
