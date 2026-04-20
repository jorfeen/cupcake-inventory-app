from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from database.db import items
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label


class BaseScreen(Screen):
    def build_layout(self, title):
        root = BoxLayout(orientation="vertical")

        nav = BoxLayout(size_hint_y=None, height=50)

        for name, screen in [
            ("Dashboard", "dashboard"),
            ("Inventory", "inventory"),
            ("Reports", "reports"),
            ("Settings", "settings"),
        ]:
            btn = Button(text=name)
            btn.bind(on_press=lambda x, s=screen: self.switch_screen(s))
            nav.add_widget(btn)

        root.add_widget(nav)

        root.add_widget(Label(text=title, size_hint_y=None, height=40))

        return root

    def switch_screen(self, screen_name):
        self.manager.current = screen_name


class DashboardScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        layout = self.build_layout("Dashboard")

        layout.add_widget(Label(text="Total / Low Stock / Inventory Value"))
        layout.add_widget(Label(text="Low Stock Alerts"))
        layout.add_widget(Label(text="Recent Activity"))

        add_btn = Button(text="+", size_hint=(None, None), size=(60, 60),
                         pos_hint={"right": 1, "y": 0})
        add_btn.bind(on_press=lambda x: self.switch_screen("add_item"))
        layout.add_widget(add_btn)

        self.add_widget(layout)


class InventoryScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        layout = self.build_layout("Inventory")

        layout.add_widget(Label(text="Search Bar", size_hint_y=None, height=40))
        layout.add_widget(Label(text="Sort Options", size_hint_y=None, height=40))

        scroll = ScrollView()
        item_list = BoxLayout(orientation="vertical", size_hint_y=None, spacing=10, padding=10)
        item_list.bind(minimum_height=item_list.setter("height"))

        if not items:
            item_list.add_widget(Label(text="No inventory items yet.", size_hint_y=None, height=40))
        else:
            for item in items:
                item_text = (
                    f"{item['name']} (SKU {item['sku']})\n"
                    f"Qty: {item['quantity']} • ${item['price']:.2f} • Last restock: {item['last_restock']}"
                )
                btn = Button(
                    text=item_text,
                    size_hint_y=None,
                    height=80,
                    halign="left",
                    valign="middle"
                )
                btn.text_size = (btn.width - 20, None)
                btn.bind(size=self.update_text_size)
                btn.bind(on_press=lambda _, selected=item: self.open_item_details(selected))
                item_list.add_widget(btn)

        scroll.add_widget(item_list)
        layout.add_widget(scroll)

        self.add_widget(layout)

    def update_text_size(self, instance, value):
        instance.text_size = (instance.width - 20, None)

    def open_item_details(self, item):
        self.manager.get_screen("item_details").selected_item = item
        self.manager.current = "item_details"


class ItemDetailsScreen(BaseScreen):
    selected_item = None

    def on_enter(self):
        self.clear_widgets()
        layout = self.build_layout("Item Details")

        if not self.selected_item:
            layout.add_widget(Label(text="No item selected"))
            self.add_widget(layout)
            return

        item = self.selected_item

        layout.add_widget(Label(text=f"Name: {item['name']}", size_hint_y=None, height=40))
        layout.add_widget(Label(text=f"SKU: {item['sku']}", size_hint_y=None, height=40))
        layout.add_widget(Label(text=f"Quantity: {item['quantity']}", size_hint_y=None, height=40))
        layout.add_widget(Label(text=f"Price: ${item['price']:.2f}", size_hint_y=None, height=40))
        layout.add_widget(Label(text=f"Stock Threshold: {item['threshold']}", size_hint_y=None, height=40))
        layout.add_widget(Label(text=f"Last Restock: {item['last_restock']}", size_hint_y=None, height=40))

        button_row = BoxLayout(size_hint_y=None, height=50, spacing=10)
        edit_btn = Button(text="Edit")
        delete_btn = Button(text="Delete")

        edit_btn.bind(on_press=self.edit_item)
        delete_btn.bind(on_press=self.delete_item)

        button_row.add_widget(edit_btn)
        button_row.add_widget(delete_btn)
        layout.add_widget(button_row)

        layout.add_widget(Label(text="Transaction History", size_hint_y=None, height=40))

        history_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=5)
        history_box.bind(minimum_height=history_box.setter("height"))

        for record in item["history"]:
            text = f"{record['date']} | {record['change']} | {record['note']}"
            history_box.add_widget(Label(text=text, size_hint_y=None, height=30))

        history_scroll = ScrollView(size_hint=(1, 1))
        history_scroll.add_widget(history_box)
        layout.add_widget(history_scroll)

        self.add_widget(layout)

    def edit_item(self, instance):
        print("Edit functionality coming next.")

    def delete_item(self, instance):
        if self.selected_item in items:
            items.remove(self.selected_item)
        self.selected_item = None
        self.manager.current = "inventory"


class AddItemScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        layout = self.build_layout("Add Item")

        self.name_input = TextInput(hint_text="Item Name", multiline=False)
        self.sku_input = TextInput(hint_text="SKU", multiline=False)
        self.price_input = TextInput(hint_text="Unit Price", multiline=False)
        self.qty_input = TextInput(hint_text="Starting Quantity", multiline=False)
        self.threshold_input = TextInput(hint_text="Stock Threshold", multiline=False)

        layout.add_widget(self.name_input)
        layout.add_widget(self.sku_input)
        layout.add_widget(self.price_input)
        layout.add_widget(self.qty_input)
        layout.add_widget(self.threshold_input)

        save_btn = Button(text="Save Item", size_hint_y=None, height=50)
        save_btn.bind(on_press=self.save_item)
        layout.add_widget(save_btn)

        self.message = Label(text="", size_hint_y=None, height=40)
        layout.add_widget(self.message)

        self.add_widget(layout)

    def save_item(self, instance):
        name = self.name_input.text.strip()
        sku = self.sku_input.text.strip()
        price = self.price_input.text.strip()
        qty = self.qty_input.text.strip()
        threshold = self.threshold_input.text.strip()

        if not all([name, sku, price, qty, threshold]):
            self.message.text = "Error: Fill all fields"
            return

        if any(item["sku"] == sku for item in items):
            self.message.text = "Error: SKU already exists"
            return

        try:
            price = float(price)
            qty = int(qty)
            threshold = int(threshold)
        except ValueError:
            self.message.text = "Error: Price must be number, qty/threshold must be integers"
            return

        if price < 0 or qty < 0 or threshold < 0:
            self.message.text = "Error: Values cannot be negative"
            return

        item = {
            "name": name,
            "sku": sku,
            "price": price,
            "quantity": qty,
            "threshold": threshold,
            "last_restock": "04/20/2026",
            "history": [
                {
                    "date": "04/20/2026",
                    "change": f"+{qty} units",
                    "note": "Added new stock"
                }
            ]
        }

        items.append(item)

        self.message.text = "Item saved!"

        self.name_input.text = ""
        self.sku_input.text = ""
        self.price_input.text = ""
        self.qty_input.text = ""
        self.threshold_input.text = ""

        self.manager.current = "inventory"


class ReportsScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        layout = self.build_layout("Reports")

        layout.add_widget(Label(text="Select Report Type"))
        layout.add_widget(Button(text="Generate Report"))
        layout.add_widget(Label(text="Summary"))

        self.add_widget(layout)


class SettingsScreen(BaseScreen):
    def on_enter(self):
        self.clear_widgets()
        layout = self.build_layout("Settings")

        layout.add_widget(Label(text="Dark Mode Toggle"))
        layout.add_widget(Label(text="Default Stock Threshold"))
        layout.add_widget(Button(text="Reset Settings"))

        self.add_widget(layout)


class InventoryApp(App):
    def build(self):
        sm = ScreenManager()

        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(InventoryScreen(name="inventory"))
        sm.add_widget(ItemDetailsScreen(name="item_details"))
        sm.add_widget(AddItemScreen(name="add_item"))
        sm.add_widget(ReportsScreen(name="reports"))
        sm.add_widget(SettingsScreen(name="settings"))

        return sm


if __name__ == "__main__":
    InventoryApp().run()