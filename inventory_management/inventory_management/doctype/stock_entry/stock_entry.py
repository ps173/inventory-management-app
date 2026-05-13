# Copyright (c) 2026, mehmehsloth <pratham@frappe.io> and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.types import DF
from frappe.utils import now_datetime
from pypika.functions import Avg, Coalesce, Sum

from inventory_management.inventory_management.doctype.stock_entry_item.stock_entry_item import (
	StockEntryItem,
)


class StockEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from inventory_management.inventory_management.doctype.stock_entry_item.stock_entry_item import (
			StockEntryItem,
		)

		amended_from: DF.Link | None
		entry_items: DF.Table[StockEntryItem]
		posting_datetime: DF.Datetime | None
	# end: auto-generated types

	# check if there is enough stock before submitting for consume and transfer calls for all the child items
	def check_is_stock_available(self):
		for item in self.entry_items:
			if item.entry_type in ("Consume", "Transfer"):
				warehouse = item.to_warehouse if item.entry_type == "Receipt" else item.from_warehouse
				stock_entry_ledger = frappe.qb.DocType("Stock Entry Ledger")
				query = (
					frappe.qb.from_(stock_entry_ledger)
					.select(Coalesce(Sum(stock_entry_ledger.quantity_change), 0))
					.where(
						stock_entry_ledger.product == item.product
						and stock_entry_ledger.warehouse == warehouse
					)
				)
				query_data = query.run()
				current_stock = int(query_data[0][0])

				if current_stock < item.quantity:
					frappe.throw(
						f"Insufficient stock for product {item.product} at {warehouse}. "
						f"Available: {current_stock}, Required: {item.quantity}",
						frappe.ValidationError,
					)

	def before_save(self):
		self.posting_datetime = self.posting_datetime or now_datetime()
		self.check_is_stock_available()

	def on_submit(self):
		for _item in self.entry_items:
			item = frappe._dict({**_item.as_dict(), "posting_datetime": self.posting_datetime})
			match item.entry_type:
				case "Receipt":
					create_stock_ledger_entry(item, item.entry_type)
					calculate_product_valuation(item.product)
				case "Consume":
					create_stock_ledger_entry(item, item.entry_type)
				case "Transfer":
					create_stock_ledger_entry(item, "Receipt")
					create_stock_ledger_entry(item, "Consume")


def create_stock_ledger_entry(item, entry_type: DF.Literal["Receipt", "Consume"]):
	warehouse = item.to_warehouse if entry_type == "Receipt" else item.from_warehouse
	ledger_entry = frappe.new_doc("Stock Entry Ledger")
	ledger_entry.update(
		{
			"entry_type": entry_type,
			"posting_datetime": item.posting_datetime,
			"product": item.product,
			"quantity_change": item.quantity if entry_type == "Receipt" else -item.quantity,
			"valuation_rate": item.valuation_rate,
			"warehouse": warehouse,
		}
	)
	ledger_entry.save()


def calculate_product_valuation(product: str):
	stock_entry_ledger = frappe.qb.DocType("Stock Entry Ledger")
	query = (
		frappe.qb.from_(stock_entry_ledger)
		.select(Avg(stock_entry_ledger.valuation_rate))
		.where(stock_entry_ledger.product == product)
	)
	query_data = query.run()

	average_valuation_rate = query_data[0][0]
	product = frappe.get_doc("Product", product, for_update=True)
	product.unit_price = float(average_valuation_rate)
	product.save()
