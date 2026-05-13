# Copyright (c) 2026, mehmehsloth <pratham@frappe.io> and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.types import DF
from pypika.functions import Coalesce, Sum


class StockEntryItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		entry_type: DF.Literal["Receipt", "Consume", "Transfer"]
		from_warehouse: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		product: DF.Link
		quantity: DF.Int
		to_warehouse: DF.Link | None
		valuation_rate: DF.Currency
	# end: auto-generated types

	pass
