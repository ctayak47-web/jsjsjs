package com.crustychess.overlay

import android.app.Service
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Intent
import android.graphics.Color
import android.graphics.PixelFormat
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.os.Build
import android.os.IBinder
import android.provider.Settings
import android.view.Gravity
import android.view.MotionEvent
import android.view.View
import android.view.WindowManager
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import kotlin.math.abs

/** A draggable, translucent green panel. Start/Stop control its local UI state only. */
class FloatingPanelService : Service() {
    private var windowManager: WindowManager? = null
    private var panel: View? = null
    private var layoutParams: WindowManager.LayoutParams? = null
    private lateinit var status: TextView
    private lateinit var startButton: Button
    private var running = false

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startPanelForegroundNotification()
        if (!Settings.canDrawOverlays(this)) {
            stopSelf()
            return START_NOT_STICKY
        }
        if (panel == null) showPanel()
        return START_NOT_STICKY
    }

    private fun startPanelForegroundNotification() {
        val manager = getSystemService(NOTIFICATION_SERVICE) as NotificationManager
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            manager.createNotificationChannel(
                NotificationChannel(CHANNEL_ID, "CrustyChess floating panel", NotificationManager.IMPORTANCE_LOW)
            )
        }
        val notification = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            Notification.Builder(this, CHANNEL_ID)
        } else {
            @Suppress("DEPRECATION") Notification.Builder(this)
        }.setSmallIcon(android.R.drawable.ic_menu_info_details)
            .setContentTitle("CrustyChess is active")
            .setContentText("Floating panel is available over other apps")
            .setOngoing(true)
            .build()
        startForeground(NOTIFICATION_ID, notification)
    }

    private fun showPanel() {
        windowManager = getSystemService(WINDOW_SERVICE) as WindowManager
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(15), dp(13), dp(15), dp(14))
            background = rounded(Color.argb(238, 12, 28, 17), Color.argb(150, 137, 226, 141), 24)
            elevation = dp(12).toFloat()
        }

        val header = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            setPadding(0, 0, 0, dp(8))
        }
        val brand = TextView(this).apply {
            text = "♞  CRUSTYCHESS"
            textSize = 15f
            setTextColor(Color.rgb(181, 245, 154))
            typeface = Typeface.create("sans-serif", Typeface.BOLD)
        }
        val dragHint = TextView(this).apply {
            text = "  ⠿"
            textSize = 20f
            setTextColor(Color.argb(190, 220, 245, 220))
        }
        header.addView(brand, LinearLayout.LayoutParams(0, dp(30), 1f))
        header.addView(dragHint, LinearLayout.LayoutParams(dp(30), dp(30)))
        header.setOnTouchListener(DragTouchListener())

        status = TextView(this).apply {
            text = "READY  /  ANALYSIS NOT CONNECTED"
            textSize = 10.5f
            letterSpacing = 0.06f
            setTextColor(Color.rgb(181, 200, 183))
            setPadding(0, dp(3), 0, dp(12))
        }

        startButton = makeButton("START", true) {
            running = true
            status.text = "RUNNING  /  ENGINE NOT CONNECTED"
            startButton.text = "STARTED"
        }
        val stopButton = makeButton("STOP", false) {
            running = false
            status.text = "STOPPED  /  WAITING"
            startButton.text = "START"
        }
        val closeButton = makeButton("CLOSE PANEL", false) { stopSelf() }

        root.addView(header)
        root.addView(status)
        root.addView(startButton, buttonParams())
        root.addView(stopButton, buttonParams())
        root.addView(closeButton, buttonParams())

        val type = overlayWindowType()

        val params = WindowManager.LayoutParams(
            dp(260), WindowManager.LayoutParams.WRAP_CONTENT, type,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.TOP or Gravity.END
            x = dp(12)
            y = dp(150)
        }
        panel = root
        layoutParams = params
        windowManager?.addView(root, params)
    }

    @Suppress("DEPRECATION")
    private fun overlayWindowType(): Int = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O)
        WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
    else WindowManager.LayoutParams.TYPE_PHONE

    private fun makeButton(label: String, primary: Boolean, action: () -> Unit) = Button(this).apply {
        text = label
        textSize = 11f
        isAllCaps = true
        typeface = Typeface.create("sans-serif", Typeface.BOLD)
        setTextColor(if (primary) Color.rgb(7, 16, 11) else Color.rgb(220, 239, 221))
        background = rounded(
            if (primary) Color.rgb(181, 245, 154) else Color.argb(70, 120, 180, 130),
            if (primary) Color.rgb(181, 245, 154) else Color.argb(100, 140, 200, 150), 14
        )
        setOnClickListener { action() }
    }

    private fun buttonParams() = LinearLayout.LayoutParams(
        LinearLayout.LayoutParams.MATCH_PARENT, dp(42)
    ).apply { bottomMargin = dp(7) }

    private fun rounded(fill: Int, stroke: Int, radiusDp: Int) = GradientDrawable().apply {
        setColor(fill)
        cornerRadius = dp(radiusDp).toFloat()
        setStroke(dp(1), stroke)
    }

    private fun dp(value: Int): Int = (value * resources.displayMetrics.density + 0.5f).toInt()

    private inner class DragTouchListener : View.OnTouchListener {
        private var initialX = 0
        private var initialY = 0
        private var touchX = 0f
        private var touchY = 0f
        private var moved = false

        override fun onTouch(view: View, event: MotionEvent): Boolean {
            val params = layoutParams ?: return false
            when (event.action) {
                MotionEvent.ACTION_DOWN -> {
                    initialX = params.x
                    initialY = params.y
                    touchX = event.rawX
                    touchY = event.rawY
                    moved = false
                    return true
                }
                MotionEvent.ACTION_MOVE -> {
                    val dx = (event.rawX - touchX).toInt()
                    val dy = (event.rawY - touchY).toInt()
                    if (abs(dx) + abs(dy) > dp(3)) moved = true
                    params.x = (initialX - dx).coerceAtLeast(0)
                    params.y = (initialY + dy).coerceAtLeast(0)
                    try { panel?.let { windowManager?.updateViewLayout(it, params) } } catch (_: Exception) { }
                    return true
                }
                MotionEvent.ACTION_UP -> return moved
            }
            return false
        }
    }

    override fun onDestroy() {
        panel?.let { view -> try { windowManager?.removeView(view) } catch (_: Exception) { } }
        panel = null
        layoutParams = null
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    companion object {
        private const val CHANNEL_ID = "crustychess_floating_panel"
        private const val NOTIFICATION_ID = 1001
    }
}
