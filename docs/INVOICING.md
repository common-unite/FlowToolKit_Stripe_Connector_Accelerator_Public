# Stripe Invoicing — How It Works

This guide covers everything related to Stripe Invoice and Checkout Session functionality in the Stripe Connector Accelerator. It explains the included flows, custom fields, platform events, and how they work together to create, sync, and manage invoices from Opportunity records.

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Actions](#quick-actions)
3. [Invoice Lifecycle](#invoice-lifecycle)
4. [Flows](#flows)
5. [Custom Fields](#custom-fields)
6. [Platform Events](#platform-events)
7. [Checkout Sessions](#checkout-sessions)
8. [How It All Fits Together](#how-it-all-fits-together)

---

## Overview

The invoicing system links **Opportunities** to **Stripe Invoices**. Each Opportunity can have one active Stripe Invoice. Opportunity Line Items become Stripe Invoice Items. The package handles:

- Creating invoices from Opportunity records (manual via quick action)
- Syncing invoice data back to Salesforce (automatic via platform events)
- Finalizing, replacing, and managing invoice status (automatic via record-triggered flows)
- Syncing line item changes to draft invoices (automatic via record-triggered flows)
- Generating Stripe-hosted checkout sessions from Opportunities

All Stripe API calls are made through the **Stripe Connector for Salesforce** managed package (`stripeGC`) — the accelerator orchestrates these calls through declarative Flows.

---

## Quick Actions

These quick actions are available on record pages and can be added to page layouts or Lightning actions:

| Object | Action | What It Does |
|--------|--------|-------------|
| Opportunity | **Generate Invoice** | Opens a screen flow that creates a Stripe Invoice from the Opportunity's line items |
| Opportunity | **Open Checkout** | Opens a screen flow that creates a Stripe Checkout Session and returns a payment link |
| Opportunity | **Setup Payment Method** | Opens a screen flow to save a payment method for the related customer |
| Account | **Setup Payment Method** | Opens a screen flow to save a payment method for the Account's Stripe Customer |
| Contact | **Setup Payment Method** | Opens a screen flow to save a payment method for the Contact's Stripe Customer |

---

## Invoice Lifecycle

An invoice moves through these stages, tracked by the `Stripe Invoice Status` field on the Opportunity:

```
                  Generate Invoice
                       │
                       ▼
                  ┌──────────┐
                  │  draft    │ ← Line items can be added/modified
                  └────┬─────┘
                       │ Finalize (change status to "open")
                       ▼
                  ┌──────────┐
                  │  open     │ ← Sent to customer, awaiting payment
                  └────┬─────┘
                       │ Customer pays
                       ▼
                  ┌──────────┐
                  │  paid     │ ← Payment received
                  └──────────┘

  Other terminal states:
  • uncollectible — Payment failed after exhausting retries
  • void — Manually voided by admin
```

**Key behaviors:**
- Setting the status to **"open"** triggers the Finalize Invoice flow, which finalizes the draft in Stripe and generates the PDF and hosted URL
- Setting the status to **"draft"** on an open invoice triggers the Replace Invoice flow, which creates a new draft from the existing invoice (allowing modifications)
- Adding or modifying line items on an Opportunity with a **draft** invoice automatically syncs the changes to Stripe

---

## Flows

### Screen Flows (User-Initiated)

#### Opportunity Generate Invoice

| | |
|---|---|
| **API Name** | `Opportunity_Generate_Invoice` |
| **Type** | Screen Flow (Overridable) |
| **Launched From** | "Generate Invoice" quick action on Opportunity |
| **What It Does** | Validates the Opportunity has products, collects invoice parameters (due date, collection method), then creates a Stripe Invoice with all line items |

**Validation checks:**
- Opportunity must have at least one product (OpportunityLineItem)
- Opportunity must not already have an active invoice

**Parameters collected:**
- Due date
- Collection method (charge automatically or send invoice)
- Whether to finalize immediately

**Calls:** `Stripe_Utility_Create_Invoices` subflow

---

### Record-Triggered Flows (Automatic)

#### Finalize Invoice

| | |
|---|---|
| **API Name** | `Stripe_Trigger_Handler_Opportunity_After_Update_Finalize_Invoice` |
| **Type** | Auto-Launched (Overridable) |
| **Trigger** | Opportunity After Update |
| **Condition** | `Stripe Invoice Status` changes to "open" AND `Stripe Invoice Id` is not blank |
| **What It Does** | Retrieves the draft invoice from Stripe and finalizes it, generating the PDF and hosted payment URL |

#### Replace Invoice

| | |
|---|---|
| **API Name** | `Stripe_Trigger_Handler_Opportunity_After_Update_Replace_Invoice` |
| **Type** | Auto-Launched (Overridable) |
| **Trigger** | Opportunity After Update |
| **Condition** | `Stripe Invoice Status` changes to "draft" AND `Stripe Invoice Id` is not blank AND `Stripe Invoice Effective Date` is not blank |
| **What It Does** | Creates a new draft invoice from an existing open invoice, allowing the admin to make modifications before re-finalizing |

#### Sync Line Item Changes

| | |
|---|---|
| **API Name** | `Stripe_Trigger_Handler_OpportunityLineItem_After_Insert_Update_Handle_Invoice` |
| **Type** | Auto-Launched (Overridable) |
| **Trigger** | OpportunityLineItem After Create/Update |
| **Condition** | Related Opportunity has a Stripe Invoice ID, invoice status is "draft", and Quantity or UnitPrice changed |
| **What It Does** | Publishes a `Stripe_Invoice_Item__e` platform event to sync the line item changes to the Stripe invoice asynchronously |

---

### Platform Event Handlers

#### Sync Invoice to Opportunity

| | |
|---|---|
| **API Name** | `Stripe_Event_Handler_Sync_Invoice` |
| **Type** | Auto-Launched (Overridable) |
| **Trigger** | `Stripe_Invoice__e` platform event |
| **What It Does** | Retrieves invoice details from Stripe and updates the Opportunity with: Invoice ID, Status, URL, PDF URL, Due Date, and Effective Date |

Includes retry logic (up to 7 retries) for record lock scenarios where the Opportunity is being updated by another process simultaneously.

#### Sync Invoice Item to Line Item

| | |
|---|---|
| **API Name** | `Stripe_Event_Handler_Sync_Invoice_Item` |
| **Type** | Auto-Launched |
| **Trigger** | `Stripe_Invoice_Item__e` platform event |
| **What It Does** | Retrieves invoice item details from Stripe and updates the OpportunityLineItem with the Stripe Invoice Item ID and quantity |

---

### Utility Subflows

These are called by other flows — not triggered directly.

| Flow | What It Does |
|------|-------------|
| **Stripe_Utility_Create_Invoices** | Core invoice creation logic. Converts dates to UNIX timestamps, calls the Stripe API to create the invoice with all line items, optionally finalizes it, and publishes the sync event. Supports creating from scratch or from an existing invoice (for replacements). |
| **Stripe_Utility_Create_Invoice_Items** | Adds individual line items to a draft invoice. Called for each OpportunityLineItem. |
| **Stripe_Utility_Stripe_Event_Response_Body_Sync_Invoice_to_Opportunity** | Parses a raw Stripe API response, extracts invoice fields, converts timestamps, and returns mapped data for updating the Opportunity. |
| **Stripe_Utility_Stripe_Event_Response_Body_Sync_Invoice_Item** | Parses a raw Stripe API response for invoice items and returns mapped data for updating the OpportunityLineItem. |

---

## Custom Fields

### Opportunity — Invoice Fields

| Field | API Name | Type | Description |
|-------|----------|------|-------------|
| Stripe Invoice Id | `cUnite_Stripe_Invoice_Id__c` | Text (255) | The Stripe Invoice ID (e.g., `in_xxx`). External ID. Set when the invoice is created. |
| Stripe Invoice Status | `cUnite_Stripe_Invoice_Status__c` | Picklist | Current invoice status: `draft`, `open`, `paid`, `uncollectible`, or `void`. Changing this value triggers automation (see Invoice Lifecycle). |
| Stripe Invoice URL | `cUnite_Stripe_Invoice_URL__c` | URL | Hosted invoice page where the customer can view and pay. Available after the invoice is finalized. |
| Stripe Invoice PDF | `cUnite_Stripe_Invoice_PDF__c` | URL | Direct download link for the invoice PDF. Available after the invoice is finalized. |
| Stripe Invoice Due Date | `cUnite_Stripe_Invoice_Due_Date__c` | Date | Payment due date. Only applicable for `send_invoice` collection method. |
| Stripe Invoice Effective Date | `cUnite_Stripe_Invoice_Effective_Date__c` | Date | The date the invoice is in effect. Replaces the system-generated "Date of issue" on the PDF. |
| Stripe Invoice Footer | `cUnite_Stripe_Invoice_Footer__c` | Long Text Area | Custom footer text displayed on the invoice PDF. |

### Opportunity — Checkout Session Fields

| Field | API Name | Type | Description |
|-------|----------|------|-------------|
| Stripe Checkout Session Id | `cUnite_Stripe_Checkout_Session_Id__c` | Text (255) | The Stripe Checkout Session ID. External ID. Set when a checkout session is created. |
| Stripe Checkout Session URL | `cUnite_Stripe_Checkout_Session_URL__c` | Long Text Area | URL to redirect the customer to the Stripe-hosted checkout page. Only present while the session is active. |

### Opportunity — Payment Receipt Fields

| Field | API Name | Type | Description |
|-------|----------|------|-------------|
| Stripe Charge Receipt URL | `cUnite_Stripe_Charge_Receipt_URL__c` | URL | Link to the Stripe-hosted payment receipt. Updated with the latest charge state. |
| Stripe Charge Receipt Number | `cUnite_Stripe_Charge_Receipt_Number__c` | Text (255) | Transaction number that appears on email receipts. Null until a receipt is sent. |
| Receipt | `cUnite_Stripe_Charge_Receipt__c` | Formula (Text) | Clickable hyperlink to the receipt URL. Displays the receipt number or "Open Receipt". |
| Stripe Payment Method Id | `cUnite_Stripe_Payment_Method_Id__c` | Text (255) | The Stripe Payment Method used for payment. External ID. |

### OpportunityLineItem — Invoice Item Fields

| Field | API Name | Type | Description |
|-------|----------|------|-------------|
| Stripe Invoice Item Id | `cUnite_Stripe_Invoice_Item_Id__c` | Text (255) | The Stripe InvoiceItem ID linking this line item to the Stripe invoice line. External ID. |
| Stripe Product Id | `cUnite_Stripe_Product_Id__c` | Formula (Text) | Pulls the Stripe Product ID from the related Product2 record via PricebookEntry. |
| Stripe Product Name | `cUnite_Stripe_Product_Name__c` | Text | Product name from Stripe. |
| Stripe Product Description | `cUnite_Stripe_Product_Description__c` | Long Text Area | Product description from Stripe. |
| Stripe Currency | `cUnite_Stripe_Currency__c` | Text | ISO currency code for this line item (e.g., `usd`). |
| Stripe Event Last Triggered | `cUnite_Stripe_Event_Last_Triggered__c` | DateTime | Timestamp of the last platform event trigger. Prevents duplicate processing and sync loops. |

---

## Platform Events

### Stripe Invoice (`Stripe_Invoice__e`)

Published when an invoice is created or modified. Triggers the `Stripe_Event_Handler_Sync_Invoice` flow to sync data back to the Opportunity.

| Field | Type | Description |
|-------|------|-------------|
| Stripe Invoice Id | Text (Required) | The Stripe Invoice ID |
| Opportunity Id | Text | The related Salesforce Opportunity ID |

- **Publish Behavior:** PublishAfterCommit (ensures the triggering transaction completes first)
- **Volume:** High Volume

### Stripe Invoice Item (`Stripe_Invoice_Item__e`)

Published when an invoice line item is added or modified. Triggers the `Stripe_Event_Handler_Sync_Invoice_Item` flow to sync data back to the OpportunityLineItem.

| Field | Type | Description |
|-------|------|-------------|
| Invoice Id | Text (Required) | The related Stripe Invoice ID |
| Invoice Item Id | Text | The Stripe InvoiceItem ID |
| Opportunity Line Item Id | Text | The related Salesforce OpportunityLineItem ID |

- **Publish Behavior:** PublishAfterCommit
- **Volume:** High Volume

---

## Checkout Sessions

Checkout Sessions provide an alternative to invoicing — instead of creating a Stripe Invoice, you generate a Stripe-hosted checkout page that the customer can visit to pay.

### Flow: Stripe Payment Checkout Session Opportunity

| | |
|---|---|
| **API Name** | `Stripe_Payment_Checkout_Session_Opportunity` |
| **Type** | Screen Flow |
| **Launched From** | "Open Checkout" quick action on Opportunity |
| **What It Does** | Reads the Opportunity and its line items, resolves Stripe Product IDs, creates a Checkout Session, and returns the hosted checkout URL |

The checkout URL is stored on the Opportunity (`Stripe Checkout Session URL`) and can be emailed to the customer or displayed on the page.

### Webhook Handler: Checkout Session Completed

| | |
|---|---|
| **API Name** | `Stripe_Event_After_Insert_Checkout_Session_Completed` |
| **Location** | `force-app-unpackaged` (not in the managed package — deploy separately if needed) |
| **What It Does** | When the customer completes checkout, retrieves the charge/payment intent details and updates the Opportunity with receipt information |

**Additional flows available:**
- `Stripe_Payment_Checkout_Session_Overridable` — Overridable version for customization
- `Stripe_Payment_Checkout_Session_Template` — Read-only template for reference

---

## How It All Fits Together

```
  Admin clicks "Generate Invoice" on Opportunity
       │
       ▼
  Opportunity_Generate_Invoice (Screen Flow)
       │  validates products, collects parameters
       ▼
  Stripe_Utility_Create_Invoices (Subflow)
       │  calls Stripe API, creates invoice + items
       │  publishes Stripe_Invoice__e
       ▼
  Stripe_Event_Handler_Sync_Invoice (Event Handler)
       │  retrieves invoice from Stripe
       │  updates Opportunity fields:
       │    Invoice Id, Status, URL, PDF, Dates
       ▼
  Opportunity record updated with invoice data
       │
       ├─── Admin changes status to "open"
       │         │
       │         ▼
       │    Finalize Invoice (Record-Triggered)
       │         │  finalizes draft, generates PDF + URL
       │         ▼
       │    Stripe_Invoice__e → sync back to Opportunity
       │
       ├─── Admin changes status to "draft"
       │         │
       │         ▼
       │    Replace Invoice (Record-Triggered)
       │         │  creates new draft from existing invoice
       │         ▼
       │    Stripe_Invoice__e → sync back to Opportunity
       │
       └─── Admin adds/modifies line items on draft invoice
                 │
                 ▼
            Sync Line Items (Record-Triggered)
                 │  publishes Stripe_Invoice_Item__e
                 ▼
            Stripe_Event_Handler_Sync_Invoice_Item
                 │  syncs item data to OpportunityLineItem
```

### Why Platform Events?

Salesforce doesn't allow API callouts from record-triggered flows directly. Platform events let the system make Stripe API calls asynchronously in a separate transaction, avoiding governor limit issues and ensuring reliable processing even when records are locked by other operations.

### Sync Loop Prevention

The `Stripe Event Last Triggered` field on Opportunity and OpportunityLineItem records prevents infinite sync loops. When a record is updated by a webhook handler, this timestamp is set. Record-triggered flows check this timestamp and skip the sync if the change was just made by a webhook.
