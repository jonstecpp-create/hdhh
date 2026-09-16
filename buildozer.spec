[app]
title = SpotYt
package.name = spotyt
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

requirements = python3,kivy,yt-dlp,urllib3,certifi,openssl

orientation = portrait
fullscreen = 0

android.permissions = INTERNET, ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 21

[buildozer]
log_level = 2
warn_on_root = 1
