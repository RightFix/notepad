[app]

title = Notepad

package.name = notepad

package.domain = org.rightfix

source.dir = .

source.include_exts = py,png,jpg,atlas

source.include_patterns = assets/*,assets/*/*

version = 0.1

requirements = python3,kivy,pillow,android

presplash.filename = %(source.dir)s/assets/images/presplash.png

icon.filename = %(source.dir)s/assets/images/icon.png

orientation = portrait

fullscreen = 0

android.presplash_color = black

android.permissions = android.permission.INTERNET, (name=android.permission.WRITE_EXTERNAL_STORAGE;maxSdkVersion=18)

android.api = 34

android.accept_sdk_license = True

android.enable_androidx = True

android.archs = arm64-v8a, armeabi-v7a

android.allow_backup = True

p4a.bootstrap = sdl2

 [buildozer]

log_level = 2

warn_on_root = 1