# Copyright (c) 2026, redtch and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today


class PowerofAttorney(Document):
	def validate(self):
		if self.expiry_date and getdate(self.expiry_date) < getdate(today()):
			self.is_active = 0
