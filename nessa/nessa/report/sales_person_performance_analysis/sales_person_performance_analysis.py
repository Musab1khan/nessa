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
    if not filters.get("ignore_duration_for_opportunity"):
        filters["ignore_duration_for_opportunity"] = 0

    columns, data = get_columns(filters), get_data(filters)
    return columns, data


def get_data(filters):
    conditions = get_conditions(filters)
    data = frappe.db.sql(
        """        
        select 
            tsp.name , 
            coalesce(tq.quotation_count,0) quotation_count, 
            coalesce(topp.strong_pipeline_value,0) strong_pipeline_value, 
            coalesce(topp.normal_pipeline_value,0) normal_pipeline_value, 
            coalesce(topp.inquiries_sent,0) inquiries_sent,
            coalesce(so.base_net_total,0) orders_received, 
            coalesce(si.base_net_total,0) invoiced_value, 
            coalesce(visit.meetings_done,0) meetings_done,
            coalesce(evt.ct,0) total_meetings
        from `tabSales Person` tsp 
        left outer join (
            select tq.sales_person_cf, count(tq.sales_person_cf) quotation_count
            from tabQuotation tq
            where tq.transaction_date between %(from_date)s and %(to_date)s
            and tq.docstatus = 1
            group by tq.sales_person_cf  
        ) tq on tq.sales_person_cf = tsp.name
        left outer join (
            select 
            opp.sales_person_cf ,
            round(sum(case when opp.sales_stage = 'Strong Pipeline' 
                then opp.opportunity_amount else 0 end)) strong_pipeline_value ,
            round(sum(case when opp.sales_stage = 'Normal Pipeline' 
                then opp.opportunity_amount else 0 end)) normal_pipeline_value ,
            count(opp.name) inquiries_sent 
            from tabOpportunity opp
            where %(ignore_duration_for_opportunity)s = 1 
            or opp.transaction_date between %(from_date)s and %(to_date)s
            group by opp.sales_person_cf 
        ) topp on topp.sales_person_cf = tsp.name
        left outer join (
            select sales_person , count(sales_person) meetings_done 
            from `tabCustomer Visit` tcv 
            where actual_date is not null
            and actual_date between %(from_date)s and %(to_date)s
            group by sales_person
        ) visit on visit.sales_person = tsp.name
        left outer join (
            select tst.sales_person , round(sum(tso.base_net_total)) base_net_total
            from `tabSales Order` tso inner join `tabSales Team` tst on tst.parent = tso.name
            where tso.transaction_date between %(from_date)s and %(to_date)s
            and tso.docstatus = 1
            group by tst.sales_person
        ) so on so.sales_person = tsp.name
        left outer join (
            select tst.sales_person , round(sum(tst.allocated_amount)) base_net_total
            from `tabSales Invoice` tsi 
            inner join `tabSales Team` tst on tst.parent = tsi.name
            where tsi.posting_date between %(from_date)s and %(to_date)s
            and tsi.docstatus = 1
            group by tst.sales_person
        ) si on si.sales_person = tsp.name        
        left outer join (
	        select tsp.sales_person_name , count(tsp.sales_person_name) ct 
	        from tabEvent te 
	        inner join `tabSales Person` tsp on tsp.user_cf = te.owner
	        where te.starts_on between %(from_date)s and %(to_date)s
	        group by tsp.sales_person_name
	    ) evt on evt.sales_person_name = tsp.name        
        where tsp.enabled = 1
        order by tsp.name
    """.format(
            conditions=conditions, user=frappe.db.escape(frappe.session.user)
        ),
        filters,
        as_dict=True,
        # debug=True,
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
        data = [x for x in data if x.get("name") in [a[0] for a in sales_person]]

    return data


def get_columns(filters):
    columns = [
        {
            "label": _("Sales Person"),
            "fieldtype": "Link",
            "fieldname": "name",
            "options": "Sales Person",
            "width": 280,
        },
        {
            "label": _("Invoiced Value"),
            "fieldtype": "Currency",
            "fieldname": "invoiced_value",
            "width": 175,
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
            "label": _("No of Customer Visits Done"),
            "fieldtype": "Int",
            "fieldname": "meetings_done",
            "width": 200,
        },
        {
            "label": _("No Of Meetings"),
            "fieldtype": "Int",
            "fieldname": "total_meetings",
            "width": 155,
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
