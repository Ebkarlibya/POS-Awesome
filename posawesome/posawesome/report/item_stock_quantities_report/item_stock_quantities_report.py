# Copyright (c) 2024, Youssef Restom and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
    columns, data = get_columns(filters), get_data(filters)
    return columns, data

def get_columns(filters):
    return [
        _("Item") + ":Link/Item:150",
        _("Brand") + ":Link/Brand:150",
        _("Supplier") + ":Link/Supplier:150",
        _("Warehouse") + ":Link/Warehouse:150",
        _("Available Qty") + "::150",
        _("Quantity In") + "::150",
    ]

def get_conditions(filters):
    conditions = ""

    # Apply filters if provided
    if filters.get("item"): 
        conditions += " AND pri.item_code = '{0}' ".format(filters.get("item"))
    if filters.get("supplier"): 
        conditions += " AND pr.supplier = '{0}' ".format(filters.get("supplier"))
    if filters.get("warehouse"): 
        conditions += " AND pri.warehouse = '{0}' ".format(filters.get("warehouse"))
    if filters.get("from"): 
        conditions += " AND pr.posting_date >= '{0}' ".format(filters.get("from"))
    if filters.get("to"): 
        conditions += " AND pr.posting_date <= '{0}' ".format(filters.get("to"))
    
    return conditions

def get_data(filters):
    data = []
    conditions = get_conditions(filters)

    items = frappe.db.sql("""
        SELECT 
            pri.item_code AS item_code, 
            item.brand AS brand, 
            pr.supplier AS supplier, 
            pri.warehouse AS warehouse,
            SUM(pri.qty) AS quantity_in
        FROM `tabPurchase Receipt Item` AS pri
        JOIN `tabPurchase Receipt` AS pr ON pri.parent = pr.name
        JOIN `tabItem` AS item ON pri.item_code = item.name
        LEFT JOIN `tabBin` AS bin ON pri.item_code = bin.item_code AND pri.warehouse = bin.warehouse
        WHERE pr.docstatus = 1 {0}
        GROUP BY pri.item_code, pr.supplier, pri.warehouse
    """.format(conditions), as_dict=1)

    for item in items:
        available_qty = frappe.db.sql("""
            SELECT IFNULL(SUM(actual_qty), 0) AS available_qty
            FROM `tabBin`
            WHERE item_code = '{0}' AND warehouse = '{1}'
        """.format(item.item_code, item.warehouse), as_dict=1)
        
        available_qty = available_qty and flt(available_qty[0]["available_qty"]) or 0

        row = [
            item.item_code,
            item.brand,
            item.supplier,
            item.warehouse,
            available_qty,
            item.quantity_in
        ]
        data.append(row)

    return data
