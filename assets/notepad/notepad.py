import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button


class NotesScreen(Screen):
    BG_COLOR = (0.95, 0.95, 0.95, 1)
    HEADER_COLOR = (0.2, 0.2, 0.3, 1)
    BTN_COLOR = (0.0, 0.5, 0.8, 1)
    TEXT_BG_COLOR = (1, 1, 1, 1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.notes_file = "notes.txt"
        self.build_ui()

    def build_ui(self):
        main_layout = BoxLayout(
            orientation="vertical", spacing=10, padding=[15, 10, 15, 10]
        )

        app_bar = BoxLayout(size_hint_y=None, height=65, padding=15)
        header = Label(
            text="[b]Notepad[/b]",
            markup=True,
            font_size=28,
            halign="left",
            valign="center",
            color=(1, 1, 1, 1),
        )
        app_bar.add_widget(header)
        main_layout.add_widget(app_bar)

        display_container = BoxLayout(
            orientation="vertical", size_hint_y=0.75, padding=[10, 5, 10, 5], spacing=5
        )

        self.note_input = TextInput(
            hint_text="Write your note here...",
            font_size=20,
            multiline=True,
            background_color=self.TEXT_BG_COLOR,
            padding=[10, 10],
        )
        display_container.add_widget(self.note_input)
        main_layout.add_widget(display_container)

        buttons_container = BoxLayout(spacing=8, size_hint_y=None, height=50)
        save_btn = Button(
            text="Save",
            font_size=18,
            background_color=self.BTN_COLOR,
            color=(1, 1, 1, 1),
            bold=True,
        )
        save_btn.bind(on_release=self.save_note)

        clear_btn = Button(
            text="Clear",
            font_size=18,
            background_color=(0.7, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            bold=True,
        )
        clear_btn.bind(on_release=self.clear_note)

        view_btn = Button(
            text="View Notes",
            font_size=18,
            background_color=self.BTN_COLOR,
            color=(1, 1, 1, 1),
            bold=True,
        )
        view_btn.bind(on_release=self.view_notes)

        buttons_container.add_widget(save_btn)
        buttons_container.add_widget(clear_btn)
        buttons_container.add_widget(view_btn)
        main_layout.add_widget(buttons_container)

        self.notes_list = BoxLayout(
            orientation="vertical", size_hint_y=0.25, padding=[10, 5], spacing=5
        )
        self.notes_label = Label(
            text="No notes yet",
            font_size=16,
            color=(0.3, 0.3, 0.3, 1),
            halign="left",
            valign="top",
        )
        self.notes_list.add_widget(self.notes_label)
        main_layout.add_widget(self.notes_list)

        self.add_widget(main_layout)

    def save_note(self, *args):
        note = self.note_input.text.strip()
        if note:
            try:
                with open(self.notes_file, "a") as f:
                    f.write(note + "\n---\n")
                self.notes_label.text = "Note saved!"
                self.note_input.text = ""
            except Exception as e:
                self.notes_label.text = f"Error: {str(e)}"
        else:
            self.notes_label.text = "Nothing to save"

    def clear_note(self, *args):
        self.note_input.text = ""

    def view_notes(self, *args):
        try:
            if os.path.exists(self.notes_file):
                with open(self.notes_file, "r") as f:
                    notes = f.read()
                if notes:
                    self.notes_label.text = notes[:500]
                else:
                    self.notes_label.text = "No notes yet"
            else:
                self.notes_label.text = "No notes yet"
        except Exception as e:
            self.notes_label.text = f"Error: {str(e)}"
