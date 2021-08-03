// Copyright (c) 2021, Greycube and contributors
// For license information, please see license.txt

frappe.ui.form.on("Customer Visit Plan", {
  setup: function (frm) {
    frm.fields_dict["customer_visit_plan_detail"].grid.get_field(
      "contact"
    ).get_query = function (doc, cdt, cdn) {
      let d = locals[cdt][cdn];
      return {
        query:
          "nessa.nessa.doctype.customer_visit_plan.customer_visit_plan.get_customer_contacts",
        filters: { customer: d.customer },
      };
    };
  },
});

frappe.ui.form.on(
  "Customer Visit Plan Detail",
  "customer_visit_plan_detail_add",
  function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    row.plan_date = frm.doc.transaction_date;
  }
);
