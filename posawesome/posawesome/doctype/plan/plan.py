# Copyright (c) 2024, Youssef Restom and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Plan(Document):
    def validate(self):
        self.validate_plan_percent()

    def validate_plan_percent(self):
        if self.plan_percent>100 or self.plan_percent<0:
            frappe.throw("Plan Percent must be between 0 and 100")
