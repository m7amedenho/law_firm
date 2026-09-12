# Copyright (c) 2026, redtch and contributors
# For license information, please see license.txt

import frappe
from frappe import _

STATUSES = ["متداولة", "محجوزة للحكم", "صدر حكم", "مستأنفة", "منتهية"]


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	columns = [
		{"label": _("Case Type"), "fieldname": "case_type", "fieldtype": "Data", "width": 160},
	]
	for status in STATUSES:
		columns.append(
			{"label": status, "fieldname": frappe.scrub(status), "fieldtype": "Int", "width": 120}
		)
	columns.append({"label": _("Total"), "fieldname": "total", "fieldtype": "Int", "width": 100})
	return columns


def get_data(filters):
	conditions = {}
	if filters.get("case_type"):
		conditions["case_type"] = filters.get("case_type")
	if filters.get("assigned_lawyer"):
		conditions["assigned_lawyer"] = filters.get("assigned_lawyer")

	cases = frappe.get_all(
		"Law Case", filters=conditions, fields=["case_type", "status"]
	)

	summary = {}
	for case in cases:
		case_type = case.case_type or _("Not Set")
		row = summary.setdefault(case_type, {frappe.scrub(status): 0 for status in STATUSES})
		status_key = frappe.scrub(case.status) if case.status in STATUSES else None
		if status_key:
			row[status_key] += 1

	data = []
	for case_type, counts in summary.items():
		row = {"case_type": case_type, **counts}
		row["total"] = sum(counts.values())
		data.append(row)

	data.sort(key=lambda r: r["case_type"])
	return data
