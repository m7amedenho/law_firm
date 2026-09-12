# Copyright (c) 2026, redtch and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import add_days, getdate, today


def send_hearing_reminders():
	"""Notify the assigned lawyer about hearings scheduled for tomorrow."""
	tomorrow = add_days(today(), 1)
	hearings = frappe.get_all(
		"Case Hearing",
		filters={"hearing_date": tomorrow, "hearing_status": "مجدولة"},
		fields=["name", "case", "hearing_date", "hearing_time", "court_room", "assigned_lawyer"],
	)

	for hearing in hearings:
		if not hearing.assigned_lawyer:
			continue

		user = frappe.db.get_value("Employee", hearing.assigned_lawyer, "user_id")
		if not user:
			continue

		case_title = frappe.db.get_value("Law Case", hearing.case, "case_title") or hearing.case

		frappe.get_doc(
			{
				"doctype": "Notification Log",
				"subject": frappe._("Hearing tomorrow for case {0}").format(case_title),
				"for_user": user,
				"type": "Alert",
				"document_type": "Case Hearing",
				"document_name": hearing.name,
			}
		).insert(ignore_permissions=True)

		frappe.sendmail(
			recipients=[user],
			subject=frappe._("Reminder: Court Hearing Tomorrow - {0}").format(case_title),
			message=frappe._(
				"You have a hearing scheduled tomorrow ({0}) for case <b>{1}</b>"
				" at court room {2}."
			).format(hearing.hearing_date, case_title, hearing.court_room or "-"),
		)


def send_poa_expiry_alerts():
	"""Notify Legal Admin users about Power of Attorney records expiring in 15 days."""
	target_date = add_days(today(), 15)
	expiring_poas = frappe.get_all(
		"Power of Attorney",
		filters={"expiry_date": target_date, "is_active": 1},
		fields=["name", "poa_number", "client", "expiry_date"],
	)

	if not expiring_poas:
		return

	admin_users = frappe.get_all(
		"Has Role", filters={"role": "Legal Admin", "parenttype": "User"}, pluck="parent"
	)
	if not admin_users:
		return

	for poa in expiring_poas:
		client_name = frappe.db.get_value("Customer", poa.client, "customer_name") or poa.client
		for user in admin_users:
			frappe.get_doc(
				{
					"doctype": "Notification Log",
					"subject": frappe._("POA {0} for {1} expires on {2}").format(
						poa.poa_number or poa.name, client_name, poa.expiry_date
					),
					"for_user": user,
					"type": "Alert",
					"document_type": "Power of Attorney",
					"document_name": poa.name,
				}
			).insert(ignore_permissions=True)


def deactivate_expired_poas():
	"""Flip is_active off for Power of Attorney records that have expired."""
	frappe.db.set_value(
		"Power of Attorney",
		{"expiry_date": ["<", today()], "is_active": 1},
		"is_active",
		0,
	)


def daily():
	send_hearing_reminders()
	send_poa_expiry_alerts()
	deactivate_expired_poas()

	from law_firm.permissions import sync_all_lawyer_permissions

	sync_all_lawyer_permissions()
