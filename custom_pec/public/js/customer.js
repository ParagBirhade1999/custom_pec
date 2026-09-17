frappe.ui.form.on("Customer", {
	refresh(frm) {
		const stats = (frm.doc.__onload && frm.doc.__onload.pec_bid_intelligence) || {};
		const html = `
			<div class="pec-bid-intelligence" style="padding: 8px 0;">
				<p><b>${__("Total Inquiries / Projects Received")}:</b> ${stats.total ?? frm.doc.custom_total_inquiries ?? 0}</p>
				<p><b>${__("Won")}:</b> ${stats.won ?? frm.doc.custom_projects_won ?? 0}</p>
				<p><b>${__("Lost")}:</b> ${stats.lost ?? frm.doc.custom_projects_lost ?? 0}</p>
				<p><b>${__("Cold")}:</b> ${stats.cold ?? frm.doc.custom_projects_cold ?? 0}</p>
				<p><b>${__("Active Bids")}:</b> ${stats.active ?? frm.doc.custom_active_bids ?? 0}</p>
			</div>`;
		if (frm.fields_dict.custom_account_intelligence_html) {
			frm.fields_dict.custom_account_intelligence_html.$wrapper.html(html);
		}
	},
});
