# Copyright (c) 2025, brian and Contributors
# See license.txt
import uuid
import frappe
import unittest
from frappe.tests.utils import FrappeTestCase

class TestStockEntry(unittest.TestCase):
    def setUp(self):
        # Create test item
        unique_code = f"TEST-Tecno-{uuid.uuid4().hex[:6]}"
        self.item = frappe.get_doc({
            "doctype": "Item",
            "item_code": unique_code,
            "item_name": "Tecno",
            "uom": "Nos"
        }).insert(ignore_if_duplicate=True)

        # Create test warehouse
        unique_warehouse = f"Test Bin A-{uuid.uuid4().hex[:6]}"
        self.warehouse = frappe.get_doc({
            "doctype": "Warehouse",
            "warehouse_name": unique_warehouse
        }).insert(ignore_if_duplicate=True)

        # self.target_warehouse = frappe.get_doc({
        #     "doctype": "Warehouse",
        #     "warehouse_name": "Target Warehouse"
        # }).insert(ignore_if_duplicate=True)

    def test_receipt_entry_creates_sle(self):
        se = frappe.get_doc({
            "doctype": "Stock Entry",
            "type": "Receipt",
            "posting_datetime": frappe.utils.nowdate(),
            "to_warehouse": self.warehouse.name,
            "items": [{
                "item": self.item.name,
                "quantity": 5,
                "valuation_rate": 10000
            }]
        })
        se.insert()
        se.submit()

        sle = frappe.get_all("Stock Ledger Entry", filters={
            "voucher_no": se.name,
            "item": self.item.name,
            "warehouse": self.warehouse.name
        }, fields=["actual_quantity", "valuation_rate"])

        self.assertEqual(len(sle), 1)
        self.assertEqual(sle[0].actual_quantity, 5)
        self.assertEqual(sle[0].valuation_rate, 10000)

    def test_consume_entry_creates_sle(self):
        receipt = frappe.get_doc({
            "doctype": "Stock Entry",
            "type": "Receipt",
            "posting_datetime": frappe.utils.nowdate(),
            "to_warehouse": self.warehouse.name,
            "items": [{
                "item": self.item.name,
                "quantity": 10,
                "valuation_rate": 50
            }]
        })
        receipt.insert()
        receipt.submit() 
      
     



        consume = frappe.get_doc({
            "doctype": "Stock Entry",
            "type": "Consume",
            "posting_datetime": frappe.utils.nowdate(),
            "from_warehouse": self.warehouse.name,
            "items": [{
                "item": self.item.name,
                "quantity": 4,
                "valuation_rate": 30
            }]
        })
        consume.insert()
        consume.submit()
        sle = frappe.get_all("Stock Ledger Entry", filters={
            "voucher_no": consume.name,
            "item": self.item.name,
            "warehouse": self.warehouse.name
        }, fields=["actual_quantity", "valuation_rate"])

        self.assertEqual(len(sle), 1)
        self.assertEqual(sle[0].actual_quantity, -4)
        self.assertGreater(sle[0].valuation_rate, 0)
