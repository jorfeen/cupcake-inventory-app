from kivy.uix.screenmanager import Screen
from database.db import items, recent_activity
from datetime import date
import database.db as db


class AddItemScreen(Screen):
    editing_item = None

    def set_edit_item(self, item):
        self.editing_item = item

    def on_enter(self):
        self.ids.screen_title.text = "Edit Item" if self.editing_item else "Add Item"
        self.ids.save_btn.text = "Save Changes" if self.editing_item else "Save Item"
        self.ids.message.text = ""
        self.ids.threshold_input.text = "" if self.editing_item else str(db.default_threshold)
        self.populate_fields()

    def populate_fields(self):
        if not self.editing_item:
            self.ids.name_input.text = ""
            self.ids.sku_input.text = ""
            self.ids.price_input.text = ""
            self.ids.qty_input.text = ""
            return

        self.ids.name_input.text = self.editing_item["name"]
        self.ids.sku_input.text = self.editing_item["sku"]
        self.ids.price_input.text = str(self.editing_item["price"])
        self.ids.qty_input.text = str(self.editing_item["quantity"])
        self.ids.threshold_input.text = str(self.editing_item["threshold"])

    def save_item(self):
        name      = self.ids.name_input.text.strip()
        sku       = self.ids.sku_input.text.strip()
        price     = self.ids.price_input.text.strip()
        qty       = self.ids.qty_input.text.strip()
        threshold = self.ids.threshold_input.text.strip()

        if not all([name, sku, price, qty, threshold]):
            self.ids.message.text = "Please fill in all fields."
            return

        if any(i["sku"] == sku and i is not self.editing_item for i in items):
            self.ids.message.text = "Error: SKU already exists."
            return

        try:
            price     = float(price)
            qty       = int(qty)
            threshold = int(threshold)
        except ValueError:
            self.ids.message.text = "Price must be a number; qty/threshold must be integers."
            return

        if price < 0 or qty < 0 or threshold < 0:
            self.ids.message.text = "Values cannot be negative."
            return

        if self.editing_item:
            self.editing_item["name"]      = name
            self.editing_item["sku"]       = sku
            self.editing_item["price"]     = price
            self.editing_item["quantity"]  = qty
            self.editing_item["threshold"] = threshold

            recent_activity.insert(0, f"Updated {name} (SKU {sku})")
            if len(recent_activity) > 5:
                recent_activity.pop()

            self.manager.get_screen("item_details").selected_item = self.editing_item
            self.editing_item = None
            self.manager.current = "item_details"
            return

        today = date.today().strftime("%m/%d/%Y")

        item = {
            "name":         name,
            "sku":          sku,
            "price":        price,
            "quantity":     qty,
            "threshold":    threshold,
            "last_restock": today,
            "history": [{
                "date":   today,
                "change": f"+{qty} units",
                "note":   "Added new stock",
            }],
        }

        items.append(item)

        recent_activity.insert(0, f"Added {name} (SKU {sku})")
        if len(recent_activity) > 5:
            recent_activity.pop()

        self.editing_item = None
        self.manager.current = "inventory"

    def go_back(self):
        if self.editing_item:
            self.manager.current = "item_details"
        else:
            self.manager.current = "dashboard"