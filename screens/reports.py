from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.graphics import Color, Line, RoundedRectangle
from database.db import items


REPORT_TYPES = ["Summary", "Low Stock", "Top Quantity", "Lowest Quantity"]


class ReportsScreen(Screen):
    selected_report = "Summary"

    def on_enter(self):
        self.ids.report_type_btn.text = self.selected_report + "  ▾"
        self._hide_all()

    # ── Visibility helpers ─────────────────────────────────────────────────────

    def _hide_all(self):
        self._set_card_visible(self.ids.summary_card, False)
        self._set_card_visible(self.ids.low_stock_list_card, False)

    def _show_summary(self):
        self._set_card_visible(self.ids.summary_card, False)
        self._set_card_visible(self.ids.low_stock_list_card, True)

    def _show_low_stock(self):
        self._set_card_visible(self.ids.summary_card, False)
        self._set_card_visible(self.ids.low_stock_list_card, True)

    def _show_both(self):
        self._set_card_visible(self.ids.summary_card, True)
        self._set_card_visible(self.ids.low_stock_list_card, True)

    def _set_card_visible(self, card, visible):
        card.opacity = 1 if visible else 0
        card.size_hint_y = None if visible else None
        if not visible:
            card.saved_height = card.height
            card.height = 0
        else:
            card.height = card.minimum_height

    # ── Dropdown ───────────────────────────────────────────────────────────────

    def open_dropdown(self):
        content = BoxLayout(orientation="vertical", spacing=0, padding=0)

        popup = Popup(
            title="",
            content=content,
            size_hint=(0.75, None),
            height=str(len(REPORT_TYPES) * 49) + "dp",
            separator_height=0,
            background="",
            background_color=(1, 1, 1, 1),
        )

        for report in REPORT_TYPES:
            btn = Button(
                text=report,
                font_size="14sp",
                color=(0.133, 0.153, 0.196, 1),
                background_normal="",
                background_color=(0, 0, 0, 0),
                size_hint_y=None,
                height="48dp",
            )
            with btn.canvas.before:
                Color(1, 1, 1, 1)
                btn._bg = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[0])
            btn.bind(
                pos=lambda i, v: setattr(i._bg, "pos", i.pos),
                size=lambda i, v: setattr(i._bg, "size", i.size),
            )
            btn.bind(on_press=lambda _, rpt=report: self._select_report(rpt, popup))
            content.add_widget(btn)

            div = BoxLayout(size_hint_y=None, height="1dp")
            with div.canvas.before:
                Color(0.878, 0.886, 0.910, 1)
                div._bg = RoundedRectangle(pos=div.pos, size=div.size, radius=[0])
            div.bind(
                pos=lambda i, v: setattr(i._bg, "pos", i.pos),
                size=lambda i, v: setattr(i._bg, "size", i.size),
            )
            content.add_widget(div)

        popup.open()

    def _select_report(self, report, popup):
        self.selected_report = report
        self.ids.report_type_btn.text = report + "  ▾"
        self._hide_all()
        popup.dismiss()

    # ── Generate ───────────────────────────────────────────────────────────────

    def generate_report(self):
        if self.selected_report == "Summary":
            self._generate_summary()
        elif self.selected_report == "Low Stock":
            self._generate_low_stock()
        elif self.selected_report == "Top Quantity":
            self._generate_top_quantity()
        elif self.selected_report == "Lowest Quantity":
            self._generate_lowest_quantity()

    def _generate_summary(self):
        total_value    = sum(i["quantity"] * i["price"] for i in items)
        low_stock      = [i for i in items if i["quantity"] <= i["threshold"]]
        highest_item   = max(items, key=lambda i: i["quantity"]) if items else None
        lowest_item    = min(items, key=lambda i: i["quantity"]) if items else None
        recent_restock = max(items, key=lambda i: i["last_restock"]) if items else None

        self.ids.total_value.text     = f"${total_value:,.2f}"
        self.ids.low_stock_count.text = str(len(low_stock))
        self.ids.total_items.text     = str(len(items))
        self.ids.top_selling.text     = f"{highest_item['name']} — {highest_item['quantity']} units" if highest_item else "—"
        self.ids.lowest_stock.text    = f"{lowest_item['name']} — {lowest_item['quantity']} units" if lowest_item else "—"
        self.ids.recent_restock.text  = f"{recent_restock['name']} — {recent_restock['last_restock']}" if recent_restock else "—"

        self._build_low_stock_list(low_stock)
        self._show_both()

    def _generate_low_stock(self):
        low_stock = [i for i in items if i["quantity"] <= i["threshold"]]
        low_stock.sort(key=lambda i: i["quantity"])
        self._build_low_stock_list(low_stock)
        self._show_low_stock()

    def _generate_top_quantity(self):
        sorted_items = sorted(items, key=lambda i: i["quantity"], reverse=True)[:5]
        self._build_quantity_list(sorted_items, color=(0.133, 0.694, 0.298, 1))
        self._show_low_stock()  # reuses the same card

    def _generate_lowest_quantity(self):
        sorted_items = sorted(items, key=lambda i: i["quantity"])[:5]
        self._build_quantity_list(sorted_items, color=(0.902, 0.224, 0.224, 1))
        self._show_low_stock()  # reuses the same card

    # ── List builders ──────────────────────────────────────────────────────────

    def _build_low_stock_list(self, low_stock):
        container = self.ids.low_stock_list
        container.clear_widgets()

        self.ids.low_stock_list_card_title.text = "Low Stock Details"

        if not low_stock:
            container.add_widget(self._empty_label("No low stock items."))
            return

        for item in low_stock:
            row = self._detail_row(
                left=f"{item['name']} (SKU {item['sku']})",
                right=f"{item['quantity']} / {item['threshold']}",
                right_color=(0.902, 0.224, 0.224, 1),
            )
            container.add_widget(row)

    def _build_quantity_list(self, sorted_items, color):
        container = self.ids.low_stock_list
        container.clear_widgets()

        title = "Top 5 by Quantity" if color == (0.133, 0.694, 0.298, 1) else "Lowest 5 by Quantity"
        self.ids.low_stock_list_card_title.text = title

        if not sorted_items:
            container.add_widget(self._empty_label("No items found."))
            return

        for item in sorted_items:
            row = self._detail_row(
                left=f"{item['name']} (SKU {item['sku']})",
                right=f"{item['quantity']} units",
                right_color=color,
            )
            container.add_widget(row)

    def _detail_row(self, left, right, right_color):
        row = BoxLayout(orientation="horizontal", size_hint_y=None, height="44dp")

        left_lbl = Label(
            text=left,
            font_size="13sp",
            color=(0.133, 0.153, 0.196, 1),
            halign="left",
            valign="middle",
        )
        left_lbl.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))

        right_lbl = Label(
            text=right,
            font_size="13sp",
            bold=True,
            color=right_color,
            halign="right",
            valign="middle",
            size_hint=(None, 1),
            width="100dp",
        )
        right_lbl.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))

        row.add_widget(left_lbl)
        row.add_widget(right_lbl)

        with row.canvas.after:
            Color(0.878, 0.886, 0.910, 1)
            row._div = Line(points=[0, 0, 0, 0], width=1)

        def _upd(inst, val):
            inst._div.points = [inst.x, inst.y, inst.right, inst.y]

        row.bind(pos=_upd, size=_upd)
        return row

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

    def go_to(self, screen_name):
        self.manager.current = screen_name