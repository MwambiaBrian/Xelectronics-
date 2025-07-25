# Copyright (c) 2025, brian and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime


class StockEntry(Document):
    def on_submit(self):
        frappe.msgprint(f"Processing {len(self.items)} items")
        if self.type == "Receipt":
            for row in self.items:
                frappe.get_doc(
                    {
                        "doctype": "Stock Ledger Entry",
                        "item": row.item,
                        "warehouse": self.to_warehouse,
                        "posting_date": self.posting_datetime,
                        "actual_quantity": row.quantity,
                        "valuation_rate": row.valuation_rate,
                        "voucher_type": "Stock Entry",
                        "voucher_no": self.name,
                    }
                ).insert()
                frappe.db.commit()

        elif self.type == "Consume":
            for row in self.items:
                # fetch current valuation
                valuation_rate = self.get_current_valuation_rate(
                    row.item, self.from_warehouse
                )

                # get total available quantity
                available_quantity = self.get_available_quantity(
                    row.item, self.from_warehouse
                )

                if row.quantity > available_quantity:
                    frappe.throw(
                        f"Cannot consume {row.quantity} units of item {row.item} from {self.from_warehouse}. "
                        f"Only {available_quantity} units available."
                    )

                frappe.get_doc(
                    {
                        "doctype": "Stock Ledger Entry",
                        "item": row.item,
                        "warehouse": self.from_warehouse,
                        "posting_date": self.posting_datetime,
                        "actual_quantity": -row.quantity,
                        "valuation_rate": valuation_rate,
                        "voucher_type": "Stock Entry",
                        "voucher_no": self.name,
                    }
                ).insert()

        elif self.type == "Transfer":
            for row in self.items:
                # get total available quantity
                available_quantity = self.get_available_quantity(
                    row.item, self.from_warehouse
                )

                if row.quantity > available_quantity:
                    frappe.throw(
                        f"Cannot transfer {row.quantity} units of item {row.item} from {self.from_warehouse}. "
                        f"Only {available_quantity} units available."
                    )

                # get valuation rate from the source warehouse
                valuation_rate = self.get_current_valuation_rate(
                    row.item, self.from_warehouse
                )

                # oubound entry
                frappe.get_doc(
                    {
                        "doctype": "Stock Ledger Entry",
                        "item": row.item,
                        "warehouse": self.from_warehouse,
                        "posting_date": self.posting_datetime,
                        "actual_quantity": -row.quantity,
                        "valuation_rate": valuation_rate,
                        "voucher_type": "Stock Entry",
                        "voucher_no": self.name,
                    }
                ).insert()

                # inbound entry
                frappe.get_doc(
                    {
                        "doctype": "Stock Ledger Entry",
                        "item": row.item,
                        "warehouse": self.to_warehouse,
                        "posting_date": self.posting_datetime,
                        "actual_quantity": row.quantity,
                        "valuation_rate": valuation_rate,
                        "voucher_type": "Stock Entry",
                        "voucher_no": self.name,
                    }
                ).insert()

    def validate(self):
        # set posting_date to current date if not specified
        if not self.posting_datetime:
            self.posting_datetime = datetime.strptime(
                frappe.utils.today(), "%Y-%m-%d"
            ).date()

        # ensure posing date is not in the future
        today = datetime.strptime(frappe.utils.today(), "%Y-%m-%d").date()

        # get date version of posting date string
        if isinstance(self.posting_datetime, str):
            self.posting_datetime = datetime.strptime(self.posting_datetime, "%Y-%m-%d").date()

        if self.posting_datetime > today:
            frappe.throw("Posting date cannot be in the future!")

        if not self.items:
            frappe.throw("Please add at least one item to the Stock Entry!")

        for row in self.items:
            # ensure quantity > 0
            if not row.quantity or row.quantity <= 0:
                frappe.throw(f"Quantity must be greater than zero for {row.item}")

            # ensure correct warehouse on entry
            if self.type == "Receipt":
                if not self.to_warehouse:
                    frappe.throw(
                        f"To warehouse is required for receipt item - {row.item}"
                    )
                if self.from_warehouse:
                    frappe.thow(f"From warehouse must be blank for {row.item}")

                # ensure warehouse is a leaf
                is_group = frappe.db.get_value(
                    "Warehouse", self.to_warehouse, "is_group"
                )

                if is_group:
                    frappe.throw(
                        f"To warehouse must be a leaf node (not a group) for item {row.item}!"
                    )

                if not row.valuation_rate or row.valuation_rate <= 0:
                    frappe.throw(
                        f"Valuation rate on receopt entry must be valid and greater than 0!"
                    )

            elif self.type == "Consume":
                if not self.from_warehouse:
                    frappe.throw(
                        f"From warehouse is required for receipt item - {row.item}"
                    )
                if self.to_warehouse:
                    frappe.thow(f"To warehouse must be blank for {row.item}")

                # ensure warehouse is a leaf
                is_group = frappe.db.get_value(
                    "Warehouse", self.from_warehouse, "is_group"
                )

                if is_group:
                    frappe.throw(
                        f"From warehouse must be a leaf node (not a group) for item {row.item}"
                    )

            elif self.type == "Transfer":
                if not self.from_warehouse or not self.to_warehouse:
                    frappe.throw(
                        f"Both From and To Warehouses are required for Transfer (item {row.item})"
                    )
                if self.from_warehouse == self.to_warehouse:
                    frappe.throw(
                        f"From and To Warehouses cannot be the same for item {row.item}"
                    )

                # ensure warehouse is a leaf
                from_wh_is_group = frappe.db.get_value(
                    "Warehouse", self.from_warehouse, "is_group"
                )
                to_wh_is_group = frappe.db.get_value(
                    "Warehouse", self.from_warehouse, "is_group"
                )

                if from_wh_is_group:
                    frappe.throw(
                        f"From warehouse must be a leaf node (not a group) for item {row.item}"
                    )

                if to_wh_is_group:
                    frappe.throw(
                        f"To warehouse must be a leaf node (not a group) for item {row.item}"
                    )

    def get_current_valuation_rate(self, item, warehouse):
        # formula => valuation_rate = total_stock_value / total_stock_qty
        result = frappe.db.sql(
            """
            SELECT COALESCE(SUM(actual_quantity * valuation_rate), 0) as total_value,
                   COALESCE(SUM(actual_quantity), 0) as total_quantity
            FROM `tabStock Ledger Entry`
            WHERE item = %s AND warehouse = %s
        """,
            (item, warehouse),
        )
        total_value, total_quantity = result[0]

        if total_quantity <= 0:
            return 0

        return total_value / total_quantity

    def get_available_quantity(self, item, warehouse):
        return frappe.db.sql(
            """
                SELECT COALESCE(SUM(actual_quantity), 0)
                FROM `tabStock Ledger Entry`
                WHERE item = %s AND warehouse = %s
            """,
            (item, warehouse),
        )[0][0]