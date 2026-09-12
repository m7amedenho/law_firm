// Copyright (c) 2026, redtch and contributors
// For license information, please see license.txt

frappe.ui.form.on("Law Case", {
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

	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		frm.add_custom_button(
			__("طلب أتعاب محاماة"),
			() => request_legal_fees(frm),
			__("إجراءات")
		);

		frm.add_custom_button(
			__("إنشاء فاتورة أتعاب"),
			() => {
				frappe.new_doc("Sales Invoice", {
					customer: frm.doc.client,
					law_case: frm.doc.name,
				});
			},
			__("إجراءات")
		);

		if (frm.doc.status !== "منتهية") {
			frm.add_custom_button(
				__("إغلاق القضية"),
				() => close_case(frm),
				__("إجراءات")
			);
		}
	},
});

function request_legal_fees(frm) {
	frappe.prompt(
		[
			{ fieldname: "amount", label: __("المبلغ المطلوب"), fieldtype: "Currency" },
			{ fieldname: "notes", label: __("ملاحظات"), fieldtype: "Small Text" },
		],
		(values) => {
			frappe.call({
				method: "law_firm.api.request_legal_fees",
				args: {
					law_case: frm.doc.name,
					amount: values.amount,
					notes: values.notes,
				},
				freeze: true,
				callback: () => {
					frappe.show_alert({ message: __("تم إرسال طلب الأتعاب"), indicator: "green" });
				},
			});
		},
		__("طلب أتعاب محاماة"),
		__("إرسال")
	);
}

function close_case(frm) {
	frappe.prompt(
		[{ fieldname: "closure_notes", label: __("ملاحظات الإغلاق"), fieldtype: "Small Text" }],
		(values) => {
			frappe.confirm(__("هل أنت متأكد من إغلاق القضية؟"), () => {
				frappe.call({
					method: "law_firm.api.close_case",
					args: {
						law_case: frm.doc.name,
						closure_notes: values.closure_notes,
					},
					freeze: true,
					callback: () => {
						frappe.show_alert({ message: __("تم إغلاق القضية"), indicator: "green" });
						frm.reload_doc();
					},
				});
			});
		},
		__("إغلاق القضية"),
		__("تأكيد")
	);
}
