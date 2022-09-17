// Copyright (c) 2016, Greycube and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Person Performance Analysis"] = {
  filters: [
    {
      fieldname: "from_date",
      label: __("From Date"),
      fieldtype: "Date",
      default: frappe.datetime.add_days(frappe.datetime.get_today(), -7),
    },
    {
      fieldname: "to_date",
      label: __("To Date"),
      fieldtype: "Date",
      default: frappe.datetime.get_today(),
    },
    {
      fieldname: "timespan",
      label: __("Opportunity Creation Date in "),
      fieldtype: "Select",
      options: nessa.utils.TIMESPAN_OPTIONS,
      on_change: function (query_report) {
        let date_range = nessa.utils.get_date_range(
          query_report.get_values().timespan
        );
        frappe.query_report.set_filter_value({
          from_date: date_range[0],
          to_date: date_range[1],
        });
      },
      default: "Last Week",
    },
    {
      fieldname: "sales_person",
      label: __("Sales Person"),
      fieldtype: "Link",
      options: "Sales Person",
    },
    {
      fieldname: "ignore_duration_for_opportunity",
      label: __("Ignore Duration for Opportunity"),
      fieldtype: "Check",
      default: 1
    },
  ],
};
