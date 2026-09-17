frappe.ui.form.on("Opportunity", {
	refresh(frm) {
		frm.trigger("pec_apply_lost_freeze");
		frm.trigger("pec_add_buttons");
	},

	sales_stage(frm) {
		frm.trigger("pec_stage_hint");
	},

	custom_subcontract_required(frm) {
		frm.refresh_field("custom_subcontracted_scope");
	},

	custom_evaluation_sub_stage(frm) {
		frm.refresh_field("custom_commercial_rank");
	},

	custom_qualified_go_nogo(frm) {
		if (frm.doc.custom_qualified_go_nogo === "No" && frm.doc.status !== "Lost") {
			frappe.msgprint({
				title: __("Mark as Lost"),
				indicator: "red",
				message: __(
					"No-Go keeps this Opportunity in Qualification. Use Set as Lost and pick a Loss Reason so history shows where the pursuit died."
				),
			});
		}
	},

	pec_apply_lost_freeze(frm) {
		const lost = frm.doc.status === "Lost";
		frm.set_df_property("sales_stage", "read_only", lost ? 1 : 0);
		if (lost) {
			frm.dashboard.set_headline_alert(
				__("Lost in stage {0}. Pipeline stage is frozen.", [frm.doc.sales_stage || ""]),
				"red"
			);
		}
	},

	pec_add_buttons(frm) {
		if (frm.is_new()) {
			return;
		}
		frm.add_custom_button(__("Link Orphan Email"), () => pec_link_orphan_email(frm), __("PEC"));
		if (frm.doc.custom_project) {
			frm.add_custom_button(__("Open Project"), () => {
				frappe.set_route("Form", "Project", frm.doc.custom_project);
			}, __("PEC"));
		}
	},

	pec_stage_hint(frm) {
		if (!frm.doc.sales_stage) {
			return;
		}
		frm.dashboard.clear_headline();
		frm.dashboard.set_headline(
			__("EPC Pipeline: {0}. Stage fields are on the EPC Pipeline tab.", [frm.doc.sales_stage])
		);
	},
});

function pec_link_orphan_email(frm) {
	const d = new frappe.ui.Dialog({
		title: __("Link email to this Opportunity"),
		fields: [
			{
				fieldname: "communication",
				fieldtype: "Link",
				options: "Communication",
				label: __("Communication"),
				reqd: 1,
				get_query() {
					return {
						filters: {
							communication_type: "Communication",
							reference_name: ["in", ["", null]],
						},
					};
				},
			},
		],
		primary_action_label: __("Link"),
		primary_action(values) {
			frappe.call({
				method: "custom_pec.crm.opportunity.link_communication_to_opportunity",
				args: {
					opportunity: frm.doc.name,
					communication: values.communication,
				},
				freeze: true,
				callback() {
					d.hide();
					frappe.show_alert({ message: __("Email linked"), indicator: "green" });
					frm.reload_doc();
				},
			});
		},
	});
	d.show();
}
