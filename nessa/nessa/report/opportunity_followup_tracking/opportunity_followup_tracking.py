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
            "label": _("Opportunity"),
            "fieldtype": "Link",
            "fieldname": "name",
            "options": "Opportunity",
            "width": 300,
        },
        {
            "label": _("Total Emails"),
            "fieldtype": "Int",
            "fieldname": "total_emails",
            "width": 200,
        },
        {
            "label": _("Total Events"),
            "fieldtype": "Int",
            "fieldname": "total_events",
            "width": 200,
        },
        {
            "label": _("Total Calls"),
            "fieldtype": "Int",
            "fieldname": "total_calls",
            "width": 200,
        },
        {
            "label": _("Total Meetings"),
            "fieldtype": "Int",
            "fieldname": "total_meetings",
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
        select 
            opp.name, 
            count(event_category) total_events,
            count(com.name) total_emails,
            sum(if(event_category='Call',1,0)) total_calls,
            sum(if(event_category='Meeting',1,0)) total_meetings
        from 
        tabOpportunity opp
        left outer join `tabEvent Participants` ep on ep.reference_doctype = 'Opportunity' 
        and ep.reference_docname = opp.name 
        left outer join tabEvent e on e.name = ep.parent 
        left outer join tabCommunication com on com.reference_doctype = 'Opportunity'
        and com.reference_name = opp.name
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
        group by opp.name, event_category
            """.format(
            conditions=conditions, user=frappe.db.escape(frappe.session.user)
        ),
        filters,
        as_dict=True,
    )

    return data
