# Copyright (c) 2013, Greycube and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns, data = get_columns(filters), get_data(filters)
    return columns, data


def get_columns(filters):
    columns = [
        {
            "label": "Sales Person",
            "fieldtype": "Data",
            "fieldname": "sales_person_cf",
            "width": 200,
        },
        {
            "label": _("Total Opportunity"),
            "fieldtype": "Int",
            "fieldname": "total_opportunity",
            "width": 200,
        },
        {
            "label": _("Total Won"),
            "fieldtype": "Int",
            "fieldname": "total_won",
            "width": 200,
        },
        {
            "label": _("Total Lost"),
            "fieldtype": "Int",
            "fieldname": "total_lost",
            "width": 200,
        },
    ]
    return columns


def get_conditions(filters):
    conditions = []
    if filters.get("from_date"):
        conditions += ["date(opp.transaction_date) >= %(from_date)s"]
    if filters.get("to_date"):
        conditions += ["date(opp.transaction_date) <= %(to_date)s"]
    if filters.get("sales_person"):
        conditions += ["opp.sales_person_cf <= %(sales_person)s"]

    return conditions and " and " + " and ".join(conditions) or ""


def get_data(filters):
    conditions = get_conditions(filters)
    data = frappe.db.sql(
        """
    with fn as 
    (
        select 
            opp.sales_person_cf,
            count(name) total_opportunity, 
            sum(if(status='Converted',1,0)) total_won,
            sum(if(status='Lost',1,0)) total_lost 
        from tabOpportunity opp
            where 
            (
                opp.sales_person_cf in (
                select for_value 
                from `tabUser Permission` 
                where allow = 'Sales Person' and user = {user})
            or not exists (
                select 1 
                from `tabUser Permission` 
                where allow = 'Sales Person' and user = {user})
            )
        {conditions}
        group by opp.sales_person_cf
    )
    select * from fn
    union all
    select 'Total', sum(total_opportunity), sum(total_won), sum(total_lost)
    from fn
    """.format(
            conditions=conditions, user=frappe.db.escape(frappe.session.user)
        ),
        filters,
        as_dict=True,
    )

    return data
