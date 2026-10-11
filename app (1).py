"""
Project 1: Local Shop Inventory & Sales System  (Streamlit version)

Run locally:   streamlit run app.py
Deploy:        push app.py + requirements.txt (+ your CSV) to GitHub, then deploy on Streamlit Cloud.
"""

import csv
import io
import os

import streamlit as st

DEFAULT_CSV = "retail_store_inventory_data-selected-columns.csv"


# ---------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------
class InventoryItem:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity


class Shop:
    def __init__(self, log_file="sales_log.txt"):
        self.items = {}      # name -> InventoryItem
        self.sales = []      # list of (name, quantity, revenue) for this session
        self.log_file = log_file

    # ---------- Loading ----------
    def load_inventory_from_text(self, text, store_id, target_date):
        loaded = 0
        reader = csv.DictReader(io.StringIO(text))
        for row in reader:
            if row["Store ID"] == store_id and row["Date"] == target_date:
                name = row["Product ID"]
                self.items[name] = InventoryItem(
                    name, float(row["Price"]), int(row["Inventory Level"])
                )
                loaded += 1
        return loaded

    # ---------- Core operations (each returns (ok, message)) ----------
    def add_stock(self, name, price, quantity):
        if not name:
            return False, "Item name cannot be empty."
        if quantity <= 0:
            return False, "Quantity must be positive."
        if price < 0:
            return False, "Price cannot be negative."
        if name in self.items:
            self.items[name].quantity += quantity
        else:
            self.items[name] = InventoryItem(name, price, quantity)
        return True, f"Added {quantity} units of {name}."

    def restock(self, name, quantity):
        if name not in self.items:
            return False, f"Cannot restock '{name}' - item does not exist."
        if quantity <= 0:
            return False, "Restock quantity must be positive."
        self.items[name].quantity += quantity
        return True, f"Restocked {name}: +{quantity} units (now {self.items[name].quantity})."

    def sell_item(self, name, quantity):
        if name not in self.items:
            return False, f"Sale failed: '{name}' does not exist in inventory."
        item = self.items[name]
        if quantity <= 0:
            return False, "Sale quantity must be a positive number."
        if quantity > item.quantity:
            return False, (f"Sale failed: only {item.quantity} units of '{name}' "
                           f"in stock, tried to sell {quantity}.")
        item.quantity -= quantity
        revenue = round(quantity * item.price, 2)
        self.sales.append((name, quantity, revenue))
        self._log_sale(name, quantity, revenue)
        return True, f"Sold {quantity} x {name} for Rs.{revenue:.2f}."

    def _log_sale(self, name, quantity, revenue):
        # File logging is best-effort (cloud hosts may have read-only/ephemeral disks)
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"{name},{quantity},{revenue}\n")
        except OSError:
            pass

    # ---------- Reporting ----------
    def summary(self, low_stock_threshold=20):
        if not self.sales:
            return None
        sales_by_item = {}
        for name, qty, _ in self.sales:
            sales_by_item[name] = sales_by_item.get(name, 0) + qty
        top_item = max(sales_by_item, key=sales_by_item.get)
        return {
            "count": len(self.sales),
            "top_item": top_item,
            "top_units": sales_by_item[top_item],
            "revenue": sum(r for _, _, r in self.sales),
            "low_stock": [i.name for i in self.items.values()
                          if i.quantity < low_stock_threshold],
            "by_item": sales_by_item,
        }


# ---------------------------------------------------------------------------
# Streamlit helpers
# ---------------------------------------------------------------------------
def show_result(ok, msg):
    (st.success if ok else st.error)(msg)


def inventory_rows(shop):
    return [
        {"Item": i.name, "Price (Rs.)": round(i.price, 2), "Quantity": i.quantity}
        for i in sorted(shop.items.values(), key=lambda i: i.name)
    ]


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Local Shop Inventory & Sales", page_icon="🛒", layout="wide")
st.title("🛒 Local Shop Inventory & Sales System")

