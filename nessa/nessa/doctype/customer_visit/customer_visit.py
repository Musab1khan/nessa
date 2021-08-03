# -*- coding: utf-8 -*-
# Copyright (c) 2021, Greycube and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.utils import cint, cstr
from frappe.model.document import Document
import json


class CustomerVisit(Document):
    def on_submit(self):
        if not self.status in ["Completed", "Cancelled"]:
            frappe.throw(_("Invalid status {0}. Can submit Visit only when status is Completed or Cancelled.").format(frappe.bold(self.status)))

        if not self.actual_date and self.status in ["Completed"]:
            self.actual_date = frappe.utils.today()
        for d in frappe.get_all(
            "Customer Visit Plan Detail",
            filters=[["customer_visit_reference_cf", "=", self.name]],
        ):
            frappe.db.set_value(
                "Customer Visit Plan Detail", d.name, "status", self.status
            )

    def on_cancel(self):
        self.status = "Cancelled"

    def before_cancel(self):
        frappe.db.sql(
            """
            update `tabCustomer Visit Plan Detail`
            set customer_visit_reference_cf = null
            where customer_visit_reference_cf = %s""",
            (self.name),
        )
