# Copyright (c) 2026, redtch and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import add_days, today


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"label": _("Hearing Date"), "fieldname": "hearing_date", "fieldtype": "Date", "width": 100},
		{"label": _("Hearing Time"), "fieldname": "hearing_time", "fieldtype": "Time", "width": 90},
		{"label": _("Case"), "fieldname": "case", "fieldtype": "Link", "options": "Law Case", "width": 130},
		{"label": _("Case Title"), "fieldname": "case_title", "fieldtype": "Data", "width": 160},
		{"label": _("Case Number"), "fieldname": "case_number", "fieldtype": "Data", "width": 100},
		{"label": _("Client"), "fieldname": "client_name", "fieldtype": "Data", "width": 140},
		{"label": _("Opponent"), "fieldname": "opponent_name", "fieldtype": "Data", "width": 130},
		{"label": _("Case Type"), "fieldname": "case_type", "fieldtype": "Link", "options": "Case Type", "width": 110},
		{"label": _("Court"), "fieldname": "court", "fieldtype": "Link", "options": "Court", "width": 130},
		{"label": _("Court Room"), "fieldname": "court_room", "fieldtype": "Data", "width": 90},
		{"label": _("Judge Name"), "fieldname": "judge_name", "fieldtype": "Data", "width": 110},
		{
			"label": _("Assigned Lawyer"),
			"fieldname": "assigned_lawyer_name",
			"fieldtype": "Data",
			"width": 130,
		},
		{"label": _("Status"), "fieldname": "hearing_status", "fieldtype": "Data", "width": 100},
		{"label": _("Court Decision"), "fieldname": "decisions", "fieldtype": "Data", "width": 160},
		{"label": _("Next Hearing Date"), "fieldname": "next_hearing_date", "fieldtype": "Date", "width": 110},
	]


def get_data(filters):
	conditions = []
	values = {}

	from_date = filters.get("from_date") or today()
	to_date = filters.get("to_date") or add_days(today(), 7)
	conditions.append("ch.hearing_date between %(from_date)s and %(to_date)s")
	values["from_date"] = from_date
	values["to_date"] = to_date

	if filters.get("court"):
		conditions.append("lc.court = %(court)s")
		values["court"] = filters.get("court")

	if filters.get("assigned_lawyer"):
		conditions.append("ch.assigned_lawyer = %(assigned_lawyer)s")
		values["assigned_lawyer"] = filters.get("assigned_lawyer")

	if filters.get("hearing_status"):
		conditions.append("ch.hearing_status = %(hearing_status)s")
		values["hearing_status"] = filters.get("hearing_status")

	if filters.get("case"):
		conditions.append("ch.case = %(case)s")
		values["case"] = filters.get("case")

	condition_str = " and ".join(conditions)

	return frappe.db.sql(
		f"""
		select
			ch.hearing_date,
			ch.hearing_time,
			ch.case,
			lc.case_title,
			lc.case_number,
			cust.customer_name as client_name,
			lc.opponent_name,
			lc.case_type,
			lc.court,
			ch.court_room,
			ch.judge_name,
			emp.employee_name as assigned_lawyer_name,
			ch.hearing_status,
			ch.decisions,
			ch.next_hearing_date
		from `tabCase Hearing` ch
		left join `tabLaw Case` lc on lc.name = ch.case
		left join `tabCustomer` cust on cust.name = lc.client
		left join `tabEmployee` emp on emp.name = ch.assigned_lawyer
		where {condition_str}
		order by ch.hearing_date asc, ch.hearing_time asc
		""",
		values,
		as_dict=1,
	)
