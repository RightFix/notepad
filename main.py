from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDFabButton, MDIconButton, MDButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screenmanager import ScreenManager
from kivymd.uix.appbar import MDTopAppBar
from kivymd.uix.textfield import MDTextField

# Ensure NotesScreen and NoteEditorScreen are imported so the classes are registered with the Factory
from assets.notes import NotesScreen, NoteEditorScreen

class Main(MDApp):
    kv_file = None
    def build(self):
        self.theme_cls.primary_palette = "Blue"  # Use standard palette
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.accent_palette = "Amber"
        return Builder.load_file("main.kv")

    def add_note(self, title: str = None, content: str = None):
        
        try:
            screen = self.root.get_screen('notes')
        except Exception:
            return None
        return screen.add_note(title=title, content=content)

if __name__ == '__main__':
    Main().run()
