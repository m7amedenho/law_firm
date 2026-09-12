# Copyright (c) 2026, redtch and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today


class CaseDocument(Document):
	def before_insert(self):
		if not self.uploaded_by:
			self.uploaded_by = frappe.session.user
		if not self.upload_date:
			self.upload_date = today()
		self.is_latest = 1
		self.version = self.get_next_version()

	def after_insert(self):
		self.clear_previous_latest()

	def get_version_group_filters(self):
		return {
			"case": self.case,
			"document_type": self.document_type,
			"title": self.title or "",
		}

	def get_next_version(self):
		last_version = frappe.db.get_value(
			"Case Document", self.get_version_group_filters(), "version", order_by="version desc"
		)
		return (last_version or 0) + 1

	def clear_previous_latest(self):
		frappe.db.set_value(
			"Case Document",
			{**self.get_version_group_filters(), "name": ["!=", self.name]},
			"is_latest",
			0,
		)
