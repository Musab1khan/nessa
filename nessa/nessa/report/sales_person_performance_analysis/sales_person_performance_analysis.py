# Copyright (c) 2013, Greycube and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint


def execute(filters=None):

    # if not filters.get("sales_stage"):
    # filters["sales_stage"] = "Strong Pipeline"

    if not filters.get("from_date"):
        filters["from_date"] = "1900-01-01"

    if not filters.get("to_date"):
        filters["to_date"] = "3000-01-01"

    columns, data = get_columns(filters), get_data(filters)
    return columns, data


def get_columns(filters):
    columns = [
        {
            "label": _("Sales Person"),
            "fieldtype": "Link",
            "fieldname": "sales_person_cf",
            "options": "Sales Person",
            "width": 280,
        },
        {
            "label": _("Orders Received"),
            "fieldtype": "Currency",
            "fieldname": "orders_received",
            "width": 175,
        },
        {
            "label": _("Strong Pipeline Value"),
            "fieldtype": "Currency",
            "fieldname": "strong_pipeline_value",
            "width": 175,
        },
        {
            "label": _("Normal Pipeline Value"),
            "fieldtype": "Currency",
            "fieldname": "normal_pipeline_value",
            "width": 175,
        },
        {
            "label": _("No of Meetings Done"),
            "fieldtype": "Int",
            "fieldname": "meetings_done",
            "width": 175,
        },
        {
            "label": _("No of inquiries handled/<br>Quote sent"),
            "fieldtype": "Int",
            "fieldname": "inquiries_sent",
            "width": 175,
        },
        {
            "label": _("Quotation Count"),
            "fieldtype": "Int",
            "fieldname": "quotation_count",
            "width": 145,
        },
    ]
    return columns


def get_conditions(filters):
    conditions = []
    if filters.get("from_date"):
        conditions += ["date(opp.transaction_date) >= %(from_date)s"]
    if filters.get("to_date"):
        conditions += ["date(opp.transaction_date) <= %(to_date)s"]

    return conditions and " where " + " and ".join(conditions) or ""


def get_data(filters):
    conditions = get_conditions(filters)
    data = frappe.db.sql(
        """        
    select t1.* , round(so.base_net_total) orders_received,  visit.mtg_count meetings_done
    from 
    (
	   	select 
	    COALESCE(opp.sales_person_cf,'') sales_person_cf,
	    round(sum(case when opp.sales_stage = 'Strong Pipeline' then opp.opportunity_amount else 0 end)) strong_pipeline_value,
	    round(sum(case when opp.sales_stage = 'Normal Pipeline' then opp.opportunity_amount else 0 end)) normal_pipeline_value,
	    count(opp.name) inquiries_sent ,
	    count(DISTINCT q.name) quotation_count
	    from tabOpportunity opp
	    left outer join tabQuotation q on q.opportunity = opp.name
        {conditions}
	    group by COALESCE(opp.sales_person_cf,'')
    ) t1
    left outer join (
	    select sales_person , count(sales_person) mtg_count 
	    from `tabCustomer Visit` tcv 
	    where actual_date is not null
        and actual_date between %(from_date)s and %(to_date)s
	    group by sales_person
    ) visit on visit.sales_person = t1.sales_person_cf
    left outer join (
       select tst.sales_person , sum(tso.base_net_total) base_net_total
	   from `tabSales Order` tso inner join `tabSales Team` tst on tst.parent = tso.name
       where tso.transaction_date between %(from_date)s and %(to_date)s
	   group by tst.sales_person
    ) so on so.sales_person = t1.sales_person_cf
    """.format(
            conditions=conditions, user=frappe.db.escape(frappe.session.user)
        ),
        filters,
        as_dict=True,
    )

    if filters.get("sales_person"):
        sales_person = frappe.db.sql(
            """
            select b.name  from `tabSales Person` a 
            inner join `tabSales Person` b on b.lft >= a.lft and b.rgt <= a.rgt 
            where a.name = %s;        
        """,
            (filters.get("sales_person")),
            as_list=True,
        )
        data = [
            x for x in data if x.get("sales_person_cf") in [a[0] for a in sales_person]
        ]

    return data
