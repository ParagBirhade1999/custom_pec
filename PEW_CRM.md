# PEW Engineering CRM — functionality guide

This document explains every behaviour implemented in the `custom_pec` app on the **erpnext-training** site (`training.local`). ERPNext and Frappe core were not modified. Customisations use Custom Fields, Property Setters, hooks, client scripts, and a scheduler.

Open an Opportunity and use the **EPC Pipeline** tab. Change **Sales Stage** on the main form; only that stage’s fields appear.

---

## How the two “status” fields work together

ERPNext already had two independent fields. PEW uses both on purpose:

| Field | Meaning for PEW |
| --- | --- |
| **Sales Stage** | Where the pursuit sits in the 7-stage pipeline (Kanban column). |
| **Status** | Outcome: Open, Lost, Converted, etc. |

There is **no Lost sales stage**. If a bid dies in Qualification, Sales Stage stays **Qualification (Go / No-Go)** and Status becomes **Lost**. That is how you report *where* in the pipeline the pursuit failed.

---

## The 7 Sales Stages

Created as **Sales Stage** masters (Desk → Sales Stage). Default for new Opportunities is **Cold**.

1. **Cold** — rumoured work, unreleased tenders, or stalled conversations. Keeps dead air off the active board without deleting the record.
2. **Inquiry / Tender** — RFQ or portal tender is in hand. Organisation, contact, source, and assignment.
3. **Qualification (Go / No-Go)** — legal/docs, study metrics, subcontract, internal go/no-go.
4. **Queries & Clarifications** — pre-bid date, addendums, scope lock.
5. **Proposal Submitted** — bid value, validity, commercial proposal file, EMD gate.
6. **Evaluation** — sub-stage (technical / price / negotiation) and optional L1–L3 rank.
7. **Closure (Won)** — award data and automatic Project handoff.

You may skip stages that do not apply (for example a private inquiry that never sat in Cold). Moving **one step forward** requires the previous stage’s gate checkboxes (and Go = Yes when leaving Qualification). Skipping more than one step is allowed so public vs private pursuits are not forced through irrelevant gates.

---

## Stage-dependent fields

Each PEW section uses Frappe **Depends On**:

`eval:doc.sales_stage=='<stage name>'`

When you pick a Sales Stage, only that section is shown on the **EPC Pipeline** tab. Data from other stages is still saved; select that stage again to see it.

Inner dependencies:

- **Subcontracted Scope** appears only if Subcontract Required = Yes (Qualification).
- **Our Commercial Rank** appears only if Evaluation sub-stage = Price Bid Review.

Standard fields reused (not duplicated):

- Organisation → Opportunity From + Party (Customer / Lead / Prospect). Existing Customer auto-fills organisation details.
- Contact, Job Title, Phone, Email, Address, Website, Market Segment.
- **Leading Deal Responsible** = Opportunity Owner (label changed by Property Setter).
- **Estimated Value** = Opportunity Amount.
- **Expected Award Date** = Expected Closing.

Added on Inquiry: Type of Organisation, Lead Source, Holding/Parent Company, Key Account, Referral Contact, WINGMAN (second User).

---

## Gates (checklists)

Gates are Check fields. Advancing to the **next** stage in order is blocked until they are ticked on the previous stage:

| Moving to | Required on previous stage |
| --- | --- |
| Qualification | Inquiry logged & assigned |
| Queries | Docs uploaded, deadline logged, Go/No-Go = Yes |
| Proposal | Queries clarified, scope locked |
| Evaluation | Proposal sent |
| Closure | LOI/PO received |

**Go / No-Go = No:** the system will not let Status stay Open. Use **Set as Lost** and a Loss Reason. The card stays in Qualification.

---

## Lost mechanic

Use ERPNext **Set as Lost** (dialog). Seeded reasons:

- Outside Domain  
- Internal No-Go/Lack of Bandwidth  
- Unacceptable Commercial Terms  
- Technical Disqualification  
- Outbid on Price  
- Client Cancelled Project  
- Client Went Cold  

Also fill **Competitor Who Won** when known (standard Competitors table).

After Lost:

- Sales Stage cannot be changed (server + read-only).
- Headline shows “Lost in stage …”.
- Kanban column stays the stage where it died.

---

## Customer bid intelligence

On **Customer → Bid Intelligence**:

- Total Inquiries / Projects Received  
- Won (Converted or Closure stage)  
- Lost (Status Lost)  
- Cold (stage Cold, not Lost)  
- Active Bids (stages Inquiry through Evaluation, not Lost/Converted/Closed)

Counts refresh whenever a linked Opportunity is saved.

---

## Communication and email

- Opportunity already has a **timeline** (emails, comments, calls, meetings).
- **Email Subject Tag** (read-only), e.g. `[CRM-OPP-2026-00001]`. Put this in the subject so inbound mail can be matched.
- New Communications whose subject contains that tag are auto-linked to the Opportunity.
- **PEC → Link Orphan Email** links a Communication that arrived without a tag.
- Google Workspace: configure **Email Account** (IMAP/SMTP) in Frappe; that is not custom code.

Commercial vs technical files: Attach fields on stages 3–7. **Final Proposal** and **Work Order / Client PO** are commercial and are **not** copied to Project. Other Opportunity attachments copy as technical unless File **PEC Document Class** = Commercial.

---

## Project handoff (Closure)

When Sales Stage becomes **Closure (Won)** and the record saves:

1. Party must already be a **Customer** (convert Lead first).
2. Final contract value and expected start/end dates are mandatory.
3. A **Project** is created in **Handoff Status = Pending Review** (this is the Draft gate; standard Project Status has no Draft).
4. Mapped: customer, opportunity name, contract value, dates, link back to Opportunity.
5. Technical files are copied; proposal and WO/PO are not.
6. Opportunity Status is set to **Converted** and **Handoff Project** is filled.

A manager sets **Handoff Status = Live** when execution may start.

**Execution Team** is ERPNext’s Project **Users** table (label renamed). Adding a user shares the Project. **View attachments** is turned on so they can open transferred technical files.

---

## Bid validity reminder

Daily job `custom_pec.tasks.notify_bid_validity_expiry`: if Sales Stage is Proposal Submitted and Bid Validity Expiry Date is in 7 days, the Leading Deal Responsible gets a desk Alert.

Trigger manually:

`bench --site training.local execute custom_pec.tasks.notify_bid_validity_expiry`

---

## Kanban

Board **EPC Pipeline** groups Opportunities by Sales Stage. Open Opportunity List → Kanban → EPC Pipeline. Lost cards remain in the column of the stage where they were lost.

---

## What was already in ERPNext (not rebuilt)

- Customer/Contact masters and Opportunity party linking  
- Timeline, email append, Activities  
- Lost dialog and lost-reason child table  
- Project Users sharing / attachment visibility  
- Market Segment, website, contact fields on Opportunity  

## What this app added

- 7 PEW Sales Stages and Lost Reason masters  
- Stage-dependent Custom Fields  
- Gates, Lost freeze, No-Go rule, Closure → Project  
- Customer KPIs, file class, bid-validity notification, subject-tag routing, orphan email button  
