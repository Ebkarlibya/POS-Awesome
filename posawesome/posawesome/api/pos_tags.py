import frappe


@frappe.whitelist(allow_guest=False, methods=['GET'])
def get_pos_tags():
    return frappe.get_all('POS Tag', fields=['tag_name', 'order_weight'])
