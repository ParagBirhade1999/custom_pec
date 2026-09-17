import frappe
from frappe.utils import cint

from custom_pec.constants import ACTIVE_BID_STAGES, STAGE_CLOSURE, STAGE_COLD


def refresh_customer_bid_intelligence(customer: str):
	if not customer or not frappe.db.exists("Customer", customer):
		return

	rows = frappe.get_all(
		"Opportunity",
		filters={"opportunity_from": "Customer", "party_name": customer},
		fields=["name", "status", "sales_stage"],
	)
	total = len(rows)
	won = sum(1 for r in rows if r.status == "Converted" or r.sales_stage == STAGE_CLOSURE)
	lost = sum(1 for r in rows if r.status == "Lost")
	cold = sum(1 for r in rows if r.sales_stage == STAGE_COLD and r.status != "Lost")
	active = sum(
		1 for r in rows if r.status not in ("Lost", "Converted", "Closed") and r.sales_stage in ACTIVE_BID_STAGES
	)

	frappe.db.set_value(
		"Customer",
		customer,
		{
			"custom_total_inquiries": total,
			"custom_projects_won": won,
			"custom_projects_lost": lost,
			"custom_projects_cold": cold,
			"custom_active_bids": active,
		},
		update_modified=False,
	)


def onload(doc, method=None):
	if not doc.name:
		return
	refresh_customer_bid_intelligence(doc.name)
	doc.set_onload(
		"pec_bid_intelligence",
		{
			"total": cint(doc.custom_total_inquiries),
			"won": cint(doc.custom_projects_won),
			"lost": cint(doc.custom_projects_lost),
			"cold": cint(doc.custom_projects_cold),
			"active": cint(doc.custom_active_bids),
		},
	)
