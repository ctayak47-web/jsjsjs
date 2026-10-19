# CrustyChess project audit (2026-10-19)

## Build fixes applied

- Aligned Java and Kotlin bytecode targets to JVM 17 in `app/build.gradle.kts`. The previous CI failure was `compileDebugJavaWithJavac (1.8)` versus `compileDebugKotlin (17)`.
- Added `.github/workflows/build.yml` for a GitHub Actions debug APK build with Java 17, Android SDK Platform 35 / Build Tools 35.0.0, Gradle 8.9, and an uploaded APK artifact.
- Added basic file-existence checks so a wrong repository root fails with a clearer message.

## Findings that are not build blockers

- `ScreenCaptureService` is a placeholder: it stops itself and does not request/consume MediaProjection consent or process captured frames.
- `ChessEngine.kt` defines only an interface/data model. No Stockfish binary or concrete engine implementation is bundled.
- The floating panel's Start/Stop buttons only change UI labels/state. They do not start recognition or engine analysis.
- `SetupGuide` is not connected to `MainActivity`; subscription verification, calibration, and the described onboarding callbacks are not wired into the current app flow.
- The app UI explicitly says server-side Telegram subscription verification and live recognition/Stockfish are not connected. Those features should not be considered implemented or secure.
- Recognition code is heuristic/template-based and its own comments say it needs calibration against real captures. Its FEN output intentionally requires confirmation for side-to-move, castling, and en-passant state.
- `ChessComGreenPieceClassifier` requires assets under `app/src/main/assets/piece_templates`; the current archive includes these files.

## Scope and verification

The supplied CI log proves Android resource/manifest processing succeeded and compilation stopped at JVM-target validation. The source was statically inspected and the target mismatch was fixed. A successful end-to-end build is **not yet verified** until the new GitHub Actions run completes. Additional compiler or runtime issues may only become visible after this first blocker is removed.
