# Flow Tool Kit: Stripe Connector Accelerator

The Stripe Connector Accelerator extends the [Stripe Connector for Salesforce](https://stripe.com/docs/connectors/salesforce) and the [Flow Tool Kit](https://github.com/common-unite/Flow_Tool_Kit_Public) to let you collect payments, save payment methods, and create subscriptions directly inside Salesforce Flows and Experience Cloud pages — no code required.

![Demo Donation Flow Form with Flow Tool Kit and Stripe Payment Component](docs/images/Demo%20Donation%20Flow%20Form%20with%20Flow%20Tool%20Kit%20and%20Stripe%20Payment%20Component.png)

### Pricing

This package is **100% free** to install and use in **sandboxes and scratch orgs** — no activation required. Build, test, and evaluate the full package at no cost.

To use the package in a **production org**, a one-time setup fee is required. There is no recurring payment. Visit the [Stripe Accelerator activation page](https://common-unite.my.site.com/s/stripe-accelerator) to get started.

---

## What You Can Do

### Collect Payments in Flows

Drop a payment screen component into any Flow to collect one-time payments, save cards for later, or start subscriptions. The payment form supports credit/debit cards, Apple Pay, Google Pay, and Link.

![Easy to use property editor for collecting payments in flow screens](docs/images/Flow%20%7C%20Easy%20to%20use%20property%20editor%20for%20collecting%20payments%20in%20flow%20screens.png)

| Screen Component | Use It When... |
|-----------------|----------------|
| **Stripe Payment** | You need to collect a one-time payment or authorize a charge. |
| **Stripe Setup Card** | You want to save a customer's payment method for future billing without charging them now. |
| **Stripe Subscription** | You want to set up recurring billing with configurable items, billing cycles, and discounts. |

### Collect Payments on Experience Cloud Pages

Embed payments directly on your community/portal pages:

| Component | Use It When... |
|-----------|----------------|
| **Stripe Payment Form** | You want users to fill out a form and pay in one step. Maps form fields to payment inputs automatically. |
| **Express Payment** | You want a one-click checkout button (Apple Pay / Google Pay) next to product details. |

### Use Pre-Built Flows Out of the Box

The package includes ready-to-use Screen Flows you can launch from buttons, quick actions, or embed as subflows:

- **Collect Payment Form** — Collects a one-time payment
- **Setup Payment Method** — Saves a card (works with Accounts, Contacts, Leads, Users, and Opportunities)
- **New Subscription** — Creates a recurring subscription
- **Checkout Session** — Generates a Stripe-hosted checkout page from Opportunity line items
- **Generate Invoice** — Creates a Stripe invoice from an Opportunity

### Automate Stripe Sync

The package includes background automation that keeps Salesforce and Stripe in sync:

- **Customer sync** — Account changes automatically push to Stripe Customers
- **Product & price sync** — New or updated Products and Pricebook Entries sync to Stripe
- **Invoice sync** — Opportunity line items sync to Stripe invoices, and webhook updates flow back
- **Webhook handlers** — Stripe events (payment confirmations, customer updates, checkout completions) automatically update Salesforce records

### Work with Stripe Metadata in Flows

Five Flow actions let you work with Stripe data without writing code:

- **Get Stripe Account Keys** — Automatically picks the right Stripe account (test vs. live)
- **Build Subscription Item** — Creates subscription line items with pricing for use in subscription flows
- **Get Metadata / Put Metadata** — Read and write key-value metadata on Stripe objects
- **Get JSON Metadata** — Extracts metadata from Stripe webhook event payloads

---

## Documentation

- **[Overview](docs/OVERVIEW.md)** — What's in the package and how the pieces work together. Start here.
- **[Implementation Guide](docs/TECHNICAL_REFERENCE.md)** — Detailed inputs/outputs for every component and action, custom fields and objects, configuration settings, and important considerations for admins.

---

## Installation

Install the dependencies **in order**, then install the Accelerator.

### Step 1: Flow Tool Kit (Base Package)

[Get It Now](https://common-unite.my.site.com/s/latest-release) from the Common Unite site.

### Step 2: Stripe Connector for Salesforce (2 packages)

**Stripe Connector — Package 1:**
- [Production & Developer Edition Orgs](https://login.salesforce.com/packaging/installPackage.apexp?p0=04tRN000004ZhkXYAS)
- [Sandbox & Scratch Orgs](https://test.salesforce.com/packaging/installPackage.apexp?p0=04tRN000004ZhkXYAS)

**Stripe Connector — Package 2:**
- [Production & Developer Edition Orgs](https://login.salesforce.com/packaging/installPackage.apexp?p0=04t4x0000003MzaAAE)
- [Sandbox & Scratch Orgs](https://test.salesforce.com/packaging/installPackage.apexp?p0=04t4x0000003MzaAAE)

### Step 3: Stripe Connector Accelerator

Install the latest release from the [Releases page](https://github.com/common-unite/FlowToolKit_Stripe_Connector_Accelerator_Public/releases).

### Step 4: Configure the Stripe Connector

After installing all packages, follow Stripe's [Installation Guide](https://docs.stripe.com/use-stripe-apps/stripe-app-for-salesforce/installation-guide) to connect your Stripe account to Salesforce and complete the setup.
