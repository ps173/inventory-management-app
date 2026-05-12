# Copyright (c) 2026, mehmehsloth <pratham@frappe.io> and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase

EXTRA_TEST_RECORD_DEPENDENCIES = []
IGNORE_TEST_RECORD_DEPENDENCIES = []


class IntegrationTestStockEntry(IntegrationTestCase):
	def setUp(self):
		super().setUp()
		self.product = frappe.get_doc(
			{
				"doctype": "Product",
				"product_name": "_Test PRODUCT A",
				"unit_price": 100.0,
			}
		).insert()

		self.warehouse_a = frappe.get_doc(
			{
				"doctype": "Warehouse",
				"warehouse_name": "_Test WAREHOUSE A",
			}
		).insert()

		self.warehouse_b = frappe.get_doc(
			{
				"doctype": "Warehouse",
				"warehouse_name": "_Test WAREHOUSE B",
			}
		).insert()


	def tearDown(self):
		frappe.db.rollback()

	def test_receipt_creates_one_ledger_entry_with_positive_quantity(self):
		stock_entry = frappe.new_doc("Stock Entry")
		stock_entry.update(
			{
				"type": "Receipt",
				"product": self.product.name,
				"quantity": 10,
				"valuation_rate": 100.0,
				"to_warehouse": self.warehouse_a.name,
			}
		)
		stock_entry.insert()
		stock_entry.submit()

		entries = frappe.get_all(
			"Stock Entry Ledger",
			filters={"product": self.product.name},
			fields=["entry_type", "quantity_change", "warehouse"],
		)

		self.assertEqual(len(entries), 1)
		self.assertEqual(entries[0].entry_type, "Receipt")
		self.assertEqual(entries[0].quantity_change, 10)
		self.assertEqual(entries[0].warehouse, self.warehouse_a.name)

	def test_consume_creates_one_ledger_entry_with_negative_quantity(self):
		se = frappe.new_doc("Stock Entry")
		se.update(
			{
				"type": "Receipt",
				"product": self.product.name,
				"quantity": 10,
				"valuation_rate": 100.0,
				"to_warehouse": self.warehouse_a.name,
			}
		)
		se.insert()
		se.submit()

		se2 = frappe.new_doc("Stock Entry")
		se2.update(
			{
				"type": "Consume",
				"product": self.product.name,
				"quantity": 5,
				"valuation_rate": 100.0,
				"to_warehouse": self.warehouse_a.name,
			}
		)
		se2.insert()
		se2.submit()

		entries = frappe.get_all(
			"Stock Entry Ledger",
			filters={"product": self.product.name, "entry_type": "Consume"},
			fields=["quantity_change", "warehouse"],
		)

		self.assertEqual(len(entries), 1)
		self.assertEqual(entries[0].quantity_change, -5)
		self.assertEqual(entries[0].warehouse, self.warehouse_a.name)

	def test_transfer_creates_two_ledger_entries(self):
		# initialize the stock entry by reciept
		se = frappe.new_doc("Stock Entry")
		se.update({
			"type": "Receipt",
			"product": self.product.name,
			"quantity": 10,
			"valuation_rate": 100.0,
			"to_warehouse": self.warehouse_a.name,
		})
		se.insert()
		se.submit()

		se2 = frappe.new_doc("Stock Entry")
		se2.update(
			{
				"type": "Transfer",
				"product": self.product.name,
				"quantity": 5,
				"valuation_rate": 100.0,
				"from_warehouse": self.warehouse_a.name,
				"to_warehouse": self.warehouse_b.name,
			}
		)
		se2.insert()
		se2.submit()

		entries = frappe.get_all(
			"Stock Entry Ledger",
			filters={"product": self.product.name},
			fields=["entry_type", "quantity_change", "warehouse"],
			order_by="creation desc",
		)

		self.assertEqual(len(entries), 3)


		consume_entry = next(e for e in entries if e.entry_type == "Consume")
		receipt_entry = next(e for e in entries if e.entry_type == "Receipt")

		self.assertEqual(consume_entry.quantity_change, -5)
		self.assertEqual(consume_entry.warehouse, self.warehouse_a.name)

		self.assertEqual(receipt_entry.quantity_change, 5)
		self.assertEqual(receipt_entry.warehouse, self.warehouse_b.name)

	def test_valuation_rate_updates_after_submit(self):
		se = frappe.new_doc("Stock Entry")
		se.update(
			{
				"type": "Receipt",
				"product": self.product.name,
				"quantity": 5,
				"valuation_rate": 200.0,
				"to_warehouse": self.warehouse_a.name,
			}
		)
		se.insert()
		se.submit()
		self.product.reload()
		self.assertEqual(self.product.unit_price, 200.0)

		se2 = frappe.new_doc("Stock Entry")
		se2.update(
			{
				"type": "Receipt",
				"product": self.product.name,
				"quantity": 5,
				"valuation_rate": 100.0,
				"to_warehouse": self.warehouse_a.name,
			}
		)
		se2.insert()
		se2.submit()
		self.product.reload()
		self.assertEqual(self.product.unit_price, 150.0)

	def test_consume_exceeding_stock_raises_validation_error(self):
		receipt = frappe.new_doc("Stock Entry")
		receipt.update(
			{
				"type": "Receipt",
				"product": self.product.name,
				"quantity": 5,
				"valuation_rate": 100.0,
				"to_warehouse": self.warehouse_a.name,
			}
		)
		receipt.insert()
		receipt.submit()

		consume = frappe.new_doc("Stock Entry")
		consume.update(
			{
				"type": "Consume",
				"product": self.product.name,
				"quantity": 10,
				"valuation_rate": 100.0,
				"to_warehouse": self.warehouse_a.name,
			}
		)
		consume.insert()
		with self.assertRaises(frappe.ValidationError):
			consume.submit()

	def test_transfer_exceeding_source_stock_raises_validation_error(self):
		transfer = frappe.new_doc("Stock Entry")
		transfer.update(
			{
				"type": "Transfer",
				"product": self.product.name,
				"quantity": 1,
				"valuation_rate": 100.0,
				"from_warehouse": self.warehouse_a.name,
				"to_warehouse": self.warehouse_b.name,
			}
		)
		transfer.insert()
		with self.assertRaises(frappe.ValidationError):
			transfer.submit()

	def test_submitted_stock_entry_sets_posting_datetime(self):
		se = frappe.new_doc("Stock Entry")
		se.update(
			{
				"type": "Receipt",
				"product": self.product.name,
				"quantity": 1,
				"valuation_rate": 100.0,
				"to_warehouse": self.warehouse_a.name,
			}
		)
		se.insert()
		self.assertIsNotNone(se.posting_datetime)
