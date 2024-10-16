# Copyright (c) 2024, Youssef Restom and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class RelatedCustomer(Document):
	def validate(self):
		pass
		# if self.employee_percentage+self.company_percentage!=100.0:
		# 	frappe.throw("Total employee and company percentage must be 100%")
