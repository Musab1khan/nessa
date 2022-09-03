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


def validate_bom(doc, method):

    item_details = {}

    for d in frappe.db.sql(
        """
    select tbi.item_code , 
    GROUP_CONCAT(CONCAT(tim.manufacturer,'\t,\t',tim.manufacturer_part_no) SEPARATOR '\n') details
    from `tabBOM Item` tbi 
    inner join `tabItem Manufacturer` tim on tim.item_code = tbi.item_code 
    where tbi.parent = %s
    group by tbi.item_code 
    """,
        (doc.name,),
        as_dict=True,
    ):
        item_details[d.item_code] = d.details

    if item_details:
        for d in doc.items:
            if not d.item_manufacturer_detail_cf:
                d.item_manufacturer_detail_cf = item_details.get(d.item_code)
