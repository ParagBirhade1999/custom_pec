import frappe
from frappe.desk.doctype.notification_log.notification_log import enqueue_create_notification
from frappe.utils import add_days, getdate


def notify_bid_validity_expiry():
	"""Daily: alert deal owner 7 days before bid validity expires."""
	target = add_days(getdate(), 7)
	rows = frappe.get_all(
		"Opportunity",
		filters={
			"sales_stage": "Proposal Submitted",
			"status": ["not in", ["Lost", "Converted", "Closed"]],
			"custom_bid_validity_expiry_date": target,
		},
		fields=["name", "opportunity_owner", "party_name", "custom_bid_validity_expiry_date"],
	)
	for opp in rows:
		if not opp.opportunity_owner:
			continue
		enqueue_create_notification(
			[opp.opportunity_owner],
			{
				"type": "Alert",
				"document_type": "Opportunity",
				"document_name": opp.name,
				"subject": f"Bid validity expires in 7 days: {opp.name}",
				"from_user": "Administrator",
				"email_content": (
					f"Opportunity {opp.name} ({opp.party_name}) bid validity expires on "
					f"{opp.custom_bid_validity_expiry_date}."
				),
			},
			dedupe_on=["document_type", "document_name", "subject", "for_user"],
		)
