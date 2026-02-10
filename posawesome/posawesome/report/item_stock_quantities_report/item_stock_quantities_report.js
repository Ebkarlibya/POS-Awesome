// Copyright (c) 2024, Youssef Restom and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Stock Quantities Report"] = {
	"filters": [
		{
			"fieldname":"item",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item"
		},
		{
			"fieldname":"warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse"
		},
		{
			"fieldname":"supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier"
		},
		{
			"fieldname":"from",
			"label": __("From"),
			"fieldtype": "Date"
		},
		{
			"fieldname":"to",
			"label": __("To"),
			"fieldtype": "Date"
		}
	]
};
