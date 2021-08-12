frappe.listview_settings["Customer Visit"] = {
  hide_name_column: true,
  has_indicator_for_draft: 1,
  get_indicator: function (doc) {
    var colors = {
      Open: "orange",
      Completed: "green",
      Cancelled: "red",
    };

    return [__(doc.status), colors[doc.status], "status,=," + doc.status];
  },

  refresh: function (me) {},
};
