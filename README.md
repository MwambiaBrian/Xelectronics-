# 📦 Warehouse Management System for X Electronics

A full-featured, modular warehouse and inventory management application built with the [Frappe Framework](https://frappeframework.com/). Designed for efficient stock tracking, real-time ledger operations, and insightful reporting.

---

## 🚀 Features

### ✅ Core Modules

- **Product Management**
  - Maintain a list of stockable items.
- **Warehouse Management**
  - Tree-based warehouse structure (supports nesting of warehouses/locations).
- **Stock Ledger Entry (Stateless)**
  - Real-time, stateless stock movement tracking.
  - Moving average valuation using a single optimized SQL query.
- **Stock Entry**
  - Stock Receipt
  - Stock Consumption
  - Stock Transfer (between warehouses)

### 📊 Reports

- **Stock Ledger Report**

  - Shows item-wise movement history.

  - <img width="1360" height="452" alt="image" src="https://github.com/user-attachments/assets/db16f103-3925-41de-a598-b85efabed1ef" />

- **Stock Balance Report**
  - Shows quantity and valuation as of a given date.
  - Supports grouping and aggregation by warehouse or item.
  - <img width="1366" height="697" alt="image" src="https://github.com/user-attachments/assets/6f7a67f1-c7f8-4c4e-b0b2-b032c1d02daa" />

### 🧪 Test Coverage

- Unit tests for all core functionality (e.g. stock entry logic, validations).
- Basic unit tests for reports to ensure accurate aggregation and filtering.

---

## 📁 DocTypes Structure

| DocType              | Description                                   |
| -------------------- | --------------------------------------------- |
| `Product`            | Defines items in the system                   |
| `Warehouse`          | Tree Doctype for organizing warehouses        |
| `Stock Entry`        | User-facing document for all stock actions    |
| `Stock Ledger Entry` | Stateless system DocType for audit + tracking |

<img width="1366" height="698" alt="image" src="https://github.com/user-attachments/assets/fade84b9-172a-4767-98f9-8571d7450859" />
<img width="1360" height="653" alt="image" src="https://github.com/user-attachments/assets/6e8a4603-f85d-460d-a6a4-6613aeb10df9" />
<img width="1363" height="649" alt="image" src="https://github.com/user-attachments/assets/de93b08b-df00-4736-bfc6-a8d6280af588" />

---

## 📚 Reports

<img width="1366" height="697" alt="image" src="https://github.com/user-attachments/assets/db349f83-c980-466f-a002-c0e2e413713b" />

| Report Name     | Purpose                                      |
| --------------- | -------------------------------------------- |
| `Stock Ledger`  | Line-by-line movement details                |
| `Stock Balance` | Current value and quantity by item/warehouse |

---

<img width="1363" height="705" alt="image" src="https://github.com/user-attachments/assets/9d177e1b-a637-4036-97f8-fcc1b2fcd6c0" />

## 🧪 Running Tests

```bash
# Run all tests
bench --site xelectronics2.com run-tests --app xelectronics

# Run a specific test file
bench --site xelectronics2.com run-tests --file warehouse_mgmt/warehouse_mgmt/doctype/product/test_product.py
```

<img width="1366" height="240" alt="image" src="https://github.com/user-attachments/assets/7b2da690-ad2c-45c2-bc2a-69b821c0e658" />

## Developer Notes

# Server Scripts must be enabled in common_site_config.json:

```json
"developer_mode": 1,
"enable_server_script": 1
```

Use bench execute to trigger backend utility methods for testing.

## Installation

```bash
# Clone and get started
git clone https://github.com/MwambiaBrian/Xelectronics.git
cd Xelectronics
bench get-app Xelectronics
bench --site [yoursite] install-app Xelectronics
```
