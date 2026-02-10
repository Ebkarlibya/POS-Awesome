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
    conditions = []

    # Apply filters if provided
    if filters.get("item"):
        conditions.append("pri.item_code = %s")
    if filters.get("supplier"):
        conditions.append("pr.supplier = %s")
    if filters.get("warehouse"):
        conditions.append("pri.warehouse = %s")
    if filters.get("from"):
        conditions.append("pr.posting_date >= %s")
    if filters.get("to"):
        conditions.append("pr.posting_date <= %s")
    
    return " AND ".join(conditions), [
        filters.get("item"),
        filters.get("supplier"),
        filters.get("warehouse"),
        filters.get("from"),
        filters.get("to"),
    ]

def get_data(filters):
    data = []
    conditions, values = get_conditions(filters)

    query = f"""
        SELECT 
            pri.item_code AS item_code, 
            item.brand AS brand, 
            pr.supplier AS supplier, 
            pri.warehouse AS warehouse,
            SUM(pri.qty) AS quantity_in
        FROM `tabPurchase Receipt Item` AS pri
        JOIN `tabPurchase Receipt` AS pr ON pri.parent = pr.name
        JOIN `tabItem` AS item ON pri.item_code = item.name
        WHERE pr.docstatus = 1
        {f"AND {conditions}" if conditions else ""}
        GROUP BY pri.item_code, pr.supplier, pri.warehouse
    """
    items = frappe.db.sql(query, [v for v in values if v], as_dict=1)

    for item in items:
        # Fetch available quantity from Bin
        available_qty = frappe.db.sql("""
            SELECT IFNULL(SUM(actual_qty), 0) AS available_qty
            FROM `tabBin`
            WHERE item_code = %s AND warehouse = %s
        """, (item.item_code, item.warehouse), as_dict=1)
        
        available_qty = available_qty[0]["available_qty"] if available_qty else 0

        # Append the data row
        row = [
            item.item_code,
            item.brand,
            item.supplier,
            item.warehouse,
            flt(available_qty),
            item.quantity_in
        ]
        data.append(row)

    return data
