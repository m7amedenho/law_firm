# Copyright (c) 2026, redtch and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

# Maps a hearing outcome to the case-level status it should push onto the
# linked Law Case. Only statuses that represent a real milestone are mapped.
HEARING_TO_CASE_STATUS = {
	"حجزت للحكم": "محجوزة للحكم",
	"صدر الحكم": "صدر حكم",
}


class CaseHearing(Document):
	def on_update(self):
		self.sync_case_status()

	def sync_case_status(self):
		new_case_status = HEARING_TO_CASE_STATUS.get(self.hearing_status)
		if not new_case_status or not self.case:
			return

		current_status = frappe.db.get_value("Law Case", self.case, "status")
		if current_status and current_status != new_case_status:
			frappe.db.set_value("Law Case", self.case, "status", new_case_status)
