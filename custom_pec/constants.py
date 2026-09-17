"""PEW Engineering CRM pipeline constants. Do not change ERPNext core stage names here."""

STAGE_COLD = "Cold"
STAGE_INQUIRY = "Inquiry / Tender"
STAGE_QUALIFICATION = "Qualification (Go / No-Go)"
STAGE_QUERIES = "Queries & Clarifications"
STAGE_PROPOSAL = "Proposal Submitted"
STAGE_EVALUATION = "Evaluation"
STAGE_CLOSURE = "Closure (Won)"

PIPELINE_STAGES = [
	STAGE_COLD,
	STAGE_INQUIRY,
	STAGE_QUALIFICATION,
	STAGE_QUERIES,
	STAGE_PROPOSAL,
	STAGE_EVALUATION,
	STAGE_CLOSURE,
]

LOST_REASONS = [
	"Outside Domain",
	"Internal No-Go/Lack of Bandwidth",
	"Unacceptable Commercial Terms",
	"Technical Disqualification",
	"Outbid on Price",
	"Client Cancelled Project",
	"Client Went Cold",
]

COMMERCIAL_ATTACH_FIELDS = {
	"custom_final_proposal_upload",
	"custom_work_order_po_upload",
}

ACTIVE_BID_STAGES = {
	STAGE_INQUIRY,
	STAGE_QUALIFICATION,
	STAGE_QUERIES,
	STAGE_PROPOSAL,
	STAGE_EVALUATION,
}
