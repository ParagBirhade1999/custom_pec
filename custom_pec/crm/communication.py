import re

import frappe

OPP_TAG = re.compile(r"\[(CRM-OPP-[^\]]+)\]")


def after_insert(doc, method=None):
	if doc.reference_doctype or not doc.subject:
		return
	match = OPP_TAG.search(doc.subject)
	if not match:
		return
	opportunity = match.group(1)
	if not frappe.db.exists("Opportunity", opportunity):
		return
	doc.db_set(
		{
			"reference_doctype": "Opportunity",
			"reference_name": opportunity,
		},
		update_modified=False,
	)
