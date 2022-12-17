// Copyright (c) 20201 Youssef Restom and contributors
// For license information, please see license.txt

frappe.ui.form.on('POS Profile', {
    setup: function (frm) {
        frm.set_query("posa_cash_mode_of_payment", function (doc) {
            return {
                filters: { 'type': 'Cash' }
            };
        });
    },
    validate: function(frm) {
        if(frm.doc.posa_enable_pos_additional_item_description === 1 && !frm.doc.posa_display_additional_notes) {
            frappe.throw('Please Check "Display Additional Notes" first.');
        }
    }
});