import os
import json
from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, StringProperty
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse, Line
from kivy.core.window import Window
from ..ui_custom import RoundedButton, RoundedTextInput


NOTE_COLORS = {
    "white": (1, 1, 1, 1),
    "yellow": (1, 0.95, 0.8, 1),
    "green": (0.85, 0.95, 0.85, 1),
    "blue": (0.85, 0.92, 0.95, 1),
    "pink": (1, 0.9, 0.9, 1),
    "purple": (0.95, 0.9, 0.95, 1),
}


class NoteCard(BoxLayout):
    note_id = StringProperty("")
    title = StringProperty("")
    content = StringProperty("")
    color_name = StringProperty("white")
    timestamp = StringProperty("")

    def __init__(self, note_id, title, content, color_name, timestamp, **kwargs):
        super().__init__(**kwargs)
        self.note_id = note_id
        self.title = title
        self.content = content
        self.color_name = color_name
        self.timestamp = timestamp
        self.orientation = "vertical"
        self.padding = 12
        self.spacing = 5
        self.size_hint_y = None
        self.height = 120
        self.add_widget(Widget(size_hint_y=None, height=0))


class NotesScreen(Screen):
    BG_COLOR = (0.95, 0.95, 0.98, 1)
    HEADER_COLOR = (0.24, 0.51, 0.27, 1)
    ACCENT_COLOR = (0.24, 0.51, 0.27, 1)
    CARD_COLOR = (1, 1, 1, 1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.notes_file = "notes.json"
        self.notes = []
        self._editor = None
        self._existing_note = None
        self._editor_title = None
        self._editor_content = None
        self._selected_color = "white"
        self._color_buttons = {}
        self.load_notes()
        self.build_ui()

    def load_notes(self):
        if os.path.exists(self.notes_file):
            try:
                with open(self.notes_file, "r") as f:
                    data = json.load(f)
                    self.notes = data.get("notes", [])
            except:
                self.notes = []

    def save_notes_to_file(self):
        try:
            with open(self.notes_file, "w") as f:
                json.dump({"notes": self.notes}, f, indent=2)
        except Exception as e:
            print(f"Error saving notes: {e}")

    def build_ui(self):
        with self.canvas.before:
            Color(*self.BG_COLOR)
            self._bg_rect = Rectangle(size=Window.size, pos=(0, 0))
        Window.bind(on_resize=self._update_bg)

        main_layout = BoxLayout(orientation="vertical")
        header = BoxLayout(orientation="vertical", size_hint_y=0.15)
        title_label = Label(
            text="[b]Note Pad[/b]",
            markup=True,
            font_size=26,
            halign="center",
            valign="center",
            color=self.ACCENT_COLOR,
        )
        header.add_widget(title_label)

        main_layout.add_widget(header)

        self.search_container = BoxLayout(
            size_hint_y=0.12, padding=[15, 5], size_hint_x=1
        )
        self.search_input = RoundedTextInput(
            hint_text="Search notes...",
            font_size=16,
            multiline=False,
            size_hint_y=1,
            size_hint_x=0.85,
            height=50,
            padding=[15, 15],
        )
        search_btn = RoundedButton(
            text="Search",
            radius=8,
            size_hint_x=0.15,
            size_hint_y=1,
            height=50,
            font_size=16,
            padding=[0, 15],
        )
        search_btn.bind(on_release=self.toggle_search)
        self.search_input.bind(text=self.filter_notes)
        self.search_container.add_widget(self.search_input)
        self.search_container.add_widget(search_btn)
        main_layout.add_widget(self.search_container)

        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.notes_container = GridLayout(
            cols=2, spacing=12, padding=[15, 10], size_hint_y=None
        )
        self.notes_container.bind(minimum_height=self.notes_container.setter("height"))
        scroll.add_widget(self.notes_container)
        main_layout.add_widget(scroll)

        self.add_widget(main_layout)

        float_layout = FloatLayout()
        self.add_new_btn = RoundedButton(
            text="+",
            radius=32,
            btn_color=self.ACCENT_COLOR,
            size_hint=(None, None),
            size=(65, 65),
            pos_hint={"center_x": 0.9, "y": 0.06},
            font_size=32,
        )
        self.add_new_btn.bind(on_release=self.open_note_editor)
        float_layout.add_widget(self.add_new_btn)
        self.add_widget(float_layout)
        self.refresh_notes_display()

    def _update_bg(self, window, width, height):
        if hasattr(self, "_bg_rect"):
            self._bg_rect.size = (width, height)

    def toggle_search(self, *args):
        if self.search_container.height > 0:
            self.search_container.height = 0
            self.search_input.text = ""
            self.filter_notes()
        else:
            self.search_container.height = 60

    def filter_notes(self, *args):
        self.refresh_notes_display()

    def get_filtered_notes(self):
        query = self.search_input.text.lower().strip()
        if not query:
            return self.notes
        return [
            n
            for n in self.notes
            if query in n.get("title").lower() or query in n.get("content").lower()
        ]

    def refresh_notes_display(self):
        self.notes_container.clear_widgets()
        filtered = self.get_filtered_notes()

        for note in filtered:
            card = self.create_note_card(note)
            self.notes_container.add_widget(card)
        if not filtered:
            empty_label = Label(
                text="No notes yet\nTap + to create one!",
                font_size=18,
                color=(0.5, 0.5, 0.5, 1),
                halign="center",
            )
            self.notes_container.add_widget(empty_label)

    def create_note_card(self, note):
        card = NoteCard(
            note_id=note.get("id"),
            title=note.get("title"),
            content=note.get("content"),
            color_name=note.get("color"),
            timestamp=note.get("timestamp"),
        )

        bg_color = NOTE_COLORS.get(note.get("color", "white"), (1, 1, 1, 1))
        with card.canvas.before:
            Color(*bg_color)
            card.bg_rect = RoundedRectangle(size=card.size, pos=card.pos, radius=[12])

        card.bind(pos=self.update_card_rect, size=self.update_card_rect)
        card.bind(
            on_touch_up=lambda instance, touch: self._on_card_click(
                instance, touch, note
            )
        )

        title_label = Label(
            text=note.get("title", "Untitled"),
            font_size=16,
            bold=True,
            color=(0.2, 0.2, 0.25, 1),
            halign="left",
            valign="top",
            size_hint_y=None,
            height=30,
            text_size=(None, 30),
        )
        card.add_widget(title_label)
        card.bind(
            width=lambda w, _: setattr(title_label, "text_size", (w.width - 24, 30))
        )

        content_text = note.get("content", "")
        content_label = Label(
            text=content_text[:80] + "..." if len(content_text) > 80 else content_text,
            font_size=14,
            color=(0.3, 0.3, 0.35, 1),
            halign="left",
            valign="top",
            size_hint_y=None,
            height=40,
            text_size=(None, 40),
        )
        card.add_widget(content_label)
        card.bind(
            width=lambda w, _: setattr(content_label, "text_size", (w.width - 24, 40))
        )

        actions = BoxLayout(size_hint_y=None, height=30, spacing=8)

        # edit_btn.bind(on_release=lambda x, n=note: self.open_note_editor(n))
        delete_btn = RoundedButton(
            text="Delete",
            radius=6,
            btn_color=(0.9, 0.3, 0.3, 0.15),
            size_hint_x=None,
            width=70,
            font_size=14,
            color=(0.9, 0.3, 0.3, 1),
        )
        delete_btn.bind(on_release=lambda x, n=note: self.delete_note(n))
        # actions.add_widget(edit_btn)
        actions.add_widget(delete_btn)
        actions.add_widget(Widget())
        card.add_widget(actions)

        return card

    def update_card_rect(self, instance, *args):
        instance.bg_rect.pos = instance.pos
        instance.bg_rect.size = instance.size

    def _on_card_click(self, instance, touch, note):
        if instance.collide_point(touch.x, touch.y):
            self.open_note_editor(note)

    def open_note_editor(self, *args):
        if args and isinstance(args[0], dict):
            note = args[0]
            self.show_editorScreen(note)
        else:
            self.show_editorScreen()

    def show_editorScreen(self, existing_note=None):
        editor = BoxLayout(orientation="vertical", padding=20, spacing=15)
        with editor.canvas.before:
            Color(0.95, 0.95, 0.98, 1)
            editor._bg_rect = RoundedRectangle(
                size=editor.size, pos=editor.pos, radius=[20]
            )
        editor.bind(
            pos=lambda w, *_: setattr(w._bg_rect, "pos", w.pos),
            size=lambda w, *_: setattr(w._bg_rect, "size", w.size),
        )

        editor_header = BoxLayout(size_hint_y=None, height=50)
        editor_header.add_widget(Widget())
        cancel_btn = RoundedButton(
            text="Cancel",
            radius=8,
            btn_color=(0.6, 0.6, 0.6, 1),
            size_hint_x=None,
            width=100,
            font_size=16,
        )
        cancel_btn.bind(on_release=self.close_editor)
        editor_header.add_widget(cancel_btn)
        save_btn = RoundedButton(
            text="Save",
            radius=8,
            btn_color=self.ACCENT_COLOR,
            size_hint_x=None,
            width=100,
            font_size=16,
        )
        save_btn.bind(on_release=lambda x: self.save_note_from_editor(existing_note))
        editor_header.add_widget(save_btn)
        editor.add_widget(editor_header)

        title_input = RoundedTextInput(
            hint_text="Title",
            font_size=22,
            multiline=False,
            size_hint_y=None,
            height=55,
            text=existing_note.get("title", "") if existing_note else "",
            padding=[15, 0],
        )
        self._editor_title = title_input
        editor.add_widget(title_input)

        content_input = RoundedTextInput(
            hint_text="Write your note here...",
            font_size=18,
            multiline=True,
            text=existing_note.get("content", "") if existing_note else "",
            padding=[15, 15],
        )
        self._editor_content = content_input
        editor.add_widget(content_input)

        self._editor = editor
        self._existing_note = existing_note
        self.add_widget(editor)

    def select_color(self, color_name):
        self._selected_color = color_name
        for name, btn in self._color_buttons.items():
            if name == color_name:
                btn.border = (3, 3, 3, 3)
                btn.outline_color = (0, 0, 0, 1)
            else:
                btn.border = (0, 0, 0, 0)

    def save_note_from_editor(self, *args):
        title = self._editor_title.text.strip()
        content = self._editor_content.text.strip()
        if not title and not content:
            self.close_editor()
            return

        if not title:
            title = content[:30] + "..." if len(content) > 30 else content

        timestamp = datetime.now().strftime("%b %d, %Y %H:%M")

        if self._existing_note:
            for i, note in enumerate(self.notes):
                if note.get("id") == self._existing_note.get("id"):
                    self.notes[i] = {
                        "id": self._existing_note.get("id"),
                        "title": title,
                        "content": content,
                        "color": self._selected_color,
                        "timestamp": timestamp,
                    }
                    break
        else:
            new_id = str(datetime.now().timestamp())
            self.notes.insert(
                0,
                {
                    "id": new_id,
                    "title": title,
                    "content": content,
                    "color": self._selected_color,
                    "timestamp": timestamp,
                },
            )

        self.save_notes_to_file()
        self.close_editor()
        self.refresh_notes_display()

    def close_editor(self, *args):
        if (
            hasattr(self, "_editor")
            and self._editor is not None
            and self._editor.parent is not None
        ):
            self.remove_widget(self._editor)
        self._editor = None
        self._existing_note = None

    def delete_note(self, note):
        self.notes = [n for n in self.notes if n.get("id") != note.get("id")]
        self.save_notes_to_file()
        self.refresh_notes_display()
