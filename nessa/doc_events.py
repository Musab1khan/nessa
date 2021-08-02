# Copyright (c) 2013, Greycube and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def validate_lead(doc, method):
    if doc.lead_owner:
        for d in frappe.db.get_all(
            "Sales Person", filters={"user_cf": doc.lead_owner}, limit=1
        ):
            doc.sales_person_cf = d.name
