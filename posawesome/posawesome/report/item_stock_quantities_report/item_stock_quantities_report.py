# Copyright (c) 2024, Youssef Restom and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data

def get_columns(filters):
	return [
		_("Item") + ":Link/Item:150",
		_("Brand") + ":Link/Brand:150",
		_("Supplier") + ":Link/Supplier:150",
		_("Available Qty") + "::150",
		_("Quantity In") + "::150",
		]


def get_conditions(filters):
	conditions = ""

	if filters.get("item"): conditions += " and item.name= '{0}' ".format(filters.get("item"))
	if filters.get("brand"): conditions += " and item.brand= '{0}' ".format(filters.get("brand"))
	if filters.get("supplier"): conditions += " and sup.supplier= '{0}' ".format(filters.get("supplier"))
	# if filters.get("start_date") and filters.get("end_date"):
	# 	conditions += "and start_date = '{0}' and end_date = '{1}' ".format(filters.get("start_date"), filters.get("end_date"))

	return conditions


def get_data(filters):
	data=[]
	conditions = get_conditions(filters)
	items=frappe.db.sql("""select item.name as name, item.brand as brand, sup.supplier as supplier from `tabItem` as item join `tabItem Supplier` as sup on item.name=sup.parent where 1=1 {0}""".format(conditions),as_dict=1)

	for item in items:
		doc = frappe.get_doc("Item", item.name)
		row = [
			item.name,
			item.brand,
			item.supplier,
			0,
			0
		]
		data.append(row)

	return data

