import frappe

@frappe.whitelist()
def get_additional_item_descriptions(item_code: str):
    additional_item_descriptions = frappe.get_all(
        "POS Additional Item Description Table",
        fields=["description"],
        filters={"parent": item_code}    
    )

    return additional_item_descriptions

@frappe.whitelist()
def get_restaurant_tables():
    tables =  frappe.get_all(
        "POS Restaurant Table",
        order_by="table_number desc"
    )

    return tables