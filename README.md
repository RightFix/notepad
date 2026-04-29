# Keep Notes

A simple and elegant note-taking application built with Kivy for Android and desktop.

## Features

- **Create Notes**: Add new notes with title and content
- **Edit Notes**: Tap on any note card to edit it
- **Delete Notes**: Remove unwanted notes
- **Color-coded Notes**: Choose from 6 note colors (white, yellow, green, blue, pink, purple)
- **Search**: Filter notes by title or content
- **Persistent Storage**: Notes are saved locally in JSON format

## Screenshots

The app features:
- Modern green header with rounded corners
- Note cards with colored backgrounds and rounded edges
- Floating action button (+) to create new notes
- Search functionality to filter notes
- Full-screen editor for creating/editing notes

## Installation

### Prerequisites
- Python 3.8+
- Kivy

### Install Dependencies

```bash
pip install kivy
```

### Run the App

```bash
python main.py
```

### Build for Android

Make sure Buildozer is installed, then:

```bash
buildozer android debug
```

## Project Structure

```
notepad/
├── main.py                 # App entry point
├── notes.json              # Local storage for notes
├── buildozer.spec          # Buildozer configuration
├── assets/
│   ├── pages/
│   │   └── notepad.py      # Main screen and UI logic
│   ├── ui_custom.py        # Custom UI components
│   └── images/
│       ├── icon.png        # App icon
│       └── presplash.png   # Splash screen
└── README.md
```

## Usage

1. **Create Note**: Tap the green + button at the bottom right
2. **Edit Note**: Tap anywhere on a note card
3. **Delete Note**: Tap the "Delete" button on a note card
4. **Search**: Tap "Search" in the header to filter notes
5. **Save**: Enter title and content, then tap "Save"
6. **Cancel**: Tap "Cancel" to discard changes

## License

MIT License