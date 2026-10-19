# Green-board recognition: implementation status and reliability plan

## Implemented in this prototype
- A confidence-gated recognition API.
- Candidate board geometry scoring based on the alternating green/cream square pattern.
- 64-square crop generation in FEN scan order.
- An explicit abstain/review path whenever piece confidence is low.
- No automatic FEN acceptance when side-to-move and rule state are unknown.

## Not yet a production-grade recognizer
`PieceClassifier` is an interface by design. It must be backed by a trained
on-device model that matches the exact Chess.com piece set, scale, antialiasing,
and screen-capture pipeline. Returning guessed pieces from color alone would be
unsafe because piece identity is not encoded by square color.

## Recommended production pipeline
1. Require the user to select the green board theme and a supported piece set.
2. Capture the board using Android MediaProjection after explicit OS consent.
3. Detect the 8x8 grid and rectify it to a canonical 512x512 image.
4. Classify each square using a quantized TensorFlow Lite model trained on
   Chess.com screenshots, with 13 classes: empty + 12 piece/color classes.
5. Use temporal voting across several stable frames to reduce animation artifacts.
6. Validate piece counts, king counts, pawn ranks, and legal position constraints.
7. If any square is below threshold, highlight it for manual correction and do not
   send the position to the engine as if it were certain.
8. Infer side-to-move only from a visible, validated UI cue or explicit user choice.
   Castling rights and en-passant cannot generally be reconstructed from one frame;
   request confirmation or obtain move history where permitted.

## Dataset requirement
A reliable model needs labeled board screenshots across board sizes, piece sets,
light/dark display settings, orientations, highlights, legal-move markers, and
animation states. The green board theme standardizes square colors but does not
standardize piece art. Do not claim a high accuracy percentage without a held-out
evaluation set from real device captures.
## Reference-template classifier update
`ChessComGreenPieceClassifier` now loads normalized templates extracted from
the user's supplied Chess.com Green theme screenshot. It removes each square's
background brightness using the median border, compares signed grayscale
foreground descriptors, and treats near-uniform squares as empty. It keeps
multiple examples for repeated piece art (rooks, knights, bishops, pawns).
The recognizer uses confidence gating and basic legality sanity checks.

This is a template-matching baseline, not a general-purpose trained AI model.
It is tuned to the exact piece artwork in the supplied screenshot. Actual game
captures may differ due to scaling, highlights, animations, coordinates,
different piece sets, or browser rendering. Those cases need a held-out test
set and possibly more reference templates before the module should be trusted.\n
Use `GreenThemeRecognition.create(context)` once after startup, then call `recognize(frameRgb, sideToMove)` for captured RGB frames. Keep and reuse the recognizer; do not reload templates for every frame. The current screen-capture service is still a stub, so this recognition module is not yet wired to live MediaProjection frames.\n