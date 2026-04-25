from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from kivy.core.window import Window
from screens.dashboard import DashboardScreen
from screens.add_item import AddItemScreen
from screens.inventory import InventoryScreen
from screens.item_details import ItemDetailsScreen
from screens.reports import ReportsScreen
from screens.settings import SettingsScreen

Builder.load_file("screens/dashboard.kv")
Builder.load_file("screens/add_item.kv")
Builder.load_file("screens/inventory.kv")
Builder.load_file("screens/item_details.kv")
Builder.load_file("screens/reports.kv")
Builder.load_file("screens/settings.kv")

Window.clearcolor = (0.961, 0.965, 0.980, 1)


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