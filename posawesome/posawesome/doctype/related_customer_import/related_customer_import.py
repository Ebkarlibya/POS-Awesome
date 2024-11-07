# Copyright (c) 2024, Youssef Restom and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from pymysql import MySQLError
from datetime import datetime

class RelatedCustomerImport(Document):
    @frappe.whitelist()
    def import_related_customer_data(self):
        directory_type = 'public'
        if '/private/' in self.attach_file:
            directory_type = 'private'

        from frappe.utils.csvutils import read_csv_content
        file_name = self.attach_file.split('/')[-1]
        file_path = frappe.get_site_path(directory_type, 'files', file_name)

        if not self.percent_table:
            return 'Customer: {0}, has no percent table data!'.format(self.customer)

        try:
            with open(file_path, "r") as infile:
                rows = read_csv_content(infile.read())
                i = 0
                for index, row in enumerate(rows):
                    if index!=0:

                        if row[0] and row[1] and row[2] and row[3] and row[4]:
                            if not frappe.db.exists("Related Customer", {"employee_name": row[0], "phone": row[2]}):
                                if row[0]:
                                    try:

                                        try:
                                            card_expiry_date = datetime.strptime(row[4], "%d/%m/%Y").strftime("%Y-%m-%d")
                                        except ValueError:
                                            card_expiry_date = None

                                        doc = frappe.new_doc("Related Customer")
                                        doc.update({
                                            "doctype":"Related Customer",
                                            "employee_name": row[0],
                                            "employee_id": row[1],
                                            "phone": row[2],
                                            "card_number": row[3],
                                            "card_expiry_date": card_expiry_date,
                                            "designation": row[5],
                                            "parent_customer": self.customer
                                        })

                                        for percent_table in self.percent_table:
                                            doc.append('percent_table',{
                                                "doctype": "Percent Table",
                                                "item_group": percent_table.item_group,
                                                "employee_percentage": percent_table.employee_percentage,
                                                "company_percentage": percent_table.company_percentage
                                            })
                                        
                                        doc.save(ignore_permissions=True)
                                        frappe.db.commit()
                                    except MySQLError as e:
                                        if e.args[0] == 1292:
                                            frappe.msgprint("Error!", alert=True, indicator='red')
                                            return f"Incorrect date value: {e.args[1]}"
                                        else:
                                            frappe.msgprint("Error!", alert=True, indicator='red')
                                            return f"Error adding percent table for customer {customer_name}: {e.args[1]}"
                                        continue

                                    i+=1
                                    print(f"- Successfully add related customer: {row[0]}")
                                    frappe.msgprint(f"- Successfully add related customer: {row[0]}", alert=True, indicator='green')
                        else:
                            return "Missing Data!" 
                print('*************')
                frappe.msgprint("Success!", alert=True, indicator='green')
                return f"Total Related Customer added: {i}"
        except Exception as e:
            frappe.msgprint("Error!", alert=True, indicator='red')
            return f"An error occurred: {e}"
            


