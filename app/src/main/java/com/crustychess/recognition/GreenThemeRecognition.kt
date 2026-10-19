package com.crustychess.recognition

import android.content.Context
import org.opencv.android.OpenCVLoader

object GreenThemeRecognition {
    /**
     * Call once after app startup, then reuse this recognizer for subsequent
     * frames. Do not construct one per frame because templates are loaded once.
     */
    fun create(context: Context): GreenBoardRecognizer {
        check(OpenCVLoader.initLocal()) { "OpenCV native runtime failed to initialize." }
        return GreenBoardRecognizer(ChessComGreenPieceClassifier(context.applicationContext))
    }
}
