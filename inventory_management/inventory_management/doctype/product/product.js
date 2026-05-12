// Copyright (c) 2026, mehmehsloth <pratham@frappe.io> and contributors
// For license information, please see license.txt

frappe.ui.form.on("Product", {
	refresh(frm) {
		frm.add_custom_button(__("Create a stock entry"), () => {
			// frappe.set_route("Form", "Stock Entry", {
			// 	product: frm.doc.name,
			// 	valuation_rate: frm.doc.valuation_rate,
			// });
			url = frappe.utils.get_form_link("Stock Entry", "new", false, null, {
				product: frm.doc.name,
				valuation_rate: frm.doc.valuation_rate,
			});

			// frappe.set_route(url);
			window.location.href = url;
		});
	},
});
