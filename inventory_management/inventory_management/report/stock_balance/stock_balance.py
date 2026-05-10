# Copyright (c) 2026, mehmehsloth <pratham@frappe.io> and contributors
# For license information, please see license.txt

from typing import TypedDict
from warnings import warn_explicit

import frappe
from frappe import _
from frappe.types import DF


class Filter(TypedDict, total=False):
	date_from: DF.Datetime
	date_to: DF.Datetime
	product: DF.Link



def execute(filters: Filter):
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
			"label": _("Date"),
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
			"label": _("Balance"),
			"fieldname": "balance",
			"fieldtype": "Int",
		},
		{
			"label": _("Warehouse"),
			"fieldname": "warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
		},
	]


def get_data(filters: Filter) -> list[list]:
	"""Return data for the report.

	The report data is a list of rows, with each row being a list of cell values.
	"""
	formatted_filters = {"date_to": filters.get("date_to"), "date_from": filters.get("date_from"), "product": filters.get("product")}

	query_data = frappe.db.sql("""
		SELECT DATE(posting_datetime) as date, product, SUM(quantity_change) as balance, warehouse
		FROM `tabStock Entry Ledger`
		WHERE posting_datetime BETWEEN %(date_from)s AND %(date_to)s
		AND CASE WHEN %(product)s IS NOT NULL THEN product = %(product)s ELSE 1=1 END
		GROUP BY DATE(posting_datetime), product, warehouse;
	""", formatted_filters)


	print(query_data)

	if not query_data:
		return []

	return [
		[item for item in row] for row in query_data
	]
