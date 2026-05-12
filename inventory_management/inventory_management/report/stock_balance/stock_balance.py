# Copyright (c) 2026, mehmehsloth <pratham@frappe.io> and contributors
# For license information, please see license.txt

from typing import TypedDict

import frappe
from frappe import _
from frappe.types import DF
from pypika import Order
from pypika.functions import Extract, Sum


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
			"width": "400",
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
	formatted_filters = {
		"date_to": filters.get("date_to"),
		"date_from": filters.get("date_from"),
		"product": filters.get("product"),
	}

	stock_entry_ledger = frappe.qb.DocType("Stock Entry Ledger")
	query = (
		frappe.qb.from_(stock_entry_ledger)
		.select(
			stock_entry_ledger.posting_datetime,
			stock_entry_ledger.product,
			Sum(stock_entry_ledger.quantity_change),
			stock_entry_ledger.warehouse,
		)
		.where(
			stock_entry_ledger.posting_datetime.between(
				formatted_filters["date_from"], formatted_filters["date_to"]
			)
		)
		.groupby(
			Extract("day", stock_entry_ledger.posting_datetime),
			stock_entry_ledger.product,
			stock_entry_ledger.warehouse,
		)
		.orderby(Extract("day", stock_entry_ledger.posting_datetime), order=Order.desc)
	)

	if formatted_filters["product"]:
		query = query.where(stock_entry_ledger.product == formatted_filters["product"])

	query_data = query.run()

	if not query_data:
		return []

	return [[item for item in row] for row in query_data]
