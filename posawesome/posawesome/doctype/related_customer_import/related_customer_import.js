// Copyright (c) 2024, Youssef Restom and contributors
// For license information, please see license.txt

frappe.ui.form.on('Related Customer Import', {
	customer: function(frm) {
		frm.set_value("output", )
		cur_frm.doc.percent_table = []
		frappe.model.with_doc("Customer", frm.doc.customer, function() {
		    var tabletransfer= frappe.model.get_doc("Customer", frm.doc.customer)
		    frm.refresh_field("percent_table");
		    $.each(tabletransfer.custom_percent_table, function(index, row){
		        var d = frm.add_child("percent_table");
		        d.item_group = row.item_group;
		        d.employee_percentage = row.employee_percentage;
		        d.company_percentage = row.company_percentage;
		        frm.refresh_field("percent_table");
		    });
		})
	},
	download_template: function(frm) {
		window.location.href = '/assets/posawesome/file/Related Customer Template.csv';
	},
	attach_file: function (frm) {
    	frm.set_value("output", )
    },
    get_data: function (frm) {
    	if(frm.doc.attach_file){
    		frm.set_value("employee_overtime_dates", )
    		frm.set_value("total_hours", 0)

            frappe.call({
		        doc: cur_frm.doc,
		        method: "get_monthly_overtime_request_file",
		        callback: function(r) {
		        	frm.set_value('total_hours', r.message)
		            cur_frm.refresh_fields(['employee_overtime_dates']);
		        }
		    });
	    }else{
	    	frappe.throw("من فضلك قم بارفاق ملف أولا.")
	    }
    }
});
