// Copyright (c) 2023, Greycube and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales person Target"] = {
	"filters": [
		{
			"fieldname" : "sales_person_name",
			"fieldtype" : "Link",
			"label": "Sales Person",
			"options" : "Sales Person",

		},
		{
			fieldname: "fiscal_year",
			label: "Fiscal Year",
			fieldtype: "Link",
			options: "Fiscal Year",
			// default: frappe.sys_defaults.fiscal_year,
			
		},

	]
};
