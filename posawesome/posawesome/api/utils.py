from erpnext.accounts.utils import get_balance_on
import frappe
from frappe.utils.data import now


def get_outstanding_amount(name, customer):
    starting_balance = get_balance_on(
        date=now(),
        party_type="Customer",
        party=customer,
    )

    field1_value = starting_balance or 0.0
    field2_value = (
        frappe.db.get_value("Sales Invoice", {"name": name}, "grand_total") or 0.0
    )

    total = field1_value + field2_value

    return total
