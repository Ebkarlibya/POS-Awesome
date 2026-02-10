// Copyright (c) 2024, Youssef Restom and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Administrative File Report"] = {
	"filters": [
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee"
		}
	]
};