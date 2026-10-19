# Automatic board location and move annotations

## DPI and resolution
MediaProjection frames are measured in physical image pixels. Board geometry is detected in that coordinate space and the recognizer downsamples frames for search. Do not use Android dp values to locate squares. When drawing on an overlay, transform captured-frame coordinates into the overlay's local coordinate space; status/navigation bars and display cutouts must be accounted for.

## Board detection
The current implementation searches for a square region with an alternating light/dark pattern and a green-color proportion. It is a prototype heuristic, not a production-validated detector. A production version should:
- locate the largest plausible board region, including partial UI occlusions;
- fit all 7 internal vertical and horizontal grid lines, rather than relying only on candidate squares;
- estimate perspective/rotation if supported layouts need it;
- require temporal stability over multiple captured frames;
- support board orientation (white at bottom / black at bottom).

## Piece model
The included `PieceClassifier` interface must be backed by a trained TensorFlow Lite model with 13 classes (empty + 12 pieces). Train and evaluate on captured Chess.com green-theme boards and the exact piece set. Until the model is supplied, the recognizer intentionally marks squares uncertain instead of inventing piece identities.

## Dots and arrows
`MoveAnnotationView` draws green dots on caller-supplied occupied squares and a gold arrow for a UCI move such as `e2e4`. The caller must provide screen-to-overlay coordinate transforms and must only pass annotations after the user has accepted a recognized position. It visualizes analysis and does not automate moves on Chess.com.


## Runtime optimization update
Board search now downsamples frames to at most 480 px on the longest edge,
scans a bounded range of board sizes, and uses half-square position steps.
This is intended to reduce CPU cost versus exhaustive scans. It still needs
profiling on real Android devices and testing against false positives.

The annotation view now exposes capture-origin offsets and independent X/Y
scale factors so the integration layer can map capture pixels to overlay-local
pixels. Those values must be set from actual MediaProjection and overlay bounds.
