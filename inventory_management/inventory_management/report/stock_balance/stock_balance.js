// Copyright (c) 2026, mehmehsloth <pratham@frappe.io> and contributors
// For license information, please see license.txt

frappe.query_reports["Stock Balance"] = {
	filters: [
		{
			fieldname: "date_from",
			label: __("From Date"),
			fieldtype: "Datetime",
			default: frappe.datetime.add_days(frappe.datetime.get_today(), -30), // Default to 30 days ago
			reqd: 1,
		},
		{
			fieldname: "date_to",
			label: __("To Date"),
			fieldtype: "Datetime",
			default: frappe.datetime.get_today(), // Default to today
			reqd: 1,
		},
		{
			fieldname: "product",
			label: __("Product"),
			fieldtype: "Link",
			options: "Product",
		},
	],
};
