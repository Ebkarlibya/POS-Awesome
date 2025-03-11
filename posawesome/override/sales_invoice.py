import frappe
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice

def custom_get_total_in_party_account_currency(
    invoice, outstanding_amount=None, total_amount=None
):
    """Custom function to override get_total_in_party_account_currency"""
    party_account_currency = invoice.party_account_currency
    if party_account_currency == invoice.company_currency:
        return total_amount if total_amount is not None else invoice.total

    if outstanding_amount is None:
        outstanding_amount = invoice.outstanding_amount

    total_in_party_account_currency = (
        frappe.db.get_value(
            "Sales Invoice", invoice.name, "total_in_party_account_currency"
        )
        or invoice.total_in_party_account_currency
    )

    if total_in_party_account_currency:
        return total_in_party_account_currency

    return outstanding_amount

# Override the method in SalesInvoice
SalesInvoice.get_total_in_party_account_currency = custom_get_total_in_party_account_currency
