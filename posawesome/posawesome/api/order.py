import frappe
import json


@frappe.whitelist()
def get_orders_list():
    try:
        term_sql_cond = ""
        include_drafts = json.loads(frappe.form_dict["include_drafts"])

        docstatuses = ""

        if include_drafts:
            docstatuses = "(0,1)"
        else:
            docstatuses = "(1)"

        if "term" in frappe.form_dict and len(frappe.form_dict["term"]) > 0:
            escaped_input = frappe.db.escape(f"%{frappe.form_dict['term']}%")
            term_sql_cond = f"""
                and name like {escaped_input}
                or grand_total like {escaped_input}
            """
            # cond_filters["name"] = ["like", f"%{frappe.form_dict['term']}%"]
            # cond_filters["posa_pos_restaurant_table"] = ["like", f"%{frappe.form_dict['term']}%"]

        orders = frappe.db.sql(
            f"""
                select name, customer, delivery_date, grand_total, transaction_date,
                currency, docstatus
                from `tabSales Order`
                    
                where docstatus in {docstatuses}
                {term_sql_cond}
                order by creation desc
                limit 20
            """,
            as_dict=True
        )

        # for order in orders:
        #     si_items = frappe.get_all(
        #         "Sales Invoice Item",
        #         fields=["posa_has_warranty"],
        #         filters={"parent": invoice["name"]}
        #     )
        #     for si_item in si_items:
        #         if (si_item["posa_has_warranty"]):
        #             invoice["posa_has_warranty"] = "Yes"
        return orders
    except:
        tb = frappe.get_traceback()
        print(frappe.get_traceback())


@frappe.whitelist()
def get_order_items():
    try:
        order = json.loads(frappe.form_dict["order"])
        items = frappe.db.sql(
            f"""
                SELECT item_code, qty, rate, amount
                FROM `tabSales Order Item`
                    
                WHERE parent = {frappe.db.escape(f"{order['name']}")}
                order by creation desc
                limit 20
            """,
            as_dict=True
        )
        return items
    except:
        tb = frappe.get_traceback()
        print(frappe.get_traceback())
