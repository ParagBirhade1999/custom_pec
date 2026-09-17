import frappe
from frappe import _

from custom_pec.constants import (
	PIPELINE_STAGES,
	STAGE_CLOSURE,
	STAGE_EVALUATION,
	STAGE_PROPOSAL,
	STAGE_QUALIFICATION,
	STAGE_QUERIES,
)
from custom_pec.crm.customer import refresh_customer_bid_intelligence
from custom_pec.project.handoff import create_project_from_opportunity

STAGE_GATES = {
	STAGE_QUALIFICATION: ["custom_gate_inquiry_logged"],
	STAGE_QUERIES: [
		"custom_gate_docs_uploaded",
		"custom_gate_deadline_logged",
		"custom_qualified_go_nogo",
	],
	STAGE_PROPOSAL: ["custom_gate_queries_clarified", "custom_gate_scope_locked"],
	STAGE_EVALUATION: ["custom_gate_proposal_sent"],
	STAGE_CLOSURE: ["custom_gate_loi_po_received"],
}


def validate(doc, method=None):
	_set_email_subject_tag(doc)
	_validate_lost_freeze(doc)
	_validate_go_nogo(doc)
	_validate_stage_gates(doc)
	_validate_closure(doc)


def on_update(doc, method=None):
	if doc.name and doc.custom_email_subject_tag != f"[{doc.name}]":
		doc.db_set("custom_email_subject_tag", f"[{doc.name}]", update_modified=False)
	_handle_closure_handoff(doc)
	if doc.opportunity_from == "Customer" and doc.party_name:
		refresh_customer_bid_intelligence(doc.party_name)


def _set_email_subject_tag(doc):
	if doc.name and not doc.is_new():
		doc.custom_email_subject_tag = f"[{doc.name}]"


def _validate_lost_freeze(doc):
	if doc.is_new() or doc.status != "Lost":
		return
	previous = doc.get_doc_before_save()
	if not previous or previous.status != "Lost":
		return
	if previous.sales_stage != doc.sales_stage:
		frappe.throw(
			_("A Lost Opportunity stays in Sales Stage {0}. Lost is a status, not a pipeline stage.").format(
				previous.sales_stage
			)
		)


def _validate_go_nogo(doc):
	if doc.sales_stage != STAGE_QUALIFICATION:
		return
	if doc.custom_qualified_go_nogo == "No" and doc.status != "Lost":
		frappe.throw(
			_(
				"Internal No-Go: set Status to Lost with a Loss Reason. "
				"The Opportunity must remain in Qualification so history shows where the pursuit died."
			)
		)


def _validate_stage_gates(doc):
	if doc.status == "Lost" or doc.is_new():
		return
	previous = doc.get_doc_before_save()
	if not previous or previous.sales_stage == doc.sales_stage:
		return
	if doc.sales_stage not in PIPELINE_STAGES or previous.sales_stage not in PIPELINE_STAGES:
		return
	old_idx = PIPELINE_STAGES.index(previous.sales_stage)
	new_idx = PIPELINE_STAGES.index(doc.sales_stage)
	if new_idx <= old_idx:
		return
	if new_idx > old_idx + 1:
		# Spec allows bypassing irrelevant stages (private vs public tenders).
		return
	for fieldname in STAGE_GATES.get(doc.sales_stage, []):
		value = previous.get(fieldname)
		if fieldname == "custom_qualified_go_nogo" and value != "Yes":
			frappe.throw(_("Complete the Go / No-Go decision with Yes before leaving Qualification."))
		elif fieldname != "custom_qualified_go_nogo" and not value:
			label = previous.meta.get_label(fieldname) if previous.meta.has_field(fieldname) else fieldname
			frappe.throw(_("Complete the previous stage gate before advancing: {0}").format(label))


def _validate_closure(doc):
	if doc.sales_stage != STAGE_CLOSURE or doc.status == "Lost":
		return
	if doc.opportunity_from != "Customer":
		frappe.throw(_("Convert the party to a Customer before moving to Closure (Won)."))
	if not doc.custom_final_negotiated_contract_value:
		frappe.throw(_("Enter Final Negotiated Contract Value before Closure (Won)."))
	if not doc.custom_expected_project_start_date or not doc.custom_expected_project_end_date:
		frappe.throw(_("Enter expected project start and end dates before Closure (Won)."))


def _handle_closure_handoff(doc):
	if doc.sales_stage != STAGE_CLOSURE or doc.status == "Lost":
		return
	if doc.custom_project:
		return
	project_name = create_project_from_opportunity(doc)
	doc.db_set("custom_project", project_name)
	if doc.status != "Converted":
		doc.db_set("status", "Converted")


@frappe.whitelist()
def get_pipeline_stages():
	return PIPELINE_STAGES


@frappe.whitelist()
def link_communication_to_opportunity(opportunity: str, communication: str):
	frappe.has_permission("Opportunity", "write", opportunity, throw=True)
	comm = frappe.get_doc("Communication", communication)
	comm.reference_doctype = "Opportunity"
	comm.reference_name = opportunity
	comm.save(ignore_permissions=True)
	return comm.name
