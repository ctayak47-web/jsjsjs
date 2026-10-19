#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

fail() { printf '\n[ОШИБКА] %s\n' "$*" >&2; exit 1; }

command -v java >/dev/null 2>&1 || fail "Java не найдена. Попробуй: pkg search openjdk; затем установи доступный пакет OpenJDK (например, openjdk-21)."
command -v gradle >/dev/null 2>&1 || fail "Gradle не найден. Попробуй: pkg search gradle; затем pkg install gradle, если пакет доступен."

printf '%s\n' '=== Среда сборки ==='
java -version 2>&1 | head -n 3 || true
gradle --version | head -n 12

SDK="${ANDROID_SDK_ROOT:-${ANDROID_HOME:-$HOME/android-sdk}}"
if [[ ! -d "$SDK/platforms/android-35" ]]; then
  cat >&2 <<MSG

[НУЖЕН ANDROID SDK]
Не найдена платформа Android SDK 35 в:
  $SDK/platforms/android-35

Одних Java и Gradle недостаточно: Android Gradle Plugin требует Android SDK,
а стандартные Android command-line tools обычно рассчитаны на x86_64 и могут
не запускаться непосредственно в Termux на ARM64.

Если SDK уже установлен в другом месте, запусти так:
  ANDROID_SDK_ROOT=/путь/к/Android/Sdk bash "$0"

Если SDK не установлен, см. README_TERMUX.md — там описан честный вариант
сборки на удалённом Linux runner без AndroidIDE.
MSG
  exit 2
fi

export ANDROID_SDK_ROOT="$SDK"
export ANDROID_HOME="$SDK"

if [[ ! -x "$SDK/platform-tools/adb" ]]; then
  printf '%s\n' '[ПРЕДУПРЕЖДЕНИЕ] Не найден platform-tools/adb; для самой сборки он может не понадобиться.' >&2
fi

mkdir -p "$HOME/.gradle"
# Снижаем риск OOM на телефонах; пользователь может переопределить эти параметры.
export GRADLE_OPTS="${GRADLE_OPTS:--Dorg.gradle.daemon=false -Dorg.gradle.jvmargs=-Xmx1536m}"

gradle --no-daemon --stacktrace :app:assembleDebug
APK="$ROOT/app/build/outputs/apk/debug/app-debug.apk"
[[ -f "$APK" ]] || fail "Gradle завершился, но APK не найден по ожидаемому пути: $APK"

mkdir -p "$ROOT/output"
cp "$APK" "$ROOT/output/CrustyChess-debug.apk"
printf '\n[ГОТОВО] APK: %s\n' "$ROOT/output/CrustyChess-debug.apk"
