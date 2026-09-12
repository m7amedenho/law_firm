# Copyright (c) 2026, redtch and contributors
# For license information, please see license.txt

import json

import frappe
from frappe import _
from frappe.utils import today

FEE_REQUEST_ROLES = ["Legal Admin", "Law Firm Partner"]


@frappe.whitelist()
def request_legal_fees(law_case, amount=None, notes=None):
	case = frappe.get_doc("Law Case", law_case)
	case.check_permission("read")

	recipients = frappe.get_all(
		"Has Role",
		filters={"role": ["in", FEE_REQUEST_ROLES], "parenttype": "User"},
		pluck="parent",
	)
	recipients = sorted({user for user in recipients if user not in ("Administrator", frappe.session.user)})

	if not recipients:
		frappe.throw(
			_("No Legal Admin or Law Firm Partner user was found to send the fee request to.")
		)

	description = _("Legal fee request for case {0} ({1})").format(case.case_title, case.name)
	if amount:
		description += "\n" + _("Requested amount: {0}").format(amount)
	if notes:
		description += "\n" + notes

	from frappe.desk.form.assign_to import add as assign_to

	assign_to(
		{
			"assign_to": json.dumps(recipients),
			"doctype": "Law Case",
			"name": case.name,
			"description": description,
		}
	)

	return {"notified": recipients}


@frappe.whitelist()
def close_case(law_case, closure_notes=None):
	case = frappe.get_doc("Law Case", law_case)
	case.check_permission("write")

	case.status = "منتهية"
	case.closed_on = today()
	if closure_notes:
		case.closure_notes = closure_notes
	case.save()

	return {"status": case.status, "closed_on": case.closed_on}
