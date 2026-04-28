[app]

title = Keep Notes

package.name = keepnotes

version = 0.2

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