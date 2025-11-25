# app/main.py
import time
import uuid
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.properties import StringProperty
from database import init_db, list_items, get_conn
from sync_client import fetch_server_data

class RootWidget(BoxLayout):
    last_sync = StringProperty("Never")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        init_db()  # Ensure DB is initialized
        self.refresh_task_list()

    def refresh_task_list(self):
        """Load items from local DB into the UI"""
        self.ids.items_box.clear_widgets()
        items = list_items()
        for item in items:
            row = TaskRow()
            row.ids.name.text = item["name"]
            row.ids.qty.text = str(item["qty"])
            self.ids.items_box.add_widget(row)

    def do_sync(self):
        """Fetch updates from server incrementally"""
        self.ids.sync_status.text = "Syncing..."
        # Run sync in clock to avoid blocking UI
        Clock.schedule_once(self._sync, 0.1)

    def _sync(self, dt):
        result = fetch_server_data()
        if result.get("status") == "success":
            self.refresh_task_list()
            self.last_sync = time.strftime("%Y-%m-%d %H:%M:%S")
            self.ids.sync_status.text = f"Synced: {result.get('count')} items"
        else:
            self.ids.sync_status.text = f"Error: {result.get('message')}"

class TaskRow(BoxLayout):
    pass

class MeetingTaskApp(App):
    def build(self):
        return RootWidget()

if __name__ == "__main__":
    MeetingTaskApp().run()
