# encoding=utf8
# -*- coding: utf-8 -*- u
from __future__ import unicode_literals
from __future__ import division
import frappe
import frappe, os , math
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_site_base_path, cint, cstr, date_diff, flt, formatdate, getdate, get_link_to_form, \
    comma_or, get_fullname, add_years, add_months, add_days, nowdate
from frappe.utils.data import flt, nowdate, getdate, cint, rounded, add_months, add_days, get_last_day
from frappe.utils.password import update_password as _update_password
from frappe.utils import cint, cstr, flt, nowdate, comma_and, date_diff, getdate, formatdate ,get_url
import datetime
import traceback
from datetime import date
from frappe.model.mapper import get_mapped_doc
import sys
from frappe.utils import cstr
from frappe.model.document import Document
import json

from pymysql import MySQLError
from datetime import datetime



@frappe.whitelist(allow_guest=True)
def get_customer_plans(customer):
    plans = frappe.get_all('Customer Plan', 
                           filters={'parent': customer, 'parenttype': 'Customer'},
                           fields=['plan_name', 'plan_percent'])
    
    return plans


def add_related_customer_import_template():
    doc = frappe.get_doc("Related Customer Import")
    doc.download_template = '/posawesome/Related Customer Template.csv'
    doc.flags.ignore_mandatory = True
    doc.save(ignore_permissions=True)



def add_related_customer():
    print('*** Add Related Customer ***')
    from frappe.utils.csvutils import read_csv_content
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'related_customer.csv')
    try:
        with open(file_path, "r") as infile:
            rows = read_csv_content(infile.read())
            i = 0
            for index, row in enumerate(rows):
                if index!=0:
                    if not frappe.db.exists("Customer", {"name": row[5]}):
                        return 'Customer: {0} not exists!'.format(row[5])
                    else:
                        if not frappe.get_doc("Customer", row[5]).custom_percent_table:
                            return 'Customer: {0}, has no percent table data!'.format(row[5])

                    if row[0] and row[1] and row[2] and row[3] and row[4] and row[5]:
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
                                        "parent_customer": row[5],
                                        "designation": row[6]
                                    })

                                    for percent_table in frappe.get_doc("Customer", row[5]).custom_percent_table:
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
                                        print(f"Incorrect date value: {e.args[1]}")
                                    else:
                                        print(f"Error adding percent table for customer {customer_name}: {e.args[1]}")
                                    continue


                                i+=1
                                print(row[0])
                    else:
                        print("Missing Data!")
            print('*************')
            print(f"Total Related Customer added: {i}")
    except Exception as e:
        print(f"An error occurred: {e}")



@frappe.whitelist()
def validate_card_expiry():
    related_customers = frappe.get_all(
        'Related Customer', 
        filters={},
        fields=['name', 'card_expiry_date', 'enabled']
    )
    
    for related_customer in related_customers:
        doc = frappe.get_doc("Related Customer", related_customer['name'])
        if getdate(related_customer['card_expiry_date']) < getdate(nowdate()):
            if related_customer['enabled']==1:
                doc.enabled = 0
                doc.flags.ignore_mandatory = True
                doc.save(ignore_permissions=True)
                print('- Expiry Card for Related Customer: {0}'.format(related_customer['name']))
        else:
            if related_customer['enabled']==0:
                doc.enabled = 1
                doc.flags.ignore_mandatory = True
                doc.save(ignore_permissions=True)
                print('- Card Activated for Related Customer: {0}'.format(related_customer['name']))

                



@frappe.whitelist()
def update_related_customer_percentages(parent_customer):
    # Get the current customer's percent table
    current_customer = frappe.get_doc("Customer", parent_customer)

    if len(current_customer.custom_percent_table) < 1:
        frappe.throw("No Record Found in Percent Table")

    percent_table_data = current_customer.custom_percent_table

    # Find all related customers
    related_customers = frappe.get_all(
        "Related Customer",
        filters={"parent_customer": parent_customer},
        fields=["name"]
    )

    # Initialize a dictionary to count updated related customers by item group
    update_counts = {row.item_group: 0 for row in percent_table_data}

    # Loop through each related customer
    for related_customer in related_customers:
        # Get related customer document
        related_customer_doc = frappe.get_doc("Related Customer", related_customer.name)

        # Track if any changes were made for each item group
        changes_made = False

        # Update the percent_table for matching item groups
        for row in percent_table_data:
            # Check if the item group exists in the related customer's percent_table
            existing_row = next((item for item in related_customer_doc.percent_table if item.item_group == row.item_group), None)

            if existing_row:
                # Update the existing percentages for the item group
                if (existing_row.employee_percentage != row.employee_percentage or 
                    existing_row.company_percentage != row.company_percentage):
                    existing_row.employee_percentage = row.employee_percentage
                    existing_row.company_percentage = row.company_percentage
                    changes_made = True  # Mark that changes were made
                    update_counts[row.item_group] += 1  # Increment count for this item group

        # Save changes to the related customer only if there were updates
        if changes_made:
            related_customer_doc.save()

    return update_counts  # Return the counts of updated related customers by item group



@frappe.whitelist()
def get_employee_percentage(invoice_name):
    invoice_doc = frappe.get_doc("Sales Invoice", invoice_name)

    total_cash = 0

    for item in invoice_doc.items:
        amount = item.rate * item.qty

        if invoice_doc.custom_related_customer:
            employee_percentage = frappe.get_value(
                "Percent Table", 
                filters={
                    "parenttype": 'Related Customer', 
                    "parent": invoice_doc.custom_related_customer, 
                    "item_group": item.item_group
                }, 
                fieldname="employee_percentage"
            ) or 100

        if invoice_doc.custom_plan:
            employee_percentage = frappe.get_value(
                "Plan", 
                filters={
                    "plan_name": invoice_doc.custom_plan
                }, 
                fieldname="plan_percent"
            ) or 100



        total_cash += amount * (employee_percentage / 100)
    
    return total_cash




@frappe.whitelist()
def get_item_percentage_and_amount(customer, related_customer, plan, item):
    
    item = json.loads(item)

    employee_percentage = 0
    company_percentage = 0
    employee_amount = 0
    company_amount = 0

    total_amount = item['rate'] * item['qty']

    if related_customer:
        employee_percentage, company_percentage = frappe.get_value(
            "Percent Table", 
            filters={
                "parenttype": 'Related Customer', 
                "parent": related_customer, 
                "item_group": item['item_group']
            }, 
            fieldname=["employee_percentage", "company_percentage"]
        ) or (100, 0)

    if plan:
        plan_percent = frappe.get_value(
            "Plan", 
            filters={
                "plan_name": plan
            }, 
            fieldname="plan_percent"
        ) or 100

        employee_percentage = plan_percent
        company_percentage = 100 - plan_percent

    employee_amount = total_amount * (employee_percentage / 100)
    company_amount = total_amount * (company_percentage / 100)


    return employee_percentage, company_percentage, employee_amount, company_amount








