# Copyright (c) 2026, redtch and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"label": _("Case ID"), "fieldname": "name", "fieldtype": "Link", "options": "Law Case", "width": 110},
		{"label": _("Case Title"), "fieldname": "case_title", "fieldtype": "Data", "width": 170},
		{"label": _("Case Number"), "fieldname": "case_number", "fieldtype": "Data", "width": 100},
		{"label": _("Case Year"), "fieldname": "case_year", "fieldtype": "Data", "width": 80},
		{"label": _("Client"), "fieldname": "client_name", "fieldtype": "Data", "width": 150},
		{"label": _("Opponent"), "fieldname": "opponent_name", "fieldtype": "Data", "width": 130},
		{"label": _("Opponent's Lawyer"), "fieldname": "opponent_lawyer", "fieldtype": "Data", "width": 130},
		{"label": _("Case Type"), "fieldname": "case_type", "fieldtype": "Link", "options": "Case Type", "width": 110},
		{"label": _("Court"), "fieldname": "court", "fieldtype": "Link", "options": "Court", "width": 130},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
		{
			"label": _("Assigned Lawyer"),
			"fieldname": "assigned_lawyer_name",
			"fieldtype": "Data",
			"width": 130,
		},
		{"label": _("Total Hearings"), "fieldname": "hearing_count", "fieldtype": "Int", "width": 100},
		{"label": _("Last Hearing Date"), "fieldname": "last_hearing_date", "fieldtype": "Date", "width": 110},
		{"label": _("Last Hearing Status"), "fieldname": "last_hearing_status", "fieldtype": "Data", "width": 110},
		{"label": _("Next Hearing Date"), "fieldname": "next_hearing_date", "fieldtype": "Date", "width": 110},
		{"label": _("Active POA"), "fieldname": "has_active_poa", "fieldtype": "Data", "width": 90},
		{"label": _("Closed On"), "fieldname": "closed_on", "fieldtype": "Date", "width": 100},
	]


def get_data(filters):
	conditions = []
	values = {}

	for field in ("status", "case_type", "court", "assigned_lawyer"):
		if filters.get(field):
			conditions.append(f"lc.{field} = %({field})s")
			values[field] = filters.get(field)

	if filters.get("client"):
		conditions.append("lc.client = %(client)s")
		values["client"] = filters.get("client")

	if filters.get("from_date"):
		conditions.append("date(lc.creation) >= %(from_date)s")
		values["from_date"] = filters.get("from_date")

	if filters.get("to_date"):
		conditions.append("date(lc.creation) <= %(to_date)s")
		values["to_date"] = filters.get("to_date")

	condition_str = f"where {' and '.join(conditions)}" if conditions else ""

	return frappe.db.sql(
		f"""
		select
			lc.name,
			lc.case_title,
			lc.case_number,
			lc.case_year,
			cust.customer_name as client_name,
			lc.opponent_name,
			lc.opponent_lawyer,
			lc.case_type,
			lc.court,
			lc.status,
			emp.employee_name as assigned_lawyer_name,
			lc.closed_on,
			(select count(*) from `tabCase Hearing` ch where ch.case = lc.name) as hearing_count,
			(select ch.hearing_date from `tabCase Hearing` ch where ch.case = lc.name
				order by ch.hearing_date desc limit 1) as last_hearing_date,
			(select ch.hearing_status from `tabCase Hearing` ch where ch.case = lc.name
				order by ch.hearing_date desc limit 1) as last_hearing_status,
			(select ch.next_hearing_date from `tabCase Hearing` ch where ch.case = lc.name
				and ch.next_hearing_date is not null
				order by ch.hearing_date desc limit 1) as next_hearing_date,
			(select case when count(*) > 0 then %(yes)s else %(no)s end
				from `tabPower of Attorney` poa
				where poa.client = lc.client and poa.is_active = 1) as has_active_poa
		from `tabLaw Case` lc
		left join `tabCustomer` cust on cust.name = lc.client
		left join `tabEmployee` emp on emp.name = lc.assigned_lawyer
		{condition_str}
		order by lc.creation desc
		""",
		{**values, "yes": _("Yes"), "no": _("No")},
		as_dict=1,
	)
