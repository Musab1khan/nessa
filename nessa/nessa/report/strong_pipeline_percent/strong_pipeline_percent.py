# Copyright (c) 2013, Greycube and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint 


def execute(filters=None):

    # if not filters.get("sales_stage"):
    filters["sales_stage"] = 'Strong Pipeline'

    columns, data = get_columns(filters), get_data(filters)
    return columns, data


def get_columns(filters):
    columns = [
        {
            "label": _("No of {0} (Opportunity)").format(filters.get("sales_stage")),
            "fieldtype": "Int",
            "fieldname": "total_sales_stage",
            "width": 280
        },
        {
            "label": _("Total Opportunity"),
            "fieldtype": "Int",
            "fieldname": "total_opportunity",
            "width": 200
        },
        {
            "label": _("No of {0}/Total Opportunity (%)").format(filters.get("sales_stage")),
            "fieldtype": "Int",
            "fieldname": "strong_pipeline_total_percent",
            "width": 400
        },
        ]
    return columns


def get_conditions(filters):
    conditions = []
    if filters.get("from_date"):
        conditions += ["date(opp.creation) >= %(from_date)s"]
    if filters.get("to_date"):
        conditions += ["date(opp.creation) <= %(to_date)s"]

    return conditions and " where " + " and ".join(conditions) or ""


def get_data(filters):
    conditions = get_conditions(filters)
    data = frappe.db.sql("""
    select 
        count(name) total_opportunity, 
        sum(if(sales_stage = %(sales_stage)s,1,0)) total_sales_stage
    from tabOpportunity opp
    {conditions}
    """.format(conditions=conditions), filters, as_dict=True, debug=True)

    for d in data:
        if not d.total_opportunity:
            d["strong_pipeline_total_percent"] = 0
        else:
            d["strong_pipeline_total_percent"] = 100 *  cint(d["total_sales_stage"])/cint(d["total_opportunity"])
        
    return data
