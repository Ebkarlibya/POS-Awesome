# Copyright (c) 2023, Youssef Restom and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ETMSPOSWarrantyPrintTemplate(Document):
	def validate(self):
		if not frappe.db.exists("Print Format", self.template_name):
			warranty_print = frappe.new_doc("Print Format")
			warranty_print.update(
				{
					"doc_type": "Sales Invoice",
					"standard": "No",
					"custom_format": 1,
					"print_format_type": "Jinja",
					"name": self.template_name,
				}
			)
		else:
			warranty_print = frappe.get_doc("Print Format", self.template_name)

		warranty_print.html = f"""
<style>
	.print-format {{
		padding: 0px;
	}}
	@media screen {{
		.print-format {{
			padding: 0in;
		}}
	}}
</style>
<div style="position: relative; top: 0cm">
	<div style="width: {self.card_width}cm; height: {self.card_height}cm;">
		
		<span style="top: 2cm; left:2cm;
			position: absolute; display: block; width: 2cm;
			line-height:0.2cm; word-wrap: break-word;">
				{frappe.utils.money_in_words(20)}
		</span>

	</div>
</div>
		""" 
		# % {
		# 	"starting_position_from_top_edge": doc.starting_position_from_top_edge
		# 	if doc.warranty_size == "A4"
		# 	else 0.0,
		# 	"warranty_width": doc.warranty_width,
		# 	"warranty_height": doc.warranty_height,
		# 	"acc_pay_dist_from_top_edge": doc.acc_pay_dist_from_top_edge,
		# 	"acc_pay_dist_from_left_edge": doc.acc_pay_dist_from_left_edge,
		# 	"message_to_show": doc.message_to_show if doc.message_to_show else _("Account Pay Only"),
		# 	"date_dist_from_top_edge": doc.date_dist_from_top_edge,
		# 	"date_dist_from_left_edge": doc.date_dist_from_left_edge,
		# 	"acc_no_dist_from_top_edge": doc.acc_no_dist_from_top_edge,
		# 	"acc_no_dist_from_left_edge": doc.acc_no_dist_from_left_edge,
		# 	"payer_name_from_top_edge": doc.payer_name_from_top_edge,
		# 	"payer_name_from_left_edge": doc.payer_name_from_left_edge,
		# 	"amt_in_words_from_top_edge": doc.amt_in_words_from_top_edge,
		# 	"amt_in_words_from_left_edge": doc.amt_in_words_from_left_edge,
		# 	"amt_in_word_width": doc.amt_in_word_width,
		# 	"amt_in_words_line_spacing": doc.amt_in_words_line_spacing,
		# 	"amt_in_figures_from_top_edge": doc.amt_in_figures_from_top_edge,
		# 	"amt_in_figures_from_left_edge": doc.amt_in_figures_from_left_edge,
		# 	"signatory_from_top_edge": doc.signatory_from_top_edge,
		# 	"signatory_from_left_edge": doc.signatory_from_left_edge,
		# }

		warranty_print.save(ignore_permissions=True)

		# frappe.db.set_value("warranty Print Template", self.template_name, "has_print_format", 1)

		return warranty_print