from typing import List, Dict, Any
import json
from pathlib import Path

DATA_FILE = Path.cwd() / "notes.json"


class Note:
	def __init__(self, title: str, content: str, id: int = None):
		self.id = id
		self.title = title
		self.content = content

	def to_dict(self) -> Dict[str, Any]:
		return {"id": self.id, "title": self.title, "content": self.content}

	@staticmethod
	def from_dict(d: Dict[str, Any]):
		return Note(d.get("title", ""), d.get("content", ""), d.get("id"))


class NoteManager:
	def __init__(self, *args, **kwargs):
		# accept arbitrary args/kwargs because Kivy may instantiate
		# classes with extra parameters (e.g. __no_builder)
		# Ensure proper initialization for widget classes in MRO
		try:
			super().__init__(*args, **kwargs)
		except Exception:
			# if super has no initializer, ignore
			pass
		self.notes: List[Note] = []
		self._next_id = 1
		self.load()

	def add_note(self, title: str, content: str) -> Note:
		note = Note(title, content, id=self._next_id)
		self._next_id += 1
		self.notes.append(note)
		self.save()
		return note

	def get_notes(self) -> List[Note]:
		return list(self.notes)

	def update_note(self, note_id: int, title: str, content: str) -> bool:
		for n in self.notes:
			if n.id == note_id:
				n.title = title
				n.content = content
				self.save()
				return True
		return False

	def delete_note(self, note_id: int) -> bool:
		for i, n in enumerate(self.notes):
			if n.id == note_id:
				del self.notes[i]
				self.save()
				return True
		return False

	def clear_notes(self):
		self.notes.clear()
		self._next_id = 1
		self.save()

	def save(self):
		try:
			DATA_FILE.write_text(json.dumps([n.to_dict() for n in self.notes], indent=2), encoding="utf-8")
		except Exception:
			pass

	def load(self):
		if not DATA_FILE.exists():
			self.notes = []
			self._next_id = 1
			return
		try:
			data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
			self.notes = [Note.from_dict(d) for d in data]
			# set next id
			max_id = max((n.id for n in self.notes if n.id is not None), default=0)
			self._next_id = max_id + 1
		except Exception:
			self.notes = []
			self._next_id = 1


from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel


class NotesScreen(MDScreen):
	"""Screen that composes a NoteManager instance for storage and persistence.

	Composition avoids MRO/init issues when Kivy's Builder instantiates the
	screen class.
	"""
	def on_kv_post(self, base_widget):
		# create a NoteManager instance to manage notes
		self.note_manager = NoteManager()
		Clock.schedule_once(lambda dt: self.load_notes(), 0)
		
		# Add some test notes if there are none
		if not self.note_manager.get_notes():
			self.add_note("Welcome to Notepad", "This is your first note. Click the + button to add more notes.")
			self.add_note("Sample Note", "This is a sample note to show how notes are displayed in the grid.")

	def load_notes(self):
		notes_grid = self.ids.get('notes_grid') if hasattr(self, 'ids') else None
		if notes_grid is None:
			return
		notes_grid.clear_widgets()
		for note in self.note_manager.get_notes():
			notes_grid.add_widget(self.create_note_card(note))

	def add_note(self, title: str = None, content: str = None):
		if not title and not content:
			title = f"Note {len(self.note_manager.get_notes())+1}"
			content = "New note content..."
		note = self.note_manager.add_note(title, content)
		if hasattr(self.ids, 'notes_grid'):
			self.ids.notes_grid.add_widget(self.create_note_card(note))
		return note

	def create_note_card(self, note):
		from kivy.factory import Factory
		card = Factory.NoteCard()
		card.id = f"note-{note.id}"
		card.note_id = note.id
		card.title = note.title
		card.content = note.content
		return card

	def open_note(self, card):
		from kivymd.toast import toast
		toast(f"Open (NotesScreen): {getattr(card, 'title', '<untitled>')}")

	def open_edit_dialog(self, card):
		from kivymd.uix.dialog import MDDialog
		from kivymd.uix.button import MDButton
		from kivymd.uix.textfield import MDTextField

		title_field = MDTextField(text=getattr(card, 'title', ''), hint_text="Title")
		content_field = MDTextField(text=getattr(card, 'content', ''), hint_text="Content", multiline=True)

		def save_callback(*args):
			self.note_manager.update_note(getattr(card, 'note_id', None), title_field.text, content_field.text)
			self.load_notes()
			dialog.dismiss()

		def delete_callback(*args):
			self.note_manager.delete_note(getattr(card, 'note_id', None))
			self.load_notes()
			dialog.dismiss()

		dialog = MDDialog(title="Edit note",
						  type="custom",
						  size_hint=(0.9, None),
						  height=dp(300),
						  buttons=[
							  MDButton(text="Delete", on_release=delete_callback),
							  MDButton(text="Save", on_release=save_callback),
						  ])
		dialog.content_cls = BoxLayout(orientation='vertical')
		dialog.content_cls.add_widget(title_field)
		dialog.content_cls.add_widget(content_field)
		dialog.open()


class NoteEditorScreen(MDScreen):
	"""Screen for creating or editing a single note.

	For creation, Save will add a new note via the NotesScreen.note_manager and
	return to the notes list.
	"""
	def save_note(self):
		from kivymd.app import MDApp
		title = self.ids.title_field.text if 'title_field' in self.ids else ''
		content = self.ids.content_field.text if 'content_field' in self.ids else ''
		app = MDApp.get_running_app()
		try:
			notes_screen = app.root.get_screen('notes')
		except Exception:
			notes_screen = None
		if notes_screen is not None:
			notes_screen.note_manager.add_note(title or f"Note {len(notes_screen.note_manager.get_notes())+1}", content or "")
			notes_screen.load_notes()
		# clear fields and go back
		if 'title_field' in self.ids:
			self.ids.title_field.text = ''
		if 'content_field' in self.ids:
			self.ids.content_field.text = ''
		if app and app.root:
			app.root.current = 'notes'

	def cancel(self):
		# clear fields and return
		if 'title_field' in self.ids:
			self.ids.title_field.text = ''
		if 'content_field' in self.ids:
			self.ids.content_field.text = ''
		from kivymd.app import MDApp
		app = MDApp.get_running_app()
		if app and app.root:
			app.root.current = 'notes'
