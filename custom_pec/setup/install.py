import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

from custom_pec.constants import LOST_REASONS, PIPELINE_STAGES, STAGE_COLD
from custom_pec.setup.custom_fields import get_custom_fields


def after_install():
	sync_customizations()


def after_migrate():
	sync_customizations()


def sync_customizations():
	ensure_sales_stages()
	ensure_lost_reasons()
	create_custom_fields(get_custom_fields(), update=True)
	ensure_property_setters()
	ensure_kanban_board()
	frappe.clear_cache()


def ensure_sales_stages():
	for stage in PIPELINE_STAGES:
		if not frappe.db.exists("Sales Stage", stage):
			doc = frappe.get_doc({"doctype": "Sales Stage", "stage_name": stage})
			doc.insert(ignore_permissions=True)


def ensure_lost_reasons():
	for reason in LOST_REASONS:
		if not frappe.db.exists("Opportunity Lost Reason", reason):
			doc = frappe.get_doc({"doctype": "Opportunity Lost Reason", "lost_reason": reason})
			doc.insert(ignore_permissions=True)


def ensure_property_setters():
	setters = [
		("Opportunity", "sales_stage", "default", STAGE_COLD, "Text"),
		("Opportunity", "opportunity_owner", "label", "Leading Deal Responsible", "Data"),
		("Opportunity", "expected_closing", "label", "Expected Award Date", "Data"),
		("Opportunity", "opportunity_amount", "label", "Estimated Value", "Data"),
		("Project", "users_section", "label", "Execution Team", "Data"),
		(
			"Project",
			"users",
			"description",
			"Assign users here to grant Project access, including transferred technical attachments.",
			"Small Text",
		),
	]
	for doctype, fieldname, property, value, property_type in setters:
		exists = frappe.db.exists(
			"Property Setter",
			{"doc_type": doctype, "field_name": fieldname, "property": property},
		)
		if exists:
			frappe.db.set_value("Property Setter", exists, "value", value)
			continue
		make_property_setter(doctype, fieldname, property, value, property_type, validate_fields_for_doctype=False)


def ensure_kanban_board():
	name = "EPC Pipeline"
	if frappe.db.exists("Kanban Board", name):
		return
	indicators = ["Gray", "Blue", "Orange", "Cyan", "Purple", "Yellow", "Green"]
	try:
		board = frappe.new_doc("Kanban Board")
		board.kanban_board_name = name
		board.reference_doctype = "Opportunity"
		board.field_name = "sales_stage"
		board.private = 0
		board.show_labels = 1
		board.filters = "[]"
		board.fields = '["status", "opportunity_amount", "party_name"]'
		for stage, indicator in zip(PIPELINE_STAGES, indicators, strict=True):
			board.append(
				"columns",
				{"column_name": stage, "status": "Active", "indicator": indicator},
			)
		board.flags.ignore_permissions = True
		board.insert()
	except Exception:
		frappe.log_error(title="PEC Kanban Board setup")