if "shop" not in st.session_state:
    st.session_state.shop = Shop()
shop = st.session_state.shop

# ----- Sidebar: load starting inventory -----
with st.sidebar:
    st.header("Load starting inventory")
    store_id = st.text_input("Store ID", value="S001")
    target_date = st.text_input("Date (YYYY-MM-DD)", value="2022-01-01")
    uploaded = st.file_uploader("Inventory CSV", type="csv")
    st.caption(f"If nothing is uploaded, the app looks for `{DEFAULT_CSV}` next to app.py.")

    if st.button("Load inventory", width="stretch"):
        text = None
        if uploaded is not None:
            text = uploaded.getvalue().decode("utf-8")
        elif os.path.exists(DEFAULT_CSV):
            with open(DEFAULT_CSV, "r", encoding="utf-8") as f:
                text = f.read()

        if text is None:
            st.error("No CSV found. Upload a file or add it to the repo.")
        else:
            try:
                n = shop.load_inventory_from_text(text, store_id.strip(), target_date.strip())
                if n:
                    st.success(f"Loaded {n} items for store {store_id} on {target_date}.")
                else:
                    st.warning("No rows matched that Store ID and date.")
            except KeyError as e:
                st.error(f"CSV is missing the expected column {e}.")
            except Exception as e:
                st.error(f"Error loading inventory: {e}")

    st.divider()
    low_threshold = st.number_input("Low-stock threshold", min_value=1, value=20, step=1)

# ----- Tabs -----
tab_inv, tab_sell, tab_stock, tab_summary = st.tabs(
    ["📦 Inventory", "💰 Sell", "➕ Add / Restock", "📊 Daily Summary"]
)

with tab_inv:
    rows = inventory_rows(shop)
    if rows:
        st.dataframe(rows, width="stretch", hide_index=True)
    else:
        st.info("Inventory is empty. Load a CSV from the sidebar or add items in the Add / Restock tab.")

with tab_sell:
    if not shop.items:
        st.info("No items to sell yet.")
    else:
        with st.form("sell_form", clear_on_submit=True):
            name = st.selectbox("Item", sorted(shop.items))
            qty = st.number_input("Quantity", min_value=1, value=1, step=1)
            if st.form_submit_button("Record sale"):
                show_result(*shop.sell_item(name, int(qty)))

with tab_stock:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Add new item / add stock")
        with st.form("add_form", clear_on_submit=True):
            new_name = st.text_input("Item name").strip()
            new_price = st.number_input("Price (Rs.)", min_value=0.0, value=10.0, step=0.5)
            new_qty = st.number_input("Quantity", min_value=1, value=10, step=1, key="add_qty")
            if st.form_submit_button("Add stock"):
                show_result(*shop.add_stock(new_name, float(new_price), int(new_qty)))

    with col2:
        st.subheader("Restock existing item")
        if not shop.items:
            st.info("No items to restock yet.")
        else:
            with st.form("restock_form", clear_on_submit=True):
                r_name = st.selectbox("Item", sorted(shop.items), key="restock_item")
                r_qty = st.number_input("Quantity", min_value=1, value=10, step=1, key="restock_qty")
                if st.form_submit_button("Restock"):
                    show_result(*shop.restock(r_name, int(r_qty)))

with tab_summary:
    s = shop.summary(low_stock_threshold=int(low_threshold))
    if s is None:
        st.info("No sales recorded yet - nothing to summarize.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total revenue", f"Rs.{s['revenue']:.2f}")
        c2.metric("Top-selling item", s["top_item"], f"{s['top_units']} units")
        c3.metric("Sales made", s["count"])

        st.subheader("Units sold per item")
        st.bar_chart(s["by_item"])

        st.subheader(f"Low-stock items (< {int(low_threshold)} units)")
        if s["low_stock"]:
            st.warning(", ".join(s["low_stock"]))
        else:
            st.success("None")
