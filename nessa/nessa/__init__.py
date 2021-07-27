# -*- coding: utf-8 -*-
# Copyright (c) 2021, Greycube and contributors
# For license information, please see license.txt


import os
import frappe


@frappe.whitelist()
def copy_workspace_customization(src_user, target_user):
    def get_module_page_map():
        filters = {
            "for_user": src_user,
            # "module": "Support"
        }
        pages = frappe.get_all(
            "Workspace", fields=["name", "module"], filters=filters, as_list=1
        )
        return {page[1]: page[0] for page in pages if page[1]}

    module_page_map = get_module_page_map()
    for module, name in module_page_map.items():
        target = frappe.copy_doc(frappe.get_doc("Workspace", name))
        target.update(
            {
                "for_user": target_user,
            }
        )
        target.label = "{0}-{1}".format(module, target_user)
        target.insert(ignore_permissions=True)

    frappe.db.commit()


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_users_with_customization(doctype, txt, searchfield, start, page_len, filters):
    filters = [
        ["Workspace", "for_user", "like", "%{}%".format(txt)],
        ["Workspace", "for_user", "!=", frappe.session.user],
    ]

    return frappe.get_all(
        "Workspace",
        fields = ['for_user as name'],
        limit_start=start,
        limit_page_length=page_len,
        filters=filters,
        as_list=1,
    )
