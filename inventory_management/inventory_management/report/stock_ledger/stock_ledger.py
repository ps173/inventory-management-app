# Copyright (c) 2026, mehmehsloth <pratham@frappe.io> and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters: dict | None = None):
	"""Return columns and data for the report.

	This is the main entry point for the report. It accepts the filters as a
	dictionary and should return columns and data. It is called by the framework
	every time the report is refreshed or a filter is updated.
	"""
	columns = get_columns()
	data = get_data(filters)

	return columns, data


def get_columns() -> list[dict]:
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	return [
		{
			"label": _("Timestamp"),
			"fieldname": "posting_datetime",
			"fieldtype": "Datetime",
		},
		{
			"label": _("Product"),
			"fieldname": "product",
			"fieldtype": "Link",
			"options": "Product",
		},
		{
			"label": _("Warehouse"),
			"fieldname": "warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
		},
		{
			"label": _("Quantity"),
			"fieldname": "quantity",
			"fieldtype": "Int",
		},
		{
			"label": _("Valuation Rate"),
			"fieldname": "valuation_rate",
			"fieldtype": "Currency",
		},
		{
			"label": _("Entry Type"),
			"fieldname": "entry_type",
			"fieldtype": "Select",
			"options": "Reciept, Consume, Transfer",
		}
	]


def get_data(filters: dict | None = None) -> list[list]:
	"""Return data for the report.

	The report data is a list of rows, with each row being a list of cell values.
	"""
	# get stock ledger entries
	stock_ledger_entries = frappe.get_all("Stock Entry Ledger", fields=["*"], filters=filters)
	# convert to report data
	data = [
		[entry.posting_datetime, entry.product, entry.warehouse, entry.quantity_change, entry.valuation_rate, entry.entry_type]
		for entry in stock_ledger_entries
	]
	return data
