# Copyright (c) 2013, Greycube and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint


def execute(filters=None):

    # if not filters.get("sales_stage"):
    # filters["sales_stage"] = "Strong Pipeline"

    columns, data = get_columns(filters), get_data(filters)
    return columns, data


def get_columns(filters):
    columns = [
        {
            "label": _("Sales Person"),
            "fieldtype": "Link",
            "fieldname": "sales_person_cf",
			"options" :"Sales Person",
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

    return conditions and " where " + " and ".join(conditions) or ""


def get_data(filters):
    conditions = get_conditions(filters)
    data = frappe.db.sql(
        """        
    select 
    COALESCE(opp.sales_person_cf,'') sales_person_cf,
    round(sum(case when q.is_quotation_won_cf = 1 THEN q.base_net_total else 0 end)) orders_received,
    round(sum(case when opp.sales_stage = 'Strong Pipeline' then opp.opportunity_amount else 0 end)) strong_pipeline_value,
    round(sum(case when opp.sales_stage = 'Normal Pipeline' then opp.opportunity_amount else 0 end)) normal_pipeline_value,
    sum(coalesce(m.ct,0)) meetings_done,
    sum(if(q.sales_person_cf=opp.sales_person_cf,1,0)) inquiries_sent
    from tabOpportunity opp
    left outer join tabQuotation q on q.opportunity = opp.name
	left outer join
	( 
		select ep.reference_docname, sum(if(e.event_category='Meeting',1,0)) ct
		from `tabEvent Participants` ep
		inner join tabEvent e on e.name = ep.parent
		where ep.reference_doctype = 'Opportunity'
		group by ep.reference_docname
	) m on m.reference_docname = opp.name 
    {conditions}
    group by COALESCE(opp.sales_person_cf,'')
    """.format(
            conditions=conditions, user=frappe.db.escape(frappe.session.user)
        ),
        filters,
        as_dict=True,
		debug=True
    )

    return data
