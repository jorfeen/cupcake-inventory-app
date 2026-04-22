from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Line
from database.db import items, recent_activity


class DashboardScreen(Screen):

    def on_enter(self):
        self.update_stats()
        self.update_low_stock()
        self.update_recent_activity()

    def update_stats(self):
        self.ids.total_items.text = str(len(items))
        low_stock = [i for i in items if i["quantity"] <= i["threshold"]]
        self.ids.low_stock_count.text = str(len(low_stock))
        total_value = sum(i["quantity"] * i["price"] for i in items)
        self.ids.inventory_value.text = f"${total_value:,.2f}"


    def update_low_stock(self):
        container = self.ids.low_stock_list
        container.clear_widgets()
        low_stock = [i for i in items if i["quantity"] <= i["threshold"]]

        if not low_stock:
            container.add_widget(self._empty_label("No low stock items."))
            return

        for item in low_stock[:5]:
            container.add_widget(self._list_row(
                f"{item['name']} - Qty: {item['quantity']}"
            ))


    def update_recent_activity(self):
        container = self.ids.activity_list
        container.clear_widgets()

        if not recent_activity:
            container.add_widget(self._empty_label("No recent activity."))
            return

        for activity in recent_activity[:5]:
            container.add_widget(self._list_row(activity))


    def _empty_label(self, text):
        lbl = Label(
            text=text,
            font_size="13sp",
            color=(0.4, 0.42, 0.49, 1),
            size_hint_y=None,
            height="40dp",
            halign="left",
            valign="middle",
        )
        lbl.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))
        return lbl

    def _list_row(self, main):
        row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height="44dp",
        )

        lbl = Label(
            text=main,
            font_size="13sp",
            color=(0.133, 0.153, 0.196, 1),
            halign="left",
            valign="middle",
        )
        lbl.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))

        chevron = Label(
            text="›",
            font_size="22sp",
            color=(0.65, 0.67, 0.73, 1),
            size_hint=(None, 1),
            width="28dp",
            halign="center",
            valign="middle",
        )
        chevron.bind(size=lambda i, v: setattr(i, "text_size", i.size))

        row.add_widget(lbl)
        row.add_widget(chevron)

        with row.canvas.after:
            Color(0.878, 0.886, 0.910, 1)
            row._div = Line(points=[0, 0, 0, 0], width=1)

        def _upd(inst, val):
            inst._div.points = [inst.x, inst.y, inst.right, inst.y]

        row.bind(pos=_upd, size=_upd)
        return row


    def go_to_add_item(self):
        self.manager.get_screen("add_item").set_edit_item(None)
        self.manager.current = "add_item"

    def go_to(self, screen_name):
        self.manager.current = screen_name