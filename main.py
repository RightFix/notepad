from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from assets.pages.notepad import NotesScreen



class NotepadApp(App):
    screen_history = ["notes_screen"]

    def build(self):
        Window.softinput_mode = "resize"
        sm = ScreenManager()
        sm.add_widget(NotesScreen(name="notes_screen"))
        return sm

    def go_back(self):
        current = self.root.current
        if current != "notes_screen":
            if len(self.screen_history) > 1:
                self.screen_history.pop()
                self.root.current = self.screen_history[-1]
            else:
                self.root.current = "notes_screen"
            return True
        else:
            self.stop()
            return True

    def on_start(self):
        Window.bind(on_keyboard=self.on_back_button)

    def on_back_button(self, window, key, *args):
        if key == 27:
            return self.go_back()
        return False


NotepadApp().run()
