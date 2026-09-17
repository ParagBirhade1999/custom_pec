import frappe
from frappe import _
from custom_pec.constants import COMMERCIAL_ATTACH_FIELDS


def create_project_from_opportunity(opportunity) -> str:
	project_name = _unique_project_name(opportunity)
	project = frappe.get_doc(
		{
			"doctype": "Project",
			"project_name": project_name,
			"status": "Open",
			"custom_handoff_status": "Pending Review",
			"customer": opportunity.party_name,
			"company": opportunity.company,
			"expected_start_date": opportunity.custom_expected_project_start_date,
			"expected_end_date": opportunity.custom_expected_project_end_date,
			"estimated_costing": opportunity.custom_final_negotiated_contract_value,
			"custom_contract_value": opportunity.custom_final_negotiated_contract_value,
			"custom_opportunity": opportunity.name,
			"notes": _("Created from Opportunity {0}").format(opportunity.name),
		}
	)
	project.flags.ignore_permissions = True
	project.insert()
	copy_technical_files(opportunity.name, project.name)
	return project.name


def _unique_project_name(opportunity) -> str:
	base = f"{opportunity.title or opportunity.name} — {opportunity.party_name}"
	name = base[:140]
	if not frappe.db.exists("Project", {"project_name": name}):
		return name
	return f"{name} ({opportunity.name})"[:140]


def copy_technical_files(opportunity_name: str, project_name: str):
	fields = ["name", "file_url", "file_name", "is_private", "attached_to_field"]
	if frappe.db.has_column("File", "custom_document_class"):
		fields.append("custom_document_class")
	files = frappe.get_all(
		"File",
		filters={
			"attached_to_doctype": "Opportunity",
			"attached_to_name": opportunity_name,
			"is_folder": 0,
		},
		fields=fields,
	)
	for row in files:
		if row.attached_to_field in COMMERCIAL_ATTACH_FIELDS:
			continue
		if row.get("custom_document_class") == "Commercial":
			continue
		if not row.file_url:
			continue
		if frappe.db.exists(
			"File",
			{
				"attached_to_doctype": "Project",
				"attached_to_name": project_name,
				"file_url": row.file_url,
			},
		):
			continue
		frappe.get_doc(
			{
				"doctype": "File",
				"file_name": row.file_name,
				"file_url": row.file_url,
				"is_private": row.is_private,
				"attached_to_doctype": "Project",
				"attached_to_name": project_name,
				"custom_document_class": "Technical",
			}
		).insert(ignore_permissions=True)


def validate(doc, method=None):
	if doc.custom_handoff_status != "Live":
		return
	if doc.custom_opportunity and not frappe.db.get_value("Opportunity", doc.custom_opportunity, "name"):
		frappe.throw(_("Source Opportunity is missing."))


def on_update(doc, method=None):
	for row in doc.get("users") or []:
		if not row.view_attachments:
			row.db_set("view_attachments", 1, update_modified=False)
