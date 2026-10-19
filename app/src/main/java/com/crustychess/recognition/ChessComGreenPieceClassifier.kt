package com.crustychess.recognition

import android.content.Context
import android.graphics.BitmapFactory
import org.opencv.android.Utils
import org.opencv.core.Mat
import org.opencv.core.Size
import org.opencv.imgproc.Imgproc
import kotlin.math.max
import kotlin.math.sqrt

/**
 * Template-based classifier tuned to the Chess.com Green board + piece set
 * visible in the supplied reference screenshot.
 *
 * This is a practical first version, not a neural model. It compares signed
 * foreground intensity patterns after removing the square's background level.
 * The templates are captured from the reference screenshot and normalized to
 * 64x64. Unsupported piece sets/themes should be rejected or calibrated.
 */
class ChessComGreenPieceClassifier(context: Context) : PieceClassifier {
    private data class Template(val symbol: Char, val descriptor: FloatArray)
    private val templates: List<Template>
    private val scratchGray = Mat()
    private val scratchResized = Mat()

    init {
        val loaded = mutableListOf<Template>()
        val names = context.assets.list("piece_templates") ?: emptyArray()
        for (name in names.filter { it.endsWith(".png") }.sorted()) {
            val symbol = name.firstOrNull() ?: continue
            if (symbol !in "KQRBNPkqrbnp") continue
            val bitmap = context.assets.open("piece_templates/$name").use {
                BitmapFactory.decodeStream(it)
            } ?: continue
            val mat = Mat()
            try {
                Utils.bitmapToMat(bitmap, mat)
                loaded += Template(symbol, descriptor(mat))
            } finally {
                mat.release()
                bitmap.recycle()
            }
        }
        require(loaded.isNotEmpty()) {
            "No piece templates found. Check app/src/main/assets/piece_templates."
        }
        templates = loaded
    }

    @Synchronized
    override fun classify(squareRgb: Mat): PiecePrediction? {
        if (squareRgb.empty()) return null
        val candidate = descriptor(squareRgb)
        val energy = candidate.second
        val vector = candidate.first

        // Empty squares in this theme are nearly uniform after subtracting the
        // border background. This threshold is intentionally conservative.
        if (energy < EMPTY_ENERGY_THRESHOLD) {
            return PiecePrediction(null, 0.99f)
        }

        val bestBySymbol = HashMap<Char, Float>()
        for (template in templates) {
            val similarity = cosine(vector, template.descriptor)
            val old = bestBySymbol[template.symbol] ?: -1f
            if (similarity > old) bestBySymbol[template.symbol] = similarity
        }

        val ranked = bestBySymbol.entries.sortedByDescending { it.value }
        if (ranked.isEmpty()) return PiecePrediction(null, 0f)
        val best = ranked[0]
        val second = ranked.getOrNull(1)?.value ?: -1f
        val margin = if (second < 0f) 1f else (best.value - second).coerceAtLeast(0f)

        // Penalize ambiguous matches. Confidence is a heuristic similarity,
        // not a calibrated probability.
        val confidence = (best.value - max(0f, 0.08f - margin) * 0.6f)
            .coerceIn(0f, 1f)

        return if (best.value >= MIN_SIMILARITY) {
            PiecePrediction(best.key, confidence)
        } else {
            PiecePrediction(null, confidence.coerceAtMost(0.69f))
        }
    }

    /**
     * Returns normalized signed grayscale difference from the median border
     * brightness, plus RMS foreground energy. White pieces remain positive and
     * dark pieces negative; board-square color is largely removed.
     */
    private fun descriptor(source: Mat): Pair<FloatArray, Float> {
        val channels = source.channels()
        when (channels) {
            4 -> Imgproc.cvtColor(source, scratchGray, Imgproc.COLOR_RGBA2GRAY)
            3 -> Imgproc.cvtColor(source, scratchGray, Imgproc.COLOR_RGB2GRAY)
            1 -> source.copyTo(scratchGray)
            else -> return Pair(FloatArray(64 * 64), 0f)
        }
        Imgproc.resize(scratchGray, scratchResized, Size(64.0, 64.0), 0.0, 0.0, Imgproc.INTER_AREA)
        val bytes = ByteArray(64 * 64)
        scratchResized.get(0, 0, bytes)

        val border = ArrayList<Int>(64 * 8)
        for (y in 0 until 64) for (x in 0 until 64) {
            if (x < BORDER_WIDTH || x >= 64 - BORDER_WIDTH ||
                y < BORDER_WIDTH || y >= 64 - BORDER_WIDTH
            ) {
                border += bytes[y * 64 + x].toInt() and 0xff
            }
        }
        border.sort()
        val background = border[border.size / 2].toFloat()

        val result = FloatArray(64 * 64)
        var sumSquares = 0.0
        var normSquares = 0.0
        for (i in bytes.indices) {
            val diff = (bytes[i].toInt() and 0xff).toFloat() - background
            result[i] = diff
            sumSquares += diff * diff
            normSquares += diff * diff
        }
        val energy = sqrt(sumSquares / result.size).toFloat()
        val norm = sqrt(normSquares).toFloat()
        if (norm > 1e-5f) {
            for (i in result.indices) result[i] /= norm
        }
        return Pair(result, energy)
    }

    private fun cosine(a: FloatArray, b: FloatArray): Float {
        var dot = 0f
        for (i in a.indices) dot += a[i] * b[i]
        return dot.coerceIn(-1f, 1f)
    }

    companion object {
        private const val EMPTY_ENERGY_THRESHOLD = 5.5f
        private const val MIN_SIMILARITY = 0.48f
        private const val BORDER_WIDTH = 4
    }
}
