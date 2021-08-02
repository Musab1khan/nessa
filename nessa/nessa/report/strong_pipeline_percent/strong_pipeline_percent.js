// Copyright (c) 2016, Greycube and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Strong Pipeline Percent"] = {
  filters: [
    // {
    //   fieldname: "sales_stage",
    //   label: __("Sales Stage"),
    //   fieldtype: "Link",
    //   options: "Sales Stage",
    //   default: "Strong Pipeline",
    //   reqd: 1,
    // },
    {
      fieldname: "from_date",
      label: __("From Date"),
      fieldtype: "Date",
      default: frappe.datetime.month_start(),
    },
    {
      fieldname: "to_date",
      label: __("To Date"),
      fieldtype: "Date",
      default: frappe.datetime.get_today(),
    },
    {
      fieldname: "sales_person",
      label: __("Sales Person"),
      fieldtype: "Link",
      options: "Sales Person",
    },
  ],
};
