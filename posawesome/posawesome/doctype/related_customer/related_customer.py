# Copyright (c) 2024, Youssef Restom and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, cstr, flt, nowdate, comma_and, date_diff, getdate, time_diff, time_diff_in_hours
import random


class RelatedCustomer(Document):
    def validate(self):
        self.validate_card_expiry()

    def validate_card_expiry(self):
        if self.enabled==0:
            self.enabled=0
        elif getdate(self.card_expiry_date) < getdate(nowdate()):
            self.enabled=0
            frappe.msgprint(_("The card has expired. Please use a valid card."))
        else:
            self.enabled=1


    def before_save(self):
        if not self.card_number:
            while True:
                # Generate random 10-digit number with prefix "PO"
                random_number = f"PO{random.randint(1000000000, 9999999999)}"
                
                # Check if this card_number already exists
                existing = frappe.db.exists("Related Customer", {"card_number": random_number})
                
                # If not exists, assign it to card_number and break the loop
                if not existing:
                    self.card_number = random_number
                    break
