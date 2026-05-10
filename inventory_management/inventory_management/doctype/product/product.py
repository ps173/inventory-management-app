# Copyright (c) 2026, mehmehsloth <pratham@frappe.io> and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Product(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		brand: DF.Link | None
		description: DF.TextEditor | None
		image: DF.AttachImage | None
		product_name: DF.Data
		sku: DF.Data | None
		unit_price: DF.Float
	# end: auto-generated types

	pass
