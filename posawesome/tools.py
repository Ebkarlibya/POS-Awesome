# -*- coding:utf-8 -*-
# encoding: utf-8

# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import frappe, os
from frappe.model.document import Document
from frappe.utils import get_site_base_path
from frappe.utils.data import flt, nowdate, getdate, cint
from frappe.utils import cint, cstr, flt, nowdate, comma_and, date_diff, getdate


def calculate_invoices_enterprise_rate():
    count=0
    invoices = frappe.db.sql_list("select name from `tabSales Invoice`")
    for invoice in invoices:
        print(count)
        doc = frappe.get_doc("Sales Invoice", invoice)
        enterprise_percent = frappe.get_value("Customer", filters = {"name": doc.customer}, fieldname = "custom_item_enterprise_percent") or None
        
        total_enterprise_amount = 0.0
        if enterprise_percent:
            print('** Update Sales Invoice: {0}'.format(invoice))
            for item in doc.items:
                print('- Update Item: {0}'.format(item.item_name))
                item_enterprise_rate = item.rate + (item.rate * (enterprise_percent / 100))
                item_enterprise_amount = item.qty * item_enterprise_rate
                
                frappe.db.sql("update `tabSales Invoice Item` set custom_item_enterprise_rate={0}, custom_item_enterprise_amount={1} where parent='{2}' and name='{3}'".format(item_enterprise_rate, item_enterprise_amount, invoice, item.name))

                total_enterprise_amount+=item_enterprise_amount
        count+=1
        frappe.db.sql("update `tabSales Invoice` set custom_total_enterprise_amount={0} where name='{1}'".format(total_enterprise_amount, invoice))


def check_pos_profiles_for_default():
    """
    Check if all POS Profiles have at least one default payment method checked.
    """
    # Fetch all POS Profiles
    pos_profiles = frappe.get_all("POS Profile", fields=["name"])

    # Initialize a list to store profiles without a default payment method
    profiles_without_default = []

    for profile in pos_profiles:
        # Get the child table entries for the current POS Profile
        payments = frappe.get_all(
            "POS Payment Method",
            filters={"parent": profile.name, "parenttype": "POS Profile"},
            fields=["default"]
        )

        # Check if at least one payment method has default=True
        if not any(payment.get("default") for payment in payments):
            profiles_without_default.append(profile.name)

    if profiles_without_default:
        return {
            "status": "failure",
            "message": "Some POS Profiles do not have a default payment method.",
            "profiles": profiles_without_default,
        }

    return {
        "status": "success",
        "message": "All POS Profiles have at least one default payment method.",
    }
    