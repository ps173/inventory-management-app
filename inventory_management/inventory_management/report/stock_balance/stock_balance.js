// Copyright (c) 2026, mehmehsloth <pratham@frappe.io> and contributors
// For license information, please see license.txt

frappe.query_reports["Stock Balance"] = {
	filters: [
		{
			fieldname: "date_to",
			label: __("To Date"),
			fieldtype: "Datetime",
			default: "today", // Default to today
			reqd: 1,
		},
		{
			fieldname: "product",
			label: __("Product"),
			fieldtype: "Link",
			options: "Product",
		},
		{
			fieldname: "warehouse",
			label: __("Warehouse"),
			fieldtype: "Link",
			options: "Warehouse",
		},
	],
};
