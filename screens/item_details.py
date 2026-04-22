from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.graphics import Color, Line, RoundedRectangle
from database.db import items, recent_activity


class ItemDetailsScreen(Screen):
    selected_item = None

    def on_enter(self):
        self.update_view()

    def update_view(self):
        if not self.selected_item:
            return

        item = self.selected_item
        self.ids.item_name.text      = item["name"]
        self.ids.item_sku.text       = f"SKU: {item['sku']}"
        self.ids.item_quantity.text  = str(item["quantity"])
        self.ids.item_price.text     = f"${item['price']:.2f}"
        self.ids.item_threshold.text = str(item["threshold"])
        self.ids.item_restock.text   = item["last_restock"]
        self._build_history()

    def _build_history(self):
        container = self.ids.history_list
        container.clear_widgets()
        item = self.selected_item

        if not item.get("history"):
            lbl = Label(
                text="No transaction history.",
                font_size="13sp",
                color=(0.4, 0.42, 0.49, 1),
                size_hint_y=None,
                height="40dp",
                halign="left",
                valign="middle",
            )
            lbl.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))
            container.add_widget(lbl)
            return

        for record in item["history"]:
            container.add_widget(self._history_row(record))

    def _history_row(self, record):
        row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height="52dp",
            spacing="8dp",
        )

        left = BoxLayout(orientation="vertical", spacing="2dp")

        date_lbl = Label(
            text=record["date"],
            font_size="13sp",
            color=(0.133, 0.153, 0.196, 1),
            halign="left",
            valign="middle",
            size_hint_y=None,
            height="22dp",
        )
        date_lbl.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))

        note_lbl = Label(
            text=record["note"],
            font_size="12sp",
            color=(0.40, 0.42, 0.49, 1),
            halign="left",
            valign="middle",
            size_hint_y=None,
            height="18dp",
        )
        note_lbl.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))

        left.add_widget(date_lbl)
        left.add_widget(note_lbl)

        change = record["change"]
        is_positive = str(change).startswith("+")
        change_color = (0.133, 0.694, 0.298, 1) if is_positive else (0.902, 0.224, 0.224, 1)

        change_lbl = Label(
            text=change,
            font_size="13sp",
            bold=True,
            color=change_color,
            halign="right",
            valign="middle",
            size_hint=(None, 1),
            width="90dp",
        )
        change_lbl.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))

        row.add_widget(left)
        row.add_widget(change_lbl)

        with row.canvas.after:
            Color(0.878, 0.886, 0.910, 1)
            row._div = Line(points=[0, 0, 0, 0], width=1)

        def _upd(inst, val):
            inst._div.points = [inst.x, inst.y, inst.right, inst.y]

        row.bind(pos=_upd, size=_upd)
        return row

    def edit_item(self):
        self.manager.get_screen("add_item").set_edit_item(self.selected_item)
        self.manager.current = "add_item"

    def delete_item(self):
        item_name = self.selected_item["name"]

        content = BoxLayout(
            orientation="vertical",
            padding="20dp",
            spacing="16dp",
        )

        msg = Label(
            text=f"Are you sure you want to delete [b]{item_name}[/b]?\nThis cannot be undone.",
            markup=True,
            font_size="14sp",
            color=(0.133, 0.153, 0.196, 1),
            halign="center",
            valign="middle",
        )
        msg.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))

        btn_row = BoxLayout(
            size_hint_y=None,
            height="48dp",
            spacing="12dp",
        )

        cancel_btn = Button(
            text="Cancel",
            font_size="14sp",
            bold=True,
            color=(0.133, 0.153, 0.196, 1),
            background_normal="",
            background_color=(0, 0, 0, 0),
        )
        with cancel_btn.canvas.before:
            Color(0.945, 0.949, 0.965, 1)
            cancel_btn._bg = RoundedRectangle(pos=cancel_btn.pos, size=cancel_btn.size, radius=[8])
        cancel_btn.bind(
            pos=lambda i, v: setattr(i._bg, "pos", i.pos),
            size=lambda i, v: setattr(i._bg, "size", i.size),
        )

        confirm_btn = Button(
            text="Delete",
            font_size="14sp",
            bold=True,
            color=(1, 1, 1, 1),
            background_normal="",
            background_color=(0, 0, 0, 0),
        )
        with confirm_btn.canvas.before:
            Color(0.902, 0.224, 0.224, 1)
            confirm_btn._bg = RoundedRectangle(pos=confirm_btn.pos, size=confirm_btn.size, radius=[8])
        confirm_btn.bind(
            pos=lambda i, v: setattr(i._bg, "pos", i.pos),
            size=lambda i, v: setattr(i._bg, "size", i.size),
        )

        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(confirm_btn)

        content.add_widget(msg)
        content.add_widget(btn_row)

        popup = Popup(
            title="",
            content=content,
            size_hint=(0.82, None),
            height="220dp",
            separator_height=0,
            background="",
            background_color=(1, 1, 1, 1),
        )

        cancel_btn.bind(on_press=popup.dismiss)
        confirm_btn.bind(on_press=lambda _: self._confirm_delete(popup))

        popup.open()

    def _confirm_delete(self, popup):
        popup.dismiss()
        if self.selected_item in items:
            recent_activity.insert(0, f"Deleted {self.selected_item['name']} (SKU {self.selected_item['sku']})")
            if len(recent_activity) > 5:
                recent_activity.pop()
            items.remove(self.selected_item)
        self.selected_item = None
        self.manager.current = "inventory"

    def go_back(self):
        self.manager.current = "inventory"