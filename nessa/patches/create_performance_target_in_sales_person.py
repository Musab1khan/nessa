import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    print("Creating fields for Nessa sales person target report:")
    custom_fields = {
        "Sales Person": [
            dict(
                fieldname="performance_target_cf",
                label="Performance Target",
                fieldtype="Currency",
                insert_after="department",
            )
        ]
    }

    create_custom_fields(custom_fields, update=True)