# Copyright (c) 2026, mehmehsloth <pratham@frappe.io> and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.nestedset import NestedSet


class Warehouse(NestedSet):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		address: DF.LongText | None
		address_line_1: DF.Data | None
		address_line_2: DF.Data | None
		available_capacity: DF.Data | None
		citydistrictprovince: DF.Date | None
		country: DF.Data | None
		email: DF.Data | None
		is_group: DF.Check
		lft: DF.Int
		maximum_storage_capacity: DF.Int
		old_parent: DF.Link | None
		parent_warehouse: DF.Link | None
		phone_number: DF.Phone | None
		rgt: DF.Int
		state: DF.Data | None
		type: DF.Literal["Warehouse", "Floor", "Aisle", "Shelf"]
		warehouse_name: DF.Data
	# end: auto-generated types

	pass

	def on_update(self):
		# 1. Update the current node's own parent
		self.update_parent()

	def update_parent(self):
		if self.parent_warehouse:
			print("parent", self.parent_warehouse)


			# Aggregate or calculate values from self
			#    parent_doc = frappe.get_doc("Warehouse", self.parent_warehouse)
			#    # Example: Update a "total_value" field on parent
			#    # based on all direct children
			# children = frappe.get_all("MyTreeDocType",
			#     filters={"parent_mytreedoctype": self.parent_mytreedoctype},
			#     fields=["sum(total_value) as total"],
			#     group_by="parent_mytreedoctype"
			# )
			#    new_total = children[0].total if children else 0

			#    # Update parent without triggering on_update again
			#    frappe.db.set_value("MyTreeDocType", self.parent_mytreedoctype,
			#        "total_value", new_total)

			#    # Recursively update the grandparent, if needed
			#    parent_doc.update_parent()
