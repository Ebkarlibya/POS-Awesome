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
			"fieldname":"brand",
			"label": __("Brand"),
			"fieldtype": "Link",
			"options": "Brand"
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
			"fieldname":"start_date",
			"label": __("Start Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname":"end_date",
			"label": __("End Date"),
			"fieldtype": "Date"
		}
	]
};
