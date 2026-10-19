package com.crustychess.capture

import android.app.Service
import android.content.Intent
import android.os.IBinder

/**
 * Reserved for MediaProjection integration.
 * Android requires a user-visible system consent dialog before screen capture.
 */
class ScreenCaptureService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // TODO: receive MediaProjection consent result from an Activity,
        // create the MediaProjection, and process ImageReader frames.
        stopSelf()
        return START_NOT_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
