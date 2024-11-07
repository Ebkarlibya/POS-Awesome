# Copyright (c) 2024, Youssef Restom and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, cstr, flt, nowdate, comma_and, date_diff, getdate, time_diff, time_diff_in_hours

class RelatedCustomer(Document):
    def validate(self):
        self.validate_card_expiry()

    def validate_card_expiry(self):
        if getdate(self.card_expiry_date) < getdate(nowdate()):
            self.enabled=0
            frappe.msgprint(_("The card has expired. Please use a valid card."))
        else:
            self.enabled=1
