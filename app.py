"""
Project 1: Local Shop Inventory & Sales System
Command-line app in pure Python (no external libraries).

Run:
    python app.py
    python app.py --csv retail_store_inventory_data-selected-columns.csv --store S001 --date 2022-01-01
"""

import argparse
import csv
import os


# ---------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------
class InventoryItem:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

    def __repr__(self):
        return f"{self.name} | Rs.{self.price:.2f} | Qty: {self.quantity}"


class Shop:
    def __init__(self, log_file="sales_log.txt", fresh_log=False):
        self.items = {}  # name -> InventoryItem
        self.log_file = log_file
        # Sales log persists between runs unless a fresh one is requested
        if fresh_log and os.path.exists(self.log_file):
            os.remove(self.log_file)

    # ---------- Loading data ----------
    def load_starting_inventory(self, filepath, store_id, target_date):
        loaded = 0
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["Store ID"] == store_id and row["Date"] == target_date:
                        name = row["Product ID"]
                        price = float(row["Price"])
                        quantity = int(row["Inventory Level"])
                        self.items[name] = InventoryItem(name, price, quantity)
                        loaded += 1
            print(f"Loaded {loaded} items for store {store_id} on {target_date}")
        except FileNotFoundError:
            print(f"Error: Inventory file not found at '{filepath}'.")
        except KeyError as e:
            print(f"Error: CSV is missing the expected column {e}.")
        except Exception as e:
            print(f"An error occurred while loading inventory: {e}")
        return loaded

    # ---------- Core operations ----------
    def add_stock(self, name, price, quantity):
        try:
            if quantity <= 0:
                raise ValueError("Quantity must be positive.")
            if price < 0:
                raise ValueError("Price cannot be negative.")
            if name in self.items:
                self.items[name].quantity += quantity
            else:
                self.items[name] = InventoryItem(name, price, quantity)
            print(f"Added {quantity} units of {name}")
        except ValueError as e:
            print(f"Add stock failed: {e}")

    def restock(self, name, quantity):
        try:
            if name not in self.items:
                raise KeyError(
                    f"Cannot restock '{name}' - item does not exist. Use 'Add new item' first."
                )
            if quantity <= 0:
                raise ValueError("Restock quantity must be positive.")
            self.items[name].quantity += quantity
            print(f"Restocked {name}: +{quantity} units (now {self.items[name].quantity})")
        except (KeyError, ValueError) as e:
            print(f"Restock failed: {e.args[0]}")

    def sell_item(self, name, quantity):
        try:
            if name not in self.items:
                raise KeyError(f"Sale failed: '{name}' does not exist in inventory.")
            item = self.items[name]
            if quantity <= 0:
                raise ValueError("Sale quantity must be a positive number.")
            if quantity > item.quantity:
                raise ValueError(
                    f"Sale failed: only {item.quantity} units of '{name}' in stock, "
                    f"tried to sell {quantity}."
                )
            item.quantity -= quantity
            revenue = round(quantity * item.price, 2)
            self._log_sale(name, quantity, revenue)
            print(f"Sold {quantity} x {name} for Rs.{revenue:.2f}")
            return revenue
        except (KeyError, ValueError) as e:
            print(e.args[0])
            return 0

    # ---------- Sales logging ----------
    def _log_sale(self, name, quantity, revenue):
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"{name},{quantity},{revenue}\n")

    def load_sales_log(self):
        if not os.path.exists(self.log_file):
            return []
        records = []
        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    name, quantity, revenue = line.rsplit(",", 2)
                    records.append((name, int(quantity), float(revenue)))
                except ValueError:
                    continue  # skip corrupted lines
        return records

    # ---------- Reporting ----------
    def show_inventory(self):
        if not self.items:
            print("Inventory is empty.")
            return
        print(f"\n{'Item':<20}{'Price':>12}{'Qty':>8}")
        print("-" * 40)
        for item in sorted(self.items.values(), key=lambda i: i.name):
            print(f"{item.name:<20}{'Rs.' + format(item.price, '.2f'):>12}{item.quantity:>8}")
        print()

    def daily_summary(self, low_stock_threshold=20):
        sales_records = self.load_sales_log()
        if not sales_records:
            print("No sales recorded yet - nothing to summarize.")
            return

        sales_by_item = {}
        for name, qty, _ in sales_records:
            sales_by_item[name] = sales_by_item.get(name, 0) + qty

        top_item = max(sales_by_item, key=sales_by_item.get)
        total_revenue = sum(r for _, _, r in sales_records)
        low_stock = [i.name for i in self.items.values() if i.quantity < low_stock_threshold]

        print("\n----- DAILY SUMMARY -----")
        print(f"Total sales made: {len(sales_records)}")
        print(f"Top-selling item: {top_item} ({sales_by_item[top_item]} units)")
        print(f"Total revenue: Rs.{total_revenue:.2f}")
        print(f"Low stock items (< {low_stock_threshold} units): {low_stock if low_stock else 'None'}")
        print("--------------------------\n")


# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------
def ask_text(prompt):
    return input(prompt).strip()


def ask_int(prompt):
    try:
        return int(input(prompt).strip())
    except ValueError:
        print("Please enter a whole number.")
        return None


def ask_float(prompt):
    try:
        return float(input(prompt).strip())
    except ValueError:
        print("Please enter a valid number.")
        return None


# ---------------------------------------------------------------------------
# Menu
# ---------------------------------------------------------------------------
MENU = """
===== Local Shop Inventory & Sales =====
1. View inventory
2. Add new item / add stock
3. Sell item
4. Restock item
5. Daily summary
6. Exit
"""


def main():
    parser = argparse.ArgumentParser(description="Local Shop Inventory & Sales System")
    parser.add_argument("--csv", help="Path to inventory CSV file")
    parser.add_argument("--store", default="S001", help="Store ID to load (default: S001)")
    parser.add_argument("--date", default="2022-01-01", help="Date to load (default: 2022-01-01)")
    parser.add_argument("--log", default="sales_log.txt", help="Sales log file path")
    parser.add_argument("--fresh", action="store_true", help="Clear the sales log at start")
    args = parser.parse_args()

    shop = Shop(log_file=args.log, fresh_log=args.fresh)

    if args.csv:
        shop.load_starting_inventory(args.csv, args.store, args.date)
    else:
        print("No CSV given - starting with an empty inventory. "
              "(Use --csv <file> to load starting stock.)")

    while True:
        print(MENU)
        choice = ask_text("Choose an option (1-6): ")

        if choice == "1":
            shop.show_inventory()

        elif choice == "2":
            name = ask_text("Item name: ")
            if not name:
                print("Item name cannot be empty.")
                continue
            price = shop.items[name].price if name in shop.items else ask_float("Price (Rs.): ")
            qty = ask_int("Quantity: ")
            if price is not None and qty is not None:
                shop.add_stock(name, price, qty)

        elif choice == "3":
            name = ask_text("Item name: ")
            qty = ask_int("Quantity to sell: ")
            if qty is not None:
                shop.sell_item(name, qty)

        elif choice == "4":
            name = ask_text("Item name: ")
            qty = ask_int("Quantity to restock: ")
            if qty is not None:
                shop.restock(name, qty)

        elif choice == "5":
            shop.daily_summary()

        elif choice == "6":
            print("Goodbye!")
            break

        else:
            print("Invalid option. Please enter a number from 1 to 6.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
