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
        conditions += ["date(opp.creation) >= %(from_date)s"]
    if filters.get("to_date"):
        conditions += ["date(opp.creation) <= %(to_date)s"]
    if filters.get("sales_person"):
        conditions += ["opp.sales_person_cf <= %(sales_person)s"]

    return conditions and " and " + " and ".join(conditions) or ""


def get_data(filters):
    conditions = get_conditions(filters)
    data = frappe.db.sql(
        """
    select 
        count(name) total_opportunity, 
        sum(if(status='Converted',1,0)) total_won,
        sum(if(status='Lost',1,0)) total_lost 
    from tabOpportunity opp
    where opp.sales_person_cf in (
            select sp.name 
            from `tabSales Person` sp
            inner join `tabSales Person` u on u.user_cf = {user}
            where sp.lft >= u.lft and sp.rgt <= u.rgt order by sp.lft
    )
    {conditions}
    group by status
    """.format(
            conditions=conditions,
            user =frappe.db.escape(frappe.session.user)),
        filters,
        as_dict=True,
    )

    return data
