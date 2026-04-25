from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Line
from database.db import items


class InventoryScreen(Screen):

    def on_enter(self):
        self.current_sort = getattr(self, "current_sort", None)
        self.sort_dir = getattr(self, "sort_dir", {})
        self.update_list()
        self._update_sort_buttons()

    def sort_by(self, mode):
        if self.current_sort == mode:
            self.sort_dir[mode] = "desc" if self.sort_dir.get(mode) == "asc" else "asc"
        else:
            self.current_sort = mode
            self.sort_dir[mode] = "asc"
        self.update_list()
        self._update_sort_buttons()

    def _update_sort_buttons(self):
        for mode, btn_id, label in [("qty", "sort_qty_btn", "Qty"), ("price", "sort_price_btn", "Price")]:
            btn = self.ids[btn_id]
            if self.current_sort == mode:
                direction = self.sort_dir.get(mode, "asc")
                direction_label = "Low to High" if direction == "asc" else "High to Low"
                btn.text = f"{label}: {direction_label}"
                btn.color = (1, 1, 1, 1)
                btn.background_color = (0.102, 0.435, 0.910, 1)
            else:
                btn.text = f"Sort by {label}"
                btn.color = (0.133, 0.153, 0.196, 1)
                btn.background_color = (0.945, 0.949, 0.965, 1)

    def update_list(self):
        container = self.ids.item_list
        container.clear_widgets()

        filtered = self._filtered_items()

        if not filtered:
            lbl = Label(
                text="No inventory items yet.",
                font_size="13sp",
                color=(0.4, 0.42, 0.49, 1),
                size_hint_y=None,
                height="48dp",
                halign="left",
                valign="middle",
            )
            lbl.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))
            container.add_widget(lbl)
            return

        for item in filtered:
            container.add_widget(self._item_row(item))

    def _filtered_items(self):
        query = self.ids.search_input.text.strip().lower()
        result = (
            [i for i in items if query in i["name"].lower() or query in i["sku"].lower()]
            if query else list(items)
        )
        reverse = self.sort_dir.get(self.current_sort) == "desc"
        if self.current_sort == "qty":
            result.sort(key=lambda i: i["quantity"], reverse=reverse)
        elif self.current_sort == "price":
            result.sort(key=lambda i: i["price"], reverse=reverse)
        else:
            result.sort(key=lambda i: i["name"].lower())
        return result

    def _item_row(self, item):
        row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height="72dp",
            padding=["14dp", "10dp", "14dp", "10dp"],
            spacing="8dp",
        )

        with row.canvas.before:
            Color(1, 1, 1, 1)
            row._bg = RoundedRectangle(pos=row.pos, size=row.size, radius=[10])
            Color(0.878, 0.886, 0.910, 1)
            row._border = Line(
                rounded_rectangle=(row.x, row.y, row.width, row.height, 10),
                width=1,
            )

        def _upd(inst, val):
            inst._bg.pos  = inst.pos
            inst._bg.size = inst.size
            inst._border.rounded_rectangle = (inst.x, inst.y, inst.width, inst.height, 10)

        row.bind(pos=_upd, size=_upd)

        text_col = BoxLayout(orientation="vertical", spacing="2dp")

        name_lbl = Label(
            text=f"{item['name']} (SKU {item['sku']})",
            font_size="14sp",
            bold=True,
            color=(0.133, 0.153, 0.196, 1),
            halign="left",
            valign="middle",
            size_hint_y=None,
            height="26dp",
        )
        name_lbl.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))

        sub_lbl = Label(
            text=f"Qty: {item['quantity']}  •  ${item['price']:.2f}  •  Last restock: {item['last_restock']}",
            font_size="12sp",
            color=(0.40, 0.42, 0.49, 1),
            halign="left",
            valign="middle",
            size_hint_y=None,
            height="20dp",
        )
        sub_lbl.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))

        text_col.add_widget(name_lbl)
        text_col.add_widget(sub_lbl)

        chevron = Label(
            text=u"\u203a",
            font_size="18sp",
            color=(0.65, 0.67, 0.73, 1),
            size_hint=(None, 1),
            width="24dp",
        )

        row.add_widget(text_col)
        row.add_widget(chevron)

        row.bind(on_touch_down=lambda inst, touch, i=item: (
            self.open_item_details(i) if inst.collide_point(*touch.pos) else None
        ))

        return row

    def open_item_details(self, item):
        self.manager.get_screen("item_details").selected_item = item
        self.manager.current = "item_details"

    def go_to(self, screen_name):
        self.manager.current = screen_name