# Copyright (c) 2026, mehmehsloth <pratham@frappe.io> and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from inventory_management.inventory_management.doctype.stock_entry.stock_entry import StockEntry


class StockEntryLedger(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		entry_type: DF.Data | None
		posting_datetime: DF.Datetime | None
		product: DF.Link | None
		quantity_change: DF.Int
		valuation_rate: DF.Currency
		warehouse: DF.Link | None
	# end: auto-generated types

	pass
