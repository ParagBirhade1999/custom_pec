frappe.ui.form.on("Project", {
	refresh(frm) {
		if (frm.doc.custom_handoff_status === "Pending Review") {
			frm.dashboard.set_headline_alert(
				__("Handoff is Pending Review. A manager must set Handoff Status to Live before execution treats this project as released."),
				"orange"
			);
		}
		if (frm.doc.custom_opportunity) {
			frm.add_custom_button(__("Open Opportunity"), () => {
				frappe.set_route("Form", "Opportunity", frm.doc.custom_opportunity);
			});
		}
	},
});

frappe.ui.form.on("Project User", {
	user(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row && !row.view_attachments) {
			frappe.model.set_value(cdt, cdn, "view_attachments", 1);
		}
	},
});
