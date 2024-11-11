# encoding: utf-8
# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    columns, data = get_columns(filters), get_data(filters)
    return columns, data

def get_columns(filters):
    return [
        _("Employee") + ":Link/Employee:100",
        _("Employee Name") + "::150",
        _("Passport Photo") + "::150",
        _("National ID Photo") + "::150",
        _("Personal Photos") + "::150",
        _("Graduation Certificate") + "::170",
        _("License to Practice") + "::150",
        _("Work Commencement Document") + "::250",
        _("Employee Card Template") + "::180",
        _("Confidentiality Agreement Template") + "::270",
        _("Shared Vision Statement Template") + "::270",
        _("Health Insurance") + "::150",
        _("Health Certificate") + "::150"
        ]


def get_conditions(filters):
    conditions = ""
    if filters.get("employee"): conditions += " and name = '{0}'".format(filters.get("employee"))
    return conditions


def check_file_exists(employee, document_title):
    exists = frappe.db.exists("Employee Files", {"parent": employee, "title": document_title})
    print(f"Checking {document_title} for {employee}: {exists}")  # Debug print

    if exists:
        return "<div style='text-align:center;'>√√√</div>"
    else:
        return "<div style='text-align:center; background-color:#ff0000;'>ˣ</div>"


def get_data(filters):
    data = []
    conditions = get_conditions(filters)
    employees=frappe.db.sql("""select employee, employee_name from `tabEmployee` where 1=1 {0}""".format(conditions), as_dict=1)
    for emp in employees:

        document_titles = [
            "Passport Photo",
            "National ID Photo",
            "Personal Photos",
            "Graduation Certificate",
            "License to Practice",
            "Work Commencement Document",
            "Employee Card Template",
            "Confidentiality Agreement Template",
            "Shared Vision Statement Template",
            "Health Insurance",
            "Health Certificate"
        ]

        row = [
            emp.employee,
            emp.employee_name
        ]

        row.extend([check_file_exists(emp.employee, title) for title in document_titles])
        data.append(row)

    print(f"Generated Data: {data}")
    return data


