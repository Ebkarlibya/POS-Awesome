frappe.ui.form.on('Item', {
    refresh: function(frm) {
        frm.set_df_property("posa_force_selecting_only_one_option", "hidden", 1);
    }
});