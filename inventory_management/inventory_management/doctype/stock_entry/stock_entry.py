# Copyright (c) 2026, mehmehsloth <pratham@frappe.io> and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.types import DF
from frappe.utils import now_datetime
from pypika.functions import Avg, Coalesce, Sum


class StockEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		from_warehouse: DF.Link | None
		posting_datetime: DF.Datetime | None
		product: DF.Link
		quantity: DF.Int
		to_warehouse: DF.Link
		type: DF.Literal["Receipt", "Consume", "Transfer"]
		valuation_rate: DF.Currency
	# end: auto-generated types

	def before_save(self):
		self.posting_datetime = self.posting_datetime or now_datetime()

	def before_submit(self):
		# check if there is enough stock before submitting for consume and transfer calls
		if self.type in ("Consume", "Transfer"):
			warehouse = self.to_warehouse if self.type == "Consume" else self.from_warehouse
			stock_entry_ledger = frappe.qb.DocType("Stock Entry Ledger")
			query = (
				frappe.qb.from_(stock_entry_ledger)
				.select(Coalesce(Sum(stock_entry_ledger.quantity_change), 0))
				.where(
					stock_entry_ledger.product == self.product and stock_entry_ledger.warehouse == warehouse
				)
			)
			query_data = query.run()
			current_stock = int(query_data[0][0])

			if current_stock < self.quantity:
				frappe.throw(
					f"Insufficient stock for product {self.product} at {warehouse}. "
					f"Available: {current_stock}, Required: {self.quantity}",
					frappe.ValidationError,
				)

	def create_stock_ledger_entry(self, warehouse, type: DF.Literal["Receipt", "Consume"]):
		ledger_entry = frappe.new_doc("Stock Entry Ledger")
		ledger_entry.update(
			{
				"entry_type": type,
				"posting_datetime": self.posting_datetime,
				"product": self.product,
				"quantity_change": self.quantity if type == "Receipt" else -self.quantity,
				"valuation_rate": self.valuation_rate,
				"warehouse": warehouse,
			}
		)
		ledger_entry.save()

	def on_submit(self):
		match self.type:
			case "Receipt":
				self.create_stock_ledger_entry(self.to_warehouse, self.type)
			case "Consume":
				self.create_stock_ledger_entry(self.to_warehouse, self.type)
			case "Transfer":
				self.create_stock_ledger_entry(self.to_warehouse, "Receipt")
				self.create_stock_ledger_entry(self.from_warehouse, "Consume")
		calculate_product_valuation(self.product)


def calculate_product_valuation(product):
	# calculate average valuation rate for the product
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
