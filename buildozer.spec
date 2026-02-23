[app]
title = مختبرات حسين غلاب
package.name = hussainghalab
package.domain = com.lab.hussain
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0
requirements = python3,kivy==2.3.0,kivymd==1.2.0,reportlab,qrcode,pillow,arabic-reshaper,python-bidi,android
orientation = portrait
fullscreen = 0
android.minapi = 21
android.ndk = 25b
android.sdk = 34
android.archs = arm64-v8a
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.gradle_dependencies = androidx.core:core:1.9.0

[buildozer]
log_level = 2
warn_on_root = 0
