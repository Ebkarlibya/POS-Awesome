// Copyright (c) 2024, Youssef Restom and contributors
// For license information, please see license.txt

frappe.ui.form.on('Related Customer', {
    validate(frm) {
        let item_group_counts = {};
        let duplicate_item_groups = {};

        frm.doc.percent_table.forEach((row, index) => {
            if (item_group_counts[row.item_group]) {
                duplicate_item_groups[row.item_group] = 
                    (duplicate_item_groups[row.item_group] || [item_group_counts[row.item_group]]).concat(index + 1);
            } else {
                item_group_counts[row.item_group] = index + 1;
            }
        });

        if (Object.keys(duplicate_item_groups).length > 0) {
            let message = Object.entries(duplicate_item_groups)
                .map(([group, lines]) => `Item Group <b>${group}</b> is duplicated in lines: ${lines.join(", ")}`)
                .join("<br>");
            frappe.msgprint(message);
            frappe.validated = false;
        }
    },
    parent_customer(frm) {
    	frm.set_value("percent_table",)
    	if(frm.doc.parent_customer){
			frappe.model.with_doc("Customer", frm.doc.parent_customer, function() {
			    var tabletransfer= frappe.model.get_doc("Customer", frm.doc.parent_customer)
			    $.each(tabletransfer.custom_percent_table, function(index, row){
			        var d = frm.add_child("percent_table");
			        d.item_group = row.item_group;
			        d.employee_percentage = row.employee_percentage;
			        d.company_percentage = row.company_percentage;
			        frm.refresh_field("percent_table");
			    });
			})
    	}
    }
});


frappe.ui.form.on('Percent Table', {
    employee_percentage(frm, cdt, cdn) {
        var doc = locals[cdt][cdn];
        if(doc.employee_percentage){
            frappe.model.set_value(cdt, cdn, "company_percentage", 100-doc.employee_percentage);
        }
    },
    company_percentage(frm, cdt, cdn) {
        var doc = locals[cdt][cdn];
        if(doc.company_percentage){
            frappe.model.set_value(cdt, cdn, "employee_percentage", 100-doc.company_percentage);
        }
    }
})

