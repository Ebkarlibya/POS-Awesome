// Copyright (c) 2023, Youssef Restom and contributors
// For license information, please see license.txt

frappe.ui.form.on('ETMS POS Warranty Print Template', {
	refresh: function(frm) {
		if(!frm.doc.__islocal) {
			frm.add_custom_button(frm.doc.has_print_format?__("Update Print Format"):__("Create Print Format"),
				function() {
					frappe.call({
						method: "posawesome.doctype.etms_pos_warranty_print_template.create_or_update_warranty_print_format.",
						args:{
							"template_name": frm.doc.name
						},
						callback: function(r) {
							if (!r.exe && !frm.doc.has_print_format) {
								var doc = frappe.model.sync(r.message);
								frappe.set_route("Form", r.message.doctype, r.message.name);
							}
							else {
								frappe.msgprint(__("Print settings updated in respective print format"))
							}
						}
					})
				}).addClass("btn-primary");

			$(frm.fields_dict.warranty_print_preview.wrapper).empty()


			var template = '<div style="position: relative; overflow-x: scroll; border: solid 1px gray;">\
				<div id="cheque_preview" style="width: {{ card_width }}cm; \
					height: {{ card_height }}cm;\
					background-repeat: no-repeat;\
					background-size: cover;\
					border: solid 1px gray;\">\
					<span style="top: 0cm;\
						left: 0cm;\
						position: absolute;\
						display: block;\
						width: 1cm;\
						line-height: 0.2cm;\
						word-wrap: break-word;"> Amount in Words </span>\
				</div>\
			</div>';

			$(frappe.render(template, frm.doc)).appendTo(frm.fields_dict.warranty_print_preview.wrapper)

			if (frm.doc.scanned_cheque) {
				$(frm.fields_dict.warranty_print_preview.wrapper).find("#cheque_preview").css('background-image', 'url(' + frm.doc.scanned_cheque + ')');
			}
		}
	}
});
