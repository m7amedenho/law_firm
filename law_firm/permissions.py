# Copyright (c) 2026, redtch and contributors
# For license information, please see license.txt

"""Keeps a Lawyer's User Permission (Employee -> their own record) in sync,
so that they only see Law Case / Case Hearing / Case Document rows where
`assigned_lawyer` matches them (frappe applies this automatically to any
Link field pointing at Employee once the User Permission exists)."""

import frappe


def sync_employee_user_permission(doc, method=None):
	if not doc.user_id:
		remove_stale_permissions_for_employee(doc.name)
		return

	if "Lawyer" not in frappe.get_roles(doc.user_id):
		frappe.db.delete(
			"User Permission",
			{"user": doc.user_id, "allow": "Employee", "for_value": doc.name},
		)
		return

	existing = frappe.db.exists(
		"User Permission",
		{"user": doc.user_id, "allow": "Employee", "for_value": doc.name},
	)
	if existing:
		return

	frappe.get_doc(
		{
			"doctype": "User Permission",
			"user": doc.user_id,
			"allow": "Employee",
			"for_value": doc.name,
			"apply_to_all_doctypes": 1,
		}
	).insert(ignore_permissions=True)


def remove_stale_permissions_for_employee(employee):
	frappe.db.delete("User Permission", {"allow": "Employee", "for_value": employee})


def sync_all_lawyer_permissions():
	"""Fallback reconciliation, run daily in case an Employee/User change was missed."""
	lawyer_users = frappe.get_all(
		"Has Role", filters={"role": "Lawyer", "parenttype": "User"}, pluck="parent"
	)
	employees = frappe.get_all(
		"Employee", filters={"user_id": ["in", lawyer_users or [""]]}, fields=["name", "user_id"]
	)
	for employee in employees:
		sync_employee_user_permission(frappe._dict(employee))
