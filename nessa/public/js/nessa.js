frappe.provide("nessa.utils");

frappe.get_user_location = async function () {
  return new Promise((resolve, reject) => {
    // check geolocation api is available
    if (!navigator.geolocation) {
      frappe.throw(__("Geolocation is not enabled."));
      reject();
    }

    // if((window.location.href.match(/:[0-9]+/g)||[]).length) {
    //   // return client location for local test. comment in production
    //   resolve(
    //     [ '12.880834','80.215677',]
    //   );
    //   return
    // }
    navigator.geolocation.getCurrentPosition(
      (loc) => {
        // console.log([loc.coords.latitude, loc.coords.longitude]);
        resolve([loc.coords.latitude, loc.coords.longitude]);
      },
      (err) => {
        frappe.throw(err.message);
        reject([]);
      }
    );
  });
};

frappe.haversineDistance = ([lat1, lon1], [lat2, lon2], isMiles = false) => {
  const toRadian = (angle) => (Math.PI / 180) * angle;
  const distance = (a, b) => (Math.PI / 180) * (a - b);
  const RADIUS_OF_EARTH_IN_KM = 6371;

  const dLat = distance(lat2, lat1);
  const dLon = distance(lon2, lon1);

  lat1 = toRadian(lat1);
  lat2 = toRadian(lat2);

  // Haversine Formula
  const a =
    Math.pow(Math.sin(dLat / 2), 2) +
    Math.pow(Math.sin(dLon / 2), 2) * Math.cos(lat1) * Math.cos(lat2);
  const c = 2 * Math.asin(Math.sqrt(a));

  let finalDistance = RADIUS_OF_EARTH_IN_KM * c;

  if (isMiles) {
    finalDistance /= 1.60934;
  }

  console.log("Distance to client location in km - ", finalDistance);
  return finalDistance;
};

Object.assign(nessa.utils, {
  TIMESPAN_OPTIONS: [
    "Last Week",
    "Last Month",
    "Last Quarter",
    "Last Year",
    "Today",
    "This Week",
    "This Month",
    "This Quarter",
    "This Year",
  ],
  get_date_range: function (timespan = "This Month") {
    timespan = timespan.toLowerCase();
    let current_date = frappe.datetime.now_date();
    let date_range_map = {
      today: [current_date, current_date],
      "this week": [frappe.datetime.week_start(), current_date],
      "this month": [frappe.datetime.month_start(), current_date],
      "this quarter": [frappe.datetime.quarter_start(), current_date],
      "this year": [frappe.datetime.year_start(), current_date],
      "last week": [frappe.datetime.add_days(current_date, -7), current_date],
      "last month": [
        frappe.datetime.add_months(current_date, -1),
        current_date,
      ],
      "last quarter": [
        frappe.datetime.add_months(current_date, -3),
        current_date,
      ],
      "last year": [
        frappe.datetime.add_months(current_date, -12),
        current_date,
      ],
      "all time": null,
      "select date range": this.selected_date_range || [
        frappe.datetime.month_start(),
        current_date,
      ],
    };
    return date_range_map[timespan];
  },
});
