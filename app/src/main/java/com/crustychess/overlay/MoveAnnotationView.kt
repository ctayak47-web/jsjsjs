package com.crustychess.overlay

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Path
import android.view.View
import com.crustychess.recognition.BoardGeometry

/**
 * Transparent annotation layer. Coordinates are SCREEN PIXELS from MediaProjection,
 * not dp. Map them into the overlay's local coordinate system before displaying.
 *
 * Draws center dots for recognized occupied squares and a line/arrow for the
 * engine's first UCI move. It only visualizes a suggestion; it does not tap or
 * move pieces on the chess website.
 */
class MoveAnnotationView(context: Context) : View(context) {
    private val dotPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.rgb(139, 226, 141)
        style = Paint.Style.FILL
    }
    private val linePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.rgb(255, 190, 65)
        strokeWidth = 5f
        style = Paint.Style.STROKE
        strokeCap = Paint.Cap.ROUND
    }
    private val arrowPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.rgb(255, 190, 65)
        style = Paint.Style.FILL
    }

    var board: BoardGeometry? = null
        set(value) { field = value; invalidate() }
    var occupiedFenSquares: Set<String> = emptySet()
        set(value) { field = value; invalidate() }
    var suggestedMoveUci: String? = null
        set(value) { field = value; invalidate() }

    /** Capture-frame origin expressed in screen pixels (e.g. status bar offset). */
    var captureOriginX: Float = 0f
        set(value) { field = value; invalidate() }
    var captureOriginY: Float = 0f
        set(value) { field = value; invalidate() }

    /** Scale from capture pixels to this view's local pixels. Set from measured bounds. */
    var captureToViewScaleX: Float = 1f
        set(value) { field = value; invalidate() }
    var captureToViewScaleY: Float = 1f
        set(value) { field = value; invalidate() }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val b = board ?: return
        val sizeX = b.squareSize.toFloat() * captureToViewScaleX
        val sizeY = b.squareSize.toFloat() * captureToViewScaleY
        val left = (b.bounds.left.toFloat() - captureOriginX) * captureToViewScaleX
        val top = (b.bounds.top.toFloat() - captureOriginY) * captureToViewScaleY

        // FEN square names use rank 8 at the top. Screen coordinates assume
        // white is at the bottom. If the board is flipped, pass flipped=true
        // in a future orientation-aware extension rather than guessing.
        for (squareName in occupiedFenSquares) {
            val point = squareCenter(squareName, left, top, sizeX, sizeY) ?: continue
            canvas.drawCircle(point.first, point.second, minOf(sizeX, sizeY) * 0.09f, dotPaint)
        }

        val uci = suggestedMoveUci ?: return
        if (uci.length < 4) return
        val from = squareCenter(uci.substring(0, 2), left, top, sizeX, sizeY) ?: return
        val to = squareCenter(uci.substring(2, 4), left, top, sizeX, sizeY) ?: return
        canvas.drawLine(from.first, from.second, to.first, to.second, linePaint)

        val angle = kotlin.math.atan2(
            (to.second - from.second).toDouble(),
            (to.first - from.first).toDouble()
        )
        val head = minOf(sizeX, sizeY) * 0.22f
        val path = Path().apply {
            moveTo(to.first, to.second)
            lineTo(
                to.first - head * kotlin.math.cos(angle - 0.55).toFloat(),
                to.second - head * kotlin.math.sin(angle - 0.55).toFloat()
            )
            lineTo(
                to.first - head * kotlin.math.cos(angle + 0.55).toFloat(),
                to.second - head * kotlin.math.sin(angle + 0.55).toFloat()
            )
            close()
        }
        canvas.drawPath(path, arrowPaint)
        canvas.drawCircle(to.first, to.second, minOf(sizeX, sizeY) * 0.12f, dotPaint)
    }

    private fun squareCenter(
        name: String, left: Float, top: Float, sizeX: Float, sizeY: Float
    ): Pair<Float, Float>? {
        if (name.length != 2) return null
        val file = name[0] - 'a'
        val rank = name[1] - '1'
        if (file !in 0..7 || rank !in 0..7) return null
        val col = file
        val row = 7 - rank
        return Pair(left + (col + 0.5f) * sizeX, top + (row + 0.5f) * sizeY)
    }
}
