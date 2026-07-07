[app]

# ── Temel Bilgiler ──────────────────────────────────────────────────────────
title           = Chat Of Matrix
package.name    = chatofmatrix
package.domain  = org.matrix.chat

# Kaynak dizin (main.py'nin bulunduğu yer)
source.dir      = .
source.include_exts = py,png,jpg,kv,atlas,ttf,otf

version         = 1.0
# Her derlemede artır: 1, 2, 3 ...
android.numeric_version = 1

# ── Python & Kivy Gereksinimleri ────────────────────────────────────────────
requirements    = python3,kivy==2.2.1,kivymd==1.1.1,pillow,certifi

# ── Görseller (isteğe bağlı, koyarsan icon.png / presplash.png oluştur) ─────
# icon.filename   = %(source.dir)s/assets/icon.png
# presplash.filename = %(source.dir)s/assets/splash.png

# ── Orientasyon & Pencere ───────────────────────────────────────────────────
orientation     = portrait
fullscreen      = 0

# ── Android İzinleri ────────────────────────────────────────────────────────
# Şu an aktif: INTERNET
# İleride kullanılacaklar şimdiden eklendi (Aşama 2-3 için)
android.permissions = \
    INTERNET,\
    ACCESS_NETWORK_STATE,\
    RECORD_AUDIO,\
    MODIFY_AUDIO_SETTINGS,\
    CAMERA,\
    READ_EXTERNAL_STORAGE,\
    WRITE_EXTERNAL_STORAGE,\
    READ_MEDIA_IMAGES,\
    READ_MEDIA_VIDEO,\
    READ_MEDIA_AUDIO,\
    BLUETOOTH,\
    BLUETOOTH_CONNECT,\
    FOREGROUND_SERVICE,\
    WAKE_LOCK

# ── Android SDK / NDK ───────────────────────────────────────────────────────
android.api         = 33
android.minapi      = 21
android.ndk         = 25b
android.sdk         = 33

# Güncel build-tools
android.build_tools_version = 33.0.2

# ── Mimari (ARMv7 + ARM64 — Redmi 10 ARM64'tür) ────────────────────────────
android.archs       = arm64-v8a,armeabi-v7a

# ── Gradle & Java ──────────────────────────────────────────────────────────
android.gradle_dependencies = \
    com.android.support:appcompat-v7:28.0.0

# Debug APK (yayına alırken release yap ve sign et)
android.release_artifact = apk

# ── p4a (python-for-android) ────────────────────────────────────────────────
p4a.bootstrap       = sdl2

# ── Buildozer Log ──────────────────────────────────────────────────────────
[buildozer]
# 0=hata, 1=bilgi, 2=debug
log_level = 2
warn_on_root = 1
