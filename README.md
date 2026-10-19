# CrustyChess — Android V1

A native Android/Jetpack Compose project with a green glass / minimalist interface and a draggable floating panel.

## What works in this V1 source

- Main screen with dark emerald gradients, translucent glass-style cards, minimal typography and lime accents.
- Android system flow for granting `Display over other apps` permission.
- Floating window created with `WindowManager`, draggable by its header, with Start / Stop / Close controls.
- Project channel link to `https://t.me/CrustySearch`.
- Existing board-geometry and template-classifier source plus reference templates are included for continued development.

## Important limitations — please read

This is a **compilable project target**, not a tested release APK. I could not run Gradle/Android SDK in this environment, so compilation on a real toolchain has not been verified.

The floating panel works as a UI component, but Start/Stop currently change the panel's state only. They do **not** start live screen capture, piece recognition, Stockfish analysis, or move automation. The recognition classes are not wired into the UI and the template classifier has not been validated on independent game screenshots. There is no server-side Telegram membership verification yet; the channel button only opens Telegram.

## Build APK

For a Termux-specific guide and a build/check script, see [`README_TERMUX.md`](README_TERMUX.md) and [`termux-build.sh`](termux-build.sh). The script requires a working Android SDK; pure Termux on ARM64 may not be able to run the standard SDK command-line tools.


Use Android Studio or AndroidIDE on Android with Android SDK platform 35 and JDK 17 or newer:

1. Extract this ZIP into a writable folder.
2. Open the extracted `CrustyChess` folder as an existing Gradle project.
3. Allow Gradle sync to download the Android Gradle Plugin, Kotlin and dependencies.
4. Build menu → **Build APK(s)** (or run `:app:assembleDebug`).
5. The debug APK, if the build succeeds, is normally at `app/build/outputs/apk/debug/app-debug.apk`.

The project uses Gradle 8.9-compatible Android Gradle Plugin 8.7.3, Kotlin 2.0.21, `compileSdk 35`, and `minSdk 26`. An Android SDK / Gradle installation is required to compile; the APK is not included in this source ZIP.

## First run

1. Open CrustyChess.
2. Tap **Enable floating window**.
3. Android Settings opens. Allow CrustyChess to display over other apps.
4. Return to CrustyChess and tap **Open floating panel**.
5. Drag the panel by its header. Start, Stop and Close currently control the overlay UI only.

## Recognition source

The recognition package contains an experimental green-board geometry detector and a template classifier. Treat output as unverified until it is connected to `MediaProjection`, tested across independent screenshots, and validated against ground-truth positions. The templates originate from one reference screenshot, so they are not sufficient evidence of general accuracy.

## If AndroidIDE asks for a Gradle wrapper

This ZIP does not include the wrapper JAR, and this environment could not download one or run Gradle to verify the build. If your Android IDE has a Gradle installation available, open its terminal in the project root and run:

```bash
gradle wrapper --gradle-version 8.9
./gradlew :app:assembleDebug
```

If `gradle` is not installed, use the IDE's Gradle setup/sync flow to install a compatible Gradle distribution first. A successful APK build has not been confirmed in this environment.
