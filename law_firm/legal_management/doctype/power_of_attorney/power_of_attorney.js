// Copyright (c) 2026, redtch and contributors
// For license information, please see license.txt

frappe.ui.form.on("Power of Attorney", {
	setup(frm) {
		frm.set_query("authorized_signatory", () => ({
			query: "frappe.contacts.doctype.contact.contact.contact_query",
			filters: {
				link_doctype: "Customer",
				link_name: frm.doc.client,
			},
		}));
	},

	client(frm) {
		frm.set_value("authorized_signatory", "");
	},
});
