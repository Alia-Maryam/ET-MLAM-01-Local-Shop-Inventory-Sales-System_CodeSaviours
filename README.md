# ET-MLAM-01-Local-Shop-Inventory-Sales-System_CodeSaviours
# 🛒 Local Shop Inventory & Sales System

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

A Python-based system for managing a local shop's inventory and recording sales. It tracks stock levels, processes sales, updates inventory automatically, and generates simple reports.

## 🔍 Overview
Small shops often track stock and sales by hand, which leads to errors and stock-outs. This project digitizes that workflow: add products, sell items, monitor stock, and review sales.

## ✨ Features
- Add, update, and remove products
- Track quantity, price, and category `<confirm>`
- Record sales and update stock automatically
- Low-stock alerts `<confirm>`
- Sales summary and total revenue `<confirm>`
- Data storage using `<add: lists/dicts, CSV, pandas, SQLite>`

## 🛠 Tech Stack
Python, `<add: pandas, datetime, etc.>`, Jupyter Notebook

## ⚙ Installation
```bash
git clone https://github.com/<your-username>/local-shop-inventory-system.git
cd local-shop-inventory-system
pip install jupyter pandas
jupyter notebook
```

## 💻 Usage (example structure, adapt to your code)

### Add a Product
```python
inventory = {}

def add_product(name, price, quantity):
    inventory[name] = {"price": price, "quantity": quantity}

add_product("Rice 5kg", 950, 40)
add_product("Cooking Oil 1L", 480, 25)
```

### Record a Sale
```python
sales = []

def sell_product(name, qty):
    if name not in inventory:
        return "Product not found"
    if inventory[name]["quantity"] < qty:
        return "Insufficient stock"
    inventory[name]["quantity"] -= qty
    total = inventory[name]["price"] * qty
    sales.append({"product": name, "qty": qty, "total": total})
    return f"Sold {qty} x {name} = Rs. {total}"

print(sell_product("Rice 5kg", 2))
```

### Low-Stock Report
```python
def low_stock(threshold=10):
    return {k: v["quantity"] for k, v in inventory.items() if v["quantity"] <= threshold}
```

### Sales Summary
```python
def total_revenue():
    return sum(s["total"] for s in sales)

print("Total revenue:", total_revenue())
```

## 📈 Sample Output
```
Sold 2 x Rice 5kg = Rs. 1900
Total revenue: 1900
```
> Replace with real output from your notebook.

## 📁 Project Structure
```
├── Project_1_Local_Shop_Inventory_Sales_System.ipynb
├── data/            # optional CSV files
└── README.md
```

## 🚀 Future Improvements
- Add a GUI or web interface (Tkinter, Streamlit, Flask)
- Persistent storage with SQLite
- Barcode scanning support
- Profit and sales trend charts
- Multi-user login

## 👤 Author
Alia Maryam
