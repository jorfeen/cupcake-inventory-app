from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle, Line
import database.db as db


class SettingsScreen(Screen):

    def on_enter(self):
        self.ids.dark_mode_toggle.text = "On" if db.dark_mode else "Off"
        self.ids.threshold_input.text = str(db.default_threshold)
        self.ids.message.text = ""

    def toggle_dark_mode(self):
        db.dark_mode = not db.dark_mode
        self.ids.dark_mode_toggle.text = "On" if db.dark_mode else "Off"
        self.ids.message.text = "Dark mode updated."
        self.ids.message.color = (0.133, 0.694, 0.298, 1)


    def save_threshold(self):
        value = self.ids.threshold_input.text.strip()
        try:
            value = int(value)
        except ValueError:
            self._set_message("Threshold must be an integer.", error=True)
            return
        if value < 0:
            self._set_message("Threshold cannot be negative.", error=True)
            return
        db.default_threshold = value
        self._set_message(f"Default threshold set to {value}.", error=False)


    def confirm_reset(self):
        content = BoxLayout(
            orientation="vertical",
            padding="20dp",
            spacing="16dp",
        )

        msg = Label(
            text="This will delete [b]all inventory data[/b] and reset settings.\nThis cannot be undone.",
            markup=True,
            font_size="14sp",
            color=(0.133, 0.153, 0.196, 1),
            halign="center",
            valign="middle",
        )
        msg.bind(size=lambda i, v: setattr(i, "text_size", (i.width, None)))

        btn_row = BoxLayout(size_hint_y=None, height="48dp", spacing="12dp")

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
            text="Reset",
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
        confirm_btn.bind(on_press=lambda _: self._do_reset(popup))
        popup.open()

    def _do_reset(self, popup):
        popup.dismiss()
        db.items.clear()
        db.recent_activity.clear()
        db.default_threshold = 5
        db.dark_mode = False
        self.ids.dark_mode_toggle.text = "Off"
        self.ids.threshold_input.text = "5"
        self._set_message("All data and settings have been reset.", error=False)

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _set_message(self, text, error=False):
        self.ids.message.text = text
        self.ids.message.color = (
            (0.902, 0.224, 0.224, 1) if error else (0.133, 0.694, 0.298, 1)
        )

    def go_to(self, screen_name):
        self.manager.current = screen_name