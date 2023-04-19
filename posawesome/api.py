import frappe

@frappe.whitelist()
def get_additional_item_descriptions(item_code: str):
    try:
        additional_item_descriptions = frappe.get_all(
            "POS Additional Item Description Table",
            fields=["description"],
            filters={"parent": item_code}    
        )

        return additional_item_descriptions
    except:
        tb = frappe.get_traceback()
        print(frappe.get_traceback())

@frappe.whitelist()
def get_restaurant_tables():
    try:
        tables =  frappe.get_all(
            "POS Restaurant Table"
        )
        sorted(tables, key=lambda x: x["name"], reverse=True)
        return tables
    except:
        tb = frappe.get_traceback()
        print(frappe.get_traceback())

@frappe.whitelist()
def get_companies_pos_offers_names(offer_name: str, exclude_company: str):
    try:
        new_pos_offer_names = []

        companies = frappe.get_all(
            "Company",
            fields = ["name", "abbr"],
            filters={
                "name": ["!=", exclude_company]
            }
        )
        
        for company in companies:
            new_pos_offer_names.append(
                {
                    "company": company["name"],
                    "suggested_offer_name": f"""{company["abbr"]}-{offer_name}"""
                }
            )

        return new_pos_offer_names
    except:
        tb = frappe.get_traceback()
        print(frappe.get_traceback())

@frappe.whitelist()
def make_multi_company_pos_offers(current_pos_offer_name: str, for_companies):
    try:
        for_companies = frappe.parse_json(for_companies)
        created_offers = []
        current_offer = None

        for companyies_table in for_companies:
            pos_offer = frappe.get_doc(
                "POS Offer",
                current_pos_offer_name
            )


            # if pos_offer.name == current_pos_offer_name:
            #     frappe.throw(frappe._(f"POS Offer: ({pos_offer_new_name}) already exist for Company: ({pos_offer.company})"), "POS Offers Multi Company Creator")
            pos_offer.is_created_from_pos_offer = 1
            pos_offer.company = companyies_table["company"]
            if frappe.db.exists("POS Offer", companyies_table["suggested_offer_name"]):
                frappe.db.rollback()
                return { "status": "fail", "data": f"POS Offer ({companyies_table['suggested_offer_name']}) Already exist"}

            pos_offer.insert(set_name=companyies_table["suggested_offer_name"])
            # pos_offer.save()
            created_offers.append(companyies_table["suggested_offer_name"])

        frappe.db.commit()
        return { "status": "success", "data": f"Successfully Created {len(created_offers)} POS Offers"}

    except:
        print(frappe.get_traceback())
        

@frappe.whitelist()
def get_pos_tags():
    try:
        tags =  frappe.get_all(
            "POS Tag",
            fields=["name", "order_weight"],
            order_by="order_weight asc"
        )
        return tags
    except:
        tb = frappe.get_traceback()
        print(frappe.get_traceback())

@frappe.whitelist()
def get_invoices_list():
    try:
        term_sql_cond = ""

        if "term" in frappe.form_dict and len(frappe.form_dict["term"]) > 0:
            escaped_input = frappe.db.escape(f"%{frappe.form_dict['term']}%")
            term_sql_cond = f"""
                and name like {escaped_input}
                or posa_pos_restaurant_table like {escaped_input}
                or grand_total like {escaped_input}
            """
            # cond_filters["name"] = ["like", f"%{frappe.form_dict['term']}%"]
            # cond_filters["posa_pos_restaurant_table"] = ["like", f"%{frappe.form_dict['term']}%"]

        invoices = frappe.db.sql(
            f"""
                select name, customer, posting_date, grand_total, posa_pos_restaurant_table,
                docstatus
                from `tabSales Invoice`
                    
                where docstatus in (1)
                and is_return = 0
                {term_sql_cond}
                order by creation desc
                limit 20
            """,
            as_dict=True,
            debug=True
        )
        return invoices
    except:
        tb = frappe.get_traceback()
        print(frappe.get_traceback())

@frappe.whitelist()
def check_connection():
    import requests

    try:
        res = requests.get("https://google.com")

        return True
    
    except:
        print(frappe.get_traceback())
        return False