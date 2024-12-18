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
    invoices = frappe.db.sql_list("select name from `tabSales Invoice`")
    for invoice in invoices:
        doc = frappe.get_doc("Sales Invoice", invoice)
        enterprise_percent = frappe.get_value("Customer", filters = {"name": doc.customer}, fieldname = "custom_item_enterprise_percent") or None
        print('** Update Sales Invoice: {0}'.format(invoice))
        for item in doc.items:
            print('- Update Item: {0}'.format(item.item_name))
            item_enterprise_rate = item.rate * (enterprise_percent / 100)
            item_enterprise_amount = item.qty * item_enterprise_rate
            
            frappe.db.sql("update `tabSales Invoice Item` set custom_item_enterprise_rate={0}, custom_item_enterprise_amount={1} where parent='{2}' and name='{3}'".format(item_enterprise_rate, item_enterprise_amount, invoice, item.name))

