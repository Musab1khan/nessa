// Copyright (c) 2020, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("User", {
  refresh: function (frm) {
    frm.page.add_action_item(
      __("Create Workspace"),
      function () {
        var d = new frappe.ui.Dialog({
          title: "Copy Workspace",
          fields: [
            {
              label: __("Copy from User"),
              fieldtype: "Link",
              options: "User",
              only_select: true,
              fieldname: "src_user",
              reqd: 1,
              get_query: function () {
                return { query: "nessa.nessa.get_users_with_customization" };
              },
            },
          ],
          primary_action: (values) => {
            d.hide();
            frappe.call({
              method: "nessa.nessa.copy_workspace_customization",
              args: {
                src_user: values.src_user,
                target_user: frm.doc.name,
              },
              callback: function (r) {
                frappe.show_alert("User customizations have been copied.");
              },
            });
          },
        });

        d.show();
      },
      true
    );
  },
});
