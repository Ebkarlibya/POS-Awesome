from frappe import _


def get_data(data=None):
	return {
		"heatmap": True,
		"heatmap_message": _(
			"This is based on transactions against this Customer. See timeline below for details"
		),
		"fieldname": "customer",
		"non_standard_fieldnames": {
			"Payment Entry": "party",
			"Quotation": "party_name",
			"Opportunity": "party_name",
			"Bank Account": "party",
			"Subscription": "party",
			"Related Customer": "parent_customer",
		},
		"dynamic_links": {
			"party_name": ["Customer", "quotation_to"],
			"party": ["Customer", "party_type"],
		},
		"transactions": [
			{"label": _("Pre Sales"), "items": ["Opportunity", "Quotation"]},
			{"label": _("Orders"), "items": ["Sales Order", "Delivery Note", "Sales Invoice"]},
			{"label": _("Payments"), "items": ["Payment Entry", "Bank Account"]},
			{
				"label": _("Support"),
				"items": ["Issue", "Maintenance Visit", "Installation Note", "Warranty Claim"],
			},
			{"label": _("Projects"), "items": ["Project"]},
			{"label": _("Pricing"), "items": ["Pricing Rule"]},
			{"label": _("Subscriptions"), "items": ["Subscription"]},
			{"label": _("Related Customers"), "items": ["Related Customer"]},
		],
	}
